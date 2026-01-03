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
from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    from langchain.schema import Document
except ImportError:
    from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartChunker:
    """
    Wrapper cho RecursiveCharacterTextSplitter của LangChain
    Tối ưu cho tiếng Việt
    """
    
    def __init__(self,
                 chunk_size: int = 800,
                 chunk_overlap: int = 50,
                 min_chunk_size: int = 200, # (Có thể không dùng tới trong Recursive gốc nhưng giữ lại để tương thích)
                 preserve_sentences: bool = True):
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Định nghĩa các separators ưu tiên cho tiếng Việt
        # 1. Đoạn văn (\n\n)
        # 2. Xuống dòng (\n)
        # 3. Kết thúc câu (., ;, ?, !)
        # 4. Khoảng trắng
        # 5. Cắt ký tự
        separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", " ", ""]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            keep_separator=True # Giữ lại dấu câu ở cuối chunk trước thay vì đẩy sang chunk sau
        )
        
        logger.info(f"SmartChunker (Recursive) initialized: chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text using RecursiveCharacterTextSplitter
        """
        if not text:
            return []
            
        # LangChain trả về List[str] trực tiếp
        chunks = self.splitter.split_text(text)
        
        return chunks
        
    def chunk_hotel_document(self, 
                             hotel_data: Dict,
                             semantic_text: str) -> List[Document]:
        """
        Chunk hotel document với đầy đủ metadata và Golden Summary
        
        Args:
            hotel_data: Hotel metadata (hotel_id, hotel_name, etc.)
            semantic_text: Semantic text to chunk
            
        Returns:
            List of Document objects với metadata đầy đủ
        """
        # 1. TẠO "GOLDEN SUMMARY" (Thông tin cốt lõi)
        # Đây là đoạn văn ngắn (khoảng 50-100 tokens) chứa đủ thông tin ra quyết định
        # Nó sẽ đi kèm với MỌI chunk của khách sạn này.
        hotel_rank = hotel_data.get("hotel_rank")
        hotel_price = hotel_data.get("hotel_price_average", 0)
        area_name = hotel_data.get("area_name", "")
        price_category = hotel_data.get("price_category", "")
        
        golden_summary_parts = [f"Tên: {hotel_data.get('hotel_name', '')}"]
        if hotel_rank:
            golden_summary_parts.append(f"Hạng: {hotel_rank} sao")
        if hotel_price and hotel_price > 0:
            golden_summary_parts.append(f"Giá TB: {hotel_price:,.0f} VND")
        if area_name:
            golden_summary_parts.append(f"Vị trí: {area_name}")
        if price_category:
            golden_summary_parts.append(f"Phân khúc: {price_category}")
        
        golden_summary = "\n".join([f"- {part}" for part in golden_summary_parts])
        
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
                # --- QUAN TRỌNG: Thêm Golden Summary vào metadata ---
                "hotel_info_summary": golden_summary,  # Thông tin cốt lõi đi kèm mọi chunk
                "chunk_content": chunk,  # Lưu nội dung gốc của chunk (backup)
                # Chunk-specific metadata
                "chunk_index": idx,  # Index of chunk (0, 1, 2, ...)
                "total_chunks": len(text_chunks),  # Total number of chunks
                "chunk_id": f"{hotel_data.get('hotel_id')}_{idx}",  # Unique chunk ID (string, for reference)
                # Additional metadata để preserve context
                "is_first_chunk": idx == 0,
                "is_last_chunk": idx == len(text_chunks) - 1,
                # Document type
                "document_type": "hotel",
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
    
    def chunk_coupon_document(self, 
                             coupon_data: Dict,
                             semantic_text: str) -> List[Document]:
        """
        Chunk coupon document với đầy đủ metadata
        
        Args:
            coupon_data: Coupon metadata (coupon_id, coupon_name, etc.)
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
                "coupon_id": coupon_data.get("coupon_id"),
                "coupon_name": coupon_data.get("coupon_name", ""),
                "coupon_name_code": coupon_data.get("coupon_name_code", ""),
                "coupon_price_sale": coupon_data.get("coupon_price_sale"),
                "is_valid": coupon_data.get("is_valid", False),
                "location": coupon_data.get("location", ""),
                "target_audience": coupon_data.get("target_audience", ""),
                "discount_category": coupon_data.get("discount_category", ""),
                "normalized_name": coupon_data.get("normalized_name", ""),
                # Chunk-specific metadata
                "chunk_index": idx,
                "total_chunks": len(text_chunks),
                "chunk_id": f"{coupon_data.get('coupon_id')}_{idx}",
                "is_first_chunk": idx == 0,
                "is_last_chunk": idx == len(text_chunks) - 1,
                # Document type
                "document_type": "coupon",
            }
            
            # Add all other coupon data to metadata
            for key, value in coupon_data.items():
                if key not in metadata and value is not None:
                    metadata[key] = value
            
            # Create document
            doc = Document(
                page_content=chunk,
                metadata=metadata
            )
            documents.append(doc)
        
        logger.debug(f"Created {len(documents)} chunks for coupon {coupon_data.get('coupon_id')}")
        return documents
    
    def chunk_coupons_batch(self,
                          coupons_df,
                          normalizer) -> List[Document]:
        """
        Chunk multiple coupons in batch
        
        Args:
            coupons_df: DataFrame with coupon data
            normalizer: CouponDataNormalizer instance
            
        Returns:
            List of Document objects
        """
        all_documents = []
        
        for idx, coupon in coupons_df.iterrows():
            coupon_id = int(coupon["coupon_id"])
            
            # Create semantic text
            semantic_text = normalizer.create_semantic_text(coupon)
            
            if not semantic_text or not semantic_text.strip():
                logger.warning(f"Coupon {coupon_id} has no semantic_text, skipping")
                continue
            
            # Create coupon data dict
            coupon_data = {
                "coupon_id": coupon_id,
                "coupon_name": str(coupon.get("coupon_name", "")),
                "coupon_name_code": str(coupon.get("coupon_name_code", "")),
                "coupon_desc": str(coupon.get("coupon_desc", "")),
                "coupon_price_sale": float(coupon.get("coupon_price_sale", 0)) if pd.notna(coupon.get("coupon_price_sale")) else None,
                "coupon_qty_code": int(coupon.get("coupon_qty_code", 0)) if pd.notna(coupon.get("coupon_qty_code")) else None,
                "coupon_start_date": str(coupon.get("coupon_start_date", "")) if pd.notna(coupon.get("coupon_start_date")) else None,
                "coupon_end_date": str(coupon.get("coupon_end_date", "")) if pd.notna(coupon.get("coupon_end_date")) else None,
                "is_valid": normalizer._is_coupon_valid(coupon),
                "location": normalizer._extract_location(coupon),
                "target_audience": normalizer._extract_target_audience(coupon),
                "discount_category": normalizer._categorize_discount(
                    float(coupon.get("coupon_price_sale", 0))
                ) if pd.notna(coupon.get("coupon_price_sale")) else "",
                "normalized_name": normalizer.normalize_text(coupon.get("coupon_name", "")),
            }
            
            # Chunk coupon document
            chunks = self.chunk_coupon_document(coupon_data, semantic_text)
            all_documents.extend(chunks)
        
        logger.info(f"Created {len(all_documents)} chunks from {len(coupons_df)} coupons")
        return all_documents


