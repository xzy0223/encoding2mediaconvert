# MediaConvert Configuration Validator

This tool validates AWS MediaConvert job configurations against a JSON schema to ensure they conform to the required format and constraints.

## Features

- Validates MediaConvert job configurations against a JSON schema
- Focuses on validating the "Settings" object in the configuration
- Provides detailed error messages for validation failures
- Checks for unknown parameters not defined in the schema
- Can be used as a command-line tool or imported as a module

## Usage

### Command Line

```bash
# Basic usage with default schema location
python validator.py --config-path /path/to/config.json

# Specify a custom schema file
python validator.py --config-path /path/to/config.json --schema /path/to/custom_schema.json
```

### As a Module

```python
from mc_config_validator import MediaConvertConfigValidator

validator = MediaConvertConfigValidator('/path/to/schema.json')
is_valid = validator.validate_config('/path/to/config.json')

if is_valid:
    print("Configuration is valid")
else:
    print("Configuration is invalid")
```

## Requirements

- Python 3.6+
- jsonschema library

## Installation

```bash
pip install jsonschema
```
