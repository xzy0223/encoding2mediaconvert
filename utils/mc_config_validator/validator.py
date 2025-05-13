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
from jsonschema import validate, ValidationError, SchemaError


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
            print(f"Error: Schema file not found at {self.schema_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in schema file: {e}")
            sys.exit(1)

    def validate_config(self, config_path):
        """
        Validate a MediaConvert job configuration against the schema.
        
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
                print("Error: Configuration is missing the 'Settings' object")
                return False
            
            settings = config['Settings']
            
            # Validate the Settings object against the schema
            validate(instance=settings, schema=self.schema)
            print(f"Validation successful: {config_path} conforms to the schema")
            return True
            
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            return False
        except ValidationError as e:
            print(f"Validation error: {e.message}")
            print(f"Path: {' -> '.join([str(p) for p in e.path])}")
            return False
        except SchemaError as e:
            print(f"Schema error: {e.message}")
            return False


def main():
    """
    Main function to run the validator from command line.
    """
    parser = argparse.ArgumentParser(
        description='Validate AWS MediaConvert job configurations against a JSON schema'
    )
    parser.add_argument(
        'config_path',
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
