# Changelog

All notable changes to the E2MC Assistant project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-04

### Added
- Initial release of E2MC Assistant
- **ConfigConverter**: XML to JSON configuration conversion with rule-based mapping
- **VideoAnalyzer**: Video analysis and comparison using AWS Bedrock (Claude 3.5)
- **MediaConvertJobSubmitter**: AWS MediaConvert job submission and management
- **E2MCWorkflow**: End-to-end workflow automation
- **Configuration Validation**: JSON schema validation for MediaConvert configurations
- **Command Line Tools**: 
  - `e2mc-converter` for configuration conversion
  - `e2mc-analyzer` for video analysis
  - `e2mc-submitter` for job submission
  - `e2mc-workflow` for complete workflow automation
- **Comprehensive Documentation**: README files for each component
- **Rule System**: YAML-based mapping rules with complex condition support
- **Template System**: JSON templates for different output formats
- **Batch Processing**: Support for processing multiple files
- **Error Handling**: Detailed error logging and analysis
- **Multi-format Support**: MP4, HLS, DASH, CMAF, WebM, and more

### Features
- Convert Encoding.com XML configurations to AWS MediaConvert JSON
- Analyze and compare video files using AI-powered analysis
- Submit and monitor MediaConvert transcoding jobs
- Validate configurations against JSON schemas
- Support for complex multi-stream configurations
- Extensible transformation functions
- Comprehensive logging and error reporting

### Dependencies
- Python 3.6+
- PyYAML >= 5.1
- boto3 >= 1.26.0
- jsonschema >= 4.0.0

### Documentation
- Complete API documentation
- Usage examples and tutorials
- Rule configuration guide
- Multi-condition documentation
- Component-specific README files