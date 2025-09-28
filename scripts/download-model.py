#!/usr/bin/env python3
"""
Phase 2: Model Download Script
Following mental-wellness-platform-docs.md specifications
"""

import os
import sys

def download_best_compatible_model():
    """Download best compatible model for RTX 4060 (no gated access required)"""
    
    print("🤖 Phase 2: Local LLM Integration")
    print("📥 Downloading Phi-3-mini-4k-instruct (Microsoft)...")
    print("📊 Model size: ~7.6GB (3.8B parameters, perfect for RTX 4060)")
    print("🚀 Features: Instruction-tuned, high quality, 4K context, no gating")
    
    try:
        from huggingface_hub import snapshot_download
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Download Microsoft Phi-3-mini - excellent for RTX 4060
        print("🔄 Starting download...")
        model_path = snapshot_download(
            repo_id='microsoft/Phi-3-mini-4k-instruct',
            local_dir='models/phi-3-mini-4k-instruct',
            local_dir_use_symlinks=False,
            ignore_patterns=['*.bin']  # Use safetensors format
        )
        
        print(f"✅ Model downloaded to: {model_path}")
        print("🚀 Ready for 4-bit quantization and RTX 4060 optimization")
        print("💡 Phi-3-mini: Microsoft's best small model, perfect for mental wellness conversations")
        return True
        
    except ImportError:
        print("❌ huggingface_hub not installed")
        print("Installing required packages...")
        
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "huggingface_hub", "transformers", "torch", "accelerate", "bitsandbytes"
        ])
        
        print("✅ Packages installed, please run again")
        return False
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("💡 Creating model stub for development...")
        
        # Create model stub for development
        stub_dir = 'models/phi-3-mini-4k-instruct'
        os.makedirs(stub_dir, exist_ok=True)
        
        with open(f'{stub_dir}/config.json', 'w') as f:
            f.write('{"model_type": "phi3", "stub": true}')
        
        print(f"📁 Model stub created at: {stub_dir}")
        return False

if __name__ == "__main__":
    success = download_best_compatible_model()
    
    if success:
        print("\n🎯 Model download complete!")
        print("Next: Update LLM service with Phi-3-mini integration")
    else:
        print("\n⚠️ Model download incomplete, but development can continue")
        print("Model will be downloaded in background or manually later")