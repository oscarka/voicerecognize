#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用medium模型进行高质量转录
"""

import whisper
import time
import os

def transcribe_with_medium(audio_path):
    """使用medium模型转录音频"""
    print("🎵 使用medium模型进行高质量转录")
    print(f"📁 音频文件: {audio_path}")
    print("=" * 50)
    
    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        return None
    
    try:
        # 1. 加载medium模型
        print("🔄 正在加载medium模型...")
        start_load = time.time()
        model = whisper.load_model("medium")
        load_time = time.time() - start_load
        print(f"✅ medium模型加载完成，耗时: {load_time:.2f}秒")
        
        # 2. 执行转录
        print("📝 开始高质量转录...")
        start_transcribe = time.time()
        result = model.transcribe(
            audio_path,
            verbose=True,  # 显示详细进度
            word_timestamps=True  # 获取词级时间戳
        )
        transcribe_time = time.time() - start_transcribe
        
        print(f"✅ 转录完成，耗时: {transcribe_time:.2f}秒")
        
        # 3. 显示结果
        print(f"\n📋 转录结果:")
        print("-" * 40)
        print(f"检测语言: {result.get('language', '未知')}")
        print(f"语言概率: {result.get('language_probability', '未知')}")
        print(f"转录文本长度: {len(result['text'])} 字符")
        print(f"\n转录文本:")
        print(result['text'])
        
        # 4. 保存结果
        output_file = "transcription_medium_high_quality.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== Whisper Medium模型高质量转录结果 ===\n")
            f.write(f"音频文件: {audio_path}\n")
            f.write(f"使用模型: medium\n")
            f.write(f"检测语言: {result.get('language', '未知')}\n")
            f.write(f"语言概率: {result.get('language_probability', '未知')}\n")
            f.write(f"转录时间: {transcribe_time:.2f}秒\n")
            f.write(f"文本长度: {len(result['text'])} 字符\n\n")
            f.write("转录文本:\n")
            f.write(result['text'])
            
            # 保存详细时间戳
            if 'segments' in result and result['segments']:
                f.write("\n\n详细时间戳:\n")
                for segment in result['segments']:
                    start = segment['start']
                    end = segment['end']
                    text = segment['text']
                    f.write(f"[{start:.2f}s - {end:.2f}s] {text}\n")
        
        print(f"\n💾 高质量转录结果已保存到: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ 转录失败: {e}")
        return None

def main():
    """主函数"""
    audio_file = "ba84462e-fdee-42fe-9439-86808b3d3212.wav"
    
    print("🚀 Medium模型高质量转录测试")
    print("=" * 50)
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return
    
    print(f"✅ 找到音频文件: {audio_file}")
    print("⚠️  注意: medium模型较大，加载和转录时间会较长")
    
    # 执行转录
    result = transcribe_with_medium(audio_file)
    
    if result:
        print("\n🎉 Medium模型转录完成！")
        print("💡 建议对比之前的结果查看质量提升")
    else:
        print("\n❌ 转录失败")

if __name__ == "__main__":
    main() 