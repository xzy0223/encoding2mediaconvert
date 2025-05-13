#!/usr/bin/env python3
"""
Setup script for the analyzer package.
"""

from setuptools import setup, find_packages

setup(
    name="analyzer",
    version="0.1.0",
    description="Video analyzer for extracting video information, comparing videos, and analyzing differences",
    author="AWS",
    packages=find_packages(),
    install_requires=[
        "ffmpeg-python",
        "boto3",
    ],
    entry_points={
        "console_scripts": [
            "video-analyzer=analyzer.cli:main",
        ],
    },
    python_requires=">=3.6",
)
