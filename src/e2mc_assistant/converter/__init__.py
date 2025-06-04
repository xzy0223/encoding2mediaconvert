"""
Encoding.com to AWS MediaConvert Configuration Converter

This module provides tools for converting Encoding.com XML configuration files
to AWS MediaConvert JSON configuration files.

Classes:
    ConfigConverter: Main converter class for transforming configurations
    EnhancedConfigConverter: Enhanced converter with improved multi-stream support
    StreamProcessor: Specialized processor for handling different stream types
    OutputGroupGenerator: Generator for output group settings
"""

from .config_converter_enhanced import ConfigConverter, main
from .enhanced_config_converter import EnhancedConfigConverter
from .stream_processor import StreamProcessor
from .output_group_generator import OutputGroupGenerator

__all__ = ['ConfigConverter', 'main', 'EnhancedConfigConverter', 'StreamProcessor', 'OutputGroupGenerator']
