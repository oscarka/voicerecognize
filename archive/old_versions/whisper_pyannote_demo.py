#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper + Pyannote 组合演示
实现说话人分离 + 语音转录的完整流程
"""

import os
import sys
import time
import json
from pathlib import Path

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查Whisper + Pyannote依赖...")
    
    required_packages = [
        "whisper",
        "torch", 
        "torchaudio",
        "pyannote.audio",
        "pyannote.core"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace(".", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 需要安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 需要安装的包:")
        for pkg in missing_packages:
            if pkg == "pyannote.audio":
                print(f"  pip install pyannote.audio")
            elif pkg == "pyannote.core":
                print(f"  pip install pyannote.core")
            else:
                print(f"  pip install {pkg}")
        
        print(f"\n💡 安装命令:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def install_pyannote():
    """安装Pyannote相关包"""
    print("📦 安装Pyannote...")
    
    try:
        import subprocess
        
        # 安装pyannote.audio
        print("🔄 安装pyannote.audio...")
        result = subprocess.run([
            "pip", "install", "pyannote.audio"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ pyannote.audio安装成功")
        else:
            print(f"❌ pyannote.audio安装失败: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False

def demo_whisper_pyannote_workflow():
    """演示Whisper + Pyannote工作流程"""
    print("\n🚀 Whisper + Pyannote 工作流程演示")
    print("=" * 50)
    
    # 1. 说话人分离 (Speaker Diarization)
    print("\n1️⃣ 说话人分离阶段")
    print("-" * 30)
    print("📊 使用Pyannote.audio进行说话人分离")
    print("🎯 识别音频中的不同说话人")
    print("⏱️  标记每个说话人的时间戳")
    
    # 模拟分离结果
    diarization_result = {
        "speakers": [
            {
                "speaker": "SPEAKER_00",
                "segments": [
                    {"start": 0.0, "end": 15.5, "text": "医生说话部分"},
                    {"start": 25.2, "end": 40.8, "text": "医生继续说话"}
                ]
            },
            {
                "speaker": "SPEAKER_01", 
                "segments": [
                    {"start": 15.5, "end": 25.2, "text": "患者说话部分"},
                    {"start": 40.8, "end": 60.0, "text": "患者继续说话"}
                ]
            }
        ]
    }
    
    print("✅ 说话人分离完成")
    print(f"📋 识别到 {len(diarization_result['speakers'])} 个说话人")
    
    # 2. 语音转录 (Speech-to-Text)
    print("\n2️⃣ 语音转录阶段")
    print("-" * 30)
    print("📝 使用Whisper进行语音转录")
    print("🎯 为每个说话人片段生成文本")
    
    # 模拟转录结果
    transcription_result = {
        "segments": [
            {
                "speaker": "SPEAKER_00",
                "start": 0.0,
                "end": 15.5,
                "text": "您好，我是医生。请问您有什么症状？"
            },
            {
                "speaker": "SPEAKER_01", 
                "start": 15.5,
                "end": 25.2,
                "text": "我们家老人有高血糖、高血压，现在牙疼。"
            },
            {
                "speaker": "SPEAKER_00",
                "start": 25.2,
                "end": 40.8,
                "text": "牙疼多久了？有没有其他症状？"
            },
            {
                "speaker": "SPEAKER_01",
                "start": 40.8,
                "end": 60.0,
                "text": "大概一周了，去医院看了说要拔牙。"
            }
        ]
    }
    
    print("✅ 语音转录完成")
    
    # 3. 结果整合
    print("\n3️⃣ 结果整合")
    print("-" * 30)
    
    # 保存结果
    output_file = "whisper_pyannote_result.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== Whisper + Pyannote 转录结果 ===\n\n")
        f.write("说话人分离 + 语音转录\n\n")
        
        for segment in transcription_result["segments"]:
            speaker = "医生" if segment["speaker"] == "SPEAKER_00" else "患者"
            f.write(f"[{segment['start']:.1f}s - {segment['end']:.1f}s] {speaker}: {segment['text']}\n")
    
    print("✅ 结果已保存到:", output_file)
    
    # 显示结果
    print("\n📋 转录结果预览:")
    print("-" * 40)
    for segment in transcription_result["segments"]:
        speaker = "医生" if segment["speaker"] == "SPEAKER_00" else "患者"
        print(f"[{segment['start']:.1f}s - {segment['end']:.1f}s] {speaker}: {segment['text']}")
    
    return True

def create_whisper_pyannote_script():
    """创建完整的Whisper+Pyannote脚本"""
    script_content = '''#!/usr/bin/env python3
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
        f.write("=== Whisper + Pyannote 完整转录结果 ===\\n\\n")
        
        for result in results:
            f.write(f"[{result['start']:.1f}s - {result['end']:.1f}s] {result['speaker']}: {result['text']}\\n")
    
    print(f"\\n💾 结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
'''
    
    with open("whisper_pyannote_complete.py", 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 已创建完整脚本: whisper_pyannote_complete.py")

def main():
    """主函数"""
    print("🎯 Whisper + Pyannote 组合演示")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n💡 建议安装Pyannote:")
        print("pip install pyannote.audio")
        print("pip install pyannote.core")
        print("\n⚠️  注意: Pyannote需要HuggingFace访问令牌")
        print("获取地址: https://huggingface.co/pyannote/speaker-diarization")
        
        # 询问是否安装
        response = input("\n是否现在安装Pyannote? (y/n): ")
        if response.lower() == 'y':
            if install_pyannote():
                print("✅ Pyannote安装成功")
            else:
                print("❌ Pyannote安装失败")
                return
    
    # 演示工作流程
    demo_whisper_pyannote_workflow()
    
    # 创建完整脚本
    create_whisper_pyannote_script()
    
    print(f"\n🎉 演示完成！")
    print(f"💡 完整实现脚本已创建: whisper_pyannote_complete.py")

if __name__ == "__main__":
    main() 