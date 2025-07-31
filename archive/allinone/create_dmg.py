#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VoiceRecognize DMG打包脚本
将voicere.py打包成可双击安装的DMG文件
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

def check_requirements():
    """检查打包所需工具"""
    print("🔍 检查打包工具...")
    
    # 检查hdiutil (macOS自带)
    try:
        subprocess.run(['hdiutil', 'help'], capture_output=True, check=True)
        print("✅ hdiutil 可用")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ hdiutil 不可用，请确保在macOS系统上运行")
        return False
    
    # 检查create-dmg (需要安装)
    try:
        subprocess.run(['create-dmg', '--version'], capture_output=True, check=True)
        print("✅ create-dmg 可用")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  create-dmg 未安装，将使用系统自带工具")
        return True
    
    return True

def create_app_structure():
    """创建应用程序结构"""
    print("📦 创建应用程序结构...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="voicerecognize_")
    app_dir = os.path.join(temp_dir, "VoiceRecognize.app")
    contents_dir = os.path.join(app_dir, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    resources_dir = os.path.join(contents_dir, "Resources")
    
    # 创建目录结构
    os.makedirs(macos_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)
    
    # 复制主脚本
    script_path = "archive/allinone/voicere.py"
    if not os.path.exists(script_path):
        print(f"❌ 找不到脚本文件: {script_path}")
        return None
    
    app_script = os.path.join(macos_dir, "VoiceRecognize")
    shutil.copy2(script_path, app_script)
    os.chmod(app_script, 0o755)  # 添加执行权限
    
    # 创建Info.plist
    info_plist = os.path.join(contents_dir, "Info.plist")
    plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>VoiceRecognize</string>
    <key>CFBundleIdentifier</key>
    <string>com.voicerecognize.app</string>
    <key>CFBundleName</key>
    <string>VoiceRecognize</string>
    <key>CFBundleDisplayName</key>
    <string>VoiceRecognize 语音识别</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.utilities</string>
    <key>NSAppleEventsUsageDescription</key>
    <string>VoiceRecognize需要访问系统功能来运行语音识别服务</string>
</dict>
</plist>'''
    
    with open(info_plist, 'w', encoding='utf-8') as f:
        f.write(plist_content)
    
    # 创建图标文件（如果有的话）
    icon_path = os.path.join(resources_dir, "AppIcon.icns")
    if os.path.exists("archive/allinone/icon.icns"):
        shutil.copy2("archive/allinone/icon.icns", icon_path)
        # 更新Info.plist添加图标
        plist_content = plist_content.replace('</dict>', '''    <key>CFBundleIconFile</key>
    <string>AppIcon.icns</string>
</dict>''')
        with open(info_plist, 'w', encoding='utf-8') as f:
            f.write(plist_content)
    
    print(f"✅ 应用程序结构创建完成: {app_dir}")
    return temp_dir

def create_installer_script():
    """创建安装脚本"""
    print("📝 创建安装脚本...")
    
    installer_script = '''#!/bin/bash
# VoiceRecognize 安装脚本

echo "🎤 VoiceRecognize 语音识别应用安装程序"
echo "=================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "安装脚本位置: $SCRIPT_DIR"

# 检查是否已安装
if [ -d "/Applications/VoiceRecognize.app" ]; then
    echo "⚠️  检测到已安装的VoiceRecognize应用"
    read -p "是否要覆盖安装？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消"
        exit 0
    fi
    echo "正在移除旧版本..."
    rm -rf "/Applications/VoiceRecognize.app"
fi

# 检查源文件是否存在
if [ ! -d "$SCRIPT_DIR/VoiceRecognize.app" ]; then
    echo "❌ 错误: 找不到 VoiceRecognize.app"
    echo "请确保在DMG挂载后运行此脚本"
    read -p "按任意键退出..." -n 1
    exit 1
fi

# 复制应用到Applications
echo "📦 正在安装VoiceRecognize..."
cp -R "$SCRIPT_DIR/VoiceRecognize.app" "/Applications/"

# 检查复制是否成功
if [ ! -d "/Applications/VoiceRecognize.app" ]; then
    echo "❌ 安装失败: 无法复制应用到 /Applications/"
    read -p "按任意键退出..." -n 1
    exit 1
fi

# 设置权限
chmod +x "/Applications/VoiceRecognize.app/Contents/MacOS/VoiceRecognize"

echo "✅ 安装完成！"
echo ""
echo "🎉 VoiceRecognize 已成功安装到 /Applications/"
echo ""
echo "使用方法："
echo "1. 打开 Finder"
echo "2. 进入 应用程序 文件夹"
echo "3. 双击 VoiceRecognize 图标启动应用"
echo ""
echo "首次运行时会自动安装必要的依赖，请耐心等待..."
echo ""
read -p "按任意键退出..." -n 1
'''
    
    return installer_script

def create_dmg_with_system_tools(app_path, output_name="VoiceRecognize.dmg"):
    """使用系统工具创建DMG"""
    print(f"🔧 使用系统工具创建DMG: {output_name}")
    
    # 创建临时DMG
    temp_dmg = "temp_voicerecognize.dmg"
    
    # 计算所需空间（MB）
    app_size = sum(f.stat().st_size for f in Path(app_path).rglob('*') if f.is_file())
    dmg_size = max(100, app_size // (1024 * 1024) + 50)  # 至少100MB
    
    try:
        # 创建临时DMG
        print(f"创建临时DMG，大小: {dmg_size}MB")
        subprocess.run([
            'hdiutil', 'create', '-size', f'{dmg_size}m', '-fs', 'HFS+',
            '-volname', 'VoiceRecognize', '-attach', temp_dmg
        ], check=True)
        
        # 获取初始挂载点
        result = subprocess.run(['hdiutil', 'info'], capture_output=True, text=True, check=True)
        mount_point = None
        for line in result.stdout.split('\n'):
            if 'VoiceRecognize' in line and '/Volumes/' in line:
                mount_point = line.split()[-1]
                break
        
        if not mount_point:
            print("❌ 无法找到挂载点")
            return False
        
        print(f"初始挂载点: {mount_point}")
        
        # 重新挂载为可写模式
        subprocess.run(['hdiutil', 'detach', mount_point], check=True)
        subprocess.run([
            'hdiutil', 'attach', temp_dmg, '-readwrite'
        ], check=True)
        
        # 重新获取挂载点
        result = subprocess.run(['hdiutil', 'info'], capture_output=True, text=True, check=True)
        mount_point = None
        for line in result.stdout.split('\n'):
            if 'VoiceRecognize' in line and '/Volumes/' in line:
                parts = line.split()
                for part in parts:
                    if part.startswith('/Volumes/'):
                        mount_point = part
                        break
                if mount_point:
                    break
        
        if not mount_point:
            print("❌ 无法找到重新挂载点")
            return False
        
        print(f"可写挂载点: {mount_point}")
        
        # 检查挂载点是否可写
        test_file = os.path.join(mount_point, "test_write")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print("✅ 挂载点可写")
        except Exception as e:
            print(f"❌ 挂载点只读: {e}")
            return False
        
        # 复制应用程序
        app_dest = os.path.join(mount_point, "VoiceRecognize.app")
        if os.path.exists(app_dest):
            try:
                shutil.rmtree(app_dest)
            except Exception as e:
                print(f"⚠️  无法删除现有文件: {e}")
                # 尝试强制删除
                subprocess.run(['rm', '-rf', app_dest], check=True)
        shutil.copytree(app_path, app_dest)
        
        # 创建安装脚本
        installer_script = create_installer_script()
        installer_path = os.path.join(mount_point, "安装VoiceRecognize.command")
        with open(installer_path, 'w', encoding='utf-8') as f:
            f.write(installer_script)
        os.chmod(installer_path, 0o755)
        
        # 创建Applications文件夹的快捷方式
        apps_link = os.path.join(mount_point, "Applications")
        if not os.path.exists(apps_link):
            os.symlink("/Applications", apps_link)
        
        # 创建说明文件
        readme_content = '''🎤 VoiceRecognize 语音识别应用

安装说明：
1. 双击 "安装VoiceRecognize.command" 开始安装
2. 按照提示完成安装
3. 安装完成后，在应用程序文件夹中找到 VoiceRecognize 应用
4. 双击启动应用

系统要求：
- macOS 10.13 或更高版本
- 需要安装 Miniconda（如果没有会自动提示安装）

注意事项：
- 首次运行时会自动安装Python依赖，请保持网络连接
- 安装过程可能需要几分钟时间，请耐心等待
- 如果遇到权限问题，请在系统偏好设置中允许应用运行

技术支持：
如有问题，请检查：
1. 网络连接是否正常
2. 是否有足够的磁盘空间
3. 系统权限设置是否正确
'''
        
        readme_path = os.path.join(mount_point, "安装说明.txt")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # 卸载DMG
        subprocess.run(['hdiutil', 'detach', mount_point], check=True)
        
        # 转换为压缩DMG
        print("压缩DMG文件...")
        subprocess.run([
            'hdiutil', 'convert', temp_dmg, '-format', 'UDZO',
            '-o', output_name
        ], check=True)
        
        # 清理临时文件
        os.remove(temp_dmg)
        
        print(f"✅ DMG创建成功: {output_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ DMG创建失败: {e}")
        # 清理
        if os.path.exists(temp_dmg):
            os.remove(temp_dmg)
        return False

def main():
    """主函数"""
    print("=== VoiceRecognize DMG打包工具 ===")
    
    # 检查系统
    if sys.platform != "darwin":
        print("❌ 此脚本只能在macOS系统上运行")
        return 1
    
    # 检查工具
    if not check_requirements():
        return 1
    
    # 创建应用结构
    temp_dir = create_app_structure()
    if not temp_dir:
        return 1
    
    try:
        app_path = os.path.join(temp_dir, "VoiceRecognize.app")
        
        # 创建DMG
        output_name = "VoiceRecognize_安装包.dmg"
        if create_dmg_with_system_tools(app_path, output_name):
            print(f"\n🎉 打包完成！")
            print(f"📦 DMG文件: {output_name}")
            print(f"📁 位置: {os.path.abspath(output_name)}")
            print(f"\n💡 使用方法:")
            print(f"1. 双击 {output_name} 挂载DMG")
            print(f"2. 双击 '安装VoiceRecognize.command' 开始安装")
            print(f"3. 按照提示完成安装")
            print(f"4. 在应用程序文件夹中找到 VoiceRecognize 应用")
        else:
            print("❌ DMG创建失败")
            return 1
            
    finally:
        # 清理临时文件
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 