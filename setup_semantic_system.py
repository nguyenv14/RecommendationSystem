#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Setup Script for Semantic Recommendation System
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'pandas',
        'numpy',
        'torch',
        'transformers',
        'sentence_transformers',
        'qdrant_client'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements_semantic.txt")
        return False
    
    return True

def check_qdrant():
    """Check if Qdrant is running"""
    import requests
    try:
        response = requests.get('http://localhost:6333/health', timeout=2)
        if response.status_code == 200:
            print("✓ Qdrant is running")
            return True
    except:
        print("✗ Qdrant is not running")
        print("\nStart Qdrant with Docker:")
        print("  docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")
        return False

def check_gpu():
    """Check if GPU is available"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ GPU available: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA version: {torch.version.cuda}")
            return True
        else:
            print("✗ GPU not available, using CPU")
            return False
    except:
        print("✗ Could not check GPU")
        return False

def main():
    print("=" * 60)
    print("Semantic Recommendation System - Setup Check")
    print("=" * 60)
    
    print("\n1. Checking Python packages...")
    packages_ok = check_requirements()
    
    print("\n2. Checking Qdrant server...")
    qdrant_ok = check_qdrant()
    
    print("\n3. Checking GPU...")
    gpu_ok = check_gpu()
    
    print("\n" + "=" * 60)
    
    if packages_ok and qdrant_ok:
        print("✓ System ready to use!")
        print("\nRun: python semantic_recommendation_system.py")
    else:
        if not packages_ok:
            print("\n✗ Please install missing packages")
        if not qdrant_ok:
            print("✗ Please start Qdrant server")
        sys.exit(1)

if __name__ == '__main__':
    main()

