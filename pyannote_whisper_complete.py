#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pyannote + Whisper 完整实现
"""

import os
import whisper
import torch
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import json
import time

def setup_pyannote():
    """设置Pyannote"""
    # 需要设置环境变量: export HF_TOKEN=your_token
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("请设置HF_TOKEN环境变量")
    
    print("🔄 加载Pyannote模型...")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=hf_token
    )
    return pipeline

def diarize_audio(audio_path, pipeline):
    """说话人分离"""
    print("🎯 开始说话人分离...")
    
    with ProgressHook() as hook:
        diarization = pipeline(audio_path, hook=hook)
    
    return diarization

def transcribe_with_whisper(audio_path, segments, model_name="small"):
    """使用Whisper转录"""
    print(f"📝 使用Whisper {model_name}模型转录...")
    
    # 加载Whisper模型
    model = whisper.load_model(model_name)
    
    results = []
    
    for i, segment in enumerate(segments):
        start_time = segment["start"]
        end_time = segment["end"]
        speaker = segment["speaker"]
        
        print(f"🔄 转录片段 {i+1}/{len(segments)}: {start_time:.1f}s - {end_time:.1f}s")
        
        # 转录
        result = model.transcribe(
            audio_path,
            start=start_time,
            end=end_time,
            verbose=False
        )
        
        results.append({
            "speaker": speaker,
            "start": start_time,
            "end": end_time,
            "text": result["text"].strip()
        })
    
    return results

def main():
    """主函数"""
    audio_file = "ba84462e-fdee-42fe-9439-86808b3d3212.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return
    
    print("🚀 Pyannote + Whisper 完整流程")
    print("=" * 50)
    
    # 1. 设置Pyannote
    try:
        pipeline = setup_pyannote()
        print("✅ Pyannote模型加载完成")
    except Exception as e:
        print(f"❌ Pyannote设置失败: {e}")
        print("💡 请设置HF_TOKEN环境变量")
        return
    
    # 2. 说话人分离
    try:
        diarization = diarize_audio(audio_file, pipeline)
        print("✅ 说话人分离完成")
        
        # 提取片段信息
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })
        
        print(f"📋 识别到 {len(segments)} 个说话片段")
        
    except Exception as e:
        print(f"❌ 说话人分离失败: {e}")
        return
    
    # 3. 转录
    try:
        results = transcribe_with_whisper(audio_file, segments, "small")
        print("✅ 转录完成")
    except Exception as e:
        print(f"❌ 转录失败: {e}")
        return
    
    # 4. 保存结果
    output_file = "pyannote_whisper_complete.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== Pyannote + Whisper 完整转录结果 ===\n\n")
        f.write("使用模型:\n")
        f.write("- Pyannote: pyannote/speaker-diarization\n")
        f.write("- Whisper: small\n\n")
        
        for result in results:
            f.write(f"[{result['start']:.1f}s - {result['end']:.1f}s] {result['speaker']}: {result['text']}\n")
    
    print(f"\n💾 结果已保存到: {output_file}")
    
    # 显示结果预览
    print("\n📋 转录结果预览:")
    print("-" * 40)
    for result in results[:5]:  # 只显示前5个片段
        print(f"[{result['start']:.1f}s - {result['end']:.1f}s] {result['speaker']}: {result['text']}")

if __name__ == "__main__":
    main()
