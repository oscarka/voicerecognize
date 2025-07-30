# VoiceRecognize 语音识别项目

一个基于Whisper和Pyannote的本地语音识别和说话人分离工具，支持批量处理音频文件。

## 🚀 快速开始

### 系统要求
- macOS 10.15+ / Linux / Windows
- Python 3.11
- Conda (推荐) 或 pip

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/oscarka/voicerecognize.git
cd voicerecognize
```

2. **创建环境**
```bash
conda create -n voicerecognize python=3.11
conda activate voicerecognize
```

3. **安装依赖**
```bash
pip install -r requirements.txt
conda install -c conda-forge ffmpeg
```

4. **启动应用**
```bash
python app_batch.py
```

5. **访问界面**
打开浏览器访问：http://localhost:5002

## 📁 项目结构

```
voicerecognize/
├── app_batch.py              # 批量处理主应用
├── app.py                    # 单文件处理应用
├── requirements.txt           # Python依赖
├── README.md                 # 项目说明
├── .gitignore               # Git忽略文件
├── templates/               # Web界面模板
│   ├── index.html          # 单文件处理界面
│   └── batch_index.html    # 批量处理界面
├── uploads/                # 上传文件目录
├── processed/              # 处理结果目录
├── temp/                   # 临时文件目录
├── FireRedASR/            # FireRedASR项目
├── build_scripts/          # 打包脚本
│   ├── build_mac_app.py   # Mac应用打包
│   ├── create_mac_app.py  # 轻量版打包
│   ├── package_app.py     # 完整版打包
│   └── create_dmg.py      # DMG创建
├── test_files/            # 测试文件
│   ├── whisper_*.py       # Whisper测试脚本
│   ├── transcribe_*.py    # 转录测试脚本
│   ├── *.txt             # 测试结果
│   └── *.wav             # 测试音频
└── archive/               # 归档文件
    ├── whisper_pyannote_*.py  # Pyannote集成脚本
    ├── *.app/            # Mac应用文件
    ├── *.dmg             # DMG安装包
    └── *.md              # 文档文件
```

## 🎯 核心功能

### ✅ 语音识别
- 支持多种Whisper模型 (tiny/base/small/medium/large)
- 自动语言检测
- 高质量转录输出

### ✅ 说话人分离
- 基于Pyannote.audio
- 自动识别说话人
- 时间戳标注

### ✅ 批量处理
- 多文件同时处理
- 断点续传功能
- 实时进度显示

### ✅ Web界面
- 拖拽上传文件
- 实时进度监控
- 结果预览和下载

## 🔧 使用方法

### 批量处理
1. 启动应用：`python app_batch.py`
2. 打开浏览器：http://localhost:5002
3. 拖拽音频文件到上传区域
4. 选择Whisper模型和参数
5. 点击"开始批量处理"
6. 实时查看进度和结果

### 单文件处理
1. 启动应用：`python app.py`
2. 打开浏览器：http://localhost:5001
3. 上传单个音频文件
4. 选择模型和参数
5. 查看转录结果

## 📊 性能优化

### 硬件建议
- **CPU**: 多核处理器（推荐8核以上）
- **内存**: 16GB 或更多
- **GPU**: 支持CUDA的NVIDIA显卡（可选）
- **存储**: SSD硬盘

### 软件优化
- 使用较小的Whisper模型（tiny/base）提高速度
- 设置合适的最小时长参数
- 分批处理大文件
- 关闭不必要的后台应用

## 🔄 模型管理

### 首次使用
应用会自动下载必要的模型文件：
- **Whisper模型**: 约2GB
- **Pyannote模型**: 约30MB
- **HuggingFace缓存**: 约8GB

### 模型位置
- Whisper: `~/.cache/whisper/`
- Pyannote: `~/.cache/torch/pyannote/`
- HuggingFace: `~/.cache/huggingface/`

## 🛠️ 开发工具

### 测试脚本
```bash
# 测试Whisper安装
python test_files/whisper_test.py

# 测试转录功能
python test_files/transcribe_test.py

# 测试不同模型
python test_files/whisper_example.py
```

### 打包脚本
```bash
# 创建Mac应用
python build_scripts/create_mac_app.py

# 创建完整版应用
python build_scripts/package_app.py

# 创建DMG安装包
python build_scripts/create_dmg.py
```

## 🔧 故障排除

### 常见问题

#### 1. 模型下载失败
```bash
# 手动下载Whisper模型
python -c "import whisper; whisper.load_model('base')"
```

#### 2. Pyannote授权问题
```bash
# 设置HuggingFace Token
export HF_TOKEN="your_token_here"
```

#### 3. 端口被占用
```bash
# 修改端口
python app_batch.py --port 5003
```

#### 4. 内存不足
- 使用较小的模型（tiny/base）
- 分批处理文件
- 增加系统内存

## 📝 版本历史

### v1.0 (当前版本)
- ✅ 基础语音识别功能
- ✅ 批量文件处理
- ✅ 说话人分离
- ✅ Web界面
- ✅ Mac应用打包
- ✅ 项目结构整理

### 计划功能
- 🔄 GPU加速优化
- 🔄 更多模型支持
- 🔄 云端处理选项
- 🔄 移动端支持

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

如有问题，请：
1. 查看 [Issues](../../issues)
2. 查看项目文档
3. 联系开发者

---

**注意**: 首次使用需要下载模型文件，请确保网络连接稳定并有足够的磁盘空间。 