class StructuredChunker:
    """
    Structured Chunker - Chunk dữ liệu theo format có cấu trúc (1., 2., 3., ...)
    Mỗi section sẽ được chunk riêng biệt với metadata về section type
    """
    
    # Mapping section numbers to semantic types
    SECTION_TYPE_MAPPING = {
        1: "introduction",  # Giới thiệu tổng quan
        2: "amenities",     # Tiện ích & Dịch vụ
        3: "location",      # Vị trí & kết nối
        4: "highlights",    # Điểm nổi bật
        5: "summary",       # Short Summary
    }
    
    # Keywords để detect section type nếu không có số
    SECTION_KEYWORDS = {
        "introduction": ["giới thiệu", "tổng quan", "overview", "introduction"],
        "amenities": ["tiện ích", "dịch vụ", "amenities", "facilities", "services"],
        "location": ["vị trí", "kết nối", "location", "position", "address"],
        "highlights": ["điểm nổi bật", "nổi bật", "highlights", "features", "đặc biệt"],
        "summary": ["summary", "tóm tắt", "short summary", "tổng kết"],
    }
    
    def __init__(self,
                 max_section_size: int = 1500,  # Nếu section quá dài, sẽ chia nhỏ
                 fallback_chunker: Optional[SmartChunker] = None):
        """
        Initialize structured chunker
        
        Args:
            max_section_size: Maximum size of a section before sub-chunking
            fallback_chunker: SmartChunker instance để chia nhỏ section quá dài
        """
        self.max_section_size = max_section_size
        self.fallback_chunker = fallback_chunker or SmartChunker(
            chunk_size=max_section_size,
            chunk_overlap=100,
            min_chunk_size=200,
            preserve_sentences=True
        )
        
        # Pattern để detect numbered sections: "1.", "2.", "1)", "(1)", etc.
        self.section_pattern = re.compile(
            r'^(\d+)[\.\)]\s*([^\d\n]+?)(?=\n\d+[\.\)]|\n*$)', 
            re.MULTILINE | re.DOTALL
        )
        
        logger.info(f"StructuredChunker initialized: max_section_size={max_section_size}")
    
    def detect_sections(self, text: str) -> List[Dict[str, any]]:
        """
        Detect sections trong text dựa trên format số (1., 2., 3., ...)
        
        Args:
            text: Input text
            
        Returns:
            List of sections với metadata
        """
        sections = []
        
        # Try to find numbered sections
        matches = list(self.section_pattern.finditer(text))
        
        if matches:
            # Found numbered sections
            for i, match in enumerate(matches):
                section_num = int(match.group(1))
                section_content = match.group(2).strip()
                
                # Get section title (first line or first sentence)
                lines = section_content.split('\n')
                title = lines[0].strip() if lines else ""
                
                # Remove title from content if it's short (likely a title)
                if len(title) < 100 and '\n' in section_content:
                    content = '\n'.join(lines[1:]).strip()
                else:
                    content = section_content
                
                # Determine section type
                section_type = self.SECTION_TYPE_MAPPING.get(
                    section_num, 
                    self._detect_section_type(title + " " + content)
                )
                
                sections.append({
                    "section_number": section_num,
                    "section_type": section_type,
                    "title": title,
                    "content": content,
                    "full_text": section_content,
                })
        else:
            # No numbered sections found, try to detect by keywords
            logger.warning("No numbered sections found, trying keyword-based detection")
            sections = self._detect_sections_by_keywords(text)
        
        return sections
    
    def _detect_section_type(self, text: str) -> str:
        """Detect section type từ text content"""
        text_lower = text.lower()
        
        for section_type, keywords in self.SECTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return section_type
        
        return "general"  # Default type
    
    def _detect_sections_by_keywords(self, text: str) -> List[Dict[str, any]]:
        """Detect sections bằng keywords nếu không có số"""
        sections = []
        lines = text.split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if this line is a section header
            detected_type = None
            for section_type, keywords in self.SECTION_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in line_lower and len(line) < 100:  # Likely a header
                        detected_type = section_type
                        break
                if detected_type:
                    break
            
            if detected_type:
                # Save previous section
                if current_section:
                    sections.append({
                        "section_number": len(sections) + 1,
                        "section_type": current_section,
                        "title": current_content[0] if current_content else "",
                        "content": '\n'.join(current_content[1:]) if len(current_content) > 1 else '\n'.join(current_content),
                        "full_text": '\n'.join(current_content),
                    })
                
                # Start new section
                current_section = detected_type
                current_content = [line]
            else:
                if current_section:
                    current_content.append(line)
                else:
                    # No section detected yet, treat as introduction
                    if not current_section:
                        current_section = "introduction"
                    current_content.append(line)
        
        # Add last section
        if current_section and current_content:
            sections.append({
                "section_number": len(sections) + 1,
                "section_type": current_section,
                "title": current_content[0] if current_content else "",
                "content": '\n'.join(current_content[1:]) if len(current_content) > 1 else '\n'.join(current_content),
                "full_text": '\n'.join(current_content),
            })
        
        return sections
    
    def chunk_hotel_document(self,
                             hotel_data: Dict,
                             semantic_text: str) -> List[Document]:
        """
        Chunk hotel document theo format có cấu trúc
        
        Args:
            hotel_data: Hotel metadata
            semantic_text: Semantic text to chunk (có format 1., 2., 3., ...)
            
        Returns:
            List of Document objects với section metadata
        """
        # Detect sections
        sections = self.detect_sections(semantic_text)
        
        if not sections:
            # Fallback to regular chunking if no structure detected
            logger.warning(f"No structured sections found for hotel {hotel_data.get('hotel_id')}, using fallback chunker")
            return self.fallback_chunker.chunk_hotel_document(hotel_data, semantic_text)
        
        documents = []
        global_chunk_index = 0
        
        for section in sections:
            section_content = section["content"]
            
            # If section is too long, sub-chunk it
            if len(section_content) > self.max_section_size:
                sub_chunks = self.fallback_chunker.split_text(section_content)
                
                for sub_idx, sub_chunk in enumerate(sub_chunks):
                    metadata = self._create_section_metadata(
                        hotel_data, section, global_chunk_index, 
                        len(sections), sub_idx, len(sub_chunks)
                    )
                    
                    doc = Document(
                        page_content=sub_chunk,
                        metadata=metadata
                    )
                    documents.append(doc)
                    global_chunk_index += 1
            else:
                # Section fits in one chunk
                metadata = self._create_section_metadata(
                    hotel_data, section, global_chunk_index,
                    len(sections), 0, 1
                )
                
                doc = Document(
                    page_content=section_content,
                    metadata=metadata
                )
                documents.append(doc)
                global_chunk_index += 1
        
        logger.debug(f"Created {len(documents)} structured chunks for hotel {hotel_data.get('hotel_id')} "
                    f"from {len(sections)} sections")
        return documents
    
    def _create_section_metadata(self,
                                 hotel_data: Dict,
                                 section: Dict,
                                 global_chunk_index: int,
                                 total_sections: int,
                                 sub_chunk_index: int,
                                 total_sub_chunks: int) -> Dict:
        """Create metadata for a section chunk with Golden Summary"""
        # 1. TẠO "GOLDEN SUMMARY" (Thông tin cốt lõi)
        hotel_rank = hotel_data.get("hotel_rank")
        hotel_price = hotel_data.get("hotel_price_average", 0)
        area_name = hotel_data.get("area_name", "")
        price_category = hotel_data.get("price_category", "")
        
        golden_summary_parts = [f"Tên: {hotel_data.get('hotel_name', '')}"]
        if hotel_rank:
            golden_summary_parts.append(f"Hạng: {hotel_rank} sao")
        if hotel_price and hotel_price > 0:
            golden_summary_parts.append(f"Giá TB: {hotel_price:,.0f} VND")
        if area_name:
            golden_summary_parts.append(f"Vị trí: {area_name}")
        if price_category:
            golden_summary_parts.append(f"Phân khúc: {price_category}")
        
        golden_summary = "\n".join([f"- {part}" for part in golden_summary_parts])
        
        metadata = {
            "hotel_id": hotel_data.get("hotel_id"),
            "hotel_name": hotel_data.get("hotel_name", ""),
            "hotel_rank": hotel_data.get("hotel_rank"),
            "hotel_price_average": hotel_data.get("hotel_price_average"),
            "area_name": hotel_data.get("area_name", ""),
            "brand_name": hotel_data.get("brand_name", ""),
            "price_category": hotel_data.get("price_category", ""),
            "normalized_name": hotel_data.get("normalized_name", ""),
            
            # --- QUAN TRỌNG: Thêm Golden Summary vào metadata ---
            "hotel_info_summary": golden_summary,  # Thông tin cốt lõi đi kèm mọi chunk
            
            # Section-specific metadata
            "section_number": section["section_number"],
            "section_type": section["section_type"],
            "section_title": section["title"],
            "is_structured": True,
            
            # Chunk-specific metadata
            "chunk_index": global_chunk_index,
            "total_chunks": None,  # Will be set after all chunks created
            "chunk_id": f"{hotel_data.get('hotel_id')}_{section['section_number']}_{sub_chunk_index}",
            
            # Sub-chunk metadata (if section was split)
            "sub_chunk_index": sub_chunk_index,
            "total_sub_chunks": total_sub_chunks,
            "is_sub_chunked": total_sub_chunks > 1,
            
            # Section position
            "total_sections": total_sections,
            "is_first_section": section["section_number"] == 1,
            "is_last_section": section["section_number"] == total_sections,
            
            # Document type
            "document_type": "hotel",
            "chunking_method": "structured",
        }
        
        # Add all other hotel data
        for key, value in hotel_data.items():
            if key not in metadata and value is not None:
                metadata[key] = value
        
        return metadata
    
    def chunk_hotels_batch(self,
                          hotels_df,
                          normalizer) -> List[Document]:
        """
        Chunk multiple hotels in batch using structured chunking
        
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
            
            # Chunk hotel document using structured chunking
            chunks = self.chunk_hotel_document(hotel_data, semantic_text)
            
            # Update total_chunks for all chunks
            total_chunks = len(chunks)
            for chunk in chunks:
                chunk.metadata["total_chunks"] = total_chunks
            
            all_documents.extend(chunks)
        
        logger.info(f"Created {len(all_documents)} structured chunks from {len(hotels_df)} hotels")
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
    
    # Test Structured Chunker
    print("\n\n🧪 Testing Structured Chunker...")
    
    structured_chunker = StructuredChunker(max_section_size=1500)
    
    # Test với format có cấu trúc
    structured_text = """1. Giới thiệu tổng quan – Meliá Vinpearl Riverfront Đà Nẵng
