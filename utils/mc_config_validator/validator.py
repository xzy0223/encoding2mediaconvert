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
from jsonschema import Draft7Validator, SchemaError


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
        Collects all validation errors instead of stopping at the first one.
        
        Args:
            config_path (str): Path to the configuration file
            
        Returns:
            bool: True if validation passes, False otherwise
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file contains invalid JSON
        """
        import logging
        logger = logging.getLogger('ConfigConverter')
        
        try:
            with open(config_path, 'r') as config_file:
                config = json.load(config_file)
            
            # Extract the Settings object for validation
            if 'Settings' not in config:
                error_msg = "Error: Configuration is missing the 'Settings' object"
                logger.error(error_msg)
                print(error_msg)
                return False
            
            settings = config['Settings']
            
            # Collect all schema validation errors
            schema_errors = list(self.validator.iter_errors(settings))
            
            # Collect custom validation errors
            custom_errors = self._validate_h264_settings(settings)
            
            # If no errors, validation is successful
            if not schema_errors and not custom_errors:
                success_msg = f"Validation successful: {config_path} conforms to the schema"
                logger.info(success_msg)
                print(success_msg)
                return True
            
            # Output all schema validation errors
            if schema_errors:
                error_count_msg = f"Found {len(schema_errors)} schema validation errors:"
                logger.error(error_count_msg)
                print(error_count_msg)
                for i, error in enumerate(schema_errors, 1):
                    path = " -> ".join([str(p) for p in error.path]) if error.path else "root"
                    error_msg = f"{i}. Schema error at {path}: {error.message}"
                    logger.error(error_msg)
                    print(error_msg)
            
            # Output all custom validation errors
            if custom_errors:
                custom_error_msg = f"Found {len(custom_errors)} custom validation errors:"
                logger.error(custom_error_msg)
                print(custom_error_msg)
                for i, error in enumerate(custom_errors, 1):
                    error_detail = f"{i}. {error}"
                    logger.error(error_detail)
                    print(error_detail)
            
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

    def _validate_h264_settings(self, settings):
        """
        Perform additional validation on H264Settings that might not be covered by the schema.
        
        Args:
            settings (dict): The Settings object from the configuration
            
        Returns:
            list: List of validation errors, empty if no errors
        """
        errors = []
        
        # Check all outputs for H264Settings
        for i, output_group in enumerate(settings.get('OutputGroups', [])):
            for j, output in enumerate(output_group.get('Outputs', [])):
                video_desc = output.get('VideoDescription', {})
                codec_settings = video_desc.get('CodecSettings', {})
                
                if codec_settings.get('Codec') == 'H_264':
                    h264_settings = codec_settings.get('H264Settings', {})
                    
                    # Check FramerateControl
                    framerate_control = h264_settings.get('FramerateControl')
                    if framerate_control and framerate_control not in ['INITIALIZE_FROM_SOURCE', 'SPECIFIED']:
                        errors.append(f"Invalid FramerateControl value: '{framerate_control}' at OutputGroups[{i}].Outputs[{j}].VideoDescription.CodecSettings.H264Settings. "
                                     f"Must be one of: INITIALIZE_FROM_SOURCE, SPECIFIED")
                    
                    # Add more custom validations for H264Settings here
                    
        return errors


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
