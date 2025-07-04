# 🎥 Video Analyzer - AI-Powered Video Analysis & Comparison

[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-orange.svg)](https://aws.amazon.com/bedrock/)
[![Claude 3.5](https://img.shields.io/badge/AI-Claude%203.5-purple.svg)](https://www.anthropic.com/claude)

The **Video Analyzer** is an advanced component of E2MC Assistant that provides comprehensive video analysis, comparison, and AI-powered insights using AWS Bedrock with Claude 3.5 Sonnet.

---

## 🌟 Key Features

### 📊 **Comprehensive Video Analysis**
- **Metadata Extraction**: Complete video/audio stream information
- **Format Analysis**: Container, codec, and encoding parameters
- **Quality Metrics**: Bitrate, resolution, frame rate analysis
- **Stream Properties**: Audio channels, sample rates, color space

### 🔍 **Intelligent Video Comparison**
- **Side-by-Side Analysis**: Compare original vs transcoded videos
- **Difference Detection**: Identify quality, format, and encoding differences
- **Statistical Analysis**: Quantitative comparison metrics
- **Visual Quality Assessment**: Frame-level comparison capabilities

### 🤖 **AI-Powered Insights**
- **Claude 3.5 Integration**: Advanced AI analysis of video differences
- **Quality Assessment**: Intelligent quality impact evaluation
- **Optimization Recommendations**: AI-generated improvement suggestions
- **Issue Diagnosis**: Automated problem identification and solutions

### ☁️ **Cloud-Native Architecture**
- **S3 Integration**: Direct analysis of videos stored in S3
- **Serverless Processing**: No local storage requirements
- **Scalable Analysis**: Handle videos of any size
- **AWS Bedrock**: Enterprise-grade AI capabilities

---

## 🚀 Quick Start

### Command Line Usage

```bash
# Extract comprehensive video information
e2mc-analyzer extract s3://bucket/video.mp4 --output info.json

# Compare two videos
e2mc-analyzer compare \
  s3://bucket/original.mp4 \
  s3://bucket/transcoded.mp4 \
  --output differences.json

# AI-powered analysis of differences
e2mc-analyzer analyze \
  s3://bucket/original.mp4 \
  s3://bucket/transcoded.mp4 \
  --output analysis.txt

# Analyze existing differences JSON
e2mc-analyzer analyze-json differences.json --output analysis.txt
```

### Python API

```python
from e2mc_assistant.analyzer import VideoAnalyzer

# Initialize analyzer
analyzer = VideoAnalyzer(region='us-east-1')

# Extract video information
video_info = analyzer.extract_video_info('s3://bucket/video.mp4')

# Compare two videos
differences = analyzer.compare_videos(
    's3://bucket/original.mp4',
    's3://bucket/transcoded.mp4'
)

# AI-powered analysis
analysis = analyzer.analyze_differences(differences)
print(analysis)
```

---

## 📋 Prerequisites

### System Requirements

- **Python 3.6+**
- **ffmpeg/ffprobe** (for video analysis)
- **AWS CLI configured** (for S3 and Bedrock access)

### AWS Services

- **Amazon S3**: Video file storage
- **AWS Bedrock**: Claude 3.5 Sonnet access
- **IAM Permissions**: S3 read, Bedrock invoke

### Installing ffmpeg

#### macOS
```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Amazon Linux 2023
```bash
# Download static build
mkdir -p ~/ffmpeg_install && cd ~/ffmpeg_install
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xf ffmpeg-release-amd64-static.tar.xz

# Install to user bin
mkdir -p ~/bin
cp ~/ffmpeg_install/ffmpeg-*-amd64-static/{ffmpeg,ffprobe} ~/bin/
export PATH=$PATH:~/bin
echo 'export PATH=$PATH:~/bin' >> ~/.bashrc
```

---

## 🔧 Configuration

### AWS Credentials

```bash
# Using AWS CLI
aws configure

# Using environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Required IAM Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket/*",
                "arn:aws:bedrock:*:*:model/anthropic.claude-3-5-sonnet-*"
            ]
        }
    ]
}
```

---

## 📊 Analysis Capabilities

### Video Information Extraction

```python
video_info = analyzer.extract_video_info('s3://bucket/video.mp4')

# Returns comprehensive information:
{
    "format": {
        "filename": "video.mp4",
        "nb_streams": 2,
        "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
        "duration": "120.000000",
        "size": "52428800",
        "bit_rate": "3495253"
    },
    "video_streams": [{
        "codec_name": "h264",
        "width": 1920,
        "height": 1080,
        "r_frame_rate": "30/1",
        "bit_rate": "3000000",
        "color_space": "bt709"
    }],
    "audio_streams": [{
        "codec_name": "aac",
        "channels": 2,
        "sample_rate": "48000",
        "bit_rate": "128000"
    }]
}
```

### Video Comparison

```python
differences = analyzer.compare_videos(video1_info, video2_info)

