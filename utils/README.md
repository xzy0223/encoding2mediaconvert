# S3 Video Organization Utility

This utility organizes videos from encoding.com into a structured S3 bucket layout based on encoding profiles.

## Overview

The script performs the following tasks:

1. Scans the source S3 bucket (`fw-mc-profile`) for original and encoding-generated videos
2. Maps each video ID to its corresponding encoding profile category
3. Copies the videos to the target S3 bucket (`fw-mc-test`) with a structured organization:
   - First level: Encoding profile category (e.g., `mp4`, `advanced_hls`)
   - Second level: Profile ID (e.g., `1002`, `1003`)
   - Files: Original source videos and encoding-generated videos

## File Structure

The resulting S3 structure will look like:

```
s3://fw-mc-test/
├── mp4/
│   ├── 1002/
│   │   ├── 1002_552686815_source.mp4
│   │   └── 1002_552686815_target.mp4
│   ├── 1003/
│   │   ├── 1003_825654110_source.mp4
│   │   └── 1003_825654110_target.mp4
│   └── ...
├── advanced_hls/
│   ├── 1019/
│   │   ├── 1019_123456789_source.mp4
│   │   └── 1019_123456789_target.m3u8
│   └── ...
└── ...
```

## Usage

```bash
# Run in dry-run mode (no files copied)
python organize_s3_videos.py --dry-run

# Run the actual copy operation
python organize_s3_videos.py

# Specify custom bucket names
python organize_s3_videos.py --source-bucket my-source-bucket --target-bucket my-target-bucket

# Specify custom profiles directory
python organize_s3_videos.py --profiles-dir /path/to/profiles
```

## Requirements

- Python 3.6+
- boto3
- AWS credentials configured with access to both source and target S3 buckets
