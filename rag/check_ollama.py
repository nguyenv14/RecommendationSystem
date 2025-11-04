#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Ollama models and setup
"""

import requests
import json

def check_ollama():
    """Check Ollama models"""
    ollama_url = "http://localhost:11434"
    
    print("🔍 Checking Ollama...")
    
    # Check if Ollama is running
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running")
            print(f"\n📦 Available models:")
            for model in models.get("models", []):
                print(f"   - {model.get('name', 'Unknown')}")
            
            # Check for required models
            model_names = [m.get('name', '') for m in models.get("models", [])]
            required_models = ["bge-m3", "llama2"]
            
            print(f"\n🔍 Checking required models:")
            for model in required_models:
                if any(model in name for name in model_names):
                    print(f"   ✅ {model} - Available")
                else:
                    print(f"   ❌ {model} - Not found")
                    print(f"      Run: ollama pull {model}")
            
            return True
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama")
        print(f"   Make sure Ollama is running on {ollama_url}")
        print("   Start Ollama: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False


def test_embedding():
    """Test embedding API"""
    ollama_url = "http://localhost:11434"
    
    print("\n🧪 Testing Embedding API...")
    
    try:
        response = requests.post(
            f"{ollama_url}/api/embeddings",
            json={
                "model": "bge-m3",
                "prompt": "test"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get('embedding', [])
            print(f"✅ Embedding API works")
            print(f"   Embedding dimension: {len(embedding)}")
            return True
        else:
            print(f"❌ Embedding API returned status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing embedding: {e}")
        return False


def main():
    """Main function"""
    print("="*60)
    print("Ollama Setup Check")
    print("="*60)
    
    # Check Ollama
    ollama_ok = check_ollama()
    
    if ollama_ok:
        # Test embedding
        embedding_ok = test_embedding()
        
        if embedding_ok:
            print("\n✅ Ollama is ready!")
        else:
            print("\n⚠️  Embedding API has issues")
            print("   Try: ollama pull bge-m3")
    else:
        print("\n❌ Ollama setup incomplete")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

