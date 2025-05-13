#!/usr/bin/env python3
"""
Setup script for the Encoding.com to AWS MediaConvert Configuration Converter
"""

from setuptools import setup, find_packages

setup(
    name="e2mc_converter",
    version="1.0.0",
    description="Encoding.com to AWS MediaConvert Configuration Converter",
    author="AWS",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyyaml>=5.1",
    ],
    entry_points={
        "console_scripts": [
            "e2mc-converter=converter.config_converter_enhanced:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
