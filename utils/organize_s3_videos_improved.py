#!/usr/bin/env python3
"""
Script to organize videos from encoding.com to a structured S3 bucket.
Handles files with missing extensions.

This script:
1. Scans the source S3 bucket for original and encoding-generated videos
2. Organizes them by encoding profile categories and profile IDs
3. Copies them to the target S3 bucket with the new structure
"""

import os
import re
import argparse
import logging
import boto3
from botocore.exceptions import ClientError
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('s3-video-organizer')

class S3VideoOrganizer:
    def __init__(self, source_bucket, target_bucket, profiles_dir, dry_run=False):
        """
        Initialize the S3 video organizer.
        
        Args:
            source_bucket (str): Source S3 bucket name
            target_bucket (str): Target S3 bucket name
            profiles_dir (str): Directory containing encoding profiles
            dry_run (bool): If True, don't actually copy files
        """
        self.source_bucket = source_bucket
        self.target_bucket = target_bucket
        self.profiles_dir = profiles_dir
        self.dry_run = dry_run
        self.s3_client = boto3.client('s3')
        
        # Map of profile ID to category and file prefix
        self.profile_mapping = self._build_profile_mapping()
        
    def _build_profile_mapping(self):
        """
        Build a mapping of profile IDs to their categories and file prefixes.
        
        Returns:
            dict: Mapping of profile ID to (category, file_prefix)
        """
        profile_mapping = {}
        
        # Get all categories (directories) in the profiles directory
        categories = [d for d in os.listdir(self.profiles_dir) 
                     if os.path.isdir(os.path.join(self.profiles_dir, d))]
        
        for category in categories:
            category_dir = os.path.join(self.profiles_dir, category)
            
            # Get all XML files in this category
            profile_files = [f for f in os.listdir(category_dir) if f.endswith('.xml')]
            
            for profile_file in profile_files:
                # Extract the profile ID from the filename (e.g., "1002.xml" -> "1002")
                profile_id = os.path.splitext(profile_file)[0]
                
                # Store the mapping
                profile_mapping[profile_id] = (category, profile_id)
                
        logger.info(f"Built profile mapping with {len(profile_mapping)} profiles")
        return profile_mapping
    
    def list_source_videos(self):
        """
        List all videos in the source bucket.
        
        Returns:
            dict: Dictionary mapping video IDs to lists of source and target files
        """
        videos_by_id = defaultdict(lambda: {'source': None, 'target': None})
        
        try:
            # List objects in the source bucket
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.source_bucket, Prefix='enc_formats_and_videos/source_videos/')
            
            # Process each object
            for page in pages:
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    key = obj['Key']
                    filename = os.path.basename(key)
                    
                    # First try the standard pattern with extension
                    match = re.match(r'(\d+)_.*_(source|target)\.(.*)', filename)
                    if not match:
                        # Try alternative pattern without extension
                        match = re.match(r'(\d+)_.*_(source|target)$', filename)
                    
                    if match:
                        if len(match.groups()) == 3:
                            video_id, file_type, extension = match.groups()
                        else:
                            video_id, file_type = match.groups()
                            extension = "unknown"  # No extension found
                        
                        # Store in our dictionary
                        videos_by_id[video_id][file_type] = {
                            'key': key,
                            'filename': filename,
                            'extension': extension if 'extension' in locals() else "unknown",
                            'size': obj['Size']
                        }
            
            # Filter out entries that don't have both source and target
            complete_videos = {
                video_id: files 
                for video_id, files in videos_by_id.items() 
                if files['source'] is not None and files['target'] is not None
            }
            
            # Log files with missing extensions
            missing_extension_files = []
            for video_id, files in complete_videos.items():
                if files['source']['extension'] == "unknown":
                    missing_extension_files.append(files['source']['filename'])
                if files['target']['extension'] == "unknown":
                    missing_extension_files.append(files['target']['filename'])
            
            if missing_extension_files:
                logger.info(f"Found {len(missing_extension_files)} files with missing extensions:")
                for filename in sorted(missing_extension_files):
                    logger.info(f"  - {filename}")
            
            logger.info(f"Found {len(complete_videos)} complete video pairs in source bucket")
            return complete_videos
            
        except ClientError as e:
            logger.error(f"Error listing objects in source bucket: {e}")
            return {}
    
    def copy_videos_to_target(self, videos_by_id):
        """
        Copy videos to the target bucket with the new structure.
        
        Args:
            videos_by_id (dict): Dictionary mapping video IDs to source and target files
        """
        # Count for statistics
        total_videos = len(videos_by_id)
        copied_videos = 0
        skipped_videos = 0
        
        # Process each video
        for video_id, files in videos_by_id.items():
            # Check if this profile ID is in our mapping
            if video_id not in self.profile_mapping:
                logger.warning(f"No profile mapping found for video ID {video_id}, skipping")
                skipped_videos += 1
                continue
                
            category, profile_prefix = self.profile_mapping[video_id]
            
            # Define source and target paths
            source_key = files['source']['key']
            target_key = f"{category}/{profile_prefix}/{os.path.basename(source_key)}"
            
            # Copy source video
            if not self.dry_run:
                try:
                    self.s3_client.copy_object(
                        CopySource={'Bucket': self.source_bucket, 'Key': source_key},
                        Bucket=self.target_bucket,
                        Key=target_key
                    )
                    logger.info(f"Copied source video: {source_key} -> {self.target_bucket}/{target_key}")
                except ClientError as e:
                    logger.error(f"Error copying source video {source_key}: {e}")
                    continue
            else:
                logger.info(f"[DRY RUN] Would copy: {source_key} -> {self.target_bucket}/{target_key}")
            
            # Copy target (encoding-generated) video
            source_key = files['target']['key']
            target_key = f"{category}/{profile_prefix}/{os.path.basename(source_key)}"
            
            if not self.dry_run:
                try:
                    self.s3_client.copy_object(
                        CopySource={'Bucket': self.source_bucket, 'Key': source_key},
                        Bucket=self.target_bucket,
                        Key=target_key
                    )
                    logger.info(f"Copied target video: {source_key} -> {self.target_bucket}/{target_key}")
                except ClientError as e:
                    logger.error(f"Error copying target video {source_key}: {e}")
                    continue
            else:
                logger.info(f"[DRY RUN] Would copy: {source_key} -> {self.target_bucket}/{target_key}")
            
            copied_videos += 1
        
        logger.info(f"Copied {copied_videos} videos, skipped {skipped_videos} videos out of {total_videos} total")
    
    def run(self):
        """
        Run the video organization process.
        """
        logger.info(f"Starting S3 video organization from {self.source_bucket} to {self.target_bucket}")
        logger.info(f"Using profiles directory: {self.profiles_dir}")
        
        if self.dry_run:
            logger.info("DRY RUN MODE: No files will be copied")
        
        # List videos in source bucket
        videos_by_id = self.list_source_videos()
        
        # Copy videos to target bucket
        self.copy_videos_to_target(videos_by_id)
        
        logger.info("Video organization complete")

def main():
    parser = argparse.ArgumentParser(description='Organize encoding.com videos in S3')
    parser.add_argument('--source-bucket', default='fw-mc-profile', help='Source S3 bucket name')
    parser.add_argument('--target-bucket', default='fw-mc-test', help='Target S3 bucket name')
    parser.add_argument('--profiles-dir', default='/home/ec2-user/e2mc_assistant/encoding_profiles', 
                        help='Directory containing encoding profiles')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no files copied)')
    
    args = parser.parse_args()
    
    organizer = S3VideoOrganizer(
        source_bucket=args.source_bucket,
        target_bucket=args.target_bucket,
        profiles_dir=args.profiles_dir,
        dry_run=args.dry_run
    )
    
    organizer.run()

if __name__ == '__main__':
    main()
