#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VoiceRecognize 完全独立版应用（使用Conda）
自动创建conda环境、安装依赖、下载模型、启动Web服务
"""

import os
import sys
import subprocess
import importlib
import webbrowser
import time
import socket
import json
import threading
from pathlib import Path

def check_conda():
    """检查conda是否可用"""
    try:
        result = subprocess.run(['conda', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ 找到Conda: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到Conda，请先安装Miniconda")
        print("下载地址: https://docs.conda.io/en/latest/miniconda.html")
        return False

def create_conda_environment():
    """创建conda环境"""
    env_name = "voicerecognize_standalone"
    
    print(f"🔍 检查conda环境: {env_name}")
    
    # 检查环境是否存在
    try:
        result = subprocess.run(['conda', 'env', 'list'], 
                              capture_output=True, text=True, check=True)
        if env_name in result.stdout:
            print(f"✅ 找到现有环境: {env_name}")
            return env_name
    except subprocess.CalledProcessError:
        pass
    
    print(f"📦 创建新的conda环境: {env_name}")
    try:
        subprocess.run([
            'conda', 'create', '-n', env_name, 'python=3.11', '-y'
        ], check=True)
        print(f"✅ 环境创建成功: {env_name}")
        return env_name
    except subprocess.CalledProcessError as e:
        print(f"❌ 环境创建失败: {e}")
        return None

def install_dependencies(env_name):
    """在conda环境中安装依赖"""
    print(f"📦 在环境 {env_name} 中安装依赖...")
    
    # 首先安装兼容的NumPy版本
    try:
        print("安装兼容的NumPy版本...")
        subprocess.run([
            'conda', 'run', '-n', env_name, 'python', '-m', 'pip', 'install',
            'numpy<2.0'
        ], check=True)
        print("✅ NumPy安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ NumPy安装失败: {e}")
        return False
    
    # 安装基础依赖
    try:
        print("安装基础依赖...")
        subprocess.run([
            'conda', 'run', '-n', env_name, 'python', '-m', 'pip', 'install',
            'flask', 'requests', 'tqdm', 'psutil', 'soundfile'
        ], check=True)
        print("✅ 基础依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 基础依赖安装失败: {e}")
        return False
    
    # 安装PyTorch
    try:
        print("安装PyTorch...")
        subprocess.run([
            'conda', 'run', '-n', env_name, 'python', '-m', 'pip', 'install',
            'torch', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cpu'
        ], check=True)
        print("✅ PyTorch安装完成")
    except subprocess.CalledProcessError:
        try:
            print("尝试备用PyTorch安装方式...")
            subprocess.run([
                'conda', 'run', '-n', env_name, 'python', '-m', 'pip', 'install',
                'torch', 'torchaudio'
            ], check=True)
            print("✅ PyTorch安装完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ PyTorch安装失败: {e}")
            return False
    
    # 安装Whisper
    try:
        print("安装Whisper...")
        subprocess.run([
            'conda', 'run', '-n', env_name, 'python', '-m', 'pip', 'install',
            'openai-whisper'
        ], check=True)
        print("✅ Whisper安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ Whisper安装失败: {e}")
        return False
    
    # 安装FFmpeg
    try:
        print("安装FFmpeg...")
        subprocess.run([
            'conda', 'install', '-n', env_name, '-c', 'conda-forge', 'ffmpeg', '-y'
        ], check=True)
        print("✅ FFmpeg安装完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg安装失败: {e}")
        return False
    
    return True

def check_dependencies(env_name):
    """检查依赖是否正确安装"""
    print(f"🔍 检查环境 {env_name} 中的依赖...")
    
    test_script = """
import sys
import importlib

deps = ['flask', 'torch', 'whisper', 'numpy', 'soundfile', 'psutil']
missing = []

for dep in deps:
    try:
        importlib.import_module(dep)
        print(f"✅ {dep}")
    except ImportError:
        print(f"❌ {dep}")
        missing.append(dep)

