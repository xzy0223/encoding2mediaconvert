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
