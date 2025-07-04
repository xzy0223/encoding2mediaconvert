# ✅ MediaConvert Configuration Validator

[![Python](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![JSON Schema](https://img.shields.io/badge/JSON-Schema-green.svg)](https://json-schema.org)
[![AWS MediaConvert](https://img.shields.io/badge/AWS-MediaConvert-orange.svg)](https://aws.amazon.com/mediaconvert/)

The **MediaConvert Configuration Validator** validates AWS MediaConvert job configurations against a JSON schema to ensure they conform to the required format and constraints.

---

## 🌟 Key Features

### 🔍 **Schema Validation**
- **JSON Schema Validation**: Validates against MediaConvert API schema using Draft7Validator
- **Settings Object Focus**: Specifically validates the "Settings" object in configurations
- **Complete Error Collection**: Collects all validation errors instead of stopping at the first one
- **Unknown Parameter Detection**: Identifies parameters not defined in the schema

### 📊 **Detailed Error Reporting**
- **Schema Validation Errors**: Reports structural and type validation errors
- **Unknown Parameter Errors**: Lists parameters not defined in the schema with valid alternatives
- **Path-based Error Messages**: Shows exact location of errors in the configuration
- **Comprehensive Logging**: Detailed logging for debugging and analysis

### 🔧 **Easy Integration**
- **Command Line Interface**: Simple CLI for validation tasks
- **Python API**: Programmatic validation for integration into workflows
- **Flexible Schema Support**: Use custom schema files or default schema

---

## 🚀 Quick Start

### Command Line Usage

```bash
# Basic validation with default schema
python validator.py --config-path config.json

# Validate with custom schema
python validator.py --config-path config.json --schema custom_schema.json
```

### Python API

```python
from mc_config_validator.validator import MediaConvertConfigValidator

# Initialize validator with schema file
validator = MediaConvertConfigValidator('mc_setting_schema.json')

# Validate configuration file
is_valid = validator.validate_config('config.json')

if is_valid:
    print("✓ Configuration is valid")
else:
    print("✗ Configuration is invalid")
```

---

## 📋 Prerequisites

### System Requirements
- **Python 3.6+**
- **jsonschema** library

### Installation

```bash
# Install required dependency
pip install jsonschema
```

---

## 🔧 Files

### Project Structure

```
mc_config_validator/
├── validator.py                 # Main validator implementation
├── mc_setting_schema.json       # MediaConvert schema for validation
├── mc_template.json            # Base template example
└── README.md                   # This documentation
```

### Schema File

The validator uses a JSON Schema file (`mc_setting_schema.json`) that defines the structure and constraints for MediaConvert job configurations. The schema follows JSON Schema Draft 7 specification.

---

## 📊 Validation Process

### What Gets Validated

The validator performs the following checks:

1. **JSON Structure**: Ensures the configuration file contains valid JSON
2. **Settings Object**: Verifies the presence of the required "Settings" object
3. **Schema Compliance**: Validates the Settings object against the JSON schema
4. **Unknown Parameters**: Identifies parameters not defined in the schema
5. **Data Types**: Ensures all parameters have the correct data types
6. **Required Fields**: Checks that all required fields are present

### Validation Output

The validator provides detailed feedback:

- **Success**: Simple confirmation when validation passes
- **Schema Errors**: Detailed error messages with path information
- **Unknown Parameters**: Lists invalid parameters with valid alternatives
- **Error Paths**: Shows exact location of errors in the configuration structure

---

## 🎯 Usage Examples

### Example 1: Basic Validation

```python
from mc_config_validator.validator import MediaConvertConfigValidator

# Create validator instance
validator = MediaConvertConfigValidator('mc_setting_schema.json')

# Validate a configuration file
is_valid = validator.validate_config('my_config.json')

if is_valid:
    print("Configuration is valid!")
else:
    print("Configuration has errors - check the logs for details")
```

### Example 2: Command Line Validation

```bash
# Validate with default schema
python validator.py --config-path my_config.json

# Use custom schema
python validator.py --config-path my_config.json --schema my_custom_schema.json
```

### Example 3: Integration in Workflow

```python
import sys
from mc_config_validator.validator import MediaConvertConfigValidator

def validate_before_submission(config_file):
    """Validate configuration before submitting to MediaConvert"""
    validator = MediaConvertConfigValidator('mc_setting_schema.json')
    
    if validator.validate_config(config_file):
        print(f"✓ {config_file} is valid - ready for submission")
        return True
    else:
        print(f"✗ {config_file} has validation errors - check logs")
        return False

# Use in your workflow
if validate_before_submission('job_config.json'):
    # Proceed with MediaConvert job submission
    pass
else:
    # Handle validation failure
    sys.exit(1)
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **Missing Settings Object**
```
Error: Configuration is missing the 'Settings' object
```
**Solution**: Ensure your configuration has a top-level "Settings" object.

#### 2. **Schema Validation Errors**
```
Schema error at OutputGroups -> 0 -> Outputs -> 0 -> VideoDescription: 'Width' is a required property
```
**Solution**: Add the missing required property to your configuration.

#### 3. **Unknown Parameter Errors**
```
Unknown parameter 'InvalidParam' at OutputGroups.0.Outputs.0.VideoDescription. Valid parameters are: Width, Height, CodecSettings
```
**Solution**: Remove the invalid parameter or check the spelling against valid parameters.

### Debug Information

The validator uses Python's logging module. To see detailed validation information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run validation - you'll see detailed debug information
validator = MediaConvertConfigValidator('mc_setting_schema.json')
validator.validate_config('config.json')
```

---

## 📚 API Reference

### MediaConvertConfigValidator Class

```python
class MediaConvertConfigValidator:
    def __init__(self, schema_path: str):
        """Initialize validator with schema file path"""
    
    def validate_config(self, config_path: str) -> bool:
        """Validate configuration file against schema
        
        Args:
            config_path: Path to MediaConvert configuration JSON file
            
        Returns:
            True if validation passes, False otherwise
        """
```

### Command Line Interface

```bash
python validator.py [options]

Options:
  --config-path PATH    Path to MediaConvert configuration file (required)
  --schema PATH         Path to JSON schema file (default: mc_setting_schema.json)
  -h, --help           Show help message
```

**Exit Codes:**
- `0`: Validation successful
- `1`: Validation failed or error occurred

---

## 🤝 Contributing

### Adding New Validation Features

1. **Extend the validator class** with new validation methods
2. **Update the schema file** if needed for new MediaConvert features
3. **Add comprehensive error handling** and logging
4. **Update documentation** with usage examples

### Improving Error Messages

1. **Enhance error message clarity** in the validation methods
2. **Add more context** to help users fix issues
3. **Include examples** of correct configuration format

---

## 📄 License

This module is part of E2MC Assistant and is licensed under the MIT License. See [LICENSE](../../LICENSE) for full details.