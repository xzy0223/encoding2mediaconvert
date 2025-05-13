"""
MediaConvert Configuration Validator Package

This package provides tools for validating AWS MediaConvert job configurations
against a JSON schema.
"""

from .validator import MediaConvertConfigValidator

__all__ = ['MediaConvertConfigValidator']
