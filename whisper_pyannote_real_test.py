#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper + Pyannote 实际运行测试
"""

import os
import sys
import time
import json
import subprocess

def check_models():
    """检查可用的模型"""
    print("🔍 检查可用模型...")
    
    # 检查Whisper模型
    try:
        import whisper
        print("✅ Whisper可用")
        
        # 列出Whisper模型
        whisper_models = ["tiny", "base", "small", "medium", "large"]
        print(f"📋 Whisper模型: {', '.join(whisper_models)}")
        
    except ImportError:
        print("❌ Whisper不可用")
        return False
    
    # 检查Pyannote模型
    try:
        from pyannote.audio import Pipeline
        print("✅ Pyannote可用")
        print("📋 Pyannote模型: pyannote/speaker-diarization")
        
    except ImportError:
        print("❌ Pyannote不可用")
        return False
    
    return True

def test_whisper_models():
    """测试Whisper模型"""
    print("\n🧪 测试Whisper模型...")
    
    try:
        import whisper
        
        # 测试加载small模型
        print("🔄 加载Whisper small模型...")
        start_time = time.time()
        model = whisper.load_model("small")
        load_time = time.time() - start_time
        print(f"✅ small模型加载完成，耗时: {load_time:.2f}秒")
        
        # 检查模型信息
        print(f"📊 模型参数数量: {sum(p.numel() for p in model.parameters()):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper模型测试失败: {e}")
        return False

def test_pyannote_setup():
    """测试Pyannote设置"""
    print("\n🧪 测试Pyannote设置...")
    
    try:
        from pyannote.audio import Pipeline
        
        print("📋 Pyannote需要HuggingFace访问令牌")
        print("🔗 获取地址: https://huggingface.co/pyannote/speaker-diarization")
        print("📝 模型名称: pyannote/speaker-diarization")
        
        # 检查是否有访问令牌
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            print("✅ 找到HuggingFace访问令牌")
        else:
            print("⚠️  未找到HuggingFace访问令牌")
            print("💡 请设置环境变量: export HF_TOKEN=your_token")
        
        return True
        
    except Exception as e:
        print(f"❌ Pyannote设置测试失败: {e}")
        return False

def run_whisper_only_test():
    """仅运行Whisper测试"""
    print("\n🎯 运行Whisper转录测试...")
    
    audio_file = "ba84462e-fdee-42fe-9439-86808b3d3212.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return None
    
    try:
        import whisper
        
        # 加载small模型
        print("🔄 加载Whisper small模型...")
        model = whisper.load_model("small")
        
        # 转录前60秒
        print("📝 转录前60秒音频...")
        start_time = time.time()
        
        result = model.transcribe(
            audio_file,
            start=0,
            end=60,
            verbose=True
        )
        
        transcribe_time = time.time() - start_time
        print(f"✅ 转录完成，耗时: {transcribe_time:.2f}秒")
        
        # 保存结果
        output_file = "whisper_only_result.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== Whisper Only 转录结果 ===\n\n")
            f.write(f"使用模型: small\n")
            f.write(f"转录时间: {transcribe_time:.2f}秒\n")
            f.write(f"音频片段: 0-60秒\n\n")
            f.write("转录文本:\n")
            f.write(result["text"])
        
        print(f"💾 结果已保存到: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Whisper转录失败: {e}")
        return None

def create_pyannote_whisper_script():
    """创建Pyannote+Whisper完整脚本"""
    script_content = '''#!/usr/bin/env python3
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
        f.write("=== Pyannote + Whisper 完整转录结果 ===\\n\\n")
        f.write("使用模型:\\n")
        f.write("- Pyannote: pyannote/speaker-diarization\\n")
        f.write("- Whisper: small\\n\\n")
        
        for result in results:
            f.write(f"[{result['start']:.1f}s - {result['end']:.1f}s] {result['speaker']}: {result['text']}\\n")
    
    print(f"\\n💾 结果已保存到: {output_file}")
    
    # 显示结果预览
    print("\\n📋 转录结果预览:")
    print("-" * 40)
    for result in results[:5]:  # 只显示前5个片段
        print(f"[{result['start']:.1f}s - {result['end']:.1f}s] {result['speaker']}: {result['text']}")

if __name__ == "__main__":
    main()
'''
    
    with open("pyannote_whisper_complete.py", 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 已创建完整脚本: pyannote_whisper_complete.py")

def main():
    """主函数"""
    print("🎯 Whisper + Pyannote 实际运行测试")
    print("=" * 50)
    
    # 检查模型
    if not check_models():
        print("❌ 模型检查失败")
        return
    
    # 测试Whisper模型
    if not test_whisper_models():
        print("❌ Whisper模型测试失败")
        return
    
    # 测试Pyannote设置
    if not test_pyannote_setup():
        print("❌ Pyannote设置测试失败")
        return
    
    # 运行Whisper测试
    whisper_result = run_whisper_only_test()
    
    # 创建完整脚本
    create_pyannote_whisper_script()
    
    print(f"\n🎉 测试完成！")
    print(f"💡 完整脚本已创建: pyannote_whisper_complete.py")
    print(f"📋 模型信息:")
    print(f"  - Whisper: small (244M参数)")
    print(f"  - Pyannote: pyannote/speaker-diarization")
    print(f"💡 要运行完整流程，请设置HF_TOKEN环境变量")

if __name__ == "__main__":
    main() 