# Error Analysis Summary by Category

## Audio Settings Issues

### Missing Required Audio Properties

1. **Missing `sampleRate` in AAC settings** (36 occurrences)
   - **Error:** `/outputGroups/0/outputs/0/audioDescriptions/0/codecSettings/aacSettings: sampleRate is a required property`
   - **Files:** 1059, 1060, 1061, 109, 110, 111, 159, 162, 164, 340, 341, 342, 365, 369, 429, 430, 434, 435, 463, 464, 465, 504, 505, 540, 541, 542, 559, 595, 596, 63, 697, 81, 82, 849, 850, 867

2. **Missing `codingMode` in AAC settings** (32 occurrences)
   - **Error:** `/outputGroups/0/outputs/0/audioDescriptions/0/codecSettings/aacSettings: codingMode is a required property`
   - **Files:** 1003, 1004, 1005, 1006, 1007, 1009, 1011, 1012, 1013, 1021, 1033, 1046, 1064, 143, 144, 145, 747, 920, 922, 923, 924, 926, 927, 934, 935, 937, 963, 965, 966, 967, 977, 981

3. **Missing `codec` in audio codec settings** (1 occurrence)
   - **Error:** `/outputGroups/0/outputs/0/audioDescriptions/0/codecSettings: codec is a required property`
   - **Files:** 683

4. **Audio normalization issues** (2 occurrences)
   - **Error:** `/outputGroups/0/outputs/0/audioDescriptions/0/audioNormalizationSettings/targetLkfs: Should be less than or equal to 0`
   - **Files:** 578, 579

5. **Too many properties in audio codec settings** (2 occurrences)
   - **Error:** `/outputGroups/0/outputs/0/audioDescriptions/0/codecSettings: Should have at most 2 properties`
   - **Files:** 723, 975

## Video Settings Issues

### H264 Configuration Issues

1. **B-frames limit exceeded** (30 occurrences)
   - **Error:** `/outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/numberBFramesBetweenReferenceFrames: Should be less than or equal to 7`
   - **Files:** 1042, 13, 17, 19, 20, 23, 496, 50, 544, 688, 689, 690, 693, 802, 803, 804, 805, 806, 807, 808, 821, 822, 823, 826, 834, 835, 836, 852, 868, 913

2. **Invalid codec profile or missing entropy encoding** (28 occurrences)
   - **Error Type 1:** `/outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should match all dependencies... entropyEncoding is a required property... Should be equal to one of the allowed values in ["HIGH","HIGH_10BIT","HIGH_422","HIGH_422_10BIT","MAIN"]`
   - **Files:** 108, 112, 113, 114, 443, 577, 58, 59, 60, 61, 915, 916, 919, 958, 959, 961, 962
   
   - **Error Type 2:** `/outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/codecProfile: Should match all dependencies... entropyEncoding: Must be CAVLC... Should be equal to one of the allowed values`
   - **Files:** 1058, 238, 460, 695, 824, 837, 85, 86, 87, 88, 89

3. **Missing required `codec` property** (19 occurrences)
   - **Error:** `/outputGroups/0/outputs/0/videoDescription/codecSettings: codec is a required property`
   - **Files:** 1014, 1015, 1016, 1017, 1048, 1052, 526, 527, 528, 948, 949, 950, 951, 986, 987, 988, 989, 990, 991

4. **Codec mismatch** (6 occurrences)
   - **Error:** `/outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings: Should match all dependencies... codec: Must be H_264`
   - **Files:** 1030, 1031, 957, 960, 964, 982

### Rate Control Issues

1. **Incompatible rate control settings** (4 occurrences)
   - **Error:** `Your job contains values for the following settings that are incompatible: Rate control mode, Bitrate, and Max bitrate.`
   - **Files:** 521, 522, 523, 846

2. **MaxBitrate exceeds limit** (1 occurrence)
   - **Error:** `/outputGroups/0/outputs/0/videoDescription/codecSettings/h264Settings/maxBitrate: Should be less than or equal to 16800000`
   - **Files:** 437

### Resolution Issues

1. **Width exceeds 1808 limit** (7 occurrences)
   - **Error:** `/outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 1808`
   - **Files:** 772, 80, 816, 857, 861, 874, 887

2. **Width exceeds 576 limit** (1 occurrence)
   - **Error:** `/outputGroups/0/outputs/0/videoDescription/width: Should be less than or equal to 576`
   - **Files:** 776

### Other Issues

1. **Encoder initialization failure** (1 occurrence)
   - **Error:** `Error initializing encoder for video target [1] [initialization failed: Invalid level specified for the selected buffer size.]`
   - **Files:** 440

2. **Parameter validation failure** (3 occurrences)
   - **Error:** `Parameter validation failed:`
   - **Files:** 1002, 1008, 1010

## Recommendations

### Audio Settings
1. Always include required `sampleRate` property in AAC settings (e.g., 48000)
2. Always include required `codingMode` property in AAC settings (e.g., "CODING_MODE_2_0" or "CODING_MODE_1_0")
3. Ensure `targetLkfs` values are ≤ 0 for audio normalization settings
4. Include required `codec` property in audio codec settings
5. Limit audio codec settings to at most 2 properties

### Video Settings
1. Ensure `numberBFramesBetweenReferenceFrames` is ≤ 7
2. Use valid codec profiles from the allowed list: "HIGH", "HIGH_10BIT", "HIGH_422", "HIGH_422_10BIT", "MAIN"
3. Include required `entropyEncoding` property (set to "CAVLC" when needed)
4. Always include required `codec` property in video codec settings
5. Ensure codec settings match the specified codec (e.g., H264Settings with codec="H_264")
6. Ensure width is within allowed limits (≤ 1808 or ≤ 576 depending on the context)
7. Ensure maxBitrate is ≤ 16800000

### Rate Control Settings
1. For CBR: Set `RateControlMode` to "CBR", specify `Bitrate`, don't set `MaxBitrate`
2. For QVBR: Set `RateControlMode` to "QVBR", specify `MaxBitrate`, don't set `Bitrate`
3. Don't mix incompatible rate control settings
