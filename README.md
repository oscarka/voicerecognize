# VoiceRecognize 语音识别应用

一个基于Whisper的独立版语音识别应用，支持批量处理音频文件。

## 🚀 快速开始

### 运行应用
```bash
cd archive/allinone
python3 voicere.py
```

访问 http://localhost:5002 使用Web界面

### 功能特性
- ✅ 美观的Web界面
- ✅ 支持多种Whisper模型（tiny/base/small/medium/large）
- ✅ 批量文件处理
- ✅ 实时进度显示
- ✅ 格式化输出（JSON格式，包含说话人标识）
- ✅ 一键下载处理结果

## 📁 项目结构

```
voice/
├── archive/
│   ├── allinone/           # 主要应用
│   │   └── voicere.py     # 核心应用文件
│   ├── build_scripts/      # 打包脚本（归档）
│   └── old_versions/       # 旧版本文件（归档）
├── templates/              # Web模板
├── FireRedASR/            # 其他项目
├── requirements.txt        # 依赖列表
└── README.md              # 项目说明
```

## 🔧 技术栈

- **后端**: Python + Flask
- **语音识别**: OpenAI Whisper
- **环境管理**: Conda
- **前端**: HTML + CSS + JavaScript

## 📦 依赖安装

应用会自动处理依赖安装：
1. 创建Conda环境
2. 安装NumPy、Flask、PyTorch、Whisper等
3. 下载Whisper模型

## 🎯 使用说明

1. 运行 `python3 voicere.py`
2. 等待环境初始化和模型下载
3. 访问 http://localhost:5002
4. 上传音频文件并选择模型
5. 开始处理，查看实时进度
6. 下载处理结果

## 📝 输出格式

处理结果包含：
- 文件信息
- 识别文本
- 说话人分段
- 时间戳
- 处理统计

## 🛠️ 开发说明

- 主要文件：`archive/allinone/voicere.py`
- 支持模型：tiny, base, small, medium, large
- 端口：5002（自动检测可用端口）
- 临时文件：自动清理

## 📋 归档文件

- `archive/old_versions/`: 旧版本whisper脚本和测试文件
- `archive/build_scripts/`: DMG打包和Mac应用创建脚本
- `templates/`: Web界面模板文件 