#!/usr/bin/env python3
"""
Video analyzer module for extracting video information, comparing videos,
and analyzing differences using Claude 3.5 on Bedrock.
Uses subprocess to call ffprobe directly.
"""

import json
import tempfile
import os
import sys
import argparse
import subprocess
import boto3
from typing import Dict, Any, List, Tuple, Optional


class VideoAnalyzer:
    """
    A class for analyzing video files, comparing them, and analyzing differences
    using Claude 3.5 on Bedrock.
    """

    def __init__(self, region: str = "us-east-1"):
        """
        Initialize the VideoAnalyzer.

        Args:
            region: AWS region for Bedrock service
        """
        self.region = region
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region
        )

    def extract_video_info(self, s3_path: str) -> Dict[str, Any]:
        """
        Extract video information using ffprobe from a video file in S3.

        Args:
            s3_path: S3 path to the video file (s3://bucket-name/path/to/video.mp4)

        Returns:
            Dictionary containing video information
        """
        # Parse S3 path
        if not s3_path.startswith("s3://"):
            raise ValueError("S3 path must start with 's3://'")
        
        bucket_name, object_key = self._parse_s3_path(s3_path)
        
        # Create a temporary file to download the video
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=os.path.splitext(object_key)[1], delete=False)
            temp_path = temp_file.name
            temp_file.close()  # Close the file handle but keep the file
            
            # Download the video from S3
            s3_client = boto3.client('s3')
            s3_client.download_file(bucket_name, object_key, temp_path)
            
            # Extract video information using ffprobe
            try:
                # Get basic probe information
                cmd = [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    temp_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise RuntimeError(f"Failed to extract video information: {result.stderr}")
                
                probe_result = json.loads(result.stdout)
                
                # Extract additional frame information
                frame_info = self._extract_frame_info(temp_path)
                probe_result["frame_info"] = frame_info
                
                return probe_result
            except subprocess.SubprocessError as e:
                raise RuntimeError(f"Failed to extract video information: {str(e)}")
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse ffprobe output: {str(e)}")
        finally:
            # Clean up the temporary file
            if temp_file is not None:
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except Exception as e:
                    print(f"Warning: Failed to delete temporary file {temp_path}: {str(e)}", file=sys.stderr)

    def _extract_frame_info(self, video_path: str) -> Dict[str, Any]:
        """
        Extract detailed frame information from the video using ffprobe.

        Args:
            video_path: Path to the video file

        Returns:
            Dictionary containing frame information
        """
        try:
            # Use ffprobe to get frame information
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-select_streams", "v:0",
                "-show_entries", "frame=pkt_pts_time,pict_type,key_frame",
                "-of", "json",
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to extract frame information: {result.stderr}")
            
            return json.loads(result.stdout)
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Failed to extract frame information: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse ffprobe output: {str(e)}")

    def _parse_s3_path(self, s3_path: str) -> Tuple[str, str]:
        """
        Parse an S3 path into bucket name and object key.

        Args:
            s3_path: S3 path (s3://bucket-name/path/to/object)

        Returns:
            Tuple of (bucket_name, object_key)
        """
        path_parts = s3_path.replace("s3://", "").split("/", 1)
        bucket_name = path_parts[0]
        object_key = path_parts[1] if len(path_parts) > 1 else ""
        return bucket_name, object_key

    def compare_videos(self, video_info1: Dict[str, Any], video_info2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two video information dictionaries and return differences.

        Args:
            video_info1: First video information dictionary
            video_info2: Second video information dictionary

        Returns:
            Dictionary containing differences between the videos
        """
        differences = {
            "format": self._compare_format(video_info1.get("format", {}), video_info2.get("format", {})),
            "streams": self._compare_streams(video_info1.get("streams", []), video_info2.get("streams", [])),
            "frame_info": self._compare_frame_info(
                video_info1.get("frame_info", {"frames": []}), 
                video_info2.get("frame_info", {"frames": []})
            )
        }
        
        # Remove empty difference sections
        differences = {k: v for k, v in differences.items() if v}
        
        return differences

    def _compare_format(self, format1: Dict[str, Any], format2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare format information between two videos.

        Args:
            format1: Format information from first video
            format2: Format information from second video

        Returns:
            Dictionary containing format differences
        """
        differences = {}
        
        # Compare all keys from both format dictionaries
        all_keys = set(format1.keys()) | set(format2.keys())
        
        for key in all_keys:
            val1 = format1.get(key, "N/A")
            val2 = format2.get(key, "N/A")
            
            if val1 != val2:
                differences[key] = {
                    "video1": val1,
                    "video2": val2
                }
        
        return differences

    def _compare_streams(self, streams1: List[Dict[str, Any]], streams2: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare stream information between two videos.

        Args:
            streams1: Stream information from first video
            streams2: Stream information from second video

        Returns:
            Dictionary containing stream differences
        """
        differences = {}
        
        # Group streams by codec_type
        streams1_by_type = self._group_streams_by_type(streams1)
        streams2_by_type = self._group_streams_by_type(streams2)
        
        # Compare stream counts
        all_types = set(streams1_by_type.keys()) | set(streams2_by_type.keys())
        
        for stream_type in all_types:
            count1 = len(streams1_by_type.get(stream_type, []))
            count2 = len(streams2_by_type.get(stream_type, []))
            
            if count1 != count2:
                if "stream_counts" not in differences:
                    differences["stream_counts"] = {}
                
                differences["stream_counts"][stream_type] = {
                    "video1": count1,
                    "video2": count2
                }
        
        # Compare video streams
        video_diffs = self._compare_video_streams(
            streams1_by_type.get("video", []),
            streams2_by_type.get("video", [])
        )
        if video_diffs:
            differences["video_streams"] = video_diffs
        
        # Compare audio streams
        audio_diffs = self._compare_audio_streams(
            streams1_by_type.get("audio", []),
            streams2_by_type.get("audio", [])
        )
        if audio_diffs:
            differences["audio_streams"] = audio_diffs
        
        return differences

    def _group_streams_by_type(self, streams: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group streams by codec_type.

        Args:
            streams: List of stream dictionaries

        Returns:
            Dictionary with codec_type as keys and lists of streams as values
        """
        result = {}
        for stream in streams:
            codec_type = stream.get("codec_type", "unknown")
            if codec_type not in result:
                result[codec_type] = []
            result[codec_type].append(stream)
        return result

    def _compare_video_streams(self, video_streams1: List[Dict[str, Any]], video_streams2: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare video streams between two videos.

        Args:
            video_streams1: Video streams from first video
            video_streams2: Video streams from second video

        Returns:
            Dictionary containing video stream differences
        """
        differences = {}
        
        # Compare first video stream (or return differences in counts)
        if not video_streams1 and not video_streams2:
            return {}
        
        if not video_streams1:
            return {"missing_in_video1": True}
        
        if not video_streams2:
            return {"missing_in_video2": True}
        
        # Compare first video stream from each
        stream1 = video_streams1[0]
        stream2 = video_streams2[0]
        
        # Compare all keys from both stream dictionaries
        all_keys = set(stream1.keys()) | set(stream2.keys())
        
        for key in all_keys:
            val1 = stream1.get(key, "N/A")
            val2 = stream2.get(key, "N/A")
            
            if val1 != val2:
                differences[key] = {
                    "video1": val1,
                    "video2": val2
                }
        
        return differences

    def _compare_audio_streams(self, audio_streams1: List[Dict[str, Any]], audio_streams2: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare audio streams between two videos.

        Args:
            audio_streams1: Audio streams from first video
            audio_streams2: Audio streams from second video

        Returns:
            Dictionary containing audio stream differences
        """
        differences = {}
        
        # Compare first audio stream (or return differences in counts)
        if not audio_streams1 and not audio_streams2:
            return {}
        
        if not audio_streams1:
            return {"missing_in_video1": True}
        
        if not audio_streams2:
            return {"missing_in_video2": True}
        
        # Compare first audio stream from each
        stream1 = audio_streams1[0]
        stream2 = audio_streams2[0]
        
        # Compare all keys from both stream dictionaries
        all_keys = set(stream1.keys()) | set(stream2.keys())
        
        for key in all_keys:
            val1 = stream1.get(key, "N/A")
            val2 = stream2.get(key, "N/A")
            
            if val1 != val2:
                differences[key] = {
                    "video1": val1,
                    "video2": val2
                }
        
        return differences

    def _compare_frame_info(self, frame_info1: Dict[str, Any], frame_info2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare frame information between two videos.

        Args:
            frame_info1: Frame information from first video
            frame_info2: Frame information from second video

        Returns:
            Dictionary containing frame information differences
        """
        differences = {}
        
        frames1 = frame_info1.get("frames", [])
        frames2 = frame_info2.get("frames", [])
        
        # Compare frame counts
        frame_count1 = len(frames1)
        frame_count2 = len(frames2)
        
        if frame_count1 != frame_count2:
            differences["frame_count"] = {
                "video1": frame_count1,
                "video2": frame_count2
            }
        
        # Compare keyframe distribution
        keyframes1 = [f for f in frames1 if f.get("key_frame") == 1]
        keyframes2 = [f for f in frames2 if f.get("key_frame") == 1]
        
        keyframe_count1 = len(keyframes1)
        keyframe_count2 = len(keyframes2)
        
        if keyframe_count1 != keyframe_count2:
            differences["keyframe_count"] = {
                "video1": keyframe_count1,
                "video2": keyframe_count2
            }
        
        # Calculate keyframe intervals
        if keyframe_count1 > 1 and keyframe_count2 > 1:
            avg_keyframe_interval1 = frame_count1 / keyframe_count1
            avg_keyframe_interval2 = frame_count2 / keyframe_count2
            
            if abs(avg_keyframe_interval1 - avg_keyframe_interval2) > 0.5:  # Allow small differences
                differences["avg_keyframe_interval"] = {
                    "video1": avg_keyframe_interval1,
                    "video2": avg_keyframe_interval2
                }
        
        return differences

    def analyze_differences(self, differences: Dict[str, Any], model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0") -> str:
        """
        Analyze video differences using Claude 3.5 on Bedrock.

        Args:
            differences: Dictionary containing differences between videos
            model_id: Bedrock model ID to use for analysis

        Returns:
            Analysis of the differences as a string
        """
        # Create prompt for Claude
        prompt = self._create_analysis_prompt(differences)
        
        # Call Bedrock with Claude 3.5
        response = self.bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response.get('body').read())
        analysis = response_body.get('content', [{}])[0].get('text', '')
        
        return analysis

    def _create_analysis_prompt(self, differences: Dict[str, Any]) -> str:
        """
        Create a prompt for Claude 3.5 to analyze video differences.

        Args:
            differences: Dictionary containing differences between videos

        Returns:
            Prompt string for Claude 3.5
        """
        prompt = """
# Video Comparison Analysis

I need you to analyze the differences between two video files. Below is a JSON object containing the differences detected between the videos. Please provide:

1. A summary of the key differences
2. An explanation of what these differences mean in terms of video quality, encoding, and potential issues
3. Recommendations for addressing any issues or optimizing the videos
4. Any potential causes for these differences (e.g., different encoding settings, transcoding issues)

## Differences JSON:
```json
{diff_json}
```

Please format your response with clear sections and bullet points where appropriate. Focus on the most significant differences that would impact video quality or playback.
""".strip().format(diff_json=json.dumps(differences, indent=2))
        
        return prompt


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Video analyzer for extracting video information, comparing videos, "
                    "and analyzing differences using Claude 3.5 on Bedrock."
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
    
    # Analyze differences command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze differences between two videos using Claude 3.5"
    )
    analyze_parser.add_argument(
        "video1", help="S3 path to the first video file"
    )
    analyze_parser.add_argument(
        "video2", help="S3 path to the second video file"
    )
    analyze_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    analyze_parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )
    analyze_parser.add_argument(
        "--model-id", default="anthropic.claude-3-5-sonnet-20240620-v1:0",
        help="Bedrock model ID (default: anthropic.claude-3-5-sonnet-20240620-v1:0)"
    )
    
    # Analyze from JSON command
    analyze_json_parser = subparsers.add_parser(
        "analyze-json", help="Analyze differences from a JSON file using Claude 3.5"
    )
    analyze_json_parser.add_argument(
        "json_file", help="Path to the JSON file containing differences"
    )
    analyze_json_parser.add_argument(
        "--output", "-o", help="Output file path (default: stdout)"
    )
    analyze_json_parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )
    analyze_json_parser.add_argument(
        "--model-id", default="anthropic.claude-3-5-sonnet-20240620-v1:0",
        help="Bedrock model ID (default: anthropic.claude-3-5-sonnet-20240620-v1:0)"
    )
    
    return parser.parse_args()


def write_output(data, output_path=None):
    """Write data to the specified output path or stdout."""
    if output_path:
        with open(output_path, 'w') as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, indent=2)
        print(f"Output written to {output_path}")
    else:
        if isinstance(data, str):
            print(data)
        else:
            print(json.dumps(data, indent=2))


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    if args.command == "extract":
        analyzer = VideoAnalyzer(region=args.region)
        try:
            print(f"Extracting video information from {args.s3_path}...")
            video_info = analyzer.extract_video_info(args.s3_path)
            write_output(video_info, args.output)
            return 0
        except Exception as e:
            print(f"Error extracting video information: {e}", file=sys.stderr)
            return 1
    
    elif args.command == "compare":
        analyzer = VideoAnalyzer(region=args.region)
        try:
            print(f"Extracting video information from {args.video1}...")
            video1_info = analyzer.extract_video_info(args.video1)
            
            print(f"Extracting video information from {args.video2}...")
            video2_info = analyzer.extract_video_info(args.video2)
            
            print("Comparing videos...")
            differences = analyzer.compare_videos(video1_info, video2_info)
            
            write_output(differences, args.output)
            return 0
        except Exception as e:
            print(f"Error comparing videos: {e}", file=sys.stderr)
            return 1
    
    elif args.command == "analyze":
        analyzer = VideoAnalyzer(region=args.region)
        try:
            print(f"Extracting video information from {args.video1}...")
            video1_info = analyzer.extract_video_info(args.video1)
            
            print(f"Extracting video information from {args.video2}...")
            video2_info = analyzer.extract_video_info(args.video2)
            
            print("Comparing videos...")
            differences = analyzer.compare_videos(video1_info, video2_info)
            
            print("Analyzing differences with Claude 3.5...")
            analysis = analyzer.analyze_differences(differences, model_id=args.model_id)
            
            write_output(analysis, args.output)
            return 0
        except Exception as e:
            print(f"Error analyzing differences: {e}", file=sys.stderr)
            return 1
    
    elif args.command == "analyze-json":
        analyzer = VideoAnalyzer(region=args.region)
        try:
            print(f"Reading differences from {args.json_file}...")
            with open(args.json_file, 'r') as f:
                differences = json.load(f)
            
            print("Analyzing differences with Claude 3.5...")
            analysis = analyzer.analyze_differences(differences, model_id=args.model_id)
            
            write_output(analysis, args.output)
            return 0
        except Exception as e:
            print(f"Error analyzing differences: {e}", file=sys.stderr)
            return 1
    
    else:
        print("No command specified. Use --help for usage information.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
