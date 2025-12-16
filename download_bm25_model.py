#!/usr/bin/env python3
"""
Script to download BM25 model for hybrid search
This script will download the Qdrant/bm25 model even if HF_HUB_OFFLINE is set
"""

import os
import sys

def download_bm25_model():
    """Download BM25 model for hybrid search"""
    print("=" * 80)
    print("📥 Downloading BM25 Model for Hybrid Search")
    print("=" * 80)
    
    # Temporarily unset HF_HUB_OFFLINE
    original_offline = os.environ.get('HF_HUB_OFFLINE')
    if original_offline:
        print(f"⚠️  HF_HUB_OFFLINE is set to: {original_offline}")
        print("   Temporarily unsetting to allow model download...")
        del os.environ['HF_HUB_OFFLINE']
    
    try:
        print("\n📦 Loading BM25 model (this may take a few minutes on first run)...")
        from fastembed import SparseTextEmbedding
        
        model = SparseTextEmbedding(model_name="Qdrant/bm25")
        print("✅ BM25 model loaded successfully!")
        
        # Test embedding
        print("\n🧪 Testing model...")
        test_text = "khách sạn 5 sao"
        embeddings = list(model.embed([test_text]))
        if embeddings:
            print(f"✅ Model test successful! Generated embedding for: '{test_text}'")
            print(f"   Embedding size: {len(embeddings[0].indices) if hasattr(embeddings[0], 'indices') else 'N/A'}")
        else:
            print("⚠️  Model loaded but test embedding returned empty")
        
        print("\n" + "=" * 80)
        print("✅ BM25 model is ready for hybrid search!")
        print("=" * 80)
        print("\n💡 Next steps:")
        print("   1. Restart your application")
        print("   2. Hybrid search will be automatically enabled")
        print("   3. You can verify by checking logs for 'Hybrid Search enabled'")
        
        return True
        
    except ImportError:
        print("❌ Error: fastembed is not installed")
        print("   Install it with: pip install fastembed")
        return False
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your internet connection")
        print("   2. Ensure you can access https://huggingface.co")
        print("   3. Try unsetting HF_HUB_OFFLINE manually:")
        print("      export HF_HUB_OFFLINE=0")
        print("   4. Or download model manually:")
        print("      python -c 'from fastembed import SparseTextEmbedding; SparseTextEmbedding(\"Qdrant/bm25\")'")
        return False
        
    finally:
        # Restore original HF_HUB_OFFLINE value
        if original_offline is not None:
            os.environ['HF_HUB_OFFLINE'] = original_offline
            print(f"\n🔄 Restored HF_HUB_OFFLINE={original_offline}")


if __name__ == "__main__":
    success = download_bm25_model()
    sys.exit(0 if success else 1)
