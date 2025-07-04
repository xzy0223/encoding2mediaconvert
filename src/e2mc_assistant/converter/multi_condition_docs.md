# 🔀 Multi-Condition Logic - Advanced Rule Configuration

[![YAML](https://img.shields.io/badge/config-YAML-red.svg)](https://yaml.org)
[![Logic](https://img.shields.io/badge/logic-AND%2FOR%2FNOT-blue.svg)](#)

The **Multi-Condition Logic** system enables sophisticated rule evaluation using compound logical conditions with AND, OR, and NOT operators, allowing complex decision-making in configuration conversion rules.

---

## 🌟 Overview

Multi-condition functionality allows rules to use compound logical conditions, supporting AND, OR, and NOT logical operators. You can combine multiple simple conditions to express complex judgment logic, enabling precise control over when rules are applied during the conversion process.

---

## 🏗️ Condition Structure

### Basic Condition Structure

```yaml
condition:
  operator: "eq"              # Comparison operator
  value: "mp4"               # Comparison value
  source_path: "output"      # Optional: get value from another path
```

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equal to | `operator: "eq", value: "mp4"` |
| `ne` | Not equal to | `operator: "ne", value: "flv"` |
| `in` | Value in list | `operator: "in", value: ["mp4", "mov"]` |
| `exists` | Parameter exists | `operator: "exists", source_path: "maxrate"` |
| `gt` | Greater than | `operator: "gt", value: 1000` |
| `gte` | Greater than or equal | `operator: "gte", value: 30` |
| `lt` | Less than | `operator: "lt", value: 8192` |
| `lte` | Less than or equal | `operator: "lte", value: 60` |

---

## 🔗 Compound Condition Structure

### AND Conditions

All sub-conditions must be true for the entire condition to be true.

```yaml
condition:
  operator: "AND"
  conditions:
    - operator: "eq"
      value: "no"
    - operator: "exists"
      source_path: "cabr"
    - operator: "ne"
      source_path: "video_codec"
      value: "copy"
```

### OR Conditions

Any sub-condition being true makes the entire condition true.

```yaml
condition:
  operator: "OR"
  conditions:
    - operator: "eq"
      value: "yes"
    - operator: "eq"
      source_path: "cabr"
      value: "yes"
    - operator: "exists"
      source_path: "maxrate"
```

### NOT Conditions

Negates a single condition.

```yaml
condition:
  operator: "NOT"
  condition:
    operator: "eq"
    value: "mp4"
```

---

## 🎯 Nested Conditions

Conditions can be arbitrarily nested to build complex logical expressions with unlimited depth.

### Complex Nested Example

```yaml
condition:
  operator: "AND"
  conditions:
    - operator: "eq"
      value: "no"
    - operator: "OR"
      conditions:
        - operator: "AND"
          conditions:
            - operator: "exists"
              source_path: "cabr"
            - operator: "eq"
              source_path: "cabr"
              value: "no"
        - operator: "eq"
          source_path: "acbr"
          value: "no"
    - operator: "NOT"
      condition:
        operator: "eq"
        source_path: "video_codec"
        value: "copy"
```

This translates to the logical expression:
```
(cbr == "no") AND 
((cabr exists AND cabr == "no") OR (acbr == "no")) AND 
NOT(video_codec == "copy")
```

---

## 📊 Real-World Examples

### Example 1: CBR Rate Control Configuration

Apply specific rate control mode when `cbr=no` and `cabr` parameter exists and equals `no`.

```yaml
- source:
    path: "cbr"
    condition:
      operator: "AND"
      conditions:
        - operator: "eq"
          value: "no"
        - operator: "AND"
          conditions:
            - operator: "exists"
              source_path: "cabr"
            - operator: "eq"
              source_path: "cabr"
              value: "no"
  target:
    path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.RateControlMode"
    value: "QVBR"
```

### Example 2: Output Format Conditional Logic

Set different output group types when output format is not MP4.

```yaml
- source:
    path: "output"
    condition:
      operator: "NOT"
      condition:
        operator: "eq"
        value: "mp4"
  target:
    path: "Settings.OutputGroups[0].OutputGroupSettings.Type"
    value: "HLS_GROUP_SETTINGS"
```

### Example 3: Complex Encoding Configuration

Apply specific encoding configuration when multiple encoding parameters meet certain conditions.

```yaml
- source:
    path: "video_codec"
    condition:
      operator: "AND"
      conditions:
        - operator: "eq"
          value: "libx264"
        - operator: "OR"
          conditions:
            - operator: "eq"
              source_path: "profile"
              value: "high"
            - operator: "eq"
              source_path: "profile"
              value: "main"
        - operator: "exists"
          source_path: "level"
        - operator: "NOT"
          condition:
            operator: "eq"
            source_path: "preset"
            value: "ultrafast"
  target:
    path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.CodecProfile"
    value: "HIGH"
```

### Example 4: Streaming-Specific Conditions

Configure streaming settings based on multiple parameters.

```yaml
- source:
    path: "segment_seconds"
    condition:
      operator: "AND"
      conditions:
        - operator: "in"
          source_path: "output"
          value: ["advanced_hls", "mpeg_dash"]
        - operator: "OR"
          conditions:
            - operator: "gte"
              value: 2
            - operator: "exists"
              source_path: "keyframe_interval"
        - operator: "NOT"
          condition:
            operator: "eq"
            source_path: "live_stream"
            value: "yes"
  target:
    path: "Settings.OutputGroups[0].OutputGroupSettings.HlsGroupSettings.SegmentLength"
    value: 6
```

---

## 🎨 Advanced Patterns

### Conditional Transformations

Use conditions to apply different transformations based on context.

```yaml
# High bitrate for high resolution
- source:
    path: "bitrate"
    type: "string"
    regex: "(\\d+)k"
    condition:
      operator: "AND"
      conditions:
        - operator: "exists"
          source_path: "size"
        - operator: "OR"
          conditions:
            - operator: "eq"
              source_path: "size"
              value: "1920x1080"
            - operator: "eq"
              source_path: "size"
              value: "3840x2160"
  target:
    path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.Bitrate"
    value: "$1000"

# Standard bitrate for lower resolution
- source:
    path: "bitrate"
    type: "string"
    regex: "(\\d+)k"
    condition:
      operator: "AND"
      conditions:
        - operator: "exists"
          source_path: "size"
        - operator: "NOT"
          condition:
            operator: "OR"
            conditions:
              - operator: "eq"
                source_path: "size"
                value: "1920x1080"
              - operator: "eq"
                source_path: "size"
                value: "3840x2160"
  target:
    path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.Bitrate"
    value: "$1500"  # Higher multiplier for lower resolution
```

### Multi-Output Conditions

Configure different outputs based on complex conditions.

```yaml
# Primary output for high quality
- source:
    path: "quality"
    condition:
      operator: "AND"
      conditions:
        - operator: "eq"
          value: "high"
        - operator: "exists"
          source_path: "bitrate"
        - operator: "gte"
          source_path: "bitrate"
          value: "2000k"
  target:
    - path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.QualityTuningLevel"
      value: "MULTI_PASS_HQ"
    - path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.RateControlMode"
      value: "VBR"

# Secondary output for standard quality
- source:
    path: "quality"
    condition:
      operator: "OR"
      conditions:
        - operator: "eq"
          value: "standard"
        - operator: "AND"
          conditions:
            - operator: "eq"
              value: "high"
            - operator: "lt"
              source_path: "bitrate"
              value: "2000k"
  target:
    - path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.QualityTuningLevel"
      value: "SINGLE_PASS"
    - path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.RateControlMode"
      value: "CBR"
```

---

## 🔍 Debugging Multi-Conditions

### Verbose Logging

Enable verbose logging to see detailed condition evaluation:

```bash
e2mc-converter \
  --source input.xml \
  --rules rules.yaml \
  --output output.json \
  --verbose
```

### Condition Evaluation Log Example

```
[DEBUG] Evaluating condition for rule 'cbr_rate_control':
[DEBUG]   AND condition with 2 sub-conditions:
[DEBUG]     1. eq: cbr == "no" → TRUE
[DEBUG]     2. AND condition with 2 sub-conditions:
[DEBUG]       2.1. exists: cabr → TRUE (value: "no")
[DEBUG]       2.2. eq: cabr == "no" → TRUE
[DEBUG]   Final result: TRUE
[DEBUG] Rule 'cbr_rate_control' applied successfully
```

### Testing Conditions

Create test cases for complex conditions:

```python
# Test condition evaluation
from e2mc_assistant.converter import ConfigConverter

converter = ConfigConverter('rules.yaml')

# Test data
test_config = {
    'cbr': 'no',
    'cabr': 'no',
    'video_codec': 'libx264',
    'profile': 'high'
}

# Evaluate specific rule
rule_result = converter.evaluate_rule_condition(
    rule_name='cbr_rate_control',
    config_data=test_config
)

print(f"Rule condition result: {rule_result}")
```

---

## 🎓 Best Practices

### 1. Condition Organization

```yaml
# ✅ Good: Simple conditions first for fast evaluation
condition:
  operator: "AND"
  conditions:
    - operator: "eq"          # Simple equality check first
      value: "mp4"
    - operator: "exists"      # Existence check second
      source_path: "bitrate"
    - operator: "OR"          # Complex OR condition last
      conditions:
        - operator: "gte"
          source_path: "bitrate"
          value: "1000k"
        - operator: "exists"
          source_path: "maxrate"
```

### 2. String Value Handling

```yaml
# ✅ Good: Always quote string values in YAML
condition:
  operator: "eq"
  value: "no"              # Quoted string

# ❌ Bad: Unquoted values can cause parsing issues
condition:
  operator: "eq"
  value: no                # May be interpreted as boolean
```

### 3. Readability and Maintainability

```yaml
# ✅ Good: Well-structured with clear logic
condition:
  operator: "AND"
  conditions:
    # Check if CBR is disabled
    - operator: "eq"
      value: "no"
    # Ensure CABR parameter exists and is configured
    - operator: "AND"
      conditions:
        - operator: "exists"
          source_path: "cabr"
        - operator: "eq"
          source_path: "cabr"
          value: "no"

# ❌ Bad: Overly complex nesting
condition:
  operator: "AND"
  conditions:
    - operator: "OR"
      conditions:
        - operator: "AND"
          conditions:
            - operator: "NOT"
              condition:
                operator: "OR"
                conditions:
                  # ... deeply nested conditions
```

### 4. Performance Optimization

```yaml
# ✅ Good: Most selective conditions first
condition:
  operator: "AND"
  conditions:
    - operator: "eq"          # Most selective first
      source_path: "output"
      value: "advanced_hls"
    - operator: "exists"      # Less selective second
      source_path: "segment_seconds"
    - operator: "gte"         # Least selective last
      source_path: "bitrate"
      value: "1000k"
```

### 5. Error Prevention

```yaml
# ✅ Good: Check existence before value comparison
condition:
  operator: "AND"
  conditions:
    - operator: "exists"      # Check existence first
      source_path: "cabr"
    - operator: "eq"          # Then check value
      source_path: "cabr"
      value: "no"

# ❌ Bad: May cause errors if parameter doesn't exist
condition:
  operator: "eq"
  source_path: "cabr"        # May not exist
  value: "no"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **Condition Never Matches**

```yaml
# Problem: Incorrect operator or value
condition:
  operator: "eq"
  value: no                  # Should be "no" (string)

# Solution: Use correct data types
condition:
  operator: "eq"
  value: "no"               # Correct string value
```

#### 2. **Parameter Not Found Errors**

```yaml
# Problem: Referencing non-existent parameter
condition:
  operator: "eq"
  source_path: "non_existent_param"
  value: "value"

# Solution: Check existence first
condition:
  operator: "AND"
  conditions:
    - operator: "exists"
      source_path: "param_name"
    - operator: "eq"
      source_path: "param_name"
      value: "value"
```

#### 3. **Complex Condition Performance**

```yaml
# Problem: Inefficient condition ordering
condition:
  operator: "AND"
  conditions:
    - operator: "OR"          # Complex condition first (slow)
      conditions:
        # ... many sub-conditions
    - operator: "eq"          # Simple condition last
      value: "mp4"

# Solution: Reorder for efficiency
condition:
  operator: "AND"
  conditions:
    - operator: "eq"          # Simple condition first (fast)
      value: "mp4"
    - operator: "OR"          # Complex condition last
      conditions:
        # ... many sub-conditions
```

---

## 📚 Reference

### Condition Evaluation Order

1. **Simple operators** (`eq`, `ne`, `exists`) are evaluated first
2. **Comparison operators** (`gt`, `gte`, `lt`, `lte`) are evaluated second
3. **List operators** (`in`) are evaluated third
4. **Compound operators** (`AND`, `OR`, `NOT`) are evaluated last

### Performance Characteristics

| Operator | Performance | Notes |
|----------|-------------|-------|
| `eq`, `ne` | Fast | Direct value comparison |
| `exists` | Fast | Simple existence check |
| `gt`, `gte`, `lt`, `lte` | Medium | Numeric conversion required |
| `in` | Medium | List iteration required |
| `AND` | Variable | Short-circuits on first false |
| `OR` | Variable | Short-circuits on first true |
| `NOT` | Fast | Single condition negation |

---

## 📄 License

This documentation is part of E2MC Assistant and is licensed under the MIT License.
