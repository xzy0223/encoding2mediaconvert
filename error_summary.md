# Error Analysis Summary

## Top Error Messages

1. **Missing Required Audio Properties** (68 occurrences)
   - Missing `sampleRate` in AAC settings (36 occurrences)
   - Missing `codingMode` in AAC settings (32 occurrences)

2. **Invalid H264 Settings** (47 occurrences)
   - `numberBFramesBetweenReferenceFrames` exceeds maximum value of 7 (30 occurrences)
   - Invalid `codecProfile` values or missing required properties (17 occurrences)

3. **Missing Required Video Properties** (19 occurrences)
   - Missing `codec` property in video codec settings

4. **Incompatible Rate Control Settings** (4 occurrences)
   - Incompatible combination of rate control mode, bitrate, and max bitrate

5. **Resolution Constraints** (8 occurrences)
   - Width exceeds maximum allowed value (1808 or 576)

## Recommendations

1. **Fix Audio Settings**
   - Always include required `sampleRate` and `codingMode` properties in AAC settings
   - Example: `"AacSettings": {"SampleRate": 48000, "CodingMode": "CODING_MODE_2_0"}`

2. **Fix H264 Settings**
   - Ensure `numberBFramesBetweenReferenceFrames` is ≤ 7
   - Use valid codec profiles from the allowed list: "HIGH", "HIGH_10BIT", "HIGH_422", "HIGH_422_10BIT", "MAIN"
   - Include required properties like `entropyEncoding`

3. **Fix Rate Control Settings**
   - For CBR: Set `RateControlMode` to "CBR", specify `Bitrate`, don't set `MaxBitrate`
   - For QVBR: Set `RateControlMode` to "QVBR", specify `MaxBitrate`, don't set `Bitrate`

4. **Resolution Constraints**
   - Ensure width is within allowed limits (≤ 1808 or ≤ 576 depending on the context)

5. **General**
   - Always include required properties (`codec` in codec settings)
   - Validate job configurations before submission
