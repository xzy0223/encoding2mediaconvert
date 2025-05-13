# Video Analyzer

This module provides functionality for analyzing video files, comparing them, and analyzing differences using Claude 3.5 on Bedrock.

## Features

- Extract video information from S3 using ffmpeg
- Compare two videos and identify differences in:
  - Format information (duration, bitrate, etc.)
  - Video stream properties (codec, resolution, framerate, etc.)
  - Audio stream properties (codec, channels, sample rate, etc.)
  - Frame information (keyframe distribution, etc.)
- Analyze differences using Claude 3.5 on Bedrock

## Requirements

- ffmpeg and ffprobe installed on the system
- AWS credentials configured with access to:
  - S3 (for reading video files)
  - Bedrock (for Claude 3.5 access)

## Installation

### Installing ffmpeg

Since ffmpeg is not available in the default repositories for Amazon Linux 2023, we'll install it from a static build:

```bash
# Create a directory for the installation files
mkdir -p ~/ffmpeg_install
cd ~/ffmpeg_install

# Download the static build of ffmpeg
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

# Extract the archive
tar xf ffmpeg-release-amd64-static.tar.xz

# Create a bin directory in your home folder (if it doesn't exist)
mkdir -p ~/bin

# Copy the ffmpeg and ffprobe binaries to your bin directory
cp ~/ffmpeg_install/ffmpeg-*-amd64-static/ffmpeg ~/bin/
cp ~/ffmpeg_install/ffmpeg-*-amd64-static/ffprobe ~/bin/

# Add the bin directory to your PATH
export PATH=$PATH:~/bin

# Add the PATH update to your .bashrc for persistence
echo 'export PATH=$PATH:~/bin' >> ~/.bashrc
```

### Installing Python Dependencies

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate

# Install required Python packages
pip install boto3
```

## Usage

### Python API

To use the analyzer as a Python module, make sure the project root directory is in your Python path:

```bash
# Add the project root to PYTHONPATH
export PYTHONPATH=/path/to/e2mc_assistant:$PYTHONPATH
```

Then import the module:

```python
from src.analyzer import VideoAnalyzer

analyzer = VideoAnalyzer(region="us-east-1")
video_info = analyzer.extract_video_info("s3://my-bucket/path/to/video.mp4")
print(video_info)
```

#### Compare Two Videos

```python
from src.analyzer import VideoAnalyzer

analyzer = VideoAnalyzer(region="us-east-1")

# Extract information from both videos
video1_info = analyzer.extract_video_info("s3://my-bucket/path/to/video1.mp4")
video2_info = analyzer.extract_video_info("s3://my-bucket/path/to/video2.mp4")

# Compare the videos
differences = analyzer.compare_videos(video1_info, video2_info)
print(differences)
```

#### Analyze Differences with Claude 3.5

```python
from src.analyzer import VideoAnalyzer

analyzer = VideoAnalyzer(region="us-east-1")

# Extract information from both videos
video1_info = analyzer.extract_video_info("s3://my-bucket/path/to/video1.mp4")
video2_info = analyzer.extract_video_info("s3://my-bucket/path/to/video2.mp4")

# Compare the videos
differences = analyzer.compare_videos(video1_info, video2_info)

# Analyze differences using Claude 3.5
analysis = analyzer.analyze_differences(differences)
print(analysis)
```

### Command-Line Interface

The analyzer also provides a command-line interface for all operations.

#### Extract Video Information

```bash
cd /home/ec2-user/e2mc_assistant
source venv/bin/activate
export PATH=$PATH:~/bin
python src/analyzer/video_analyzer_fixed.py extract s3://my-bucket/path/to/video.mp4 --output video_info.json
```

#### Compare Two Videos

```bash
python src/analyzer/video_analyzer_fixed.py compare s3://my-bucket/path/to/video1.mp4 s3://my-bucket/path/to/video2.mp4 --output differences.json
```

#### Analyze Differences with Claude 3.5

```bash
python src/analyzer/video_analyzer_fixed.py analyze s3://my-bucket/path/to/video1.mp4 s3://my-bucket/path/to/video2.mp4 --output analysis.txt
```

#### Analyze Differences from JSON File

```bash
python src/analyzer/video_analyzer_fixed.py analyze-json differences.json --output analysis.txt
```

#### Help

```bash
python src/analyzer/video_analyzer_fixed.py --help
python src/analyzer/video_analyzer_fixed.py extract --help
python src/analyzer/video_analyzer_fixed.py compare --help
python src/analyzer/video_analyzer_fixed.py analyze --help
python src/analyzer/video_analyzer_fixed.py analyze-json --help
```

## Simple Analyzer

For basic video information without requiring ffmpeg, you can use the `simple_analyzer.py` script:

```bash
python src/analyzer/simple_analyzer.py extract s3://my-bucket/path/to/video.mp4
python src/analyzer/simple_analyzer.py list s3://my-bucket/path/
```

This provides basic metadata from S3 and doesn't require ffmpeg to be installed.

## Claude 3.5 Prompt Template

The analyzer uses the following prompt template when sending differences to Claude 3.5:

```
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
```

This prompt can be customized by modifying the `_create_analysis_prompt` method in the `VideoAnalyzer` class.
