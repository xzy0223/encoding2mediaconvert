#!/usr/bin/env python3
"""
MediaConvert Configuration Validator

This script validates AWS MediaConvert job configurations against a JSON schema.
It focuses on validating the "Settings" object in the configuration to ensure
it conforms to the schema specifications.
"""

import json
import sys
import os
import argparse
import logging
from jsonschema import Draft7Validator, SchemaError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')


class MediaConvertConfigValidator:
    """
    Validates AWS MediaConvert job configurations against a JSON schema.
    """

    def __init__(self, schema_path):
        """
        Initialize the validator with the schema file path.
        
        Args:
            schema_path (str): Path to the JSON schema file
        """
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)
        self.logger = logging.getLogger('ConfigValidator')

    def _load_schema(self):
        """
        Load the JSON schema from file.
        
        Returns:
            dict: The loaded JSON schema
        
        Raises:
            FileNotFoundError: If the schema file doesn't exist
            json.JSONDecodeError: If the schema file contains invalid JSON
        """
        try:
            with open(self.schema_path, 'r') as schema_file:
                return json.load(schema_file)
        except FileNotFoundError:
            self.logger.error(f"Error: Schema file not found at {self.schema_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error: Invalid JSON in schema file: {e}")
            sys.exit(1)

    def validate_config(self, config_path):
        """
        Validate a MediaConvert job configuration against the schema.
        Collects all validation errors instead of stopping at the first one.
        Also checks for any parameters in the config that are not defined in the schema.
        
        Args:
            config_path (str): Path to the configuration file
            
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file contains invalid JSON
        """
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
            
            # Extract the Settings object for validation
            if 'Settings' not in config:
                self.logger.error("Error: Configuration is missing the 'Settings' object")
                return False
            
            settings = config['Settings']
            
            # Collect all schema validation errors
            schema_errors = list(self.validator.iter_errors(settings))
            
            # Check for unknown parameters not defined in the schema
            unknown_param_errors = self._check_unknown_parameters(settings)
            
            # If no errors, validation is successful
            if not schema_errors and not unknown_param_errors:
                self.logger.info(f"Validation successful: {config_path} conforms to the schema")
                return True
            
            # Output all schema validation errors
            if schema_errors:
                self.logger.error(f"Found {len(schema_errors)} schema validation errors:")
                for i, error in enumerate(schema_errors, 1):
                    path = " -> ".join([str(p) for p in error.path]) if error.path else "root"
                    self.logger.error(f"{i}. Schema error at {path}: {error.message}")
            
            # Output all unknown parameter errors
            if unknown_param_errors:
                self.logger.error(f"Found {len(unknown_param_errors)} unknown parameter errors:")
                for i, error in enumerate(unknown_param_errors, 1):
                    self.logger.error(f"{i}. {error}")
                    
                    # Extract the invalid parameter name and full path for clearer reporting
                    if "Unknown parameter '" in error:
                        param_name = error.split("Unknown parameter '")[1].split("'")[0]
                        param_path = error.split(" at ")[1].split(".")[0]
                        full_path = error.split(" at ")[1].split(". Valid")[0]
                        self.logger.error(f"   --> INVALID PARAMETER: '{param_name}'")
                        self.logger.error(f"   --> FULL PATH: '{full_path}'")
            
            return False
            
        except FileNotFoundError:
            error_msg = f"Error: Configuration file not found at {config_path}"
            logger.error(error_msg)
            print(error_msg)
            return False
        except json.JSONDecodeError as e:
            error_msg = f"Error: Invalid JSON in configuration file: {e}"
            logger.error(error_msg)
            print(error_msg)
            return False
        except SchemaError as e:
            error_msg = f"Schema error: {e.message}"
            logger.error(error_msg)
            print(error_msg)
            return False

    def _check_unknown_parameters(self, config, path="", schema=None):
        """
        Recursively check for parameters in the config that are not defined in the schema.
        
        Args:
            config (dict): The configuration object or sub-object
            path (str): Current path in the configuration (for error reporting)
            schema (dict): Current schema or sub-schema to check against
            
        Returns:
            list: List of error messages for unknown parameters
        """
        errors = []
        
        if schema is None:
            schema = self.schema
        
        if isinstance(config, dict):
            # For objects, check each property against the schema
            for key, value in config.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if this is a property defined in the schema
                if 'properties' in schema and key in schema['properties']:
                    # Recursively check this property's value against its schema
                    sub_schema = schema['properties'][key]
                    errors.extend(self._check_unknown_parameters(value, current_path, sub_schema))
                elif 'additionalProperties' in schema and schema['additionalProperties'] is not False:
                    # If additionalProperties is allowed, check against that schema
                    if isinstance(schema['additionalProperties'], dict):
                        errors.extend(self._check_unknown_parameters(value, current_path, schema['additionalProperties']))
                elif 'patternProperties' in schema:
                    # Handle pattern properties (for dynamic keys)
                    pattern_matched = False
                    for pattern, pattern_schema in schema['patternProperties'].items():
                        import re
                        if re.match(pattern, key):
                            pattern_matched = True
                            errors.extend(self._check_unknown_parameters(value, current_path, pattern_schema))
                    
                    if not pattern_matched and key not in ['type', 'properties', 'items', 'additionalProperties', 'required', 'enum', 'patternProperties']:
                        # List valid properties if available
                        valid_props = []
                        if 'properties' in schema:
                            valid_props = list(schema['properties'].keys())
                        
                        if valid_props:
                            errors.append(f"Unknown parameter '{key}' at {current_path}. Valid parameters are: {', '.join(valid_props)}")
                        else:
                            errors.append(f"Unknown parameter '{key}' at {current_path}")
                elif key not in ['type', 'properties', 'items', 'additionalProperties', 'required', 'enum', 'patternProperties']:
                    # This is an unknown property
                    # List valid properties if available
                    valid_props = []
                    if 'properties' in schema:
                        valid_props = list(schema['properties'].keys())
                    
                    if valid_props:
                        errors.append(f"Unknown parameter '{key}' at {current_path}. Valid parameters are: {', '.join(valid_props)}")
                    else:
                        errors.append(f"Unknown parameter '{key}' at {current_path}")
                
        elif isinstance(config, list):
            # For arrays, check each item against the items schema
            if 'items' in schema:
                for i, item in enumerate(config):
                    current_path = f"{path}[{i}]"
                    errors.extend(self._check_unknown_parameters(item, current_path, schema['items']))
        
        return errors


def main():
    """
    Main function to run the validator from command line.
    """
    parser = argparse.ArgumentParser(
        description='Validate AWS MediaConvert job configurations against a JSON schema'
    )
    parser.add_argument(
        '--config-path',
        required=True,
        help='Path to the MediaConvert job configuration file'
    )
    parser.add_argument(
        '--schema',
        default=os.path.join(os.path.dirname(__file__), 'mc_setting_schema.json'),
        help='Path to the JSON schema file (default: mc_setting_schema.json in the same directory)'
    )
    
    args = parser.parse_args()
    
    validator = MediaConvertConfigValidator(args.schema)
    is_valid = validator.validate_config(args.config_path)
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