if missing:
    print(f"缺少依赖: {missing}")
    sys.exit(1)
else:
    print("✅ 所有依赖已正确安装")
"""
    
    try:
        result = subprocess.run([
            'conda', 'run', '-n', env_name, 'python', '-c', test_script
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖检查失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def download_models(env_name):
    """下载必要的模型"""
    print(f"\n📥 在环境 {env_name} 中检查模型文件...")
    
    download_script = """
import whisper
import os
import sys

print("正在检查Whisper模型...")
try:
    # 确保使用兼容的NumPy版本
    import numpy as np
    print(f"NumPy版本: {np.__version__}")
    
    model = whisper.load_model('base')
    print("✅ Whisper模型已就绪")
except Exception as e:
    print(f"📥 正在下载Whisper模型...")
    try:
        model = whisper.load_model('base')
        print("✅ Whisper模型下载完成")
    except Exception as e2:
        print(f"❌ 模型下载失败: {e2}")
        sys.exit(1)
"""
    
    try:
        result = subprocess.run([
            'conda', 'run', '-n', env_name, 'python', '-c', download_script
        ], capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 模型下载失败: {e}")
        print(f"错误输出: {e.stderr}")
        
        # 尝试修复NumPy版本问题
        print("🔄 尝试修复NumPy版本问题...")
        try:
            subprocess.run([
                'conda', 'run', '-n', env_name, 'python', '-m', 'pip', 'install',
                '--force-reinstall', 'numpy<2.0'
            ], check=True)
            print("✅ NumPy版本已修复，重新尝试下载模型...")
            
            # 重新尝试下载
            result = subprocess.run([
                'conda', 'run', '-n', env_name, 'python', '-c', download_script
            ], capture_output=True, text=True, check=True)
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ 修复失败: {e2}")
        return False

def find_free_port(start_port=5002):
    """查找可用端口"""
    port = start_port
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            port += 1
    return None

def start_web_app(env_name, port):
    """启动Web应用"""
    print(f"\n🚀 在环境 {env_name} 中启动Web应用...")
    print(f"🌐 应用地址: http://localhost:{port}")
    
    # 创建简化的Web应用脚本
    web_app_script = '''
import os
import sys
import json
import time
import threading
from flask import Flask, render_template, request, jsonify, send_file
import whisper
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
    'error': None
}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_single_file(audio_file, model_name='base'):
    """处理单个音频文件"""
    try:
        # 加载Whisper模型
        whisper_model = whisper.load_model(model_name)
        
        # 使用Whisper转录
        result = whisper_model.transcribe(
            audio_file,
            language="zh",
            task="transcribe"
        )
        
        # 格式化输出，模拟说话人识别
        segments = result.get('segments', [])
        formatted_segments = []
        
        for i, segment in enumerate(segments):
            # 简单的说话人分配（实际项目中可以用pyannote.audio）
            speaker = f"说话人{i % 2 + 1}"  # 交替分配说话人
            formatted_segments.append({
                'speaker': speaker,
                'start': segment.get('start', 0),
                'end': segment.get('end', 0),
                'text': segment.get('text', '').strip()
            })
        
        return {
            'file': audio_file,
            'file_name': os.path.basename(audio_file),
            'status': 'completed',
            'text': result['text'].strip(),
            'language': result.get('language', 'zh'),
            'total_speakers': len(set(seg['speaker'] for seg in formatted_segments)),
            'total_segments': len(formatted_segments),
            'transcriptions': formatted_segments
        }
        
    except Exception as e:
        return {
            'file': audio_file,
            'file_name': os.path.basename(audio_file),
            'status': 'failed',
            'error': str(e)
        }

def process_batch_files(file_list, model_name='base'):
    """批量处理文件"""
    global batch_status
    
    batch_status['running'] = True
    batch_status['total_files'] = len(file_list)
    batch_status['processed_files'] = 0
    batch_status['results'] = []
    batch_status['error'] = None
    
    try:
        for i, file_path in enumerate(file_list):
            if not batch_status['running']:
                break
                
            batch_status['current_file'] = os.path.basename(file_path)
            batch_status['current_progress'] = (i / len(file_list)) * 100
            batch_status['current_step'] = f'处理文件 {i+1}/{len(file_list)} - 使用模型: {model_name}'
            
            print(f"处理文件: {file_path} (模型: {model_name})")
            result = process_single_file(file_path, model_name)
            batch_status['results'].append(result)
            batch_status['processed_files'] += 1
            
        batch_status['current_step'] = '处理完成'
        batch_status['current_progress'] = 100
        
    except Exception as e:
        batch_status['error'] = str(e)
        print(f"批量处理错误: {e}")
    
    finally:
        batch_status['running'] = False

@app.route('/')
def index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VoiceRecognize 语音识别</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }

            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }

            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }

            .content {
                padding: 40px;
            }

            .section {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
            }

            .section h2 {
                margin-bottom: 20px;
                color: #333;
                font-size: 1.5em;
            }

            .upload-area {
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                background: #f0f4ff;
                transition: all 0.3s;
                cursor: pointer;
            }

            .upload-area:hover {
                border-color: #764ba2;
                background: #e8f0ff;
            }

            .upload-area.dragover {
                border-color: #764ba2;
                background: #e8f0ff;
                transform: scale(1.02);
            }

            .upload-icon {
                font-size: 3em;
                color: #667eea;
                margin-bottom: 20px;
            }

            .file-input {
                display: none;
            }

            .file-list {
                margin-top: 20px;
            }

            .file-item {
                background: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }

            .file-info {
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .file-icon {
                font-size: 1.5em;
                color: #667eea;
            }

            .file-details h4 {
                margin-bottom: 5px;
                color: #333;
            }

            .file-details p {
                color: #666;
                font-size: 0.9em;
            }

            .file-actions {
                display: flex;
                gap: 10px;
            }

            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
            }

            .btn:hover {
                transform: translateY(-2px);
            }

            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }

            .btn-danger {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            }

            .btn-success {
                background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
            }

            .form-group {
                margin-bottom: 20px;
            }

            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
            }

            .form-group select, .form-group input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }

            .form-group select:focus, .form-group input:focus {
                outline: none;
                border-color: #667eea;
            }

            .progress-section {
                display: none;
            }

            .progress-bar {
                width: 100%;
                height: 20px;
                background: #e1e5e9;
                border-radius: 10px;
                overflow: hidden;
                margin-bottom: 15px;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                width: 0%;
                transition: width 0.3s ease;
            }

            .progress-text {
                text-align: center;
                font-weight: 600;
                color: #333;
            }

            .batch-stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }

            .stat-card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }

            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }

            .stat-label {
                color: #666;
                margin-top: 5px;
            }

            .result-section {
                display: none;
            }

            .result-item {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }

            .result-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid #e1e5e9;
            }

            .result-title {
                font-weight: 600;
                color: #333;
            }

            .result-status {
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 600;
            }

            .status-completed {
                background: #d4edda;
                color: #155724;
            }

            .status-failed {
                background: #f8d7da;
                color: #721c24;
            }

            .transcription-preview {
                max-height: 200px;
                overflow-y: auto;
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }

            .transcription-item {
                margin-bottom: 10px;
                padding: 10px;
                background: white;
                border-radius: 5px;
            }

            .speaker {
                background: #667eea;
                color: white;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: 600;
                margin-right: 10px;
            }

            .error-message {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #c33;
            }

            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎤 VoiceRecognize 语音识别</h1>
                <p>支持批量上传音频文件进行语音识别</p>
            </div>

            <div class="content">
                <!-- 文件上传区域 -->
                <div class="section">
                    <h2>📤 文件上传</h2>
                    <div class="upload-area" id="uploadArea">
                        <div class="upload-icon">📁</div>
                        <h3>拖拽文件到此处或点击选择</h3>
                        <p>支持 WAV, MP3, M4A, FLAC, AAC 格式</p>
                        <input type="file" id="fileInput" class="file-input" multiple accept=".wav,.mp3,.m4a,.flac,.aac">
                    </div>
                    <div class="file-list" id="fileList"></div>
                </div>

                <!-- 处理设置 -->
                <div class="section">
                    <h2>⚙️ 处理设置</h2>
                    <div class="form-group">
                        <label for="modelSelect">Whisper模型:</label>
                        <select id="modelSelect">
                            <option value="tiny">Tiny (最快, 39M)</option>
                            <option value="base" selected>Base (平衡, 74M)</option>
                            <option value="small">Small (推荐, 244M)</option>
                            <option value="medium">Medium (高质量, 769M)</option>
                            <option value="large">Large (最高质量, 1550M)</option>
                        </select>
                    </div>
                    <div style="display: flex; gap: 15px;">
                        <button class="btn" id="startBtn" onclick="startBatchProcessing()">
                            🚀 开始批量处理
                        </button>
                        <button class="btn btn-danger" id="stopBtn" onclick="stopBatchProcessing()" style="display: none;">
                            ⏹️ 停止处理
                        </button>
                    </div>
                </div>

                <!-- 进度显示 -->
                <div class="progress-section" id="progressSection">
                    <h2>📊 处理进度</h2>
                    <div class="batch-stats" id="batchStats"></div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <div class="progress-text" id="progressText">准备中...</div>
                </div>

                <!-- 结果显示 -->
                <div class="result-section" id="resultSection">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2>📝 处理结果</h2>
                        <button class="btn" onclick="downloadResults()">📥 下载结果</button>
                    </div>
                    <div id="resultsList"></div>
                </div>

                <!-- 错误信息 -->
                <div class="error-message" id="errorMessage" style="display: none;"></div>
            </div>
        </div>

        <script>
            let uploadedFiles = [];
            let statusInterval;

            // 页面加载时获取文件列表
            window.onload = function() {
                loadFileList();
            };

            // 文件上传处理
            document.getElementById('uploadArea').addEventListener('click', () => {
                document.getElementById('fileInput').click();
            });

            document.getElementById('uploadArea').addEventListener('dragover', (e) => {
                e.preventDefault();
                document.getElementById('uploadArea').classList.add('dragover');
            });

            document.getElementById('uploadArea').addEventListener('dragleave', () => {
                document.getElementById('uploadArea').classList.remove('dragover');
            });

            document.getElementById('uploadArea').addEventListener('drop', (e) => {
                e.preventDefault();
                document.getElementById('uploadArea').classList.remove('dragover');
                const files = e.dataTransfer.files;
                handleFileUpload(files);
            });

            document.getElementById('fileInput').addEventListener('change', (e) => {
                handleFileUpload(e.target.files);
            });

            function handleFileUpload(files) {
                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }
                
                fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showError(data.error);
                    } else {
                        showMessage(data.message);
                        loadFileList();
                    }
                })
                .catch(error => {
                    showError('上传失败: ' + error.message);
                });
            }

            function loadFileList() {
                fetch('/api/files')
                .then(response => response.json())
                .then(data => {
                    uploadedFiles = data.upload_files;
                    displayFileList();
                })
                .catch(error => {
                    console.error('加载文件列表失败:', error);
                });
            }

            function displayFileList() {
                const fileList = document.getElementById('fileList');
                fileList.innerHTML = '';
                
                uploadedFiles.forEach(file => {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    fileItem.innerHTML = `
                        <div class="file-info">
                            <div class="file-icon">🎵</div>
                            <div class="file-details">
                                <h4>${file.name}</h4>
                                <p>${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                        </div>
                        <div class="file-actions">
                            <button class="btn btn-danger" onclick="removeFile('${file.name}')">🗑️ 删除</button>
                        </div>
                    `;
                    fileList.appendChild(fileItem);
                });
            }

            function removeFile(filename) {
                // 这里可以添加删除文件的API调用
                loadFileList();
            }

            function startBatchProcessing() {
                if (uploadedFiles.length === 0) {
                    showError('请先上传文件');
                    return;
                }

                const model = document.getElementById('modelSelect').value;
                
                // 禁用按钮
                document.getElementById('startBtn').disabled = true;
                document.getElementById('startBtn').innerHTML = '<span class="loading-spinner"></span>启动中...';
                document.getElementById('stopBtn').style.display = 'inline-block';
                
                // 隐藏错误信息
                document.getElementById('errorMessage').style.display = 'none';
                
                // 显示进度区域
                document.getElementById('progressSection').style.display = 'block';
                document.getElementById('resultSection').style.display = 'none';
                
                const filePaths = uploadedFiles.map(file => file.path);
                
                fetch('/api/process_batch', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        files: filePaths,
                        model: model
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        showError(data.error);
                        resetButtons();
                        return;
                    }
                    
                    // 开始轮询状态
                    startStatusPolling();
                    
                })
                .catch(error => {
                    showError('网络错误: ' + error.message);
                    resetButtons();
                });
            }

            function stopBatchProcessing() {
                fetch('/api/stop_batch')
                .then(response => response.json())
                .then(data => {
                    showMessage(data.message);
                    resetButtons();
                });
            }

            function startStatusPolling() {
                statusInterval = setInterval(async () => {
                    try {
                        const response = await fetch('/api/batch_status');
                        const status = await response.json();
                        
                        updateBatchProgress(status);
                        
                        if (!status.running && status.results && status.results.length > 0) {
                            // 处理完成
                            clearInterval(statusInterval);
                            showBatchResults(status.results);
                            resetButtons();
                        } else if (!status.running && status.error) {
                            // 处理出错
                            clearInterval(statusInterval);
                            showError(status.error);
                            resetButtons();
                        }
                        
                    } catch (error) {
                        console.error('获取状态失败:', error);
                    }
                }, 1000);
            }

            function updateBatchProgress(status) {
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const batchStats = document.getElementById('batchStats');
                
                if (status.total_files > 0) {
                    const progress = (status.processed_files / status.total_files) * 100;
                    progressFill.style.width = progress + '%';
                }
                
                progressText.innerHTML = status.current_step;
                
                // 更新统计信息
                batchStats.innerHTML = `
                    <div class="stat-card">
                        <div class="stat-number">${status.total_files}</div>
                        <div class="stat-label">总文件数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${status.processed_files}</div>
                        <div class="stat-label">已处理</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${status.current_file || '无'}</div>
                        <div class="stat-label">当前文件</div>
                    </div>
                `;
            }

            function showBatchResults(results) {
                const resultSection = document.getElementById('resultSection');
                const resultsList = document.getElementById('resultsList');
                
                resultsList.innerHTML = '';
                
                results.forEach(result => {
                    const item = document.createElement('div');
                    item.className = 'result-item';
                    
                    const statusClass = result.status === 'completed' ? 'status-completed' : 'status-failed';
                    const statusText = result.status === 'completed' ? '✅ 完成' : '❌ 失败';
                    
                    let content = `
                        <div class="result-header">
                            <div class="result-title">${result.file_name}</div>
                            <div class="result-status ${statusClass}">${statusText}</div>
                        </div>
                    `;
                    
                    if (result.status === 'completed') {
                        content += `
                            <div class="transcription-preview">
                                <p><strong>说话人:</strong> ${result.total_speakers} | <strong>片段:</strong> ${result.total_segments}</p>
                                ${result.transcriptions.slice(0, 3).map(trans => `
                                    <div class="transcription-item">
                                        <span class="speaker">${trans.speaker}</span>
                                        <span>${trans.text}</span>
                                    </div>
                                `).join('')}
                                ${result.transcriptions.length > 3 ? `<p>... 还有 ${result.transcriptions.length - 3} 个片段</p>` : ''}
                            </div>
                        `;
                    } else if (result.error) {
                        content += `<p style="color: #c33;">错误: ${result.error}</p>`;
                    }
                    
                    item.innerHTML = content;
                    resultsList.appendChild(item);
                });
                
                resultSection.style.display = 'block';
            }

            function downloadResults() {
                window.open('/api/download_result', '_blank');
            }

            function showError(message) {
                const errorMessage = document.getElementById('errorMessage');
                errorMessage.innerHTML = `❌ ${message}`;
                errorMessage.style.display = 'block';
            }

            function showMessage(message) {
                // 可以添加一个消息提示组件
                console.log(message);
            }

            function resetButtons() {
                document.getElementById('startBtn').disabled = false;
                document.getElementById('startBtn').innerHTML = '🚀 开始批量处理';
                document.getElementById('stopBtn').style.display = 'none';
            }
        </script>
    </body>
    </html>
    """

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """文件上传API"""
    if 'files' not in request.files:
        return jsonify({'error': '没有文件'})
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            uploaded_files.append(filename)
    
    return jsonify({
        'message': f'成功上传 {len(uploaded_files)} 个文件',
        'files': uploaded_files
    })

