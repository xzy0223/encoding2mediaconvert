#!/usr/bin/env python3
"""
Test script for multi-condition functionality in ConfigConverter
"""

import os
import json
import logging
from config_converter_enhanced import ConfigConverter

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_multi_condition():
    """Test the multi-condition functionality with different scenarios"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the test rules file
    rules_file = os.path.join(current_dir, 'rules', 'test_multi_condition.yaml')
    
    # Create converter instance
    converter = ConfigConverter(rules_file)
    
    # Test case 1: cbr=no and cabr=no
    logger.info("Test case 1: cbr=no and cabr=no")
    source_data = {
        "cbr": "no",
        "cabr": "no",
        "output": "mp4"
    }
    
    result1 = converter.convert_dict(source_data)
    logger.info(f"Result 1: {json.dumps(result1, indent=2)}")
    
    # Test case 2: cbr=yes
    logger.info("Test case 2: cbr=yes")
    source_data = {
        "cbr": "yes",
        "output": "mp4"
    }
    
    result2 = converter.convert_dict(source_data)
    logger.info(f"Result 2: {json.dumps(result2, indent=2)}")
    
    # Test case 3: cbr=no but cabr=yes
    logger.info("Test case 3: cbr=no but cabr=yes")
    source_data = {
        "cbr": "no",
        "cabr": "yes",
        "output": "mp4"
    }
    
    result3 = converter.convert_dict(source_data)
    logger.info(f"Result 3: {json.dumps(result3, indent=2)}")
    
    # Test case 4: output=hls (NOT mp4)
    logger.info("Test case 4: output=hls (NOT mp4)")
    source_data = {
        "cbr": "no",
        "output": "hls"
    }
    
    result4 = converter.convert_dict(source_data)
    logger.info(f"Result 4: {json.dumps(result4, indent=2)}")
    
    return {
        "case1": result1,
        "case2": result2,
        "case3": result3,
        "case4": result4
    }

if __name__ == "__main__":
    # Add convert_dict method to ConfigConverter for testing
    def convert_dict(self, source_data):
        """Convert a dictionary directly without reading from file"""
        target_data = {"Settings": {"OutputGroups": [{"Outputs": [{"VideoDescription": {"CodecSettings": {"H264Settings": {}}}}], "OutputGroupSettings": {}}]}}
        processed_params = set()
        
        # Create a rule lookup dictionary for faster access
        rule_lookup = {}
        iteration_rules = []
        dummy_rules = []
        
        # Organize rules by their source path for easier lookup
        for rule in self.rules:
            if rule['source'].get('type') == 'iteration':
                iteration_rules.append(rule)
                continue
            elif rule['source'].get('type') == 'dummy':
                dummy_rules.append(rule)
                continue
                
            source_path = rule['source']['path']
            if source_path not in rule_lookup:
                rule_lookup[source_path] = []
            rule_lookup[source_path].append(rule)
        
        # Process rules
        for path, rules in rule_lookup.items():
            source_value = self.get_value_by_path(source_data, path)
            self.logger.debug(f"Processing rules for path: {path}, value: {source_value}")
            for rule in rules:
                # Check condition (if any)
                if 'condition' in rule['source']:
                    self.logger.debug(f"Evaluating condition for {path}")
                    if not self.evaluate_condition(rule['source']['condition'], source_value, source_data):
                        self.logger.debug(f"Skipping rule for {path} due to source condition")
                        continue
                    else:
                        self.logger.debug(f"Condition passed for {path}")
                
                # Process target mapping
                targets = rule['target'] if isinstance(rule['target'], list) else [rule['target']]
                for target in targets:
                    target_path = target['path']
                    target_value = target.get('value', source_value)
                    self.logger.debug(f"Setting {target_path} = {target_value}")
                    self._set_nested_value(target_data, target_path, target_value)
        
        return target_data
    
    # Add the method to the class
    ConfigConverter.convert_dict = convert_dict
    
    # Run the test
    results = test_multi_condition()
    
    # Print summary
    print("\nTest Summary:")
    print("=============")
    
    # Case 1: cbr=no and cabr=no should use QVBR
    rate_control_1 = results["case1"].get("Settings", {}).get("OutputGroups", [{}])[0].get("Outputs", [{}])[0].get(
        "VideoDescription", {}).get("CodecSettings", {}).get("H264Settings", {}).get("RateControlMode")
    print(f"Case 1 (cbr=no, cabr=no): RateControlMode = {rate_control_1}")
    
    # Case 2: cbr=yes should use CBR
    rate_control_2 = results["case2"].get("Settings", {}).get("OutputGroups", [{}])[0].get("Outputs", [{}])[0].get(
        "VideoDescription", {}).get("CodecSettings", {}).get("H264Settings", {}).get("RateControlMode")
    print(f"Case 2 (cbr=yes): RateControlMode = {rate_control_2}")
    
    # Case 3: cbr=no but cabr=yes should not match the first rule
    rate_control_3 = results["case3"].get("Settings", {}).get("OutputGroups", [{}])[0].get("Outputs", [{}])[0].get(
        "VideoDescription", {}).get("CodecSettings", {}).get("H264Settings", {}).get("RateControlMode")
    print(f"Case 3 (cbr=no, cabr=yes): RateControlMode = {rate_control_3}")
    
    # Case 4: output=hls should use HLS_GROUP_SETTINGS
    output_group_type = results["case4"].get("Settings", {}).get("OutputGroups", [{}])[0].get("OutputGroupSettings", {}).get("Type")
    print(f"Case 4 (output=hls): OutputGroupSettings.Type = {output_group_type}")
