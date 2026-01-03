#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Collections Script
Tạo collections và index data từ database
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_settings , Collections
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
        (Collections.RECOMMENDATION_SEMANTIC, "Semantic Hotels (Search)", 1024, "🔍"),
    ]
    
    client = vectorstore.client
    
    for collection_name, description, vector_size, emoji in collections_to_create:
        try:
            # Check if exists
            collections = client.get_collections()
            existing_names = [col.name for col in collections.collections]
            
            if collection_name in existing_names:
                info = client.get_collection(collection_name)
                # Check if collection uses named vectors (old hybrid search format)
                vectors_config = info.config.params.vectors
                uses_named_vectors = isinstance(vectors_config, dict)
                
                if uses_named_vectors:
                    logger.warning(f"⚠️  {emoji} {description} ({collection_name}): Uses named vectors (old format)")
                    logger.info(f"   Recreating with dense vectors only...")
                    # Delete and recreate with dense vectors only
                    client.delete_collection(collection_name)
                    client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=vector_size,
                            distance=Distance.COSINE
                        )
                    )
                    logger.info(f"✅ {emoji} {description} ({collection_name}): Recreated with dense vectors")
                else:
                    logger.info(f"✅ {emoji} {description} ({collection_name}): {info.points_count} points (dense vectors)")
            else:
                # Create collection with dense vectors only
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ {emoji} {description} ({collection_name}): Created (dense vectors)")
                
        except Exception as e:
            logger.error(f"❌ Error creating {collection_name}: {e}")


def index_rag_data():
    """
    Index data cho RAG system (chatbot)
    Sử dụng IndexingService từ src/core/ (Single Responsibility Principle)
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("🤖 RAG: Indexing Data for Chatbot")
    logger.info("=" * 80)
    
    try:
        # Initialize IndexingService
        logger.info("Initializing IndexingService...")
        settings = get_settings()
        
        from src.core import EmbeddingService, VectorStoreService, IndexingService
        
        # Create IndexingService (no sparse vectors)
        indexing_service = IndexingService(
            embedding_service=EmbeddingService(
                provider="ollama",
                model_name=settings.EMBEDDING_MODEL,
                ollama_url=settings.OLLAMA_URL,
                cache_enabled=settings.EMBEDDING_CACHE_ENABLED
            ),
            sparse_embedding_service=None,  # No sparse vectors
            vectorstore_service=VectorStoreService(url=settings.QDRANT_URL)
        )
        
        # Index hotels (with chunking)
        logger.info("\n📊 Indexing hotels...")
        hotels_result = indexing_service.index_rag_hotels(
            collection_name=settings.RAG_COLLECTION_HOTELS,
            batch_size=32
        )
        if not hotels_result.get('success'):
            logger.warning(f"  ⚠️  Hotels indexing failed: {hotels_result.get('error')}")
        else:
            logger.info(f"  ✅ Indexed {hotels_result.get('indexed', 0)} hotel chunks")
        
        # Index rooms and type_rooms (cùng collection với hotels)
        logger.info("\n📊 Indexing rooms and type_rooms...")
        rooms_result = indexing_service.index_rag_rooms(
            collection_name=settings.RAG_COLLECTION_HOTELS,
            batch_size=50
        )
        if not rooms_result.get('success'):
            logger.warning(f"  ⚠️  Rooms indexing failed: {rooms_result.get('error')}")
        
        type_rooms_result = indexing_service.index_rag_type_rooms(
            collection_name=settings.RAG_COLLECTION_HOTELS,
            batch_size=50
        )
        if not type_rooms_result.get('success'):
            logger.warning(f"  ⚠️  Type rooms indexing failed: {type_rooms_result.get('error')}")
        
        if rooms_result.get('success') and type_rooms_result.get('success'):
            logger.info("  ✅ Rooms and type_rooms indexed successfully!")
            logger.info(f"     - Rooms: {rooms_result.get('indexed', 0)} indexed")
            logger.info(f"     - Type Rooms: {type_rooms_result.get('indexed', 0)} indexed")
        
        # Index coupons (with chunking)
        logger.info("\n📊 Indexing coupons...")
        coupons_result = indexing_service.index_rag_coupons(
            collection_name=settings.RAG_COLLECTION_COUPONS,
            batch_size=32
        )
        if not coupons_result.get('success'):
            logger.warning(f"  ⚠️  Coupons indexing failed: {coupons_result.get('error')}")
        else:
            logger.info(f"  ✅ Indexed {coupons_result.get('indexed', 0)} coupon chunks")
        
        # Check overall success
        all_success = (
            hotels_result.get('success', False) and
            rooms_result.get('success', False) and
            type_rooms_result.get('success', False) and
            coupons_result.get('success', False)
        )
        
        if all_success:
            logger.info("\n✅ RAG data indexed successfully!")
            return True
        else:
            logger.warning("\n⚠️  Some indexing failed, but continuing...")
            return False
        
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
        
        from src.core import EmbeddingService, VectorStoreService
        
        embedding_service = EmbeddingService(
            provider="ollama",
            model_name=settings.EMBEDDING_MODEL,
            ollama_url=settings.OLLAMA_URL,
            cache_enabled=settings.EMBEDDING_CACHE_ENABLED
        )
        
        vectorstore_service = VectorStoreService(url=settings.QDRANT_URL)
        
        indexing_service = IndexingService(
            embedding_service=embedding_service,
            sparse_embedding_service=None,  # No sparse vectors
            vectorstore_service=vectorstore_service
        )
        
        # Index hotels
        result = indexing_service.index_recommendation_hotels(
            collection_name=settings.REC_COLLECTION_HOTELS,
            recreate_collection=False,
            batch_size=5  # Reduced batch size to avoid JSON size issues
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


def index_semantic_data():
    """
    Index data cho Semantic Search system
    Sử dụng IndexingService từ src/core/
    Tương tự như recommendation nhưng cho collection semantic
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("🔍 SEMANTIC: Indexing Data for Semantic Search")
    logger.info("=" * 80)
    
    try:
        # Initialize indexing service
        logger.info("Initializing indexing service...")
        settings = get_settings()
        
        from src.core import EmbeddingService, VectorStoreService
        
        embedding_service = EmbeddingService(
            provider="ollama",
            model_name=settings.EMBEDDING_MODEL,
            ollama_url=settings.OLLAMA_URL,
            cache_enabled=settings.EMBEDDING_CACHE_ENABLED
        )
        
        vectorstore_service = VectorStoreService(url=settings.QDRANT_URL)
        
        indexing_service = IndexingService(
            embedding_service=embedding_service,
            sparse_embedding_service=None,  # No sparse vectors
            vectorstore_service=vectorstore_service
        )
        
        # Index hotels vào semantic collection
        result = indexing_service.index_recommendation_hotels(
            collection_name=settings.REC_COLLECTION_SEMANTIC,
            recreate_collection=False,
            batch_size=10
        )
        
        if result.get('success'):
            logger.info(f"\n✅ Semantic data indexed successfully!")
            logger.info(f"   Indexed: {result.get('indexed')} hotels")
            logger.info(f"   Skipped: {result.get('skipped')} hotels")
            return True
        else:
            logger.error(f"❌ Semantic indexing failed: {result.get('error')}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Semantic indexing failed: {e}")
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
            # Index Semantic data
            semantic_success = index_semantic_data()
            if not (rag_success and rec_success and semantic_success):
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

