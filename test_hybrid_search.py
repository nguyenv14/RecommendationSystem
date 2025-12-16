#!/usr/bin/env python3
"""
Test script to verify hybrid search is working
"""

import os
import sys

# Unset HF_HUB_OFFLINE before importing
_original_hf_offline = os.environ.get('HF_HUB_OFFLINE')
if _original_hf_offline == '1':
    if 'HF_HUB_OFFLINE' in os.environ:
        del os.environ['HF_HUB_OFFLINE']
    print("⚠️  Temporarily unset HF_HUB_OFFLINE")

# Now import
from src.core import SparseEmbeddingService

print("=" * 80)
print("🧪 Testing Hybrid Search Setup")
print("=" * 80)

# Test sparse embedding service
print("\n1️⃣ Testing SparseEmbeddingService...")
try:
    sparse_service = SparseEmbeddingService(
        model_name="Qdrant/bm25",
        allow_download=True
    )
    
    if sparse_service.is_available:
        print("✅ SparseEmbeddingService is available!")
        
        # Test embedding
        print("\n2️⃣ Testing sparse embedding generation...")
        test_query = "khách sạn 5 sao"
        sparse_vector = sparse_service.embed_query(test_query)
        
        if sparse_vector:
            print(f"✅ Generated sparse vector for: '{test_query}'")
            print(f"   Vector size: {len(sparse_vector)} tokens")
            print("✅ Hybrid search is READY!")
        else:
            print("⚠️  Sparse vector is empty")
    else:
        print("❌ SparseEmbeddingService is NOT available")
        print("   Hybrid search will use semantic search only")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Restore original value
if _original_hf_offline == '1':
    os.environ['HF_HUB_OFFLINE'] = '1'
    print(f"\n🔄 Restored HF_HUB_OFFLINE={_original_hf_offline}")

print("\n" + "=" * 80)
