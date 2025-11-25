#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Chunker Module
Chunking thông minh với metadata preservation để không mất ngữ nghĩa
"""

import re
import logging
import pandas as pd
from typing import List, Dict, Optional

try:
    from langchain.schema import Document
except ImportError:
    from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartChunker:
    """Smart chunking với metadata preservation"""
    
    def __init__(self,
                 chunk_size: int = 800,  # Tăng chunk_size để giảm số lượng chunks
                 chunk_overlap: int = 50,  # Giảm overlap
                 min_chunk_size: int = 200,  # Tăng min_chunk_size
                 preserve_sentences: bool = True):
        """
        Initialize smart chunker
        
        Args:
            chunk_size: Maximum size of each chunk (characters)
            chunk_overlap: Overlap between chunks (characters)
            min_chunk_size: Minimum size of chunk (characters)
            preserve_sentences: If True, don't split in middle of sentences
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.preserve_sentences = preserve_sentences
        
        # Vietnamese sentence endings
        self.sentence_endings = r'[.!?。！？]\s+'
        
        logger.info(f"SmartChunker initialized: chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        
        if self.preserve_sentences:
            # Split by sentences first
            sentences = re.split(self.sentence_endings, text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            current_chunk = ""
            for sentence in sentences:
                # If adding this sentence would exceed chunk_size
                if len(current_chunk) + len(sentence) + 2 > self.chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    # Start new chunk with overlap
                    if chunks and self.chunk_overlap > 0:
                        # Get last part of previous chunk for overlap
                        prev_chunk = chunks[-1]
                        overlap_text = prev_chunk[-self.chunk_overlap:]
                        current_chunk = overlap_text + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    if current_chunk:
                        current_chunk += ". " + sentence
                    else:
                        current_chunk = sentence
            
            # Add last chunk
            if current_chunk:
                chunks.append(current_chunk.strip())
        else:
            # Simple character-based chunking
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                
                # Add overlap from previous chunk
                if start > 0 and self.chunk_overlap > 0:
                    overlap_start = max(0, start - self.chunk_overlap)
                    chunk = text[overlap_start:end]
                else:
                    chunk = text[start:end]
                
                chunks.append(chunk.strip())
                start = end - self.chunk_overlap
        
        # Filter out chunks that are too small
        chunks = [chunk for chunk in chunks if len(chunk) >= self.min_chunk_size]
        
        return chunks
    
    def chunk_hotel_document(self, 
                             hotel_data: Dict,
                             semantic_text: str) -> List[Document]:
        """
        Chunk hotel document với đầy đủ metadata
        
        Args:
            hotel_data: Hotel metadata (hotel_id, hotel_name, etc.)
            semantic_text: Semantic text to chunk
            
        Returns:
            List of Document objects với metadata đầy đủ
        """
        # Split text into chunks
        text_chunks = self.split_text(semantic_text)
        
        # Create documents with metadata
        documents = []
        for idx, chunk in enumerate(text_chunks):
            # Create metadata với đầy đủ thông tin
            metadata = {
                "hotel_id": hotel_data.get("hotel_id"),
                "hotel_name": hotel_data.get("hotel_name", ""),
                "hotel_rank": hotel_data.get("hotel_rank"),
                "hotel_price_average": hotel_data.get("hotel_price_average"),
                "area_name": hotel_data.get("area_name", ""),
                "brand_name": hotel_data.get("brand_name", ""),
                "price_category": hotel_data.get("price_category", ""),
                "normalized_name": hotel_data.get("normalized_name", ""),
                # Chunk-specific metadata
                "chunk_index": idx,  # Index of chunk (0, 1, 2, ...)
                "total_chunks": len(text_chunks),  # Total number of chunks
                "chunk_id": f"{hotel_data.get('hotel_id')}_{idx}",  # Unique chunk ID (string, for reference)
                # Additional metadata để preserve context
                "is_first_chunk": idx == 0,
                "is_last_chunk": idx == len(text_chunks) - 1,
            }
            
            # Add all other hotel data to metadata
            for key, value in hotel_data.items():
                if key not in metadata and value is not None:
                    metadata[key] = value
            
            # Create document
            doc = Document(
                page_content=chunk,
                metadata=metadata
            )
            documents.append(doc)
        
        logger.debug(f"Created {len(documents)} chunks for hotel {hotel_data.get('hotel_id')}")
        return documents
    
    def chunk_hotels_batch(self,
                          hotels_df,
                          normalizer) -> List[Document]:
        """
        Chunk multiple hotels in batch
        
        Args:
            hotels_df: DataFrame with hotel data
            normalizer: HotelDataNormalizer instance
            
        Returns:
            List of Document objects
        """
        all_documents = []
        
        for idx, hotel in hotels_df.iterrows():
            hotel_id = int(hotel["hotel_id"])
            
            # Create semantic text
            semantic_text = normalizer.create_semantic_text(hotel)
            
            if not semantic_text or not semantic_text.strip():
                logger.warning(f"Hotel {hotel_id} has no semantic_text, skipping")
                continue
            
            # Create hotel data dict
            hotel_data = {
                "hotel_id": hotel_id,
                "hotel_name": str(hotel.get("hotel_name", "")),
                "hotel_rank": int(hotel.get("hotel_rank", 0)) if pd.notna(hotel.get("hotel_rank")) else None,
                "hotel_price_average": float(hotel.get("hotel_price_average", 0)) if pd.notna(hotel.get("hotel_price_average")) else None,
                "area_name": str(hotel.get("area_name", "")) if pd.notna(hotel.get("area_name")) else "",
                "brand_name": str(hotel.get("brand_name", "")) if pd.notna(hotel.get("brand_name")) else "",
                "price_category": normalizer._categorize_price(
                    float(hotel.get("hotel_price_average", 0))
                ) if pd.notna(hotel.get("hotel_price_average")) else "",
                "normalized_name": normalizer.normalize_text(hotel.get("hotel_name", "")),
            }
            
            # Chunk hotel document
            chunks = self.chunk_hotel_document(hotel_data, semantic_text)
            all_documents.extend(chunks)
        
        logger.info(f"Created {len(all_documents)} chunks from {len(hotels_df)} hotels")
        return all_documents


def main():
    """Test smart chunker"""
    import pandas as pd
    
    print("🧪 Testing Smart Chunker...")
    
    # Initialize chunker
    chunker = SmartChunker(
        chunk_size=500,
        chunk_overlap=100,
        min_chunk_size=100,
        preserve_sentences=True
    )
    
    # Test text
    test_text = """
    Khách sạn A là một khách sạn 5 sao tuyệt đẹp tọa lạc tại trung tâm thành phố Đà Nẵng.
    Khách sạn có view biển tuyệt đẹp, nhìn ra biển Mỹ Khê thơ mộng.
    Với hơn 200 phòng nghỉ sang trọng, khách sạn mang đến trải nghiệm nghỉ dưỡng đẳng cấp.
    Khách sạn có đầy đủ tiện ích như hồ bơi vô cực, spa thư giãn, nhà hàng cao cấp.
    Khách sạn phù hợp cho cả du lịch nghỉ dưỡng và công tác.
    """
    
    print(f"\nOriginal text length: {len(test_text)} characters")
    
    # Split text
    chunks = chunker.split_text(test_text)
    print(f"\nSplit into {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} ({len(chunk)} chars):")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)
    
    # Test chunking with metadata
    print("\n\n🧪 Testing chunking with metadata...")
    hotel_data = {
        "hotel_id": 1,
        "hotel_name": "Khách sạn A",
        "hotel_rank": 5,
        "hotel_price_average": 2000000,
        "area_name": "Sơn Trà",
        "brand_name": "Vinpearl",
        "price_category": "giá cao",
        "normalized_name": "khach san a"
    }
    
    documents = chunker.chunk_hotel_document(hotel_data, test_text)
    print(f"\nCreated {len(documents)} documents:")
    for i, doc in enumerate(documents):
        print(f"\nDocument {i+1}:")
        print(f"  Content: {doc.page_content[:100]}...")
        print(f"  Metadata: hotel_id={doc.metadata['hotel_id']}, "
              f"chunk_index={doc.metadata['chunk_index']}, "
              f"total_chunks={doc.metadata['total_chunks']}")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    main()

