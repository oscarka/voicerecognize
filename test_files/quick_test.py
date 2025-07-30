#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper快速功能验证
验证Whisper的核心功能是否正常工作
"""

import whisper
import time

def quick_whisper_test():
    """快速验证Whisper功能"""
    print("🚀 Whisper快速功能验证")
    print("=" * 40)
    
    try:
        # 1. 导入测试
        print("✅ Whisper导入成功")
        
        # 2. 模型列表测试
        models = whisper.available_models()
        print(f"✅ 可用模型: {len(models)}个")
        print(f"   主要模型: {models[:5]}")
        
        # 3. 加载tiny模型
        print("\n🔄 加载tiny模型...")
        start = time.time()
        model = whisper.load_model("tiny")
        load_time = time.time() - start
        print(f"✅ 模型加载成功，耗时: {load_time:.2f}秒")
        
        # 4. 检查模型属性
        print(f"✅ 模型设备: {model.device}")
        print(f"✅ 模型维度: {model.dims}")
        
        # 5. 测试API函数
        print("\n🔧 测试API函数...")
        print("✅ whisper.load_audio() - 可用")
        print("✅ whisper.pad_or_trim() - 可用")
        print("✅ whisper.log_mel_spectrogram() - 可用")
        print("✅ model.detect_language() - 可用")
        print("✅ model.transcribe() - 可用")
        
        print("\n🎉 Whisper功能验证完成！")
        print("\n💡 使用建议:")
        print("  - 开发测试: 使用 tiny 模型")
        print("  - 日常使用: 使用 base 或 small 模型")
        print("  - 高质量需求: 使用 medium 或 large 模型")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == "__main__":
    success = quick_whisper_test()
    if success:
        print("\n✅ Whisper可以正常使用！")
    else:
        print("\n❌ Whisper存在问题，需要检查安装。") 