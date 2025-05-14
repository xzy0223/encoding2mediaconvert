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
                                         [--track-job]
"""

import argparse
import boto3
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Custom JSON encoder for handling datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MediaConvertJobSubmitter:
    """Class to handle AWS MediaConvert job submission and tracking."""

    # Job status constants
    STATUS_SUBMITTED = 'SUBMITTED'
    STATUS_PROGRESSING = 'PROGRESSING'
    STATUS_COMPLETE = 'COMPLETE'
    STATUS_CANCELED = 'CANCELED'
    STATUS_ERROR = 'ERROR'
    
    # Terminal states
    TERMINAL_STATES = [STATUS_COMPLETE, STATUS_CANCELED, STATUS_ERROR]

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

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a MediaConvert job.

        Args:
            job_id: The ID of the job to check

        Returns:
            Dict containing job details
        """
        try:
            response = self.client.get_job(Id=job_id)
            return response['Job']
        except Exception as e:
            logger.error(f"Failed to get job status for job {job_id}: {str(e)}")
            raise

    def list_jobs(self, status: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        List MediaConvert jobs with optional status filter.

        Args:
            status: Optional status filter (SUBMITTED, PROGRESSING, COMPLETE, CANCELED, ERROR)
            max_results: Maximum number of jobs to return (default: 20)

        Returns:
            List of job summaries
        """
        try:
            params = {'MaxResults': max_results}
            if status:
                params['Status'] = status
                
            response = self.client.list_jobs(**params)
            return response['Jobs']
        except Exception as e:
            logger.error(f"Failed to list jobs: {str(e)}")
            raise

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a MediaConvert job.

        Args:
            job_id: The ID of the job to cancel

        Returns:
            Dict containing the response
        """
        try:
            response = self.client.cancel_job(Id=job_id)
            logger.info(f"Canceled job {job_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {str(e)}")
            raise

    def track_job(self, job_id: str, poll_interval: int = 10, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Track a MediaConvert job until completion or timeout.

        Args:
            job_id: The ID of the job to track
            poll_interval: Time in seconds between status checks (default: 10)
            timeout: Optional timeout in seconds (default: None, no timeout)

        Returns:
            Dict containing the final job details
        """
        start_time = time.time()
        elapsed_time = 0
        
        logger.info(f"Starting to track job {job_id}")
        
        while timeout is None or elapsed_time < timeout:
            job = self.get_job_status(job_id)
            status = job['Status']
            
            # Calculate progress percentage if available
            progress_pct = job.get('JobPercentComplete', 0)
            
            # Get current phase if available
            current_phase = job.get('CurrentPhase', 'Unknown')
            
            logger.info(f"Job {job_id} status: {status}, progress: {progress_pct}%, phase: {current_phase}")
            
            # If job is in a terminal state, return the job details
            if status in self.TERMINAL_STATES:
                if status == self.STATUS_COMPLETE:
                    logger.info(f"Job {job_id} completed successfully")
                elif status == self.STATUS_ERROR:
                    error_message = job.get('ErrorMessage', 'Unknown error')
                    logger.error(f"Job {job_id} failed with error: {error_message}")
                elif status == self.STATUS_CANCELED:
                    logger.info(f"Job {job_id} was canceled")
                
                return job
            
            # Sleep before next check
            time.sleep(poll_interval)
            elapsed_time = time.time() - start_time
        
        # If we reach here, we've timed out
        logger.warning(f"Tracking job {job_id} timed out after {elapsed_time:.1f} seconds")
        return self.get_job_status(job_id)

    def get_job_metrics(self, job_id: str) -> Dict[str, Any]:
        """
        Get detailed metrics for a completed job.

        Args:
            job_id: The ID of the job to get metrics for

        Returns:
            Dict containing job metrics
        """
        job = self.get_job_status(job_id)
        
        # Only get metrics for completed jobs
        if job['Status'] != self.STATUS_COMPLETE:
            logger.warning(f"Job {job_id} is not complete, metrics may be incomplete")
        
        metrics = {
            'job_id': job_id,
            'status': job['Status'],
            'created_at': job.get('CreatedAt'),
            'submitted_at': job.get('SubmittedAt'),
            'started_at': job.get('StartedAt'),
            'completed_at': job.get('CompletedAt'),
            'elapsed_time_seconds': None,
            'billing_tags': job.get('BillingTagsSource'),
            'queue': job.get('Queue'),
            'user_metadata': job.get('UserMetadata', {}),
            'warnings': job.get('Warnings', []),
            'output_group_details': []
        }
        
        # Calculate elapsed time if possible
        if metrics['started_at'] and metrics['completed_at']:
            start_time = metrics['started_at'].timestamp() if hasattr(metrics['started_at'], 'timestamp') else 0
            end_time = metrics['completed_at'].timestamp() if hasattr(metrics['completed_at'], 'timestamp') else 0
            metrics['elapsed_time_seconds'] = end_time - start_time
        
        # Extract output group details
        if 'Settings' in job and 'OutputGroups' in job['Settings']:
            for i, output_group in enumerate(job['Settings']['OutputGroups']):
                group_detail = {
                    'Type': output_group.get('OutputGroupSettings', {}).get('Type', 'Unknown'),
                    'OutputDetails': []
                }
                
                # Extract output details
                if 'Outputs' in output_group:
                    for output in output_group['Outputs']:
                        # Try to determine output file paths
                        output_paths = []
                        
                        # Get destination from output group settings
                        destination = None
                        group_settings = output_group.get('OutputGroupSettings', {})
                        
                        # Handle different output group types
                        if 'FileGroupSettings' in group_settings:
                            destination = group_settings['FileGroupSettings'].get('Destination', '')
                        elif 'HlsGroupSettings' in group_settings:
                            destination = group_settings['HlsGroupSettings'].get('Destination', '')
                        elif 'DashIsoGroupSettings' in group_settings:
                            destination = group_settings['DashIsoGroupSettings'].get('Destination', '')
                        elif 'CmafGroupSettings' in group_settings:
                            destination = group_settings['CmafGroupSettings'].get('Destination', '')
                        elif 'MsSmoothGroupSettings' in group_settings:
                            destination = group_settings['MsSmoothGroupSettings'].get('Destination', '')
                        
                        # Construct output path using destination and name modifier
                        if destination:
                            name_modifier = output.get('NameModifier', '')
                            extension = output.get('Extension', '')
                            
                            # If no extension but we have container settings, try to determine it
                            if not extension and 'ContainerSettings' in output:
                                container = output['ContainerSettings'].get('Container', '')
                                if container == 'MP4':
                                    extension = '.mp4'
                                elif container == 'MOV':
                                    extension = '.mov'
                                elif container == 'M3U8':
                                    extension = '.m3u8'
                                elif container == 'MPD':
                                    extension = '.mpd'
                                # Add more container types as needed
                            
                            if name_modifier or extension:
                                output_path = f"{destination}{name_modifier}{extension}"
                                output_paths.append(output_path)
                        
                        group_detail['OutputDetails'].append({
                            'OutputFilePaths': output_paths
                        })
                
                metrics['output_group_details'].append(group_detail)
        
        return metrics


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
    parser.add_argument('--track-job', action='store_true',
                        help='Track job progress until completion')
    parser.add_argument('--poll-interval', type=int, default=10,
                        help='Polling interval in seconds when tracking jobs (default: 10)')
    parser.add_argument('--timeout', type=int,
                        help='Timeout in seconds when tracking jobs (optional)')
    parser.add_argument('--job-id',
                        help='Job ID to track (if not submitting a new job)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--list-jobs', action='store_true',
                        help='List recent jobs')
    parser.add_argument('--status-filter',
                        help='Filter jobs by status when listing (SUBMITTED, PROGRESSING, COMPLETE, CANCELED, ERROR)')
    parser.add_argument('--max-results', type=int, default=20,
                        help='Maximum number of jobs to list (default: 20)')
    parser.add_argument('--cancel-job',
                        help='Cancel a job by ID')
    
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
        
        # Handle job cancellation if requested
        if args.cancel_job:
            response = submitter.cancel_job(args.cancel_job)
            print(f"Job {args.cancel_job} cancellation request sent")
            return 0
        
        # Handle job listing if requested
        if args.list_jobs:
            jobs = submitter.list_jobs(status=args.status_filter, max_results=args.max_results)
            print(f"Found {len(jobs)} jobs:")
            for job in jobs:
                created_at = job.get('CreatedAt', 'Unknown')
                if hasattr(created_at, 'strftime'):
                    created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
                print(f"ID: {job['Id']}, Status: {job['Status']}, Created: {created_at}")
            return 0
        
        # Handle job tracking if job ID is provided
        if args.job_id:
            print(f"Tracking job {args.job_id}...")
            job = submitter.track_job(args.job_id, poll_interval=args.poll_interval, timeout=args.timeout)
            
            # Print final status
            print(f"Job {args.job_id} final status: {job['Status']}")
            
            # If job completed, print metrics
            if job['Status'] == MediaConvertJobSubmitter.STATUS_COMPLETE:
                metrics = submitter.get_job_metrics(args.job_id)
                if metrics['elapsed_time_seconds']:
                    print(f"Job processing time: {metrics['elapsed_time_seconds']:.1f} seconds")
                
                # Print output details if available
                if 'output_group_details' in metrics and metrics['output_group_details']:
                    print("Output details:")
                    for group in metrics['output_group_details']:
                        print(f"  - Type: {group.get('Type', 'Unknown')}")
                        for output in group.get('OutputDetails', []):
                            output_paths = output.get('OutputFilePaths', [])
                            if output_paths:
                                for path in output_paths:
                                    print(f"    - Output: {path}")
                            else:
                                print(f"    - Output: Unknown")
            
            return 0 if job['Status'] == MediaConvertJobSubmitter.STATUS_COMPLETE else 1
        
        # Submit a new job
        job_profile = submitter.load_job_profile(args.profile_path)
        job_profile = submitter.update_input_url(job_profile, args.input_url)
        job_profile = submitter.update_output_destination(job_profile, args.output_destination)
        
        response = submitter.submit_job(job_profile)
        job_id = response['Job']['Id']
        
        print(f"Job submitted successfully. Job ID: {job_id}")
        
        # Print the full response as JSON if verbose
        if args.verbose:
            print(json.dumps(response, indent=2, cls=DateTimeEncoder))
        
        # Track the job if requested
        if args.track_job:
            print("Tracking job progress...")
            job = submitter.track_job(job_id, poll_interval=args.poll_interval, timeout=args.timeout)
            
            # Print final status
            print(f"Job final status: {job['Status']}")
            
            # If job completed, print metrics
            if job['Status'] == MediaConvertJobSubmitter.STATUS_COMPLETE:
                metrics = submitter.get_job_metrics(job_id)
                if metrics['elapsed_time_seconds']:
                    print(f"Job processing time: {metrics['elapsed_time_seconds']:.1f} seconds")
                
                # Print output details if available
                if 'output_group_details' in metrics and metrics['output_group_details']:
                    print("Output details:")
                    for group in metrics['output_group_details']:
                        print(f"  - Type: {group.get('Type', 'Unknown')}")
                        for output in group.get('OutputDetails', []):
                            output_paths = output.get('OutputFilePaths', [])
                            if output_paths:
                                for path in output_paths:
                                    print(f"    - Output: {path}")
                            else:
                                print(f"    - Output: Unknown")
            
            return 0 if job['Status'] == MediaConvertJobSubmitter.STATUS_COMPLETE else 1
        
        return 0
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
