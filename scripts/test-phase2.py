#!/usr/bin/env python3
"""
Phase 2 Validation Test
Tests the enhanced LLM service and model integration
"""

import sys
import os
sys.path.append('.')

def test_imports():
    """Test if all required packages are installed"""
    print("🧪 Testing Phase 2 Dependencies...")
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
        
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
        
        import huggingface_hub
        print(f"✅ Hugging Face Hub: {huggingface_hub.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_model_files():
    """Test if model files are downloaded"""
    print("\n📁 Testing Model Files...")
    
    phi3_path = "./models/phi-3-mini-4k-instruct"
    
    if os.path.exists(phi3_path):
        print("✅ Phi-3-mini model directory exists")
        
        config_file = os.path.join(phi3_path, "config.json")
        if os.path.exists(config_file):
            print("✅ Phi-3-mini config.json found")
            
            # Check model files
            model_files = [f for f in os.listdir(phi3_path) if f.endswith('.safetensors')]
            print(f"✅ Found {len(model_files)} model files")
            
            total_size = sum(os.path.getsize(os.path.join(phi3_path, f)) for f in model_files)
            print(f"✅ Total model size: {total_size / (1024**3):.1f} GB")
            
            return True
        else:
            print("⚠️ Config file missing")
            return False
    else:
        print("❌ Phi-3-mini model not found")
        return False

def test_gpu_availability():
    """Test GPU availability for model acceleration"""
    print("\n🔥 Testing GPU Availability...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"✅ GPU Available: {gpu_name}")
            print(f"✅ GPU Memory: {gpu_memory:.1f} GB")
            
            if "4060" in gpu_name:
                print("🎯 Perfect! RTX 4060 detected - optimal for our setup")
            
            return True
        else:
            print("⚠️ No GPU available, will use CPU")
            return False
            
    except Exception as e:
        print(f"❌ GPU test failed: {e}")
        return False

def test_database():
    """Test database availability"""
    print("\n🗄️ Testing Database...")
    
    db_path = "./data/wellness_platform.db"
    
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path)
        print(f"✅ SQLite database found: {db_size} bytes")
        return True
    else:
        print("❌ Database not found")
        return False

def main():
    """Run all Phase 2 validation tests"""
    print("🚀 Phase 2: Local LLM Integration - Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Dependencies", test_imports),
        ("Model Files", test_model_files), 
        ("GPU Support", test_gpu_availability),
        ("Database", test_database)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Phase 2 Validation Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    success_rate = (passed / len(results)) * 100
    print(f"\nSuccess Rate: {success_rate:.0f}% ({passed}/{len(results)})")
    
    if success_rate >= 75:
        print("🎉 Phase 2 infrastructure is ready!")
        print("Next: Start LLM service and create React frontend")
    else:
        print("⚠️ Some components need attention before proceeding")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)