#!/usr/bin/env python3
"""
Command-line interface for the enhanced multi-stream converter.
"""

import argparse
import os
import logging
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.e2mc_assistant.converter.enhanced_config_converter import EnhancedConfigConverter
from utils.mc_config_validator.validator import MediaConvertConfigValidator

def setup_logging(log_file=None, verbose=False):
    """Setup logging to both console and file if log_file is provided."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        root_logger.addHandler(file_handler)
        logging.info(f"Logging to file: {log_file}")

def setup_file_logging(log_file, verbose=False):
    """Setup file logging for a specific conversion."""
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create file handler for this specific conversion
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Get the root logger and add this handler
    root_logger = logging.getLogger()
    
    # Remove any existing FileHandlers (to avoid duplicate logs)
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)
    
    # Add the new file handler
    root_logger.addHandler(file_handler)
    logging.info(f"Logging conversion details to: {log_file}")

def batch_convert(converter, source_dir, output_dir, template_file=None, schema_file=None):
    """Batch convert all XML files in directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for filename in os.listdir(source_dir):
        if filename.endswith('.xml') or filename.endswith('.format.xml'):
            source_file = os.path.join(source_dir, filename)
            
            # Determine output filename
            if filename.endswith('.format.xml'):
                output_file = os.path.join(output_dir, filename.replace('.format.xml', '.json'))
                # Check for matching template file (e.g., 1.format.xml -> 1-setting.json)
                template_name = filename.replace('.format.xml', '-setting.json')
            else:
                output_file = os.path.join(output_dir, filename.replace('.xml', '.json'))
                # Check for matching template file (e.g., 27.xml -> 27-setting.json)
                template_name = filename.replace('.xml', '-setting.json')
                
            template_path = os.path.join(source_dir, template_name)
            
            # Setup logging for this specific file
            log_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(output_file))[0]}.log")
            setup_file_logging(log_file)
            
            if os.path.exists(template_path):
                current_template = template_path
                logging.info(f"Using template: {template_path}")
            else:
                current_template = template_file
            
            try:
                result = converter.convert(source_file, current_template)
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                logging.info(f"Converted {source_file} to {output_file}")
                print(f"Converted {source_file} to {output_file}")
                
                # Validate the converted file if schema is provided
                if schema_file:
                    validator = MediaConvertConfigValidator(schema_file)
                    logging.info(f"Validating {output_file} against schema {schema_file}")
                    is_valid = validator.validate_config(output_file)
                    if not is_valid:
                        error_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(output_file))[0]}.err")
                        with open(error_file, 'w') as f:
                            f.write(f"Validation failed for {output_file}\n")
                            f.write("See log file for details\n")
                        logging.error(f"Validation failed for {output_file}. Error log written to {error_file}")
                        print(f"Validation failed for {output_file}. Error log written to {error_file}")
                    else:
                        logging.info(f"Validation successful for {output_file}")
                        print(f"Validation successful for {output_file}")
                
            except Exception as e:
                error_msg = f"Error converting {source_file}: {str(e)}"
                logging.error(error_msg)
                print(error_msg)
                
                # Write error to .err file
                error_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(output_file))[0]}.err")
                with open(error_file, 'w') as f:
                    f.write(f"Error converting {source_file}: {str(e)}\n")
                logging.error(f"Error log written to {error_file}")
                print(f"Error log written to {error_file}")

def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(description='Enhanced converter for Encoding.com to AWS MediaConvert with multi-stream support')
    parser.add_argument('--source', help='Source configuration file (XML) or directory')
    parser.add_argument('--rules', required=True, help='Mapping rules file (YAML)')
    parser.add_argument('--template', help='Template MediaConvert file (JSON)')
    parser.add_argument('--output', help='Output file path or directory')
    parser.add_argument('--batch', action='store_true', help='Batch process all XML files in source directory')
    parser.add_argument('--validate', help='JSON Schema file for validation')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up basic logging first
    setup_logging(verbose=args.verbose)
    
    # Create converter instance
    converter = EnhancedConfigConverter(args.rules)
    
    if args.batch:
        if not args.source or not args.output:
            parser.error("--batch requires both --source and --output to be directories")
        
        # For batch processing, each file will get its own log
        batch_convert(converter, args.source, args.output, args.template, args.validate)
    else:
        if not args.source or not args.output:
            parser.error("--source and --output are required for single file conversion")
        
        # Setup logging to a file in the same directory as the output file
        output_dir = os.path.dirname(args.output)
        output_filename = os.path.basename(args.output)
        log_file = os.path.join(output_dir, f"{os.path.splitext(output_filename)[0]}.log")
        setup_file_logging(log_file, args.verbose)
        
        try:
            result = converter.convert(args.source, args.template)
            
            # Write the output file
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            
            logging.info(f"Conversion completed. Output saved to {args.output}")
            print(f"Conversion completed. Output saved to {args.output}")
            
            # Validate result if schema is provided
            if args.validate:
                validator = MediaConvertConfigValidator(args.validate)
                logging.info(f"Validating {args.output} against schema {args.validate}")
                is_valid = validator.validate_config(args.output)
                if not is_valid:
                    error_file = os.path.join(output_dir, f"{os.path.splitext(output_filename)[0]}.err")
                    with open(error_file, 'w') as f:
                        f.write(f"Validation failed for {args.output}\n")
                        f.write("See log file for details\n")
                    logging.error(f"Validation failed for {args.output}. Error log written to {error_file}")
                    print(f"Validation failed for {args.output}. Error log written to {error_file}")
                else:
                    logging.info(f"Validation successful for {args.output}")
                    print(f"Validation successful for {args.output}")
                    
        except Exception as e:
            error_msg = f"Error converting {args.source}: {str(e)}"
            logging.error(error_msg)
            print(error_msg)
            
            # Write error to .err file
            error_file = os.path.join(output_dir, f"{os.path.splitext(output_filename)[0]}.err")
            with open(error_file, 'w') as f:
                f.write(f"Error converting {args.source}: {str(e)}\n")
            logging.error(f"Error log written to {error_file}")
            print(f"Error log written to {error_file}")

if __name__ == "__main__":
    main()
