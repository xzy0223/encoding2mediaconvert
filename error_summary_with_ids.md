# Error Analysis Summary

## Error Messages with Associated File IDs

### 1. Error Type (18 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should match all dependencies: See other errors for more details | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: Should match exactly one schema defined in "oneOf" | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: entropyEncoding is a required property | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should be equal to one of the allowed values in ["HIGH","HIGH_10BIT","HIGH_422","HIGH_422_10BIT","MAIN"]
```

**Affected Files:** 1002, 108, 112, 113, 114, 443, 577, 58, 59, 60, 61, 915, 916, 919, 958, 959, 961, 962

### 2. Error Type (14 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 720
```

**Affected Files:** 1042, 802, 803, 804, 805, 806, 821, 822, 823, 826, 834, 835, 836, 852

### 3. Error Type (11 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should match all dependencies: See other errors for more details | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: Should match exactly one schema defined in "oneOf" | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/entropyEncoding: Must be CAVLC | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should be equal to one of the allowed values in ["HIGH","HIGH_10BIT","HIGH_422","HIGH_422_10BIT","MAIN"]
```

**Affected Files:** 1058, 238, 460, 695, 824, 837, 85, 86, 87, 88, 89

### 4. Error Type (8 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 1808
```

**Affected Files:** 772, 80, 808, 816, 857, 861, 874, 887

### 5. Error Type (4 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 752
```

**Affected Files:** 1061, 341, 465, 82

### 6. Error Type (4 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 576
```

**Affected Files:** 342, 776, 807, 81

### 7. Error Type (3 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 832
```

**Affected Files:** 435, 596, 849

### 8. Error Type (3 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: Your job contains values for the following settings that are incompatible: Rate control mode, Bitrate, and Max bitrate. Adjust your settings and resubmit your job. Some valid combinations of settings are these: Set Rate control mode to QVBR, specify a value for Max bitrate, and don't specify a value for Bitrate. Or, set Rate control mode to CBR, specify a value for Bitrate, and don't specify a value for Max bitrate.
```

**Affected Files:** 521, 522, 523

### 9. Error Type (2 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/audioDescriptions/0/codecSettings/aacSettings/bitrate: You specified a value for Bitrate that is not valid with the combination of Profile LC, Coding mode CODING_MODE_2_0, and Sample rate 48000 you selected. Specify a bitrate in the range of 64000-576000, and resubmit your job For a list of supported bitrates, see: https://docs.aws.amazon.com/mediaconvert/latest/ug/aac-support.html
```

**Affected Files:** 1014, 920

### 10. Error Type (2 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/audioDescriptions/0/codecSettings/aacSettings/bitrate: You specified a value for Bitrate that is not valid with the combination of Profile LC, Coding mode CODING_MODE_2_0, and Sample rate 44100 you selected. Specify a bitrate in the range of 64000-512000, and resubmit your job For a list of supported bitrates, see: https://docs.aws.amazon.com/mediaconvert/latest/ug/aac-support.html
```

**Affected Files:** 578, 579

### 11. Error Type (1 occurrences)

**Error Message:**
```
No audio frames decoded on [selector-(Audio Selector 1)-track-1-drc]
```

**Affected Files:** 110

### 12. Error Type (1 occurrences)

**Error Message:**
```
Invalid resolution [912 x 513], only even values are supported. video_description [1]. For 111_881430577_source.mpg
```

**Affected Files:** 111

### 13. Error Type (1 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/audioDescriptions/0/codecSettings/aacSettings: sampleRate is a required property
```

**Affected Files:** 430

### 14. Error Type (1 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 1200
```

**Affected Files:** 434

### 15. Error Type (1 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/maxBitrate: Should be less than or equal to 16800000
```

**Affected Files:** 437

### 16. Error Type (1 occurrences)

**Error Message:**
```
Error initializing encoder for video target [1] [initialization failed: Invalid level specified for the selected buffer size.]
```

**Affected Files:** 440

### 17. Error Type (1 occurrences)

**Error Message:**
```
Demuxer: [ReadPacketData File read failed - end of file hit at length [1257472]. Is file truncated?]
```

**Affected Files:** 482

### 18. Error Type (1 occurrences)

**Error Message:**
```
Unable to open input file [s3://fw-mc-test/mp4/540/540_882779581_source.mp4]: [Failed probe/open: [no moov box found in file]]
```

**Affected Files:** 540

### 19. Error Type (1 occurrences)

**Error Message:**
```
Unable to open input file [s3://fw-mc-test/mp4/541/541_882418980_source.mp4]: [Failed probe/open: [no moov box found in file]]
```

**Affected Files:** 541

### 20. Error Type (1 occurrences)

**Error Message:**
```
Demuxer: [ReadPacketData File read failed - end of file hit at length [1212416]. Is file truncated?]
```

**Affected Files:** 559

### 21. Error Type (1 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/captionDescriptions/0/destinationSettings/burninDestinationSettings: Should match all dependencies: See other errors for more details | /outputGroups/0/outputs/0/captionDescriptions/0/destinationSettings/destinationType: Must be BURN_IN
```

**Affected Files:** 913

### 22. Error Type (1 occurrences)

**Error Message:**
```
Demuxer: [ReadPacketData File read failed - end of file hit at length [96256]. Is file truncated?]
```

**Affected Files:** 975

### 23. Error Type (1 occurrences)

**Error Message:**
```
Error initializing encoder for video target [1] [initialization failed: Invalid level specified for the selected resolution.]
```

**Affected Files:** 977


## Statistics

- Total unique error messages: 23
- Total error occurrences: 82
