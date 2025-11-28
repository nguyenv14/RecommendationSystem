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
from src.core import VectorStoreService
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
                # Create collection
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ {emoji} {description} ({collection_name}): Created")
                
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
        rag = SimpleRAGSystem(
            collection_name="hotels_rag",
            qdrant_url="http://localhost:6333",
            ollama_url="http://localhost:11434",
            embedding_model="bge-m3",
            llm_model="qwen3"
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
    Logic từ recommendation/semantic_recommendation_system.py
    """
    logger.info("")
    logger.info("=" * 80)
    logger.info("🎯 RECOMMENDATION: Indexing Data for Similar Hotels")
    logger.info("=" * 80)
    
    try:
        # Import recommendation system
        sys.path.insert(0, str(Path(__file__).parent / 'recommendation'))
        from semantic_recommendation_system import SemanticRecommendationSystem
        import pymysql
        import pandas as pd
        import numpy as np
        from qdrant_client.models import PointStruct
        
        # Initialize recommendation system
        logger.info("Initializing recommendation system...")
        rec_system = SemanticRecommendationSystem(
            model_name='paraphrase-multilingual-MiniLM-L12-v2',
            qdrant_url="http://localhost:6333",
            use_ollama=True,
            ollama_url="http://localhost:11434"
        )
        rec_system.collection_name = "hotels_recommendation"
        
        # Fetch hotels from database
        logger.info("Fetching hotels from database...")
        connection = pymysql.connect(
            host='localhost',
            port=3308,
            user='root',
            password='root',
            database='myhotel'
        )
        
        query = "SELECT * FROM tbl_hotel WHERE hotel_status = 1"
        hotels_df = pd.read_sql(query, connection)
        connection.close()
        
        logger.info(f"Fetched {len(hotels_df)} hotels")
        
        # Clean dataframe
        logger.info("\n📊 Cleaning data...")
        hotels_df = hotels_df.fillna({
            'hotel_name': '',
            'hotel_desc': '',
            'hotel_placedetails': '',
            'hotel_tag_keyword': '',
            'hotel_rank': 0,
            'hotel_price_average': 0
        })
        
        # Prepare hotel texts
        hotel_texts = []
        hotel_metadata = []
        
        for idx, hotel in hotels_df.iterrows():
            hotel_id = hotel['hotel_id']
            
            # Combine description
            description_parts = []
            if pd.notna(hotel.get('hotel_name')) and str(hotel.get('hotel_name')).strip():
                description_parts.append(f"Tên: {hotel['hotel_name']}")
            if pd.notna(hotel.get('hotel_desc')) and str(hotel.get('hotel_desc')).strip():
                description_parts.append(str(hotel['hotel_desc'])[:500])  # Limit length
            if pd.notna(hotel.get('hotel_placedetails')) and str(hotel.get('hotel_placedetails')).strip():
                description_parts.append(f"Địa chỉ: {hotel['hotel_placedetails']}")
            
            full_description = ' '.join(description_parts)
            
            # Skip if no description
            if not full_description or len(full_description.strip()) < 10:
                logger.warning(f"Skipping hotel {hotel_id}: no valid description")
                continue
            
            # Limit description length
            if len(full_description) > 512:
                full_description = full_description[:512]
            
            hotel_texts.append(full_description)
            hotel_metadata.append({
                'hotel_id': int(hotel_id),
                'hotel_name': str(hotel.get('hotel_name', f'Hotel {hotel_id}')),
                'hotel_rank': float(hotel.get('hotel_rank', 0)),
                'hotel_price_average': float(hotel.get('hotel_price_average', 0))
            })
        
        logger.info(f"Prepared {len(hotel_texts)} hotels for indexing")
        
        # Create embeddings
        logger.info("\n📊 Creating embeddings...")
        embeddings = rec_system.create_embeddings(hotel_texts)
        
        # Validate embeddings
        valid_points = []
        for idx, (embedding, metadata) in enumerate(zip(embeddings, hotel_metadata)):
            try:
                # Convert to list
                embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
                
                # Check for NaN/Inf
                if not all(np.isfinite(embedding_list)):
                    logger.warning(f"Skipping hotel {metadata['hotel_id']}: invalid embedding (NaN/Inf)")
                    continue
                
                # Create point
                point = PointStruct(
                    id=metadata['hotel_id'],
                    vector=embedding_list,
                    payload=metadata
                )
                valid_points.append(point)
                
            except Exception as e:
                logger.warning(f"Skipping hotel {metadata['hotel_id']}: {e}")
                continue
        
        logger.info(f"Valid points: {len(valid_points)}")
        
        # Upload to Qdrant in batches
        if valid_points:
            logger.info("\n📊 Uploading to Qdrant...")
            batch_size = 10
            for i in range(0, len(valid_points), batch_size):
                batch = valid_points[i:i+batch_size]
                rec_system.client.upsert(
                    collection_name=rec_system.collection_name,
                    points=batch
                )
                logger.info(f"Uploaded batch {i//batch_size + 1}/{(len(valid_points)-1)//batch_size + 1}")
        
        logger.info("\n✅ Recommendation data indexed successfully!")
        return True
        
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
        
        # 3. Index data (ONLY if enabled)
        auto_index = os.getenv('AUTO_INDEX_DATA', 'false').lower() == 'true'
        
        if auto_index:
            logger.info("\n🔄 AUTO_INDEX_DATA=true, indexing data...")
            
            # Index RAG data
            rag_success = index_rag_data()
            
            # Index Recommendation data
            rec_success = index_recommendation_data()
            
            if not (rag_success and rec_success):
                logger.warning("\n⚠️  Some indexing failed, but collections are ready")
        else:
            logger.info("\n⏭️  Skipping data indexing (set AUTO_INDEX_DATA=true to enable)")
            logger.info("   To index manually:")
            logger.info("   - RAG: cd rag/ && python simple_rag_system.py")
            logger.info("   - Recommendation: cd recommendation/ && python semantic_recommendation_system.py")
        
        # 4. Verify
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 Final Verification")
        logger.info("=" * 80)
        
        client = vectorstore_service.client
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