# Returns detailed comparison:
{
    "format_differences": {
        "duration": {"video1": 120.0, "video2": 119.8, "diff": -0.2},
        "bit_rate": {"video1": 3495253, "video2": 2800000, "diff": -695253}
    },
    "video_differences": {
        "resolution": {"video1": "1920x1080", "video2": "1280x720"},
        "codec": {"video1": "h264", "video2": "h264"},
        "bitrate_change": -20.5  # percentage
    },
    "audio_differences": {
        "codec": {"video1": "aac", "video2": "aac"},
        "channels": {"video1": 2, "video2": 2},
        "bitrate_change": 0.0
    }
}
```

### AI-Powered Analysis

```python
analysis = analyzer.analyze_differences(differences)

# Returns Claude 3.5 analysis:
"""
# Video Comparison Analysis

## Key Differences Summary
- **Resolution Downscale**: Video was downscaled from 1920x1080 to 1280x720 (33% reduction)
- **Bitrate Reduction**: Overall bitrate reduced by 20.5%, indicating compression optimization
- **Duration Variance**: Minor 0.2-second difference, likely due to encoding precision

## Quality Impact Assessment
- **Visual Quality**: Moderate impact due to resolution reduction
- **File Size**: Significant reduction (~30% smaller file)
- **Compatibility**: Improved compatibility with lower-end devices

## Recommendations
1. **For Quality Priority**: Consider maintaining original resolution with optimized encoding
2. **For Bandwidth**: Current settings provide good balance of quality vs size
3. **For Mobile**: Current transcoding is well-suited for mobile delivery

## Potential Causes
- Transcoding profile configured for mobile/web delivery
- Bandwidth optimization settings applied
- Standard definition output target specified
"""
```

---

## 🎯 Use Cases

### 1. **Quality Assurance**
```python
# Validate transcoding quality
original_info = analyzer.extract_video_info('s3://bucket/original.mp4')
transcoded_info = analyzer.extract_video_info('s3://bucket/transcoded.mp4')

differences = analyzer.compare_videos(original_info, transcoded_info)
quality_report = analyzer.analyze_differences(differences)

# Automated quality checks
if differences['video_differences'].get('bitrate_change', 0) < -50:
    print("⚠️  Significant quality reduction detected")
```

### 2. **Migration Validation**
```python
# Compare Encoding.com vs MediaConvert outputs
encoding_com_video = analyzer.extract_video_info('s3://bucket/encoding_com_output.mp4')
mediaconvert_video = analyzer.extract_video_info('s3://bucket/mediaconvert_output.mp4')

migration_analysis = analyzer.compare_videos(encoding_com_video, mediaconvert_video)
migration_report = analyzer.analyze_differences(migration_analysis)
```

### 3. **Batch Analysis**
```python
# Analyze multiple video pairs
video_pairs = [
    ('s3://bucket/original1.mp4', 's3://bucket/transcoded1.mp4'),
    ('s3://bucket/original2.mp4', 's3://bucket/transcoded2.mp4'),
    # ... more pairs
]

for original, transcoded in video_pairs:
    differences = analyzer.compare_videos(original, transcoded)
    analysis = analyzer.analyze_differences(differences)
    
    # Save analysis results
    with open(f'analysis_{original.split("/")[-1]}.txt', 'w') as f:
        f.write(analysis)
```

### 4. **Performance Monitoring**
```python
# Monitor transcoding performance over time
def analyze_transcoding_batch(input_videos, output_videos):
    results = []
    
    for input_video, output_video in zip(input_videos, output_videos):
        start_time = time.time()
        
        # Extract and compare
        input_info = analyzer.extract_video_info(input_video)
        output_info = analyzer.extract_video_info(output_video)
        differences = analyzer.compare_videos(input_info, output_info)
        
        analysis_time = time.time() - start_time
        
        results.append({
            'input': input_video,
            'output': output_video,
            'differences': differences,
            'analysis_time': analysis_time
        })
    
    return results
```

---

## 🔍 Advanced Features

### Custom Analysis Prompts

```python
# Customize AI analysis prompts
custom_prompt = """
Analyze these video differences focusing on:
1. Encoding efficiency improvements
2. Compatibility with streaming platforms
3. Mobile device optimization
4. Bandwidth usage implications

Differences: {differences}
"""

analyzer = VideoAnalyzer(region='us-east-1')
analyzer.set_analysis_prompt(custom_prompt)

analysis = analyzer.analyze_differences(differences)
```

### Parallel Processing

```python
import concurrent.futures

