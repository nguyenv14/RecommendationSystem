#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để index rooms và type_rooms vào RAG system
Chạy script này để vector hóa và lưu rooms + type_rooms vào Qdrant (cùng collection với hotels)
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_rag_system import SimpleRAGSystem
from data.processor import DataProcessor
from data.connector import DatabaseConnector
from data.normalizer import HotelDataNormalizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to index rooms and type_rooms"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Index rooms and type_rooms into RAG system')
    parser.add_argument('--ollama-url', type=str, default='http://localhost:11434',
                       help='Ollama server URL (default: http://localhost:11434)')
    parser.add_argument('--qdrant-url', type=str, default='http://localhost:6333',
                       help='Qdrant server URL (default: http://localhost:6333)')
    parser.add_argument('--embedding-model', type=str, default='bge-m3',
                       help='Embedding model name (default: bge-m3)')
    parser.add_argument('--collection-name', type=str, default='hotels',
                       help='Qdrant collection name (default: hotels - same as hotels)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Batch size for processing (default: 100)')
    parser.add_argument('--index-rooms', action='store_true', default=True,
                       help='Index rooms (default: True)')
    parser.add_argument('--index-type-rooms', action='store_true', default=True,
                       help='Index type_rooms (default: True)')
    parser.add_argument('--hotel-ids', type=str, default=None,
                       help='Comma-separated hotel IDs to index (e.g., "1,2,3"). If not provided, index all.')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting rooms and type_rooms indexing...")
    logger.info(f"Configuration:")
    logger.info(f"  - Ollama URL: {args.ollama_url}")
    logger.info(f"  - Qdrant URL: {args.qdrant_url}")
    logger.info(f"  - Embedding model: {args.embedding_model}")
    logger.info(f"  - Collection name: {args.collection_name}")
    logger.info(f"  - Batch size: {args.batch_size}")
    logger.info(f"  - Index rooms: {args.index_rooms}")
    logger.info(f"  - Index type_rooms: {args.index_type_rooms}")
    if args.hotel_ids:
        logger.info(f"  - Hotel IDs filter: {args.hotel_ids}")
    
    try:
        # Initialize RAG system
        logger.info("📦 Initializing RAG system...")
        rag_system = SimpleRAGSystem(
            ollama_url=args.ollama_url,
            qdrant_url=args.qdrant_url,
            embedding_model=args.embedding_model,
            collection_name=args.collection_name
        )
        
        # Initialize DataProcessor
        logger.info("📦 Initializing DataProcessor...")
        processor = DataProcessor(rag=rag_system)
        
        # Parse hotel IDs if provided
        hotel_ids_list = None
        if args.hotel_ids:
            try:
                hotel_ids_list = [int(hid.strip()) for hid in args.hotel_ids.split(',') if hid.strip().isdigit()]
                logger.info(f"Filtering by hotel IDs: {hotel_ids_list}")
            except Exception as e:
                logger.warning(f"Invalid hotel_ids format: {e}, indexing all hotels")
        
        # Index rooms
        if args.index_rooms:
            logger.info("")
            logger.info("=" * 70)
            logger.info("🔄 Indexing ROOMS...")
            logger.info("=" * 70)
            
            try:
                # If hotel_ids specified, we need to filter rooms
                if hotel_ids_list:
                    # Get rooms for specific hotels
                    db_connector = DatabaseConnector()
                    rooms_df = db_connector.get_rooms_enriched(hotel_ids=hotel_ids_list)
                    
                    if not rooms_df.empty:
                        logger.info(f"📊 Found {len(rooms_df)} rooms for specified hotels")
                        normalizer = HotelDataNormalizer()
                        normalized_df = normalizer.normalize_rooms(rooms_df)
                        
                        # Convert to documents
                        from langchain.schema import Document
                        documents = []
                        for _, row in normalized_df.iterrows():
                            doc = Document(
                                page_content=row['semantic_text'],
                                metadata={
                                    'document_type': 'room',
                                    'hotel_id': int(row['hotel_id']),
                                    'hotel_name': row['hotel_name'],
                                    'room_id': int(row['room_id']),
                                    'price': float(row['search_price']),
                                    'type_name': row['type_room_name']
                                }
                            )
                            documents.append(doc)
                        
                        # Index documents
                        rag_system._store_documents_in_qdrant(
                            documents=documents,
                            recreate_collection=False,
                            batch_size=args.batch_size,
                            use_upsert=True
                        )
                        logger.info(f"✅ Indexed {len(documents)} rooms successfully")
                    else:
                        logger.warning("No rooms found for specified hotel IDs")
                else:
                    # Index all rooms using processor
                    success = processor.process_and_index_rooms(
                        recreate_collection=False,
                        batch_size=args.batch_size
                    )
                    if success:
                        logger.info("✅ Rooms indexing completed successfully!")
                    else:
                        logger.error("❌ Failed to index rooms")
            except Exception as e:
                logger.error(f"❌ Error indexing rooms: {e}", exc_info=True)
        
        # Index type_rooms
        if args.index_type_rooms:
            logger.info("")
            logger.info("=" * 70)
            logger.info("🔄 Indexing TYPE ROOMS...")
            logger.info("=" * 70)
            
            try:
                # If hotel_ids specified, we need to filter type_rooms
                if hotel_ids_list:
                    # Get type_rooms for specific hotels
                    db_connector = DatabaseConnector()
                    type_rooms_df = db_connector.get_type_rooms_enriched(hotel_ids=hotel_ids_list)
                    
                    if not type_rooms_df.empty:
                        logger.info(f"📊 Found {len(type_rooms_df)} type_rooms for specified hotels")
                        normalizer = HotelDataNormalizer()
                        normalized_df = normalizer.normalize_type_rooms(type_rooms_df)
                        
                        # Convert to documents
                        from langchain.schema import Document
                        documents = []
                        for _, row in normalized_df.iterrows():
                            # Parse hotel_ids string to list
                            hotel_ids_str = str(row.get('hotel_ids', ''))
                            hotel_ids_list_parsed = []
                            if hotel_ids_str and hotel_ids_str != 'nan':
                                try:
                                    hotel_ids_list_parsed = [int(hid) for hid in hotel_ids_str.split(',') if hid.strip().isdigit()]
                                except:
                                    hotel_ids_list_parsed = []
                            
                            doc = Document(
                                page_content=row['semantic_text'],
                                metadata={
                                    'document_type': 'type_room',
                                    'type_room_id': int(row['type_room_id']),
                                    'type_room_name': row['type_room_name'],
                                    'hotel_ids': hotel_ids_list_parsed,
                                    'hotel_names': str(row.get('hotel_names', '')),
                                    'min_price': float(row.get('search_min_price', 0)),
                                    'max_price': float(row.get('search_max_price', 0)),
                                    'avg_price': float(row.get('search_avg_price', 0)),
                                    'room_count': int(row.get('room_count', 0))
                                }
                            )
                            documents.append(doc)
                        
                        # Index documents
                        rag_system._store_documents_in_qdrant(
                            documents=documents,
                            recreate_collection=False,
                            batch_size=args.batch_size,
                            use_upsert=True
                        )
                        logger.info(f"✅ Indexed {len(documents)} type_rooms successfully")
                    else:
                        logger.warning("No type_rooms found for specified hotel IDs")
                else:
                    # Index all type_rooms using processor
                    success = processor.process_and_index_type_rooms(
                        recreate_collection=False,
                        batch_size=args.batch_size
                    )
                    if success:
                        logger.info("✅ Type rooms indexing completed successfully!")
                    else:
                        logger.error("❌ Failed to index type_rooms")
            except Exception as e:
                logger.error(f"❌ Error indexing type_rooms: {e}", exc_info=True)
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ Rooms and Type Rooms indexing completed!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Error during indexing: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()





