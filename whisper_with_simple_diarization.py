#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper + 简化说话人分离演示
由于Pyannote需要接受条款，先创建一个简化版本展示效果
"""
import os
import sys
import time
import json
import subprocess
from pathlib import Path
import whisper

def simulate_diarization(audio_file):
    """模拟说话人分离 - 基于时间间隔分割"""
    print("=== 使用时间间隔模拟说话人分离 ===")
    
    # 获取音频时长
    cmd = [
        "ffprobe", "-v", "quiet", "-show_entries", 
        "format=duration", "-of", "csv=p=0", audio_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        print(f"音频总时长: {duration:.2f}秒")
    except:
        duration = 438.36  # 使用已知时长
        print(f"使用默认时长: {duration:.2f}秒")
    
    # 模拟说话人分离 - 每30秒切换一次说话人
    segments = []
    segment_duration = 30  # 每30秒一个片段
    current_time = 0
    
    while current_time < duration:
        end_time = min(current_time + segment_duration, duration)
        speaker = "SPEAKER_01" if len(segments) % 2 == 0 else "SPEAKER_02"
        
        segments.append({
            'start': current_time,
            'end': end_time,
            'speaker': speaker
        })
        
        current_time = end_time
    
    print(f"模拟生成 {len(segments)} 个语音片段")
    return segments

def run_whisper_with_diarization(audio_file):
    """运行Whisper + 说话人分离"""
    print(f"\n=== 开始处理音频: {audio_file} ===")
    
    # 1. 初始化Whisper模型
    print("1. 加载Whisper模型...")
    start_time = time.time()
    whisper_model = whisper.load_model("small")
    whisper_load_time = time.time() - start_time
    print(f"   Whisper模型加载完成，耗时: {whisper_load_time:.2f}秒")
    
    # 2. 模拟说话人分离
    print("2. 执行说话人分离...")
    start_time = time.time()
    segments = simulate_diarization(audio_file)
    diarization_time = time.time() - start_time
    print(f"   说话人分离完成，耗时: {diarization_time:.2f}秒")
    
    # 3. 对每个片段进行转录
    print("3. 对每个片段进行转录...")
    transcription_results = []
    total_transcribe_time = 0
    
    for i, segment in enumerate(segments):
        print(f"   处理片段 {i+1}/{len(segments)}: {segment['start']:.1f}s - {segment['end']:.1f}s ({segment['speaker']})")
        
        # 使用ffmpeg提取音频片段
        segment_file = f"temp_segment_{i}.wav"
        
        # 提取音频片段
        cmd = [
            "ffmpeg", "-i", audio_file,
            "-ss", str(segment['start']),
            "-t", str(segment['end'] - segment['start']),
            "-c", "copy", segment_file,
            "-y"
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️  片段 {i+1} 提取失败，跳过")
            continue
        
        # 使用Whisper转录
        transcribe_start = time.time()
        result = whisper_model.transcribe(segment_file, verbose=False)
        transcribe_time = time.time() - transcribe_start
        total_transcribe_time += transcribe_time
        
        # 保存结果
        transcription_results.append({
            'segment_id': i,
            'start': segment['start'],
            'end': segment['end'],
            'speaker': segment['speaker'],
            'text': result['text'].strip(),
            'transcribe_time': transcribe_time
        })
        
        print(f"     转录完成: {result['text'].strip()}")
        
        # 清理临时文件
        if os.path.exists(segment_file):
            os.remove(segment_file)
    
    # 4. 生成最终结果
    print("4. 生成最终结果...")
    final_result = {
        'audio_file': audio_file,
        'total_speakers': 2,  # 模拟2个说话人
        'total_segments': len(segments),
        'whisper_model': 'small',
        'diarization_method': 'time-based-simulation',
        'processing_times': {
            'whisper_load': whisper_load_time,
            'diarization': diarization_time,
            'total_transcription': total_transcribe_time
        },
        'transcriptions': transcription_results
    }
    
    return final_result

def save_results(result, output_file):
    """保存结果到文件"""
    print(f"\n=== 保存结果到: {output_file} ===")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== Whisper + 说话人分离演示结果 ===\n\n")
        
        f.write(f"音频文件: {result['audio_file']}\n")
        f.write(f"说话人数量: {result['total_speakers']}\n")
        f.write(f"语音片段数: {result['total_segments']}\n")
        f.write(f"Whisper模型: {result['whisper_model']}\n")
        f.write(f"分离方法: {result['diarization_method']}\n\n")
        
        f.write("处理时间:\n")
        for key, value in result['processing_times'].items():
            f.write(f"  {key}: {value:.2f}秒\n")
        f.write("\n")
        
        f.write("转录结果:\n")
        f.write("=" * 50 + "\n")
        
        for trans in result['transcriptions']:
            f.write(f"[{trans['start']:.1f}s - {trans['end']:.1f}s] {trans['speaker']}: {trans['text']}\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write("JSON格式结果:\n")
        f.write(json.dumps(result, ensure_ascii=False, indent=2))

def main():
    """主函数"""
    print("=== Whisper + 说话人分离演示 ===")
    
    # 音频文件
    audio_file = "ba84462e-fdee-42fe-9439-86808b3d3212.wav"
    
    if not os.path.exists(audio_file):
        print(f"\n❌ 音频文件不存在: {audio_file}")
        return
    
    # 运行Whisper + 说话人分离
    try:
        result = run_whisper_with_diarization(audio_file)
        
        # 保存结果
        output_file = "whisper_diarization_demo_result.txt"
        save_results(result, output_file)
        
        print(f"\n✅ 处理完成！结果已保存到: {output_file}")
        
        # 显示简要结果
        print("\n=== 简要结果预览 ===")
        for trans in result['transcriptions'][:8]:  # 显示前8个片段
            print(f"[{trans['start']:.1f}s - {trans['end']:.1f}s] {trans['speaker']}: {trans['text']}")
        
        if len(result['transcriptions']) > 8:
            print(f"... 还有 {len(result['transcriptions']) - 8} 个片段")
        
    except Exception as e:
        print(f"\n❌ 处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 