#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper + Pyannote 优化版本
提高速度和质量
"""
import os
import sys
import time
import json
import subprocess
from pathlib import Path
import whisper
from pyannote.audio import Pipeline

def run_optimized_test(audio_file):
    """运行优化版本的测试"""
    print(f"\n=== Whisper + Pyannote 优化测试 ===")
    print(f"处理音频: {audio_file}")
    
    # 1. 加载Whisper模型 (使用base模型，更快)
    print("\n1. 加载Whisper模型...")
    start_time = time.time()
    whisper_model = whisper.load_model("base")  # 改用base模型，更快
    whisper_load_time = time.time() - start_time
    print(f"   Whisper模型加载完成，耗时: {whisper_load_time:.2f}秒")
    
    # 2. 初始化Pyannote Pipeline
    print("\n2. 初始化Pyannote Pipeline...")
    start_time = time.time()
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=os.getenv("HF_TOKEN")
    )
    pyannote_load_time = time.time() - start_time
    print(f"   Pyannote Pipeline加载完成，耗时: {pyannote_load_time:.2f}秒")
    
    # 3. 执行说话人分离
    print("\n3. 执行说话人分离...")
    start_time = time.time()
    diarization = pipeline(audio_file)
    diarization_time = time.time() - start_time
    print(f"   说话人分离完成，耗时: {diarization_time:.2f}秒")
    
    # 4. 分析说话人分离结果
    print("\n4. 分析说话人分离结果...")
    speakers = set()
    segments = []
    
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        # 过滤掉太短的片段（<2秒）
        if turn.end - turn.start >= 2.0:
            speakers.add(speaker)
            segments.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker
            })
    
    print(f"   检测到 {len(speakers)} 个说话人: {list(speakers)}")
    print(f"   总共 {len(segments)} 个有效语音片段（过滤短片段）")
    
    # 5. 对每个片段进行转录（优化版本）
    print("\n5. 对每个片段进行转录...")
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
        
        # 使用Whisper转录（优化参数）
        transcribe_start = time.time()
        result = whisper_model.transcribe(
            segment_file, 
            verbose=False,
            language="zh",  # 强制指定中文
            task="transcribe",  # 明确指定任务
            fp16=False  # 禁用FP16，避免警告
        )
        transcribe_time = time.time() - transcribe_start
        total_transcribe_time += transcribe_time
        
        # 保存结果
        transcription_results.append({
            'segment_id': i,
            'start': segment['start'],
            'end': segment['end'],
            'speaker': segment['speaker'],
            'text': result['text'].strip(),
            'language': result.get('language', 'zh'),
            'transcribe_time': transcribe_time
        })
        
        print(f"     转录完成: {result['text'].strip()}")
        
        # 清理临时文件
        if os.path.exists(segment_file):
            os.remove(segment_file)
    
    # 6. 生成最终结果
    print("\n6. 生成最终结果...")
    final_result = {
        'audio_file': audio_file,
        'total_speakers': len(speakers),
        'total_segments': len(segments),
        'whisper_model': 'base',  # 使用base模型
        'pyannote_model': 'pyannote/speaker-diarization-3.1',
        'optimizations': {
            'min_segment_duration': 2.0,
            'forced_language': 'zh',
            'fp16_disabled': True
        },
        'processing_times': {
            'whisper_load': whisper_load_time,
            'pyannote_load': pyannote_load_time,
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
        f.write("=== Whisper + Pyannote 优化测试结果 ===\n\n")
        
        f.write(f"音频文件: {result['audio_file']}\n")
        f.write(f"说话人数量: {result['total_speakers']}\n")
        f.write(f"语音片段数: {result['total_segments']}\n")
        f.write(f"Whisper模型: {result['whisper_model']}\n")
        f.write(f"Pyannote模型: {result['pyannote_model']}\n\n")
        
        f.write("优化设置:\n")
        for key, value in result['optimizations'].items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")
        
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
    print("=== Whisper + Pyannote 优化测试 ===")
    
    # 检查HF_TOKEN
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token or hf_token == "hf_xxx":
        print("❌ 请设置有效的HF_TOKEN环境变量")
        print("   获取地址: https://huggingface.co/settings/tokens")
        return
    
    # 音频文件
    audio_file = "short_test_audio.wav"
    
    if not os.path.exists(audio_file):
        print(f"\n❌ 音频文件不存在: {audio_file}")
        print("请先运行 whisper_pyannote_quick_test.py 创建短音频文件")
        return
    
    # 运行优化测试
    try:
        result = run_optimized_test(audio_file)
        
        # 保存结果
        output_file = "whisper_pyannote_optimized_result.txt"
        save_results(result, output_file)
        
        print(f"\n✅ 优化测试完成！结果已保存到: {output_file}")
        
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