"""
Encoding.com to AWS MediaConvert Configuration Converter

This module provides tools for converting Encoding.com XML configuration files
to AWS MediaConvert JSON configuration files.

Classes:
    ConfigConverter: Main converter class for transforming configurations
"""

from .config_converter_enhanced import ConfigConverter, main

__all__ = ['ConfigConverter', 'main']
