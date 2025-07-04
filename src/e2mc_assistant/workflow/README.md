# 🔄 E2MC Workflow - End-to-End Migration Automation

[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-MediaConvert-orange.svg)](https://aws.amazon.com/mediaconvert/)
[![Automation](https://img.shields.io/badge/automation-workflow-purple.svg)](#)

The **E2MC Workflow** provides a complete automation solution for migrating from Encoding.com to AWS MediaConvert, handling configuration conversion, job submission, and video analysis in a single integrated workflow.

---

## 🌟 Key Features

### 🚀 **Three Main Commands**
- **convert**: Convert Encoding.com XML configurations to MediaConvert JSON
- **submit**: Submit MediaConvert jobs and track their execution
- **analyze**: Compare original and transcoded videos
- **workflow**: Run the complete end-to-end process

### 🔧 **Flexible Processing**
- **Selective Processing**: Include/exclude specific video IDs
- **Batch Operations**: Process multiple configurations simultaneously
- **S3 Integration**: Direct integration with S3 for video storage
- **Comprehensive Logging**: Detailed logs for each step and video ID

### 📊 **Monitoring & Analysis**
- **Job Tracking**: Real-time MediaConvert job monitoring
- **Video Comparison**: Automated analysis of transcoded videos
- **Error Reporting**: Detailed error logs for failed operations
- **Summary Reports**: Consolidated execution summaries

---

## 🚀 Quick Start

### Command Line Usage

```bash
# Run complete end-to-end workflow
python -m e2mc_assistant.workflow.e2mc_workflow workflow \
  --input-dir encoding_profiles/mp4/ \
  --output-dir converted_profiles/ \
  --rules-file rules/e2mc_rules.yaml \
  --s3-source-path s3://bucket/videos/ \
  --region us-east-1

# Convert configurations only
python -m e2mc_assistant.workflow.e2mc_workflow convert \
  --input-dir encoding_profiles/mp4/ \
  --output-dir converted_profiles/ \
  --rules-file rules/e2mc_rules.yaml

# Submit MediaConvert jobs only
python -m e2mc_assistant.workflow.e2mc_workflow submit \
  --config-dir converted_profiles/ \
  --s3-source-path s3://bucket/videos/ \
  --region us-east-1

# Analyze videos only
python -m e2mc_assistant.workflow.e2mc_workflow analyze \
  --s3-path s3://bucket/videos/ \
  --region us-east-1
```

### Python API

```python
from e2mc_assistant.workflow.e2mc_workflow import E2MCWorkflow

# Initialize workflow
workflow = E2MCWorkflow(region='us-east-1', role_arn='arn:aws:iam::123456789012:role/MediaConvertRole')

# Convert configurations
converted_files = workflow.convert_configs(
    input_dir='encoding_profiles/mp4/',
    output_dir='converted_profiles/',
    rules_file='rules/e2mc_rules.yaml'
)

# Submit MediaConvert jobs
job_results = workflow.submit_mediaconvert_jobs(
    config_dir='converted_profiles/',
    s3_source_path='s3://bucket/videos/',
    wait_for_completion=True
)

# Analyze videos
analysis_results = workflow.analyze_videos(
    s3_path='s3://bucket/videos/'
)
```

---

## 📋 Prerequisites

### System Requirements
- **Python 3.6+**
- **AWS CLI configured** with appropriate permissions
- **ffmpeg/ffprobe** (for video analysis)

### AWS Services & Permissions
- **AWS MediaConvert**: Job submission and management
- **Amazon S3**: Input/output file storage
- **AWS Bedrock**: AI-powered video analysis (optional)
- **AWS IAM**: Service role permissions

### Required IAM Permissions

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
                "s3:ListBucket",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
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

The MediaConvert service needs a role to access S3 resources:

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

## 🔧 Command Options

### Common Options

All commands support these common options:

- `--region`: AWS region (default: us-east-1)
- `--include`: Comma-separated list of video IDs to include
- `--exclude`: Comma-separated list of video IDs to exclude

### Convert Command

```bash
python -m e2mc_assistant.workflow.e2mc_workflow convert [options]
```

**Required Options:**
- `--input-dir`: Directory containing Encoding.com XML files
- `--output-dir`: Directory to save MediaConvert JSON files
- `--rules-file`: Path to the mapping rules YAML file

**Optional Options:**
- `--template-file`: Path to a template MediaConvert file
- `--validate`: Path to JSON schema file for validation

### Submit Command

```bash
python -m e2mc_assistant.workflow.e2mc_workflow submit [options]
```

**Required Options:**
- `--config-dir`: Directory containing MediaConvert JSON files
- `--s3-source-path`: S3 path where source videos are stored

**Optional Options:**
- `--role-arn`: IAM role ARN for MediaConvert
- `--no-wait`: Don't wait for jobs to complete

### Analyze Command

```bash
python -m e2mc_assistant.workflow.e2mc_workflow analyze [options]
```

**Required Options:**
- `--s3-path`: S3 path containing videos to analyze

**Optional Options:**
- `--use-llm`: Use Amazon Bedrock for AI-powered analysis

### Workflow Command

```bash
python -m e2mc_assistant.workflow.e2mc_workflow workflow [options]
```

**Required Options:**
- `--input-dir`: Directory containing Encoding.com XML files
- `--output-dir`: Directory to save MediaConvert JSON files
- `--rules-file`: Path to the mapping rules YAML file
- `--s3-source-path`: S3 path where source videos are stored

**Optional Options:**
- `--template-file`: Path to a template MediaConvert file
- `--role-arn`: IAM role ARN for MediaConvert
- `--no-wait`: Don't wait for jobs to complete

---

## 🎯 Workflow Operations

### 1. Configuration Conversion

Converts Encoding.com XML files to MediaConvert JSON configurations:

- Processes all XML files in the input directory
- Applies mapping rules from the YAML rules file
- Generates detailed conversion logs for each file
- Optional validation against MediaConvert schema
- Creates error files for failed conversions

### 2. Job Submission

Submits MediaConvert jobs for each configuration:

- Loads MediaConvert JSON configurations
- Finds corresponding source videos in S3
- Submits jobs to AWS MediaConvert
- Optionally waits for job completion
- Creates detailed job logs and error files
- Uploads configuration files to S3 with timestamps

### 3. Video Analysis

Analyzes and compares transcoded videos:

- Supports HLS (.m3u8) and DASH (.mpd) formats
- Extracts video metadata using ffmpeg
- Compares original and transcoded videos
- Generates comprehensive analysis reports
- Saves reports to S3 for review

### 4. Selective Processing

All operations support selective processing:

- `--include`: Process only specified video IDs
- `--exclude`: Skip specified video IDs
- Useful for testing or processing subsets

---

## 🚀 Usage Examples

### Example 1: Complete Workflow

```bash
# Run the complete end-to-end workflow
python -m e2mc_assistant.workflow.e2mc_workflow workflow \
  --input-dir encoding_profiles/mp4/ \
  --output-dir converted_profiles/ \
  --rules-file rules/e2mc_rules.yaml \
  --s3-source-path s3://my-bucket/videos/ \
  --region us-east-1 \
  --role-arn arn:aws:iam::123456789012:role/MediaConvertRole
```

### Example 2: Selective Processing

```bash
# Process only specific video IDs
python -m e2mc_assistant.workflow.e2mc_workflow workflow \
  --input-dir encoding_profiles/mp4/ \
  --output-dir converted_profiles/ \
  --rules-file rules/e2mc_rules.yaml \
  --s3-source-path s3://my-bucket/videos/ \
  --include 123,456,789

# Exclude specific video IDs
python -m e2mc_assistant.workflow.e2mc_workflow workflow \
  --input-dir encoding_profiles/mp4/ \
  --output-dir converted_profiles/ \
  --rules-file rules/e2mc_rules.yaml \
  --s3-source-path s3://my-bucket/videos/ \
  --exclude 999,888
```

### Example 3: Step-by-Step Processing

```bash
# Step 1: Convert configurations only
python -m e2mc_assistant.workflow.e2mc_workflow convert \
  --input-dir encoding_profiles/mp4/ \
  --output-dir converted_profiles/ \
  --rules-file rules/e2mc_rules.yaml

# Step 2: Submit jobs without waiting
python -m e2mc_assistant.workflow.e2mc_workflow submit \
  --config-dir converted_profiles/ \
  --s3-source-path s3://my-bucket/videos/ \
  --no-wait

# Step 3: Analyze videos later
python -m e2mc_assistant.workflow.e2mc_workflow analyze \
  --s3-path s3://my-bucket/videos/ \
  --use-llm
```

### Example 4: Python API Usage

```python
from e2mc_assistant.workflow.e2mc_workflow import E2MCWorkflow

# Initialize workflow
workflow = E2MCWorkflow(
    region='us-east-1',
    role_arn='arn:aws:iam::123456789012:role/MediaConvertRole'
)

# Convert configurations
converted_files = workflow.convert_configs(
    input_dir='encoding_profiles/mp4/',
    output_dir='converted_profiles/',
    rules_file='rules/e2mc_rules.yaml'
)
print(f"Converted {len(converted_files)} files")

# Submit jobs with selective processing
job_results = workflow.submit_mediaconvert_jobs(
    config_dir='converted_profiles/',
    s3_source_path='s3://my-bucket/videos/',
    wait_for_completion=True,
    include_ids=['123', '456']  # Process only these IDs
)
print(f"Submitted {len(job_results)} jobs")

# Analyze videos
analysis_results = workflow.analyze_videos(
    s3_path='s3://my-bucket/videos/',
    exclude_ids=['999']  # Skip this ID
)
print(f"Analyzed {len(analysis_results)} video pairs")
```

---

## 📊 Output and Logging

### Generated Files

The workflow creates several types of output files:

#### Conversion Step
- `{id}.json`: Converted MediaConvert configuration
- `{id}_conversion.log`: Detailed conversion log for each file
- `{id}.err`: Error file for failed conversions (if any)
- `conversion_details.log`: Overall conversion summary

#### Job Submission Step
- `{id}_job_submission.log`: Job submission details
- `{id}_job_execution.err`: Error details for failed jobs
- `job_execution_summary.log`: Summary of all job submissions

#### Analysis Step
- Analysis reports saved to S3 in the video's directory
- Comparison results for HLS and DASH formats
- Video metadata and difference reports

### S3 Structure

The workflow organizes files in S3 as follows:

```
s3://bucket/prefix/
├── {video_id}/
│   ├── {video_id}_source.mp4          # Original video
│   ├── {video_id}_mc_output.mp4       # MediaConvert output
│   ├── {video_id}_{timestamp}.json    # Configuration with timestamp
│   ├── update.log                     # Change history
│   └── reports/                       # Analysis reports
│       ├── comparison.json
│       └── metadata.json
```

---

## 🔍 Key Features

### Intelligent File Matching

The workflow automatically finds source videos in S3:

- Looks for files with `_source` in the filename first
- Falls back to any video file matching the ID pattern
- Excludes files with `_mc` or `_output` in the name
- Supports common video formats (.mp4, .mov, .mpg, .mpeg, .mxf, .webm)

### Error Handling

Comprehensive error handling and logging:

- Individual error files for each failed operation
- Detailed error messages and stack traces
- Continuation of processing even when individual files fail
- Summary reports showing success/failure counts

### S3 Integration

Direct S3 integration for video processing:

- Automatic S3 path parsing and validation
- Efficient S3 object listing and filtering
- Upload of configuration files with timestamps
- Maintenance of change history logs

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **No Source Videos Found**
```
Warning: No source video found for ID 123
```
**Solution**: Ensure source videos are in S3 with the correct naming pattern:
- `{id}_source.{ext}` (preferred)
- `{id}_{anything}.{ext}` (fallback)
- Avoid `_mc` or `_output` in filenames

#### 2. **MediaConvert Job Failures**
Check the error files created in the output directory:
- `{id}_job_execution.err`: Contains job failure details
- `{id}_job_submission.err`: Contains submission errors

#### 3. **Conversion Failures**
Check the conversion logs:
- `{id}_conversion.log`: Individual file conversion details
- `conversion_details.log`: Overall conversion summary
- `{id}.err`: Specific conversion errors

### Debug Mode

Enable verbose logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run the workflow
workflow = E2MCWorkflow(region='us-east-1')
```

---

## 📚 API Reference

### E2MCWorkflow Class

```python
class E2MCWorkflow:
    def __init__(self, region: str = 'us-east-1', role_arn: Optional[str] = None):
        """Initialize workflow with AWS region and optional role ARN"""
    
    def convert_configs(self, input_dir: str, output_dir: str, rules_file: str, 
                       template_file: Optional[str] = None, 
                       schema_file: Optional[str] = None) -> List[str]:
        """Convert Encoding.com XML files to MediaConvert JSON files"""
    
    def submit_mediaconvert_jobs(self, config_dir: str, s3_source_path: str, 
                                wait_for_completion: bool = True,
                                include_ids: Optional[List[str]] = None,
                                exclude_ids: Optional[List[str]] = None) -> Dict[str, str]:
        """Submit MediaConvert jobs for configuration files"""
    
    def analyze_videos(self, s3_path: str, 
                      include_ids: Optional[List[str]] = None,
                      exclude_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze and compare videos in S3"""
```

### Command Line Interface

```bash
# Main workflow command
python -m e2mc_assistant.workflow.e2mc_workflow [command] [options]

# Commands:
#   convert             Convert XML to JSON configurations
#   submit              Submit MediaConvert jobs
#   analyze             Analyze and compare videos
#   workflow            Run complete end-to-end workflow

# Common options:
#   --region REGION     AWS region (default: us-east-1)
#   --include IDS       Comma-separated list of IDs to include
#   --exclude IDS       Comma-separated list of IDs to exclude

# Convert options:
#   --input-dir PATH    Directory with XML files
#   --output-dir PATH   Directory for JSON files
#   --rules-file PATH   YAML rules file
#   --template-file PATH Optional template file
#   --validate PATH     Optional schema file for validation

# Submit options:
#   --config-dir PATH   Directory with JSON files
#   --s3-source-path URL S3 path with source videos
#   --role-arn ARN      MediaConvert service role
#   --no-wait           Don't wait for job completion

# Analyze options:
#   --s3-path URL       S3 path with videos to analyze
#   --use-llm           Use Amazon Bedrock for AI analysis

# Workflow options:
#   Combines all the above options for end-to-end processing
```

---

## 🤝 Contributing

### Adding New Features

1. **Extend E2MCWorkflow class** with new methods
2. **Add corresponding CLI commands** in the main function
3. **Update argument parser** with new options
4. **Add comprehensive error handling** and logging
5. **Update documentation** with usage examples

### Improving Analysis

1. **Extend VideoAnalyzer integration** for new formats
2. **Add support for additional video metadata**
3. **Improve comparison algorithms**
4. **Add new report formats**

---

## 📄 License

This module is part of E2MC Assistant and is licensed under the MIT License. See [LICENSE](../../../LICENSE) for full details.