#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频转录测试脚本
使用Whisper转录指定的音频文件
"""

import whisper
import time
import os

def transcribe_audio_file(audio_path, model_name="tiny"):
    """
    转录音频文件
    
    Args:
        audio_path (str): 音频文件路径
        model_name (str): 模型名称 (tiny, base, small)
    """
    print(f"🎵 开始转录音频文件: {audio_path}")
    print(f"🤖 使用模型: {model_name}")
    print("=" * 50)
    
    # 检查文件是否存在
    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        return None
    
    try:
        # 1. 加载模型
        print(f"🔄 正在加载 {model_name} 模型...")
        start_load = time.time()
        model = whisper.load_model(model_name)
        load_time = time.time() - start_load
        print(f"✅ 模型加载完成，耗时: {load_time:.2f}秒")
        
        # 2. 执行转录
        print(f"📝 开始转录...")
        start_transcribe = time.time()
        result = model.transcribe(audio_path)
        transcribe_time = time.time() - start_transcribe
        
        print(f"✅ 转录完成，耗时: {transcribe_time:.2f}秒")
        
        # 3. 显示结果
        print(f"\n📋 转录结果:")
        print("-" * 30)
        print(f"检测语言: {result.get('language', '未知')}")
        print(f"语言概率: {result.get('language_probability', '未知')}")
        print(f"转录文本: {result['text']}")
        
        # 4. 显示详细时间戳（如果有）
        if 'segments' in result and result['segments']:
            print(f"\n⏰ 详细时间戳:")
            for segment in result['segments']:
                start = segment['start']
                end = segment['end']
                text = segment['text'].strip()
                print(f"[{start:.2f}s - {end:.2f}s] {text}")
        
        # 5. 保存结果到文件
        output_file = f"transcription_{model_name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Whisper转录结果 ===\n")
            f.write(f"音频文件: {audio_path}\n")
            f.write(f"使用模型: {model_name}\n")
            f.write(f"检测语言: {result.get('language', '未知')}\n")
            f.write(f"语言概率: {result.get('language_probability', '未知')}\n")
            f.write(f"转录时间: {transcribe_time:.2f}秒\n\n")
            f.write("转录文本:\n")
            f.write(result['text'])
            
            if 'segments' in result and result['segments']:
                f.write("\n\n详细时间戳:\n")
                for segment in result['segments']:
                    start = segment['start']
                    end = segment['end']
                    text = segment['text']
                    f.write(f"[{start:.2f}s - {end:.2f}s] {text}\n")
        
        print(f"\n💾 转录结果已保存到: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ 转录失败: {e}")
        return None

def compare_models(audio_path):
    """比较不同模型的转录效果"""
    print(f"🔍 模型对比测试")
    print(f"音频文件: {audio_path}")
    print("=" * 50)
    
    models_to_test = ["tiny", "base", "small"]
    results = {}
    
    for model_name in models_to_test:
        print(f"\n🔄 测试 {model_name} 模型...")
        result = transcribe_audio_file(audio_path, model_name)
        if result:
            results[model_name] = result
    
    # 显示对比结果
    if results:
        print(f"\n📊 模型对比总结:")
        print("-" * 50)
        for model_name, result in results.items():
            print(f"\n{model_name.upper()} 模型:")
            print(f"  语言: {result.get('language', '未知')}")
            print(f"  文本: {result['text'][:100]}{'...' if len(result['text']) > 100 else ''}")

def main():
    """主函数"""
    # 使用您提供的音频文件
    audio_file = "ba84462e-fdee-42fe-9439-86808b3d3212.wav"
    
    print("🚀 Whisper音频转录测试")
    print("=" * 50)
    
    # 检查文件
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        print("请确保音频文件在当前目录中")
        return
    
    print(f"✅ 找到音频文件: {audio_file}")
    
    # 选择测试模式
    print("\n请选择测试模式:")
    print("1. 单个模型测试 (tiny)")
    print("2. 模型对比测试 (tiny, base, small)")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        # 单个模型测试
        transcribe_audio_file(audio_file, "tiny")
    elif choice == "2":
        # 模型对比测试
        compare_models(audio_file)
    else:
        print("❌ 无效选择，使用默认模式")
        transcribe_audio_file(audio_file, "tiny")

if __name__ == "__main__":
    main() 