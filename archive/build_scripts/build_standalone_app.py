#!/usr/bin/env python3
"""
构建独立应用程序脚本
使用PyInstaller创建完全独立的应用程序
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    print("📦 安装PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../archive/VoiceRecognize_轻量版.app/Contents/Resources/app_batch.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../archive/VoiceRecognize_轻量版.app/Contents/Resources/templates', 'templates'),
        ('../archive/VoiceRecognize_轻量版.app/Contents/Resources/uploads', 'uploads'),
        ('../archive/VoiceRecognize_轻量版.app/Contents/Resources/processed', 'processed'),
        ('../archive/VoiceRecognize_轻量版.app/Contents/Resources/temp', 'temp'),
    ],
    hiddenimports=[
        'flask',
        'whisper',
        'torch',
        'torchaudio',
        'numpy',
        'soundfile',
        'psutil',
        'webbrowser',
        'werkzeug',
        'jinja2',
        'requests',
        'threading',
        'queue',
        'pathlib',
        'json',
        'time',
        'subprocess',
        'shutil',
        'socket'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceRecognize',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
'''
    
    with open('VoiceRecognize.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ 创建spec文件完成")

def build_app():
    """构建应用程序"""
    print("🔨 开始构建应用程序...")
    
    # 使用PyInstaller构建
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name=VoiceRecognize",
        "--add-data=../archive/VoiceRecognize_轻量版.app/Contents/Resources/templates:templates",
        "--add-data=../archive/VoiceRecognize_轻量版.app/Contents/Resources/uploads:uploads",
        "--add-data=../archive/VoiceRecognize_轻量版.app/Contents/Resources/processed:processed",
        "--add-data=../archive/VoiceRecognize_轻量版.app/Contents/Resources/temp:temp",
        "../archive/VoiceRecognize_轻量版.app/Contents/Resources/app_batch.py"
    ], check=True)
    
    print("✅ 应用程序构建完成")

def create_macos_app():
    """创建macOS应用程序包"""
    print("🍎 创建macOS应用程序包...")
    
    # 创建应用程序包结构
    app_name = "VoiceRecognize.app"
    app_path = Path(app_name)
    
    if app_path.exists():
        shutil.rmtree(app_path)
    
    # 创建目录结构
    (app_path / "Contents" / "MacOS").mkdir(parents=True, exist_ok=True)
    (app_path / "Contents" / "Resources").mkdir(parents=True, exist_ok=True)
    
    # 复制可执行文件
    shutil.copy("dist/VoiceRecognize", app_path / "Contents" / "MacOS" / "VoiceRecognize")
    
    # 创建Info.plist
    info_plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>VoiceRecognize</string>
    <key>CFBundleIdentifier</key>
    <string>com.voicerecognize.app</string>
    <key>CFBundleName</key>
    <string>VoiceRecognize</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>'''
    
    with open(app_path / "Contents" / "Info.plist", 'w', encoding='utf-8') as f:
        f.write(info_plist)
    
    print("✅ macOS应用程序包创建完成")

def main():
    """主函数"""
    print("=== VoiceRecognize 独立应用构建器 ===\n")
    
    try:
        # 1. 安装PyInstaller
        install_pyinstaller()
        
        # 2. 构建应用程序
        build_app()
        
        # 3. 创建macOS应用程序包
        create_macos_app()
        
        print("\n🎉 构建完成！")
        print("📁 应用程序位置: VoiceRecognize.app")
        print("💡 双击VoiceRecognize.app即可运行")
        
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 