# Error Analysis Summary

## Error Messages with Associated File IDs

### 1. Error Type (36 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/audioDescriptions/0/codecSettings/aacSettings: sampleRate is a required property
```

**Affected Files:** 1059, 1060, 1061, 109, 110, 111, 159, 162, 164, 340, 341, 342, 365, 369, 429, 430, 434, 435, 463, 464, 465, 504, 505, 540, 541, 542, 559, 595, 596, 63, 697, 81, 82, 849, 850, 867

### 2. Error Type (32 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/audioDescriptions/0/codecSettings/aacSettings: codingMode is a required property
```

**Affected Files:** 1003, 1004, 1005, 1006, 1007, 1009, 1011, 1012, 1013, 1021, 1033, 1046, 1064, 143, 144, 145, 747, 920, 922, 923, 924, 926, 927, 934, 935, 937, 963, 965, 966, 967, 977, 981

### 3. Error Type (30 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/numberBFramesBetweenReferenceFrames: Should be less than or equal to 7
```

**Affected Files:** 1042, 13, 17, 19, 20, 23, 496, 50, 544, 688, 689, 690, 693, 802, 803, 804, 805, 806, 807, 808, 821, 822, 823, 826, 834, 835, 836, 852, 868, 913

### 4. Error Type (19 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings: codec is a required property
```

**Affected Files:** 1014, 1015, 1016, 1017, 1048, 1052, 526, 527, 528, 948, 949, 950, 951, 986, 987, 988, 989, 990, 991

### 5. Error Type (17 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should match all dependencies: See other errors for more details | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: Should match exactly one schema defined in "oneOf" | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: entropyEncoding is a required property | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should be equal to one of the allowed values in ["HIGH","HIGH_10BIT","HIGH_422","HIGH_422_10BIT","MAIN"]
```

**Affected Files:** 108, 112, 113, 114, 443, 577, 58, 59, 60, 61, 915, 916, 919, 958, 959, 961, 962

### 6. Error Type (11 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should match all dependencies: See other errors for more details | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: Should match exactly one schema defined in "oneOf" | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/entropyEncoding: Must be CAVLC | /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should be equal to one of the allowed values in ["HIGH","HIGH_10BIT","HIGH_422","HIGH_422_10BIT","MAIN"]
```

**Affected Files:** 1058, 238, 460, 695, 824, 837, 85, 86, 87, 88, 89

### 7. Error Type (7 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 1808
```

**Affected Files:** 772, 80, 816, 857, 861, 874, 887

### 8. Error Type (6 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: Should match all dependencies: See other errors for more details | /outputGroups/0/outputs/0/videoDescription/codecSettings/codec: Must be H_264
```

**Affected Files:** 1030, 1031, 957, 960, 964, 982

### 9. Error Type (4 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: Your job contains values for the following settings that are incompatible: Rate control mode, Bitrate, and Max bitrate. Adjust your settings and resubmit your job. Some valid combinations of settings are these: Set Rate control mode to QVBR, specify a value for Max bitrate, and don't specify a value for Bitrate. Or, set Rate control mode to CBR, specify a value for Bitrate, and don't specify a value for Max bitrate.
```

**Affected Files:** 521, 522, 523, 846

### 10. Error Type (3 occurrences)

**Error Message:**
```
Parameter validation failed:
```

**Affected Files:** 1002, 1008, 1010

### 11. Error Type (2 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/audioDescriptions/0/audioNormalizationSettings/targetLkfs: Should be less than or equal to 0
```

**Affected Files:** 578, 579

### 12. Error Type (2 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/audioDescriptions/0/codecSettings: Should have at most 2 properties
```

**Affected Files:** 723, 975

### 13. Error Type (1 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/maxBitrate: Should be less than or equal to 16800000
```

**Affected Files:** 437

### 14. Error Type (1 occurrences)

**Error Message:**
```
Error initializing encoder for video target [1] [initialization failed: Invalid level specified for the selected buffer size.]
```

**Affected Files:** 440

### 15. Error Type (1 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/audioDescriptions/0/codecSettings: codec is a required property
```

**Affected Files:** 683

### 16. Error Type (1 occurrences)

**Error Message:**
```
An error occurred (BadRequestException) when calling the CreateJob operation: /outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 576
```

**Affected Files:** 776


## Statistics

- Total unique error messages: 16
- Total error occurrences: 173
