#!/usr/bin/env python3
"""
Script to find missing videos in the target S3 bucket compared to encoding profiles.
"""

import os
import re
import argparse
import logging
import boto3
from botocore.exceptions import ClientError
from collections import defaultdict, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('find-missing-videos')

class MissingVideoFinder:
    def __init__(self, source_bucket, target_bucket, profiles_dir):
        """
        Initialize the missing video finder.
        
        Args:
            source_bucket (str): Source S3 bucket name
            target_bucket (str): Target S3 bucket name
            profiles_dir (str): Directory containing encoding profiles
        """
        self.source_bucket = source_bucket
        self.target_bucket = target_bucket
        self.profiles_dir = profiles_dir
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
                    
                    # Parse the filename to extract ID and type
                    match = re.match(r'(\d+)_.*_(source|target)\.(.*)', filename)
                    if match:
                        video_id, file_type, extension = match.groups()
                        
                        # Store in our dictionary
                        videos_by_id[video_id][file_type] = {
                            'key': key,
                            'filename': filename,
                            'extension': extension,
                            'size': obj['Size']
                        }
            
            # Filter out entries that don't have both source and target
            complete_videos = {
                video_id: files 
                for video_id, files in videos_by_id.items() 
                if files['source'] is not None and files['target'] is not None
            }
            
            logger.info(f"Found {len(complete_videos)} complete video pairs in source bucket")
            return complete_videos
            
        except ClientError as e:
            logger.error(f"Error listing objects in source bucket: {e}")
            return {}
    
    def list_target_videos(self):
        """
        List all videos in the target bucket.
        
        Returns:
            set: Set of profile IDs that have videos in the target bucket
        """
        profile_ids_in_target = set()
        file_count = 0
        
        try:
            # List objects in the target bucket
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.target_bucket)
            
            # Process each object
            for page in pages:
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    key = obj['Key']
                    file_count += 1
                    
                    # Parse the key to extract category and profile ID
                    parts = key.split('/')
                    if len(parts) >= 3:
                        profile_id = parts[1]
                        profile_ids_in_target.add(profile_id)
            
            logger.info(f"Found {file_count} files in target bucket across {len(profile_ids_in_target)} profile IDs")
            return profile_ids_in_target, file_count
            
        except ClientError as e:
            logger.error(f"Error listing objects in target bucket: {e}")
            return set(), 0
    
    def find_missing_videos(self):
        """
        Find videos that are missing in the target bucket.
        """
        # Get all profile IDs from the mapping
        all_profile_ids = set(self.profile_mapping.keys())
        logger.info(f"Total number of profile IDs in mapping: {len(all_profile_ids)}")
        
        # Get videos from source bucket
        source_videos = self.list_source_videos()
        source_profile_ids = set(source_videos.keys())
        logger.info(f"Number of profile IDs with videos in source bucket: {len(source_profile_ids)}")
        
        # Get profile IDs from target bucket
        target_profile_ids, target_file_count = self.list_target_videos()
        logger.info(f"Number of profile IDs with videos in target bucket: {len(target_profile_ids)}")
        logger.info(f"Total number of files in target bucket: {target_file_count}")
        
        # Find profiles that have videos in source but not in target
        missing_in_target = source_profile_ids - target_profile_ids
        if missing_in_target:
            logger.info(f"Found {len(missing_in_target)} profile IDs with videos in source but not in target:")
            for profile_id in sorted(missing_in_target):
                if profile_id in self.profile_mapping:
                    category, _ = self.profile_mapping[profile_id]
                    logger.info(f"  - Profile ID {profile_id} (Category: {category})")
                else:
                    logger.info(f"  - Profile ID {profile_id} (No category mapping)")
        else:
            logger.info("No missing profile IDs found in target bucket")
        
        # Find profiles that have incomplete file pairs in target
        # Each profile should have 2 files (source and target)
        profile_file_counts = Counter()
        
        try:
            # List objects in the target bucket
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.target_bucket)
            
            # Count files per profile ID
            for page in pages:
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    key = obj['Key']
                    parts = key.split('/')
                    if len(parts) >= 3:
                        profile_id = parts[1]
                        profile_file_counts[profile_id] += 1
            
            # Find profiles with incomplete file pairs
            incomplete_profiles = []
            for profile_id, count in profile_file_counts.items():
                if count != 2:  # Should have source and target
                    incomplete_profiles.append((profile_id, count))
            
            if incomplete_profiles:
                logger.info(f"Found {len(incomplete_profiles)} profile IDs with incomplete file pairs:")
                for profile_id, count in sorted(incomplete_profiles):
                    if profile_id in self.profile_mapping:
                        category, _ = self.profile_mapping[profile_id]
                        logger.info(f"  - Profile ID {profile_id} (Category: {category}) has {count} file(s) instead of 2")
                    else:
                        logger.info(f"  - Profile ID {profile_id} has {count} file(s) instead of 2")
            else:
                logger.info("No incomplete file pairs found in target bucket")
                
            # Calculate expected vs actual file count
            expected_file_count = len(target_profile_ids) * 2  # Each profile should have source and target
            logger.info(f"Expected file count: {expected_file_count}, Actual file count: {target_file_count}")
            if expected_file_count != target_file_count:
                logger.info(f"Discrepancy: {expected_file_count - target_file_count} files")
                
        except ClientError as e:
            logger.error(f"Error analyzing target bucket: {e}")

def main():
    parser = argparse.ArgumentParser(description='Find missing videos in target S3 bucket')
    parser.add_argument('--source-bucket', default='fw-mc-profile', help='Source S3 bucket name')
    parser.add_argument('--target-bucket', default='fw-mc-test', help='Target S3 bucket name')
    parser.add_argument('--profiles-dir', default='/home/ec2-user/e2mc_assistant/encoding_profiles', 
                        help='Directory containing encoding profiles')
    
    args = parser.parse_args()
    
    finder = MissingVideoFinder(
        source_bucket=args.source_bucket,
        target_bucket=args.target_bucket,
        profiles_dir=args.profiles_dir
    )
    
    finder.find_missing_videos()

if __name__ == '__main__':
    main()
