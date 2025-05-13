#!/usr/bin/env python3
"""
Test script for the MediaConvert Configuration Validator
"""

import os
import unittest
from validator import MediaConvertConfigValidator


class TestMediaConvertConfigValidator(unittest.TestCase):
    """Test cases for the MediaConvert Configuration Validator"""

    def setUp(self):
        """Set up test environment"""
        self.schema_path = os.path.join(os.path.dirname(__file__), 'mc_setting_schema.json')
        self.example_config_path = '/home/ec2-user/e2mc_assistant/tranformed_mc_profiles/examples/1-setting.json'
        self.validator = MediaConvertConfigValidator(self.schema_path)

    def test_schema_loading(self):
        """Test that the schema loads correctly"""
        self.assertIsNotNone(self.validator.schema)
        self.assertIsInstance(self.validator.schema, dict)

    def test_valid_config(self):
        """Test validation with a valid configuration"""
        result = self.validator.validate_config(self.example_config_path)
        self.assertTrue(result)

    def test_nonexistent_config(self):
        """Test validation with a nonexistent configuration file"""
        result = self.validator.validate_config('/path/to/nonexistent/config.json')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
