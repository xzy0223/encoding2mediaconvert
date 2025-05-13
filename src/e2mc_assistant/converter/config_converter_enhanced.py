#!/usr/bin/env python3
import argparse
import json
import os
import re
import xml.etree.ElementTree as ET
import yaml
from typing import Dict, Any, List, Union, Callable
import logging
import copy


class ConfigConverter:
    def __init__(self, rules_file: str):
        """Initialize converter with mapping rules"""
        with open(rules_file, 'r') as f:
            self.config = yaml.safe_load(f)
        self.rules = self.config.get('rules', [])
        self.transformers = self.config.get('transformers', {})
        self.custom_functions = {}
        self.logger = logging.getLogger('ConfigConverter')
        
        # Register built-in custom functions
        self.register_custom_function('process_streams', self._process_streams)
        
    def register_custom_function(self, name: str, func: Callable):
        """Register a custom transformation function"""
        self.custom_functions[name] = func
        
    def parse_xml(self, xml_file: str) -> Dict:
        """Parse Encoding.com XML configuration file"""
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Convert XML to dictionary
        result = {}
        
        def process_element(element, current_dict):
            # Handle array-like elements (multiple stream tags)
            if element.tag == 'stream' and element.tag in current_dict:
                # If this is a stream and we already have one, convert to array
                if not isinstance(current_dict[element.tag], list):
                    current_dict[element.tag] = [current_dict[element.tag]]
                
                # Process this stream
                stream_dict = {}
                for child in element:
                    process_element(child, stream_dict)
                
                # Add to array
                current_dict[element.tag].append(stream_dict)
                return
                
            if len(element) == 0:
                # Leaf node
                text = element.text
                if text is not None:
                    if text.isdigit():
                        text = int(text)
                    elif self._is_float(text):
                        text = float(text)
                current_dict[element.tag] = text
            else:
                # Non-leaf node
                new_dict = {}
                current_dict[element.tag] = new_dict
                for child in element:
                    process_element(child, new_dict)
        
        # Special handling for stream elements which can be multiple
        streams = []
        non_streams = []
        
        for child in root:
            if child.tag == 'stream':
                streams.append(child)
            else:
                non_streams.append(child)
        
        # Process non-stream elements first
        for child in non_streams:
            process_element(child, result)
            
        # Process stream elements
        if streams:
            result['stream'] = []
            for stream in streams:
                stream_dict = {}
                for child in stream:
                    process_element(child, stream_dict)
                result['stream'].append(stream_dict)
        
        # Debug output
        self.logger.debug(f"Parsed XML structure: {result}")
                
        return result
    
    def _is_float(self, value: str) -> bool:
        """Check if string can be converted to float"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def get_value_by_path(self, data: Dict, path: str) -> Any:
        """Get value from dictionary by path"""
        parts = path.split('/')
        current = data
        
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return None
                
        return current
    
    def set_value_by_path(self, data: Dict, path: str, value: Any) -> None:
        """Set value in dictionary by path, properly handling nested structures and arrays"""
        self._set_nested_value(data, path, value)
    
    def apply_transform(self, value: Any, transform_name: str, context: Dict = None) -> Any:
        """Apply transformation function"""
        # Check if it's a custom function
        if transform_name in self.custom_functions:
            return self.custom_functions[transform_name](value, context)
            
        # Check if it's a predefined transformation mapping
        if transform_name in self.transformers:
            transformer = self.transformers[transform_name]
            str_value = str(value)
            if str_value in transformer:
                return transformer[str_value]
        
        return value
    
    def evaluate_condition(self, condition: Dict, source_value: Any, source_data: Dict = None) -> bool:
        """Evaluate condition"""
        # If condition has source_path, get value from there instead
        if 'source_path' in condition and source_data:
            source_value = self.get_value_by_path(source_data, condition['source_path'])
            self.logger.debug(f"Condition using source_path {condition['source_path']}, value: {source_value}")
            
        op = condition.get('operator', 'eq')
        compare_value = condition.get('value')
        
        if op == 'eq':
            result = source_value == compare_value
        elif op == 'ne':
            result = source_value != compare_value
        elif op == 'gt':
            result = source_value > compare_value
        elif op == 'lt':
            result = source_value < compare_value
        elif op == 'gte':
            result = source_value >= compare_value
        elif op == 'lte':
            result = source_value <= compare_value
        elif op == 'in':
            result = source_value in compare_value
        elif op == 'contains':
            result = compare_value in source_value
        elif op == 'exists':
            result = source_value is not None
        else:
            result = False
            
        self.logger.debug(f"Condition evaluation: {op} {source_value} {compare_value} = {result}")
        return result
    
    def _process_streams(self, streams: List, context: Dict) -> List:
        """Process multiple streams for HLS/DASH outputs"""
        outputs = []
        source_data = context.get('source_data', {})
        output_format = self.get_value_by_path(source_data, 'output')
        
        self.logger.debug(f"Processing streams for format: {output_format}")
        self.logger.debug(f"Number of streams: {len(streams)}")
        
        # Create template for output
        if output_format == "advanced_hls":
            container = "M3U8"
            template = {
                "ContainerSettings": {
                    "Container": container,
                    "M3u8Settings": {}
                },
                "VideoDescription": {
                    "CodecSettings": {
                        "Codec": "H_264",
                        "H264Settings": {
                            "FramerateDenominator": 1,
                            "FramerateControl": "SPECIFIED"
                        }
                    }
                },
                "AudioDescriptions": [
                    {
                        "CodecSettings": {
                            "Codec": "AAC",
                            "AacSettings": {}
                        }
                    }
                ],
                "OutputSettings": {
                    "HlsSettings": {}
                }
            }
        elif output_format == "advanced_dash":
            container = "MPD"
            template = {
                "ContainerSettings": {
                    "Container": container,
                    "MpdSettings": {}
                },
                "VideoDescription": {
                    "CodecSettings": {
                        "Codec": "H_264",
                        "H264Settings": {
                            "FramerateDenominator": 1,
                            "FramerateControl": "SPECIFIED"
                        }
                    }
                },
                "AudioDescriptions": [
                    {
                        "CodecSettings": {
                            "Codec": "AAC",
                            "AacSettings": {}
                        }
                    }
                ]
            }
        else:
            self.logger.warning(f"Unsupported output format for streams: {output_format}")
            return outputs
        
        # Process each stream
        for i, stream in enumerate(streams):
            output = copy.deepcopy(template)
            
            # Check if this is audio-only or video-only stream
            is_audio_only = stream.get('audio_only') == 'yes'
            is_video_only = stream.get('video_only') == 'yes'
            
            self.logger.debug(f"Stream {i}: audio_only={is_audio_only}, video_only={is_video_only}")
            
            # Set size
            if 'size' in stream and not is_audio_only:
                size_match = re.match(r'(\d+)x(\d+)', stream['size'])
                if size_match:
                    width, height = size_match.groups()
                    output['VideoDescription']['Width'] = int(width)
                    output['VideoDescription']['Height'] = int(height)
                    self.logger.debug(f"Stream {i}: Set size to {width}x{height}")
            
            # Set bitrate
            if 'bitrate' in stream and not is_audio_only:
                bitrate_match = re.match(r'(\d+)k', stream['bitrate'])
                if bitrate_match:
                    bitrate = int(bitrate_match.group(1)) * 1000
                    output['VideoDescription']['CodecSettings']['H264Settings']['Bitrate'] = bitrate
                    self.logger.debug(f"Stream {i}: Set video bitrate to {bitrate}")
            
            # Set framerate
            if 'framerate' in stream and not is_audio_only:
                output['VideoDescription']['CodecSettings']['H264Settings']['FramerateNumerator'] = int(stream['framerate'])
                self.logger.debug(f"Stream {i}: Set framerate to {stream['framerate']}")
            
            # Set rate control mode
            if 'cbr' in stream and not is_audio_only:
                mode = 'CBR' if stream['cbr'] == 'yes' else 'QVBR'
                output['VideoDescription']['CodecSettings']['H264Settings']['RateControlMode'] = mode
                self.logger.debug(f"Stream {i}: Set rate control mode to {mode}")
            
            # Set audio bitrate
            if 'audio_bitrate' in stream and not is_video_only:
                audio_bitrate_match = re.match(r'(\d+)k', stream['audio_bitrate'])
                if audio_bitrate_match:
                    audio_bitrate = int(audio_bitrate_match.group(1)) * 1000
                    output['AudioDescriptions'][0]['CodecSettings']['AacSettings']['Bitrate'] = audio_bitrate
                    self.logger.debug(f"Stream {i}: Set audio bitrate to {audio_bitrate}")
            
            # Set audio sample rate
            if 'audio_sample_rate' in stream and not is_video_only:
                output['AudioDescriptions'][0]['CodecSettings']['AacSettings']['SampleRate'] = int(stream['audio_sample_rate'])
                self.logger.debug(f"Stream {i}: Set audio sample rate to {stream['audio_sample_rate']}")
            
            # Set audio channels
            if 'audio_channels_number' in stream and not is_video_only:
                channels = int(stream['audio_channels_number'])
                if channels == 2:
                    output['AudioDescriptions'][0]['CodecSettings']['AacSettings']['CodingMode'] = 'CODING_MODE_2_0'
                elif channels == 1:
                    output['AudioDescriptions'][0]['CodecSettings']['AacSettings']['CodingMode'] = 'CODING_MODE_1_0'
                self.logger.debug(f"Stream {i}: Set audio channels to {channels}")
            
            # Remove video description for audio-only streams
            if is_audio_only:
                output.pop('VideoDescription', None)
                self.logger.debug(f"Stream {i}: Removed video description (audio-only)")
            
            # Remove audio descriptions for video-only streams
            if is_video_only:
                output.pop('AudioDescriptions', None)
                self.logger.debug(f"Stream {i}: Removed audio description (video-only)")
            
            # Create name modifier based on resolution and bitrate
            name_modifier = ""
            if 'size' in stream and not is_audio_only:
                name_modifier += f"_{stream['size'].replace('x', 'x')}"
            if 'bitrate' in stream and not is_audio_only:
                bitrate_match = re.match(r'(\d+)k', stream['bitrate'])
                if bitrate_match:
                    name_modifier += f"_{bitrate_match.group(1)}K"
            elif is_audio_only:
                name_modifier = "_audio"
                
            output['NameModifier'] = name_modifier
            self.logger.debug(f"Stream {i}: Set name modifier to {name_modifier}")
            
            outputs.append(output)
        
        self.logger.debug(f"Processed {len(outputs)} streams")
        return outputs
        
    def _merge_dicts(self, target: Dict, source: Dict) -> None:
        """Recursively merge source dict into target dict"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dicts(target[key], value)
            else:
                target[key] = value
                
    def _set_nested_value(self, target_dict: Dict, path: str, value: Any) -> None:
        """Helper method to properly set nested values, handling array indices correctly"""
        parts = path.split('.')
        current = target_dict
        
        for i, part in enumerate(parts):
            # Check if this is the last part
            is_last = (i == len(parts) - 1)
            
            # Handle array indices, e.g., AudioDescriptions[0]
            array_match = re.match(r'(.+)\[(\d+)\]', part)
            
            if array_match:
                key = array_match.group(1)
                index = int(array_match.group(2))
                
                # If this is the last part, set the value directly
                if is_last:
                    if key not in current:
                        current[key] = []
                    # Ensure array has enough elements
                    while len(current[key]) <= index:
                        current[key].append({})
                    
                    # If value is a dict and current value is also a dict, merge them
                    if isinstance(value, dict) and isinstance(current[key][index], dict):
                        self._merge_dicts(current[key][index], value)
                    else:
                        current[key][index] = value
                else:
                    # Not the last part, create/ensure the nested structure
                    if key not in current:
                        current[key] = []
                    # Ensure array has enough elements
                    while len(current[key]) <= index:
                        current[key].append({})
                    current = current[key][index]
            else:
                # Regular key (not array)
                if is_last:
                    # If value is a dict and current value is also a dict, merge them
                    if isinstance(value, dict) and part in current and isinstance(current[part], dict):
                        self._merge_dicts(current[part], value)
                    else:
                        current[part] = value
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                    
    def _process_iteration_rule(self, rule: Dict, source_data: Dict, target_data: Dict):
        """Process iteration rules for array elements like streams"""
        source_path = rule['source']['path']
        source_array = self.get_value_by_path(source_data, source_path)
        
        if not source_array or not isinstance(source_array, list):
            self.logger.debug(f"No array found at {source_path} or not a list")
            return
        
        sub_rules = rule['source'].get('rules', [])
        target_base_path = rule['target_base_path']
        name_modifier_config = rule.get('name_modifier')
        
        # Get template structure if it exists
        template_outputs = None
        parts = target_base_path.split('.')
        current = target_data
        for part in parts:
            if part in current:
                current = current[part]
                if isinstance(current, list) and len(current) > 0:
                    template_outputs = current[0]  # Use first item as template
                    break
        
        # Create target array
        target_array = []
        
        # Process each source element
        for i, source_item in enumerate(source_array):
            self.logger.debug(f"Processing {source_path}[{i}]")
            
            # Start with template structure if available
            if template_outputs:
                target_item = copy.deepcopy(template_outputs)
            else:
                target_item = {}
            
            # Apply each sub-rule
            for sub_rule in sub_rules:
                sub_source_path = sub_rule['source']['path']
                sub_source_value = source_item.get(sub_source_path)
                
                # Skip if value is None and no default
                if sub_source_value is None:
                    if 'default' in sub_rule['source']:
                        sub_source_value = sub_rule['source']['default']
                        self.logger.debug(f"Using default value for {sub_source_path}: {sub_source_value}")
                    else:
                        self.logger.debug(f"Skipping sub-rule for {sub_source_path} (no value and no default)")
                        continue
                
                # Check condition if any
                if 'condition' in sub_rule['source']:
                    condition = sub_rule['source']['condition']
                    if not self.evaluate_condition(condition, sub_source_value, source_item):
                        self.logger.debug(f"Skipping sub-rule for {sub_source_path} due to condition")
                        continue
                
                # Process target (can be single or multiple)
                sub_targets = sub_rule['target'] if isinstance(sub_rule['target'], list) else [sub_rule['target']]
                
                for sub_target in sub_targets:
                    sub_target_path = sub_target['path']
                    sub_transform = sub_target.get('transform')
                    
                    # Check target condition if any
                    if 'condition' in sub_target:
                        if not self.evaluate_condition(sub_target['condition'], sub_source_value, source_item):
                            self.logger.debug(f"Skipping sub-target {sub_target_path} due to condition")
                            continue
                    
                    # Process value transformation
                    if 'value' in sub_target:
                        # Process with regex if specified
                        source_regex = sub_rule['source'].get('regex')
                        if source_regex:
                            match = re.match(source_regex, str(sub_source_value))
                            if match:
                                value_template = sub_target['value']
                                # Replace $1, $2, etc. with match groups
                                for j, group in enumerate(match.groups(), 1):
                                    value_template = value_template.replace(f'${j}', group)
                                
                                # Convert to appropriate type
                                if value_template.isdigit():
                                    sub_target_value = int(value_template)
                                elif self._is_float(value_template):
                                    sub_target_value = float(value_template)
                                else:
                                    sub_target_value = value_template
                                
                                self.logger.debug(f"Regex transformed {sub_source_value} to {sub_target_value}")
                            else:
                                self.logger.debug(f"Regex pattern {source_regex} did not match {sub_source_value}")
                                continue
                        else:
                            sub_target_value = sub_target['value']
                            self.logger.debug(f"Using static value: {sub_target_value}")
                    else:
                        sub_target_value = sub_source_value
                        
                        # Apply transformation function
                        if sub_transform:
                            context = {'source_data': source_item, 'target_data': target_item}
                            original_value = sub_target_value
                            sub_target_value = self.apply_transform(sub_target_value, sub_transform, context)
                            self.logger.debug(f"Transformed {original_value} using {sub_transform} to {type(sub_target_value)}")
                    
                    # Handle nested paths properly, especially for arrays like AudioDescriptions[0]
                    self._set_nested_value(target_item, sub_target_path, sub_target_value)
                    self.logger.debug(f"Set {sub_target_path}={sub_target_value} in stream {i}")
            
            # Generate name modifier
            if name_modifier_config:
                template = name_modifier_config.get('template', '')
                name_modifier = template
                
                # Replace template variables
                for var_name, replacement in name_modifier_config.get('replacements', {}).items():
                    var_value = source_item.get(var_name, '')
                    if var_value and 'regex' in replacement:
                        regex = replacement['regex']
                        format_str = replacement.get('format', '$1')
                        
                        match = re.match(regex, str(var_value))
                        if match:
                            replaced_value = format_str
                            for j, group in enumerate(match.groups(), 1):
                                replaced_value = replaced_value.replace(f'${j}', group)
                            var_value = replaced_value
                    
                    name_modifier = name_modifier.replace(f"{{{var_name}}}", str(var_value))
                
                target_item['NameModifier'] = name_modifier
                self.logger.debug(f"Generated NameModifier: {name_modifier} for stream {i}")
            
            target_array.append(target_item)
        
        # Set target array
        self.set_value_by_path(target_data, target_base_path, target_array)
        self.logger.debug(f"Set {len(target_array)} items at {target_base_path}")
    def convert(self, source_file: str, template_file: str = None) -> Dict:
        """Execute configuration conversion"""
        # Parse source file
        if source_file.endswith('.xml'):
            source_data = self.parse_xml(source_file)
        else:
            with open(source_file, 'r') as f:
                source_data = json.load(f)
        
        # Load target template (if provided)
        if template_file:
            with open(template_file, 'r') as f:
                target_data = json.load(f)
        else:
            target_data = {"Settings": {"OutputGroups": [{}], "Inputs": [{}]}}
        
        # Track which parameters have been processed
        processed_params = set()
        
        # Apply mapping rules
        for rule in self.rules:
            # Handle iteration rules
            if rule['source'].get('type') == 'iteration':
                self.logger.debug(f"Processing iteration rule for {rule['source']['path']}")
                self._process_iteration_rule(rule, source_data, target_data)
                processed_params.add(rule['source']['path'])
                continue
                
            source_path = rule['source']['path']
            source_type = rule['source'].get('type', 'string')
            source_regex = rule['source'].get('regex')
            
            # Get source value
            source_value = self.get_value_by_path(source_data, source_path)
            self.logger.debug(f"Processing rule for {source_path}, value: {source_value}")
            
            # Add to processed parameters
            processed_params.add(source_path)
            
            # Check condition (if any)
            if 'condition' in rule['source'] and source_value is not None:
                if not self.evaluate_condition(rule['source']['condition'], source_value, source_data):
                    self.logger.debug(f"Skipping rule for {source_path} due to source condition")
                    continue
            
            # If source value doesn't exist, use default (if provided)
            if source_value is None:
                if 'default' in rule['source']:
                    source_value = rule['source']['default']
                    self.logger.debug(f"Using default value for {source_path}: {source_value}")
                else:
                    self.logger.debug(f"Skipping rule for {source_path} (no value and no default)")
                    continue
            
            # Process target mapping (can be single target or multiple targets)
            targets = rule['target'] if isinstance(rule['target'], list) else [rule['target']]
            
            for target in targets:
                target_path = target['path']
                transform = target.get('transform')
                
                # Check target condition (if any)
                if 'condition' in target:
                    if not self.evaluate_condition(target['condition'], source_value, source_data):
                        self.logger.debug(f"Skipping target {target_path} due to target condition")
                        continue
                
                # Process value transformation
                if 'value' in target:
                    # Process with regex if specified
                    if source_regex:
                        match = re.match(source_regex, str(source_value))
                        if match:
                            value_template = target['value']
                            # Replace $1, $2, etc. with match groups
                            for i, group in enumerate(match.groups(), 1):
                                value_template = value_template.replace(f'${i}', group)
                            
                            # Convert to appropriate type
                            if value_template.isdigit():
                                target_value = int(value_template)
                            elif self._is_float(value_template):
                                target_value = float(value_template)
                            else:
                                target_value = value_template
                            
                            self.logger.debug(f"Regex transformed {source_value} to {target_value}")
                        else:
                            self.logger.debug(f"Regex pattern {source_regex} did not match {source_value}")
                            continue
                    else:
                        target_value = target['value']
                        self.logger.debug(f"Using static value: {target_value}")
                else:
                    target_value = source_value
                    
                    # Apply transformation function
                    if transform:
                        context = {'source_data': source_data, 'target_data': target_data}
                        original_value = target_value
                        target_value = self.apply_transform(target_value, transform, context)
                        self.logger.debug(f"Transformed {original_value} using {transform} to {type(target_value)}")
                
                # Set target value using the improved nested value setter
                self._set_nested_value(target_data, target_path, target_value)
                self.logger.debug(f"Mapped {source_path}={source_value} to {target_path}")
        
        # Log unmapped parameters
        self._log_unmapped_parameters(source_data, processed_params)
        
        return target_data
        
    def _log_unmapped_parameters(self, source_data: Dict, processed_params: set, parent_path: str = ""):
        """Log parameters that don't have mapping rules"""
        for key, value in source_data.items():
            current_path = f"{parent_path}/{key}" if parent_path else key
            
            # Skip already processed parameters
            if current_path in processed_params:
                continue
                
            # Handle nested dictionaries
            if isinstance(value, dict):
                self._log_unmapped_parameters(value, processed_params, current_path)
            # Handle lists (except for stream which is handled specially)
            elif isinstance(value, list) and key != "stream":
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        list_path = f"{current_path}[{i}]"
                        self._log_unmapped_parameters(item, processed_params, list_path)
            # Log unmapped leaf parameters
            else:
                self.logger.warning(f"Unmapped parameter: {current_path} = {value}")


