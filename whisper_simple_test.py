#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Whisper测试
"""

import os
import time
import whisper

def test_whisper_models():
    """测试Whisper模型"""
    print("🧪 测试Whisper模型...")
    
    # 测试音频文件
    audio_file = "ba84462e-fdee-42fe-9439-86808b3d3212.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ 音频文件不存在: {audio_file}")
        return None
    
    try:
        # 加载small模型
        print("🔄 加载Whisper small模型...")
        start_time = time.time()
        model = whisper.load_model("small")
        load_time = time.time() - start_time
        print(f"✅ small模型加载完成，耗时: {load_time:.2f}秒")
        
        # 检查模型信息
        total_params = sum(p.numel() for p in model.parameters())
        print(f"📊 模型参数数量: {total_params:,}")
        
        # 转录
        print("📝 开始转录...")
        transcribe_start = time.time()
        
        result = model.transcribe(audio_file, verbose=True)
        
        transcribe_time = time.time() - transcribe_start
        print(f"✅ 转录完成，耗时: {transcribe_time:.2f}秒")
        
        # 保存结果
        output_file = "whisper_simple_result.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== Whisper Simple 转录结果 ===\n\n")
            f.write(f"使用模型: small\n")
            f.write(f"模型参数: {total_params:,}\n")
            f.write(f"加载时间: {load_time:.2f}秒\n")
            f.write(f"转录时间: {transcribe_time:.2f}秒\n")
            f.write(f"检测语言: {result.get('language', '未知')}\n\n")
            f.write("转录文本:\n")
            f.write(result["text"])
        
        print(f"💾 结果已保存到: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"❌ Whisper转录失败: {e}")
        return None

def main():
    """主函数"""
    print("🎯 Whisper 简单测试")
    print("=" * 30)
    
    result = test_whisper_models()
    
    if result:
        print(f"\n🎉 测试完成！")
        print(f"📋 模型信息:")
        print(f"  - 模型: small")
        print(f"  - 参数: 244M")
        print(f"  - 语言: {result.get('language', '未知')}")
        print(f"  - 文本长度: {len(result['text'])} 字符")
    else:
        print(f"\n❌ 测试失败")

if __name__ == "__main__":
    main() 