# Encoding.com 到 AWS MediaConvert 配置转换工具文档

## 目录

1. [工具概述](#1-工具概述)
2. [转换程序详解](#2-转换程序详解)
3. [映射规则文件详解](#3-映射规则文件详解)
4. [使用方法](#4-使用方法)
5. [规则编写指南](#5-规则编写指南)
6. [扩展功能](#6-扩展功能)
7. [故障排除](#7-故障排除)
8. [示例](#8-示例)

## 1. 工具概述

该工具用于将 Encoding.com 的 XML 配置文件转换为 AWS MediaConvert 的 JSON 配置文件。工具支持单输出配置（如 MP4）和多流配置（如 HLS、DASH），并通过可配置的映射规则实现灵活的转换逻辑。

### 主要功能

- 解析 Encoding.com XML 配置文件
- 应用映射规则进行转换
- 生成 AWS MediaConvert JSON 配置文件
- 支持批量处理多个文件
- 记录未映射的参数
- 支持模板文件
- 支持迭代规则处理多流配置

## 2. 转换程序详解

### 2.1 核心组件

#### 2.1.1 ConfigConverter 类

主要转换引擎，负责解析配置文件、应用规则和生成输出。

```python
class ConfigConverter:
    def __init__(self, rules_file: str):
        """初始化转换器，加载规则文件"""
        # 加载规则文件
        # 注册内置函数
        
    def parse_xml(self, xml_file: str) -> Dict:
        """解析 Encoding.com XML 配置文件"""
        # 特殊处理 stream 元素
        
    def convert(self, source_file: str, template_file: str = None) -> Dict:
        """执行配置转换"""
        # 解析源文件
        # 加载模板（如果提供）
        # 应用映射规则
        # 记录未映射参数
```

#### 2.1.2 路径处理

```python
def get_value_by_path(self, data: Dict, path: str) -> Any:
    """根据路径获取字典中的值"""
    # 使用 / 分隔路径部分
    
def set_value_by_path(self, data: Dict, path: str, value: Any) -> None:
    """根据路径设置字典中的值"""
    # 处理数组索引，如 OutputGroups[0]
```

#### 2.1.3 转换函数

```python
def apply_transform(self, value: Any, transform_name: str, context: Dict = None) -> Any:
    """应用转换函数"""
    # 检查自定义函数
    # 检查预定义转换映射
```

#### 2.1.4 条件评估

```python
def evaluate_condition(self, condition: Dict, source_value: Any, source_data: Dict = None) -> bool:
    """评估条件"""
    # 支持多种操作符：eq, ne, gt, lt, in 等
```

#### 2.1.5 迭代规则处理

```python
def _process_iteration_rule(self, rule: Dict, source_data: Dict, target_data: Dict):
    """处理迭代规则，用于数组元素如 streams"""
    # 处理每个源元素
    # 应用子规则
    # 生成名称修饰符
```

#### 2.1.6 流处理

```python
def _process_streams(self, streams: List, context: Dict) -> List:
    """处理多流配置（HLS/DASH）"""
    # 创建输出模板
    # 处理每个流
    # 设置视频/音频参数
```

#### 2.1.7 未映射参数记录

```python
def _log_unmapped_parameters(self, source_data: Dict, processed_params: set, parent_path: str = ""):
    """记录没有映射规则的参数"""
    # 递归检查未处理的参数
```

### 2.2 命令行接口

```python
def main():
    """命令行入口点"""
    # 解析命令行参数
    # 设置日志级别
    # 执行转换
```

### 2.3 批量处理

```python
def batch_convert(converter: ConfigConverter, source_dir: str, output_dir: str, template_file: str = None):
    """批量转换目录中的所有 XML 文件"""
    # 支持 .format.xml 和 .xml 格式
    # 自动查找匹配的模板文件
```

## 3. 映射规则文件详解

映射规则文件使用 YAML 格式定义如何将 Encoding.com 配置转换为 MediaConvert 配置。

### 3.1 规则文件结构

规则文件使用YAML格式，主要包含两个顶级部分：
- `rules`: 定义转换规则列表
- `transformers`: 定义值转换映射

```yaml
rules:
  - source: {...}
    target: {...}
  # 更多规则...

transformers:
  transformer1: {...}
  transformer2: {...}
  # 更多转换器...
```

### 3.2 规则字段详解

每条规则由`source`和`target`两部分组成，分别定义源配置和目标配置的映射关系。

#### 3.2.1 source 字段

`source`定义从Encoding.com配置中提取值的方式。

| 字段 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `path` | 字符串 | 是 | 源配置中的路径，使用`/`分隔层级 | `"output"`, `"video_codec_parameters/level"` |
| `type` | 字符串 | 否 | 数据类型，可选值：`string`, `number`, `array`, `iteration` | `"string"` |
| `default` | 任意 | 否 | 当源值不存在时使用的默认值 | `"mp4"`, `30` |
| `regex` | 字符串 | 否 | 用于提取值的正则表达式 | `"(\\d+)x(\\d+)"` |
| `condition` | 对象 | 否 | 应用规则的条件 | `{"operator": "eq", "value": "mp4"}` |
| `rules` | 数组 | 仅迭代类型 | 迭代规则的子规则列表 | `[{source: {...}, target: {...}}]` |

##### condition 子字段

| 字段 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `operator` | 字符串 | 是 | 条件操作符 | `"eq"`, `"ne"`, `"in"` |
| `value` | 任意 | 是 | 比较值 | `"mp4"`, `1`, `["advanced_hls", "advanced_dash"]` |
| `source_path` | 字符串 | 否 | 用于获取比较值的源路径 | `"output"` |

#### 3.2.2 target 字段

`target`定义如何将提取的值映射到MediaConvert配置中。

| 字段 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `path` | 字符串 | 是 | 目标配置中的路径，使用`.`分隔层级 | `"Settings.OutputGroups[0].OutputGroupSettings.Type"` |
| `value` | 任意 | 否 | 静态值或模板（使用`$1`, `$2`等引用正则捕获组） | `"MP4"`, `"$1000"` |
| `transform` | 字符串 | 否 | 要应用的转换函数名称 | `"video_codec_format"` |
| `condition` | 对象 | 否 | 应用目标映射的条件 | `{"source_path": "output", "operator": "eq", "value": "mp4"}` |

#### 3.2.3 迭代规则特有字段

| 字段 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `target_base_path` | 字符串 | 是 | 目标数组的基础路径 | `"Settings.OutputGroups[0].Outputs"` |
| `name_modifier` | 对象 | 否 | 名称修饰符配置 | `{"template": "_{size}_{bitrate}", "replacements": {...}}` |

##### name_modifier 子字段

| 字段 | 类型 | 必填 | 描述 | 示例 |
|------|------|------|------|------|
| `template` | 字符串 | 是 | 名称模板，使用`{变量名}`引用源值 | `"_{size}_{bitrate}"` |
| `replacements` | 对象 | 否 | 变量替换规则 | `{"bitrate": {"regex": "(\\d+)k", "format": "$1K"}}` |

#### 3.2.4 transformers 字段

`transformers`定义值转换映射，将源值转换为目标值。

```yaml
transformers:
  transformer_name:
    "source_value1": "target_value1"
    "source_value2": "target_value2"
```

### 3.3 规则类型

#### 3.3.1 基本规则

```yaml
- source:
    path: "output"              # 源路径
    type: "string"              # 数据类型
    default: "mp4"              # 默认值
  target:
    path: "Settings.OutputGroups[0].OutputGroupSettings.Type"  # 目标路径
    transform: "output_group_type"  # 转换函数
```

#### 3.3.2 条件规则

```yaml
- source:
    path: "output"
    type: "string"
    condition:                  # 源条件
      operator: "eq"
      value: "mp4"
  target:
    path: "Settings.OutputGroups[0].Outputs[0].ContainerSettings.Container"
    value: "MP4"                # 静态值
    condition:                  # 目标条件
      source_path: "output"
      operator: "eq"
      value: "mp4"
```

#### 3.3.3 正则表达式规则

```yaml
- source:
    path: "size"
    type: "string"
    regex: "(\\d+)x(\\d+)"      # 正则表达式
  target:
    - path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.Width"
      value: "$1"               # 使用正则捕获组
    - path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.Height"
      value: "$2"
```

#### 3.3.4 迭代规则

```yaml
- source:
    path: "stream"
    type: "iteration"
    rules:                      # 子规则列表
      - source:
          path: "size"
          type: "string"
          regex: "(\\d+)x(\\d+)"
        target:
          - path: "VideoDescription.Width"
            value: "$1"
          - path: "VideoDescription.Height"
            value: "$2"
      # 更多子规则...
  target_base_path: "Settings.OutputGroups[0].Outputs"  # 目标基础路径
  name_modifier:                # 名称修饰符配置
    template: "_{size}_{bitrate}"
    replacements:
      "bitrate": 
        regex: "(\\d+)k"
        format: "$1K"
```

### 3.4 条件操作符

| 操作符 | 描述 | 示例 |
|--------|------|------|
| `eq` | 等于 | `{"operator": "eq", "value": "mp4"}` |
| `ne` | 不等于 | `{"operator": "ne", "value": "mp4"}` |
| `gt` | 大于 | `{"operator": "gt", "value": 30}` |
| `lt` | 小于 | `{"operator": "lt", "value": 60}` |
| `gte` | 大于等于 | `{"operator": "gte", "value": 25}` |
| `lte` | 小于等于 | `{"operator": "lte", "value": 30}` |
| `in` | 包含于 | `{"operator": "in", "value": ["mp4", "mov"]}` |
| `contains` | 包含 | `{"operator": "contains", "value": "264"}` |
| `exists` | 存在 | `{"operator": "exists"}` |

### 3.5 常用转换函数

| 转换函数 | 描述 | 示例映射 |
|----------|------|----------|
| `output_group_type` | 输出组类型转换 | `"mp4": "FILE_GROUP_SETTINGS"` |
| `container_format` | 容器格式转换 | `"mp4": "MP4"` |
| `video_codec_format` | 视频编解码器转换 | `"libx264": "H_264"` |
| `audio_codec_format` | 音频编解码器转换 | `"libfaac": "AAC"` |
| `rate_control_mode` | 码率控制模式转换 | `"yes": "CBR", "no": "QVBR"` |
| `profile_format` | 编码配置文件转换 | `"main": "MAIN"` |
| `h264_level_format` | H.264级别转换 | `"42": "LEVEL_4_2"` |

## 4. 使用方法

### 4.1 基本用法

```bash
python config_converter.py --source input.xml --rules mapping_rules.yaml --output output.json
```

### 4.2 使用模板

```bash
python config_converter.py --source input.xml --rules mapping_rules.yaml --template template.json --output output.json
```

### 4.3 批量处理

```bash
python config_converter.py --source /path/to/xml/files --rules mapping_rules.yaml --output /path/to/output --batch
```

### 4.4 详细日志

```bash
python config_converter.py --source input.xml --rules mapping_rules.yaml --output output.json --verbose
```

### 4.5 命令行参数

| 参数 | 描述 | 示例 |
|------|------|------|
| `--source` | 源配置文件（XML）或目录 | `--source input.xml` |
| `--rules` | 映射规则文件（YAML） | `--rules mapping_rules.yaml` |
| `--template` | 模板MediaConvert文件（JSON） | `--template template.json` |
| `--output` | 输出文件路径或目录 | `--output output.json` |
| `--batch` | 批量处理源目录中的所有XML文件 | `--batch` |
| `--validate` | JSON Schema验证文件 | `--validate schema.json` |
| `--verbose` | 启用详细日志记录 | `--verbose` |

## 5. 规则编写指南

### 5.1 路径表示法

- 源路径使用斜杠（/）分隔，如 `format/video_codec`
- 目标路径使用点（.）分隔，如 `Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.Codec`
- 数组索引使用方括号，如 `OutputGroups[0]`

### 5.2 条件规则编写

1. **基于输出格式的条件**

```yaml
- source:
    path: "output"
    type: "string"
    condition:
      operator: "eq"
      value: "mp4"
  target:
    path: "Settings.OutputGroups[0].Outputs[0].ContainerSettings.Container"
    value: "MP4"
```

2. **基于其他字段的条件**

```yaml
- source:
    path: "segment_duration"
    type: "number"
  target:
    path: "Settings.OutputGroups[0].OutputGroupSettings.HlsGroupSettings.SegmentLength"
    condition:
      source_path: "output"
      operator: "eq"
      value: "advanced_hls"
```

### 5.3 迭代规则编写

1. **定义迭代规则**

```yaml
- source:
    path: "stream"
    type: "iteration"
    rules:
      # 子规则列表...
  target_base_path: "Settings.OutputGroups[0].Outputs"
```

2. **子规则示例**

```yaml
rules:
  - source:
      path: "size"
      type: "string"
      regex: "(\\d+)x(\\d+)"
    target:
      - path: "VideoDescription.Width"
        value: "$1"
      - path: "VideoDescription.Height"
        value: "$2"
```

3. **名称修饰符配置**

```yaml
name_modifier:
  template: "_{size}_{bitrate}"
  replacements:
    "bitrate": 
      regex: "(\\d+)k"
      format: "$1K"
```

### 5.4 最佳实践

1. **路径命名**
   - 源路径使用斜杠（/）分隔
   - 目标路径使用点（.）分隔
   - 数组索引使用方括号，如`[0]`

2. **条件使用**
   - 为不同输出格式创建条件规则
   - 使用`source_path`引用其他字段值
   - 组合多个条件处理复杂场景

3. **默认值**
   - 为重要参数提供默认值
   - 确保生成的配置完整有效

4. **迭代规则**
   - 使用相对路径简化子规则
   - 为每个流生成唯一的名称修饰符
   - 处理音频流和视频流的特殊情况

5. **转换函数**
   - 集中定义常用的值转换
   - 使用转换函数处理格式差异
   - 为复杂转换注册自定义函数

## 6. 扩展功能

### 6.1 自定义转换函数

```python
def my_custom_transform(value, context):
    # 自定义转换逻辑
    return transformed_value

converter = ConfigConverter('mapping_rules.yaml')
converter.register_custom_function('my_transform', my_custom_transform)
```

### 6.2 验证功能

```python
def validate(self, data: Dict, schema_file: str = None) -> bool:
    """验证生成的配置是否符合要求"""
    # 使用 jsonschema 验证
```

### 6.3 未映射参数记录

工具会自动记录未映射的参数，以便后续完善规则：

```
WARNING - Unmapped parameter: turbo = yes
WARNING - Unmapped parameter: duration_precision = 3
WARNING - Unmapped parameter: pack_files = yes
```

## 7. 故障排除

### 7.1 常见问题

1. **未映射参数**：检查日志中的 "Unmapped parameter" 警告，添加相应的映射规则
2. **路径错误**：确保源路径和目标路径格式正确
3. **条件不匹配**：检查条件操作符和值是否正确
4. **类型转换错误**：确保数据类型兼容

### 7.2 调试技巧

1. 使用 `--verbose` 参数获取详细日志
2. 检查源数据结构是否符合预期
3. 验证转换函数是否正确定义
4. 检查条件评估结果

## 8. 示例

### 8.1 MP4 配置转换

**源配置 (1.format.xml)**:
```xml
<format>
    <output>mp4</output>
    <video_codec>libx264</video_codec>
    <framerate>25</framerate>
    <profile>main</profile>
    <bitrate>1300k</bitrate>
    <size>1024x576</size>
    <audio_codec>libfaac</audio_codec>
    <audio_bitrate>128k</audio_bitrate>
    <audio_sample_rate>48000</audio_sample_rate>
</format>
```

**映射规则**:
```yaml
# MP4 相关规则
- source:
    path: "output"
    type: "string"
    condition:
      operator: "eq"
      value: "mp4"
  target:
    path: "Settings.OutputGroups[0].Outputs[0].ContainerSettings.Container"
    value: "MP4"
```

**转换结果**:
```json
{
  "Settings": {
    "OutputGroups": [
      {
        "OutputGroupSettings": {
          "Type": "FILE_GROUP_SETTINGS"
        },
        "Outputs": [
          {
            "ContainerSettings": {
              "Container": "MP4"
            },
            "VideoDescription": {
              "CodecSettings": {
                "Codec": "H_264",
                "H264Settings": {
                  "FramerateNumerator": 25,
                  "Bitrate": 1300000
                }
              },
              "Width": 1024,
              "Height": 576
            },
            "AudioDescriptions": [
              {
                "CodecSettings": {
                  "Codec": "AAC",
                  "AacSettings": {
                    "Bitrate": 128000,
                    "SampleRate": 48000
                  }
                }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 8.2 HLS 配置转换

**源配置 (2.format.xml)**:
```xml
<format>
    <output>advanced_hls</output>
    <stream>
        <size>320x180</size>
        <bitrate>180k</bitrate>
        <framerate>30</framerate>
        <audio_bitrate>96k</audio_bitrate>
    </stream>
    <stream>
        <size>640x360</size>
        <bitrate>675k</bitrate>
        <framerate>30</framerate>
        <audio_bitrate>96k</audio_bitrate>
    </stream>
    <segment_duration>2</segment_duration>
</format>
```

**映射规则**:
```yaml
# 迭代规则处理多流
- source:
    path: "stream"
    type: "iteration"
    rules:
      - source:
          path: "size"
          type: "string"
          regex: "(\\d+)x(\\d+)"
        target:
          - path: "VideoDescription.Width"
            value: "$1"
          - path: "VideoDescription.Height"
            value: "$2"
      - source:
          path: "bitrate"
          type: "string"
          regex: "(\\d+)k"
        target:
          path: "VideoDescription.CodecSettings.H264Settings.Bitrate"
          value: "$1000"
  target_base_path: "Settings.OutputGroups[0].Outputs"
```

**转换结果**:
```json
{
  "Settings": {
    "OutputGroups": [
      {
        "OutputGroupSettings": {
          "Type": "HLS_GROUP_SETTINGS",
          "HlsGroupSettings": {
            "SegmentLength": 2
          }
        },
        "Outputs": [
          {
            "VideoDescription": {
              "Width": 320,
              "Height": 180,
              "CodecSettings": {
                "H264Settings": {
                  "Bitrate": 180000,
                  "FramerateNumerator": 30
                },
                "Codec": "H_264"
              }
            },
            "NameModifier": "_320x180_180K"
          },
          {
            "VideoDescription": {
              "Width": 640,
              "Height": 360,
              "CodecSettings": {
                "H264Settings": {
                  "Bitrate": 675000,
                  "FramerateNumerator": 30
                },
                "Codec": "H_264"
              }
            },
            "NameModifier": "_640x360_675K"
          }
        ]
      }
    ]
  }
}
```

### 8.3 嵌套参数处理

**源配置**:
```xml
<format>
    <output>mp4</output>
    <video_codec_parameters>
        <color_range>1</color_range>
        <level>42</level>
    </video_codec_parameters>
</format>
```

**映射规则**:
```yaml
# 处理嵌套参数
- source:
    path: "video_codec_parameters/level"
    type: "number"
  target:
    path: "Settings.OutputGroups[0].Outputs[0].VideoDescription.CodecSettings.H264Settings.Level"
    transform: "h264_level_format"
```

**转换结果**:
```json
{
  "Settings": {
    "OutputGroups": [
      {
        "Outputs": [
          {
            "VideoDescription": {
              "CodecSettings": {
                "H264Settings": {
                  "Level": "LEVEL_4_2"
                }
              }
            }
          }
        ]
      }
    ]
  }
}
```

## 总结

该转换工具通过可配置的映射规则实现了 Encoding.com 配置到 AWS MediaConvert 配置的灵活转换。核心功能包括：

1. 基于路径的值映射
2. 条件规则处理
3. 值转换和格式化
4. 多流配置处理
5. 迭代规则支持
6. 未映射参数记录

通过这些功能，工具可以处理各种复杂的转码配置，并生成符合 AWS MediaConvert 要求的 JSON 配置文件。