def batch_convert(converter: ConfigConverter, source_dir: str, output_dir: str, template_file: str = None):
    """Batch convert all XML files in directory"""
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
            
            if os.path.exists(template_path):
                current_template = template_path
                print(f"Using template: {template_path}")
            else:
                current_template = template_file
            
            try:
                result = converter.convert(source_file, current_template)
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Converted {source_file} to {output_file}")
            except Exception as e:
                print(f"Error converting {source_file}: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Convert Encoding.com configuration to AWS MediaConvert')
    parser.add_argument('--source', help='Source configuration file (XML) or directory')
    parser.add_argument('--rules', required=True, help='Mapping rules file (YAML)')
    parser.add_argument('--template', help='Template MediaConvert file (JSON)')
    parser.add_argument('--output', help='Output file path or directory')
    parser.add_argument('--batch', action='store_true', help='Batch process all XML files in source directory')
    parser.add_argument('--validate', help='JSON Schema file for validation')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    converter = ConfigConverter(args.rules)
    
    if args.batch:
        if not args.source or not args.output:
            parser.error("--batch requires both --source and --output to be directories")
        batch_convert(converter, args.source, args.output, args.template)
    else:
        if not args.source or not args.output:
            parser.error("--source and --output are required for single file conversion")
            
        result = converter.convert(args.source, args.template)
        
        # Validate result
        if args.validate:
            if not converter.validate(result, args.validate):
                print("Validation failed. See log for details.")
                return
        
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"Conversion completed. Output saved to {args.output}")


if __name__ == "__main__":
    main()
