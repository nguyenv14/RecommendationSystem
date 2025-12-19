#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Processor Module
ETL pipeline và auto-indexing cho Room và Type Room data
"""

import logging
from typing import Optional, List
import pandas as pd
from langchain.schema import Document

from .connector import DatabaseConnector
from .normalizer import HotelDataNormalizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Data processor cho ETL và auto-indexing
    Connects database -> normalizes -> indexes to vector store
    """
    
    def __init__(self,
                 db_connector: Optional[DatabaseConnector] = None,
                 normalizer: Optional[HotelDataNormalizer] = None,
                 rag=None):
        """
        Initialize data processor
        
        Args:
            db_connector: Database connector (creates if None)
            normalizer: Data normalizer (creates if None) 
            rag: RAG service for indexing (SimpleRAGSystem instance)
        """
        self.db = db_connector or DatabaseConnector()
        self.normalizer = normalizer or HotelDataNormalizer()
        self.rag = rag
        
        logger.info("✅ DataProcessor initialized")
    
    def process_and_index_rooms(self, 
                               recreate_collection: bool = False,
                               batch_size: int = 100) -> bool:
        """
        ETL Pipeline cho Room Data
        
        Args:
            recreate_collection: If True, recreate collection (will delete all data)
            batch_size: Number of documents per batch
            
        Returns:
            True if successful
        """
        logger.info("🔄 Processing and indexing ROOMS...")
        try:
            # 1. Fetch
            rooms_df = self.db.get_rooms_enriched()
            if rooms_df.empty:
                logger.warning("No rooms found in DB")
                return False
                
            logger.info(f"📊 Extracted {len(rooms_df)} rooms. Normalizing...")
            
            # 2. Normalize
            normalized_df = self.normalizer.normalize_rooms(rooms_df)
            
            # 3. Convert to Documents format
            documents = []
            
            for _, row in normalized_df.iterrows():
                doc = Document(
                    page_content=row['semantic_text'],
                    metadata={
                        'document_type': 'room',
                        'hotel_id': int(row['hotel_id']),  # Key để filter theo khách sạn
                        'hotel_name': row['hotel_name'],
                        'room_id': int(row['room_id']),
                        'type_room_id': int(row.get('type_room_id', 0)),
                        'price': float(row['search_price']),
                        'type_name': row.get('room_name', '')  # Use room_name instead of type_room_name
                    }
                )
                documents.append(doc)
            
            # 4. Indexing
            if self.rag:
                # Use SimpleRAGSystem's _store_documents_in_qdrant method
                # Có thể dùng chung collection 'rag_collection' hoặc tạo mới 'rag_rooms'
                # Recommendation: Dùng chung để search 1 lần ra cả khách sạn lẫn phòng
                try:
                    # Store documents using SimpleRAGSystem's internal method
                    self.rag._store_documents_in_qdrant(
                        documents=documents,
                        recreate_collection=False,  # Luôn là False nếu index chung
                        batch_size=batch_size,
                        use_upsert=True  # Use upsert for incremental updates
                    )
                    logger.info(f"✅ Indexed {len(documents)} rooms successfully")
                    return True
                except Exception as e:
                    logger.error(f"❌ Error indexing rooms: {e}")
                    return False
            else:
                logger.warning("⚠️  RAG service not initialized - skipping indexing")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing rooms: {e}")
            return False
    
    def process_and_index_type_rooms(self, 
                                     recreate_collection: bool = False,
                                     batch_size: int = 100) -> bool:
        """
        ETL Pipeline cho Type Room Data
        
        Args:
            recreate_collection: If True, recreate collection (will delete all data)
            batch_size: Number of documents per batch
            
        Returns:
            True if successful
        """
        logger.info("🔄 Processing and indexing TYPE ROOMS...")
        try:
            # 1. Fetch
            type_rooms_df = self.db.get_type_rooms_enriched()
            if type_rooms_df.empty:
                logger.warning("No type rooms found in DB")
                return False
                
            logger.info(f"📊 Extracted {len(type_rooms_df)} type rooms. Normalizing...")
            
            # 2. Normalize
            normalized_df = self.normalizer.normalize_type_rooms(type_rooms_df)
            
            # 3. Convert to Documents format
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
                
                doc = Document(
                    page_content=row['semantic_text'],
                    metadata={
                        'document_type': 'type_room',
                        'type_room_id': int(row['type_room_id']),
                        'type_room_name': row['type_room_name'],
                        'hotel_ids': hotel_ids_list,  # List of hotel IDs using this type
                        'hotel_names': str(row.get('hotel_names', '')),
                        'min_price': float(row.get('search_min_price', 0)),
                        'max_price': float(row.get('search_max_price', 0)),
                        'avg_price': float(row.get('search_avg_price', 0)),
                        'room_count': int(row.get('room_count', 0))
                    }
                )
                documents.append(doc)
            
            # 4. Indexing
            if self.rag:
                # Use SimpleRAGSystem's _store_documents_in_qdrant method
                # Có thể dùng chung collection 'rag_collection' hoặc tạo mới 'rag_type_rooms'
                # Recommendation: Dùng chung để search 1 lần ra cả khách sạn, phòng và loại phòng
                try:
                    # Store documents using SimpleRAGSystem's internal method
                    self.rag._store_documents_in_qdrant(
                        documents=documents,
                        recreate_collection=False,  # Luôn là False nếu index chung
                        batch_size=batch_size,
                        use_upsert=True  # Use upsert for incremental updates
                    )
                    logger.info(f"✅ Indexed {len(documents)} type rooms successfully")
                    return True
                except Exception as e:
                    logger.error(f"❌ Error indexing type rooms: {e}")
                    return False
            else:
                logger.warning("⚠️  RAG service not initialized - skipping indexing")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing type rooms: {e}")
            return False

