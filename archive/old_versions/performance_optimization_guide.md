# Whisper + Pyannote 性能优化指南

## 当前问题分析

### 1. **速度问题**
- **说话人分离耗时过长**: 452秒处理2分钟音频
- **转录速度慢**: 每个片段单独处理，效率低
- **CPU运行**: 没有GPU加速

### 2. **质量问题**
- **语言检测错误**: 中文对话被误判为English、Korean等
- **短片段问题**: <1秒片段容易误判
- **转录质量**: 部分文本不准确

## 优化方案

### 1. **模型选择优化**

#### Whisper模型对比：
| 模型 | 参数量 | 速度 | 准确性 | 推荐场景 |
|------|--------|------|--------|----------|
| tiny | 39M | ⭐⭐⭐⭐⭐ | ⭐⭐ | 实时应用 |
| base | 74M | ⭐⭐⭐⭐ | ⭐⭐⭐ | 平衡选择 |
| small | 244M | ⭐⭐⭐ | ⭐⭐⭐⭐ | 推荐使用 |
| medium | 769M | ⭐⭐ | ⭐⭐⭐⭐⭐ | 高质量需求 |
| large | 1550M | ⭐ | ⭐⭐⭐⭐⭐ | 最高质量 |

**建议**: 使用 `base` 模型平衡速度和准确性

### 2. **参数优化**

#### Whisper转录参数：
```python
result = whisper_model.transcribe(
    audio_file,
    language="zh",        # 强制指定中文
    task="transcribe",    # 明确指定任务
    fp16=False,          # 禁用FP16，避免警告
    verbose=False        # 减少输出
)
```

#### Pyannote优化：
```python
# 过滤短片段
min_duration = 2.0  # 最少2秒
segments = [s for s in segments if s['end'] - s['start'] >= min_duration]
```

### 3. **硬件优化**

#### GPU加速（推荐）：
```bash
# 检查GPU
nvidia-smi

# 安装CUDA版本
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 内存优化：
- 使用较小的模型
- 分批处理长音频
- 及时清理临时文件

### 4. **音频预处理优化**

#### 音频格式优化：
```bash
# 转换为16kHz单声道
ffmpeg -i input.wav -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

#### 音频分段策略：
- 按时间分段（如每30秒）
- 按说话人分段
- 合并短片段

### 5. **代码优化**

#### 批量处理：
```python
# 批量转录多个片段
def batch_transcribe(segments, model):
    results = []
    for segment in segments:
        result = model.transcribe(segment['file'])
        results.append(result)
    return results
```

#### 并行处理：
```python
import concurrent.futures

def parallel_transcribe(segments, model):
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(model.transcribe, seg['file']) for seg in segments]
        results = [future.result() for future in futures]
    return results
```

## 实际优化效果

### 优化前：
- 说话人分离: 452秒
- 转录时间: 较长
- 语言检测: 错误
- 片段数量: 32个（包含短片段）

### 优化后（预期）：
- 说话人分离: 200-300秒
- 转录时间: 减少50%
- 语言检测: 准确（强制中文）
- 片段数量: 15-20个（过滤短片段）

## 使用建议

### 1. **快速测试**：
```bash
python whisper_pyannote_optimized.py
```

### 2. **生产环境**：
- 使用GPU加速
- 预处理音频格式
- 使用更大的模型（medium/large）
- 实现缓存机制

### 3. **实时应用**：
- 使用tiny/base模型
- 流式处理
- 并行转录

## 监控指标

### 性能指标：
- 说话人分离时间
- 转录时间
- 内存使用
- GPU利用率

### 质量指标：
- 语言检测准确率
- 转录准确率
- 说话人分离准确率

## 故障排除

### 常见问题：
1. **内存不足**: 使用更小的模型
2. **GPU不可用**: 检查CUDA安装
3. **语言检测错误**: 强制指定语言
4. **短片段问题**: 设置最小时长过滤

### 调试技巧：
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查模型信息
print(f"Model: {model.name}")
print(f"Device: {model.device}")
``` 