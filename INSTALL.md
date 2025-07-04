# Installation Guide

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- AWS credentials configured (for AWS services)

## Installation Methods

### 1. Development Installation (Recommended for development)

```bash
# Clone the repository
git clone https://github.com/xzy0223/encoding2mediaconvert.git
cd encoding2mediaconvert

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### 2. Production Installation

```bash
# Install from source
pip install .

# Or install with specific extras
pip install ".[test]"  # Include testing dependencies
pip install ".[docs]"  # Include documentation dependencies
```

### 3. Using requirements.txt

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

## Verification

After installation, verify that the command-line tools are available:

```bash
# Check converter
e2mc-converter --help

# Check analyzer
e2mc-analyzer --help

# Check job submitter
e2mc-submitter --help

# Check workflow tool
e2mc-workflow --help
```

## Python API Usage

```python
# Import main components
from e2mc_assistant import ConfigConverter, VideoAnalyzer, MediaConvertJobSubmitter

# Use the converter
converter = ConfigConverter('path/to/rules.yaml')
result = converter.convert('input.xml', 'template.json')

# Use the analyzer
analyzer = VideoAnalyzer()
video_info = analyzer.extract_video_info('s3://bucket/video.mp4')

# Use the job submitter
submitter = MediaConvertJobSubmitter()
response = submitter.submit_job(job_config)
```

## AWS Configuration

The tools require AWS credentials to be configured. You can set them up using:

### AWS CLI
```bash
aws configure
```

### Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### IAM Roles (for EC2 instances)
The tools will automatically use IAM roles if running on EC2.

## Required AWS Permissions

The tools need the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "mediaconvert:*",
                "s3:GetObject",
                "s3:PutObject",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you've installed the package correctly
2. **AWS Credentials**: Ensure AWS credentials are properly configured
3. **Permission Errors**: Check that your AWS user/role has the required permissions

### Getting Help

- Check the README.md for usage examples
- Review component-specific documentation in each module
- Check the GitHub issues for known problems