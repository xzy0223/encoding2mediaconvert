#!/usr/bin/env python3
"""
Script to analyze .err log files in the specified directory,
extract error messages after "Error message:", and remove duplicates.
Also includes the file IDs associated with each error message.
"""

import os
import re
from collections import defaultdict

def extract_error_messages(directory):
    """
    Extract error messages from .err files in the specified directory.
    
    Args:
        directory: Path to the directory containing .err files
        
    Returns:
        Dictionary mapping error messages to lists of file IDs
    """
    error_to_files = defaultdict(list)
    error_pattern = re.compile(r'Error message:\s*(.*?)(?:\n|$)')
    
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return {}
    
    # Find all .err files in the directory
    err_files = [f for f in os.listdir(directory) if f.endswith('.err')]
    
    if not err_files:
        print(f"No .err files found in {directory}")
        return {}
    
    print(f"Found {len(err_files)} .err files in {directory}")
    
    # Process each .err file
    for err_file in err_files:
        file_path = os.path.join(directory, err_file)
        try:
            # Extract file ID from filename (e.g., 1064_job_submission.err -> 1064)
            file_id = err_file.split('_')[0]
            
            with open(file_path, 'r') as f:
                content = f.read()
                # Find all error messages in the file
                matches = error_pattern.findall(content)
                for match in matches:
                    error_to_files[match].append(file_id)
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
    
    return error_to_files

def main():
    """Main function to run the error message extraction."""
    directory = "/home/ec2-user/e2mc_assistant/tranformed_mc_profiles/mp4"
    error_to_files = extract_error_messages(directory)
    
    if not error_to_files:
        print("No error messages found.")
        return
    
    # Sort errors by frequency (number of files)
    sorted_errors = sorted(error_to_files.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("\nUnique error messages with associated file IDs:")
    print("-" * 80)
    
    for i, (message, file_ids) in enumerate(sorted_errors, 1):
        print(f"{i}. [{len(file_ids)} occurrences] {message}")
        print(f"   Files: {', '.join(sorted(file_ids))}")
        print("-" * 80)
    
    print(f"\nTotal unique error messages: {len(error_to_files)}")
    print(f"Total error occurrences: {sum(len(files) for files in error_to_files.values())}")
    
    # Generate a markdown summary
    with open('/home/ec2-user/e2mc_assistant/error_summary_with_ids.md', 'w') as f:
        f.write("# Error Analysis Summary\n\n")
        f.write("## Error Messages with Associated File IDs\n\n")
        
        for i, (message, file_ids) in enumerate(sorted_errors, 1):
            f.write(f"### {i}. Error Type ({len(file_ids)} occurrences)\n\n")
            f.write(f"**Error Message:**\n```\n{message}\n```\n\n")
            f.write(f"**Affected Files:** {', '.join(sorted(file_ids))}\n\n")
            
        f.write("\n## Statistics\n\n")
        f.write(f"- Total unique error messages: {len(error_to_files)}\n")
        f.write(f"- Total error occurrences: {sum(len(files) for files in error_to_files.values())}\n")
    
    print(f"\nDetailed summary saved to: /home/ec2-user/e2mc_assistant/error_summary_with_ids.md")

if __name__ == "__main__":
    main()
