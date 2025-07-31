#!/usr/bin/env python3
"""
创建Mac本地应用 - 轻量版
仅包含代码，模型在线下载
"""

import os
import shutil
import subprocess
from pathlib import Path

def create_app():
    """创建Mac应用"""
    print("=== 创建VoiceRecognize Mac应用 ===")
    
    # 创建应用目录
    app_name = "VoiceRecognize.app"
    app_dir = Path(app_name)
    
    if app_dir.exists():
        shutil.rmtree(app_dir)
    
    # 创建目录结构
    (app_dir / "Contents" / "MacOS").mkdir(parents=True, exist_ok=True)
    (app_dir / "Contents" / "Resources").mkdir(parents=True, exist_ok=True)
    
    # 创建Info.plist
    info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>VoiceRecognize</string>
    <key>CFBundleIdentifier</key>
    <string>com.voicerecognize.app</string>
    <key>CFBundleName</key>
    <string>VoiceRecognize</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>"""
    
    with open(app_dir / "Contents" / "Info.plist", "w") as f:
        f.write(info_plist)
    
    # 创建启动脚本
    launcher_script = """#!/bin/bash
# VoiceRecognize 启动脚本

# 获取应用目录
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESOURCES_DIR="$APP_DIR/Contents/Resources"

echo "=== VoiceRecognize 语音识别应用 ==="
echo "应用目录: $RESOURCES_DIR"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    echo "请先安装Python3：https://www.python.org/downloads/"
    read -p "按回车键退出..."
    exit 1
fi

# 检查Conda
if ! command -v conda &> /dev/null; then
    echo "❌ 错误：未找到Conda"
    echo "请先安装Miniconda：https://docs.conda.io/en/latest/miniconda.html"
    read -p "按回车键退出..."
    exit 1
fi

# 进入应用目录
cd "$RESOURCES_DIR"

# 检查环境
if ! conda env list | grep -q "voicerecognize"; then
    echo "📦 首次运行，正在创建环境..."
    echo "这可能需要几分钟时间..."
    
    # 创建环境
    conda create -n voicerecognize python=3.11 -y
    
    # 激活环境并安装依赖
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate voicerecognize
    
    # 安装依赖
    pip install -r requirements.txt
    
    # 安装FFmpeg
    conda install -c conda-forge ffmpeg -y
    
    echo "✅ 环境创建完成！"
else
    echo "✅ 找到现有环境"
fi

# 激活环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate voicerecognize

echo "🚀 启动应用..."
echo "应用将在浏览器中打开：http://localhost:5002"
echo "按 Ctrl+C 停止应用"

# 启动应用
python app_batch.py
"""
    
    launcher_path = app_dir / "Contents" / "MacOS" / "VoiceRecognize"
    with open(launcher_path, "w") as f:
        f.write(launcher_script)
    
    # 设置执行权限
    os.chmod(launcher_path, 0o755)
    
    # 复制核心文件
    resources_dir = app_dir / "Contents" / "Resources"
    
    core_files = [
        "app_batch.py",
        "app.py",
        "requirements.txt",
        "README.md",
        "templates/",
        "uploads/",
        "processed/",
        "temp/"
    ]
    
    print("📁 复制项目文件...")
    for file in core_files:
        src = Path(file)
        dst = resources_dir / file
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        elif src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  跳过 {file}（文件不存在）")
    
    # 创建说明文件
    readme_content = """# VoiceRecognize 语音识别应用

## 应用信息
- **版本**: 1.0
- **类型**: 轻量版（模型在线下载）
- **大小**: 约50MB
- **支持系统**: macOS 10.15+

## 系统要求
- macOS 10.15 或更高版本
- Python 3.11
- Miniconda 或 Anaconda

## 首次使用
1. 双击 VoiceRecognize.app 启动
2. 应用会自动创建Python环境
3. 首次运行会下载必要的模型文件
4. 浏览器会自动打开应用界面

## 功能特点
- ✅ 批量音频文件处理
- ✅ 多种Whisper模型选择
- ✅ 说话人分离（Pyannote）
- ✅ 实时进度显示
- ✅ 断点续传功能
- ✅ 结果预览和下载

## 使用方法
1. 启动应用后，浏览器会自动打开
2. 拖拽音频文件到上传区域
3. 选择Whisper模型和参数
4. 点击开始处理
5. 实时查看进度和结果

## 注意事项
- 首次使用需要下载模型文件（约2-3GB）
- 建议使用GPU加速（如果可用）
- 处理大文件时请耐心等待
- 确保有足够的磁盘空间

## 故障排除
如果遇到问题：
1. 确保已安装Python3和Conda
2. 检查网络连接（首次运行需要下载模型）
3. 查看终端输出的错误信息
4. 重启应用重试

## 技术支持
如有问题，请查看项目README.md文件。
"""
    
    readme_path = resources_dir / "应用说明.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 计算应用大小
    try:
        app_size = subprocess.check_output(["du", "-sh", str(app_dir)]).decode().split()[0]
    except:
        app_size = "未知"
    
    print(f"\n✅ 应用创建完成！")
    print(f"📦 应用位置: {app_dir.absolute()}")
    print(f"📏 应用大小: {app_size}")
    print()
    print("使用方法：")
    print("1. 双击 VoiceRecognize.app 启动")
    print("2. 或使用终端：open VoiceRecognize.app")
    print()
    print("注意：")
    print("- 首次运行会自动创建Python环境")
    print("- 首次使用会下载模型文件（约2-3GB）")
    print("- 确保已安装Python3和Conda")

if __name__ == "__main__":
    create_app() 