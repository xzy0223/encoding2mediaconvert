#!/usr/bin/env python3
"""
Setup script for the Encoding.com to AWS MediaConvert Assistant

This package provides comprehensive tools for migrating video transcoding workflows
from Encoding.com to AWS MediaConvert, including configuration conversion, job
management, video analysis, and workflow automation.
"""

import os
from setuptools import setup, find_packages

# Read the README file for long description
def read_readme():
    """Read README.md file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read version from a version file or use default
def get_version():
    """Get version from version file or use default."""
    version_path = os.path.join(os.path.dirname(__file__), 'src', 'e2mc_assistant', '__version__.py')
    if os.path.exists(version_path):
        try:
            version_vars = {}
            with open(version_path, 'r', encoding='utf-8') as f:
                exec(f.read(), version_vars)
            return version_vars.get('__version__', '1.0.0')
        except Exception:
            pass
    return "1.0.0"

setup(
    name="e2mc_assistant",
    version=get_version(),
    description="Encoding.com to AWS MediaConvert Assistant - Complete migration toolkit",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="AWS Professional Services",
    author_email="aws-professional-services@amazon.com",
    url="https://github.com/xzy0223/encoding2mediaconvert",
    project_urls={
        "Bug Reports": "https://github.com/xzy0223/encoding2mediaconvert/issues",
        "Source": "https://github.com/xzy0223/encoding2mediaconvert",
        "Documentation": "https://github.com/xzy0223/encoding2mediaconvert/blob/main/README.md",
    },
    
    # Package configuration
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    
    # Dependencies
    install_requires=[
        # Core dependencies
        "pyyaml>=5.1",                    # YAML configuration parsing
        "boto3>=1.26.0",                  # AWS SDK for MediaConvert, S3, Bedrock
        "botocore>=1.29.0",               # AWS core library
        "jsonschema>=4.0.0",              # JSON schema validation
        
        # Standard library backports for older Python versions
        "pathlib2>=2.3.0; python_version<'3.4'",
        "typing>=3.7.0; python_version<'3.5'",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
            "pre-commit>=2.15.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.15.0",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "moto>=4.0.0",  # AWS service mocking for tests
        ],
    },
    
    # Command line tools
    entry_points={
        "console_scripts": [
            # Main conversion tool
            "e2mc-converter=e2mc_assistant.converter.config_converter_enhanced:main",
            
            # Video analysis tool
            "e2mc-analyzer=e2mc_assistant.analyzer.video_analyzer:main",
            
            # MediaConvert job submission tool
            "e2mc-submitter=e2mc_assistant.requester.mediaconvert_job_submitter:main",
            
            # Complete workflow automation
            "e2mc-workflow=e2mc_assistant.workflow.e2mc_workflow:main",
        ],
    },
    
    # Python version requirements
    python_requires=">=3.6",
    
    # Package metadata
    keywords=[
        "aws", "mediaconvert", "encoding", "video", "transcoding", 
        "conversion", "migration", "media", "streaming", "hls", "dash"
    ],
    
    classifiers=[
        # Development status
        "Development Status :: 4 - Beta",
        
        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # Operating system
        "Operating System :: OS Independent",
        
        # Topic
        "Topic :: Multimedia :: Video :: Conversion",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        
        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
)
