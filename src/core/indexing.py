"""
Indexing Service
Unified indexing service cho cả RAG và Recommendation
Sử dụng unified services từ src/core/
"""

from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from qdrant_client.models import PointStruct, SparseVector
from ..shared import get_logger
from ..config import get_settings, Collections
from .embeddings import EmbeddingService
from .sparse_embeddings import SparseEmbeddingService
from .vectorstore import VectorStoreService

logger = get_logger(__name__)


class IndexingService:
    """
    Unified indexing service
    Handles indexing cho cả RAG và Recommendation systems
    """
    
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        sparse_embedding_service: Optional[SparseEmbeddingService] = None,
        vectorstore_service: Optional[VectorStoreService] = None
    ):
        """
        Initialize indexing service
        
        Args:
            embedding_service: Embedding service instance
            sparse_embedding_service: Sparse embedding service instance (for hybrid search)
            vectorstore_service: Vector store service instance
        """
        settings = get_settings()
        
        self.embedding_service = embedding_service or EmbeddingService(
            provider="ollama",
            model_name=settings.EMBEDDING_MODEL,
            ollama_url=settings.OLLAMA_URL,
            cache_enabled=settings.EMBEDDING_CACHE_ENABLED
        )
        
        self.sparse_embedding_service = sparse_embedding_service
        if self.sparse_embedding_service is None:
            try:
                self.sparse_embedding_service = SparseEmbeddingService(
                    model_name="Qdrant/bm25",
                    cache_enabled=settings.EMBEDDING_CACHE_ENABLED
                )
            except Exception as e:
                logger.warning(f"Sparse embedding service not available: {e}")
                self.sparse_embedding_service = None
        
        self.vectorstore_service = vectorstore_service or VectorStoreService(
            url=settings.QDRANT_URL
        )
        
        # Database connection
        self._db_engine = None
        
        logger.info("✅ IndexingService initialized")
    
    def _get_db_engine(self):
        """Get database engine (lazy initialization)"""
        if self._db_engine is None:
            settings = get_settings()
            self._db_engine = create_engine(
                f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
                f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
                pool_pre_ping=True
            )
        return self._db_engine
    
    def _create_hybrid_point(
        self,
        point_id: int,
        dense_vector: list,
        sparse_vector: Optional[Dict[str, float]],
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
        if sparse_vector and len(sparse_vector) > 0:
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
    
    def index_recommendation_hotels(
        self,
        collection_name: Optional[str] = None,
        recreate_collection: bool = False,
        batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Index hotels for recommendation system với hybrid search
        
        Args:
            collection_name: Collection name (default: REC_COLLECTION_HOTELS)
            recreate_collection: Recreate collection if exists
            batch_size: Batch size for embedding and upload
            
        Returns:
            Dict with indexing results
        """
        settings = get_settings()
        collection_name = collection_name or settings.REC_COLLECTION_HOTELS
        
        logger.info("=" * 80)
        logger.info("🎯 Indexing Hotels for Recommendation (Hybrid Search)")
        logger.info("=" * 80)
        
        try:
            # Fetch hotels from database
            logger.info("Fetching hotels from database...")
            engine = self._get_db_engine()
            query = "SELECT * FROM tbl_hotel WHERE hotel_status = 1"
            hotels_df = pd.read_sql(text(query), engine)
            
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
            for i in range(0, len(hotel_texts), batch_size):
                batch = hotel_texts[i:i + batch_size]
                batch_embeddings = self.embedding_service.embed_documents(batch)
                dense_embeddings.extend(batch_embeddings)
                logger.info(f"Embedded {min(i + batch_size, len(hotel_texts))}/{len(hotel_texts)}")
            
            # Create sparse embeddings (if available)
            sparse_embeddings = []
            if self.sparse_embedding_service and self.sparse_embedding_service.is_available:
                logger.info("\n📊 Creating sparse embeddings (BM25)...")
                sparse_embeddings = self.sparse_embedding_service.embed_documents(
                    hotel_texts, 
                    batch_size=32
                )
                logger.info(f"Created {len(sparse_embeddings)} sparse embeddings")
            else:
                sparse_embeddings = [None] * len(hotel_texts)
                logger.info("Sparse embeddings skipped (service not available)")
            
            # Create points with hybrid vectors
            logger.info("\n📊 Creating points with hybrid vectors...")
            points = []
            for idx, (dense_emb, sparse_emb, metadata) in enumerate(zip(dense_embeddings, sparse_embeddings, hotel_metadata)):
                try:
                    # Convert dense embedding to list
                    dense_list = dense_emb.tolist() if hasattr(dense_emb, 'tolist') else list(dense_emb)
                    
                    # Check for NaN/Inf
                    if not all(np.isfinite(dense_list)):
                        logger.warning(f"Skipping hotel {metadata['hotel_id']}: invalid embedding (NaN/Inf)")
                        continue
                    
                    # Create point with hybrid vectors
                    point = self._create_hybrid_point(
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
                self.vectorstore_service.upsert_points(
                    collection_name=collection_name,
                    points=points,
                    batch_size=batch_size
                )
                logger.info(f"✅ Uploaded {len(points)} points to {collection_name}")
            
            logger.info("\n✅ Recommendation indexing completed successfully!")
            
            return {
                'success': True,
                'collection': collection_name,
                'indexed': len(points),
                'total': len(hotel_texts),
                'skipped': len(hotel_texts) - len(points)
            }
            
        except Exception as e:
            logger.error(f"❌ Recommendation indexing failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'collection': collection_name
            }
    
    def get_indexing_status(self) -> Dict[str, Any]:
        """
        Get status of all collections
        
        Returns:
            Dict with collection statuses
        """
        settings = get_settings()
        client = self.vectorstore_service.client
        
        collections_info = {}
        
        try:
            collections = client.get_collections()
            for col in collections.collections:
                info = client.get_collection(col.name)
                collections_info[col.name] = {
                    'points_count': info.points_count,
                    'vectors_count': info.vectors_count if hasattr(info, 'vectors_count') else 0,
                    'status': 'ready' if info.points_count > 0 else 'empty'
                }
        except Exception as e:
            logger.error(f"Error getting collection status: {e}")
        
        # Get DB counts for comparison
        db_counts = {}
        try:
            engine = self._get_db_engine()
            query = "SELECT COUNT(*) FROM tbl_hotel WHERE hotel_status = 1"
            db_counts['hotels'] = pd.read_sql(text(query), engine).iloc[0, 0]
        except Exception as e:
            logger.warning(f"Could not get DB counts: {e}")
        
        return {
            'collections': collections_info,
            'db_counts': db_counts
        }
