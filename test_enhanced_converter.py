#!/usr/bin/env python3
import os
import json
import logging
from src.e2mc_assistant.converter.config_converter_enhanced import ConfigConverter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_multi_value_conversion():
    """Test conversion of a file with multi-value fields like bitrates, size, keyframes, framerates"""
    # Path to the test file
    test_file = "/home/ec2-user/e2mc_assistant/encoding_profiles/ipad_stream/54.xml"
    
    # Path to the rules file
    rules_file = "/home/ec2-user/e2mc_assistant/src/e2mc_assistant/converter/rules/e2mc_rules.yaml"
    
    # Output file path
    output_file = "/home/ec2-user/e2mc_assistant/test_output_54.json"
    
    # Create converter instance
    converter = ConfigConverter(rules_file)
    
    # Convert the file
    print(f"Converting {test_file}...")
    result = converter.convert(test_file)
    
    # Write the output file
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Conversion completed. Output saved to {output_file}")
    
    # Print summary of the conversion
    print("\nConversion Summary:")
    print(f"- Total parameters: {len(converter.mapped_parameters) + len(converter.unmapped_parameters)}")
    print(f"- Mapped parameters: {len(converter.mapped_parameters)}")
    print(f"- Unmapped parameters: {len(converter.unmapped_parameters)}")
    
    # Check if we have multiple outputs in the result
    if 'Settings' in result and 'OutputGroups' in result['Settings'] and result['Settings']['OutputGroups']:
        output_group = result['Settings']['OutputGroups'][0]
        if 'Outputs' in output_group:
            outputs = output_group['Outputs']
            print(f"\nGenerated {len(outputs)} outputs")
            
            # Print details of each output
            for i, output in enumerate(outputs):
                print(f"\nOutput {i+1}:")
                if 'NameModifier' in output:
                    print(f"- NameModifier: {output['NameModifier']}")
                if 'VideoDescription' in output and 'Width' in output['VideoDescription'] and 'Height' in output['VideoDescription']:
                    print(f"- Resolution: {output['VideoDescription']['Width']}x{output['VideoDescription']['Height']}")
                if 'VideoDescription' in output and 'CodecSettings' in output['VideoDescription']:
                    codec_settings = output['VideoDescription']['CodecSettings']
                    if 'H264Settings' in codec_settings and 'Bitrate' in codec_settings['H264Settings']:
                        print(f"- Video Bitrate: {codec_settings['H264Settings']['Bitrate']}")
                if 'AudioDescriptions' in output and output['AudioDescriptions']:
                    audio_desc = output['AudioDescriptions'][0]
                    if 'CodecSettings' in audio_desc:
                        audio_codec = audio_desc['CodecSettings'].get('Codec', 'Unknown')
                        print(f"- Audio Codec: {audio_codec}")
                        if 'AacSettings' in audio_desc['CodecSettings'] and 'Bitrate' in audio_desc['CodecSettings']['AacSettings']:
                            print(f"- Audio Bitrate: {audio_desc['CodecSettings']['AacSettings']['Bitrate']}")

if __name__ == "__main__":
    test_multi_value_conversion()
