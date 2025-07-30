# VoiceRecognize - 语音识别项目

这是一个基于OpenAI Whisper和Pyannote.audio的语音识别项目，支持多语言语音转录和说话人分离。

## 功能特性

- 🎤 **语音转录**: 使用OpenAI Whisper进行高精度语音转文本
- 👥 **说话人分离**: 使用Pyannote.audio识别不同说话人
- 🌍 **多语言支持**: 支持中文、英文等多种语言
- ⚡ **本地运行**: 完全本地化，无需云端服务
- 📊 **详细分析**: 提供转录时间、说话人统计等详细信息

## 项目结构

```
voicerecognize/
├── README.md                    # 项目说明
├── .gitignore                   # Git忽略文件
├── requirements.txt             # Python依赖
├── whisper_test.py             # Whisper环境测试
├── whisper_example.py          # Whisper使用示例
├── whisper_simple_test.py      # 简单Whisper测试
├── whisper_pyannote_real.py    # Whisper + Pyannote完整实现
├── whisper_with_simple_diarization.py  # 简化说话人分离演示
├── transcribe_test.py          # 转录测试脚本
├── demo_whisper.py             # Whisper演示脚本
├── quick_test.py               # 快速测试脚本
├── README_whisper.md           # Whisper详细说明
├── real_vs_demo_comparison.md  # 真实结果与演示对比
└── FireRedASR/                 # FireRedASR相关文件
    ├── test_fireredasr.py
    ├── test_with_audio.py
    ├── long_audio_processor.py
    ├── test_fireredasr_official.py
    ├── test_single_segment.py
    └── final_comparison_report.md
```

## 环境要求

- Python 3.8-3.11
- FFmpeg
- PyTorch
- OpenAI Whisper
- Pyannote.audio (可选，用于说话人分离)

## 快速开始

### 1. 环境设置

```bash
# 创建conda环境
conda create -n whisper python=3.11
conda activate whisper

# 安装FFmpeg
conda install -c conda-forge ffmpeg

# 安装依赖
pip install -U openai-whisper
pip install "numpy<2"
pip install psutil
pip install pyannote.audio  # 可选，用于说话人分离
```

### 2. 基本使用

```bash
# 测试环境
python whisper_test.py

# 简单转录
python whisper_simple_test.py

# 完整Whisper + Pyannote (需要HF_TOKEN)
export HF_TOKEN="your_token_here"
python whisper_pyannote_real.py
```

## 模型说明

### Whisper模型
- **tiny**: 最快，适合实时应用
- **base**: 平衡速度和准确性
- **small**: 推荐使用，准确性好
- **medium**: 更高准确性，但较慢
- **large**: 最高准确性，但需要更多资源

### Pyannote模型
- **speaker-diarization-3.1**: 说话人分离模型
- **segmentation-3.0**: 语音分割模型

## 使用示例

### 基本转录
```python
import whisper

# 加载模型
model = whisper.load_model("small")

# 转录音频
result = model.transcribe("audio.wav")
print(result["text"])
```

### 说话人分离 + 转录
```python
from pyannote.audio import Pipeline
import whisper

# 初始化Pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="your_token"
)

# 说话人分离
diarization = pipeline("audio.wav")

# 对每个片段进行转录
whisper_model = whisper.load_model("small")
for turn, _, speaker in diarization.itertracks(yield_label=True):
    # 提取音频片段并转录
    # ...
```

## 测试结果

项目包含多个测试脚本和结果文件：
- `whisper_simple_result.txt`: Whisper转录结果
- `whisper_pyannote_real_result.txt`: 完整转录结果
- `real_vs_demo_comparison.md`: 结果分析

## 注意事项

1. **模型文件**: 首次运行会自动下载模型文件，需要网络连接
2. **HF_TOKEN**: 使用Pyannote需要HuggingFace访问令牌
3. **内存要求**: 大模型需要较多内存和GPU资源
4. **音频格式**: 支持常见音频格式，建议使用WAV格式

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进项目！ 