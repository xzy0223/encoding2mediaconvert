# Technology Stack

## Build System & Package Management
- **Python 3.6+** with setuptools
- **pip** for dependency management
- Package structure follows standard Python conventions with `src/` layout

## Core Dependencies
- **PyYAML** (>=5.1) - YAML configuration parsing for mapping rules
- **boto3** - AWS SDK for MediaConvert, S3, and Bedrock operations
- **xml.etree.ElementTree** - XML parsing for Encoding.com configurations
- **jsonschema** - Configuration validation

## AWS Services Integration
- **AWS MediaConvert** - Video transcoding service
- **AWS S3** - File storage and retrieval
- **AWS Bedrock (Claude 3.5)** - AI-powered video analysis
- **AWS IAM** - Role-based access for MediaConvert jobs

## Common Commands

### Installation
```bash
# Development installation
pip install -e .

# Production installation
pip install .
```

### CLI Usage
```bash
# Convert single configuration
e2mc-converter --source input.xml --rules rules.yaml --output output.json

# Batch conversion with template
e2mc-converter --source /path/to/xml/files --rules rules.yaml --template template.json --output /path/to/output --batch

# Video analysis
python -m e2mc_assistant.analyzer.video_analyzer compare s3://bucket/video1.mp4 s3://bucket/video2.mp4

# Full workflow execution
python -m e2mc_assistant.workflow.e2mc_workflow --config-dir configs/ --s3-path s3://bucket/videos/
```

### Development
```bash
# Run with verbose logging
python config_converter_enhanced.py --source input.xml --rules rules.yaml --output output.json --verbose

# Validate configurations
python -m utils.mc_config_validator.validator --config output.json --schema schema.json
```

## Architecture Patterns
- **Rule-based transformation** using YAML configuration files
- **Template-driven conversion** preserving MediaConvert job structure  
- **Modular component design** with clear separation of concerns
- **Extensible transformation functions** via custom function registration
- **Comprehensive logging** with file-specific log outputs