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
                    'hotel_name': row['hotel_name'],
                    'hotel_rank': float(row['hotel_rank']) if row['hotel_rank'] else 0,
                    'hotel_vote': int(row['hotel_vote']) if row['hotel_vote'] else 0,
                    'hotel_place': row['hotel_place'],
                    'hotel_price_average': float(row['hotel_price_average']) if row['hotel_price_average'] else 0,
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
                doc = {
                    'id': f"coupon_{row['coupon_id']}",
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
    
    def auto_sync(
        self,
        sync_hotels: bool = True,
        sync_coupons: bool = True,
        incremental: bool = True
    ) -> bool:
        """
        Auto-sync data from database to vector store
        
        Args:
            sync_hotels: Sync hotels
            sync_coupons: Sync coupons
            incremental: Incremental sync (don't recreate)
            
        Returns:
            True if successful
        """
        logger.info("🔄 Starting auto-sync from database...")
        
        success = True
        
        if sync_hotels:
            hotel_success = self.process_and_index_hotels(
                recreate_collection=not incremental
            )
            success = success and hotel_success
        
        if sync_coupons:
            coupon_success = self.process_and_index_coupons(
                valid_only=True,
                recreate_collection=not incremental
            )
            success = success and coupon_success
        
        if success:
            logger.info("✅ Auto-sync completed successfully")
        else:
            logger.warning("⚠️  Auto-sync completed with errors")
        
        return success

