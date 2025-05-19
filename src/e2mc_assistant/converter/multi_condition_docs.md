# 多条件判断功能

## 概述

多条件判断功能允许在规则中使用复合逻辑条件，支持 AND、OR、NOT 逻辑运算符，可以组合多个简单条件来表达复杂的判断逻辑。

## 条件结构

### 基本条件结构

```yaml
condition:
  operator: "eq"  # 操作符
  value: "mp4"    # 比较值
  source_path: "output"  # 可选，从其他路径获取值
```

### 复合条件结构

#### AND 条件

当所有子条件都为真时，整个条件为真。

```yaml
condition:
  operator: "AND"
  conditions:
    - operator: "eq"
      value: "no"
    - operator: "exists"
      source_path: "cabr"
```

#### OR 条件

当任一子条件为真时，整个条件为真。

```yaml
condition:
  operator: "OR"
  conditions:
    - operator: "eq"
      value: "yes"
    - operator: "eq"
      source_path: "cabr"
      value: "yes"
```

#### NOT 条件

对单个条件取反。

```yaml
condition:
  operator: "NOT"
  condition:
    operator: "eq"
    value: "mp4"
```

## 嵌套条件

条件可以任意嵌套，构建复杂的逻辑表达式。

```yaml
condition:
  operator: "AND"
  conditions:
    - operator: "eq"
      value: "no"
    - operator: "OR"
      conditions:
        - operator: "exists"
          source_path: "cabr"
        - operator: "eq"
          source_path: "acbr"
          value: "no"
```

## 实际应用示例

### 示例1: CBR 设置条件

当 `cbr=no` 且 `cabr` 参数存在且等于 `no` 时，设置特定的码率控制模式。

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
    value: "QVBR_WITH_CABR"
```

### 示例2: 输出格式条件

当输出格式不是 `mp4` 时，设置不同的输出组类型。

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

### 示例3: 复杂编码设置

当满足多个编码参数条件时，应用特定的编码配置。

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
  target:
    path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.CodecProfile"
    value: "HIGH"
```

## 最佳实践

1. **条件组织**
   - 将简单条件放在复合条件的开始位置，以便快速评估
   - 使用嵌套结构表达复杂逻辑，提高可读性

2. **字符串值**
   - 在YAML中使用引号包围字符串值，避免解析问题
   - 例如：`value: "no"` 而不是 `value: no`

3. **条件调试**
   - 使用 `--verbose` 参数查看详细的条件评估日志
   - 检查条件评估结果，确保逻辑正确

4. **避免过度复杂**
   - 过于复杂的条件难以维护，考虑拆分为多个规则
   - 保持条件嵌套层级不超过3层
