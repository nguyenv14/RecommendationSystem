#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Collections Script
Tạo collections và index data từ database
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_settings, Collections
from src.shared import get_logger, setup_logging
from src.core import VectorStoreService, IndexingService
from qdrant_client.models import Distance, VectorParams

# Setup logging
setup_logging()
logger = get_logger(__name__)


def create_collections(vectorstore: VectorStoreService):
    """
    Tạo các collections cần thiết với vector size phù hợp
    - RAG: 1024 dims (bge-m3)
    - Recommendation: 1024 dims (dùng chung bge-m3 cho đơn giản)
    """
    logger.info("=" * 80)
    logger.info("🔧 Creating Collections")
    logger.info("=" * 80)
    
    collections_to_create = [
        (Collections.RAG_HOTELS, "RAG Hotels (Chatbot)", 1024, "🏨"),
        (Collections.RAG_COUPONS, "RAG Coupons (Chatbot)", 1024, "🎟️"),
        (Collections.RECOMMENDATION_HOTELS, "Recommendation Hotels (Similar)", 1024, "🎯"),
    ]
    
    client = vectorstore.client
    
    for collection_name, description, vector_size, emoji in collections_to_create:
        try:
            # Check if exists
            collections = client.get_collections()
            existing_names = [col.name for col in collections.collections]
            
            if collection_name in existing_names:
                info = client.get_collection(collection_name)
                logger.info(f"✅ {emoji} {description} ({collection_name}): {info.points_count} points")
            else:
                # Create collection with hybrid search support (dense + sparse)
                try:
                    from qdrant_client.models import SparseVectorParams
                    client.create_collection(
                        collection_name=collection_name,
                        vectors_config={
                            "dense": VectorParams(
                                size=vector_size,
                                distance=Distance.COSINE
                            )
                        },
                        sparse_vectors_config={
                            "sparse": SparseVectorParams()  # BM25 for keyword search
                        }
                    )
                    logger.info(f"✅ {emoji} {description} ({collection_name}): Created with hybrid search")
                except Exception as e:
                    logger.warning(f"Failed to create with sparse vectors: {e}, trying dense only")
                    # Fallback to dense only
                    client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=vector_size,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"✅ {emoji} {description} ({collection_name}): Created (dense only)")
                
        except Exception as e:
            logger.error(f"❌ Error creating {collection_name}: {e}")


