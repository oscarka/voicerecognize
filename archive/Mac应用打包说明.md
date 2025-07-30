# VoiceRecognize Mac应用打包说明

## 📦 已创建的应用

### 1. 轻量版应用
- **文件名**: `VoiceRecognize_轻量版.app`
- **大小**: 13MB
- **DMG包**: `VoiceRecognize_轻量版.dmg` (7.8MB)
- **特点**: 仅包含代码，模型在线下载

### 2. 标准版应用
- **文件名**: `VoiceRecognize.app`
- **大小**: 13MB
- **特点**: 仅包含代码，模型在线下载

## 🎯 应用特点

### ✅ 功能完整
- 批量音频文件处理
- 多种Whisper模型选择（tiny/base/small/medium/large）
- 说话人分离（Pyannote）
- 实时进度显示
- 断点续传功能
- 结果预览和下载

### ✅ 用户友好
- 双击即可启动
- 自动环境检测和创建
- 自动模型下载
- 浏览器界面操作
- 详细错误提示

### ✅ 系统兼容
- 支持 macOS 10.15+
- 自动检测Python和Conda
- 自动安装依赖
- 自动配置环境变量

## 📋 系统要求

### 必需软件
- **macOS**: 10.15 或更高版本
- **Python**: 3.11
- **Conda**: Miniconda 或 Anaconda

### 推荐配置
- **内存**: 8GB 或更多
- **存储**: 至少 5GB 可用空间
- **网络**: 稳定的互联网连接（首次使用）

## 🚀 使用方法

### 方法1：DMG安装（推荐）
1. 双击 `VoiceRecognize_轻量版.dmg` 挂载
2. 将应用拖拽到 Applications 文件夹
3. 从 Applications 启动应用

### 方法2：直接使用
1. 双击 `VoiceRecognize_轻量版.app` 启动
2. 或使用终端：`open VoiceRecognize_轻量版.app`

## 📱 首次使用流程

1. **启动应用**
   - 双击应用图标
   - 系统会打开终端窗口显示启动过程

2. **环境检查**
   - 自动检测Python和Conda
   - 如果缺少会提示安装

3. **环境创建**
   - 首次运行自动创建 `voicerecognize` 环境
   - 自动安装所有依赖包
   - 安装FFmpeg

4. **模型下载**
   - 首次使用自动下载Whisper模型
   - 下载Pyannote模型（需要HF_TOKEN）
   - 模型文件约2-3GB

5. **启动界面**
   - 浏览器自动打开 `http://localhost:5002`
   - 显示批量处理界面

## 🔧 故障排除

### 常见问题

#### 1. Python未安装
```
❌ 错误：未找到Python3
```
**解决方案**: 安装Python3
```bash
# 从官网下载：https://www.python.org/downloads/
# 或使用Homebrew：
brew install python
```

#### 2. Conda未安装
```
❌ 错误：未找到Conda
```
**解决方案**: 安装Miniconda
```bash
# 下载地址：https://docs.conda.io/en/latest/miniconda.html
# 或使用Homebrew：
brew install --cask miniconda
```

#### 3. 模型下载失败
```
Could not download model...
```
**解决方案**: 
- 检查网络连接
- 确保有足够的磁盘空间
- 重新启动应用

#### 4. 端口被占用
```
Address already in use
```
**解决方案**: 
- 关闭其他占用5002端口的应用
- 或修改应用端口

### 手动环境设置
如果自动环境创建失败，可以手动设置：

```bash
# 1. 创建环境
conda create -n voicerecognize python=3.11

# 2. 激活环境
conda activate voicerecognize

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装FFmpeg
conda install -c conda-forge ffmpeg

# 5. 运行应用
python app_batch.py
```

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

## 🔄 更新应用

### 获取更新
1. 从GitHub下载最新版本
2. 或使用Git更新：
```bash
git pull origin main
```

### 重新打包
```bash
# 创建轻量版
python create_mac_app.py

# 创建完整版
python package_app.py

# 创建DMG
python create_dmg.py
```

## 📞 技术支持

### 获取帮助
- 查看应用内的说明文档
- 查看项目README.md
- 检查终端输出的错误信息
- 联系开发者

### 日志文件
应用运行日志位于：
- 终端输出
- `~/.cache/whisper/` (Whisper日志)
- `~/.cache/huggingface/` (HuggingFace日志)

## 📝 版本历史

### v1.0 (当前版本)
- ✅ 基础语音识别功能
- ✅ 批量文件处理
- ✅ 说话人分离
- ✅ Web界面
- ✅ Mac应用打包
- ✅ DMG安装包

### 计划功能
- 🔄 GPU加速优化
- 🔄 更多模型支持
- 🔄 云端处理选项
- 🔄 移动端支持

---

**注意**: 首次使用需要下载模型文件，请确保网络连接稳定并有足够的磁盘空间。 