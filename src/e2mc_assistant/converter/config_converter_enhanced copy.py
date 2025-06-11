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
        self.register_custom_function('process_alternate_sources', self._process_alternate_sources)
        self.register_custom_function('generate_outputs_from_streams', self._generate_outputs_from_streams)
        self.register_custom_function('generate_outputs_with_settings', self.generate_outputs_with_settings)
        
    def register_custom_function(self, name: str, func: Callable):
        """Register a custom transformation function"""
        self.custom_functions[name] = func
        
    def generate_outputs_with_settings(self, streams: List, context: Dict) -> List:
        """
        Generate outputs from streams and apply both rate control and audio settings
        
        This function combines _generate_outputs_from_streams with _process_rate_control_settings
        and _process_audio_settings to create outputs with proper settings, while respecting
        video-only and audio-only outputs. It also applies stream-specific rules from
        mp4_rules_fixed.yaml.
        
        Args:
            streams: List of stream dictionaries from Encoding.com format
            context: Context dictionary with source_data and other information
            
        Returns:
            List of output structures for MediaConvert with proper settings
        """
        # 添加防止递归调用的标记
        if context.get('processing_streams'):
            self.logger.warning("Detected recursive call to generate_outputs_with_settings, returning empty list to prevent infinite loop")
            return []
        
        # 设置处理标记
        context['processing_streams'] = True
        
        try:
            # First, generate basic outputs from streams
            outputs = self._generate_outputs_from_streams(streams, context)
            source_data = context.get('source_data', {})
            
            # Track processed parameters
            processed_params = set()
            
            # Process each output to apply rate control and audio settings
            for i, output in enumerate(outputs):
                # Create a temporary target data structure to use with processing methods
                temp_target = {"Settings": {"OutputGroups": [{"Outputs": [output]}]}}
                
                # Check if this is a video-only output (no AudioDescriptions)
                is_video_only = "AudioDescriptions" not in output
                
                # Check if this is an audio-only output (no VideoDescription)
                is_audio_only = "VideoDescription" not in output
                
                # Get the corresponding stream data to use as source_data for processing
                # This ensures we use stream-specific settings rather than global settings
                stream_data = streams[i] if i < len(streams) else {}
                
                # Apply rate control settings for video (skip for audio-only outputs)
                if not is_audio_only and "VideoDescription" in output:
                    # Use stream data as source_data instead of global source_data
                    # This ensures we get stream-specific settings like cbr, bitrate, etc.
                    rate_control_processed = self._process_rate_control_settings(stream_data, temp_target)
                    if rate_control_processed:
                        processed_params.update(rate_control_processed)
                    self.logger.debug(f"Applied rate control settings for output {i} using stream-specific data")
                elif is_audio_only:
                    self.logger.debug(f"Skipping rate control settings for audio-only output {i}")
                
                # Apply audio settings (skip for video-only outputs)
                if not is_video_only and ("AudioDescriptions" in output or is_audio_only):
                    # Use stream data for audio settings as well
                    audio_processed = self._process_audio_settings(stream_data, temp_target)
                    if audio_processed:
                        processed_params.update(audio_processed)
                    self.logger.debug(f"Applied audio settings for output {i} using stream-specific data")
                elif is_video_only:
                    self.logger.debug(f"Skipping audio settings for video-only output {i}")
                    
                # Extract the processed output back
                processed_output = temp_target["Settings"]["OutputGroups"][0]["Outputs"][0]
                
                # Update the original output with processed settings
                for key, value in processed_output.items():
                    output[key] = value
            
            # Now load the rules from mp4_rules_fixed.yaml, but exclude stream rules
            rules_file = os.path.join(os.path.dirname(__file__), 'rules/mp4_rules_fixed.yaml')
            with open(rules_file, 'r') as f:
                rules_data = yaml.safe_load(f)
            
            # Create a rule lookup dictionary for faster access
            rule_lookup = {}
            dummy_rules = []
            
            # Organize rules by their source path for easier lookup, but skip stream rules
            for rule in rules_data.get('rules', []):
                # Skip rules that target stream path to avoid recursion
                if rule['source'].get('path') == 'stream':
                    self.logger.info("Skipping stream rule to avoid recursion")
                    continue
                    
                if rule['source'].get('type') == 'dummy':
                    dummy_rules.append(rule)
                    continue
                    
                source_path = rule['source']['path']
                if source_path not in rule_lookup:
                    rule_lookup[source_path] = []
                rule_lookup[source_path].append(rule)
            
            # Process dummy rules to mark parameters as processed
            for rule in dummy_rules:
                source_path = rule['source']['path']
                source_value = self.get_value_by_path(source_data, source_path)
                self.logger.debug(f"Processing dummy rule for {source_path}")
                processed_params.add(source_path)
                # Log the dummy rule match
                self.logger.debug(f"Mapped parameter: {source_path}={source_value} → [DUMMY RULE]")
            
            # Now process each stream individually with the rules
            for i, stream in enumerate(streams):
                # Create a temporary target data structure for this stream's output
                temp_target = {"Settings": {"OutputGroups": [{"Outputs": [outputs[i]]}]}}
                
                # Create a separate processed_params set for each stream to avoid skipping parameters
                # that were processed in previous streams
                stream_processed_params = set()
                
                # Process each parameter in the stream using the rules
                self.logger.info(f"Applying rules to stream {i+1}/{len(streams)}")
                
                # Process the stream with rules, but avoid recursive processing
                # by not processing 'stream' paths
                self._process_source_data(stream, "", rule_lookup, temp_target, stream_processed_params)
                
                # Extract the processed output back
                processed_output = temp_target["Settings"]["OutputGroups"][0]["Outputs"][0]
                
                # Update the original output with processed settings
                for key, value in processed_output.items():
                    if key not in outputs[i]:
                        outputs[i][key] = value
                    elif isinstance(outputs[i][key], dict) and isinstance(value, dict):
                        # Merge dictionaries for nested settings
                        outputs[i][key].update(value)
                
                # Add the stream's processed parameters to the global set
                processed_params.update(stream_processed_params)
            
            # Clean up outputs based on video_only and audio_only flags
            for i, stream in enumerate(streams):
                if i < len(outputs):
                    # Check if this stream has video_only=yes
                    if stream.get('video_only') == 'yes' and 'AudioDescriptions' in outputs[i]:
                        self.logger.info(f"Removing AudioDescriptions from output {i} because video_only=yes is set")
                        outputs[i].pop('AudioDescriptions', None)
                    
                    # Check if this stream has audio_only=yes
                    if stream.get('audio_only') == 'yes' and 'VideoDescription' in outputs[i]:
                        self.logger.info(f"Removing VideoDescription from output {i} because audio_only=yes is set")
                        outputs[i].pop('VideoDescription', None)
            
            self.logger.info(f"Final outputs after cleanup: {len(outputs)} outputs")
            return outputs
                    
            return outputs
        finally:
            # 确保无论如何都清除处理标记
            if 'processing_streams' in context:
                del context['processing_streams']
        
        
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
            # 防止递归调用
            if transform_name == "generate_outputs_with_settings" and context and context.get('processing_streams'):
                self.logger.warning(f"Detected potential recursive call to {transform_name}, skipping transformation")
                return value
            return self.custom_functions[transform_name](value, context)
            
        # Special case for audio_volume_format
        if transform_name == "audio_volume_format":
            try:
                # (Calculate -27 + 25 * value) / 100
                volume_value = float(value)
                return -27 + (25 * volume_value / 100)
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
                self.logger.info(f"Evaluating AND condition with {len(condition['conditions'])} subconditions")
                result = all(self.evaluate_condition(subcond, source_value, source_data) 
                          for subcond in condition['conditions'])
                self.logger.info(f"AND condition result: {result}")
                return result
            
            elif logical_op == 'OR':
                # Any subcondition can be true
                self.logger.info(f"Evaluating OR condition with {len(condition['conditions'])} subconditions")
                result = any(self.evaluate_condition(subcond, source_value, source_data) 
                          for subcond in condition['conditions'])
                self.logger.info(f"OR condition result: {result}")
                return result
            
            elif logical_op == 'NOT':
                # Negate the result of the subcondition
                self.logger.info(f"Evaluating NOT condition")
                result = not self.evaluate_condition(condition['condition'], source_value, source_data)
                self.logger.info(f"NOT condition result: {result}")
                return result
        
        # Handle simple condition (backward compatible with existing rules)
        # If condition has source_path, get value from there instead
        if 'source_path' in condition and source_data:
            source_value = self.get_value_by_path(source_data, condition['source_path'])
            self.logger.info(f"Condition using source_path {condition['source_path']}, value: {source_value}")
            
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
            
        self.logger.info(f"Condition evaluation: {op} {source_value} {compare_value} = {result}")
        return result
    

        
    def _process_alternate_sources(self, alternate_sources: List, context: Dict) -> Dict:
        """Process multiple alternate audio sources for HLS/DASH outputs
        
        This function processes alternate_source elements from Encoding.com format
        and converts them to AWS MediaConvert audio selectors.
        
        Args:
            alternate_sources: List of alternate_source dictionaries
            context: Context dictionary with source_data and other information
            
        Returns:
            Dictionary of audio selectors for MediaConvert
        """
        audio_selectors = {}
        source_data = context.get('source_data', {})
        
        # Language code mapping
        language_code_format = {
            "es": "SPA",
            "fr": "FRA",
            "en": "ENG",
            "de": "DEU",
            "it": "ITA",
            "ja": "JPN",
            "ko": "KOR",
            "pt": "POR",
            "ru": "RUS",
            "zh": "CHI"
        }
        
        self.logger.debug(f"Processing {len(alternate_sources)} alternate audio sources")
        
        # Process each alternate source
        for i, source in enumerate(alternate_sources):
            # Create a unique selector name
            selector_name = f"Audio Selector {i+1}"
            
            # Create base selector
            selector = {}
            
            # Always add SelectorType as LANGUAGE_CODE
            selector['SelectorType'] = "LANGUAGE_CODE"
            
            # Set language code if available
            if 'language' in source:
                language = source['language'].lower()
                # Use the language code mapping
                if language in language_code_format:
                    selector['LanguageCode'] = language_code_format[language]
                # Fallback to previous mappings for compatibility
                elif language in ['eng', 'english']:
                    selector['LanguageCode'] = 'ENG'
                elif language in ['spa', 'spanish']:
                    selector['LanguageCode'] = 'SPA'
                elif language in ['fre', 'fra', 'french']:
                    selector['LanguageCode'] = 'FRA'
                elif language in ['ger', 'deu', 'german']:
                    selector['LanguageCode'] = 'DEU'
                else:
                    # Use as is for other languages
                    selector['LanguageCode'] = language.upper()
            
            # Set custom language name if available
            if 'audio_name' in source:
                selector['CustomLanguageCode'] = source['audio_name']
            
            # Set as default if specified
            if source.get('alternate_default') == 'yes':
                selector['DefaultSelection'] = 'DEFAULT'
            else:
                selector['DefaultSelection'] = 'NOT_DEFAULT'
            
            # Add to audio selectors dictionary
            audio_selectors[selector_name] = selector
            self.logger.debug(f"Created audio selector: {selector_name} with settings: {selector}")
        
        # If no selectors were created, add a default one
        if not audio_selectors:
            audio_selectors["Audio Selector 1"] = {
                "DefaultSelection": "DEFAULT",
                "SelectorType": "LANGUAGE_CODE"
            }
            self.logger.debug("Added default audio selector")
        
        return audio_selectors
        
    def _generate_outputs_from_streams(self, streams: List, context: Dict) -> List:
        """Generate basic output structures from streams
        
        This function analyzes the streams in the Encoding.com format and generates
        the corresponding basic output structures for AWS MediaConvert.
        
        Args:
            streams: List of stream dictionaries from Encoding.com format
            context: Context dictionary with source_data and other information
            
        Returns:
            List of basic output structures for MediaConvert
        """
        outputs = []
        source_data = context.get('source_data', {})
        output_format = self.get_value_by_path(source_data, 'output')
        
        self.logger.debug(f"Generating outputs from {len(streams)} streams for format: {output_format}")
        
        # Count video and audio streams
        video_streams = []
        audio_streams = []
        
        for stream in streams:
            if stream.get('audio_only') == 'yes':
                audio_streams.append(stream)
            elif stream.get('video_only') == 'yes':
                video_streams.append(stream)
            else:
                # If not explicitly marked, check for typical video parameters
                if 'size' in stream or 'bitrate' in stream:
                    video_streams.append(stream)
                # If it has audio parameters, consider it an audio stream too
                if 'audio_bitrate' in stream or 'audio_sample_rate' in stream:
                    audio_streams.append(stream)
        
        self.logger.debug(f"Found {len(video_streams)} video streams and {len(audio_streams)} audio streams")
        
        # Create template for output based on format
        if output_format == "advanced_hls":
            container = "M3U8"
            container_settings_key = "M3u8Settings"
        elif output_format in ["fmp4_hls", "advanced_fmp4"]:
            container = "CMFC"
            container_settings_key = "CmfcSettings"
        elif output_format == "advanced_dash":
            container = "MPD"
            container_settings_key = "MpdSettings"
        elif output_format == "mp4":
            container = "MP4"
            container_settings_key = "Mp4Settings"
        else:
            container = "MP4"  # Default
            container_settings_key = "Mp4Settings"
            
        # Generate outputs for video streams
        for i, stream in enumerate(video_streams):
            output = {
                "ContainerSettings": {
                    "Container": container,
                    container_settings_key: {}
                }
            }
            
            # Only add VideoDescription if not audio_only
            if stream.get('audio_only') != 'yes':
                output["VideoDescription"] = {
                    "CodecSettings": {
                        "Codec": "H_264"
                    }
                }
                
                # Set basic video parameters based on stream data
                if 'size' in stream:
                    size_match = re.match(r'(\d+)x(\d+)', stream['size'])
                    if size_match:
                        width, height = size_match.groups()
                        output['VideoDescription']['Width'] = int(width)
                        output['VideoDescription']['Height'] = int(height)
            
            # Add basic name modifier
            name_modifier = f"_video_{i+1}"
            if 'size' in stream:
                name_modifier = f"_{stream['size']}"
            if 'bitrate' in stream:
                bitrate_match = re.match(r'(\d+)k', stream['bitrate'])
                if bitrate_match:
                    name_modifier += f"_{bitrate_match.group(1)}K"
            
            output["NameModifier"] = name_modifier
            
            # Only add AudioDescriptions if not video_only
            # Explicitly check for 'yes' to ensure we don't add AudioDescriptions for video_only streams
            if stream.get('video_only') != 'yes':
                output["AudioDescriptions"] = [
                    {
                        "CodecSettings": {
                            "Codec": "AAC"
                        }
                    }
                ]
            
            outputs.append(output)
            self.logger.debug(f"Generated basic video output structure with name modifier: {name_modifier}")
        
        # Generate outputs for audio-only streams
        for i, stream in enumerate(audio_streams):
            # Skip if this stream was already included with video
            if stream in video_streams and stream.get('audio_only') != 'yes':
                continue
                
            output = {
                "ContainerSettings": {
                    "Container": container,
                    container_settings_key: {}
                },
                "AudioDescriptions": [
                    {
                        "CodecSettings": {
                            "Codec": "AAC"
                        }
                    }
                ]
            }
            
            # Add basic name modifier
            name_modifier = f"_audio_{i+1}"
            if 'audio_bitrate' in stream:
                audio_bitrate_match = re.match(r'(\d+)k', stream['audio_bitrate'])
                if audio_bitrate_match:
                    name_modifier = f"_audio_{audio_bitrate_match.group(1)}K"
            
            # Add codec info to name modifier
            if 'audio_codec' in stream:
                if stream['audio_codec'] == "eac3":
                    name_modifier += "_eac3"
                elif stream['audio_codec'] in ["dolby_aac", "dolby_heaac", "libfaac"]:
                    name_modifier += "_aac"
            
            # Add channels info to name modifier
            if 'audio_channels_number' in stream:
                channels = int(stream['audio_channels_number'])
                if channels == 6:
                    name_modifier += "_surround"
                elif channels == 2:
                    name_modifier += "_stereo"
                elif channels == 1:
                    name_modifier += "_mono"
            
            output["NameModifier"] = name_modifier
            
            outputs.append(output)
            self.logger.debug(f"Generated basic audio output structure with name modifier: {name_modifier}")
        
        self.logger.debug(f"Generated a total of {len(outputs)} basic output structures")
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
    
    def _process_rate_control_settings(self, source_data: Dict, target_data: Dict) -> set:
        """
        Process rate control settings (CBR/VBR/QVBR) based on complex rules
        
        Args:
            source_data: Source data dictionary
            target_data: Target data dictionary to update
            
        Returns:
            Set of processed parameter names
        """
        # Check if output is mp4, otherwise log warning and return
        output_format = self.get_value_by_path(source_data, 'output')
        # if output_format != 'mp4':
        #     self.logger.warning(f"Rate control settings processing is only supported for MP4 output, got {output_format}. "
        #                        "Need to add independent processing function for this format.")
        #     return False
            
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
                self.logger.info(f"Set RateControlMode to CBR because <cbr>=yes")
                
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
                        self.logger.info(f"Set RateControlMode to QVBR because <cbr>=no and <cabr>=yes")
                        
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
                        self.logger.info(f"Set RateControlMode to VBR because <cbr>=no and <cabr>=no")
                        
                        if bitrate_str:
                            self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate)
                            processed_params.add('bitrate')
                            self.logger.info(f"Set Bitrate to {bitrate} from <bitrate>={bitrate_str}")
                            
                        if maxrate_str:
                            self._set_nested_value(target_data, f"{target_path}.MaxBitrate", maxrate)
                            processed_params.add('maxrate')
                            self.logger.info(f"Set MaxBitrate to {maxrate} from <maxrate>={maxrate_str}")
                else:
                    # New case: cbr=no and cabr doesn't exist
                    if bitrate_str:
                        # Set RateControlMode to VBR
                        self._set_nested_value(target_data, f"{target_path}.RateControlMode", "VBR")
                        self.logger.info(f"Set RateControlMode to VBR because <cbr>=no and <cabr> doesn't exist")
                        
                        # Set Bitrate
                        self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate)
                        processed_params.add('bitrate')
                        self.logger.info(f"Set Bitrate to {bitrate} from <bitrate>={bitrate_str}")
                        
                        # Set MaxBitrate to 2.5 * Bitrate
                        calculated_maxrate = int(bitrate * 2.5)
                        self._set_nested_value(target_data, f"{target_path}.MaxBitrate", calculated_maxrate)
                        self.logger.info(f"Setting MaxBitrate to {calculated_maxrate} (2.5 * Bitrate)")
                        
                        # Log if minrate is ignored
                        if minrate_str:
                            self.logger.info(f"Ignoring <minrate>={minrate_str} (not supported in MediaConvert)")
                            processed_params.add('minrate')
                            
        
        # Case 2: If <cbr> doesn't exist
        elif bitrate_str:
            processed_params.add('bitrate')
            
            if not maxrate_str:
                # Case 2.a: bitrate exists, maxrate doesn't exist or is empty
                self._set_nested_value(target_data, f"{target_path}.RateControlMode", "VBR")
                self.logger.info(f"Set RateControlMode to VBR because <cbr> doesn't exist and <maxrate> doesn't exist")
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
                    self.logger.info(f"Set RateControlMode to VBR because <cbr> doesn't exist and <maxrate> > <bitrate>")
                    self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate_value)
                    self._set_nested_value(target_data, f"{target_path}.MaxBitrate", maxrate_value)
                    self.logger.info(f"Set Bitrate to {bitrate_value} from <bitrate>={bitrate_str}")
                    self.logger.info(f"Set MaxBitrate to {maxrate_value} from <maxrate>={maxrate_str}")
                    
                elif maxrate_value == bitrate_value:
                    # Case 2.c: bitrate exists, maxrate exists and equals bitrate
                    self._set_nested_value(target_data, f"{target_path}.RateControlMode", "CBR")
                    self.logger.info(f"Set RateControlMode to CBR because <cbr> doesn't exist and <maxrate> equals <bitrate>")
                    self._set_nested_value(target_data, f"{target_path}.Bitrate", bitrate_value)
                    self.logger.info(f"Set Bitrate to {bitrate_value} from <bitrate>={bitrate_str}")
                    self.logger.info(f"Using CBR mode because maxrate equals bitrate")
                
                # Log if minrate is ignored
                if minrate_str:
                    self.logger.info(f"Ignoring <minrate>={minrate_str} (not supported in MediaConvert)")
                    processed_params.add('minrate')
        
        # Return processed parameters
        return processed_params
    
    def _process_video_codec_settings(self, source_data: Dict, target_data: Dict) -> bool:
        """
        Process video codec settings, setting defaults if needed
        
        Args:
            source_data: Source data dictionary
            target_data: Target data dictionary to update
            
        Returns:
            True if video codec settings were processed, False otherwise
        """
        # Check if video_codec exists
        video_codec = self.get_value_by_path(source_data, 'video_codec')
        
        # If video_codec doesn't exist, set default to AVC (H.264)
        if not video_codec:
            target_path = "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.Codec"
            self._set_nested_value(target_data, target_path, "H_264")
            self.logger.info(f"Set {target_path} to H_264 (default because <video_codec> not specified)")
            return {'video_codec'}
        
        return set()
    
    def _process_audio_settings(self, source_data: Dict, target_data: Dict) -> bool:
        """
        Process audio codec settings based on complex rules
        
        Args:
            source_data: Source data dictionary
            target_data: Target data dictionary to update
            
        Returns:
            True if audio settings were processed, False otherwise
        """
        # Get relevant source parameters
        audio_codec = self.get_value_by_path(source_data, 'audio_codec')
        audio_bitrate_str = self.get_value_by_path(source_data, 'audio_bitrate')
        audio_sample_rate = self.get_value_by_path(source_data, 'audio_sample_rate')
        audio_maxrate_str = self.get_value_by_path(source_data, 'audio_maxrate')
        audio_minrate_str = self.get_value_by_path(source_data, 'audio_minrate')
        
        # Track if we've processed these parameters
        processed_params = set()
        
        # Get the target path for AudioDescriptions
        target_path = "Settings.OutputGroups[0].Outputs[0].AudioDescriptions[0]"
        
        # Parse audio bitrate value
        audio_bitrate = None
        if audio_bitrate_str:
            processed_params.add('audio_bitrate')
            bitrate_match = re.match(r'(\d+)k', audio_bitrate_str)
            if bitrate_match:
                audio_bitrate = int(bitrate_match.group(1)) * 1000
            else:
                try:
                    audio_bitrate = int(audio_bitrate_str)
                except (ValueError, TypeError):
                    self.logger.warning(f"Failed to parse audio_bitrate: {audio_bitrate_str}")
        
        # Case 1: If <audio_codec> exists and is not empty
        if audio_codec:
            processed_params.add('audio_codec')
            
            # Case 1.a: audio_codec is one of the AAC variants
            if audio_codec in ["dolby_aac", "dolby_heaac", "libfaac"]:
                # i. Set codec to AAC
                self._set_nested_value(target_data, f"{target_path}.CodecSettings.Codec", "AAC")
                self.logger.info(f"Set AudioDescriptions[0].CodecSettings.Codec to AAC from <audio_codec>={audio_codec}")
                
                # ii. Set default bitrate
                self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.Bitrate", 96000)
                self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.Bitrate to default value 96000")
                
                # iii. Set default sample rate
                self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.SampleRate", 48000)
                self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.SampleRate to default value 48000")
                
                # Set default coding mode to stereo
                self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.CodingMode", "CODING_MODE_2_0")
                self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.CodingMode to CODING_MODE_2_0 (default stereo)")
                
                # iv. Override bitrate if specified
                if audio_bitrate:
                    self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.Bitrate", audio_bitrate)
                    self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.Bitrate to {audio_bitrate} from <audio_bitrate>={audio_bitrate_str}")
                
                # v. Override sample rate if specified
                if audio_sample_rate:
                    processed_params.add('audio_sample_rate')
                    self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.SampleRate", audio_sample_rate)
                    self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.SampleRate to {audio_sample_rate} from <audio_sample_rate>={audio_sample_rate}")
                
                # vi. Log if audio_maxrate or audio_minrate are ignored
                if audio_maxrate_str:
                    processed_params.add('audio_maxrate')
                    self.logger.info(f"Ignoring <audio_maxrate>={audio_maxrate_str} (not supported for AAC in MediaConvert)")
                
                if audio_minrate_str:
                    processed_params.add('audio_minrate')
                    self.logger.info(f"Ignoring <audio_minrate>={audio_minrate_str} (not supported for AAC in MediaConvert)")
            
            # Case 1.b: audio_codec is AC3
            elif audio_codec == "ac3":
                # i. Set codec to AC3
                self._set_nested_value(target_data, f"{target_path}.CodecSettings.Codec", "AC3")
                self.logger.info(f"Set AudioDescriptions[0].CodecSettings.Codec to AC3 from <audio_codec>={audio_codec}")
                
                # ii. Set bitrate if specified
                if audio_bitrate:
                    self._set_nested_value(target_data, f"{target_path}.CodecSettings.Ac3Settings.Bitrate", audio_bitrate)
                    self.logger.info(f"Set AudioDescriptions[0].CodecSettings.Ac3Settings.Bitrate to {audio_bitrate} from <audio_bitrate>={audio_bitrate_str}")
                
                # Log if audio_sample_rate, audio_maxrate or audio_minrate are ignored
                if audio_sample_rate:
                    processed_params.add('audio_sample_rate')
                    self.logger.info(f"Ignoring <audio_sample_rate>={audio_sample_rate} (not supported for AC3 in MediaConvert)")
                
                if audio_maxrate_str:
                    processed_params.add('audio_maxrate')
                    self.logger.info(f"Ignoring <audio_maxrate>={audio_maxrate_str} (not supported for AC3 in MediaConvert)")
                
                if audio_minrate_str:
                    processed_params.add('audio_minrate')
                    self.logger.info(f"Ignoring <audio_minrate>={audio_minrate_str} (not supported for AC3 in MediaConvert)")
            
            # Case 1.c: audio_codec is EAC3
            elif audio_codec == "eac3":
                # i. Set codec to EAC3
                self._set_nested_value(target_data, f"{target_path}.CodecSettings.Codec", "EAC3")
                self.logger.info(f"Set AudioDescriptions[0].CodecSettings.Codec to EAC3 from <audio_codec>={audio_codec}")
                
                # ii. Set bitrate if specified
                if audio_bitrate:
                    self._set_nested_value(target_data, f"{target_path}.CodecSettings.Eac3Settings.Bitrate", audio_bitrate)
                    self.logger.info(f"Set AudioDescriptions[0].CodecSettings.Eac3Settings.Bitrate to {audio_bitrate} from <audio_bitrate>={audio_bitrate_str}")
                
                # Log if audio_sample_rate, audio_maxrate or audio_minrate are ignored
                if audio_sample_rate:
                    processed_params.add('audio_sample_rate')
                    self.logger.info(f"Ignoring <audio_sample_rate>={audio_sample_rate} (not supported for EAC3 in MediaConvert)")
                
                if audio_maxrate_str:
                    processed_params.add('audio_maxrate')
                    self.logger.info(f"Ignoring <audio_maxrate>={audio_maxrate_str} (not supported for EAC3 in MediaConvert)")
                
                if audio_minrate_str:
                    processed_params.add('audio_minrate')
                    self.logger.info(f"Ignoring <audio_minrate>={audio_minrate_str} (not supported for EAC3 in MediaConvert)")
            
            # Case 1.d: audio_codec is something else
            else:
                self.logger.warning(f"Unsupported <audio_codec>={audio_codec}. Manual conversion logic needed.")
                # Still mark as processed to avoid double processing
            if audio_bitrate_str:
                processed_params.add('audio_bitrate')
            if audio_sample_rate:
                processed_params.add('audio_sample_rate')
            if audio_maxrate_str:
                processed_params.add('audio_maxrate')
            if audio_minrate_str:
                processed_params.add('audio_minrate')
        
        # Case 2: If <audio_codec> doesn't exist or is empty
        else:
            # a. Set codec to AAC
            self._set_nested_value(target_data, f"{target_path}.CodecSettings.Codec", "AAC")
            self.logger.info(f"Set AudioDescriptions[0].CodecSettings.Codec to AAC (default because <audio_codec> not specified)")
            
            # b. Set default bitrate
            self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.Bitrate", 96000)
            self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.Bitrate to default value 96000")
            
            # c. Set default sample rate
            self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.SampleRate", 48000)
            self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.SampleRate to default value 48000")
            
            # Set default coding mode to stereo
            self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.CodingMode", "CODING_MODE_2_0")
            self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.CodingMode to CODING_MODE_2_0 (default stereo)")
            
            # d. Override bitrate if specified
            if audio_bitrate:
                self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.Bitrate", audio_bitrate)
                self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.Bitrate to {audio_bitrate} from <audio_bitrate>={audio_bitrate_str}")
            
            # e. Override sample rate if specified
            if audio_sample_rate:
                processed_params.add('audio_sample_rate')
                self._set_nested_value(target_data, f"{target_path}.CodecSettings.AacSettings.SampleRate", audio_sample_rate)
                self.logger.info(f"Set AudioDescriptions[0].CodecSettings.AacSettings.SampleRate to {audio_sample_rate} from <audio_sample_rate>={audio_sample_rate}")
            
            # f. Log if audio_maxrate or audio_minrate are ignored
            if audio_maxrate_str:
                processed_params.add('audio_maxrate')
                self.logger.info(f"Ignoring <audio_maxrate>={audio_maxrate_str} (not supported for AAC in MediaConvert)")
            
            if audio_minrate_str:
                processed_params.add('audio_minrate')
                self.logger.info(f"Ignoring <audio_minrate>={audio_minrate_str} (not supported for AAC in MediaConvert)")
        
        # Return processed parameters
        return processed_params
    
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
        
        # Check if this is a multi-stream configuration
        streams = self.get_value_by_path(source_data, 'stream')
        is_multi_stream = streams is not None and isinstance(streams, list) and len(streams) > 0
        
        if is_multi_stream:
            self.logger.info(f"Detected multi-stream configuration with {len(streams)} streams")
            # Handle multi-stream scenario using specialized functions
            context = {'source_data': source_data}
            
            # Process streams directly using the specialized functions
            # This avoids the need for stream path rules that could cause recursion
            # outputs = self._generate_outputs_from_streams(streams, context)
            
            # Apply settings to the generated outputs
            context = {'source_data': source_data}
            outputs_with_settings = self.generate_outputs_with_settings(streams, context)
            
            # Add the outputs to the target data
            if outputs_with_settings:
                if 'Settings' not in target_data:
                    target_data['Settings'] = {}
                if 'OutputGroups' not in target_data['Settings']:
                    target_data['Settings']['OutputGroups'] = [{}]
                if not target_data['Settings']['OutputGroups']:
                    target_data['Settings']['OutputGroups'] = [{}]
                
                # Add outputs to the first output group
                if 'Outputs' not in target_data['Settings']['OutputGroups'][0]:
                    target_data['Settings']['OutputGroups'][0]['Outputs'] = []
                
                target_data['Settings']['OutputGroups'][0]['Outputs'].extend(outputs_with_settings)
            
            # Mark stream parameter as processed
            processed_params.add('stream')
        else:
            # Non-multi-stream scenario - use the original approach
            # Process rate control settings first (special handling for CBR/VBR/QVBR)
            if self._process_rate_control_settings(source_data, target_data):
                # Mark these parameters as processed
                for param in ['cbr', 'cabr', 'bitrate', 'maxrate', 'minrate']:
                    if self.get_value_by_path(source_data, param) is not None:
                        processed_params.add(param)
                        self.logger.info(f"Parameter {param} processed by custom rate control handler")
            
            # Process audio settings next (special handling for audio codec and related settings)
            audio_processed_params = self._process_audio_settings(source_data, target_data)
            if audio_processed_params:
                processed_params.update(audio_processed_params)
                self.logger.info(f"Audio parameters processed by custom audio settings handler")
                
            # Process video codec settings (set default if needed)
            video_processed_params = self._process_video_codec_settings(source_data, target_data)
            if video_processed_params:
                processed_params.update(video_processed_params)
                self.logger.info(f"Video codec parameters processed by custom video codec handler")
        
        # Create a rule lookup dictionary for faster access
        rule_lookup = {}
        dummy_rules = []
        
        # Organize rules by their source path for easier lookup
        for rule in self.rules:
            if rule['source'].get('type') == 'dummy':
                dummy_rules.append(rule)
                continue
                
            source_path = rule['source']['path']
            if source_path not in rule_lookup:
                rule_lookup[source_path] = []
            rule_lookup[source_path].append(rule)
        
        # Process dummy rules to mark parameters as processed
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
                self.logger.info(f"Skipping already processed parameter: {path}={value}")
                continue
                
            # Special handling for stream array
            if key == 'stream' and isinstance(value, list):
                self.logger.info(f"Processing stream array with {len(value)} elements")
                self._process_stream_array(value, path, rule_lookup, target_data, processed_params)
            
            # Check if we have rules for this path
            if path in rule_lookup:
                self.logger.info(f"Found {len(rule_lookup[path])} rules for parameter: {path}={value}")
                # Process all rules for this path
                for rule in rule_lookup[path]:
                    self._process_rule(rule, path, value, source_data, target_data, processed_params)
            else:
                self.logger.info(f"No rules found for parameter: {path}={value}")
            
            # If this is a dictionary, process it recursively
            if isinstance(value, dict):
                self._process_source_data(value, path, rule_lookup, target_data, processed_params)
            # If this is a list, process each item if they are dictionaries
            elif isinstance(value, list) and key != 'stream':  # Skip stream array as it's handled specially
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        list_path = f"{path}[{i}]"
                        self._process_source_data(item, list_path, rule_lookup, target_data, processed_params)
                        
    def _process_stream_array(self, streams, path, rule_lookup, target_data, processed_params):
        """Process stream array elements with rules"""
        # First, find all rules that might apply to stream elements
        stream_rules = {}
        for rule_path, rules in rule_lookup.items():
            # Check if the rule path is a direct parameter name (not a path with dots)
            if '.' not in rule_path:
                stream_rules[rule_path] = rules
        
        self.logger.info(f"Found {len(stream_rules)} potential rules for stream elements")
        
        # Process each stream element
        for i, stream in enumerate(streams):
            stream_path = f"{path}[{i}]"
            self.logger.info(f"Processing stream element {i+1}/{len(streams)}")
            
            # Process each parameter in the stream
            for param_name, param_value in stream.items():
                param_path = f"{stream_path}.{param_name}"
                
                # Skip already processed parameters
                if param_path in processed_params:
                    self.logger.info(f"Skipping already processed parameter: {param_path}={param_value}")
                    continue
                
                # Check if we have rules for this parameter
                if param_name in stream_rules:
                    self.logger.info(f"Found {len(stream_rules[param_name])} rules for stream parameter: {param_name}={param_value}")
                    
                    # Process all rules for this parameter
                    for rule in stream_rules[param_name]:
                        # Create a temporary context with this stream as the source data
                        temp_context = {param_name: param_value}
                        
                        # Process the rule
                        self._process_rule(rule, param_name, param_value, temp_context, target_data, processed_params)
                        
                        # Mark the parameter as processed
                        processed_params.add(param_path)
                else:
                    self.logger.info(f"No rules found for stream parameter: {param_name}={param_value}")
                    
                # If the parameter is a dictionary, process it recursively
                if isinstance(param_value, dict):
                    self._process_source_data(param_value, param_path, rule_lookup, target_data, processed_params)
                # If the parameter is a list, process each item if they are dictionaries
                elif isinstance(param_value, list):
                    for j, item in enumerate(param_value):
                        if isinstance(item, dict):
                            item_path = f"{param_path}[{j}]"
                            self._process_source_data(item, item_path, rule_lookup, target_data, processed_params)
    
    def _process_rule(self, rule, source_path, source_value, source_data, target_data, processed_params):
        """Process a single rule for a given source path and value"""
        source_regex = rule['source'].get('regex')
        
        self.logger.info(f"Processing rule for {source_path}, value: {source_value}")
        
        # Check if this parameter was already processed by rate control settings handler
        rate_control_params = ['cbr', 'cabr', 'bitrate', 'maxrate', 'minrate']
        if source_path in rate_control_params and source_path in processed_params:
            self.logger.info(f"Skipping rule for {source_path}={source_value} as it was already processed by rate control settings handler")
            return
        
        # Add to processed parameters
        processed_params.add(source_path)
        
        # Check condition (if any)
        if 'condition' in rule['source'] and source_value is not None:
            condition_result = self.evaluate_condition(rule['source']['condition'], source_value, source_data)
            self.logger.info(f"Source condition evaluation for {source_path}: {condition_result}")
            if not condition_result:
                self.logger.info(f"Skipping rule for {source_path}={source_value} due to source condition not matching")
                return
        
        # If source value doesn't exist, use default (if provided)
        if source_value is None:
            if 'default' in rule['source']:
                source_value = rule['source']['default']
                self.logger.info(f"Using default value for {source_path}: {source_value}")
            else:
                self.logger.info(f"Skipping rule for {source_path} (no value and no default)")
                return
        
        # Process target mapping (can be single target or multiple targets)
        targets = rule['target'] if isinstance(rule['target'], list) else [rule['target']]
        
        for target in targets:
            target_path = target['path']
            transform = target.get('transform')
            
            # Check target condition (if any)
            if 'condition' in target:
                condition_result = self.evaluate_condition(target['condition'], source_value, source_data)
                self.logger.info(f"Target condition evaluation for {target_path}: {condition_result}")
                if not condition_result:
                    self.logger.info(f"Skipping target {target_path} for source {source_path}={source_value} due to target condition not matching")
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
                        
                        self.logger.info(f"Regex transformed {source_value} to {target_value} using pattern {source_regex}")
                    else:
                        self.logger.info(f"Regex pattern {source_regex} did not match {source_value} for {source_path}")
                        continue
                else:
                    target_value = target['value']
                    self.logger.info(f"Using static value: {target_value}")
            else:
                target_value = source_value
                
                # Apply transformation function
                if transform:
                    context = {'source_data': source_data, 'target_data': target_data}
                    original_value = target_value
                    self.logger.info(f"Applying transformation {transform} to {original_value}")
                    target_value = self.apply_transform(target_value, transform, context)
                    
                    # If transformation returns None, it means the value didn't match any mapping
                    if target_value is None:
                        self.logger.info(f"Skipping parameter mapping for {source_path}={source_value} → {target_path} (no matching transformation)")
                        # Add to mapped parameters list (as mapped but skipped)
                        if not hasattr(self, 'mapped_parameters'):
                            self.mapped_parameters = []
                        self.mapped_parameters.append((source_path, source_value, target_path, "SKIPPED_NO_MATCHING_TRANSFORM"))
                        continue
                        
                    self.logger.info(f"Transformed {original_value} using {transform} to {target_value}")
            
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
