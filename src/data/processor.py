"""
Data Processor
ETL pipeline and auto-indexing
"""

from typing import Optional, List
import pandas as pd
from .connector import DatabaseConnector
from .normalizer import HotelDataNormalizer
from ..core import RAGService, EmbeddingService, VectorStoreService
from ..shared import get_logger
from ..config import get_settings, Collections

logger = get_logger(__name__)


class DataProcessor:
    """
    Data processor for ETL and auto-indexing
    Connects database -> normalizes -> indexes to vector store
    """
    
    def __init__(
        self,
        db_connector: Optional[DatabaseConnector] = None,
        normalizer: Optional[HotelDataNormalizer] = None,
        rag_service: Optional[RAGService] = None
    ):
        """
        Initialize data processor
        
        Args:
            db_connector: Database connector (creates if None)
            normalizer: Data normalizer (creates if None)
            rag_service: RAG service for indexing (creates if None)
        """
        self.db = db_connector or DatabaseConnector()
        self.normalizer = normalizer or HotelDataNormalizer()
        self.rag = rag_service
        
        logger.info("✅ DataProcessor initialized")
    
    def process_and_index_hotels(
        self,
        hotel_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        recreate_collection: bool = False
    ) -> bool:
        """
        Process hotels from database and index to vector store
        
        Args:
            hotel_ids: Specific hotel IDs to process
            limit: Maximum number of hotels
            recreate_collection: Recreate collection if exists
            
        Returns:
            True if successful
        """
        logger.info("🔄 Processing and indexing hotels...")
        
        try:
            # 1. Fetch from database
            hotels_df = self.db.get_hotels(hotel_ids=hotel_ids, limit=limit)
            
            if hotels_df.empty:
                logger.warning("No hotels fetched from database")
                return False
            
            logger.info(f"📊 Fetched {len(hotels_df)} hotels from database")
            
            # 2. Normalize data
            normalized_df = self.normalizer.normalize_hotels(hotels_df)
            
            # 3. Prepare for indexing
            documents = []
            for idx, row in normalized_df.iterrows():
                doc = {
                    'id': int(row['hotel_id']),
                    'text': row['semantic_text'],
                    'hotel_id': int(row['hotel_id']),
                    'hotel_name': row.get('hotel_name', ''),
                    'hotel_rank': float(row.get('hotel_rank', 0)) if row.get('hotel_rank') else 0,
                    'hotel_view': int(row.get('hotel_view', 0)) if row.get('hotel_view') else 0,
                    'hotel_place': row.get('hotel_placedetails', ''),  # Use placedetails instead
                    'hotel_price_average': float(row.get('hotel_price_average', 0)) if row.get('hotel_price_average') else 0,
                    'document_type': 'hotel'
                }
                documents.append(doc)
            
            # 4. Index to RAG
            if self.rag:
                success = self.rag.index_documents(
                    documents=documents,
                    id_field='id',
                    text_field='text',
                    recreate_collection=recreate_collection
                )
                
                if success:
                    logger.info(f"✅ Indexed {len(documents)} hotels successfully")
                else:
                    logger.error("Failed to index hotels")
                
                return success
            else:
                logger.error("RAG service not initialized")
                return False
            
        except Exception as e:
            logger.error(f"Error processing hotels: {e}")
            return False
    
    def process_and_index_coupons(
        self,
        valid_only: bool = True,
        recreate_collection: bool = False
    ) -> bool:
        """
        Process coupons from database and index
        
        Args:
            valid_only: Only valid coupons
            recreate_collection: Recreate collection
            
        Returns:
            True if successful
        """
        logger.info("🔄 Processing and indexing coupons...")
        
        try:
            # 1. Fetch from database
            coupons_df = self.db.get_coupons(valid_only=valid_only)
            
            if coupons_df.empty:
                logger.warning("No coupons fetched from database")
                return False
            
            logger.info(f"📊 Fetched {len(coupons_df)} coupons from database")
            
            # 2. Normalize
            normalized_df = self.normalizer.normalize_coupons(coupons_df)
            
            # 3. Prepare documents
            documents = []
            for idx, row in normalized_df.iterrows():
                # Use large integer ID to avoid conflict with hotel IDs (hotels: 1-1000, coupons: 1000000+)
                doc = {
                    'id': 1000000 + int(row['coupon_id']),  # Offset to avoid collision with hotel IDs
                    'text': row['semantic_text'],
                    'coupon_id': int(row['coupon_id']),
                    'coupon_code': row.get('coupon_code', ''),
                    'coupon_name': row.get('coupon_name', ''),
                    'document_type': 'coupon'
                }
                documents.append(doc)
            
            # 4. Index
            # Use coupons collection
            if self.rag:
                # Temporarily change collection
                original_collection = self.rag.collection_name
                settings = get_settings()
                self.rag.collection_name = settings.RAG_COLLECTION_COUPONS or Collections.RAG_COUPONS
                
                success = self.rag.index_documents(
                    documents=documents,
                    id_field='id',
                    text_field='text',
                    recreate_collection=recreate_collection
                )
                
                # Restore original collection
                self.rag.collection_name = original_collection
                
                if success:
                    logger.info(f"✅ Indexed {len(documents)} coupons successfully")
                
                return success
            else:
                logger.error("RAG service not initialized")
                return False
            
        except Exception as e:
            logger.error(f"Error processing coupons: {e}")
            return False
    
    def process_and_index_hotels_for_recommendation(
        self,
        hotel_ids: Optional[List[int]] = None,
        limit: Optional[int] = None,
        recreate_collection: bool = False
    ) -> bool:
        """
        Index hotels vào RECOMMENDATION collection (khác với RAG)
        Dùng cho recommendation system, không phải chatbot
        
        Args:
            hotel_ids: Specific hotel IDs
            limit: Max hotels
            recreate_collection: Recreate if exists
            
        Returns:
            True if successful
        """
        logger.info("🎯 Processing and indexing hotels for RECOMMENDATION...")
        
        try:
            from src.core import VectorStoreService, EmbeddingService
            from ..config import get_settings
            
            settings = get_settings()
            
            # 1. Fetch from database
            hotels_df = self.db.get_hotels(hotel_ids=hotel_ids, limit=limit)
            
            if hotels_df.empty:
                logger.warning("No hotels fetched")
                return False
            
            logger.info(f"📊 Fetched {len(hotels_df)} hotels for recommendation")
            
            # 2. Normalize
            normalized_df = self.normalizer.normalize_hotels(hotels_df)
            
            # 3. Prepare for recommendation (same embeddings but different purpose)
            documents = []
            for idx, row in normalized_df.iterrows():
                doc = {
                    'id': int(row['hotel_id']),
                    'text': row['semantic_text'],  # Same text for content-based recommendations
                    'hotel_id': int(row['hotel_id']),
                    'hotel_name': row.get('hotel_name', ''),
                    'hotel_rank': float(row.get('hotel_rank', 0)) if row.get('hotel_rank') else 0,
                    'hotel_price_average': float(row.get('hotel_price_average', 0)) if row.get('hotel_price_average') else 0,
                    'document_type': 'hotel_recommendation'
                }
                documents.append(doc)
            
            # 4. Index vào RECOMMENDATION collection
            if self.rag:
                # Tạm thời switch sang recommendation collection
                original_collection = self.rag.collection_name
                self.rag.collection_name = Collections.RECOMMENDATION_HOTELS
                
                success = self.rag.index_documents(
                    documents=documents,
                    id_field='id',
                    text_field='text',
                    recreate_collection=recreate_collection
                )
                
                # Restore original collection
                self.rag.collection_name = original_collection
                
                if success:
                    logger.info(f"✅ Indexed {len(documents)} hotels to RECOMMENDATION collection")
                
                return success
            else:
                logger.error("RAG service not initialized")
                return False
                
        except Exception as e:
            logger.error(f"Error indexing hotels for recommendation: {e}")
            return False
    
    def auto_sync(
        self,
        sync_hotels: bool = True,
        sync_coupons: bool = True,
        sync_recommendations: bool = True,
        incremental: bool = True
    ) -> bool:
        """
        Auto-sync data from database to vector stores
        Sync vào CẢ RAG và RECOMMENDATION collections
        
        Args:
            sync_hotels: Sync hotels to RAG
            sync_coupons: Sync coupons to RAG
            sync_recommendations: Sync hotels to RECOMMENDATION collection
            incremental: Incremental sync (don't recreate)
            
        Returns:
            True if successful
        """
        logger.info("🔄 Starting auto-sync from database...")
        
        success = True
        
        # Sync hotels to RAG (for chatbot)
        if sync_hotels:
            logger.info("\n🤖 Syncing hotels to RAG collection...")
            hotel_success = self.process_and_index_hotels(
                recreate_collection=not incremental
            )
            success = success and hotel_success
        
        # Sync coupons to RAG (for chatbot)
        if sync_coupons:
            logger.info("\n🎟️  Syncing coupons to RAG collection...")
            coupon_success = self.process_and_index_coupons(
                valid_only=True,
                recreate_collection=not incremental
            )
            success = success and coupon_success
        
        # Sync hotels to RECOMMENDATION collection (for recommendations)
        if sync_recommendations:
            logger.info("\n🎯 Syncing hotels to RECOMMENDATION collection...")
            rec_success = self.process_and_index_hotels_for_recommendation(
                recreate_collection=not incremental
            )
            success = success and rec_success
        
        if success:
            logger.info("\n✅ Auto-sync completed successfully")
        else:
            logger.warning("\n⚠️  Auto-sync completed with errors")
        
        return success


