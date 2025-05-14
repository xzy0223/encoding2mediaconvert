# Video Analyzer

This module provides functionality for analyzing video files, comparing them, and analyzing differences using Claude 3.5 on Bedrock.

## Features

- Extract video information from S3 using ffmpeg
- Compare two videos and identify differences in:
  - Format information (all available properties)
  - Video stream properties (all available properties)
  - Audio stream properties (all available properties)
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

To use the analyzer as a Python module:

```python
from e2mc_assistant.analyzer.video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer(region="us-east-1")
video_info = analyzer.extract_video_info("s3://my-bucket/path/to/video.mp4")
print(video_info)
```

#### Compare Two Videos

```python
from e2mc_assistant.analyzer.video_analyzer import VideoAnalyzer

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
from e2mc_assistant.analyzer.video_analyzer import VideoAnalyzer

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
python -m e2mc_assistant.analyzer.video_analyzer extract s3://my-bucket/path/to/video.mp4 --output video_info.json
```

#### Compare Two Videos

```bash
python -m e2mc_assistant.analyzer.video_analyzer compare s3://my-bucket/path/to/video1.mp4 s3://my-bucket/path/to/video2.mp4 --output differences.json
```

#### Analyze Differences with Claude 3.5

```bash
python -m e2mc_assistant.analyzer.video_analyzer analyze s3://my-bucket/path/to/video1.mp4 s3://my-bucket/path/to/video2.mp4 --output analysis.txt
```

#### Analyze Differences from JSON File

```bash
python -m e2mc_assistant.analyzer.video_analyzer analyze-json differences.json --output analysis.txt
```

#### Help

```bash
python -m e2mc_assistant.analyzer.video_analyzer --help
python -m e2mc_assistant.analyzer.video_analyzer extract --help
python -m e2mc_assistant.analyzer.video_analyzer compare --help
python -m e2mc_assistant.analyzer.video_analyzer analyze --help
python -m e2mc_assistant.analyzer.video_analyzer analyze-json --help
```

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
