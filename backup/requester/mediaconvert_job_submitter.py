#!/usr/bin/env python3
"""
MediaConvert Job Submitter

This script submits transcoding jobs to AWS MediaConvert service.
It loads a MediaConvert job configuration file, allows customization of input file URLs
and output destinations, and submits the job to AWS MediaConvert.

Usage:
    python mediaconvert_job_submitter.py --profile-path <path_to_profile> 
                                         --input-url <input_url> 
                                         --output-destination <output_destination>
                                         [--region <aws_region>]
                                         [--endpoint-url <endpoint_url>]
                                         [--role-arn <role_arn>]
"""

import argparse
import boto3
import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MediaConvertJobSubmitter:
    """Class to handle AWS MediaConvert job submission."""

    def __init__(self, region: str = 'us-east-1', endpoint_url: Optional[str] = None, role_arn: Optional[str] = None):
        """
        Initialize the MediaConvert job submitter.

        Args:
            region: AWS region where MediaConvert is available
            endpoint_url: Optional custom endpoint URL for MediaConvert
            role_arn: IAM role ARN that MediaConvert will assume to access resources
        """
        self.region = region
        self.endpoint_url = endpoint_url
        self.role_arn = role_arn
        
        # If endpoint URL is not provided, get it from the service
        if not self.endpoint_url:
            self._get_endpoint_url()
            
        # Initialize MediaConvert client
        self.client = boto3.client(
            'mediaconvert',
            region_name=self.region,
            endpoint_url=self.endpoint_url
        )
        
        logger.info(f"Initialized MediaConvert client in {self.region} with endpoint {self.endpoint_url}")

    def _get_endpoint_url(self):
        """Get the endpoint URL for MediaConvert in the specified region."""
        try:
            # Create a MediaConvert client without an endpoint to get the endpoint
            mc_client = boto3.client('mediaconvert', region_name=self.region)
            response = mc_client.describe_endpoints()
            self.endpoint_url = response['Endpoints'][0]['Url']
            logger.info(f"Retrieved MediaConvert endpoint: {self.endpoint_url}")
        except Exception as e:
            logger.error(f"Failed to get MediaConvert endpoint: {str(e)}")
            raise

    def load_job_profile(self, profile_path: str) -> Dict[str, Any]:
        """
        Load a MediaConvert job profile from a JSON file.

        Args:
            profile_path: Path to the MediaConvert job profile JSON file

        Returns:
            Dict containing the job profile
        """
        try:
            with open(profile_path, 'r') as f:
                job_profile = json.load(f)
            logger.info(f"Loaded job profile from {profile_path}")
            return job_profile
        except Exception as e:
            logger.error(f"Failed to load job profile from {profile_path}: {str(e)}")
            raise

    def update_input_url(self, job_profile: Dict[str, Any], input_url: str, input_index: int = 0) -> Dict[str, Any]:
        """
        Update the input file URL in the job profile.

        Args:
            job_profile: MediaConvert job profile
            input_url: New input file URL
            input_index: Index of the input to update (default: 0)

        Returns:
            Updated job profile
        """
        try:
            if 'Settings' in job_profile and 'Inputs' in job_profile['Settings']:
                if input_index < len(job_profile['Settings']['Inputs']):
                    job_profile['Settings']['Inputs'][input_index]['FileInput'] = input_url
                    logger.info(f"Updated input URL to {input_url}")
                else:
                    logger.error(f"Input index {input_index} out of range")
            else:
                logger.error("Invalid job profile structure: 'Settings.Inputs' not found")
            
            return job_profile
        except Exception as e:
            logger.error(f"Failed to update input URL: {str(e)}")
            raise

    def update_output_destination(self, job_profile: Dict[str, Any], output_destination: str, 
                                 output_group_index: int = 0) -> Dict[str, Any]:
        """
        Update the output destination in the job profile.

        Args:
            job_profile: MediaConvert job profile
            output_destination: New output destination
            output_group_index: Index of the output group to update (default: 0)

        Returns:
            Updated job profile
        """
        try:
            if 'Settings' in job_profile and 'OutputGroups' in job_profile['Settings']:
                if output_group_index < len(job_profile['Settings']['OutputGroups']):
                    output_group = job_profile['Settings']['OutputGroups'][output_group_index]
                    
                    # Handle different output group types
                    if 'OutputGroupSettings' in output_group:
                        settings_type = output_group['OutputGroupSettings'].get('Type')
                        
                        if settings_type == 'FILE_GROUP_SETTINGS' and 'FileGroupSettings' in output_group['OutputGroupSettings']:
                            output_group['OutputGroupSettings']['FileGroupSettings']['Destination'] = output_destination
                        elif settings_type == 'HLS_GROUP_SETTINGS' and 'HlsGroupSettings' in output_group['OutputGroupSettings']:
                            output_group['OutputGroupSettings']['HlsGroupSettings']['Destination'] = output_destination
                        elif settings_type == 'DASH_ISO_GROUP_SETTINGS' and 'DashIsoGroupSettings' in output_group['OutputGroupSettings']:
                            output_group['OutputGroupSettings']['DashIsoGroupSettings']['Destination'] = output_destination
                        elif settings_type == 'CMAF_GROUP_SETTINGS' and 'CmafGroupSettings' in output_group['OutputGroupSettings']:
                            output_group['OutputGroupSettings']['CmafGroupSettings']['Destination'] = output_destination
                        elif settings_type == 'MS_SMOOTH_GROUP_SETTINGS' and 'MsSmoothGroupSettings' in output_group['OutputGroupSettings']:
                            output_group['OutputGroupSettings']['MsSmoothGroupSettings']['Destination'] = output_destination
                        else:
                            logger.warning(f"Unsupported output group type: {settings_type}")
                            
                        logger.info(f"Updated output destination to {output_destination}")
                    else:
                        logger.error("Invalid job profile structure: 'OutputGroupSettings' not found")
                else:
                    logger.error(f"Output group index {output_group_index} out of range")
            else:
                logger.error("Invalid job profile structure: 'Settings.OutputGroups' not found")
            
            return job_profile
        except Exception as e:
            logger.error(f"Failed to update output destination: {str(e)}")
            raise

    def submit_job(self, job_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit a job to AWS MediaConvert.

        Args:
            job_profile: MediaConvert job profile

        Returns:
            Response from the create_job API call
        """
        try:
            # If role ARN is provided, add it to the job profile
            if self.role_arn:
                job_profile['Role'] = self.role_arn
            
            # Submit the job
            response = self.client.create_job(**job_profile)
            
            job_id = response['Job']['Id']
            logger.info(f"Successfully submitted job with ID: {job_id}")
            
            return response
        except Exception as e:
            logger.error(f"Failed to submit job: {str(e)}")
            raise


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Submit a job to AWS MediaConvert')
    
    parser.add_argument('--profile-path', required=True, 
                        help='Path to the MediaConvert job profile JSON file')
    parser.add_argument('--input-url', required=True,
                        help='Input file URL (S3 path)')
    parser.add_argument('--output-destination', required=True,
                        help='Output destination (S3 path)')
    parser.add_argument('--region', default='us-east-1',
                        help='AWS region (default: us-east-1)')
    parser.add_argument('--endpoint-url', 
                        help='MediaConvert endpoint URL (optional)')
    parser.add_argument('--role-arn',
                        help='IAM role ARN for MediaConvert to access resources (optional)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Initialize the job submitter
        submitter = MediaConvertJobSubmitter(
            region=args.region,
            endpoint_url=args.endpoint_url,
            role_arn=args.role_arn
        )
        
        # Load the job profile
        job_profile = submitter.load_job_profile(args.profile_path)
        
        # Update input URL and output destination
        job_profile = submitter.update_input_url(job_profile, args.input_url)
        job_profile = submitter.update_output_destination(job_profile, args.output_destination)
        
        # Submit the job
        response = submitter.submit_job(job_profile)
        
        # Print the job ID
        print(f"Job submitted successfully. Job ID: {response['Job']['Id']}")
        
        # Print the full response as JSON if verbose
        if args.verbose:
            print(json.dumps(response, indent=2))
        
        return 0
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
