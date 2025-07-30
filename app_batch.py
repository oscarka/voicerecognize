#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper + Pyannote 批量处理Web界面
支持多文件处理和断点续传
"""
import os
import time
import json
import subprocess
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import whisper
from pyannote.audio import Pipeline
import threading
import queue
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
TEMP_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'aac'}

# 创建必要的文件夹
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, TEMP_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# 全局变量存储任务状态
batch_status = {
    'running': False,
    'total_files': 0,
    'processed_files': 0,
    'current_file': '',
    'current_progress': 0,
    'current_step': '',
    'results': [],
    'error': None,
    'resume_data': {}
}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_single_file(audio_file, model_name, min_duration=2.0):
    """处理单个音频文件"""
    try:
        # 1. 加载Whisper模型
        whisper_model = whisper.load_model(model_name)
        
        # 2. 初始化Pyannote Pipeline
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=os.getenv("HF_TOKEN")
        )
        
        # 3. 执行说话人分离
        diarization = pipeline(audio_file)
        
        # 4. 分析说话人分离结果
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
        transcription_results = []
        
        for i, segment in enumerate(segments):
            # 提取音频片段
            segment_file = os.path.join(TEMP_FOLDER, f"temp_segment_{i}.wav")
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
            result = whisper_model.transcribe(
                segment_file, 
                verbose=False,
                language="zh",
                task="transcribe",
                fp16=False
            )
            
            # 保存结果
            transcription_results.append({
                'segment_id': i,
                'start': segment['start'],
                'end': segment['end'],
                'speaker': segment['speaker'],
                'text': result['text'].strip(),
                'language': result.get('language', 'zh')
            })
            
            # 清理临时文件
            if os.path.exists(segment_file):
                os.remove(segment_file)
        
        return {
            'file_name': os.path.basename(audio_file),
            'total_speakers': len(speakers),
            'total_segments': len(segments),
            'whisper_model': model_name,
            'transcriptions': transcription_results,
            'status': 'completed'
        }
        
    except Exception as e:
        return {
            'file_name': os.path.basename(audio_file),
            'error': str(e),
            'status': 'failed'
        }

def process_batch_files(file_list, model_name, min_duration=2.0):
    """批量处理文件"""
    global batch_status
    
    try:
        batch_status['running'] = True
        batch_status['total_files'] = len(file_list)
        batch_status['processed_files'] = 0
        batch_status['results'] = []
        batch_status['error'] = None
        
        # 检查是否有断点续传数据
        resume_file = os.path.join(TEMP_FOLDER, 'resume_data.json')
        if os.path.exists(resume_file):
            with open(resume_file, 'r', encoding='utf-8') as f:
                resume_data = json.load(f)
                if resume_data.get('model_name') == model_name:
                    batch_status['processed_files'] = resume_data.get('processed_files', 0)
                    batch_status['results'] = resume_data.get('results', [])
                    # 跳过已处理的文件
                    file_list = file_list[resume_data.get('processed_files', 0):]
        
        for i, file_path in enumerate(file_list):
            if not batch_status['running']:
                break
                
            batch_status['current_file'] = os.path.basename(file_path)
            batch_status['current_progress'] = 0
            batch_status['current_step'] = f'处理文件 {i+1}/{len(file_list)}: {batch_status["current_file"]}'
            
            # 处理文件
            result = process_single_file(file_path, model_name, min_duration)
            batch_status['results'].append(result)
            batch_status['processed_files'] += 1
            
            # 保存断点续传数据
            resume_data = {
                'model_name': model_name,
                'processed_files': batch_status['processed_files'],
                'results': batch_status['results']
            }
            with open(resume_file, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, ensure_ascii=False, indent=2)
            
            # 移动已处理的文件
            processed_path = os.path.join(PROCESSED_FOLDER, os.path.basename(file_path))
            shutil.move(file_path, processed_path)
            
            time.sleep(0.1)  # 避免界面卡死
        
        # 清理断点续传文件
        if os.path.exists(resume_file):
            os.remove(resume_file)
            
        batch_status['current_step'] = '批量处理完成！'
        
    except Exception as e:
        batch_status['error'] = str(e)
        batch_status['current_step'] = f'错误: {str(e)}'
    finally:
        batch_status['running'] = False

@app.route('/')
def index():
    """主页"""
    return render_template('batch_index.html')

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """上传文件API"""
    if 'files' not in request.files:
        return jsonify({'error': '没有选择文件'})
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_files.append(filepath)
    
    return jsonify({
        'message': f'成功上传 {len(uploaded_files)} 个文件',
        'files': uploaded_files
    })

@app.route('/api/files')
def get_files():
    """获取文件列表"""
    upload_files = []
    processed_files = []
    
    # 获取待处理文件
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                upload_files.append({
                    'name': filename,
                    'path': filepath,
                    'size': size
                })
    
    # 获取已处理文件
    for filename in os.listdir(PROCESSED_FOLDER):
        if allowed_file(filename):
            filepath = os.path.join(PROCESSED_FOLDER, filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                processed_files.append({
                    'name': filename,
                    'path': filepath,
                    'size': size
                })
    
    return jsonify({
        'upload_files': upload_files,
        'processed_files': processed_files
    })

@app.route('/api/process_batch', methods=['POST'])
def process_batch():
    """批量处理API"""
    global batch_status
    
    if batch_status['running']:
        return jsonify({'error': '任务正在运行中'})
    
    data = request.get_json()
    file_paths = data.get('files', [])
    model_name = data.get('model', 'base')
    min_duration = data.get('min_duration', 2.0)
    
    if not file_paths:
        return jsonify({'error': '没有选择文件'})
    
    # 检查HF_TOKEN
    if not os.getenv("HF_TOKEN"):
        return jsonify({'error': '请设置HF_TOKEN环境变量'})
    
    # 启动后台任务
    thread = threading.Thread(
        target=process_batch_files,
        args=(file_paths, model_name, min_duration)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': '批量处理任务已启动'})

@app.route('/api/batch_status')
def get_batch_status():
    """获取批量处理状态"""
    return jsonify(batch_status)

@app.route('/api/stop_batch')
def stop_batch():
    """停止批量处理"""
    global batch_status
    batch_status['running'] = False
    return jsonify({'message': '已停止批量处理'})

@app.route('/api/resume_batch')
def resume_batch():
    """恢复批量处理"""
    resume_file = os.path.join(TEMP_FOLDER, 'resume_data.json')
    if os.path.exists(resume_file):
        with open(resume_file, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        return jsonify(resume_data)
    return jsonify({'error': '没有可恢复的数据'})

@app.route('/api/clear_processed')
def clear_processed():
    """清空已处理文件"""
    try:
        for filename in os.listdir(PROCESSED_FOLDER):
            filepath = os.path.join(PROCESSED_FOLDER, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        return jsonify({'message': '已清空已处理文件'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/download_result')
def download_result():
    """下载处理结果"""
    if not batch_status['results']:
        return jsonify({'error': '没有可下载的结果'})
    
    result_file = os.path.join(TEMP_FOLDER, 'batch_results.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(batch_status['results'], f, ensure_ascii=False, indent=2)
    
    return send_file(result_file, as_attachment=True, download_name='batch_results.json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 