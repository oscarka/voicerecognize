#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper + Pyannote Web界面
提供模型选择和实时进度显示
"""
import os
import time
import json
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import whisper
from pyannote.audio import Pipeline
import threading
import queue

app = Flask(__name__)

# 全局变量存储任务状态
task_status = {
    'running': False,
    'progress': 0,
    'current_step': '',
    'result': None,
    'error': None
}

# 任务队列
task_queue = queue.Queue()

def process_audio_task(audio_file, model_name, min_duration=2.0):
    """处理音频任务"""
    global task_status
    
    try:
        task_status['running'] = True
        task_status['progress'] = 0
        task_status['current_step'] = '初始化...'
        task_status['error'] = None
        
        # 1. 加载Whisper模型
        task_status['current_step'] = f'加载Whisper模型 ({model_name})...'
        task_status['progress'] = 10
        start_time = time.time()
        whisper_model = whisper.load_model(model_name)
        whisper_load_time = time.time() - start_time
        
        # 2. 初始化Pyannote Pipeline
        task_status['current_step'] = '初始化Pyannote Pipeline...'
        task_status['progress'] = 20
        start_time = time.time()
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=os.getenv("HF_TOKEN")
        )
        pyannote_load_time = time.time() - start_time
        
        # 3. 执行说话人分离
        task_status['current_step'] = '执行说话人分离...'
        task_status['progress'] = 30
        start_time = time.time()
        diarization = pipeline(audio_file)
        diarization_time = time.time() - start_time
        
        # 4. 分析说话人分离结果
        task_status['current_step'] = '分析说话人分离结果...'
        task_status['progress'] = 40
        speakers = set()
        segments = []
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            if turn.end - turn.start >= min_duration:
                speakers.add(speaker)
                segments.append({
                    'start': turn.start,
                    'end': turn.end,
                    'speaker': speaker
                })
        
        # 5. 对每个片段进行转录
        task_status['current_step'] = '转录语音片段...'
        transcription_results = []
        total_transcribe_time = 0
        
        for i, segment in enumerate(segments):
            progress = 40 + (i / len(segments)) * 50
            task_status['progress'] = int(progress)
            task_status['current_step'] = f'转录片段 {i+1}/{len(segments)}...'
            
            # 提取音频片段
            segment_file = f"temp_segment_{i}.wav"
            cmd = [
                "ffmpeg", "-i", audio_file,
                "-ss", str(segment['start']),
                "-t", str(segment['end'] - segment['start']),
                "-c", "copy", segment_file,
                "-y"
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                continue
            
            # 使用Whisper转录
            transcribe_start = time.time()
            result = whisper_model.transcribe(
                segment_file, 
                verbose=False,
                language="zh",
                task="transcribe",
                fp16=False
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
            
            # 清理临时文件
            if os.path.exists(segment_file):
                os.remove(segment_file)
        
        # 6. 生成最终结果
        task_status['current_step'] = '生成最终结果...'
        task_status['progress'] = 95
        
        final_result = {
            'audio_file': audio_file,
            'total_speakers': len(speakers),
            'total_segments': len(segments),
            'whisper_model': model_name,
            'pyannote_model': 'pyannote/speaker-diarization-3.1',
            'optimizations': {
                'min_segment_duration': min_duration,
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
        
        task_status['result'] = final_result
        task_status['progress'] = 100
        task_status['current_step'] = '完成！'
        
    except Exception as e:
        task_status['error'] = str(e)
        task_status['current_step'] = f'错误: {str(e)}'
    finally:
        task_status['running'] = False

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_audio():
    """处理音频API"""
    global task_status
    
    if task_status['running']:
        return jsonify({'error': '任务正在运行中'})
    
    data = request.get_json()
    model_name = data.get('model', 'base')
    min_duration = data.get('min_duration', 2.0)
    
    # 检查音频文件
    audio_file = "short_test_audio.wav"
    if not os.path.exists(audio_file):
        return jsonify({'error': '音频文件不存在'})
    
    # 检查HF_TOKEN
    if not os.getenv("HF_TOKEN"):
        return jsonify({'error': '请设置HF_TOKEN环境变量'})
    
    # 启动后台任务
    thread = threading.Thread(
        target=process_audio_task,
        args=(audio_file, model_name, min_duration)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': '任务已启动'})

@app.route('/api/status')
def get_status():
    """获取任务状态"""
    return jsonify(task_status)

@app.route('/api/result')
def get_result():
    """获取结果"""
    if task_status['result']:
        return jsonify(task_status['result'])
    return jsonify({'error': '没有可用的结果'})

@app.route('/api/audio_info')
def get_audio_info():
    """获取音频文件信息"""
    audio_file = "short_test_audio.wav"
    if os.path.exists(audio_file):
        # 获取文件大小
        size = os.path.getsize(audio_file)
        # 获取音频时长（简单估算）
        duration = size / (8000 * 2 * 2)  # 8kHz, 16bit, stereo
        return jsonify({
            'exists': True,
            'size': size,
            'duration': duration
        })
    return jsonify({'exists': False})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 