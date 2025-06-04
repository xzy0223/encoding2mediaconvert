#!/usr/bin/env python3
"""
Unit tests for the OutputGroupGenerator class.
"""

import unittest
from src.e2mc_assistant.converter.output_group_generator import OutputGroupGenerator

class TestOutputGroupGenerator(unittest.TestCase):
    """Test cases for the OutputGroupGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = OutputGroupGenerator()
    
    def test_generate_cmaf_group_settings(self):
        """Test CMAF group settings generation."""
        source_data = {
            "segment_duration": 4,
            "fragment_duration": 2,
            "output": "fmp4_hls"
        }
        
        settings = self.generator.generate_output_group_settings("fmp4_hls", source_data)
        
        self.assertEqual(settings["Type"], "CMAF_GROUP_SETTINGS")
        self.assertEqual(settings["CmafGroupSettings"]["SegmentLength"], 4)
        self.assertEqual(settings["CmafGroupSettings"]["FragmentLength"], 2)
        self.assertEqual(settings["CmafGroupSettings"]["WriteHlsManifest"], "ENABLED")
    
    def test_generate_hls_group_settings(self):
        """Test HLS group settings generation."""
        source_data = {
            "segment_duration": 6,
            "playlist_type": "vod"
        }
        
        settings = self.generator.generate_output_group_settings("advanced_hls", source_data)
        
        self.assertEqual(settings["Type"], "HLS_GROUP_SETTINGS")
        self.assertEqual(settings["HlsGroupSettings"]["SegmentLength"], 6)
        self.assertEqual(settings["HlsGroupSettings"]["PlaylistType"], "VOD")
    
    def test_generate_dash_group_settings(self):
        """Test DASH group settings generation."""
        source_data = {
            "segment_duration": 2
        }
        
        settings = self.generator.generate_output_group_settings("advanced_dash", source_data)
        
        self.assertEqual(settings["Type"], "DASH_ISO_GROUP_SETTINGS")
        self.assertEqual(settings["DashIsoGroupSettings"]["SegmentLength"], 2)
        self.assertEqual(settings["DashIsoGroupSettings"]["MpdProfile"], "MAIN_PROFILE")
    
    def test_generate_file_group_settings(self):
        """Test file group settings generation."""
        source_data = {}
        
        settings = self.generator.generate_output_group_settings("mp4", source_data)
        
        self.assertEqual(settings["Type"], "FILE_GROUP_SETTINGS")
        self.assertEqual(settings["FileGroupSettings"]["Destination"], "S3_OUTPUT_URL")
    
    def test_default_segment_duration(self):
        """Test default segment duration when not specified."""
        source_data = {}
        
        settings = self.generator.generate_output_group_settings("fmp4_hls", source_data)
        
        self.assertEqual(settings["CmafGroupSettings"]["SegmentLength"], 2)  # Default value
    
    def test_invalid_segment_duration(self):
        """Test handling of invalid segment duration."""
        source_data = {
            "segment_duration": "invalid"
        }
        
        settings = self.generator.generate_output_group_settings("fmp4_hls", source_data)
        
        self.assertEqual(settings["CmafGroupSettings"]["SegmentLength"], 2)  # Default value

if __name__ == '__main__':
    unittest.main()
