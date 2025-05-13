#!/usr/bin/env python3
"""
Simple video analyzer module for extracting basic video information from S3.
"""

import json
import tempfile
import os
import sys
import argparse
import boto3
from typing import Dict, Any, List


def extract_video_info(s3_path: str, region: str = "us-east-1") -> Dict[str, Any]:
    """
    Extract basic video information from a video file in S3.

    Args:
        s3_path: S3 path to the video file (s3://bucket-name/path/to/video.mp4)
        region: AWS region

    Returns:
        Dictionary containing basic video information
    """
    # Parse S3 path
    if not s3_path.startswith("s3://"):
        raise ValueError("S3 path must start with 's3://'")
    
    path_parts = s3_path.replace("s3://", "").split("/", 1)
    bucket_name = path_parts[0]
    object_key = path_parts[1] if len(path_parts) > 1 else ""
    
    # Get S3 object metadata
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Get object metadata
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        
        # Create a temporary file to download the video
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(object_key)[1]) as temp_file:
            # Download the video from S3
            s3_client.download_file(bucket_name, object_key, temp_file.name)
            
            # Get file size
            file_size = os.path.getsize(temp_file.name)
            
            # Extract basic information
            info = {
                "s3_path": s3_path,
                "file_name": os.path.basename(object_key),
                "file_extension": os.path.splitext(object_key)[1],
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "content_type": response.get('ContentType', 'unknown'),
                "last_modified": response.get('LastModified', '').isoformat() if response.get('LastModified') else None,
                "metadata": response.get('Metadata', {})
            }
            
            return info
    except Exception as e:
        raise RuntimeError(f"Failed to extract video information: {str(e)}")


def compare_videos(video_info1: Dict[str, Any], video_info2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two video information dictionaries and return differences.

    Args:
        video_info1: First video information dictionary
        video_info2: Second video information dictionary

    Returns:
        Dictionary containing differences between the videos
    """
    differences = {}
    
    # Compare file sizes
    if video_info1["file_size_bytes"] != video_info2["file_size_bytes"]:
        differences["file_size"] = {
            "video1": {
                "bytes": video_info1["file_size_bytes"],
                "mb": video_info1["file_size_mb"]
            },
            "video2": {
                "bytes": video_info2["file_size_bytes"],
                "mb": video_info2["file_size_mb"]
            },
            "difference_percent": round(
                (video_info2["file_size_bytes"] - video_info1["file_size_bytes"]) / video_info1["file_size_bytes"] * 100, 2
            )
        }
    
    # Compare content types
    if video_info1["content_type"] != video_info2["content_type"]:
        differences["content_type"] = {
            "video1": video_info1["content_type"],
            "video2": video_info2["content_type"]
        }
    
    # Compare metadata
    metadata_diff = {}
    all_keys = set(video_info1["metadata"].keys()) | set(video_info2["metadata"].keys())
    
    for key in all_keys:
        val1 = video_info1["metadata"].get(key)
        val2 = video_info2["metadata"].get(key)
        
        if val1 != val2:
            metadata_diff[key] = {
                "video1": val1,
                "video2": val2
            }
    
    if metadata_diff:
        differences["metadata"] = metadata_diff
    
    return differences


def list_s3_videos(s3_path: str, region: str = "us-east-1") -> List[str]:
    """
    List video files in an S3 path.

    Args:
        s3_path: S3 path to the directory (s3://bucket-name/path/)
        region: AWS region

    Returns:
        List of S3 paths to video files
    """
    # Parse S3 path
    if not s3_path.startswith("s3://"):
        raise ValueError("S3 path must start with 's3://'")
    
    path_parts = s3_path.replace("s3://", "").split("/", 1)
    bucket_name = path_parts[0]
    prefix = path_parts[1] if len(path_parts) > 1 else ""
    
    # Ensure prefix ends with a slash if it's not empty
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    
    # List objects in the bucket with the given prefix
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        # Filter for video files
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        video_files = []
        
        for obj in response.get('Contents', []):
            key = obj['Key']
            ext = os.path.splitext(key)[1].lower()
            
            if ext in video_extensions:
                video_files.append(f"s3://{bucket_name}/{key}")
        
        return video_files
    except Exception as e:
        raise RuntimeError(f"Failed to list S3 videos: {str(e)}")


def write_output(data, output_path=None):
    """Write data to the specified output path or stdout."""
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Output written to {output_path}")
    else:
        print(json.dumps(data, indent=2))


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Simple video analyzer for extracting basic video information from S3."
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Extract video info command
    extract_parser = subparsers.add_parser(
        "extract", help="Extract video information from an S3 path"
    )
    extract_parser.add_argument(
        "s3_path", help="S3 path to the video file (s3://bucket-name/path/to/video.mp4)"
    )
    extract_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    extract_parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )
    
    # Compare videos command
    compare_parser = subparsers.add_parser(
        "compare", help="Compare two videos and show differences"
    )
    compare_parser.add_argument(
        "video1", help="S3 path to the first video file"
    )
    compare_parser.add_argument(
        "video2", help="S3 path to the second video file"
    )
    compare_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    compare_parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )
    
    # List videos command
    list_parser = subparsers.add_parser(
        "list", help="List video files in an S3 path"
    )
    list_parser.add_argument(
        "s3_path", help="S3 path to the directory (s3://bucket-name/path/)"
    )
    list_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    list_parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )
    
    args = parser.parse_args()
    
    if args.command == "extract" or not args.command:  # Default to extract if no command is specified
        try:
            s3_path = args.s3_path if args.command == "extract" else args.s3_path
            print(f"Extracting video information from {s3_path}...")
            video_info = extract_video_info(s3_path, args.region if args.command == "extract" else "us-east-1")
            write_output(video_info, args.output if args.command == "extract" else None)
            return 0
        except Exception as e:
            print(f"Error extracting video information: {e}", file=sys.stderr)
            return 1
    
    elif args.command == "compare":
        try:
            print(f"Extracting video information from {args.video1}...")
            video1_info = extract_video_info(args.video1, args.region)
            
            print(f"Extracting video information from {args.video2}...")
            video2_info = extract_video_info(args.video2, args.region)
            
            print("Comparing videos...")
            differences = compare_videos(video1_info, video2_info)
            
            write_output(differences, args.output)
            return 0
        except Exception as e:
            print(f"Error comparing videos: {e}", file=sys.stderr)
            return 1
    
    elif args.command == "list":
        try:
            print(f"Listing video files in {args.s3_path}...")
            video_files = list_s3_videos(args.s3_path, args.region)
            
            result = {
                "s3_path": args.s3_path,
                "video_count": len(video_files),
                "videos": video_files
            }
            
            write_output(result, args.output)
            return 0
        except Exception as e:
            print(f"Error listing video files: {e}", file=sys.stderr)
            return 1
    
    else:
        print("No command specified. Use --help for usage information.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