@app.route('/api/files')
def get_files():
    """获取文件列表API"""
    upload_files = []
    processed_files = []
    
    # 获取上传文件
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
    
    # 验证模型名称
    valid_models = ['tiny', 'base', 'small', 'medium', 'large']
    if model_name not in valid_models:
        return jsonify({'error': f'无效的模型名称: {model_name}。支持: {", ".join(valid_models)}'})
    
    if not file_paths:
        return jsonify({'error': '没有选择文件'})
    
    # 启动后台任务
    thread = threading.Thread(
        target=process_batch_files,
        args=(file_paths, model_name)
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

@app.route('/api/download_result')
def download_result():
    """下载处理结果"""
    if not batch_status['results']:
        return jsonify({'error': '没有可下载的结果'})
    
    # 格式化输出结果
    formatted_results = {
        'summary': {
            'total_files': len(batch_status['results']),
            'completed_files': len([r for r in batch_status['results'] if r.get('status') == 'completed']),
            'failed_files': len([r for r in batch_status['results'] if r.get('status') == 'failed']),
            'processing_time': time.time() - batch_status.get('start_time', time.time())
        },
        'results': batch_status['results']
    }
    
    result_file = os.path.join(TEMP_FOLDER, 'voice_recognition_results.json')
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_results, f, ensure_ascii=False, indent=2)
    
    return send_file(result_file, as_attachment=True, download_name='voice_recognition_results.json')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5002)
'''
    
    # 启动Web应用
    try:
        print("正在启动Web服务器...")
        print("Web服务器将在后台运行，请访问 http://localhost:5002")
        print("按 Ctrl+C 停止服务器")
        
        # 在后台启动Web应用
        process = subprocess.Popen([
            'conda', 'run', '-n', env_name, 'python', '-c', web_app_script
        ])
        
        # 等待用户中断
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n正在停止Web服务器...")
            process.terminate()
            process.wait()
            print("Web服务器已停止")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Web应用启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("=== VoiceRecognize 独立版应用（Conda版）===")
    print("正在初始化...")
    
    # 检查conda
    if not check_conda():
        return
    
    # 创建环境
    env_name = create_conda_environment()
    if not env_name:
        return
    
    # 安装依赖
    if not install_dependencies(env_name):
        return
    
    # 检查依赖
    if not check_dependencies(env_name):
        return
    
    # 下载模型
    if not download_models(env_name):
        return
    
    # 启动Web应用
    port = find_free_port()
    start_web_app(env_name, port)

if __name__ == '__main__':
    main()
