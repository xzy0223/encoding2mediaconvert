"""
Encoding.com to AWS MediaConvert Assistant

This package provides comprehensive tools for migrating video transcoding workflows
from Encoding.com to AWS MediaConvert, including:

- Configuration conversion from XML to JSON
- Video analysis and comparison using AWS Bedrock
- MediaConvert job submission and management
- Complete workflow automation
- Configuration validation and error analysis

Main Components:
    - ConfigConverter: XML to JSON configuration conversion
    - VideoAnalyzer: Video analysis and comparison
    - MediaConvertJobSubmitter: Job submission and management
    - E2MCWorkflow: End-to-end workflow automation
"""

# Import version information
from .__version__ import __version__, __version_info__

# Import main classes for easy access
from .converter import ConfigConverter
from .analyzer import VideoAnalyzer
from .requester import MediaConvertJobSubmitter

# Define what gets imported with "from e2mc_assistant import *"
__all__ = [
    '__version__',
    '__version_info__',
    'ConfigConverter',
    'VideoAnalyzer', 
    'MediaConvertJobSubmitter',
]

# Package metadata
__author__ = "AWS Professional Services"
__email__ = "aws-professional-services@amazon.com"
__license__ = "MIT"
__description__ = "Encoding.com to AWS MediaConvert Assistant - Complete migration toolkit"
