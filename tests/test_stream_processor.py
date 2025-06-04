#!/usr/bin/env python3
"""
Unit tests for the StreamProcessor class.
"""

import unittest
from src.e2mc_assistant.converter.stream_processor import StreamProcessor

class TestStreamProcessor(unittest.TestCase):
    """Test cases for the StreamProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fmp4_processor = StreamProcessor("fmp4_hls")
        self.mp4_processor = StreamProcessor("mp4")
    
    def test_classify_streams(self):
        """Test stream classification."""
        streams = [
            {"audio_only": "yes", "audio_bitrate": "96k"},
            {"video_only": "yes", "bitrate": "1000k", "size": "1280x720"},
            {"bitrate": "2000k", "size": "1920x1080", "audio_bitrate": "128k"}
        ]
        
        classified = self.fmp4_processor.classify_streams(streams)
        
        self.assertEqual(len(classified['audio']), 1)
        self.assertEqual(len(classified['video']), 1)
        self.assertEqual(len(classified['mixed']), 1)
        
        self.assertEqual(classified['audio'][0]['audio_bitrate'], "96k")
        self.assertEqual(classified['video'][0]['size'], "1280x720")
        self.assertEqual(classified['mixed'][0]['bitrate'], "2000k")
    
    def test_generate_name_modifier(self):
        """Test name modifier generation."""
        audio_stream = {"audio_bitrate": "96k", "audio_channels_number": "2"}
        video_stream = {"bitrate": "1000k", "size": "1280x720", "framerate": "30"}
        
        audio_name = self.fmp4_processor.generate_name_modifier(audio_stream, 'audio')
        video_name = self.fmp4_processor.generate_name_modifier(video_stream, 'video')
        
        self.assertIn("audio", audio_name)
        self.assertIn("96k", audio_name)
        self.assertIn("2ch", audio_name)
        
        self.assertIn("1280_720", video_name)
        self.assertIn("1000k", video_name)
    
    def test_process_fmp4_hls(self):
        """Test processing for fmp4_hls format."""
        streams = [
            {"audio_only": "yes", "audio_bitrate": "96k", "audio_sample_rate": "48000"},
            {"video_only": "yes", "bitrate": "1000k", "size": "1280x720", "framerate": "30"}
        ]
        
        context = {"source_data": {"segment_duration": 2}}
        outputs = self.fmp4_processor.process_fmp4_hls(streams, context)
        
        self.assertEqual(len(outputs), 2)
        
        # Check audio output
        audio_output = outputs[0]
        self.assertEqual(audio_output["ContainerSettings"]["Container"], "CMFC")
        self.assertIn("AudioDescriptions", audio_output)
        self.assertNotIn("VideoDescription", audio_output)
        
        # Check video output
        video_output = outputs[1]
        self.assertEqual(video_output["ContainerSettings"]["Container"], "CMFC")
        self.assertIn("VideoDescription", video_output)
        self.assertNotIn("AudioDescriptions", video_output)
        self.assertEqual(video_output["VideoDescription"]["Width"], 1280)
        self.assertEqual(video_output["VideoDescription"]["Height"], 720)
    
    def test_process_mp4(self):
        """Test processing for mp4 format."""
        streams = [
            {"audio_only": "yes", "audio_bitrate": "96k", "audio_sample_rate": "48000"},
            {"video_only": "yes", "bitrate": "1000k", "size": "1280x720", "framerate": "30"}
        ]
        
        context = {"source_data": {}}
        outputs = self.mp4_processor.process_mp4(streams, context)
        
        self.assertEqual(len(outputs), 2)
        
        # Check that both outputs have MP4 container
        for output in outputs:
            self.assertEqual(output["ContainerSettings"]["Container"], "MP4")
        
        # Check that we have one audio-only and one video-only output
        audio_outputs = [o for o in outputs if "AudioDescriptions" in o and "VideoDescription" not in o]
        video_outputs = [o for o in outputs if "VideoDescription" in o and "AudioDescriptions" not in o]
        
        self.assertEqual(len(audio_outputs), 1)
        self.assertEqual(len(video_outputs), 1)

if __name__ == '__main__':
    unittest.main()
