"""
Example usage of the VideoAnalyzer class using ffmpeg-python.
"""

import json
from analyzer import VideoAnalyzer


def main():
    """
    Example of using the VideoAnalyzer class to extract video information,
    compare videos, and analyze differences.
    """
    # Initialize the analyzer
    analyzer = VideoAnalyzer(region="us-east-1")
    
    # Example 1: Extract video information
    print("Example 1: Extract video information")
    print("------------------------------------")
    try:
        # Replace with your S3 path
        s3_path = "s3://your-bucket/path/to/video.mp4"
        video_info = analyzer.extract_video_info(s3_path)
        print(f"Video information extracted successfully from {s3_path}")
        print(json.dumps(video_info, indent=2)[:500] + "...\n")
    except Exception as e:
        print(f"Error extracting video information: {e}\n")
    
    # Example 2: Compare two videos
    print("Example 2: Compare two videos")
    print("-----------------------------")
    try:
        # Replace with your S3 paths
        s3_path1 = "s3://your-bucket/path/to/video1.mp4"
        s3_path2 = "s3://your-bucket/path/to/video2.mp4"
        
        print(f"Extracting information from {s3_path1}...")
        video1_info = analyzer.extract_video_info(s3_path1)
        
        print(f"Extracting information from {s3_path2}...")
        video2_info = analyzer.extract_video_info(s3_path2)
        
        print("Comparing videos...")
        differences = analyzer.compare_videos(video1_info, video2_info)
        
        print("Differences:")
        print(json.dumps(differences, indent=2) + "\n")
    except Exception as e:
        print(f"Error comparing videos: {e}\n")
    
    # Example 3: Analyze differences with Claude 3.5
    print("Example 3: Analyze differences with Claude 3.5")
    print("----------------------------------------------")
    try:
        # Use the differences from Example 2 or create a sample
        if 'differences' not in locals():
            # Sample differences for demonstration
            differences = {
                "format": {
                    "duration": {
                        "video1": "120.000000",
                        "video2": "119.500000"
                    },
                    "bit_rate": {
                        "video1": "5000000",
                        "video2": "3000000"
                    }
                },
                "streams": {
                    "video_streams": {
                        "codec_name": {
                            "video1": "h264",
                            "video2": "h265"
                        },
                        "width": {
                            "video1": 1920,
                            "video2": 1280
                        },
                        "height": {
                            "video1": 1080,
                            "video2": 720
                        }
                    }
                }
            }
        
        print("Analyzing differences with Claude 3.5...")
        analysis = analyzer.analyze_differences(differences)
        
        print("Analysis:")
        print(analysis)
    except Exception as e:
        print(f"Error analyzing differences: {e}")


if __name__ == "__main__":
    main()
