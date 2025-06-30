#!/bin/bash

# Check if path is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory_path>"
    exit 1
fi

# Get the directory path from command line argument
DIR_PATH="$1"

# Check if directory exists
if [ ! -d "$DIR_PATH" ]; then
    echo "Error: Directory '$DIR_PATH' does not exist."
    exit 1
fi

# Find all json files, extract filenames without extension, and join with commas
find "$DIR_PATH" -type f -name "*.json" | xargs -I{} basename {} .json | tr '\n' ',' | sed 's/,$//'

echo ""