Meliá Vinpearl Riverfront Đà Nẵng là khách sạn 5 sao cao cấp tọa lạc tại số 341 Trần Hưng Đạo, Quận Sơn Trà, nằm ngay bên bờ sông Hàn và đối diện Cầu Rồng – biểu tượng nổi bật của thành phố Đà Nẵng. Khách sạn mang phong cách hiện đại, sang trọng, kết hợp mô hình phòng nghỉ và căn hộ tiêu chuẩn quốc tế, phù hợp cho cả kỳ nghỉ dưỡng lẫn công tác. Nhờ vị trí đắc địa, Meliá Vinpearl Riverfront Đà Nẵng sở hữu tầm nhìn toàn cảnh hướng biển, sông và trung tâm thành phố.

2. Tiện ích & Dịch vụ – Meliá Vinpearl Riverfront Đà Nẵng
Meliá Vinpearl Riverfront Đà Nẵng cung cấp hệ thống tiện ích toàn diện cho khách lưu trú:
Hồ bơi vô cực ngoài trời với tầm nhìn bao quát sông Hàn.
Nhà hàng và quầy bar cao cấp, phục vụ ẩm thực Việt Nam, quốc tế và buffet sáng phong phú.
Phòng gym hiện đại, khu spa chăm sóc sức khỏe và khu vui chơi trẻ em.
Dịch vụ hội nghị – sự kiện chuyên nghiệp.
Dịch vụ đưa đón sân bay, hỗ trợ thuê xe, lễ tân 24/7 và dịch vụ phòng.

