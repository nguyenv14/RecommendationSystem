#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để index coupons vào RAG system
Chạy script này để vector hóa và lưu coupons vào Qdrant
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_rag_system import SimpleRAGSystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to index coupons"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Index coupons into RAG system')
    parser.add_argument('--ollama-url', type=str, default='http://localhost:11434',
                       help='Ollama server URL (default: http://localhost:11434)')
    parser.add_argument('--qdrant-url', type=str, default='http://localhost:6333',
                       help='Qdrant server URL (default: http://localhost:6333)')
    parser.add_argument('--embedding-model', type=str, default='bge-m3',
                       help='Embedding model name (default: bge-m3)')
    parser.add_argument('--collection-name', type=str, default='hotels',
                       help='Qdrant collection name (default: hotels - same as hotels)')
    parser.add_argument('--recreate', action='store_true',
                       help='Recreate collection (will delete all data)')
    parser.add_argument('--no-chunking', action='store_true',
                       help='Disable smart chunking')
    parser.add_argument('--chunk-size', type=int, default=800,
                       help='Chunk size in characters (default: 800)')
    parser.add_argument('--chunk-overlap', type=int, default=50,
                       help='Chunk overlap in characters (default: 50)')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Batch size for processing (default: 50)')
    parser.add_argument('--valid-only', action='store_true',
                       help='Only index valid coupons (not expired, qty > 0)')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting coupon indexing...")
    logger.info(f"Configuration:")
    logger.info(f"  - Ollama URL: {args.ollama_url}")
    logger.info(f"  - Qdrant URL: {args.qdrant_url}")
    logger.info(f"  - Embedding model: {args.embedding_model}")
    logger.info(f"  - Collection name: {args.collection_name}")
    logger.info(f"  - Recreate collection: {args.recreate}")
    logger.info(f"  - Use chunking: {not args.no_chunking}")
    logger.info(f"  - Chunk size: {args.chunk_size}")
    logger.info(f"  - Chunk overlap: {args.chunk_overlap}")
    logger.info(f"  - Batch size: {args.batch_size}")
    logger.info(f"  - Valid only: {args.valid_only}")
    
    try:
        # Initialize RAG system
        logger.info("📦 Initializing RAG system...")
        rag_system = SimpleRAGSystem(
            ollama_url=args.ollama_url,
            qdrant_url=args.qdrant_url,
            embedding_model=args.embedding_model,
            collection_name=args.collection_name
        )
        
        # Index coupons from database
        logger.info("🔄 Indexing coupons from database...")
        rag_system.index_coupons_from_database(
            use_chunking=not args.no_chunking,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            incremental=not args.recreate,
            recreate_collection=args.recreate,
            batch_size=args.batch_size,
            valid_only=args.valid_only
        )
        
        logger.info("✅ Coupon indexing completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during coupon indexing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()



