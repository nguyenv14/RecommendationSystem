#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Store Helper

Helper functions for Qdrant vector store operations.
"""

import logging
from typing import Optional, Dict

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)


class VectorStoreHelper:
    """Helper class for Qdrant vector store operations"""
    
    @staticmethod
    def build_filter(location: Optional[str] = None,
                     rank: Optional[int] = None,
                     price_range: Optional[str] = None,
                     brand: Optional[str] = None) -> Optional[Filter]:
        """
        Build Qdrant filter từ extracted keywords
        
        Args:
            location: Area name
            rank: Hotel rank (1-5)
            price_range: "budget" or "luxury"
            brand: Brand name
            
        Returns:
            Qdrant Filter object hoặc None nếu không có filters
        """
        conditions = []
        
        if location:
            conditions.append(
                FieldCondition(key="area_name", match=MatchValue(value=location))
            )
        
        if rank:
            conditions.append(
                FieldCondition(key="hotel_rank", match=MatchValue(value=rank))
            )
        
        # Note: price_range and brand are handled by post-filtering
        # Qdrant doesn't support complex string filters well
        
        if not conditions:
            return None
        
        return Filter(must=conditions)
    
    @staticmethod
    def format_hotel_result(payload: Dict, similarity_score: float, page_content: str = "") -> Dict:
        """
        Format hotel result từ payload
        
        Args:
            payload: Qdrant payload hoặc metadata
            similarity_score: Similarity score
            page_content: Text content (optional)
            
        Returns:
            Formatted hotel dict
        """
        return {
            "hotel_id": payload.get("hotel_id"),
            "hotel_name": payload.get("hotel_name", ""),
            "hotel_rank": payload.get("hotel_rank"),
            "hotel_price_average": payload.get("hotel_price_average"),
            "area_name": payload.get("area_name", ""),
            "brand_name": payload.get("brand_name", ""),
            "price_category": payload.get("price_category", ""),
            "similarity_score": float(similarity_score),
            "text_preview": page_content[:200] + "..." if len(page_content) > 200 else page_content
        }