3. Vị trí & kết nối – Meliá Vinpearl Riverfront Đà Nẵng
Meliá Vinpearl Riverfront Đà Nẵng nằm gần các điểm du lịch nổi tiếng, dễ dàng di chuyển trong vài phút:
Cầu Rồng: khoảng 1 km
Biển Mỹ Khê: khoảng 2 km
Chợ Hàn: khoảng 1,5 km
Sân bay Quốc tế Đà Nẵng: khoảng 5 km
Từ khách sạn, du khách có thể tận hưởng tầm nhìn đẹp hướng sông Hàn, biển và thành phố, đồng thời kết nối thuận tiện đến các khu vực trung tâm.

4. Điểm nổi bật – Meliá Vinpearl Riverfront Đà Nẵng
Vị trí ven sông Hàn hiếm có, đối diện Cầu Rồng – biểu tượng của Đà Nẵng.
Hầu hết các phòng và căn hộ đều có view biển, view sông hoặc view thành phố.
Căn hộ có bếp tiện lợi, phù hợp cho gia đình hoặc kỳ lưu trú dài ngày.
Hồ bơi vô cực cùng hệ thống tiện ích sang trọng tiêu chuẩn quốc tế.
Thuộc thương hiệu Meliá, đảm bảo chất lượng dịch vụ cao cấp và tiêu chuẩn vận hành đồng nhất.

