#!/usr/bin/env python3
"""
Setup script for the Encoding.com to AWS MediaConvert Assistant
"""

from setuptools import setup, find_packages

setup(
    name="e2mc_assistant",
    version="1.0.0",
    description="Encoding.com to AWS MediaConvert Assistant",
    author="AWS",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "pyyaml>=5.1",
        # 其他依赖项
    ],
    entry_points={
        "console_scripts": [
            "e2mc-converter=e2mc_assistant.converter.config_converter_enhanced:main",
            # 其他命令行工具可以在这里添加
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
