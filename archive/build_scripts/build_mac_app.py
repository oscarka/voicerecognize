#!/usr/bin/env python3
"""
Mac本地应用打包脚本
支持不同的打包选项：
1. 轻量版（仅代码，模型在线下载）
2. 标准版（包含Whisper模型）
3. 完整版（包含所有模型）
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

def create_app_structure():
    """创建应用目录结构"""
    app_dir = Path("VoiceRecognize.app")
    if app_dir.exists():
        shutil.rmtree(app_dir)
    
    # 创建应用结构
    (app_dir / "Contents" / "MacOS").mkdir(parents=True, exist_ok=True)
    (app_dir / "Contents" / "Resources").mkdir(parents=True, exist_ok=True)
    
    return app_dir

def create_info_plist(app_dir):
    """创建Info.plist文件"""
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
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

def create_launcher_script(app_dir):
    """创建启动脚本"""
    launcher_script = f"""#!/bin/bash
# VoiceRecognize 启动脚本

# 获取应用目录
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESOURCES_DIR="$APP_DIR/Contents/Resources"

# 设置环境变量
export PYTHONPATH="$RESOURCES_DIR:$PYTHONPATH"
export PATH="$RESOURCES_DIR/bin:$PATH"

# 检查Python环境
if [ ! -f "$RESOURCES_DIR/bin/python" ]; then
    echo "错误：找不到Python环境"
    echo "请确保已正确安装Python环境"
    exit 1
fi

# 启动应用
cd "$RESOURCES_DIR"
"$RESOURCES_DIR/bin/python" app_batch.py
"""
    
    launcher_path = app_dir / "Contents" / "MacOS" / "VoiceRecognize"
    with open(launcher_path, "w") as f:
        f.write(launcher_script)
    
    # 设置执行权限
    os.chmod(launcher_path, 0o755)

def copy_project_files(app_dir, include_models=False):
    """复制项目文件"""
    resources_dir = app_dir / "Contents" / "Resources"
    
    # 复制核心文件
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
    
    # 复制模型文件（如果选择）
    if include_models:
        print("正在复制模型文件...")
        cache_dirs = [
            ("~/.cache/whisper", "models/whisper"),
            ("~/.cache/huggingface", "models/huggingface"),
            ("~/.cache/torch/pyannote", "models/pyannote")
        ]
        
        for cache_path, dest_path in cache_dirs:
            cache_full_path = Path(cache_path).expanduser()
            if cache_full_path.exists():
                dest_full_path = resources_dir / dest_path
                dest_full_path.mkdir(parents=True, exist_ok=True)
                print(f"复制 {cache_path} 到 {dest_path}")
                shutil.copytree(cache_full_path, dest_full_path, dirs_exist_ok=True)

def create_conda_env_script(app_dir):
    """创建Conda环境安装脚本"""
    env_script = f"""#!/bin/bash
# 创建Conda环境脚本

echo "正在创建VoiceRecognize环境..."

# 创建环境
conda create -n voicerecognize python=3.11 -y

# 激活环境
source $(conda info --base)/etc/profile.d/conda.sh
conda activate voicerecognize

# 安装依赖
pip install -r requirements.txt

# 安装FFmpeg
conda install -c conda-forge ffmpeg -y

echo "环境创建完成！"
echo "使用方法："
echo "1. 激活环境：conda activate voicerecognize"
echo "2. 运行应用：python app_batch.py"
"""
    
    script_path = app_dir / "Contents" / "Resources" / "install_env.sh"
    with open(script_path, "w") as f:
        f.write(env_script)
    os.chmod(script_path, 0o755)

def create_readme(app_dir, include_models=False):
    """创建说明文档"""
    readme_content = f"""# VoiceRecognize Mac应用

## 应用信息
- **版本**: 1.0
- **大小**: {'完整版（包含所有模型）' if include_models else '轻量版（模型在线下载）'}
- **支持系统**: macOS 10.15+

## 安装说明

### 方法1：使用Conda环境（推荐）
1. 打开终端，进入应用目录
2. 运行安装脚本：
   ```bash
   cd VoiceRecognize.app/Contents/Resources
   chmod +x install_env.sh
   ./install_env.sh
   ```

### 方法2：手动安装
1. 创建Python环境：
   ```bash
   conda create -n voicerecognize python=3.11
   conda activate voicerecognize
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   conda install -c conda-forge ffmpeg
   ```

## 使用方法

1. **激活环境**：
   ```bash
   conda activate voicerecognize
   ```

2. **启动应用**：
   ```bash
   python app_batch.py
   ```

3. **访问界面**：
   打开浏览器访问：http://localhost:5002

## 功能特点

- ✅ 批量音频文件处理
- ✅ 多种Whisper模型选择
- ✅ 说话人分离（Pyannote）
- ✅ 实时进度显示
- ✅ 断点续传功能
- ✅ 结果预览和下载

## 模型说明

{'本版本包含所有预训练模型，无需额外下载。' if include_models else '首次使用时会自动下载所需模型，请确保网络连接正常。'}

## 注意事项

1. 首次运行可能需要下载模型文件
2. 建议使用GPU加速（如果可用）
3. 处理大文件时请耐心等待
4. 确保有足够的磁盘空间

## 技术支持

如有问题，请查看README.md文件或联系开发者。
"""
    
    readme_path = app_dir / "Contents" / "Resources" / "应用说明.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

def main():
    """主函数"""
    print("=== VoiceRecognize Mac应用打包工具 ===")
    print()
    print("请选择打包选项：")
    print("1. 轻量版（仅代码，模型在线下载）- 约50MB")
    print("2. 标准版（包含Whisper模型）- 约2.5GB")
    print("3. 完整版（包含所有模型）- 约11GB")
    print()
    
    while True:
        choice = input("请输入选择 (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("无效选择，请重新输入")
    
    # 确定打包选项
    include_models = choice in ["2", "3"]
    include_all_models = choice == "3"
    
    print(f"\n开始打包{'完整版' if include_all_models else '标准版' if include_models else '轻量版'}...")
    
    # 创建应用结构
    app_dir = create_app_structure()
    
    # 创建应用文件
    create_info_plist(app_dir)
    create_launcher_script(app_dir)
    create_conda_env_script(app_dir)
    
    # 复制项目文件
    copy_project_files(app_dir, include_models=include_models)
    
    # 创建说明文档
    create_readme(app_dir, include_models=include_models)
    
    # 计算大小
    app_size = subprocess.check_output(["du", "-sh", str(app_dir)]).decode().split()[0]
    
    print(f"\n✅ 打包完成！")
    print(f"📦 应用位置: {app_dir.absolute()}")
    print(f"📏 应用大小: {app_size}")
    print()
    print("使用方法：")
    print("1. 双击 VoiceRecognize.app 启动")
    print("2. 或使用终端：open VoiceRecognize.app")
    print()
    print("注意：首次使用需要安装Python环境，请查看应用内的说明文档。")

if __name__ == "__main__":
    main() 