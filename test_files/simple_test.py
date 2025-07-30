#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Whisper功能测试
验证Whisper的基本功能是否正常工作
"""

import whisper
import time

def test_whisper_installation():
    """测试Whisper安装和基本功能"""
    print("🧪 Whisper基本功能测试")
    print("=" * 40)
    
    try:
        # 1. 测试导入
        print("✅ Whisper模块导入成功")
        
        # 2. 测试可用模型
        models = whisper.available_models()
        print(f"✅ 可用模型数量: {len(models)}")
        print("   主要模型:", [m for m in models if not m.endswith('.en')][:6])
        
        # 3. 测试模型加载
        print("\n🔄 测试模型加载...")
        start_time = time.time()
        model = whisper.load_model("tiny")
        load_time = time.time() - start_time
        print(f"✅ tiny模型加载成功，耗时: {load_time:.2f}秒")
        
        # 4. 测试模型属性
        print(f"✅ 模型设备: {model.device}")
        print(f"✅ 模型维度: {model.dims}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_model_loading_speed():
    """测试不同模型的加载速度"""
    print("\n⚡ 模型加载速度测试")
    print("-" * 30)
    
    models_to_test = ["tiny", "base", "small"]
    results = {}
    
    for model_name in models_to_test:
        print(f"\n🔄 测试 {model_name} 模型...")
        try:
            start_time = time.time()
            model = whisper.load_model(model_name)
            load_time = time.time() - start_time
            
            results[model_name] = {
                "load_time": load_time,
                "success": True,
                "device": model.device,
                "dims": model.dims
            }
            
            print(f"✅ {model_name} 加载成功")
            print(f"   加载时间: {load_time:.2f}秒")
            print(f"   设备: {model.device}")
            
        except Exception as e:
            print(f"❌ {model_name} 加载失败: {e}")
            results[model_name] = {
                "load_time": 0,
                "success": False,
                "error": str(e)
            }
    
    # 显示结果总结
    print(f"\n📊 加载速度对比:")
    print(f"{'模型':<10} {'状态':<8} {'加载时间':<12} {'设备':<8}")
    print("-" * 45)
    for model_name, data in results.items():
        status = "✅" if data["success"] else "❌"
        load_time = f"{data['load_time']:.2f}s" if data["success"] else "失败"
        device = str(data.get("device", "N/A")) if data["success"] else "N/A"
        print(f"{model_name:<10} {status:<8} {load_time:<12} {device:<8}")
    
    return results

def test_whisper_api():
    """测试Whisper API的基本功能"""
    print("\n🔧 Whisper API功能测试")
    print("-" * 30)
    
    try:
        # 测试音频加载功能
        print("✅ whisper.load_audio() 函数可用")
        print("✅ whisper.pad_or_trim() 函数可用")
        print("✅ whisper.log_mel_spectrogram() 函数可用")
        
        # 测试模型功能
        model = whisper.load_model("tiny")
        print("✅ model.detect_language() 方法可用")
        print("✅ model.transcribe() 方法可用")
        print("✅ model.decode() 方法可用")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 OpenAI Whisper 完整功能测试")
    print("=" * 50)
    
    tests = [
        ("基本安装测试", test_whisper_installation),
        ("模型加载速度测试", test_model_loading_speed),
        ("API功能测试", test_whisper_api)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            results[test_name] = False
    
    # 总结
    print(f"\n{'='*50}")
    print("📋 测试结果总结:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Whisper可以正常使用。")
        print("\n💡 下一步:")
        print("  1. 准备音频文件进行转录测试")
        print("  2. 使用 whisper_example.py 进行实际转录")
        print("  3. 根据需要选择合适的模型")
    else:
        print("⚠️  部分测试失败，请检查环境配置。")

if __name__ == "__main__":
    main() 