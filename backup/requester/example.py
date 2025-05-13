#!/usr/bin/env python3
"""
Example script demonstrating how to use the MediaConvertJobSubmitter class.

This script shows how to:
1. Load a MediaConvert job profile
2. Update input and output paths
3. Submit the job to AWS MediaConvert
"""

import argparse
import json
import logging
import os
import sys
from mediaconvert_job_submitter import MediaConvertJobSubmitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Example of using MediaConvertJobSubmitter')
    
    parser.add_argument('--profile-path', 
                        default='../../tranformed_mc_profiles/examples/1-setting.json',
                        help='Path to the MediaConvert job profile JSON file')
    parser.add_argument('--input-url', 
                        default='s3://example-bucket/input/video.mp4',
                        help='Input file URL (S3 path)')
    parser.add_argument('--output-destination', 
                        default='s3://example-bucket/output/',
                        help='Output destination (S3 path)')
    parser.add_argument('--region', default='us-east-1',
                        help='AWS region (default: us-east-1)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print the job profile without submitting')
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    try:
        # Initialize the job submitter
        submitter = MediaConvertJobSubmitter(region=args.region)
        
        # Load the job profile
        job_profile = submitter.load_job_profile(args.profile_path)
        
        # Update input URL and output destination
        job_profile = submitter.update_input_url(job_profile, args.input_url)
        job_profile = submitter.update_output_destination(job_profile, args.output_destination)
        
        # Print the updated job profile
        print("Updated Job Profile:")
        print(json.dumps(job_profile, indent=2))
        
        if not args.dry_run:
            # Submit the job
            response = submitter.submit_job(job_profile)
            
            # Print the job ID
            print(f"\nJob submitted successfully. Job ID: {response['Job']['Id']}")
        else:
            print("\nDry run - job not submitted")
        
        return 0
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
