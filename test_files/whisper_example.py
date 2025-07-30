#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper使用示例
展示如何在项目中使用OpenAI Whisper进行语音识别
"""

import whisper
import os
from pathlib import Path

def transcribe_audio(audio_path, model_name="tiny", language=None, task="transcribe"):
    """
    转录音频文件
    
    Args:
        audio_path (str): 音频文件路径
        model_name (str): 模型名称 (tiny, base, small, medium, large, turbo)
        language (str): 语言代码，如"zh", "en", "ja"等
        task (str): 任务类型 ("transcribe" 或 "translate")
    
    Returns:
        dict: 转录结果
    """
    try:
        print(f"🎵 正在加载模型: {model_name}")
        model = whisper.load_model(model_name)
        
        print(f"📝 开始转录: {audio_path}")
        
        # 转录选项
        options = {
            "task": task,
            "verbose": True
        }
        
        if language:
            options["language"] = language
            print(f"🌍 指定语言: {language}")
        
        # 执行转录
        result = model.transcribe(audio_path, **options)
        
        return result
        
    except Exception as e:
        print(f"❌ 转录失败: {e}")
        return None

def save_transcription(result, output_path):
    """保存转录结果到文件"""
    if not result:
        return False
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=== Whisper转录结果 ===\n\n")
            f.write(f"检测到的语言: {result.get('language', '未知')}\n")
            f.write(f"语言概率: {result.get('language_probability', '未知')}\n\n")
            f.write("转录文本:\n")
            f.write(result['text'])
            
            # 如果有时间戳信息
            if 'segments' in result:
                f.write("\n\n详细时间戳:\n")
                for segment in result['segments']:
                    start = segment['start']
                    end = segment['end']
                    text = segment['text']
                    f.write(f"[{start:.2f}s - {end:.2f}s] {text}\n")
        
        print(f"✅ 转录结果已保存到: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    """主函数示例"""
    print("🎤 Whisper语音识别示例")
    print("=" * 40)
    
    # 示例音频文件路径（需要您提供实际的音频文件）
    audio_file = "example_audio.mp3"  # 请替换为实际文件路径
    
    if not os.path.exists(audio_file):
        print(f"⚠️  音频文件不存在: {audio_file}")
        print("请将音频文件放在当前目录，或修改audio_file变量")
        return
    
    # 选择模型（根据您的硬件选择）
    models = {
        "tiny": "最快，准确度较低，适合测试",
        "base": "较快，准确度一般",
        "small": "中等速度，较好准确度",
        "medium": "较慢，高准确度",
        "large": "最慢，最高准确度",
        "turbo": "优化版本，速度快，准确度高"
    }
    
    print("可用模型:")
    for model, desc in models.items():
        print(f"  {model}: {desc}")
    
    # 使用tiny模型进行演示
    model_name = "tiny"
    print(f"\n使用模型: {model_name}")
    
    # 执行转录
    result = transcribe_audio(
        audio_path=audio_file,
        model_name=model_name,
        language=None,  # 自动检测语言
        task="transcribe"  # 或 "translate" 用于翻译
    )
    
    if result:
        print("\n📋 转录结果:")
        print("-" * 30)
        print(f"检测语言: {result.get('language', '未知')}")
        print(f"语言概率: {result.get('language_probability', '未知')}")
        print(f"转录文本: {result['text']}")
        
        # 保存结果
        output_file = f"transcription_{model_name}.txt"
        save_transcription(result, output_file)
        
        # 显示详细时间戳
        if 'segments' in result:
            print("\n⏰ 详细时间戳:")
            for segment in result['segments']:
                start = segment['start']
                end = segment['end']
                text = segment['text'].strip()
                print(f"[{start:.2f}s - {end:.2f}s] {text}")
    else:
        print("❌ 转录失败")

def batch_transcribe(audio_dir, model_name="tiny"):
    """批量转录目录中的音频文件"""
    audio_dir = Path(audio_dir)
    if not audio_dir.exists():
        print(f"❌ 目录不存在: {audio_dir}")
        return
    
    # 支持的音频格式
    audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
    
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(audio_dir.glob(f"*{ext}"))
    
    if not audio_files:
        print(f"❌ 在 {audio_dir} 中未找到音频文件")
        return
    
    print(f"🎵 找到 {len(audio_files)} 个音频文件")
    
    for audio_file in audio_files:
        print(f"\n处理文件: {audio_file.name}")
        result = transcribe_audio(str(audio_file), model_name)
        
        if result:
            output_file = audio_file.with_suffix('.txt')
            save_transcription(result, str(output_file))

if __name__ == "__main__":
    # 运行单个文件转录示例
    main()
    
    # 批量转录示例（取消注释以使用）
    # batch_transcribe("audio_files", "tiny") 