def index_rag_data():
    """
    Index data cho RAG system (chatbot)
    Logic từ rag/simple_rag_system.py
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("🤖 RAG: Indexing Data for Chatbot")
    logger.info("=" * 80)
    
    try:
        # Import RAG system
        sys.path.insert(0, str(Path(__file__).parent / 'rag'))
        from simple_rag_system import SimpleRAGSystem
        
        # Initialize RAG system
        logger.info("Initializing RAG system...")
        settings = get_settings()
        rag = SimpleRAGSystem(
            collection_name=settings.RAG_COLLECTION_HOTELS,
            qdrant_url=settings.QDRANT_URL,
            ollama_url=settings.OLLAMA_URL,
            embedding_model=settings.EMBEDDING_MODEL,
            llm_model=settings.LLM_MODEL
        )
        
        # Index hotels
        logger.info("\n📊 Indexing hotels...")
        rag.index_hotels_from_database(
            use_chunking=True,
            chunk_size=800,
            recreate_collection=False,
            batch_size=10,
            incremental=True
        )
        
        # Index rooms and type_rooms (cùng collection với hotels)
        logger.info("\n📊 Indexing rooms and type_rooms...")
        try:
            from data.processor import DataProcessor
            from data.connector import DatabaseConnector
            from data.normalizer import HotelDataNormalizer
            
            processor = DataProcessor(rag=rag)
            
            # Index rooms
            logger.info("  🔄 Indexing rooms...")
            processor.process_and_index_rooms(
                recreate_collection=False,
                batch_size=50
            )
            
            # Index type_rooms
            logger.info("  🔄 Indexing type_rooms...")
            processor.process_and_index_type_rooms(
                recreate_collection=False,
                batch_size=50
            )
            
            logger.info("  ✅ Rooms and type_rooms indexed successfully!")
        except Exception as e:
            logger.warning(f"  ⚠️  Failed to index rooms/type_rooms: {e}")
            logger.warning("  Continuing with coupons indexing...")
        
        # Index coupons  
        logger.info("\n📊 Indexing coupons...")
        rag.index_coupons_from_database(
            use_chunking=True,
            chunk_size=800,
            recreate_collection=False,
            batch_size=10,
            incremental=True
        )
        
        logger.info("\n✅ RAG data indexed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG indexing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def index_recommendation_data():
    """
    Index data cho Recommendation system
    Sử dụng IndexingService từ src/core/
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("🎯 RECOMMENDATION: Indexing Data for Similar Hotels")
    logger.info("=" * 80)
    
    try:
        # Initialize indexing service
        logger.info("Initializing indexing service...")
        settings = get_settings()
        
        from src.core import EmbeddingService, SparseEmbeddingService, VectorStoreService
        
        embedding_service = EmbeddingService(
            provider="ollama",
            model_name=settings.EMBEDDING_MODEL,
            ollama_url=settings.OLLAMA_URL,
            cache_enabled=settings.EMBEDDING_CACHE_ENABLED
        )
        
        sparse_service = None
        try:
            sparse_service = SparseEmbeddingService(
                model_name="Qdrant/bm25",
                cache_enabled=settings.EMBEDDING_CACHE_ENABLED
            )
        except Exception as e:
            logger.warning(f"Sparse embedding service not available: {e}")
        
        vectorstore_service = VectorStoreService(url=settings.QDRANT_URL)
        
        indexing_service = IndexingService(
            embedding_service=embedding_service,
            sparse_embedding_service=sparse_service,
            vectorstore_service=vectorstore_service
        )
        
        # Index hotels
        result = indexing_service.index_recommendation_hotels(
            collection_name=settings.REC_COLLECTION_HOTELS,
            recreate_collection=False,
            batch_size=10
        )
        
        if result.get('success'):
            logger.info(f"\n✅ Recommendation data indexed successfully!")
            logger.info(f"   Indexed: {result.get('indexed')} hotels")
            logger.info(f"   Skipped: {result.get('skipped')} hotels")
            return True
        else:
            logger.error(f"❌ Recommendation indexing failed: {result.get('error')}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Recommendation indexing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup function"""
    logger.info("=" * 80)
    logger.info("🚀 Unified Hotel System - Collections Setup")
    logger.info("=" * 80)
    
    settings = get_settings()
    
    logger.info(f"Qdrant URL: {settings.QDRANT_URL}")
    logger.info(f"Ollama URL: {settings.OLLAMA_URL}")
    logger.info(f"Embedding Model: {settings.EMBEDDING_MODEL}")
    logger.info("")
    
    try:
        # 1. Initialize vectorstore (only for creating collections)
        logger.info("🔄 Connecting to Qdrant...")
        
        vectorstore_service = VectorStoreService(
            url=settings.QDRANT_URL
        )
        
        logger.info("✅ Connected to Qdrant")
        
        # 2. Create collections
        create_collections(vectorstore_service)
        
        # 3. Check if collections need update (compare DB and Qdrant counts)
        logger.info("\n🔍 Checking collections data and DB for updates...")
        client = vectorstore_service.client
        collections = client.get_collections()
        should_index = False
        # Check hotels collection
        try:
            from sqlalchemy import create_engine, text
            settings = get_settings()
            engine = create_engine(
                f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
                f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
                pool_pre_ping=True
            )
            query = "SELECT COUNT(*) FROM tbl_hotel WHERE hotel_status = 1"
            db_count = engine.execute(text(query)).scalar()
            engine.dispose()
            hotels_collection = None
            settings = get_settings()
            for col in collections.collections:
                if col.name == settings.REC_COLLECTION_HOTELS:
                    hotels_collection = client.get_collection(col.name)
                    break
            qdrant_count = hotels_collection.points_count if hotels_collection else 0
            logger.info(f"  DB hotels: {db_count}, Qdrant hotels: {qdrant_count}")
            if db_count != qdrant_count:
                should_index = True
                logger.info("\n🔄 DB and Qdrant counts differ, will index data...")
        except Exception as e:
            logger.warning(f"Could not compare DB and Qdrant counts: {e}")
            should_index = True
        # Also allow force index by env
        auto_index = os.getenv('AUTO_INDEX_DATA', 'false').lower() == 'true'
        if auto_index:
            should_index = True
            logger.info("\n🔄 AUTO_INDEX_DATA=true, will index data...")
        if should_index:
            # Index RAG data
            rag_success = index_rag_data()
            # Index Recommendation data
            rec_success = index_recommendation_data()
            if not (rag_success and rec_success):
                logger.warning("\n⚠️  Some indexing failed, but collections are ready")
        else:
            logger.info("\n✅ All collections up-to-date, skipping indexing")
            logger.info("\n💡 To re-index manually:")
            logger.info("   - RAG: cd rag/ && python simple_rag_system.py")
            logger.info("   - Recommendation: Use API endpoint POST /api/indexing/recommendation")
            logger.info("   - Or: python setup_collections.py (with AUTO_INDEX_DATA=true)")
        
        # 5. Final Verification
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 Final Verification")
        logger.info("=" * 80)
        
        collections = client.get_collections()
        
        for col in collections.collections:
            info = client.get_collection(col.name)
            logger.info(f"  {col.name}: {info.points_count} points")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("🎉 Setup Complete!")
        logger.info("=" * 80)
        logger.info("\nYou can now run: python app.py")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

