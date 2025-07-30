#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper本地运行测试脚本
用于验证环境是否支持OpenAI Whisper
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    if version.major == 3 and 8 <= version.minor <= 11:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本不兼容: {version.major}.{version.minor}.{version.micro}")
        print("   需要Python 3.8-3.11")
        return False

def check_ffmpeg():
    """检查FFmpeg是否安装"""
    print("🔍 检查FFmpeg...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
            return True
        else:
            print("❌ FFmpeg未正确安装")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg未安装")
        print("   请安装FFmpeg:")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ 检查FFmpeg时出错: {e}")
        return False

def check_whisper_installation():
    """检查Whisper是否已安装"""
    print("🔍 检查Whisper安装...")
    try:
        import whisper
        print("✅ Whisper已安装")
        return True
    except ImportError:
        print("❌ Whisper未安装")
        print("   请运行: pip install -U openai-whisper")
        return False

def test_whisper_basic():
    """基础Whisper功能测试"""
    print("🔍 测试Whisper基础功能...")
    try:
        import whisper
        
        # 加载小模型进行测试
        print("   正在加载tiny模型...")
        model = whisper.load_model("tiny")
        print("✅ 模型加载成功")
        
        # 检查可用模型
        available_models = ["tiny", "base", "small", "medium", "large", "turbo"]
        print(f"   可用模型: {', '.join(available_models)}")
        
        return True
    except Exception as e:
        print(f"❌ Whisper测试失败: {e}")
        return False

def check_system_resources():
    """检查系统资源"""
    print("🔍 检查系统资源...")
    
    # 检查内存
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"   系统内存: {memory_gb:.1f}GB")
        
        if memory_gb >= 8:
            print("✅ 内存充足")
        else:
            print("⚠️  内存可能不足，建议至少8GB")
    except ImportError:
        print("⚠️  无法检查内存（需要psutil包）")
    
    # 检查GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"✅ 检测到GPU: {gpu_count}个设备")
            print(f"   GPU显存: {gpu_memory:.1f}GB")
        else:
            print("⚠️  未检测到CUDA GPU，将使用CPU运行（速度较慢）")
    except ImportError:
        print("⚠️  无法检查GPU（需要PyTorch）")

def main():
    """主测试函数"""
    print("🚀 Whisper本地运行环境测试")
    print("=" * 50)
    
    tests = [
        check_python_version,
        check_ffmpeg,
        check_whisper_installation,
        test_whisper_basic,
        check_system_resources
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 环境检查通过！可以运行Whisper")
        print("\n📝 使用示例:")
        print("import whisper")
        print("model = whisper.load_model('tiny')")
        print("result = model.transcribe('audio.mp3')")
        print("print(result['text'])")
    else:
        print("⚠️  环境检查未完全通过，请解决上述问题后再试")

if __name__ == "__main__":
    main() 