#!/usr/bin/env python3
"""
Output group generator module for creating appropriate output group settings
based on the output format in encoding.com to MediaConvert conversion.
"""

import logging
from typing import Dict, Any

class OutputGroupGenerator:
    """
    Generates output group settings for different output formats.
    """
    
    def __init__(self):
        """Initialize the output group generator."""
        self.logger = logging.getLogger('OutputGroupGenerator')
    
    def generate_output_group_settings(self, output_format: str, source_data: Dict) -> Dict:
        """
        Generate output group settings based on the output format.
        
        Args:
            output_format: The output format (e.g., "fmp4_hls", "advanced_hls", "cmaf")
            source_data: Source data dictionary from encoding.com
            
        Returns:
            MediaConvert OutputGroupSettings configuration
        """
        if output_format == "fmp4_hls":
            return self._generate_cmaf_group_settings(source_data)
        elif output_format == "advanced_hls":
            return self._generate_hls_group_settings(source_data)
        elif output_format == "advanced_dash":
            return self._generate_dash_group_settings(source_data)
        elif output_format == "cmaf":
            return self._generate_cmaf_group_settings(source_data)
        elif output_format == "mp4":
            return self._generate_file_group_settings(source_data)
        elif output_format == "smooth_streaming":
            return self._generate_ms_smooth_group_settings(source_data)
        else:
            self.logger.warning(f"No specialized output group settings for {output_format}, using FILE_GROUP_SETTINGS")
            return self._generate_file_group_settings(source_data)
    
    def _generate_cmaf_group_settings(self, source_data: Dict) -> Dict:
        """
        Generate CMAF group settings.
        
        Args:
            source_data: Source data dictionary from encoding.com
            
        Returns:
            CMAF_GROUP_SETTINGS configuration
        """
        settings = {
            "Type": "CMAF_GROUP_SETTINGS",
            "CmafGroupSettings": {
                "WriteDashManifest": "DISABLED",
                "SegmentLength": self._get_segment_duration(source_data),
                "Destination": "S3_OUTPUT_URL",
                "FragmentLength": self._get_fragment_length(source_data),
                "SegmentControl": "SEGMENTED_FILES",
                "ManifestDurationFormat": "FLOATING_POINT"
            }
        }
        
        # Check if we should write HLS manifest
        if source_data.get('output') == "fmp4_hls":
            settings["CmafGroupSettings"]["WriteHlsManifest"] = "ENABLED"
        else:
            settings["CmafGroupSettings"]["WriteHlsManifest"] = "DISABLED"
        
        return settings
    
    def _generate_hls_group_settings(self, source_data: Dict) -> Dict:
        """
        Generate HLS group settings.
        
        Args:
            source_data: Source data dictionary from encoding.com
            
        Returns:
            HLS_GROUP_SETTINGS configuration
        """
        settings = {
            "Type": "HLS_GROUP_SETTINGS",
            "HlsGroupSettings": {
                "SegmentLength": self._get_segment_duration(source_data),
                "Destination": "S3_OUTPUT_URL",
                "MinSegmentLength": 0,
                "SegmentControl": "SEGMENTED_FILES",
                "ManifestDurationFormat": "FLOATING_POINT"
            }
        }
        
        # Set playlist type
        playlist_type = source_data.get('playlist_type', 'vod')
        if playlist_type.lower() == 'live':
            settings["HlsGroupSettings"]["ProgramDateTime"] = "INCLUDE"
            settings["HlsGroupSettings"]["ProgramDateTimePeriod"] = 600
        else:
            settings["HlsGroupSettings"]["PlaylistType"] = "VOD"
        
        return settings
    
    def _generate_dash_group_settings(self, source_data: Dict) -> Dict:
        """
        Generate DASH group settings.
        
        Args:
            source_data: Source data dictionary from encoding.com
            
        Returns:
            DASH_ISO_GROUP_SETTINGS configuration
        """
        settings = {
            "Type": "DASH_ISO_GROUP_SETTINGS",
            "DashIsoGroupSettings": {
                "SegmentLength": self._get_segment_duration(source_data),
                "Destination": "S3_OUTPUT_URL",
                "FragmentLength": self._get_fragment_length(source_data),
                "SegmentControl": "SEGMENTED_FILES"
            }
        }
        
        # Set MPD profile
        settings["DashIsoGroupSettings"]["MpdProfile"] = "MAIN_PROFILE"
        
        return settings
    
    def _generate_file_group_settings(self, source_data: Dict) -> Dict:
        """
        Generate file group settings.
        
        Args:
            source_data: Source data dictionary from encoding.com
            
        Returns:
            FILE_GROUP_SETTINGS configuration
        """
        settings = {
            "Type": "FILE_GROUP_SETTINGS",
            "FileGroupSettings": {
                "Destination": "S3_OUTPUT_URL"
            }
        }
        return settings
    
    def _generate_ms_smooth_group_settings(self, source_data: Dict) -> Dict:
        """
        Generate MS Smooth group settings.
        
        Args:
            source_data: Source data dictionary from encoding.com
            
        Returns:
            MS_SMOOTH_GROUP_SETTINGS configuration
        """
        settings = {
            "Type": "MS_SMOOTH_GROUP_SETTINGS",
            "MsSmoothGroupSettings": {
                "FragmentLength": self._get_fragment_length(source_data),
                "Destination": "S3_OUTPUT_URL"
            }
        }
        return settings
    
    def _get_segment_duration(self, source_data: Dict) -> int:
        """
        Get segment duration from source data.
        
        Args:
            source_data: Source data dictionary from encoding.com
            
        Returns:
            Segment duration in seconds
        """
        segment_duration = source_data.get('segment_duration')
        if segment_duration is not None:
            try:
                return int(segment_duration)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid segment_duration: {segment_duration}, using default")
        
        return 2  # Default segment duration
    
    def _get_fragment_length(self, source_data: Dict) -> int:
        """
        Get fragment length from source data.
        
        Args:
            source_data: Source data dictionary from encoding.com
            
        Returns:
            Fragment length in seconds
        """
        fragment_duration = source_data.get('fragment_duration')
        if fragment_duration is not None:
            try:
                return int(fragment_duration)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid fragment_duration: {fragment_duration}, using segment_duration")
                return self._get_segment_duration(source_data)
        
        return self._get_segment_duration(source_data)  # Default to segment duration
