#!/usr/bin/env python3
"""
Stream processor module for handling different types of streams in encoding.com to MediaConvert conversion.
This module provides specialized processing for different output formats and stream types.
"""

import re
import logging
from typing import Dict, List, Any, Optional

class StreamProcessor:
    """
    Processes streams from encoding.com format to AWS MediaConvert format.
    Handles different output formats and stream types with specialized processing.
    """
    
    def __init__(self, output_format: str):
        """
        Initialize the stream processor for a specific output format.
        
        Args:
            output_format: The output format (e.g., "fmp4_hls", "advanced_hls", "cmaf")
        """
        self.output_format = output_format
        self.logger = logging.getLogger('StreamProcessor')
        
        # Map output formats to their processing methods
        self.format_processors = {
            "fmp4_hls": self.process_fmp4_hls,
            "advanced_hls": self.process_advanced_hls,
            "advanced_dash": self.process_advanced_dash,
            "cmaf": self.process_cmaf,
            "mp4": self.process_mp4,
            "smooth_streaming": self.process_smooth_streaming
        }
    
    def process_streams(self, streams: List[Dict], context: Dict) -> List[Dict]:
        """
        Process a list of streams based on the output format.
        
        Args:
            streams: List of stream dictionaries from encoding.com
            context: Additional context information including source_data
            
        Returns:
            List of MediaConvert output configurations
        """
        self.logger.info(f"Processing {len(streams)} streams for format: {self.output_format}")
        
        # Use the appropriate processor for the format
        if self.output_format in self.format_processors:
            return self.format_processors[self.output_format](streams, context)
        else:
            self.logger.warning(f"No specialized processor for {self.output_format}, using default")
            return self.process_default(streams, context)
    
    def classify_streams(self, streams: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Classify streams into audio, video, and mixed types.
        
        Args:
            streams: List of stream dictionaries from encoding.com
            
        Returns:
            Dictionary with keys 'audio', 'video', 'mixed' containing lists of streams
        """
        audio_streams = []
        video_streams = []
        mixed_streams = []
        
        for stream in streams:
            if stream.get('audio_only') == 'yes':
                audio_streams.append(stream)
            elif stream.get('video_only') == 'yes':
                video_streams.append(stream)
            else:
                mixed_streams.append(stream)
        
        self.logger.info(f"Classified streams: {len(audio_streams)} audio, {len(video_streams)} video, {len(mixed_streams)} mixed")
        return {
            'audio': audio_streams,
            'video': video_streams,
            'mixed': mixed_streams
        }
    
    def create_stream_relationships(self, classified_streams: Dict[str, List[Dict]], output_format: str) -> List[Dict]:
        """
        Create relationships between streams based on output format requirements.
        
        Args:
            classified_streams: Dictionary with classified streams
            output_format: The output format
            
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        
        # For formats that need audio-video pairing
        if output_format in ["mp4", "mov"]:
            # For each video stream, find the best matching audio stream
            for video_stream in classified_streams['video']:
                best_audio = self._find_best_matching_audio(video_stream, classified_streams['audio'])
                if best_audio:
                    relationships.append({
                        'video': video_stream,
                        'audio': best_audio,
                        'type': 'paired'
                    })
                else:
                    # If no audio stream is available, just use the video stream alone
                    relationships.append({
                        'video': video_stream,
                        'type': 'video_only'
                    })
            
            # Add any remaining audio streams as audio-only
            for audio_stream in classified_streams['audio']:
                if not any(rel.get('audio') == audio_stream for rel in relationships if 'audio' in rel):
                    relationships.append({
                        'audio': audio_stream,
                        'type': 'audio_only'
                    })
                    
            # Add any mixed streams
            for mixed_stream in classified_streams['mixed']:
                relationships.append({
                    'mixed': mixed_stream,
                    'type': 'mixed'
                })
        else:
            # For streaming formats like HLS/DASH, each stream is processed independently
            for stream_type, streams in classified_streams.items():
                for stream in streams:
                    relationships.append({
                        'stream': stream,
                        'type': stream_type
                    })
        
        self.logger.info(f"Created {len(relationships)} stream relationships")
        return relationships
    
    def _find_best_matching_audio(self, video_stream: Dict, audio_streams: List[Dict]) -> Optional[Dict]:
        """
        Find the best matching audio stream for a video stream.
        
        Args:
            video_stream: Video stream dictionary
            audio_streams: List of audio stream dictionaries
            
        Returns:
            Best matching audio stream or None if no audio streams available
        """
        if not audio_streams:
            return None
            
        # For now, just return the first audio stream
        # In a more sophisticated implementation, we could match based on language, bitrate, etc.
        return audio_streams[0]
    
    def generate_name_modifier(self, stream: Dict, stream_type: str) -> str:
        """
        Generate a name modifier for an output based on stream properties.
        
        Args:
            stream: Stream dictionary
            stream_type: Type of stream ('audio', 'video', 'mixed')
            
        Returns:
            Name modifier string
        """
        name_parts = []
        
        if stream_type == 'audio':
            name_parts.append("audio")
            
            # Add audio bitrate if available
            if 'audio_bitrate' in stream:
                bitrate_match = re.match(r'(\d+)k', stream['audio_bitrate'])
                if bitrate_match:
                    name_parts.append(f"{bitrate_match.group(1)}k")
                    
            # Add audio channels if available
            if 'audio_channels_number' in stream:
                name_parts.append(f"{stream['audio_channels_number']}ch")
                
        elif stream_type == 'video' or stream_type == 'mixed':
            # Add resolution if available
            if 'size' in stream:
                name_parts.append(stream['size'].replace('x', '_'))
                
            # Add bitrate if available
            if 'bitrate' in stream:
                bitrate_match = re.match(r'(\d+)k', stream['bitrate'])
                if bitrate_match:
                    name_parts.append(f"{bitrate_match.group(1)}k")
        
        # Join all parts with underscores
        return "_".join(name_parts) if name_parts else "output"
    
    def process_default(self, streams: List[Dict], context: Dict) -> List[Dict]:
        """
        Default stream processor when no specialized processor is available.
        
        Args:
            streams: List of stream dictionaries
            context: Additional context information
            
        Returns:
            List of MediaConvert output configurations
        """
        outputs = []
        
        # Classify streams
        classified_streams = self.classify_streams(streams)
        
        # Create stream relationships
        relationships = self.create_stream_relationships(classified_streams, self.output_format)
        
        # Process each relationship
        for relationship in relationships:
            output = self.process_relationship(relationship, context)
            if output:
                outputs.append(output)
        
        return outputs
    
    def process_relationship(self, relationship: Dict, context: Dict) -> Dict:
        """
        Process a stream relationship into a MediaConvert output.
        
        Args:
            relationship: Stream relationship dictionary
            context: Additional context information
            
        Returns:
            MediaConvert output configuration
        """
        rel_type = relationship.get('type')
        output = {"ContainerSettings": {}}
        
        if rel_type == 'audio_only':
            # Process audio-only output
            audio_stream = relationship.get('audio')
            if audio_stream:
                output["AudioDescriptions"] = [self._create_audio_description(audio_stream)]
                output["NameModifier"] = self.generate_name_modifier(audio_stream, 'audio')
                
        elif rel_type == 'video_only':
            # Process video-only output
            video_stream = relationship.get('video')
            if video_stream:
                output["VideoDescription"] = self._create_video_description(video_stream)
                output["NameModifier"] = self.generate_name_modifier(video_stream, 'video')
                
        elif rel_type == 'paired':
            # Process paired audio-video output
            video_stream = relationship.get('video')
            audio_stream = relationship.get('audio')
            
            if video_stream:
                output["VideoDescription"] = self._create_video_description(video_stream)
                
            if audio_stream:
                output["AudioDescriptions"] = [self._create_audio_description(audio_stream)]
                
            # Use video stream for name modifier if available
            if video_stream:
                output["NameModifier"] = self.generate_name_modifier(video_stream, 'video')
            elif audio_stream:
                output["NameModifier"] = self.generate_name_modifier(audio_stream, 'audio')
                
        elif rel_type == 'mixed':
            # Process mixed audio-video stream
            mixed_stream = relationship.get('mixed')
            if mixed_stream:
                output["VideoDescription"] = self._create_video_description(mixed_stream)
                output["AudioDescriptions"] = [self._create_audio_description(mixed_stream)]
                output["NameModifier"] = self.generate_name_modifier(mixed_stream, 'mixed')
                
        elif rel_type in ['audio', 'video']:
            # Process individual stream from streaming formats
            stream = relationship.get('stream')
            if stream:
                if rel_type == 'audio':
                    output["AudioDescriptions"] = [self._create_audio_description(stream)]
                elif rel_type == 'video':
                    output["VideoDescription"] = self._create_video_description(stream)
                    
                output["NameModifier"] = self.generate_name_modifier(stream, rel_type)
        
        return output
    
    def _create_video_description(self, stream: Dict) -> Dict:
        """
        Create a video description from a stream.
        
        Args:
            stream: Stream dictionary
            
        Returns:
            MediaConvert VideoDescription configuration
        """
        video_desc = {
            "CodecSettings": {
                "Codec": "H_264",
                "H264Settings": {
                    "FramerateDenominator": 1,
                    "FramerateControl": "SPECIFIED",
                    "RateControlMode": "VBR"
                }
            }
        }
        
        # Set size if available
        if 'size' in stream:
            size_match = re.match(r'(\d+)x(\d+)', stream['size'])
            if size_match:
                width, height = size_match.groups()
                video_desc["Width"] = int(width)
                video_desc["Height"] = int(height)
        
        # Set bitrate if available
        if 'bitrate' in stream:
            bitrate_match = re.match(r'(\d+)k', stream['bitrate'])
            if bitrate_match:
                bitrate = int(bitrate_match.group(1)) * 1000
                video_desc["CodecSettings"]["H264Settings"]["Bitrate"] = bitrate
        
        # Set framerate if available
        if 'framerate' in stream:
            video_desc["CodecSettings"]["H264Settings"]["FramerateNumerator"] = int(stream['framerate'])
        
        # Set codec profile if available
        if 'profile' in stream:
            profile_map = {
                'baseline': 'BASELINE',
                'main': 'MAIN',
                'high': 'HIGH'
            }
            profile = stream['profile'].lower()
            if profile in profile_map:
                video_desc["CodecSettings"]["H264Settings"]["CodecProfile"] = profile_map[profile]
        
        # Add deinterlacer if needed
        if stream.get('deinterlacing') == 'yes' or stream.get('deinterlacing') == 'auto':
            video_desc["VideoPreprocessors"] = {
                "Deinterlacer": {
                    "Algorithm": "INTERPOLATE",
                    "Mode": "DEINTERLACE"
                }
            }
        
        return video_desc
    
    def _create_audio_description(self, stream: Dict) -> Dict:
        """
        Create an audio description from a stream.
        
        Args:
            stream: Stream dictionary
            
        Returns:
            MediaConvert AudioDescription configuration
        """
        audio_desc = {
            "CodecSettings": {
                "Codec": "AAC",
                "AacSettings": {
                    "AudioDescriptionBroadcasterMix": "NORMAL",
                    "CodingMode": "CODING_MODE_2_0"
                }
            }
        }
        
        # Set audio bitrate if available
        if 'audio_bitrate' in stream:
            bitrate_match = re.match(r'(\d+)k', stream['audio_bitrate'])
            if bitrate_match:
                audio_bitrate = int(bitrate_match.group(1)) * 1000
                audio_desc["CodecSettings"]["AacSettings"]["Bitrate"] = audio_bitrate
        
        # Set audio sample rate if available
        if 'audio_sample_rate' in stream:
            audio_desc["CodecSettings"]["AacSettings"]["SampleRate"] = int(stream['audio_sample_rate'])
        
        # Set audio channels if available
        if 'audio_channels_number' in stream:
            channels = int(stream['audio_channels_number'])
            if channels == 1:
                audio_desc["CodecSettings"]["AacSettings"]["CodingMode"] = "CODING_MODE_1_0"
            elif channels == 2:
                audio_desc["CodecSettings"]["AacSettings"]["CodingMode"] = "CODING_MODE_2_0"
            elif channels == 6:
                audio_desc["CodecSettings"]["AacSettings"]["CodingMode"] = "CODING_MODE_5_1"
        
        return audio_desc
    
    # Format-specific processors
    
    def process_fmp4_hls(self, streams: List[Dict], context: Dict) -> List[Dict]:
        """
        Process streams for fmp4_hls format.
        
        Args:
            streams: List of stream dictionaries
            context: Additional context information
            
        Returns:
            List of MediaConvert output configurations
        """
        outputs = []
        
        # Classify streams
        classified_streams = self.classify_streams(streams)
        
        # Process audio streams
        for audio_stream in classified_streams['audio']:
            output = {
                "ContainerSettings": {
                    "Container": "CMFC"
                },
                "AudioDescriptions": [self._create_audio_description(audio_stream)],
                "NameModifier": self.generate_name_modifier(audio_stream, 'audio'),
                "Extension": "m4s"
            }
            outputs.append(output)
        
        # Process video streams
        for video_stream in classified_streams['video']:
            output = {
                "ContainerSettings": {
                    "Container": "CMFC"
                },
                "VideoDescription": self._create_video_description(video_stream),
                "NameModifier": self.generate_name_modifier(video_stream, 'video'),
                "Extension": "m4s"
            }
            outputs.append(output)
        
        # Process mixed streams
        for mixed_stream in classified_streams['mixed']:
            output = {
                "ContainerSettings": {
                    "Container": "CMFC"
                },
                "VideoDescription": self._create_video_description(mixed_stream),
                "AudioDescriptions": [self._create_audio_description(mixed_stream)],
                "NameModifier": self.generate_name_modifier(mixed_stream, 'mixed'),
                "Extension": "m4s"
            }
            outputs.append(output)
        
        return outputs
    
    def process_advanced_hls(self, streams: List[Dict], context: Dict) -> List[Dict]:
        """
        Process streams for advanced_hls format.
        
        Args:
            streams: List of stream dictionaries
            context: Additional context information
            
        Returns:
            List of MediaConvert output configurations
        """
        outputs = []
        
        # Classify streams
        classified_streams = self.classify_streams(streams)
        
        # Process audio streams
        for audio_stream in classified_streams['audio']:
            output = {
                "ContainerSettings": {
                    "Container": "M3U8",
                    "M3u8Settings": {}
                },
                "AudioDescriptions": [self._create_audio_description(audio_stream)],
                "NameModifier": self.generate_name_modifier(audio_stream, 'audio'),
                "OutputSettings": {
                    "HlsSettings": {
                        "AudioGroupId": "audio",
                        "AudioRenditionSets": "audio"
                    }
                }
            }
            outputs.append(output)
        
        # Process video streams
        for video_stream in classified_streams['video']:
            output = {
                "ContainerSettings": {
                    "Container": "M3U8",
                    "M3u8Settings": {}
                },
                "VideoDescription": self._create_video_description(video_stream),
                "NameModifier": self.generate_name_modifier(video_stream, 'video'),
                "OutputSettings": {
                    "HlsSettings": {
                        "AudioGroupId": "audio"
                    }
                }
            }
            outputs.append(output)
        
        # Process mixed streams
        for mixed_stream in classified_streams['mixed']:
            output = {
                "ContainerSettings": {
                    "Container": "M3U8",
                    "M3u8Settings": {}
                },
                "VideoDescription": self._create_video_description(mixed_stream),
                "AudioDescriptions": [self._create_audio_description(mixed_stream)],
                "NameModifier": self.generate_name_modifier(mixed_stream, 'mixed')
            }
            outputs.append(output)
        
        return outputs
    
    def process_advanced_dash(self, streams: List[Dict], context: Dict) -> List[Dict]:
        """
        Process streams for advanced_dash format.
        
        Args:
            streams: List of stream dictionaries
            context: Additional context information
            
        Returns:
            List of MediaConvert output configurations
        """
        outputs = []
        
        # Classify streams
        classified_streams = self.classify_streams(streams)
        
        # Process audio streams
        for audio_stream in classified_streams['audio']:
            output = {
                "ContainerSettings": {
                    "Container": "MPD",
                    "MpdSettings": {}
                },
                "AudioDescriptions": [self._create_audio_description(audio_stream)],
                "NameModifier": self.generate_name_modifier(audio_stream, 'audio')
            }
            outputs.append(output)
        
        # Process video streams
        for video_stream in classified_streams['video']:
            output = {
                "ContainerSettings": {
                    "Container": "MPD",
                    "MpdSettings": {}
                },
                "VideoDescription": self._create_video_description(video_stream),
                "NameModifier": self.generate_name_modifier(video_stream, 'video')
            }
            outputs.append(output)
        
        # Process mixed streams
        for mixed_stream in classified_streams['mixed']:
            output = {
                "ContainerSettings": {
                    "Container": "MPD",
                    "MpdSettings": {}
                },
                "VideoDescription": self._create_video_description(mixed_stream),
                "AudioDescriptions": [self._create_audio_description(mixed_stream)],
                "NameModifier": self.generate_name_modifier(mixed_stream, 'mixed')
            }
            outputs.append(output)
        
        return outputs
    
    def process_cmaf(self, streams: List[Dict], context: Dict) -> List[Dict]:
        """
        Process streams for cmaf format.
        
        Args:
            streams: List of stream dictionaries
            context: Additional context information
            
        Returns:
            List of MediaConvert output configurations
        """
        # CMAF is similar to fmp4_hls but with different container settings
        outputs = self.process_fmp4_hls(streams, context)
        
        # Update container settings for CMAF
        for output in outputs:
            output["ContainerSettings"]["Container"] = "CMFC"
        
        return outputs
    
    def process_mp4(self, streams: List[Dict], context: Dict) -> List[Dict]:
        """
        Process streams for mp4 format.
        
        Args:
            streams: List of stream dictionaries
            context: Additional context information
            
        Returns:
            List of MediaConvert output configurations
        """
        outputs = []
        
        # Classify streams
        classified_streams = self.classify_streams(streams)
        
        # Create stream relationships
        relationships = self.create_stream_relationships(classified_streams, "mp4")
        
        # Process each relationship
        for relationship in relationships:
            output = {
                "ContainerSettings": {
                    "Container": "MP4",
                    "Mp4Settings": {}
                }
            }
            
            rel_type = relationship.get('type')
            
            if rel_type == 'paired':
                # Process paired audio-video output
                video_stream = relationship.get('video')
                audio_stream = relationship.get('audio')
                
                if video_stream:
                    output["VideoDescription"] = self._create_video_description(video_stream)
                    
                if audio_stream:
                    output["AudioDescriptions"] = [self._create_audio_description(audio_stream)]
                    
                # Use video stream for name modifier
                if video_stream:
                    output["NameModifier"] = self.generate_name_modifier(video_stream, 'video')
                    
            elif rel_type == 'video_only':
                # Process video-only output
                video_stream = relationship.get('video')
                if video_stream:
                    output["VideoDescription"] = self._create_video_description(video_stream)
                    output["NameModifier"] = self.generate_name_modifier(video_stream, 'video')
                    
            elif rel_type == 'audio_only':
                # Process audio-only output
                audio_stream = relationship.get('audio')
                if audio_stream:
                    output["AudioDescriptions"] = [self._create_audio_description(audio_stream)]
                    output["NameModifier"] = self.generate_name_modifier(audio_stream, 'audio')
                    
            elif rel_type == 'mixed':
                # Process mixed audio-video stream
                mixed_stream = relationship.get('mixed')
                if mixed_stream:
                    output["VideoDescription"] = self._create_video_description(mixed_stream)
                    output["AudioDescriptions"] = [self._create_audio_description(mixed_stream)]
                    output["NameModifier"] = self.generate_name_modifier(mixed_stream, 'mixed')
            
            outputs.append(output)
        
        return outputs
    
    def process_smooth_streaming(self, streams: List[Dict], context: Dict) -> List[Dict]:
        """
        Process streams for smooth_streaming format.
        
        Args:
            streams: List of stream dictionaries
            context: Additional context information
            
        Returns:
            List of MediaConvert output configurations
        """
        outputs = []
        
        # Classify streams
        classified_streams = self.classify_streams(streams)
        
        # Process audio streams
        for audio_stream in classified_streams['audio']:
            output = {
                "ContainerSettings": {
                    "Container": "ISM",
                    "IsmSettings": {}
                },
                "AudioDescriptions": [self._create_audio_description(audio_stream)],
                "NameModifier": self.generate_name_modifier(audio_stream, 'audio')
            }
            outputs.append(output)
        
        # Process video streams
        for video_stream in classified_streams['video']:
            output = {
                "ContainerSettings": {
                    "Container": "ISM",
                    "IsmSettings": {}
                },
                "VideoDescription": self._create_video_description(video_stream),
                "NameModifier": self.generate_name_modifier(video_stream, 'video')
            }
            outputs.append(output)
        
        # Process mixed streams
        for mixed_stream in classified_streams['mixed']:
            output = {
                "ContainerSettings": {
                    "Container": "ISM",
                    "IsmSettings": {}
                },
                "VideoDescription": self._create_video_description(mixed_stream),
                "AudioDescriptions": [self._create_audio_description(mixed_stream)],
                "NameModifier": self.generate_name_modifier(mixed_stream, 'mixed')
            }
            outputs.append(output)
        
        return outputs
