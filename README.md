# E2MC Assistant - Encoding.com to AWS MediaConvert Migration Toolkit

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![AWS](https://img.shields.io/badge/AWS-MediaConvert-orange.svg)](https://aws.amazon.com/mediaconvert/)

**E2MC Assistant** is a comprehensive toolkit designed to simplify the migration from Encoding.com to AWS MediaConvert. It provides intelligent configuration conversion, video analysis, job management, and workflow automation capabilities.

---

## 🌟 Key Features

### 🔄 **Intelligent Configuration Conversion**
- Convert Encoding.com XML configurations to AWS MediaConvert JSON
- Support for 10+ video formats (MP4, HLS, DASH, CMAF, WebM, etc.)
- Rule-based mapping with complex condition support
- Template-driven conversion preserving MediaConvert structure
- 100% parameter mapping with detailed logging

### 🎥 **AI-Powered Video Analysis**
- Extract comprehensive video metadata from S3
- Compare videos and identify quality differences
- AI-powered analysis using AWS Bedrock (Claude 3.5)
- Support for multiple video formats and codecs

### ⚡ **Automated Workflow Management**
- End-to-end migration workflow automation
- AWS MediaConvert job submission and tracking
- Batch processing capabilities
- Real-time job monitoring and status updates

### 🛠️ **Enterprise-Grade Tools**
- JSON schema validation for MediaConvert configurations
- Comprehensive error analysis and reporting
- Pilot program management tools
- Extensive logging and debugging capabilities

---

## 📊 Project Statistics

- **683** Encoding.com configuration samples
- **334** Successfully converted MediaConvert profiles
- **10+** Supported video formats
- **4** Command-line tools
- **100%** Parameter mapping coverage

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/xzy0223/encoding2mediaconvert.git
cd encoding2mediaconvert

# Install in development mode
pip install -e .

# Verify installation
e2mc-converter --help
```

### Basic Usage

```bash
# Convert a single configuration
e2mc-converter \
  --source encoding_profiles/mp4/916.xml \
  --rules src/e2mc_assistant/converter/rules/e2mc_rules.yaml \
  --template src/e2mc_assistant/converter/templates/mp4_template.json \
  --output output/916.json \
  --verbose

# Batch convert multiple files
e2mc-converter \
  --source encoding_profiles/mp4/ \
  --rules src/e2mc_assistant/converter/rules/e2mc_rules.yaml \
  --output output/ \
  --batch

# Analyze video differences
e2mc-analyzer compare \
  s3://bucket/original-video.mp4 \
  s3://bucket/converted-video.mp4 \
  --output differences.json

# Submit MediaConvert job
e2mc-submitter \
  --profile-path output/916.json \
  --input-url s3://input-bucket/video.mp4 \
  --output-destination s3://output-bucket/ \
  --track-job
```

---

## 🏗️ Architecture

### Core Components

```
E2MC Assistant
├── 🔄 Converter          # XML → JSON configuration conversion
├── 🎥 Video Analyzer     # AI-powered video analysis & comparison  
├── 📤 Job Submitter      # MediaConvert job management
├── 🔄 Workflow Engine    # End-to-end automation
└── ✅ Validator          # Configuration validation
```

### Project Structure

```
e2mc_assistant/
├── src/e2mc_assistant/           # Core package
│   ├── converter/                # Configuration conversion engine
│   │   ├── rules/               # YAML mapping rules
│   │   └── templates/           # MediaConvert job templates
│   ├── analyzer/                # Video analysis & comparison
│   ├── requester/               # MediaConvert job management
│   └── workflow/                # End-to-end workflow automation
├── encoding_profiles/           # 683 sample configurations
│   ├── mp4/                    # MP4 format samples
│   ├── advanced_hls/           # HLS streaming samples
│   ├── mpeg_dash/              # DASH streaming samples
│   └── pilot1/                 # Pilot program samples
├── tranformed_mc_profiles/      # 334 converted configurations
└── utils/                       # Validation and utility tools
```

---

## 🛠️ Command Line Tools

### `e2mc-converter` - Configuration Conversion
```bash
e2mc-converter --source input.xml --rules rules.yaml --output output.json
```

### `e2mc-analyzer` - Video Analysis
```bash
e2mc-analyzer compare video1.mp4 video2.mp4 --output differences.json
e2mc-analyzer analyze video1.mp4 video2.mp4 --output analysis.txt
```

### `e2mc-submitter` - Job Management
```bash
e2mc-submitter --profile-path config.json --input-url s3://input.mp4 --output-destination s3://output/
```

### `e2mc-workflow` - Complete Automation
```bash
e2mc-workflow workflow --config-dir configs/ --s3-input s3://input/ --s3-output s3://output/
```

---

## 🎯 Production Workflow Commands

For production-level profile conversion and job submission, we recommend using these two core commands that provide comprehensive control and filtering capabilities:

### 1. `convert` - Profile Conversion Command

Convert Encoding.com XML profiles to AWS MediaConvert JSON configurations with advanced filtering options.

```bash
python /home/ec2-user/e2mc_assistant/src/e2mc_assistant/workflow/e2mc_workflow.py convert \
    --input-dir /home/ec2-user/e2mc_assistant/encoding_profiles/batch2/iphone \
    --output-dir /home/ec2-user/e2mc_assistant/tranformed_mc_profiles/batch2/iphone \
    --rules-file /home/ec2-user/e2mc_assistant/src/e2mc_assistant/converter/rules/e2mc_rules.yaml \
    --template-file /home/ec2-user/e2mc_assistant/src/e2mc_assistant/converter/templates/mp4_template.json \
    --validate /home/ec2-user/e2mc_assistant/utils/mc_config_validator/mc_setting_schema.json \
    --include 16
```

#### Parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--input-dir` | ✅ | Directory containing Encoding.com XML profile files to convert |
| `--output-dir` | ✅ | Directory where converted MediaConvert JSON files will be saved |
| `--rules-file` | ✅ | Path to YAML rules file defining conversion mappings |
| `--template-file` | ✅ | Path to MediaConvert JSON template file |
| `--validate` | ❌ | Path to JSON schema file for validating output configurations |
| `--include` | ❌ | Process only profiles with this ID (extracted from filename) |
| `--exclude` | ❌ | Skip profiles with this ID (extracted from filename) |

#### Profile ID Extraction:
- **ID Source**: Profile IDs are extracted from XML filenames
- **Pattern**: `^(\d+)` - extracts the leading number from filename
- **Examples**: 
  - `16.xml` → ID: `16`
  - `720_test.xml` → ID: `720`
  - `1080p_profile.xml` → ID: `1080`
  - `test_16.xml` → ID: `test_16` (fallback to full filename without extension)

#### Examples:

```bash
# Convert all profiles in a directory
python .../e2mc_workflow.py convert \
    --input-dir encoding_profiles/mp4 \
    --output-dir tranformed_mc_profiles/mp4 \
    --rules-file rules/e2mc_rules.yaml \
    --template-file templates/mp4_template.json

# Convert only profile with ID "16"
python .../e2mc_workflow.py convert \
    --input-dir encoding_profiles/hls \
    --output-dir tranformed_mc_profiles/hls \
    --rules-file rules/e2mc_rules.yaml \
    --template-file templates/hls_template.json \
    --include 16

# Convert all except profile with ID "720"
python .../e2mc_workflow.py convert \
    --input-dir encoding_profiles/all \
    --output-dir tranformed_mc_profiles/all \
    --rules-file rules/e2mc_rules.yaml \
    --template-file templates/mp4_template.json \
    --exclude 720 \
    --validate utils/mc_config_validator/mc_setting_schema.json
```

### 2. `submit` - Job Submission Command

Submit MediaConvert jobs using converted JSON configurations with S3 input/output paths.

```bash
python /home/ec2-user/e2mc_assistant/src/e2mc_assistant/workflow/e2mc_workflow.py submit \
    --config-dir /home/ec2-user/e2mc_assistant/tranformed_mc_profiles/batch2/iphone \
    --s3-source-path s3://fw-e2mc-batch2/encoding_sample_videos/iphone/ \
    --s3-output-path s3://fw-e2mc-batch2/encoding_sample_videos/output/iphone/ \
    --role-arn arn:aws:iam::935206693453:role/MediaConvertRole \
    --include 16
```

#### Parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--config-dir` | ✅ | Directory containing MediaConvert JSON configuration files |
| `--s3-source-path` | ✅ | S3 base path containing input video files organized by ID (must end with /) |
| `--s3-output-path` | ✅ | S3 path where output files will be stored (must end with /) |
| `--role-arn` | ✅ | IAM role ARN with MediaConvert and S3 permissions |
| `--include` | ❌ | Submit jobs only for configs with this ID (extracted from filename) |
| `--exclude` | ❌ | Skip configs with this ID (extracted from filename) |

#### S3 Path Structure:

The S3 source path must be organized with subdirectories for each profile ID:

```
s3://bucket-name/base-path/
├── 16/
│   ├── 16_sample_source.mp4
│   └── 16_metadata.json
├── 720/
│   ├── 720_test_source.mp4
│   └── 720_info.txt
└── 1080/
    ├── 1080_hd_source.mp4
    └── 1080_config.xml
```

**Expected Structure**: `s3://bucket/base-path/{id}/{id}_*_source.{extension}`

**Example**: For profile ID `16`, the system looks for videos in `s3://bucket/base-path/16/` with patterns like:
- `16_sample_source.mp4` (preferred - contains "_source")
- `16_video.mp4` (fallback - starts with ID)

#### Examples:

```bash
# Submit all jobs in a directory
python .../e2mc_workflow.py submit \
    --config-dir tranformed_mc_profiles/mp4 \
    --s3-source-path s3://input-bucket/videos/ \
    --s3-output-path s3://output-bucket/results/ \
    --role-arn arn:aws:iam::123456789012:role/MediaConvertRole

# Submit only job for profile ID "16"
python .../e2mc_workflow.py submit \
    --config-dir tranformed_mc_profiles/hls \
    --s3-source-path s3://input-bucket/hls-videos/ \
    --s3-output-path s3://output-bucket/hls-results/ \
    --role-arn arn:aws:iam::123456789012:role/MediaConvertRole \
    --include 16

# Submit all except profile ID "720"
python .../e2mc_workflow.py submit \
    --config-dir tranformed_mc_profiles/all \
    --s3-source-path s3://input-bucket/all-videos/ \
    --s3-output-path s3://output-bucket/all-results/ \
    --role-arn arn:aws:iam::123456789012:role/MediaConvertRole \
    --exclude 720
```

#### Profile ID Filtering:

Both commands support `--include` and `--exclude` parameters for precise profile selection:

- **`--include`**: Process only profiles whose ID matches the specified value
- **`--exclude`**: Skip profiles whose ID matches the specified value  
- **Priority**: `--exclude` takes precedence over `--include`
- **ID Extraction**: IDs are extracted from filenames using pattern `^(\d+)`
- **Use Cases**: 
  - Process specific profile: `--include 16` (processes only `16.xml` → `16.json`)
  - Skip problematic profile: `--exclude 720` (skips `720.xml`)
  - Test single profile: `--include 1080` (processes only `1080.xml`)

#### Complete Workflow Example:

```bash
# Step 1: Convert only profile ID "16" for iPhone format
python .../e2mc_workflow.py convert \
    --input-dir encoding_profiles/pilot1/iphone \
    --output-dir tranformed_mc_profiles/pilot1/iphone \
    --rules-file src/e2mc_assistant/converter/rules/e2mc_rules.yaml \
    --template-file src/e2mc_assistant/converter/templates/mp4_template.json \
    --validate utils/mc_config_validator/mc_setting_schema.json \
    --include 16

# Step 2: Submit MediaConvert job for the converted profile ID "16"
python .../e2mc_workflow.py submit \
    --config-dir tranformed_mc_profiles/pilot1/iphone \
    --s3-source-path s3://my-bucket/source-videos/iphone/ \
    --s3-output-path s3://my-bucket/output-videos/iphone/ \
    --role-arn arn:aws:iam::123456789012:role/MediaConvertRole \
    --include 16
```

#### File Naming Convention:

For the commands to work correctly, ensure your files follow this naming pattern:
- **Input XML files**: `{ID}.xml` (e.g., `16.xml`, `720.xml`, `1080.xml`)
- **Output JSON files**: `{ID}.json` (e.g., `16.json`, `720.json`, `1080.json`)
- **S3 video files**: `{ID}_*_source.*` (e.g., `16_sample_source.mp4`)

---

## 🐍 Python API

### Configuration Conversion
```python
from e2mc_assistant import ConfigConverter

# Initialize converter with rules
converter = ConfigConverter('rules/e2mc_rules.yaml')

# Convert single configuration
result = converter.convert('input.xml', 'mp4_template.json')

# Batch conversion
results = converter.convert_batch('input_dir/', 'output_dir/')
```

### Video Analysis
```python
from e2mc_assistant import VideoAnalyzer

# Initialize analyzer
analyzer = VideoAnalyzer(region='us-east-1')

# Extract video information
video_info = analyzer.extract_video_info('s3://bucket/video.mp4')

# Compare two videos
differences = analyzer.compare_videos(video1_info, video2_info)

# AI-powered analysis
analysis = analyzer.analyze_differences(differences)
```

### Job Management
```python
from e2mc_assistant import MediaConvertJobSubmitter

# Initialize job submitter
submitter = MediaConvertJobSubmitter(region='us-east-1')

# Submit job
response = submitter.submit_job(
    profile_path='config.json',
    input_url='s3://input/video.mp4',
    output_destination='s3://output/'
)

# Track job progress
status = submitter.track_job(response['Job']['Id'])
```

---

## 🎯 Supported Formats

| Format | Input (Encoding.com) | Output (MediaConvert) | Status |
|--------|---------------------|----------------------|---------|
| MP4 | ✅ | ✅ | Fully Supported |
| Advanced HLS | ✅ | ✅ | Fully Supported |
| MPEG-DASH | ✅ | ✅ | Fully Supported |
| CMAF/fMP4 | ✅ | ✅ | Fully Supported |
| WebM | ✅ | ✅ | Fully Supported |
| MPEG-TS | ✅ | ✅ | Fully Supported |
| Smooth Streaming | ✅ | ✅ | Fully Supported |
| iPhone/iPad | ✅ | ✅ | Fully Supported |
| MOV | ✅ | ✅ | Fully Supported |
| FLV | ✅ | ✅ | Fully Supported |

---

## ☁️ AWS Integration

### Required AWS Services
- **AWS MediaConvert** - Video transcoding service
- **Amazon S3** - File storage and retrieval  
- **AWS Bedrock** - AI-powered video analysis (Claude 3.5)
- **AWS IAM** - Access control and permissions

### Required Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "mediaconvert:*",
                "s3:GetObject",
                "s3:PutObject",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

### AWS Configuration
```bash
# Using AWS CLI
aws configure

# Using environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

---

## 📚 Documentation

### Component Documentation
- [🔄 Converter Guide](src/e2mc_assistant/converter/README.md) - Detailed conversion documentation
- [🎥 Video Analyzer Guide](src/e2mc_assistant/analyzer/README.md) - Video analysis capabilities
- [📤 Job Submitter Guide](src/e2mc_assistant/requester/README.md) - MediaConvert job management
- [🔄 Workflow Engine Guide](src/e2mc_assistant/workflow/README.md) - End-to-end automation workflows
- [✅ Validator Guide](utils/mc_config_validator/README.md) - Configuration validation

### Additional Resources
- [📋 Installation Guide](INSTALL.md) - Detailed installation instructions
- [📝 Changelog](CHANGELOG.md) - Version history and updates
- [🔧 Multi-Condition Rules](src/e2mc_assistant/converter/multi_condition_docs.md) - Advanced rule configuration

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Documentation**: Check component-specific README files
- **Issues**: [GitHub Issues](https://github.com/xzy0223/encoding2mediaconvert/issues)
- **AWS Support**: Contact AWS Professional Services

---

## 🏷️ Version

**Current Version**: 1.0.0

**Compatibility**: Python 3.6+, AWS MediaConvert API

---

<div align="center">

**Built with ❤️ by AWS Professional Services**

[🏠 Home](https://github.com/xzy0223/encoding2mediaconvert) • [📖 Docs](src/) • [🐛 Issues](https://github.com/xzy0223/encoding2mediaconvert/issues) • [💬 Discussions](https://github.com/xzy0223/encoding2mediaconvert/discussions)

</div>

---

# E2MC Assistant - Encoding.com 到 AWS MediaConvert 迁移工具包

[![Python 版本](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![许可证](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![AWS](https://img.shields.io/badge/AWS-MediaConvert-orange.svg)](https://aws.amazon.com/mediaconvert/)

**E2MC Assistant** 是一个全面的工具包，旨在简化从 Encoding.com 到 AWS MediaConvert 的迁移过程。它提供智能配置转换、视频分析、任务管理和工作流自动化功能。

---

## 🌟 核心特性

### 🔄 **智能配置转换**
- 将 Encoding.com XML 配置转换为 AWS MediaConvert JSON
- 支持 10+ 种视频格式（MP4、HLS、DASH、CMAF、WebM 等）
- 基于规则的映射，支持复杂条件判断
- 模板驱动转换，保持 MediaConvert 结构
- 100% 参数映射，详细日志记录

### 🎥 **AI 驱动的视频分析**
- 从 S3 提取全面的视频元数据
- 比较视频并识别质量差异
- 使用 AWS Bedrock (Claude 3.5) 进行 AI 分析
- 支持多种视频格式和编解码器

### ⚡ **自动化工作流管理**
- 端到端迁移工作流自动化
- AWS MediaConvert 任务提交和跟踪
- 批量处理能力
- 实时任务监控和状态更新

### 🛠️ **企业级工具**
- MediaConvert 配置的 JSON 模式验证
- 全面的错误分析和报告
- 试点项目管理工具
- 广泛的日志记录和调试功能

---

## 📊 项目统计

- **683** 个 Encoding.com 配置样本
- **334** 个成功转换的 MediaConvert 配置
- **10+** 种支持的视频格式
- **4** 个命令行工具
- **100%** 参数映射覆盖率

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/xzy0223/encoding2mediaconvert.git
cd encoding2mediaconvert

# 开发模式安装
pip install -e .

# 验证安装
e2mc-converter --help
```

### 基本用法

```bash
# 转换单个配置
e2mc-converter \
  --source encoding_profiles/mp4/916.xml \
  --rules src/e2mc_assistant/converter/rules/e2mc_rules.yaml \
  --template src/e2mc_assistant/converter/templates/mp4_template.json \
  --output output/916.json \
  --verbose

# 批量转换多个文件
e2mc-converter \
  --source encoding_profiles/mp4/ \
  --rules src/e2mc_assistant/converter/rules/e2mc_rules.yaml \
  --output output/ \
  --batch

# 分析视频差异
e2mc-analyzer compare \
  s3://bucket/original-video.mp4 \
  s3://bucket/converted-video.mp4 \
  --output differences.json

# 提交 MediaConvert 任务
e2mc-submitter \
  --profile-path output/916.json \
  --input-url s3://input-bucket/video.mp4 \
  --output-destination s3://output-bucket/ \
  --track-job
```

---

## 🏗️ 架构

### 核心组件

```
E2MC Assistant
├── 🔄 转换器           # XML → JSON 配置转换
├── 🎥 视频分析器       # AI 驱动的视频分析和比较
├── 📤 任务提交器       # MediaConvert 任务管理
├── 🔄 工作流引擎       # 端到端自动化
└── ✅ 验证器          # 配置验证
```

### 项目结构

```
e2mc_assistant/
├── src/e2mc_assistant/           # 核心包
│   ├── converter/                # 配置转换引擎
│   │   ├── rules/               # YAML 映射规则
│   │   └── templates/           # MediaConvert 任务模板
│   ├── analyzer/                # 视频分析和比较
│   ├── requester/               # MediaConvert 任务管理
│   └── workflow/                # 端到端工作流自动化
├── encoding_profiles/           # 683 个样本配置
│   ├── mp4/                    # MP4 格式样本
│   ├── advanced_hls/           # HLS 流媒体样本
│   ├── mpeg_dash/              # DASH 流媒体样本
│   └── pilot1/                 # 试点项目样本
├── tranformed_mc_profiles/      # 334 个转换后的配置
└── utils/                       # 验证和实用工具
```

---

## 🛠️ 命令行工具

### `e2mc-converter` - 配置转换
```bash
e2mc-converter --source input.xml --rules rules.yaml --output output.json
```

### `e2mc-analyzer` - 视频分析
```bash
e2mc-analyzer compare video1.mp4 video2.mp4 --output differences.json
e2mc-analyzer analyze video1.mp4 video2.mp4 --output analysis.txt
```

### `e2mc-submitter` - 任务管理
```bash
e2mc-submitter --profile-path config.json --input-url s3://input.mp4 --output-destination s3://output/
```

### `e2mc-workflow` - 完整自动化
```bash
e2mc-workflow workflow --config-dir configs/ --s3-input s3://input/ --s3-output s3://output/
```

---

## 🎯 生产环境工作流命令

对于生产级别的配置文件转换和任务提交，我们推荐使用这两个核心命令，它们提供全面的控制和过滤功能：

### 1. `convert` - 配置文件转换命令

将 Encoding.com XML 配置文件转换为 AWS MediaConvert JSON 配置，支持高级过滤选项。

```bash
python /home/ec2-user/e2mc_assistant/src/e2mc_assistant/workflow/e2mc_workflow.py convert \
    --input-dir /home/ec2-user/e2mc_assistant/encoding_profiles/batch2/iphone \
    --output-dir /home/ec2-user/e2mc_assistant/tranformed_mc_profiles/batch2/iphone \
    --rules-file /home/ec2-user/e2mc_assistant/src/e2mc_assistant/converter/rules/e2mc_rules.yaml \
    --template-file /home/ec2-user/e2mc_assistant/src/e2mc_assistant/converter/templates/mp4_template.json \
    --validate /home/ec2-user/e2mc_assistant/utils/mc_config_validator/mc_setting_schema.json \
    --include 16
```

#### 参数说明：

| 参数 | 必需 | 说明 |
|------|------|------|
| `--input-dir` | ✅ | 包含 Encoding.com XML 配置文件的目录 |
| `--output-dir` | ✅ | 保存转换后的 MediaConvert JSON 文件的目录 |
| `--rules-file` | ✅ | 定义转换映射的 YAML 规则文件路径 |
| `--template-file` | ✅ | MediaConvert JSON 模板文件路径 |
| `--validate` | ❌ | 用于验证输出配置的 JSON 模式文件路径 |
| `--include` | ❌ | 只处理具有此 ID 的配置文件（从文件名提取） |
| `--exclude` | ❌ | 跳过具有此 ID 的配置文件（从文件名提取） |

#### 配置文件 ID 提取：
- **ID 来源**：从 XML 文件名中提取配置文件 ID
- **提取模式**：`^(\d+)` - 提取文件名开头的数字
- **示例**：
  - `16.xml` → ID: `16`
  - `720_test.xml` → ID: `720`
  - `1080p_profile.xml` → ID: `1080`
  - `test_16.xml` → ID: `test_16`（回退到不含扩展名的完整文件名）

### 2. `submit` - 任务提交命令

使用转换后的 JSON 配置文件提交 MediaConvert 任务，支持 S3 输入/输出路径。

```bash
python /home/ec2-user/e2mc_assistant/src/e2mc_assistant/workflow/e2mc_workflow.py submit \
    --config-dir /home/ec2-user/e2mc_assistant/tranformed_mc_profiles/batch2/iphone \
    --s3-source-path s3://fw-e2mc-batch2/encoding_sample_videos/iphone/ \
    --s3-output-path s3://fw-e2mc-batch2/encoding_sample_videos/output/iphone/ \
    --role-arn arn:aws:iam::935206693453:role/MediaConvertRole \
    --include 16
```

#### 参数说明：

| 参数 | 必需 | 说明 |
|------|------|------|
| `--config-dir` | ✅ | 包含 MediaConvert JSON 配置文件的目录 |
| `--s3-source-path` | ✅ | 包含按 ID 组织的输入视频文件的 S3 基础路径（必须以 / 结尾） |
| `--s3-output-path` | ✅ | 存储输出文件的 S3 路径（必须以 / 结尾） |
| `--role-arn` | ✅ | 具有 MediaConvert 和 S3 权限的 IAM 角色 ARN |
| `--include` | ❌ | 只为具有此 ID 的配置文件提交任务（从文件名提取） |
| `--exclude` | ❌ | 跳过具有此 ID 的配置文件（从文件名提取） |

#### S3 路径结构：

S3 源路径必须按每个配置文件 ID 组织子目录：

```
s3://bucket-name/base-path/
├── 16/
│   ├── 16_sample_source.mp4
│   └── 16_metadata.json
├── 720/
│   ├── 720_test_source.mp4
│   └── 720_info.txt
└── 1080/
    ├── 1080_hd_source.mp4
    └── 1080_config.xml
```

**预期结构**：`s3://bucket/base-path/{id}/{id}_*_source.{extension}`

**示例**：对于配置文件 ID `16`，系统会在 `s3://bucket/base-path/16/` 中查找符合以下模式的视频：
- `16_sample_source.mp4`（首选 - 包含 "_source"）
- `16_video.mp4`（备选 - 以 ID 开头）

#### 配置文件 ID 过滤：

两个命令都支持 `--include` 和 `--exclude` 参数进行精确的配置文件选择：

- **`--include`**：只处理 ID 匹配指定值的配置文件
- **`--exclude`**：跳过 ID 匹配指定值的配置文件
- **优先级**：`--exclude` 优先于 `--include`
- **ID 提取**：使用模式 `^(\d+)` 从文件名中提取 ID
- **使用场景**：
  - 处理特定配置文件：`--include 16`（只处理 `16.xml` → `16.json`）
  - 跳过有问题的配置文件：`--exclude 720`（跳过 `720.xml`）
  - 测试单个配置文件：`--include 1080`（只处理 `1080.xml`）

#### 完整工作流示例：

```bash
# 步骤 1：只转换 iPhone 格式的配置文件 ID "16"
python .../e2mc_workflow.py convert \
    --input-dir encoding_profiles/pilot1/iphone \
    --output-dir tranformed_mc_profiles/pilot1/iphone \
    --rules-file src/e2mc_assistant/converter/rules/e2mc_rules.yaml \
    --template-file src/e2mc_assistant/converter/templates/mp4_template.json \
    --validate utils/mc_config_validator/mc_setting_schema.json \
    --include 16

# 步骤 2：为转换后的配置文件 ID "16" 提交 MediaConvert 任务
python .../e2mc_workflow.py submit \
    --config-dir tranformed_mc_profiles/pilot1/iphone \
    --s3-source-path s3://my-bucket/source-videos/iphone/ \
    --s3-output-path s3://my-bucket/output-videos/iphone/ \
    --role-arn arn:aws:iam::123456789012:role/MediaConvertRole \
    --include 16
```

#### 文件命名约定：

为了确保命令正常工作，请确保您的文件遵循以下命名模式：
- **输入 XML 文件**：`{ID}.xml`（例如：`16.xml`、`720.xml`、`1080.xml`）
- **输出 JSON 文件**：`{ID}.json`（例如：`16.json`、`720.json`、`1080.json`）
- **S3 视频文件**：`s3://bucket/base-path/{ID}/{ID}_*_source.*`（例如：`s3://bucket/videos/16/16_sample_source.mp4`）

---

## 🐍 Python API

### 配置转换
```python
from e2mc_assistant import ConfigConverter

# 使用规则初始化转换器
converter = ConfigConverter('rules/e2mc_rules.yaml')

# 转换单个配置
result = converter.convert('input.xml', 'mp4_template.json')

# 批量转换
results = converter.convert_batch('input_dir/', 'output_dir/')
```

### 视频分析
```python
from e2mc_assistant import VideoAnalyzer

# 初始化分析器
analyzer = VideoAnalyzer(region='us-east-1')

# 提取视频信息
video_info = analyzer.extract_video_info('s3://bucket/video.mp4')

# 比较两个视频
differences = analyzer.compare_videos(video1_info, video2_info)

# AI 驱动分析
analysis = analyzer.analyze_differences(differences)
```

### 任务管理
```python
from e2mc_assistant import MediaConvertJobSubmitter

# 初始化任务提交器
submitter = MediaConvertJobSubmitter(region='us-east-1')

# 提交任务
response = submitter.submit_job(
    profile_path='config.json',
    input_url='s3://input/video.mp4',
    output_destination='s3://output/'
)

# 跟踪任务进度
status = submitter.track_job(response['Job']['Id'])
```

---

## 🎯 支持的格式

| 格式 | 输入 (Encoding.com) | 输出 (MediaConvert) | 状态 |
|------|-------------------|-------------------|------|
| MP4 | ✅ | ✅ | 完全支持 |
| Advanced HLS | ✅ | ✅ | 完全支持 |
| MPEG-DASH | ✅ | ✅ | 完全支持 |
| CMAF/fMP4 | ✅ | ✅ | 完全支持 |
| WebM | ✅ | ✅ | 完全支持 |
| MPEG-TS | ✅ | ✅ | 完全支持 |
| Smooth Streaming | ✅ | ✅ | 完全支持 |
| iPhone/iPad | ✅ | ✅ | 完全支持 |
| MOV | ✅ | ✅ | 完全支持 |
| FLV | ✅ | ✅ | 完全支持 |

---

## ☁️ AWS 集成

### 所需的 AWS 服务
- **AWS MediaConvert** - 视频转码服务
- **Amazon S3** - 文件存储和检索
- **AWS Bedrock** - AI 驱动的视频分析 (Claude 3.5)
- **AWS IAM** - 访问控制和权限

### 所需权限
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "mediaconvert:*",
                "s3:GetObject",
                "s3:PutObject",
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

### AWS 配置
```bash
# 使用 AWS CLI
aws configure

# 使用环境变量
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

---

## 📚 文档

### 组件文档
- [🔄 转换器指南](src/e2mc_assistant/converter/README.md) - 详细转换文档
- [🎥 视频分析器指南](src/e2mc_assistant/analyzer/README.md) - 视频分析功能
- [📤 任务提交器指南](src/e2mc_assistant/requester/README.md) - MediaConvert 任务管理
- [🔄 工作流引擎指南](src/e2mc_assistant/workflow/README.md) - 端到端自动化工作流
- [✅ 验证器指南](utils/mc_config_validator/README.md) - 配置验证

### 其他资源
- [📋 安装指南](INSTALL.md) - 详细安装说明
- [📝 更新日志](CHANGELOG.md) - 版本历史和更新
- [🔧 多条件规则](src/e2mc_assistant/converter/multi_condition_docs.md) - 高级规则配置

---

## 🤝 贡献

我们欢迎贡献！请查看我们的贡献指南：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

## 🆘 支持

- **文档**: 查看组件特定的 README 文件
- **问题**: [GitHub Issues](https://github.com/xzy0223/encoding2mediaconvert/issues)
- **AWS 支持**: 联系 AWS 专业服务

---

## 🏷️ 版本

**当前版本**: 1.0.0

**兼容性**: Python 3.6+, AWS MediaConvert API

---

<div align="center">

**由 AWS 专业服务团队用 ❤️ 构建**

[🏠 主页](https://github.com/xzy0223/encoding2mediaconvert) • [📖 文档](src/) • [🐛 问题](https://github.com/xzy0223/encoding2mediaconvert/issues) • [💬 讨论](https://github.com/xzy0223/encoding2mediaconvert/discussions)

</div>
