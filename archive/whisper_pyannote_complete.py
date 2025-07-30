#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper + Pyannote 完整实现
"""

import whisper
import torch
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import json
import os

def setup_pyannote():
    """设置Pyannote"""
    # 需要从HuggingFace获取访问令牌
    # https://huggingface.co/pyannote/speaker-diarization
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token="YOUR_HF_TOKEN"
    )
    return pipeline

def diarize_audio(audio_path, pipeline):
    """说话人分离"""
    print("🎯 开始说话人分离...")
    
    with ProgressHook() as hook:
        diarization = pipeline(audio_path, hook=hook)
    
    return diarization

def transcribe_segments(audio_path, diarization, model_name="small"):
    """转录音频片段"""
    print("📝 开始语音转录...")
    
    # 加载Whisper模型
    model = whisper.load_model(model_name)
    
    results = []
    
    # 为每个说话人片段进行转录
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_time = turn.start
        end_time = turn.end
        
        # 提取音频片段
        # 这里需要实现音频片段提取逻辑
        
        # 转录
        result = model.transcribe(audio_path, start=start_time, end=end_time)
        
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
    
    print("🚀 Whisper + Pyannote 完整流程")
    print("=" * 50)
    
    # 1. 设置Pyannote
    try:
        pipeline = setup_pyannote()
        print("✅ Pyannote设置完成")
    except Exception as e:
        print(f"❌ Pyannote设置失败: {e}")
        print("💡 需要从HuggingFace获取访问令牌")
        return
    
    # 2. 说话人分离
    try:
        diarization = diarize_audio(audio_file, pipeline)
        print("✅ 说话人分离完成")
    except Exception as e:
        print(f"❌ 说话人分离失败: {e}")
        return
    
    # 3. 转录
    try:
        results = transcribe_segments(audio_file, diarization)
        print("✅ 转录完成")
    except Exception as e:
        print(f"❌ 转录失败: {e}")
        return
    
    # 4. 保存结果
    output_file = "whisper_pyannote_complete.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== Whisper + Pyannote 完整转录结果 ===\n\n")
        
        for result in results:
            f.write(f"[{result['start']:.1f}s - {result['end']:.1f}s] {result['speaker']}: {result['text']}\n")
    
    print(f"\n💾 结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