5. Short Summary – Meliá Vinpearl Riverfront Đà Nẵng
Meliá Vinpearl Riverfront Đà Nẵng là khách sạn 5 sao ven sông Hàn với tầm nhìn tuyệt đẹp, sở hữu phòng nghỉ và căn hộ sang trọng, hồ bơi vô cực, nhà hàng cao cấp và vị trí trung tâm thuận tiện. Đây là lựa chọn lý tưởng cho du khách muốn kết hợp nghỉ dưỡng và khám phá Đà Nẵng."""
    
    print(f"\nOriginal structured text length: {len(structured_text)} characters")
    
    # Detect sections
    sections = structured_chunker.detect_sections(structured_text)
    print(f"\nDetected {len(sections)} sections:")
    for section in sections:
        print(f"  Section {section['section_number']}: {section['section_type']} - {section['title'][:50]}...")
    
    # Chunk with metadata
    hotel_data = {
        "hotel_id": 1,
        "hotel_name": "Meliá Vinpearl Riverfront Đà Nẵng",
        "hotel_rank": 5,
        "hotel_price_average": 3000000,
        "area_name": "Sơn Trà",
        "brand_name": "Meliá Vinpearl",
        "price_category": "giá rất cao",
        "normalized_name": "melia vinpearl riverfront da nang"
    }
    
    documents = structured_chunker.chunk_hotel_document(hotel_data, structured_text)
    print(f"\nCreated {len(documents)} structured documents:")
    for i, doc in enumerate(documents):
        print(f"\nDocument {i+1}:")
        print(f"  Section: {doc.metadata['section_number']} ({doc.metadata['section_type']})")
        print(f"  Title: {doc.metadata['section_title']}")
        print(f"  Content: {doc.page_content[:100]}...")
        print(f"  Metadata: chunk_id={doc.metadata['chunk_id']}, "
              f"is_sub_chunked={doc.metadata.get('is_sub_chunked', False)}")
    
    print("\n✅ Structured chunking test complete!")


if __name__ == "__main__":
    main()

