#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để recreate Qdrant collection với HNSW config mới
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from simple_rag_system import SimpleRAGSystem

def main():
    """Recreate collection với HNSW config mới"""
    
    print("🔄 Recreating Qdrant Collection with HNSW Config")
    print("=" * 60)
    
    # Initialize RAG system
    rag = SimpleRAGSystem(
        ollama_url="http://localhost:11434",
        qdrant_url="http://localhost:6333",
        embedding_model="bge-m3",
        llm_model="qwen3",
        collection_name="hotels"
    )
    
    # Check current config
    print("\n📊 Checking current collection...")
    try:
        config_info = rag.verify_hnsw_config()
        print(f"Collection: {config_info['collection_name']}")
        print(f"Points count: {config_info.get('points_count', 0):,}")
        
        if config_info.get('hnsw_configured'):
            print(f"HNSW Config: m={config_info.get('m')}, ef_construct={config_info.get('ef_construct')}")
            print(f"full_scan_threshold: {config_info.get('full_scan_threshold')}")
        else:
            print("⚠️  HNSW not configured")
    except Exception as e:
        print(f"⚠️  Error checking collection: {e}")
    
    # Confirm
    print("\n⚠️  WARNING: This will DELETE all existing data in the collection!")
    print("   The collection will be recreated with optimized HNSW config:")
    print("   - m=16")
    print("   - ef_construct=200")
    print("   - full_scan_threshold=10 (HNSW enabled for datasets > 10 vectors)")
    
    confirm = input("\nType 'yes' to confirm: ").strip().lower()
    
    if confirm != 'yes':
        print("\n❌ Cancelled. Collection not modified.")
        return
    
    # Recreate collection
    print("\n🔄 Recreating collection...")
    try:
        rag.index_hotels(
            normalized_data_path="rag/normalized_data/normalized_hotels.csv",
            recreate_collection=True
        )
        
        # Verify new config
        print("\n✅ Collection recreated successfully!")
        print("\n📊 Verifying new HNSW config...")
        config_info = rag.verify_hnsw_config()
        
        if config_info.get('hnsw_configured'):
            print(f"✅ HNSW Config: m={config_info.get('m')}, ef_construct={config_info.get('ef_construct')}")
            print(f"✅ full_scan_threshold: {config_info.get('full_scan_threshold')}")
            print(f"✅ Points count: {config_info.get('points_count', 0):,}")
        else:
            print("⚠️  HNSW config verification failed")
            
    except Exception as e:
        print(f"\n❌ Error recreating collection: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n✅ Done! Collection recreated with optimized HNSW config.")


if __name__ == "__main__":
    main()

