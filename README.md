# Encoding.com to AWS MediaConvert Assistant

This project provides tools for converting Encoding.com configurations to AWS MediaConvert,
analyzing configurations, managing pilot programs, and performing error analysis.

## Project Structure

- `encoding_profiles/` - Contains encoding profile configurations
- `source_profile/` - Original source profile files
- `tranformed_mc_profiles/` - Transformed MediaConvert profiles
- `utils/` - Utility functions and helper scripts
- `src/` - Core source code for the converter and analyzer

## Components

### Core Components

- **Converter**: Converts Encoding.com XML configuration files to AWS MediaConvert JSON configuration files
- **Video Analyzer**: Analyzes video files, compares them, and identifies differences using Claude 3.5 on Bedrock
- **Requester**: Makes API requests to AWS MediaConvert

### Analysis Tools

- **Error Analyzer** (`analyze_errors_with_ids.py`): Analyzes and categorizes errors in MediaConvert jobs
- **Error Summary** (`error_summary_with_ids.md`): Detailed documentation of error patterns and solutions
- **Analysis Summary** (`analysis_summary.json`): JSON format summary of analysis results

### Pilot Program Tools

- **Profile Organizer** (`organize_pilot_files.py`): Organizes and manages pilot program files
- **Format Specifications** (`pilot_formats_v2.csv`): Defines supported formats for the pilot program

## Installation

```bash
# Install in development mode
pip install -e .
```

## Usage

### Converter

```bash
# Basic usage
e2mc-converter --source input.xml --rules rules.yaml --output output.json

# Using a template
e2mc-converter --source input.xml --rules rules.yaml --template template.json --output output.json

# Batch processing
e2mc-converter --source /path/to/xml/files --rules rules.yaml --output /path/to/output --batch
```

### Video Analyzer

```bash
# Extract video information
python -m e2mc_assistant.analyzer.video_analyzer extract s3://bucket-name/path/to/video.mp4 --output info.json

# Compare two videos
python -m e2mc_assistant.analyzer.video_analyzer compare s3://bucket-name/video1.mp4 s3://bucket-name/video2.mp4 --output differences.json

# Analyze differences using Claude 3.5
python -m e2mc_assistant.analyzer.video_analyzer analyze s3://bucket-name/video1.mp4 s3://bucket-name/video2.mp4 --output analysis.txt
```

### Error Analysis

```bash
# Analyze errors with job IDs
python analyze_errors_with_ids.py --input-file error_logs.json --output-file error_summary.md

# Organize pilot files
python organize_pilot_files.py --input-csv pilot_formats_v2.csv --output-dir organized_profiles
```

### Python API

```python
# Converter API
from e2mc_assistant.converter import ConfigConverter

converter = ConfigConverter('path/to/rules.yaml')
result = converter.convert('input.xml', 'template.json')

# Video Analyzer API
from e2mc_assistant.analyzer.video_analyzer import VideoAnalyzer

analyzer = VideoAnalyzer()
video_info = analyzer.extract_video_info('s3://bucket-name/path/to/video.mp4')
```

## Documentation

For detailed documentation on each component, please refer to the README.md files in the respective directories:

- [Converter Documentation](src/e2mc_assistant/converter/README.md)
- [Converter API Documentation](src/e2mc_assistant/converter/documentation.md)
- [Video Analyzer Documentation](src/e2mc_assistant/analyzer/README.md)
- [Error Analysis Documentation](error_summary_with_ids.md)

## Project Files

- `mc_template.json` - Base template for MediaConvert job configurations
- `setup.py` - Project setup and dependencies
- `MANIFEST.in` - Installation manifest
- `.gitignore` - Git ignore rules
- `analysis_summary.json` - Summary of analysis results

## License

MIT
