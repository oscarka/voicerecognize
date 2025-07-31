#!/usr/bin/env python3
"""
创建DMG安装包
"""

import os
import subprocess
import shutil
from pathlib import Path

def create_dmg(app_path, dmg_name):
    """创建DMG文件"""
    print(f"正在创建DMG安装包: {dmg_name}")
    
    # 检查hdiutil是否可用
    try:
        subprocess.run(["hdiutil", "help"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 错误：hdiutil不可用，无法创建DMG")
        return False
    
    # 创建临时目录
    temp_dir = Path("temp_dmg")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 复制应用到临时目录
    app_name = app_path.name
    shutil.copytree(app_path, temp_dir / app_name)
    
    # 创建Applications的符号链接
    os.symlink("/Applications", temp_dir / "Applications")
    
    # 创建DMG
    try:
        cmd = [
            "hdiutil", "create",
            "-volname", "VoiceRecognize",
            "-srcfolder", str(temp_dir),
            "-ov",  # 覆盖现有文件
            dmg_name
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ DMG创建成功！")
        
        # 清理临时目录
        shutil.rmtree(temp_dir)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ DMG创建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    """主函数"""
    print("=== 创建DMG安装包 ===")
    
    # 查找应用文件
    app_files = list(Path(".").glob("*.app"))
    
    if not app_files:
        print("❌ 未找到.app文件")
        return
    
    print("找到以下应用文件：")
    for i, app in enumerate(app_files, 1):
        print(f"{i}. {app.name}")
    
    if len(app_files) == 1:
        selected_app = app_files[0]
    else:
        while True:
            try:
                choice = int(input(f"请选择要打包的应用 (1-{len(app_files)}): "))
                if 1 <= choice <= len(app_files):
                    selected_app = app_files[choice - 1]
                    break
                else:
                    print("无效选择")
            except ValueError:
                print("请输入数字")
    
    print(f"选择的应用: {selected_app.name}")
    
    # 创建DMG文件名
    dmg_name = f"{selected_app.stem}.dmg"
    
    # 创建DMG
    if create_dmg(selected_app, dmg_name):
        print(f"\n✅ DMG创建完成！")
        print(f"📦 文件位置: {Path(dmg_name).absolute()}")
        print()
        print("使用方法：")
        print("1. 双击DMG文件挂载")
        print("2. 将应用拖拽到Applications文件夹")
        print("3. 从Applications启动应用")
    else:
        print("❌ DMG创建失败")

if __name__ == "__main__":
    main() 