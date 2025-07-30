#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper功能演示脚本
展示Whisper的基本功能和使用方法
"""

import whisper
import os
import time

def demo_whisper_basic():
    """演示Whisper基本功能"""
    print("🎤 Whisper功能演示")
    print("=" * 50)
    
    # 1. 显示可用模型
    print("📋 可用模型:")
    models = whisper.available_models()
    for model in models:
        print(f"  - {model}")
    
    # 2. 加载模型
    print(f"\n🔄 正在加载tiny模型...")
    start_time = time.time()
    model = whisper.load_model("tiny")
    load_time = time.time() - start_time
    print(f"✅ 模型加载完成，耗时: {load_time:.2f}秒")
    
    # 3. 显示模型信息
    print(f"\n📊 模型信息:")
    print(f"  设备: {model.device}")
    print(f"  模型维度: {model.dims}")
    
    return model

def demo_transcription_with_sample():
    """演示转录功能（使用示例文本）"""
    print("\n🎵 转录功能演示")
    print("-" * 30)
    
    # 创建一个简单的测试音频文件（使用系统命令生成）
    test_audio = "test_audio.wav"
    
    # 使用say命令生成测试音频（macOS系统命令）
    print("🔊 生成测试音频...")
    os.system(f'say -o {test_audio} "Hello, this is a test of OpenAI Whisper speech recognition."')
    
    if os.path.exists(test_audio):
        print(f"✅ 测试音频已生成: {test_audio}")
        
        # 加载模型
        model = whisper.load_model("tiny")
        
        # 执行转录
        print("📝 开始转录...")
        start_time = time.time()
        result = model.transcribe(test_audio)
        transcribe_time = time.time() - start_time
        
        print(f"✅ 转录完成，耗时: {transcribe_time:.2f}秒")
        print(f"📋 转录结果: {result['text']}")
        
        # 清理测试文件
        os.remove(test_audio)
        print("🧹 测试文件已清理")
        
        return result
    else:
        print("❌ 无法生成测试音频")
        return None

def demo_language_detection():
    """演示语言检测功能"""
    print("\n🌍 语言检测功能演示")
    print("-" * 30)
    
    # 创建中文测试音频
    test_audio_cn = "test_audio_cn.wav"
    os.system(f'say -o {test_audio_cn} -v Ting-Ting "你好，这是一个语音识别测试。"')
    
    if os.path.exists(test_audio_cn):
        model = whisper.load_model("tiny")
        
        # 加载音频
        audio = whisper.load_audio(test_audio_cn)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # 检测语言
        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        
        print(f"🔍 检测到的语言: {detected_lang}")
        print(f"📊 语言概率分布:")
        for lang, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {lang}: {prob:.3f}")
        
        # 清理
        os.remove(test_audio_cn)
        return detected_lang
    else:
        print("❌ 无法生成中文测试音频")
        return None

def demo_model_comparison():
    """演示不同模型的性能对比"""
    print("\n⚡ 模型性能对比")
    print("-" * 30)
    
    # 创建测试音频
    test_audio = "test_audio_compare.wav"
    os.system(f'say -o {test_audio} "This is a performance comparison test for different Whisper models."')
    
    if not os.path.exists(test_audio):
        print("❌ 无法生成测试音频")
        return
    
    models_to_test = ["tiny", "base", "small"]
    results = {}
    
    for model_name in models_to_test:
        print(f"\n🔄 测试模型: {model_name}")
        
        # 加载模型
        start_load = time.time()
        model = whisper.load_model(model_name)
        load_time = time.time() - start_load
        
        # 转录
        start_transcribe = time.time()
        result = model.transcribe(test_audio)
        transcribe_time = time.time() - start_transcribe
        
        results[model_name] = {
            "load_time": load_time,
            "transcribe_time": transcribe_time,
            "text": result["text"]
        }
        
        print(f"  加载时间: {load_time:.2f}秒")
        print(f"  转录时间: {transcribe_time:.2f}秒")
        print(f"  转录结果: {result['text']}")
    
    # 清理
    os.remove(test_audio)
    
    # 显示对比结果
    print(f"\n📊 性能对比总结:")
    print(f"{'模型':<10} {'加载时间':<12} {'转录时间':<12} {'总时间':<12}")
    print("-" * 50)
    for model_name, data in results.items():
        total_time = data["load_time"] + data["transcribe_time"]
        print(f"{model_name:<10} {data['load_time']:<12.2f} {data['transcribe_time']:<12.2f} {total_time:<12.2f}")

def main():
    """主演示函数"""
    print("🚀 OpenAI Whisper 功能演示")
    print("=" * 60)
    
    try:
        # 1. 基本功能演示
        model = demo_whisper_basic()
        
        # 2. 转录功能演示
        demo_transcription_with_sample()
        
        # 3. 语言检测演示
        demo_language_detection()
        
        # 4. 模型性能对比
        demo_model_comparison()
        
        print("\n🎉 所有演示完成！")
        print("\n💡 使用建议:")
        print("  - 开发测试: 使用 tiny 或 base 模型")
        print("  - 日常使用: 使用 turbo 模型")
        print("  - 高质量需求: 使用 large 模型")
        print("  - 中文识别: 建议使用 medium 或 large 模型")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")

if __name__ == "__main__":
    main() 