def analyze_video_pair(video_pair):
    original, transcoded = video_pair
    differences = analyzer.compare_videos(original, transcoded)
    return analyzer.analyze_differences(differences)

# Process multiple video pairs in parallel
video_pairs = [
    ('s3://bucket/vid1_orig.mp4', 's3://bucket/vid1_trans.mp4'),
    ('s3://bucket/vid2_orig.mp4', 's3://bucket/vid2_trans.mp4'),
    # ... more pairs
]

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    analyses = list(executor.map(analyze_video_pair, video_pairs))
```

### Error Handling and Retry Logic

```python
import time
from botocore.exceptions import ClientError

def robust_video_analysis(video_url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return analyzer.extract_video_info(video_url)
        except ClientError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e
```

---

## 📈 Performance Optimization

### Caching Results

```python
import json
import hashlib

class CachedVideoAnalyzer(VideoAnalyzer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = {}
    
    def extract_video_info(self, video_url):
        # Create cache key
        cache_key = hashlib.md5(video_url.encode()).hexdigest()
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Extract info and cache result
        info = super().extract_video_info(video_url)
        self.cache[cache_key] = info
        return info
```

### Batch Operations

```python
# Optimize for batch processing
def batch_extract_info(video_urls):
    """Extract info for multiple videos efficiently"""
    results = {}
    
    # Group by S3 bucket for better performance
    bucket_groups = {}
    for url in video_urls:
        bucket = url.split('/')[2]
        if bucket not in bucket_groups:
            bucket_groups[bucket] = []
        bucket_groups[bucket].append(url)
    
    # Process each bucket group
    for bucket, urls in bucket_groups.items():
        for url in urls:
            results[url] = analyzer.extract_video_info(url)
    
    return results
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **ffmpeg Not Found**
```bash
# Check if ffmpeg is installed
which ffmpeg
which ffprobe

# Install if missing (see installation section above)
```

#### 2. **S3 Access Denied**
```python
# Test S3 access
import boto3

s3 = boto3.client('s3')
try:
    response = s3.head_object(Bucket='your-bucket', Key='video.mp4')
    print("✓ S3 access working")
except Exception as e:
    print(f"✗ S3 access failed: {e}")
```

#### 3. **Bedrock Access Issues**
```python
# Test Bedrock access
import boto3

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
try:
    response = bedrock.list_foundation_models()
    print("✓ Bedrock access working")
except Exception as e:
    print(f"✗ Bedrock access failed: {e}")
```

#### 4. **Large Video Timeouts**
```python
# Increase timeout for large videos
analyzer = VideoAnalyzer(
    region='us-east-1',
    timeout=300  # 5 minutes
)
```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

analyzer = VideoAnalyzer(region='us-east-1')
analyzer.set_debug_mode(True)

# This will show detailed ffmpeg commands and AWS API calls
video_info = analyzer.extract_video_info('s3://bucket/video.mp4')
```

---

## 📚 API Reference

### VideoAnalyzer Class

```python
class VideoAnalyzer:
    def __init__(self, region='us-east-1', timeout=60):
        """Initialize video analyzer with AWS region and timeout"""
    
    def extract_video_info(self, video_url: str) -> dict:
        """Extract comprehensive video information from S3 video"""
    
    def compare_videos(self, video1_info: dict, video2_info: dict) -> dict:
        """Compare two video information dictionaries"""
    
    def analyze_differences(self, differences: dict) -> str:
        """Analyze differences using Claude 3.5 and return insights"""
    
    def set_analysis_prompt(self, prompt_template: str):
        """Set custom prompt template for AI analysis"""
    
    def set_debug_mode(self, enabled: bool):
        """Enable/disable debug logging"""
```

### Command Line Interface

```bash
# Main command
e2mc-analyzer <command> [options]

# Commands:
#   extract     Extract video information
#   compare     Compare two videos
#   analyze     Analyze differences with AI
#   analyze-json Analyze existing differences JSON

# Global options:
#   --region    AWS region (default: us-east-1)
#   --verbose   Enable verbose logging
#   --output    Output file path
```

---

## 🤝 Contributing

### Adding New Analysis Features

1. **Extend VideoAnalyzer class** with new methods
2. **Add corresponding CLI commands** in the main module
3. **Update tests** to cover new functionality
4. **Document new features** in this README

### Custom Analyzers

```python
class CustomVideoAnalyzer(VideoAnalyzer):
    def analyze_encoding_efficiency(self, video_info):
        """Custom analysis for encoding efficiency"""
        # Your custom analysis logic
        pass
    
    def detect_quality_issues(self, differences):
        """Custom quality issue detection"""
        # Your custom detection logic
        pass
```

---

## 📄 License

This module is part of E2MC Assistant and is licensed under the MIT License.
