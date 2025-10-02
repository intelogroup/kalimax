#!/usr/bin/env python3
"""
Setup script for Kalimax Haitian Creole Translation System

This script handles initial setup tasks:
- Environment validation
- Model downloading
- Directory structure validation
- Basic dependency checks
"""

import os
import sys
import subprocess
from pathlib import Path
import yaml
from typing import Dict, Any


def check_python_version():
    """Ensure Python 3.8+ is being used"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_gpu_availability():
    """Check if CUDA GPU is available"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
            print(f"✅ CUDA available: {gpu_count} GPU(s) - {gpu_name}")
            return True
        else:
            print("⚠️  No CUDA GPU detected - training will be slower on CPU")
            return False
    except ImportError:
        print("⚠️  PyTorch not installed - cannot check GPU status")
        return False


def create_directories():
    """Ensure all necessary directories exist"""
    dirs = [
        "data/raw",
        "data/processed", 
        "data/hiccup_corpus",
        "data/examples",
        "models/base",
        "models/lora_adapters",
        "models/cache",
        "outputs/training",
        "outputs/evaluation",
        "logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")


def download_nllb_model():
    """Download the NLLB-200-distilled-600M model"""
    try:
        print("📥 Downloading NLLB-200-distilled-600M model...")
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        model_name = "facebook/nllb-200-distilled-600M"
        cache_dir = "./models/cache"
        
        print("  - Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        
        print("  - Downloading model...")
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            cache_dir=cache_dir
        )
        
        print("✅ NLLB model downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download NLLB model: {str(e)}")
        return False


def test_basic_translation():
    """Test basic translation functionality"""
    try:
        print("🧪 Testing basic translation...")
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        model_name = "facebook/nllb-200-distilled-600M"
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="./models/cache")
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name, cache_dir="./models/cache")
        
        # Test English to Haitian Creole
        text = "Hello, how are you?"
        inputs = tokenizer(text, return_tensors="pt")
        
        # Generate translation
        with tokenizer.as_target_tokenizer():
            labels = tokenizer("Bonjou, kijan ou ye?", return_tensors="pt").input_ids
        
        outputs = model.generate(
            inputs.input_ids,
            forced_bos_token_id=tokenizer.lang_code_to_id["hat_Latn"],
            max_length=50
        )
        
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"  Test translation: '{text}' -> '{translation}'")
        print("✅ Basic translation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Translation test failed: {str(e)}")
        return False


def create_sample_hiccup_corpus():
    """Create a sample hiccup corpus CSV file"""
    sample_data = """id,src_en,tgt_ht_literal,tgt_ht_localized,domain,cultural_note,flags,editor_notes,provenance
1,"The patient has chest pain","Malad la gen doulè nan pwatrin","Malad la gen doulè nan kè a","medical","'kè' is preferred for heart/chest pain in medical context","medical,urgent","Literal translation would be confusing","expert_annotation"
2,"Take this medication twice daily","Pran medikaman sa a de fwa chak jou","Pran renmèd sa a de fwa nan yon jou","medical","'renmèd' is more commonly used than 'medikaman'","medical","Cultural preference for 'renmèd'","expert_annotation"
3,"Emergency room","Chanm ijans","Sal ijans","medical","'Sal' is more appropriate for medical facilities","medical,urgent","Room vs. hall distinction","expert_annotation"
"""
    
    hiccup_file = Path("data/hiccup_corpus/sample_hiccups.csv")
    hiccup_file.write_text(sample_data)
    print("✅ Created sample hiccup corpus")


def main():
    """Main setup function"""
    print("🚀 Setting up Kalimax Haitian Creole Translation System\n")
    
    success_count = 0
    total_checks = 6
    
    # Check Python version
    if check_python_version():
        success_count += 1
    
    # Create directory structure
    try:
        create_directories()
        success_count += 1
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
    
    # Check GPU availability
    if check_gpu_availability():
        success_count += 1
    
    # Download NLLB model
    if download_nllb_model():
        success_count += 1
    
    # Test basic translation
    if test_basic_translation():
        success_count += 1
    
    # Create sample data
    try:
        create_sample_hiccup_corpus()
        success_count += 1
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
    
    # Summary
    print(f"\n📊 Setup Summary: {success_count}/{total_checks} checks passed")
    
    if success_count == total_checks:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Review the sample hiccup corpus in data/hiccup_corpus/")
        print("2. Start collecting your expert translation data")
        print("3. Run your first training experiment")
    else:
        print("⚠️  Some setup steps failed. Please review the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())