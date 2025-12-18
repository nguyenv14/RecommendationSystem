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
        
        self.settings = settings  # Cache settings để tránh gọi get_settings() nhiều lần
        
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
            settings = self.settings  # Use cached settings
            self._db_engine = create_engine(
                f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
                f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}",
                pool_pre_ping=True,
                pool_size=5,  # Limit pool size
                max_overflow=10  # Max overflow connections
            )
        return self._db_engine
    
    def cleanup(self):
        """Cleanup resources (dispose database engine)"""
        if self._db_engine:
            self._db_engine.dispose()
            self._db_engine = None
            logger.info("Database engine disposed")
    
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
        collection_name = collection_name or self.settings.REC_COLLECTION_HOTELS
        
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
            total_batches = (len(hotel_texts) + batch_size - 1) // batch_size
            for i in range(0, len(hotel_texts), batch_size):
                batch = hotel_texts[i:i + batch_size]
                batch_embeddings = self.embedding_service.embed_documents(batch)
                dense_embeddings.extend(batch_embeddings)
                # Chỉ log mỗi 10 batches hoặc batch cuối để giảm log noise
                batch_num = i // batch_size + 1
                if batch_num % 10 == 0 or batch_num == total_batches:
                    logger.info(f"Embedded {min(i + batch_size, len(hotel_texts))}/{len(hotel_texts)} ({batch_num}/{total_batches} batches)")
                else:
                    logger.debug(f"Embedded batch {batch_num}/{total_batches}")
            
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
            query = "SELECT COUNT(*) as count FROM tbl_hotel WHERE hotel_status = 1"
            result = pd.read_sql(text(query), engine)
            db_counts['hotels'] = int(result.iloc[0]['count']) if not result.empty else 0
        except Exception as e:
            logger.warning(f"Could not get DB counts: {e}")
        
        return {
            'collections': collections_info,
            'db_counts': db_counts
        }
    
    def index_rag_rooms(
        self,
        collection_name: Optional[str] = None,
        rag_service: Optional[Any] = None,  # RAGService instance
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Index rooms for RAG system (chatbot)
        
        Args:
            collection_name: Collection name (default: RAG_COLLECTION_HOTELS)
            rag_service: Optional RAGService instance (if None, will create documents manually)
            batch_size: Batch size for processing
            
        Returns:
            Dict with indexing results
        """
        collection_name = collection_name or self.settings.RAG_COLLECTION_HOTELS
        
        logger.info("=" * 80)
        logger.info("🔄 Indexing Rooms for RAG System")
        logger.info("=" * 80)
        
        try:
            # Import data modules (from rag/data/)
            import sys
            from pathlib import Path
            rag_data_path = Path(__file__).parent.parent.parent / 'rag' / 'data'
            if str(rag_data_path) not in sys.path:
                sys.path.insert(0, str(rag_data_path.parent))
            
            from data.connector import DatabaseConnector
            from data.normalizer import HotelDataNormalizer
            
            # Initialize database connector and normalizer
            db_connector = DatabaseConnector()
            normalizer = HotelDataNormalizer()
            
            # Fetch rooms from database
            logger.info("Fetching rooms from database...")
            rooms_df = db_connector.get_rooms_enriched()
            
            if rooms_df.empty:
                logger.warning("No rooms found in database")
                return {
                    'success': False,
                    'error': 'No rooms found',
                    'collection': collection_name
                }
            
            logger.info(f"Fetched {len(rooms_df)} rooms")
            
            # Normalize rooms
            logger.info("Normalizing rooms data...")
            normalized_df = normalizer.normalize_rooms(rooms_df)
            
            # Convert to documents format
            documents = []
            for _, row in normalized_df.iterrows():
                doc = {
                    'id': f"room_{int(row['room_id'])}_{int(row.get('type_room_id', 0))}",  # Unique ID
                    'text': row['semantic_text'],
                    'page_content': row['semantic_text'],  # For compatibility
                    'document_type': 'room',
                    'hotel_id': int(row['hotel_id']),
                    'hotel_name': str(row.get('hotel_name', '')),
                    'room_id': int(row['room_id']),
                    'type_room_id': int(row.get('type_room_id', 0)),
                    'price': float(row.get('search_price', 0)),
                    'type_name': str(row.get('room_name', ''))
                }
                documents.append(doc)
            
            logger.info(f"Prepared {len(documents)} room documents")
            
            # Index using RAGService if provided, otherwise use direct indexing
            if rag_service and hasattr(rag_service, 'index_documents'):
                logger.info("Indexing using RAGService...")
                success = rag_service.index_documents(
                    documents=documents,
                    id_field='id',
                    text_field='text',
                    metadata_fields=['document_type', 'hotel_id', 'hotel_name', 'room_id', 'type_room_id', 'price', 'type_name'],
                    recreate_collection=False
                )
            else:
                # Direct indexing using embedding and vectorstore services
                logger.info("Indexing directly using embedding service...")
                success = self._index_documents_direct(
                    documents=documents,
                    collection_name=collection_name,
                    text_field='text',
                    batch_size=batch_size
                )
            
            if success:
                logger.info(f"✅ Indexed {len(documents)} rooms successfully")
                return {
                    'success': True,
                    'collection': collection_name,
                    'indexed': len(documents),
                    'document_type': 'room'
                }
            else:
                return {
                    'success': False,
                    'error': 'Indexing failed',
                    'collection': collection_name
                }
                
        except Exception as e:
            logger.error(f"❌ Room indexing failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'collection': collection_name
            }
    
    def index_rag_type_rooms(
        self,
        collection_name: Optional[str] = None,
        rag_service: Optional[Any] = None,  # RAGService instance
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Index type_rooms for RAG system (chatbot)
        
        Args:
            collection_name: Collection name (default: RAG_COLLECTION_HOTELS)
            rag_service: Optional RAGService instance
            batch_size: Batch size for processing
            
        Returns:
            Dict with indexing results
        """
        collection_name = collection_name or self.settings.RAG_COLLECTION_HOTELS
        
        logger.info("=" * 80)
        logger.info("🔄 Indexing Type Rooms for RAG System")
        logger.info("=" * 80)
        
        try:
            # Import data modules
            import sys
            from pathlib import Path
            rag_data_path = Path(__file__).parent.parent.parent / 'rag' / 'data'
            if str(rag_data_path) not in sys.path:
                sys.path.insert(0, str(rag_data_path.parent))
            
            from data.connector import DatabaseConnector
            from data.normalizer import HotelDataNormalizer
            
            # Initialize
            db_connector = DatabaseConnector()
            normalizer = HotelDataNormalizer()
            
            # Fetch type_rooms
            logger.info("Fetching type_rooms from database...")
            type_rooms_df = db_connector.get_type_rooms_enriched()
            
            if type_rooms_df.empty:
                logger.warning("No type_rooms found in database")
                return {
                    'success': False,
                    'error': 'No type_rooms found',
                    'collection': collection_name
                }
            
            logger.info(f"Fetched {len(type_rooms_df)} type_rooms")
            
            # Normalize
            logger.info("Normalizing type_rooms data...")
            normalized_df = normalizer.normalize_type_rooms(type_rooms_df)
            
            # Convert to documents
            documents = []
            for _, row in normalized_df.iterrows():
                # Parse hotel_ids string to list
                hotel_ids_str = str(row.get('hotel_ids', ''))
                hotel_ids_list = []
                if hotel_ids_str and hotel_ids_str != 'nan':
                    try:
                        hotel_ids_list = [int(hid) for hid in hotel_ids_str.split(',') if hid.strip().isdigit()]
                    except:
                        hotel_ids_list = []
                
                doc = {
                    'id': f"type_room_{int(row['type_room_id'])}",
                    'text': row['semantic_text'],
                    'page_content': row['semantic_text'],
                    'document_type': 'type_room',
                    'type_room_id': int(row['type_room_id']),
                    'type_room_name': str(row.get('type_room_name', '')),
                    'hotel_ids': hotel_ids_list,
                    'hotel_names': str(row.get('hotel_names', '')),
                    'min_price': float(row.get('search_min_price', 0)),
                    'max_price': float(row.get('search_max_price', 0)),
                    'avg_price': float(row.get('search_avg_price', 0)),
                    'room_count': int(row.get('room_count', 0))
                }
                documents.append(doc)
            
            logger.info(f"Prepared {len(documents)} type_room documents")
            
            # Index
            if rag_service and hasattr(rag_service, 'index_documents'):
                logger.info("Indexing using RAGService...")
                success = rag_service.index_documents(
                    documents=documents,
                    id_field='id',
                    text_field='text',
                    metadata_fields=['document_type', 'type_room_id', 'type_room_name', 'hotel_ids', 'hotel_names', 'min_price', 'max_price', 'avg_price', 'room_count'],
                    recreate_collection=False
                )
            else:
                logger.info("Indexing directly using embedding service...")
                success = self._index_documents_direct(
                    documents=documents,
                    collection_name=collection_name,
                    text_field='text',
                    batch_size=batch_size
                )
            
            if success:
                logger.info(f"✅ Indexed {len(documents)} type_rooms successfully")
                return {
                    'success': True,
                    'collection': collection_name,
                    'indexed': len(documents),
                    'document_type': 'type_room'
                }
            else:
                return {
                    'success': False,
                    'error': 'Indexing failed',
                    'collection': collection_name
                }
                
        except Exception as e:
            logger.error(f"❌ Type room indexing failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'collection': collection_name
            }
    
    def _index_documents_direct(
        self,
        documents: List[Dict[str, Any]],
        collection_name: str,
        text_field: str = 'text',
        batch_size: int = 32
    ) -> bool:
        """
        Index documents directly using embedding and vectorstore services
        (Helper method for when RAGService is not available)
        
        Args:
            documents: List of document dicts
            collection_name: Collection name
            text_field: Field name containing text to embed
            batch_size: Batch size for embedding
            
        Returns:
            True if successful
        """
        try:
            from qdrant_client.models import PointStruct
            
            # Extract texts
            texts = [doc.get(text_field, '') for doc in documents]
            valid_docs = [(doc, text) for doc, text in zip(documents, texts) if text and doc.get('id')]
            
            if not valid_docs:
                logger.warning("No valid documents to index")
                return False
            
            # Batch embed
            texts_to_embed = [text for _, text in valid_docs]
            logger.info(f"Embedding {len(texts_to_embed)} documents...")
            vectors = self.embedding_service.embed_documents(texts_to_embed, batch_size=batch_size)
            
            # Create points
            points = []
            for (doc, text), vector in zip(valid_docs, vectors):
                try:
                    # Convert to list
                    vector_list = vector.tolist() if hasattr(vector, 'tolist') else list(vector)
                    
                    # Prepare payload (all fields except 'id')
                    payload = {k: v for k, v in doc.items() if k != 'id'}
                    payload[text_field] = text  # Ensure text field is in payload
                    
                    # Create point ID
                    point_id = doc['id']
                    # If ID is string like "room_123_456", extract numeric parts
                    if isinstance(point_id, str):
                        if point_id.startswith('room_'):
                            # Format: room_{room_id}_{type_room_id}
                            parts = point_id.split('_')
                            if len(parts) >= 3:
                                try:
                                    # Combine room_id and type_room_id into unique int
                                    room_id = int(parts[1])
                                    type_id = int(parts[2]) if len(parts) > 2 else 0
                                    point_id = room_id * 1000000 + type_id  # room_id * 1M + type_id
                                except ValueError:
                                    # Fallback to hash
                                    import hashlib
                                    point_id = int(hashlib.md5(point_id.encode()).hexdigest()[:8], 16)
                        elif point_id.startswith('type_room_'):
                            # Format: type_room_{type_room_id}
                            parts = point_id.split('_')
                            if len(parts) >= 3:
                                try:
                                    point_id = int(parts[2]) + 1000000000  # Offset to avoid collision with rooms
                                except ValueError:
                                    import hashlib
                                    point_id = int(hashlib.md5(point_id.encode()).hexdigest()[:8], 16)
                        else:
                            # Other string IDs - use hash
                            import hashlib
                            point_id = int(hashlib.md5(point_id.encode()).hexdigest()[:8], 16)
                    
                    point = PointStruct(
                        id=point_id,
                        vector=vector_list,
                        payload=payload
                    )
                    points.append(point)
                except Exception as e:
                    logger.warning(f"Skipping document {doc.get('id')}: {e}")
                    continue
            
            # Upsert points
            if points:
                logger.info(f"Uploading {len(points)} points to {collection_name}...")
                self.vectorstore_service.upsert_points(
                    collection_name=collection_name,
                    points=points,
                    batch_size=batch_size
                )
                logger.info(f"✅ Uploaded {len(points)} points")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in direct indexing: {e}")
            return False
