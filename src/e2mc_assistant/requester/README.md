# AWS MediaConvert Job Submitter

This tool submits transcoding jobs to AWS MediaConvert service. It loads a MediaConvert job configuration file, allows customization of input file URLs and output destinations, and submits the job to AWS MediaConvert.

## Features

- Load MediaConvert job profiles from JSON files
- Customize input file URLs before submission
- Customize output destinations before submission
- Support for different output group types (FILE, HLS, DASH, CMAF, MS_SMOOTH)
- Automatic endpoint URL discovery
- Custom IAM role support
- Detailed logging

## Installation

```bash
# Install dependencies
pip install boto3
```

## Usage

### Basic Usage

```bash
python mediaconvert_job_submitter.py --profile-path /path/to/profile.json \
                                    --input-url s3://bucket/input.mp4 \
                                    --output-destination s3://bucket/output/
```

### Advanced Usage

```bash
python mediaconvert_job_submitter.py --profile-path /path/to/profile.json \
                                    --input-url s3://bucket/input.mp4 \
                                    --output-destination s3://bucket/output/ \
                                    --region us-west-2 \
                                    --role-arn arn:aws:iam::123456789012:role/MediaConvertRole \
                                    --verbose
```

## Command Line Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--profile-path` | Path to the MediaConvert job profile JSON file | Yes |
| `--input-url` | Input file URL (S3 path) | Yes |
| `--output-destination` | Output destination (S3 path) | Yes |
| `--region` | AWS region (default: us-east-1) | No |
| `--endpoint-url` | MediaConvert endpoint URL | No |
| `--role-arn` | IAM role ARN for MediaConvert | No |
| `--verbose` | Enable verbose logging | No |

## Example

Using a profile from the examples directory:

```bash
python mediaconvert_job_submitter.py \
    --profile-path ../../tranformed_mc_profiles/examples/1-setting.json \
    --input-url s3://my-bucket/input/video.mp4 \
    --output-destination s3://my-bucket/output/ \
    --region us-east-1
```

## Using as a Module

You can also use the `MediaConvertJobSubmitter` class in your own Python code:

```python
from mediaconvert_job_submitter import MediaConvertJobSubmitter

# Initialize the submitter
submitter = MediaConvertJobSubmitter(region='us-east-1')

# Load a job profile
job_profile = submitter.load_job_profile('path/to/profile.json')

# Update input and output paths
job_profile = submitter.update_input_url(job_profile, 's3://bucket/input.mp4')
job_profile = submitter.update_output_destination(job_profile, 's3://bucket/output/')

# Submit the job
response = submitter.submit_job(job_profile)

# Get the job ID
job_id = response['Job']['Id']
print(f"Job submitted with ID: {job_id}")
```

## AWS Permissions

The AWS credentials used to run this script must have permissions to:

1. Call `mediaconvert:DescribeEndpoints`
2. Call `mediaconvert:CreateJob`
3. Access the input and output S3 buckets

If using a role ARN, the role must have these permissions and a trust relationship with MediaConvert.
