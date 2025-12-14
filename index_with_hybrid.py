#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Index Data with Hybrid Search Support
Index data với cả dense và sparse vectors cho hybrid search
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_settings, Collections
from src.shared import get_logger, setup_logging
from src.core import (
    EmbeddingService,
    SparseEmbeddingService,
    VectorStoreService
)
from qdrant_client.models import PointStruct, SparseVector
import pandas as pd
from sqlalchemy import create_engine, text

# Setup logging
setup_logging()
logger = get_logger(__name__)


def create_hybrid_point(
    point_id: int,
    dense_vector: list,
    sparse_vector: dict,
    payload: dict
) -> PointStruct:
    """
    Create PointStruct with both dense and sparse vectors
    
    Args:
        point_id: Point ID
        dense_vector: Dense embedding vector
        sparse_vector: Sparse embedding dict (BM25) - {token_index: weight}
        payload: Point payload
        
    Returns:
        PointStruct with hybrid vectors
    """
    # Convert sparse vector dict to SparseVector format
    if sparse_vector and len(sparse_vector) > 0:
        # SparseVector expects indices (list of int) and values (list of float)
        # sparse_vector dict format: {str(token_index): float(weight)}
        indices = []
        values = []
        for token_idx_str, weight in sparse_vector.items():
            try:
                indices.append(int(token_idx_str))
                values.append(float(weight))
            except (ValueError, TypeError):
                continue
        
        if indices and values:
            sparse_vec = SparseVector(indices=indices, values=values)
            
            return PointStruct(
                id=point_id,
                vector={
                    "dense": dense_vector,
                    "sparse": sparse_vec
                },
                payload=payload
            )
    
    # Fallback to dense only
    return PointStruct(
        id=point_id,
        vector=dense_vector,
        payload=payload
    )


def index_recommendation_hotels_with_hybrid():
    """
    Index hotels for recommendation với hybrid search (dense + sparse)
    """
    logger.info("=" * 80)
    logger.info("🎯 Indexing Hotels with Hybrid Search")
    logger.info("=" * 80)
    
    settings = get_settings()
    
    try:
        # Initialize services
        logger.info("Initializing services...")
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
            logger.info("✅ Sparse embedding service initialized")
        except Exception as e:
            logger.warning(f"⚠️  Sparse embedding service failed: {e}")
            logger.warning("   Will index with dense vectors only")
        
        vectorstore = VectorStoreService(url=settings.QDRANT_URL)
        
        # Fetch hotels from database
        logger.info("Fetching hotels from database...")
        engine = create_engine(
            f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
            f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
            pool_pre_ping=True
        )
        
        query = "SELECT * FROM tbl_hotel WHERE hotel_status = 1"
        hotels_df = pd.read_sql(text(query), engine)
        engine.dispose()
        
        logger.info(f"Fetched {len(hotels_df)} hotels")
        
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
                description_parts.append(str(hotel['hotel_desc'])[:500])
            if pd.notna(hotel.get('hotel_placedetails')) and str(hotel.get('hotel_placedetails')).strip():
                description_parts.append(f"Địa chỉ: {hotel['hotel_placedetails']}")
            
            full_description = ' '.join(description_parts)
            
            if not full_description or len(full_description.strip()) < 10:
                logger.warning(f"Skipping hotel {hotel_id}: no valid description")
                continue
            
            if len(full_description) > 512:
                full_description = full_description[:512]
            
            hotel_texts.append(full_description)
            hotel_metadata.append({
                'hotel_id': int(hotel_id),
                'hotel_name': str(hotel.get('hotel_name', f'Hotel {hotel_id}')),
                'hotel_rank': float(hotel.get('hotel_rank', 0)),
                'hotel_price_average': float(hotel.get('hotel_price_average', 0)),
                'area_id': int(hotel.get('area_id', 0)) if pd.notna(hotel.get('area_id')) else 0
            })
        
        logger.info(f"Prepared {len(hotel_texts)} hotels for indexing")
        
        # Create dense embeddings
        logger.info("\n📊 Creating dense embeddings...")
        dense_embeddings = []
        batch_size = 10
        for i in range(0, len(hotel_texts), batch_size):
            batch = hotel_texts[i:i + batch_size]
            batch_embeddings = embedding_service.embed_documents(batch)
            dense_embeddings.extend(batch_embeddings)
            logger.info(f"Embedded {min(i + batch_size, len(hotel_texts))}/{len(hotel_texts)}")
        
        # Create sparse embeddings
        sparse_embeddings = []
        if sparse_service:
            logger.info("\n📊 Creating sparse embeddings (BM25)...")
            sparse_embeddings = sparse_service.embed_documents(hotel_texts, batch_size=32)
            logger.info(f"Created {len(sparse_embeddings)} sparse embeddings")
        else:
            sparse_embeddings = [None] * len(hotel_texts)
        
        # Create points with hybrid vectors
        logger.info("\n📊 Creating points with hybrid vectors...")
        points = []
        for idx, (dense_emb, sparse_emb, metadata) in enumerate(zip(dense_embeddings, sparse_embeddings, hotel_metadata)):
            try:
                # Convert dense embedding to list
                dense_list = dense_emb.tolist() if hasattr(dense_emb, 'tolist') else list(dense_emb)
                
                # Create point with hybrid vectors
                point = create_hybrid_point(
                    point_id=metadata['hotel_id'],
                    dense_vector=dense_list,
                    sparse_vector=sparse_emb if sparse_emb else None,
                    payload=metadata
                )
                points.append(point)
                
            except Exception as e:
                logger.warning(f"Skipping hotel {metadata['hotel_id']}: {e}")
                continue
        
        logger.info(f"Created {len(points)} points")
        
        # Upload to Qdrant
        if points:
            logger.info("\n📊 Uploading to Qdrant...")
            collection_name = settings.REC_COLLECTION_HOTELS
            vectorstore.upsert_points(
                collection_name=collection_name,
                points=points,
                batch_size=10
            )
            logger.info(f"✅ Uploaded {len(points)} points to {collection_name}")
        
        logger.info("\n✅ Indexing completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Indexing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🚀 Hybrid Search Indexing")
    logger.info("=" * 80)
    
    success = index_recommendation_hotels_with_hybrid()
    
    if success:
        logger.info("\n✅ All done!")
    else:
        logger.error("\n❌ Indexing failed!")
        sys.exit(1)

