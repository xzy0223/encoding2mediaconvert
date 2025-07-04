# 📤 MediaConvert Job Submitter - AWS MediaConvert Job Management

[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![AWS MediaConvert](https://img.shields.io/badge/AWS-MediaConvert-orange.svg)](https://aws.amazon.com/mediaconvert/)
[![Boto3](https://img.shields.io/badge/AWS-Boto3-yellow.svg)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

The **MediaConvert Job Submitter** is a powerful component of E2MC Assistant that handles AWS MediaConvert job submission, monitoring, and management with enterprise-grade features.

---

## 🌟 Key Features

### 🚀 **Job Management**
- **Intelligent Job Submission**: Submit jobs with automatic configuration validation
- **Real-time Monitoring**: Track job progress with live status updates
- **Batch Processing**: Submit multiple jobs simultaneously
- **Job Queuing**: Manage job priorities and queuing strategies

### 🔧 **Advanced Configuration**
- **Dynamic Input/Output**: Customize S3 paths at runtime
- **Multi-Format Support**: Handle all MediaConvert output formats
- **Role Management**: Flexible IAM role assignment
- **Endpoint Discovery**: Automatic MediaConvert endpoint resolution

### 📊 **Monitoring & Analytics**
- **Progress Tracking**: Real-time job progress monitoring
- **Status Reporting**: Comprehensive job status information
- **Error Analysis**: Detailed error reporting and diagnostics
- **Performance Metrics**: Job duration and throughput analysis

### 🛡️ **Enterprise Features**
- **Error Handling**: Robust retry logic and error recovery
- **Logging**: Comprehensive logging for debugging and auditing
- **Security**: IAM role-based access control
- **Scalability**: Handle high-volume job submissions

---

## 🚀 Quick Start

### Command Line Usage

```bash
# Submit a single job
e2mc-submitter \
  --profile-path config.json \
  --input-url s3://input-bucket/video.mp4 \
  --output-destination s3://output-bucket/ \
  --track-job

# Submit with custom role and region
e2mc-submitter \
  --profile-path config.json \
  --input-url s3://input-bucket/video.mp4 \
  --output-destination s3://output-bucket/ \
  --region us-west-2 \
  --role-arn arn:aws:iam::123456789012:role/MediaConvertRole \
  --verbose

# List recent jobs
e2mc-submitter --list-jobs --max-results 10

# Track existing job
e2mc-submitter --job-id 1234567890123-abcdef --track-job

# Cancel a job
e2mc-submitter --cancel-job 1234567890123-abcdef
```

### Python API

```python
from e2mc_assistant.requester.mediaconvert_job_submitter import MediaConvertJobSubmitter

# Initialize submitter
submitter = MediaConvertJobSubmitter(region='us-east-1')

# Load and prepare job profile
job_profile = submitter.load_job_profile('config.json')
job_profile = submitter.update_input_url(job_profile, 's3://input-bucket/video.mp4')
job_profile = submitter.update_output_destination(job_profile, 's3://output-bucket/')

# Submit job
response = submitter.submit_job(job_profile)
job_id = response['Job']['Id']

# Track job progress
final_job = submitter.track_job(job_id, poll_interval=30)
print(f"Job completed with status: {final_job['Status']}")
```

---

## 📋 Prerequisites

### AWS Services & Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "mediaconvert:CreateJob",
                "mediaconvert:GetJob",
                "mediaconvert:ListJobs",
                "mediaconvert:CancelJob",
                "mediaconvert:DescribeEndpoints"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::input-bucket/*",
                "arn:aws:s3:::output-bucket/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::*:role/MediaConvert*"
        }
    ]
}
```

### MediaConvert Service Role

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "*"
        }
    ]
}
```

---

## 🔧 Configuration

### Job Profile Structure

```json
{
    "Settings": {
        "Inputs": [{
            "FileInput": "{SOURCE_S3_URL}",
            "VideoSelector": {},
            "AudioSelectors": {
                "Audio Selector 1": {
                    "DefaultSelection": "DEFAULT"
                }
            }
        }],
        "OutputGroups": [{
            "OutputGroupSettings": {
                "Type": "FILE_GROUP_SETTINGS",
                "FileGroupSettings": {
                    "Destination": "{DEST_S3_URL}"
                }
            },
            "Outputs": [{
                "VideoDescription": {
                    "CodecSettings": {
                        "Codec": "H_264",
                        "H264Settings": {
                            "RateControlMode": "VBR",
                            "Bitrate": 2000000
                        }
                    }
                },
                "AudioDescriptions": [{
                    "CodecSettings": {
                        "Codec": "AAC",
                        "AacSettings": {
                            "Bitrate": 128000,
                            "SampleRate": 48000
                        }
                    }
                }]
            }]
        }]
    }
}
```

### Environment Configuration

```bash
# AWS Configuration
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# MediaConvert Configuration
export MEDIACONVERT_ROLE_ARN=arn:aws:iam::123456789012:role/MediaConvertRole
export MEDIACONVERT_QUEUE=Default
```

---

## 📊 Job Management

### Job Submission

```python
# Basic job submission
submitter = MediaConvertJobSubmitter()

response = submitter.submit_job(
    profile_path='mp4_profile.json',
    input_url='s3://input/video.mp4',
    output_destination='s3://output/'
)

job_id = response['Job']['Id']
print(f"Job submitted: {job_id}")
```

### Advanced Job Submission

```python
# Initialize with custom role and endpoint
submitter = MediaConvertJobSubmitter(
    region='us-west-2',
    role_arn='arn:aws:iam::123456789012:role/CustomRole'
)

# Load and customize job profile
job_profile = submitter.load_job_profile('hls_profile.json')
job_profile = submitter.update_input_url(job_profile, 's3://input/video.mp4')
job_profile = submitter.update_output_destination(job_profile, 's3://output/hls/')

# Add custom metadata to job profile
job_profile['UserMetadata'] = {
    'project': 'video-migration',
    'customer': 'acme-corp',
    'priority': 'high'
}

# Submit job
response = submitter.submit_job(job_profile)
```

### Batch Job Submission

```python
# Submit multiple jobs manually
job_configs = [
    {
        'profile_path': 'mp4_profile.json',
        'input_url': 's3://input/video1.mp4',
        'output_destination': 's3://output/video1/'
    },
    {
        'profile_path': 'hls_profile.json',
        'input_url': 's3://input/video2.mp4',
        'output_destination': 's3://output/video2/'
    }
]

job_ids = []
for config in job_configs:
    # Load and prepare each job
    job_profile = submitter.load_job_profile(config['profile_path'])
    job_profile = submitter.update_input_url(job_profile, config['input_url'])
    job_profile = submitter.update_output_destination(job_profile, config['output_destination'])
    
    # Submit job
    response = submitter.submit_job(job_profile)
    job_ids.append(response['Job']['Id'])

print(f"Submitted {len(job_ids)} jobs: {job_ids}")
```

---

## 📈 Job Monitoring

### Real-time Tracking

```python
# Track job progress using the built-in track_job method
final_job = submitter.track_job(
    job_id='1234567890123-abcdef',
    poll_interval=15,  # Check every 15 seconds
    timeout=3600       # 1 hour timeout
)

print(f"Job completed with status: {final_job['Status']}")

# Get detailed job status at any time
job_status = submitter.get_job_status('1234567890123-abcdef')
print(f"Progress: {job_status.get('JobPercentComplete', 0)}%")
print(f"Current Phase: {job_status.get('CurrentPhase', 'Unknown')}")
```

### Batch Monitoring

```python
# Monitor multiple jobs by checking their status
job_ids = ['job1', 'job2', 'job3']

# Check status of all jobs
for job_id in job_ids:
    job_status = submitter.get_job_status(job_id)
    print(f"Job {job_id}: {job_status['Status']} - {job_status.get('JobPercentComplete', 0)}%")

# Track multiple jobs to completion (sequential)
results = {}
for job_id in job_ids:
    final_job = submitter.track_job(job_id, poll_interval=30)
    results[job_id] = final_job['Status']

for job_id, status in results.items():
    print(f"Job {job_id}: {status}")
```

### Job Status Analysis

```python
# Get detailed job information
job_details = submitter.get_job_status('1234567890123-abcdef')

print(f"Status: {job_details['Status']}")
print(f"Progress: {job_details.get('JobPercentComplete', 0)}%")
print(f"Created: {job_details['CreatedAt']}")
print(f"Current Phase: {job_details.get('CurrentPhase', 'Unknown')}")

if job_details['Status'] == 'ERROR':
    print(f"Error: {job_details.get('ErrorMessage', 'Unknown error')}")

# Get comprehensive metrics for completed jobs
if job_details['Status'] == 'COMPLETE':
    metrics = submitter.get_job_metrics('1234567890123-abcdef')
    print(f"Processing time: {metrics.get('elapsed_time_seconds', 0):.1f} seconds")
    print(f"Output groups: {len(metrics.get('output_group_details', []))}")
```

---

## 🎯 Use Cases

### 1. **Migration Validation**

```python
# Submit jobs for migration validation
validation_jobs = []

# Example: Submit a job using converted configuration
job_profile = submitter.load_job_profile('converted_config.json')
job_profile = submitter.update_input_url(job_profile, 's3://input/original_video.mp4')
job_profile = submitter.update_output_destination(job_profile, 's3://output/converted/')

response = submitter.submit_job(job_profile)
job_id = response['Job']['Id']

print(f"Migration validation job submitted: {job_id}")
```

### 2. **Quality Assurance Pipeline**

```python
# QA pipeline with multiple quality levels
quality_profiles = [
    'profiles/high_quality.json',
    'profiles/medium_quality.json',
    'profiles/low_quality.json'
]

qa_jobs = []
input_video = 's3://input/test_video.mp4'

for profile_path in quality_profiles:
    # Load and prepare each profile
    job_profile = submitter.load_job_profile(profile_path)
    job_profile = submitter.update_input_url(job_profile, input_video)
    job_profile = submitter.update_output_destination(job_profile, f's3://qa-bucket/{profile_path.split("/")[-1]}/')
    
    # Submit job
    response = submitter.submit_job(job_profile)
    qa_jobs.append(response['Job']['Id'])

# Check status of all QA jobs
for job_id in qa_jobs:
    job_status = submitter.get_job_status(job_id)
    print(f"QA Job {job_id}: {job_status['Status']}")
```

### 3. **Automated Retry Logic**

```python
import time

def submit_with_retry(submitter, profile_path, input_url, output_destination, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Load and prepare job profile
            job_profile = submitter.load_job_profile(profile_path)
            job_profile = submitter.update_input_url(job_profile, input_url)
            job_profile = submitter.update_output_destination(job_profile, output_destination)
            
            # Submit job
            response = submitter.submit_job(job_profile)
            job_id = response['Job']['Id']
            
            # Track job to completion
            final_job = submitter.track_job(job_id)
            
            if final_job['Status'] == 'COMPLETE':
                return job_id
            elif final_job['Status'] == 'ERROR':
                if attempt < max_retries - 1:
                    print(f"Job failed, retrying... (attempt {attempt + 2})")
                    continue
                else:
                    raise Exception(f"Job failed after {max_retries} attempts")
                    
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Submission failed, retrying... (attempt {attempt + 2})")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise e
```

### 4. **Cost Optimization**

```python
def estimate_duration(input_url):
    """Simplified duration estimation - replace with actual logic"""
    # This is a placeholder - you would implement actual duration detection
    return 60  # Assume 60 minutes for example

def cost_optimized_submission(submitter, jobs, budget_limit):
    submitted_jobs = []
    estimated_cost = 0
    
    for job_config in jobs:
        # Estimate job cost (simplified)
        duration_estimate = estimate_duration(job_config['input_url'])
        job_cost = duration_estimate * 0.0075  # $0.0075 per minute
        
        if estimated_cost + job_cost <= budget_limit:
            # Load and prepare job profile
            job_profile = submitter.load_job_profile(job_config['profile_path'])
            job_profile = submitter.update_input_url(job_profile, job_config['input_url'])
            job_profile = submitter.update_output_destination(job_profile, job_config['output_destination'])
            
            # Submit job
            response = submitter.submit_job(job_profile)
            submitted_jobs.append(response['Job']['Id'])
            estimated_cost += job_cost
        else:
            print(f"Budget limit reached. Skipping remaining jobs.")
            break
    
    return submitted_jobs, estimated_cost
```







---

## 🐛 Troubleshooting

### Common Issues

#### 1. **Job Submission Failures**

```python
# Debug job submission issues
try:
    response = submitter.submit_job(
        profile_path='config.json',
        input_url='s3://bucket/video.mp4',
        output_destination='s3://bucket/output/'
    )
except Exception as e:
    print(f"Submission failed: {e}")
    
    # Check common issues
    if "InvalidInput" in str(e):
        print("Check input file exists and is accessible")
    elif "InvalidRole" in str(e):
        print("Check IAM role permissions")
    elif "InvalidDestination" in str(e):
        print("Check output S3 bucket permissions")
```

#### 2. **Job Monitoring Issues**

```python
# Handle monitoring timeouts
def safe_job_tracking(job_id, max_wait_time=3600):
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            job_status = submitter.get_job_status(job_id)
            
            if job_status in ['COMPLETE', 'ERROR', 'CANCELED']:
                return job_status
                
            time.sleep(30)
            
        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(60)  # Wait longer on error
    
    print(f"Job monitoring timed out after {max_wait_time} seconds")
    return 'TIMEOUT'
```

#### 3. **Permission Issues**

```bash
# Test MediaConvert permissions
aws mediaconvert describe-endpoints --region us-east-1

# Test S3 permissions
aws s3 ls s3://your-input-bucket/
aws s3 ls s3://your-output-bucket/

# Test IAM role
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/MediaConvertRole --role-session-name test
```

### Debug Mode

```python
# Enable comprehensive debugging
import logging

logging.basicConfig(level=logging.DEBUG)

import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

submitter = MediaConvertJobSubmitter(region='us-east-1')

# This will show detailed logging including AWS API calls
response = submitter.submit_job(
    profile_path='config.json',
    input_url='s3://bucket/video.mp4',
    output_destination='s3://bucket/output/'
)
```

---

## 📚 API Reference

### MediaConvertJobSubmitter Class

```python
class MediaConvertJobSubmitter:
    def __init__(self, region: str = 'us-east-1', endpoint_url: str = None, role_arn: str = None):
        """Initialize job submitter with AWS region, endpoint, and role"""
    
    def load_job_profile(self, profile_path: str) -> dict:
        """Load MediaConvert job profile from JSON file"""
    
    def update_input_url(self, job_profile: dict, input_url: str, input_index: int = 0) -> dict:
        """Update input file URL in job profile"""
    
    def update_output_destination(self, job_profile: dict, output_destination: str, 
                                 output_group_index: int = 0) -> dict:
        """Update output destination in job profile"""
    
    def submit_job(self, job_profile: dict) -> dict:
        """Submit job to MediaConvert"""
    
    def get_job_status(self, job_id: str) -> dict:
        """Get current job status and details"""
    
    def track_job(self, job_id: str, poll_interval: int = 10, timeout: int = None) -> dict:
        """Track job progress until completion"""
    
    def list_jobs(self, status: str = None, max_results: int = 20) -> list:
        """List recent jobs with optional status filter"""
    
    def cancel_job(self, job_id: str) -> dict:
        """Cancel a running job"""
    
    def get_job_metrics(self, job_id: str) -> dict:
        """Get detailed metrics for completed job"""
    
    # Class constants
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_PROGRESSING = 'PROGRESSING'
    STATUS_COMPLETE = 'COMPLETE'
    STATUS_CANCELED = 'CANCELED'
    STATUS_ERROR = 'ERROR'
    TERMINAL_STATES = [STATUS_COMPLETE, STATUS_CANCELED, STATUS_ERROR]
```

### Command Line Interface

```bash
# Submit job
python -m e2mc_assistant.requester.mediaconvert_job_submitter \
  --profile-path CONFIG \
  --input-url INPUT \
  --output-destination OUTPUT

# Options:
#   --region REGION              AWS region (default: us-east-1)
#   --endpoint-url URL           Custom MediaConvert endpoint
#   --role-arn ROLE_ARN         IAM role ARN
#   --track-job                 Track job progress
#   --poll-interval SECONDS     Polling interval for tracking (default: 10)
#   --timeout SECONDS           Timeout for tracking
#   --verbose                   Enable verbose logging

# Job management:
#   --list-jobs                 List recent jobs
#   --job-id JOB_ID            Track specific job by ID
#   --cancel-job JOB_ID        Cancel specified job
#   --status-filter STATUS     Filter jobs by status
#   --max-results NUMBER       Maximum results to return (default: 20)
```

---

## 🤝 Contributing

### Adding New Features

1. **Extend MediaConvertJobSubmitter** with new methods
2. **Add CLI commands** in the main module
3. **Update tests** for new functionality
4. **Document changes** in this README



---

## 📄 License

This module is part of E2MC Assistant and is licensed under the MIT License.
