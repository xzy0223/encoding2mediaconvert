#!/usr/bin/env python3
"""
Script to find encoding profiles that don't have corresponding videos in the source bucket.
"""

import os
import re
import argparse
import logging
import boto3
from botocore.exceptions import ClientError
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('find-profiles-without-videos')

class ProfileVideoMatcher:
    def __init__(self, source_bucket, profiles_dir):
        """
        Initialize the profile video matcher.
        
        Args:
            source_bucket (str): Source S3 bucket name
            profiles_dir (str): Directory containing encoding profiles
        """
        self.source_bucket = source_bucket
        self.profiles_dir = profiles_dir
        self.s3_client = boto3.client('s3')
        
    def get_all_profile_ids(self):
        """
        Get all profile IDs from the profiles directory.
        
        Returns:
            dict: Mapping of profile ID to category
        """
        profile_mapping = {}
        profile_files_by_category = {}
        
        # Get all categories (directories) in the profiles directory
        categories = [d for d in os.listdir(self.profiles_dir) 
                     if os.path.isdir(os.path.join(self.profiles_dir, d))]
        
        for category in categories:
            category_dir = os.path.join(self.profiles_dir, category)
            
            # Get all XML files in this category
            profile_files = [f for f in os.listdir(category_dir) if f.endswith('.xml')]
            profile_files_by_category[category] = profile_files
            
            for profile_file in profile_files:
                # Extract the profile ID from the filename (e.g., "1002.xml" -> "1002")
                profile_id = os.path.splitext(profile_file)[0]
                
                # Store the mapping
                profile_mapping[profile_id] = category
        
        logger.info(f"Found {len(profile_mapping)} profile IDs across {len(categories)} categories")
        
        # Log the count of profiles per category
        for category, files in profile_files_by_category.items():
            logger.info(f"Category '{category}': {len(files)} profiles")
            
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
    
    def find_profiles_without_videos(self):
        """
        Find encoding profiles that don't have corresponding videos in the source bucket.
        """
        # Get all profile IDs
        all_profiles = self.get_all_profile_ids()
        all_profile_ids = set(all_profiles.keys())
        
        # Get videos from source bucket
        source_videos = self.list_source_videos()
        source_profile_ids = set(source_videos.keys())
        
        # Find profiles without videos
        profiles_without_videos = all_profile_ids - source_profile_ids
        
        if profiles_without_videos:
            logger.info(f"Found {len(profiles_without_videos)} profile IDs without corresponding videos:")
            for profile_id in sorted(profiles_without_videos):
                category = all_profiles[profile_id]
                logger.info(f"  - Profile ID {profile_id} (Category: {category})")
        else:
            logger.info("All profiles have corresponding videos")
            
        # Find videos without profiles (shouldn't happen based on your description)
        videos_without_profiles = source_profile_ids - all_profile_ids
        
        if videos_without_profiles:
            logger.info(f"Found {len(videos_without_profiles)} video IDs without corresponding profiles:")
            for video_id in sorted(videos_without_profiles):
                logger.info(f"  - Video ID {video_id}")
        else:
            logger.info("All videos have corresponding profiles")
            
        # Summary
        logger.info(f"Summary:")
        logger.info(f"  - Total profiles: {len(all_profile_ids)}")
        logger.info(f"  - Total videos: {len(source_profile_ids)}")
        logger.info(f"  - Profiles without videos: {len(profiles_without_videos)}")
        logger.info(f"  - Videos without profiles: {len(videos_without_profiles)}")

def main():
    parser = argparse.ArgumentParser(description='Find encoding profiles without corresponding videos')
    parser.add_argument('--source-bucket', default='fw-mc-profile', help='Source S3 bucket name')
    parser.add_argument('--profiles-dir', default='/home/ec2-user/e2mc_assistant/encoding_profiles', 
                        help='Directory containing encoding profiles')
    
    args = parser.parse_args()
    
    matcher = ProfileVideoMatcher(
        source_bucket=args.source_bucket,
        profiles_dir=args.profiles_dir
    )
    
    matcher.find_profiles_without_videos()

if __name__ == '__main__':
    main()
