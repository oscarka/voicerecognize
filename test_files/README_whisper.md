# OpenAI Whisper 本地运行指南

## 项目概述

[OpenAI Whisper](https://github.com/openai/whisper) 是一个强大的语音识别模型，支持：

- 🎤 **多语言语音识别**：支持多种语言的语音转文字
- 🌍 **语音翻译**：将非英语语音翻译成英语
- 🔍 **语言识别**：自动检测语音语言
- ⏰ **时间戳标注**：提供详细的语音分段信息

## 环境要求

### 硬件要求
- **CPU**: 支持Python 3.8-3.11
- **内存**: 建议8GB以上
- **GPU**: 可选，但强烈推荐（大幅提升速度）
- **存储**: 模型文件大小从39M到1550M不等

### 软件依赖
- Python 3.8-3.11
- FFmpeg（音频处理必需）
- PyTorch
- OpenAI Whisper

## 安装步骤

### 1. 安装FFmpeg

**macOS (使用Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows (使用Chocolatey):**
```bash
choco install ffmpeg
```

### 2. 安装Whisper

```bash
# 安装最新稳定版本
pip install -U openai-whisper

# 或从GitHub安装最新开发版本
pip install git+https://github.com/openai/whisper.git
```

### 3. 验证安装

运行测试脚本检查环境：
```bash
python whisper_test.py
```

## 模型选择

| 模型 | 参数 | 显存需求 | 速度 | 准确度 | 推荐用途 |
|------|------|---------|------|--------|----------|
| tiny | 39M | ~1GB | 最快 | 较低 | 快速测试 |
| base | 74M | ~1GB | 快 | 一般 | 日常使用 |
| small | 244M | ~2GB | 中等 | 较好 | 平衡选择 |
| medium | 769M | ~5GB | 较慢 | 高 | 高质量转录 |
| large | 1550M | ~10GB | 最慢 | 最高 | 专业用途 |
| turbo | 809M | ~6GB | 很快 | 高 | 推荐选择 |

## 使用方法

### 基础使用

```python
import whisper

# 加载模型
model = whisper.load_model("tiny")

# 转录音频
result = model.transcribe("audio.mp3")
print(result["text"])
```

### 命令行使用

```bash
# 基础转录
whisper audio.mp3

# 指定模型和语言
whisper audio.mp3 --model medium --language Chinese

# 翻译成英语
whisper audio.mp3 --model medium --language Chinese --task translate
```

### 高级功能

```python
import whisper

model = whisper.load_model("medium")

# 检测语言
audio = whisper.load_audio("audio.mp3")
audio = whisper.pad_or_trim(audio)
mel = whisper.log_mel_spectrogram(audio).to(model.device)
_, probs = model.detect_language(mel)
print(f"检测语言: {max(probs, key=probs.get)}")

# 详细转录选项
result = model.transcribe(
    "audio.mp3",
    language="zh",  # 指定语言
    task="transcribe",  # 或 "translate"
    verbose=True,
    word_timestamps=True  # 获取词级时间戳
)
```

## 性能优化建议

### 1. 模型选择
- **开发测试**: 使用 `tiny` 或 `base`
- **生产环境**: 使用 `turbo` 或 `medium`
- **高质量需求**: 使用 `large`

### 2. 硬件优化
- **GPU加速**: 安装CUDA版本的PyTorch
- **内存管理**: 大模型需要足够显存
- **批量处理**: 避免频繁加载模型

### 3. 音频预处理
- **格式转换**: 使用FFmpeg预处理音频
- **质量优化**: 确保音频清晰度
- **长度控制**: 过长的音频分段处理

## 常见问题

### Q: 安装时出现Rust相关错误
A: 安装Rust开发环境：
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

### Q: 模型下载失败
A: 检查网络连接，或手动下载模型文件到缓存目录

### Q: 转录速度慢
A: 
- 使用GPU加速
- 选择较小的模型
- 检查音频质量和长度

### Q: 中文识别效果不好
A:
- 使用 `medium` 或 `large` 模型
- 确保音频质量良好
- 考虑使用语言指定参数

## 项目集成示例

查看 `whisper_example.py` 文件获取完整的集成示例，包括：

- 批量处理音频文件
- 保存转录结果
- 错误处理
- 多语言支持

## 许可证

Whisper使用MIT许可证，可以自由用于商业和非商业项目。

## 更多资源

- [官方GitHub仓库](https://github.com/openai/whisper)
- [模型卡片](https://github.com/openai/whisper/blob/main/model-card.md)
- [论文](https://cdn.openai.com/papers/whisper.pdf)
- [Colab示例](https://colab.research.google.com/github/openai/whisper/blob/master/notebooks/LibriSpeech.ipynb) 