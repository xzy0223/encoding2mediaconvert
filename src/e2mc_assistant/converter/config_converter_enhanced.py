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
import sys

# Add the project root to the Python path to import validator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils.mc_config_validator.validator import MediaConvertConfigValidator


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
        """Parse Encoding.com XML configuration file, returning only the format element content"""
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find the format element
        format_element = root.find('.//format')
        if format_element is None:
            self.logger.warning("No <format> element found in XML file")
            return {}
            
        # Convert format element to dictionary
        result = {}
        
        # First, identify elements that might appear multiple times
        element_counts = {}
        for child in format_element:
            tag = child.tag
            element_counts[tag] = element_counts.get(tag, 0) + 1
        
        # Process elements, handling multiples specially
        for tag, count in element_counts.items():
            if count > 1:
                # This element appears multiple times, collect them in a list
                elements = format_element.findall(tag)
                result[tag] = []
                for element in elements:
                    if len(element) == 0:  # Simple element
                        text = element.text
                        if text is not None:
                            if text.isdigit():
                                text = int(text)
                            elif self._is_float(text):
                                text = float(text)
                        result[tag].append(text)
                    else:  # Complex element
                        child_dict = {}
                        for child in element:
                            self._process_element(child, child_dict)
                        result[tag].append(child_dict)
            else:
                # Single occurrence, process normally
                elements = format_element.findall(tag)
                if elements:
                    self._process_element(elements[0], result)
        
        # Debug output
        self.logger.debug(f"Parsed XML structure: {result}")
                
        return result
        
    def _process_element(self, element, current_dict):
        """Process a single XML element into a dictionary"""
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
                self._process_element(child, new_dict)
    
    def _is_float(self, value: str) -> bool:
        """Check if string can be converted to float"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def get_value_by_path(self, data: Dict, path: str) -> Any:
        """Get value from dictionary by path with improved error handling"""
        if data is None:
            return None
            
        parts = path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
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
            
        # Special case for audio_volume_format
        if transform_name == "audio_volume_format":
            try:
                # Calculate -27 + 25 * (value / 100)
                volume_value = float(value)
                return -27 + 25 * (volume_value / 100)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid audio_volume value: {value}")
                return value
            
        # Check if it's a predefined transformation mapping
        if transform_name in self.transformers:
            transformer = self.transformers[transform_name]
            str_value = str(value)
            if str_value in transformer:
                return transformer[str_value]
            else:
                # If the value doesn't match any mapping in the transformer,
                # return None to indicate that the transformation failed
                self.logger.warning(f"Value '{str_value}' not found in transformer '{transform_name}'")
                return None
        
        return value
    
    def evaluate_condition(self, condition: Dict, source_value: Any, source_data: Dict = None) -> bool:
        """
        Evaluate condition with support for complex logical operations (AND, OR, NOT).
        
        Args:
            condition: Condition dictionary that can contain logical operators
            source_value: Value to compare against (for simple conditions)
            source_data: Source data dictionary for looking up values by path
            
        Returns:
            Boolean result of condition evaluation
        """
        # Check if this is a complex logical condition
        if 'operator' in condition and condition['operator'] in ['AND', 'OR', 'NOT']:
            logical_op = condition['operator']
            
            if logical_op == 'AND':
                # All subconditions must be true
                self.logger.debug(f"Evaluating AND condition with {len(condition['conditions'])} subconditions")
                result = all(self.evaluate_condition(subcond, source_value, source_data) 
                          for subcond in condition['conditions'])
                self.logger.debug(f"AND condition result: {result}")
                return result
            
            elif logical_op == 'OR':
                # Any subcondition can be true
                self.logger.debug(f"Evaluating OR condition with {len(condition['conditions'])} subconditions")
                result = any(self.evaluate_condition(subcond, source_value, source_data) 
                          for subcond in condition['conditions'])
                self.logger.debug(f"OR condition result: {result}")
                return result
            
            elif logical_op == 'NOT':
                # Negate the result of the subcondition
                self.logger.debug(f"Evaluating NOT condition")
                result = not self.evaluate_condition(condition['condition'], source_value, source_data)
                self.logger.debug(f"NOT condition result: {result}")
                return result
        
        # Handle simple condition (backward compatible with existing rules)
        # If condition has source_path, get value from there instead
        if 'source_path' in condition and source_data:
            source_value = self.get_value_by_path(source_data, condition['source_path'])
            self.logger.debug(f"Condition using source_path {condition['source_path']}, value: {source_value}")
            
        op = condition.get('operator', 'eq')
        compare_value = condition.get('value')
        
        # Convert string values to consistent format for comparison
        if isinstance(source_value, str) and isinstance(compare_value, str):
            source_value = source_value.lower().strip()
            compare_value = compare_value.lower().strip()
        
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
                        # Check if we're overwriting an existing value and log it
                        if part in current and current[part] != value:
                            self.logger.debug(f"Overwriting existing value at {path}: {current[part]} -> {value}")
                        current[part] = value
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                    
    def _process_iteration_rule(self, rule: Dict, source_data: Dict, target_data: Dict):
        """Process iteration rules for array elements like streams or alternate_source"""
        source_path = rule['source']['path']
        source_array = self.get_value_by_path(source_data, source_path)
        
        if not source_array:
            self.logger.debug(f"No array found at {source_path} or not a list")
            return
            
        # Convert to list if it's a single item
        if not isinstance(source_array, list):
            source_array = [source_array]
            self.logger.debug(f"Converted single item to list at {source_path}")
        
        sub_rules = rule['source'].get('rules', [])
        target_base_path = rule['target_base_path']
        name_modifier_config = rule.get('name_modifier')
        key_format = rule.get('key_format')  # New parameter for key-value mapping
        
        # Get template structure if it exists
        template_outputs = None
        if not key_format:  # Only for array-type targets (not key-value)
            parts = target_base_path.split('.')
            current = target_data
            for part in parts:
                if part in current:
                    current = current[part]
                    if isinstance(current, list) and len(current) > 0:
                        template_outputs = current[0]  # Use first item as template
                        break
        
        # Create target array or object
        if key_format:
            # For key-value mapping, ensure the target path exists
            self._ensure_path_exists(target_data, target_base_path)
            target_dict = self._get_nested_dict(target_data, target_base_path)
        else:
            # For array mapping
            target_array = []
        
        # Process each source element
        for i, source_item in enumerate(source_array):
            self.logger.debug(f"Processing {source_path}[{i}]")
            
            # Start with template structure if available
            if template_outputs and not key_format:
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
                        self.logger.warning(f"Skipping sub-rule for {sub_source_path}={sub_source_value} due to condition not matching")
                        continue
                
                # Process target (can be single or multiple)
                sub_targets = sub_rule['target'] if isinstance(sub_rule['target'], list) else [sub_rule['target']]
                
                for sub_target in sub_targets:
                    sub_target_path = sub_target['path']
                    sub_transform = sub_target.get('transform')
                    
                    # Check target condition if any
                    if 'condition' in sub_target:
                        if not self.evaluate_condition(sub_target['condition'], sub_source_value, source_item):
                            self.logger.warning(f"Skipping sub-target {sub_target_path} for source {sub_source_path}={sub_source_value} due to condition not matching")
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
                                self.logger.warning(f"Regex pattern {source_regex} did not match {sub_source_value} for {sub_source_path}")
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
                    self.logger.debug(f"Set {sub_target_path}={sub_target_value} in {source_path} {i}")
            
            # Generate name modifier
            if name_modifier_config and not key_format:
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
                self.logger.debug(f"Generated NameModifier: {name_modifier} for {source_path} {i}")
            
            # Add to target array or object
            if key_format:
                # Generate key name using the format and index
                key_name = key_format.replace('{index}', str(i + 1))
                target_dict[key_name] = target_item
                self.logger.debug(f"Added key-value pair with key: {key_name} for {source_path} {i}")
            else:
                target_array.append(target_item)
        
        # Set target array or object
        if not key_format:
            self.set_value_by_path(target_data, target_base_path, target_array)
            self.logger.debug(f"Set {len(target_array)} items at {target_base_path}")
            
    def _ensure_path_exists(self, data: Dict, path: str) -> None:
        """Ensure that a nested path exists in the dictionary"""
        parts = path.split('.')
        current = data
        
        for part in parts:
            # Handle array indices, e.g., OutputGroups[0]
            array_match = re.match(r'(.+)\[(\d+)\]', part)
            
            if array_match:
                key = array_match.group(1)
                index = int(array_match.group(2))
                
                if key not in current:
                    current[key] = []
                
                # Ensure array has enough elements
                while len(current[key]) <= index:
                    current[key].append({})
                
                current = current[key][index]
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
                
    def _get_nested_dict(self, data: Dict, path: str) -> Dict:
        """Get a nested dictionary at the specified path"""
        parts = path.split('.')
        current = data
        
        for part in parts:
            # Handle array indices, e.g., OutputGroups[0]
            array_match = re.match(r'(.+)\[(\d+)\]', part)
            
            if array_match:
                key = array_match.group(1)
                index = int(array_match.group(2))
                current = current[key][index]
            else:
                current = current[part]
                
        return current
    def _parse_bitrate(self, bitrate_str: str) -> int:
        """
        Parse bitrate string (like '1300k') to integer value (1300000)
        
        Args:
            bitrate_str: Bitrate string to parse
            
        Returns:
            Integer value of bitrate in bits per second
        """
        if not bitrate_str:
            return 0
            
        # Convert to string if it's not already
        bitrate_str = str(bitrate_str).lower().strip()
        
        # Check for common formats
        if bitrate_str.endswith('k'):
            try:
                return int(float(bitrate_str[:-1]) * 1000)
            except (ValueError, TypeError):
                self.logger.warning(f"Failed to parse bitrate: {bitrate_str}")
                return 0
        elif bitrate_str.endswith('m'):
            try:
                return int(float(bitrate_str[:-1]) * 1000000)
            except (ValueError, TypeError):
                self.logger.warning(f"Failed to parse bitrate: {bitrate_str}")
                return 0
        else:
            # Assume it's already in bits per second
            try:
                return int(float(bitrate_str))
            except (ValueError, TypeError):
                self.logger.warning(f"Failed to parse bitrate: {bitrate_str}")
                return 0
    
    def _process_rate_control_settings(self, source_data: Dict, target_data: Dict) -> bool:
        """
        Process rate control settings (CBR/VBR/QVBR) based on complex rules
        
        Args:
            source_data: Source data dictionary
            target_data: Target data dictionary to update
            
        Returns:
            True if rate control settings were processed, False otherwise
        """
        # Check if output is mp4, otherwise log warning and return
        output_format = self.get_value_by_path(source_data, 'output')
        if output_format != 'mp4':
            self.logger.warning(f"Rate control settings processing is only supported for MP4 output, got {output_format}. "
                               "Need to add independent processing function for this format.")
            return False
            
        # Get the target path for H264Settings
        target_path = "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings"
        
        # Get relevant source parameters
        cbr = self.get_value_by_path(source_data, 'cbr')
        cabr = self.get_value_by_path(source_data, 'cabr')
        bitrate_str = self.get_value_by_path(source_data, 'bitrate')
        maxrate_str = self.get_value_by_path(source_data, 'maxrate')
        minrate_str = self.get_value_by_path(source_data, 'minrate')
        
        # Parse bitrate values
        bitrate = self._parse_bitrate(bitrate_str)
        maxrate = self._parse_bitrate(maxrate_str)
        minrate = self._parse_bitrate(minrate_str)
        
        # Track if we've processed these parameters
        processed_params = set()
        
        # Case 1: If <cbr> exists and is not empty
        if cbr is not None:
            processed_params.add('cbr')
            
            if cbr == 'yes':
                # Case 1.a: cbr=yes
                self._set_nested_value(target_data, f"{target_path}.RateControlMode", "CBR")
                
                if bitrate_str:
                    self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate)
                    processed_params.add('bitrate')
                    self.logger.info(f"Set Bitrate to {bitrate} from <bitrate>={bitrate_str}")
                
                # Log if maxrate or minrate are ignored
                if maxrate_str:
                    self.logger.info(f"Ignoring <maxrate>={maxrate_str} because <cbr>=yes (CBR mode doesn't use MaxBitrate)")
                    processed_params.add('maxrate')
                if minrate_str:
                    self.logger.info(f"Ignoring <minrate>={minrate_str} because <cbr>=yes (CBR mode doesn't use MinBitrate)")
                    processed_params.add('minrate')
                    
            elif cbr == 'no':
                # Case 1.b: cbr=no
                if cabr is not None:
                    processed_params.add('cabr')
                    
                    if cabr == 'yes':
                        # Case 1.b.i: cbr=no, cabr=yes
                        self._set_nested_value(target_data, f"{target_path}.RateControlMode", "QVBR")
                        
                        if maxrate_str:
                            self._set_nested_value(target_data, f"{target_path}.MaxBitrate", maxrate)
                            processed_params.add('maxrate')
                            self.logger.info(f"Set MaxBitrate to {maxrate} from <maxrate>={maxrate_str}")
                        else:
                            self.logger.warning(f"<maxrate> not found but required for QVBR mode when <cabr>=yes")
                            
                        # Log if bitrate is ignored
                        if bitrate_str:
                            self.logger.info(f"Ignoring <bitrate>={bitrate_str} in QVBR mode (using MaxBitrate instead)")
                            processed_params.add('bitrate')
                            
                    elif cabr == 'no':
                        # Case 1.b.ii: cbr=no, cabr=no
                        self._set_nested_value(target_data, f"{target_path}.RateControlMode", "VBR")
                        
                        if bitrate_str:
                            self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate)
                            processed_params.add('bitrate')
                            self.logger.info(f"Set Bitrate to {bitrate} from <bitrate>={bitrate_str}")
                            
                        if maxrate_str:
                            self._set_nested_value(target_data, f"{target_path}.MaxBitrate", maxrate)
                            processed_params.add('maxrate')
                            self.logger.info(f"Set MaxBitrate to {maxrate} from <maxrate>={maxrate_str}")
        
        # Case 2: If <cbr> doesn't exist
        elif bitrate_str:
            processed_params.add('bitrate')
            
            if not maxrate_str:
                # Case 2.a: bitrate exists, maxrate doesn't exist or is empty
                self._set_nested_value(target_data, f"{target_path}.RateControlMode", "VBR")
                self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate)
                self.logger.info(f"Set Bitrate to {bitrate} from <bitrate>={bitrate_str}")
                
                # Set MaxBitrate to 2.5 * Bitrate
                calculated_maxrate = int(bitrate * 2.5)
                self._set_nested_value(target_data, f"{target_path}.MaxBitrate", calculated_maxrate)
                self.logger.info(f"Setting MaxBitrate to {calculated_maxrate} (2.5 * Bitrate)")
                
                # Log if minrate is ignored
                if minrate_str:
                    self.logger.info(f"Ignoring <minrate>={minrate_str} (not supported in MediaConvert)")
                    processed_params.add('minrate')
                    
            else:
                processed_params.add('maxrate')
                maxrate_value = maxrate
                bitrate_value = bitrate
                
                if maxrate_value > bitrate_value:
                    # Case 2.b: bitrate exists, maxrate exists and is greater than bitrate
                    self._set_nested_value(target_data, f"{target_path}.RateControlMode", "VBR")
                    self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate_value)
                    self._set_nested_value(target_data, f"{target_path}.MaxBitrate", maxrate_value)
                    self.logger.info(f"Set Bitrate to {bitrate_value} from <bitrate>={bitrate_str}")
                    self.logger.info(f"Set MaxBitrate to {maxrate_value} from <maxrate>={maxrate_str}")
                    
                elif maxrate_value == bitrate_value:
                    # Case 2.c: bitrate exists, maxrate exists and equals bitrate
                    self._set_nested_value(target_data, f"{target_path}.RateControlMode", "CBR")
                    self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate_value)
                    self.logger.info(f"Set Bitrate to {bitrate_value} from <bitrate>={bitrate_str}")
                    self.logger.info(f"Using CBR mode because maxrate equals bitrate")
                
                # Log if minrate is ignored
                if minrate_str:
                    self.logger.info(f"Ignoring <minrate>={minrate_str} (not supported in MediaConvert)")
                    processed_params.add('minrate')
        
        # Return processed parameters
        return len(processed_params) > 0
    
    def convert(self, source_file: str, template_file: str = None) -> Dict:
        """Execute configuration conversion using an XML-first approach"""
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
        
        # Initialize tracking variables
        processed_params = set()
        self.mapped_parameters = []  # Track successfully mapped parameters
        self.unmapped_parameters = []  # Track unmapped parameters
        
        # Process rate control settings first (special handling for CBR/VBR/QVBR)
        if self._process_rate_control_settings(source_data, target_data):
            # Mark these parameters as processed
            for param in ['cbr', 'cabr', 'bitrate', 'maxrate', 'minrate']:
                if self.get_value_by_path(source_data, param) is not None:
                    processed_params.add(param)
                    self.logger.info(f"Parameter {param} processed by custom rate control handler")
        
        # Create a rule lookup dictionary for faster access
        rule_lookup = {}
        iteration_rules = []
        dummy_rules = []
        
        # Organize rules by their source path for easier lookup
        for rule in self.rules:
            if rule['source'].get('type') == 'iteration':
                iteration_rules.append(rule)
                continue
            elif rule['source'].get('type') == 'dummy':
                dummy_rules.append(rule)
                continue
                
            source_path = rule['source']['path']
            if source_path not in rule_lookup:
                rule_lookup[source_path] = []
            rule_lookup[source_path].append(rule)
        
        # First, process iteration rules (these handle special cases like streams)
        for rule in iteration_rules:
            self.logger.debug(f"Processing iteration rule for {rule['source']['path']}")
            self._process_iteration_rule(rule, source_data, target_data)
            processed_params.add(rule['source']['path'])
        
        # Next, process dummy rules to mark parameters as processed
        for rule in dummy_rules:
            source_path = rule['source']['path']
            source_value = self.get_value_by_path(source_data, source_path)
            self.logger.debug(f"Processing dummy rule for {source_path}")
            processed_params.add(source_path)
            # Log the dummy rule match in the same format as regular mappings
            self.logger.info(f"Mapped parameter: {source_path}={source_value} → [DUMMY RULE]")
            # Add to mapped parameters list
            if not hasattr(self, 'mapped_parameters'):
                self.mapped_parameters = []
            self.mapped_parameters.append((source_path, source_value, "DUMMY_RULE", None))
        
        # Now, traverse the source data structure and apply matching rules
        self._process_source_data(source_data, "", rule_lookup, target_data, processed_params)
        
        # Log unmapped parameters
        self._log_unmapped_parameters(source_data, processed_params)
        
        # Generate summary statistics
        mapped_count = len(self.mapped_parameters)
        unmapped_count = len(self.unmapped_parameters)
        total_params = mapped_count + unmapped_count
        
        # Log summary
        self.logger.info(f"Conversion summary for {source_file}:")
        self.logger.info(f"  - Total parameters: {total_params}")
        if total_params > 0:
            self.logger.info(f"  - Mapped parameters: {mapped_count} ({mapped_count/total_params*100:.1f}%)")
            self.logger.info(f"  - Unmapped parameters: {unmapped_count} ({unmapped_count/total_params*100:.1f}%)")
        else:
            self.logger.info("  - No parameters found to convert")
        
        # Remove any _dummy sections from the output
        if '_dummy' in target_data:
            del target_data['_dummy']
            self.logger.debug("Removed _dummy section from output")
        
        # Add NameModifier to FILE_GROUP_SETTINGS outputs if missing
        self._add_missing_name_modifiers(target_data)
        
        return target_data
        
    def _add_missing_name_modifiers(self, target_data: Dict) -> None:
        """Add NameModifier to FILE_GROUP_SETTINGS outputs if missing"""
        if 'Settings' not in target_data or 'OutputGroups' not in target_data['Settings']:
            return
            
        output_groups = target_data['Settings']['OutputGroups']
        for group in output_groups:
            # Check if this is a FILE_GROUP_SETTINGS output group
            if ('OutputGroupSettings' in group and 
                'Type' in group['OutputGroupSettings'] and 
                group['OutputGroupSettings']['Type'] == 'FILE_GROUP_SETTINGS' and
                'Outputs' in group):
                
                outputs = group['Outputs']
                for output in outputs:
                    # Check if NameModifier is missing
                    if 'NameModifier' not in output:
                        # Generate NameModifier based on video settings
                        name_modifier = self._generate_name_modifier(output)
                        if name_modifier:
                            output['NameModifier'] = name_modifier
                            self.logger.info(f"Added missing NameModifier: {name_modifier}")
    
    def _generate_name_modifier(self, output: Dict) -> str:
        """Generate NameModifier based on video settings"""
        if ('VideoDescription' in output and 
            'Width' in output['VideoDescription'] and 
            'Height' in output['VideoDescription']):
            width = output['VideoDescription']['Width']
            height = output['VideoDescription']['Height']
            resolution_part = f"_{width}x{height}"
            
            # Add bitrate information if available
            if ('VideoDescription' in output and 
                'CodecSettings' in output['VideoDescription'] and 
                'H264Settings' in output['VideoDescription']['CodecSettings']):
                
                h264_settings = output['VideoDescription']['CodecSettings']['H264Settings']
                if 'Bitrate' in h264_settings:
                    return f"{resolution_part}_{h264_settings['Bitrate']}_mc"
                elif 'MaxBitrate' in h264_settings:
                    return f"{resolution_part}_{h264_settings['MaxBitrate']}_mc"
                else:
                    return f"{resolution_part}_mc"
        
        return "_mc"  # Default if we can't extract resolution/bitrate
        
    def _process_source_data(self, source_data, current_path, rule_lookup, target_data, processed_params):
        """Process source data recursively and apply matching rules"""
        if not isinstance(source_data, dict):
            return
            
        for key, value in source_data.items():
            # Build the current path
            path = f"{current_path}.{key}" if current_path else key
            
            # Skip already processed parameters
            if path in processed_params:
                self.logger.debug(f"Skipping already processed parameter: {path}")
                continue
                
            # Check if we have rules for this path
            if path in rule_lookup:
                # Process all rules for this path
                for rule in rule_lookup[path]:
                    self._process_rule(rule, path, value, source_data, target_data, processed_params)
            
            # If this is a dictionary, process it recursively
            if isinstance(value, dict):
                self._process_source_data(value, path, rule_lookup, target_data, processed_params)
            # If this is a list, process each item if they are dictionaries
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        list_path = f"{path}[{i}]"
                        self._process_source_data(item, list_path, rule_lookup, target_data, processed_params)
    
    def _process_rule(self, rule, source_path, source_value, source_data, target_data, processed_params):
        """Process a single rule for a given source path and value"""
        source_regex = rule['source'].get('regex')
        
        self.logger.debug(f"Processing rule for {source_path}, value: {source_value}")
        
        # Check if this parameter was already processed by rate control settings handler
        rate_control_params = ['cbr', 'cabr', 'bitrate', 'maxrate', 'minrate']
        if source_path in rate_control_params and source_path in processed_params:
            self.logger.info(f"Skipping rule for {source_path}={source_value} as it was already processed by rate control settings handler")
            return
        
        # Add to processed parameters
        processed_params.add(source_path)
        
        # Check condition (if any)
        if 'condition' in rule['source'] and source_value is not None:
            if not self.evaluate_condition(rule['source']['condition'], source_value, source_data):
                self.logger.warning(f"Skipping rule for {source_path}={source_value} due to source condition not matching")
                return
        
        # If source value doesn't exist, use default (if provided)
        if source_value is None:
            if 'default' in rule['source']:
                source_value = rule['source']['default']
                self.logger.debug(f"Using default value for {source_path}: {source_value}")
            else:
                self.logger.debug(f"Skipping rule for {source_path} (no value and no default)")
                return
        
        # Process target mapping (can be single target or multiple targets)
        targets = rule['target'] if isinstance(rule['target'], list) else [rule['target']]
        
        for target in targets:
            target_path = target['path']
            transform = target.get('transform')
            
            # Check target condition (if any)
            if 'condition' in target:
                if not self.evaluate_condition(target['condition'], source_value, source_data):
                    self.logger.warning(f"Skipping target {target_path} for source {source_path}={source_value} due to target condition not matching")
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
                        self.logger.warning(f"Regex pattern {source_regex} did not match {source_value} for {source_path}")
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
                    
                    # If transformation returns None, it means the value didn't match any mapping
                    if target_value is None:
                        self.logger.warning(f"Skipping parameter mapping for {source_path}={source_value} → {target_path} (no matching transformation)")
                        # Add to mapped parameters list (as mapped but skipped)
                        if not hasattr(self, 'mapped_parameters'):
                            self.mapped_parameters = []
                        self.mapped_parameters.append((source_path, source_value, target_path, "SKIPPED_NO_MATCHING_TRANSFORM"))
                        continue
                        
                    self.logger.debug(f"Transformed {original_value} using {transform} to {type(target_value)}")
            
            # Set target value using the improved nested value setter
            self._set_nested_value(target_data, target_path, target_value)
            # Log the parameter mapping with more detail
            self.logger.info(f"Mapped parameter: {source_path}={source_value} → {target_path}={target_value}")
            
            # Add to mapped parameters list
            if not hasattr(self, 'mapped_parameters'):
                self.mapped_parameters = []
            self.mapped_parameters.append((source_path, source_value, target_path, target_value))
            
        
    def _log_unmapped_parameters(self, source_data: Dict, processed_params: set, parent_path: str = ""):
        """Log parameters that don't have mapping rules"""
        if not isinstance(source_data, dict):
            return
            
        for key, value in source_data.items():
            current_path = f"{parent_path}.{key}" if parent_path else key
            
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
                # Add to a list of unmapped parameters for summary
                if not hasattr(self, 'unmapped_parameters'):
                    self.unmapped_parameters = []
                self.unmapped_parameters.append((current_path, value))


def batch_convert(converter: ConfigConverter, source_dir: str, output_dir: str, template_file: str = None, schema_file: str = None):
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


def setup_logging(log_file=None, verbose=False):
    """Setup logging to both console and file if log_file is provided"""
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
    """Setup file logging for a specific conversion"""
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
    
    # Set up basic logging first
    setup_logging(verbose=args.verbose)
    
    # Create converter instance
    converter = ConfigConverter(args.rules)
    
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
