#!/bin/bash

# Script to organize encoding XML files based on output format
# Creates subdirectories named after the <output> tag value and moves files there

# Change to the encoding_profiles directory
cd /home/ec2-user/e2mc_assistant/encoding_profiles

# Process each XML file
for xml_file in *.xml; do
    # Extract the output format from the <output> tag using a more direct approach
    output_format=$(grep -a -o '<output>[^<]*</output>' "$xml_file" | sed 's/<output>\(.*\)<\/output>/\1/' | tr -d ' \t\n\r')
    
    if [ -n "$output_format" ]; then
        # Create directory if it doesn't exist
        mkdir -p "$output_format"
        
        # Copy the file to the appropriate directory
        cp "$xml_file" "$output_format/"
        
        echo "Moved $xml_file to $output_format/"
    else
        # Try another approach with more context
        output_format=$(grep -a -A 10 '<format>' "$xml_file" | grep -a -o '<output>[^<]*</output>' | sed 's/<output>\(.*\)<\/output>/\1/' | tr -d ' \t\n\r')
        
        if [ -n "$output_format" ]; then
            # Create directory if it doesn't exist
            mkdir -p "$output_format"
            
            # Copy the file to the appropriate directory
            cp "$xml_file" "$output_format/"
            
            echo "Moved $xml_file to $output_format/"
        else
            echo "Warning: Could not find output format in $xml_file"
        fi
    fi
done

echo "Organization complete!"
