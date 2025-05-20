#!/usr/bin/env python3
"""
Script to analyze .err log files in the specified directory,
extract error messages after "Error message:", and remove duplicates.
"""

import os
import re
from collections import Counter

def extract_error_messages(directory):
    """
    Extract error messages from .err files in the specified directory.
    
    Args:
        directory: Path to the directory containing .err files
        
    Returns:
        List of unique error messages with their occurrence count
    """
    error_messages = []
    error_pattern = re.compile(r'Error message:\s*(.*?)(?:\n|$)')
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return []
    
    # Find all .err files in the directory
    err_files = [f for f in os.listdir(directory) if f.endswith('.err')]
    
    if not err_files:
        print(f"No .err files found in {directory}")
        return []
    
    print(f"Found {len(err_files)} .err files in {directory}")
    
    # Process each .err file
    for err_file in err_files:
        file_path = os.path.join(directory, err_file)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                # Find all error messages in the file
                matches = error_pattern.findall(content)
                if matches:
                    error_messages.extend(matches)
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
    
    # Count occurrences of each error message
    error_counts = Counter(error_messages)
    
    return error_counts

def main():
    """Main function to run the error message extraction."""
    directory = "/home/ec2-user/e2mc_assistant/tranformed_mc_profiles/mp4"
    error_counts = extract_error_messages(directory)
    
    if not error_counts:
        print("No error messages found.")
        return
    
    print("\nUnique error messages (with occurrence count):")
    print("-" * 80)
    
    for i, (message, count) in enumerate(error_counts.most_common(), 1):
        print(f"{i}. [{count} occurrences] {message}")
        print("-" * 80)
    
    print(f"\nTotal unique error messages: {len(error_counts)}")
    print(f"Total error occurrences: {sum(error_counts.values())}")

if __name__ == "__main__":
    main()
