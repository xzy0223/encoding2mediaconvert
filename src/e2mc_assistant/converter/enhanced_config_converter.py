#!/usr/bin/env python3
"""
Enhanced configuration converter for encoding.com to AWS MediaConvert.
This module extends the base ConfigConverter with improved multi-stream support.
"""

import os
import logging
import copy
from typing import Dict, List, Any, Optional

from .config_converter_enhanced import ConfigConverter
from .stream_processor import StreamProcessor
from .output_group_generator import OutputGroupGenerator

class EnhancedConfigConverter(ConfigConverter):
    """
    Enhanced configuration converter with improved multi-stream support.
    Extends the base ConfigConverter class.
    """
    
    def __init__(self, rules_file: str):
        """
        Initialize the enhanced converter.
        
        Args:
            rules_file: Path to the mapping rules file (YAML)
        """
        super().__init__(rules_file)
        self.logger = logging.getLogger('EnhancedConfigConverter')
        self.output_group_generator = OutputGroupGenerator()
    
    def convert(self, source_file: str, template_file: str = None) -> Dict:
        """
        Convert encoding.com configuration to AWS MediaConvert configuration.
        
        Args:
            source_file: Path to the source configuration file (XML or JSON)
            template_file: Optional path to a template MediaConvert file (JSON)
            
        Returns:
            AWS MediaConvert configuration dictionary
        """
        # Parse source file
        if source_file.endswith('.xml'):
            source_data = self.parse_xml(source_file)
            # Save original source data
            self.original_source_data = source_data.copy()
        else:
            with open(source_file, 'r') as f:
                source_data = json.load(f)
                # Save original source data
                self.original_source_data = source_data.copy()
        
        # Determine output format
        output_format = self.determine_output_format(source_data)
        self.logger.info(f"Detected output format: {output_format}")
        
        # Initialize stream processor for this format
        stream_processor = StreamProcessor(output_format)
        
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
        
        # Process basic settings (non-stream related)
        self.process_basic_settings(source_data, target_data, processed_params)
        
        # Process streams if present
        if 'stream' in source_data:
            streams = source_data['stream']
            if not isinstance(streams, list):
                streams = [streams]
            
            # Process streams using the stream processor
            context = {'source_data': source_data}
            outputs = stream_processor.process_streams(streams, context)
            
            # Generate output group settings
            output_group_settings = self.output_group_generator.generate_output_group_settings(
                output_format, source_data)
            
            # Set output group settings and outputs
            self.set_value_by_path(target_data, "Settings.OutputGroups[0].OutputGroupSettings", 
                                  output_group_settings)
            self.set_value_by_path(target_data, "Settings.OutputGroups[0].Outputs", outputs)
            
            # Mark stream as processed
            processed_params.add('stream')
            self.logger.info(f"Processed {len(streams)} streams for {output_format} format")
        
        # Process remaining settings using the base converter's rules
        self._process_source_data(source_data, "", self._create_rule_lookup(), target_data, processed_params)
        
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
    
    def determine_output_format(self, source_data: Dict) -> str:
        """
        Determine the output format from the source data.
        
        Args:
            source_data: Source data dictionary from encoding.com
            
        Returns:
            Output format string
        """
        output_format = source_data.get('output', source_data.get('o', ''))
        
        # Map encoding.com format names to our internal format names
        format_mapping = {
            'mp4': 'mp4',
            'advanced_hls': 'advanced_hls',
            'advanced_dash': 'advanced_dash',
            'fmp4_hls': 'fmp4_hls',
            'cmaf': 'cmaf',
            'smooth': 'smooth_streaming'
        }
        
        return format_mapping.get(output_format, output_format)
    
    def process_basic_settings(self, source_data: Dict, target_data: Dict, processed_params: set) -> None:
        """
        Process basic settings (non-stream related).
        
        Args:
            source_data: Source data dictionary from encoding.com
            target_data: Target data dictionary for MediaConvert
            processed_params: Set of processed parameters to update
        """
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
    
    def _create_rule_lookup(self) -> Dict:
        """
        Create a rule lookup dictionary for faster access.
        
        Returns:
            Dictionary mapping source paths to rules
        """
        rule_lookup = {}
        
        # Organize rules by their source path for easier lookup
        for rule in self.rules:
            if rule['source'].get('type') == 'iteration' or rule['source'].get('type') == 'dummy':
                continue
                
            source_path = rule['source']['path']
            if source_path not in rule_lookup:
                rule_lookup[source_path] = []
            rule_lookup[source_path].append(rule)
        
        return rule_lookup
