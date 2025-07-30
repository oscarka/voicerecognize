#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper + Pyannote 真实运行脚本
实现说话人分离 + 语音转录的完整流程
"""
import os
import sys
import time
import json
import subprocess
from pathlib import Path
import whisper
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook

def check_dependencies():
    """检查依赖"""
    print("=== 检查依赖 ===")
    
    # 检查Whisper
    try:
        import whisper
        print("✅ Whisper 已安装")
    except ImportError:
        print("❌ Whisper 未安装")
        return False
    
    # 检查Pyannote
    try:
        from pyannote.audio import Pipeline
        print("✅ Pyannote 已安装")
    except ImportError:
        print("❌ Pyannote 未安装")
        return False
    
    # 检查HF_TOKEN
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token or hf_token == "hf_xxx":
        print("❌ 请设置有效的HF_TOKEN环境变量")
        print("   获取地址: https://huggingface.co/settings/tokens")
        return False
    else:
        print("✅ HF_TOKEN 已设置")
    
    return True

def run_whisper_pyannote(audio_file):
    """运行Whisper + Pyannote组合"""
    print(f"\n=== 开始处理音频: {audio_file} ===")
    
    # 1. 初始化Whisper模型
    print("1. 加载Whisper模型...")
    start_time = time.time()
    whisper_model = whisper.load_model("small")
    whisper_load_time = time.time() - start_time
    print(f"   Whisper模型加载完成，耗时: {whisper_load_time:.2f}秒")
    
    # 2. 初始化Pyannote Pipeline
    print("2. 初始化Pyannote Pipeline...")
    start_time = time.time()
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=os.getenv("HF_TOKEN")
    )
    pyannote_load_time = time.time() - start_time
    print(f"   Pyannote Pipeline加载完成，耗时: {pyannote_load_time:.2f}秒")
    
    # 3. 执行说话人分离
    print("3. 执行说话人分离...")
    start_time = time.time()
    diarization = pipeline(audio_file)
    diarization_time = time.time() - start_time
    print(f"   说话人分离完成，耗时: {diarization_time:.2f}秒")
    
    # 4. 分析说话人分离结果
    print("4. 分析说话人分离结果...")
    speakers = set()
    segments = []
    
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.add(speaker)
        segments.append({
            'start': turn.start,
            'end': turn.end,
            'speaker': speaker
        })
    
    print(f"   检测到 {len(speakers)} 个说话人: {list(speakers)}")
    print(f"   总共 {len(segments)} 个语音片段")
    
    # 5. 对每个片段进行转录
    print("5. 对每个片段进行转录...")
    transcription_results = []
    total_transcribe_time = 0
    
    for i, segment in enumerate(segments):
        print(f"   处理片段 {i+1}/{len(segments)}: {segment['start']:.1f}s - {segment['end']:.1f}s ({segment['speaker']})")
        
        # 使用ffmpeg提取音频片段
        segment_file = f"temp_segment_{i}.wav"
        start_time_segment = time.time()
        
        # 提取音频片段
        cmd = [
            "ffmpeg", "-i", audio_file,
            "-ss", str(segment['start']),
            "-t", str(segment['end'] - segment['start']),
            "-c", "copy", segment_file,
            "-y"  # 覆盖输出文件
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
    
    # 6. 生成最终结果
    print("6. 生成最终结果...")
    final_result = {
        'audio_file': audio_file,
        'total_speakers': len(speakers),
        'total_segments': len(segments),
        'whisper_model': 'small',
        'pyannote_model': 'pyannote/speaker-diarization-3.1',
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
        f.write("=== Whisper + Pyannote 完整转录结果 ===\n\n")
        
        f.write(f"音频文件: {result['audio_file']}\n")
        f.write(f"说话人数量: {result['total_speakers']}\n")
        f.write(f"语音片段数: {result['total_segments']}\n")
        f.write(f"Whisper模型: {result['whisper_model']}\n")
        f.write(f"Pyannote模型: {result['pyannote_model']}\n\n")
        
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
    print("=== Whisper + Pyannote 真实运行测试 ===")
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先解决上述问题")
        return
    
    # 音频文件
    audio_file = "ba84462e-fdee-42fe-9439-86808b3d3212.wav"
    
    if not os.path.exists(audio_file):
        print(f"\n❌ 音频文件不存在: {audio_file}")
        return
    
    # 运行Whisper + Pyannote
    try:
        result = run_whisper_pyannote(audio_file)
        
        # 保存结果
        output_file = "whisper_pyannote_real_result.txt"
        save_results(result, output_file)
        
        print(f"\n✅ 处理完成！结果已保存到: {output_file}")
        
        # 显示简要结果
        print("\n=== 简要结果预览 ===")
        for trans in result['transcriptions'][:5]:  # 只显示前5个片段
            print(f"[{trans['start']:.1f}s - {trans['end']:.1f}s] {trans['speaker']}: {trans['text']}")
        
        if len(result['transcriptions']) > 5:
            print(f"... 还有 {len(result['transcriptions']) - 5} 个片段")
        
    except Exception as e:
        print(f"\n❌ 处理过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 