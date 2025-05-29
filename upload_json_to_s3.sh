#!/bin/bash

# Directory containing JSON files
SOURCE_DIR="/home/ec2-user/e2mc_assistant/tranformed_mc_profiles/pilot1/mp4"
# S3 bucket destination
S3_BUCKET="s3://fw-mc-test"

# Loop through all JSON files in the directory
for json_file in "$SOURCE_DIR"/*.json; do
    # Extract the filename without extension (e.g., "429" from "429.json")
    filename=$(basename "$json_file")
    id="${filename%.*}"
    
    # Upload to S3 with the pattern s3://fw-mc-test/mp4/{id}/{id}.json
    aws s3 cp "$json_file" "$S3_BUCKET/mp4/$id/$filename"
    
    # Print status
    echo "Uploaded $filename to $S3_BUCKET/mp4/$id/$filename"
done
