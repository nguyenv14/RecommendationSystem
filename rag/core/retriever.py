#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hotel Retriever

Retrieval logic for hotel search with filtering support.
"""

import logging
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant

from .query_extractor import QueryExtractor
from .vectorstore import VectorStoreHelper

logger = logging.getLogger(__name__)


class HotelRetriever:
    """
    Hotel Retriever - Layer 2: Retrieval Pipeline
    Handles both filtered (QdrantClient) and simple (LangChain) search
    """
    
    def __init__(self, qdrant_url: str, collection_name: str, 
                 vectorstore: Qdrant, embeddings, query_extractor: QueryExtractor):
        """
        Initialize Hotel Retriever
        
        Args:
            qdrant_url: Qdrant server URL
            collection_name: Collection name
            vectorstore: LangChain Qdrant vectorstore
            embeddings: Embeddings instance
            query_extractor: QueryExtractor instance
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.query_extractor = query_extractor
    
    def search_with_filter(self, query: str, query_embedding: List[float],
                          area_name: str, extracted_keywords: Dict,
                          top_k: int) -> List[Dict]:
        """
        Search hotels using QdrantClient with location filter
        
        Args:
            query: Search query
            query_embedding: Query embedding vector
            area_name: Location to filter
            extracted_keywords: Extracted keywords
            top_k: Number of results
            
        Returns:
            List of hotel results
        """
        client = QdrantClient(url=self.qdrant_url)
        
        # Build Qdrant filter
        qdrant_filter = VectorStoreHelper.build_filter(
            location=area_name,
            rank=extracted_keywords.get("rank"),
            price_range=extracted_keywords.get("price_range"),
            brand=extracted_keywords.get("brand")
        )
        
        # Search with filter
        search_results = client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=min(top_k * 2, 10),  # Get more results for post-filtering
            query_filter=qdrant_filter,
            with_payload=True,
            with_vectors=False
        )
        
        # Format and post-filter results
        hotels = []
        for result in search_results:
            payload = result.payload or {}
            hotel_area = payload.get("area_name", "")
            
            # Post-filter: location must match
            if not hotel_area or hotel_area.strip() != area_name:
                continue
            
            # Get page_content
            page_content = payload.get("content") or payload.get("text") or ""
            
            # Post-filter: keyword filters
            if not self._matches_keyword_filters(payload, page_content, extracted_keywords):
                continue
            
            # Format result
            hotels.append(VectorStoreHelper.format_hotel_result(payload, result.score, page_content))
            
            if len(hotels) >= top_k:
                break
        
        logger.info(f"Found {len(hotels)} hotels in {area_name} (after filtering)")
        return hotels
    
    def search_without_filter(self, query: str, query_embedding: List[float],
                             area_name: Optional[str], extracted_keywords: Dict,
                             top_k: int) -> List[Dict]:
        """
        Search hotels using LangChain vectorstore without filter
        
        Args:
            query: Search query
            query_embedding: Query embedding vector (not used)
            area_name: Optional location for post-filtering
            extracted_keywords: Extracted keywords
            top_k: Number of results
            
        Returns:
            List of hotel results
        """
        # Use LangChain vectorstore for simple semantic search
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=min(top_k * 2, 10)  # Get more results for post-filtering
        )
        
        hotels = []
        for doc, score in results:
            # Convert distance to similarity
            similarity_score = max(0, 1 - score)
            
            # Filter by similarity threshold
            if similarity_score < 0.3:
                continue
            
            # Validate hotel name
            hotel_name = doc.metadata.get("hotel_name", "").strip()
            if not hotel_name:
                continue
            
            # Post-filter: location (if specified)
            hotel_area = doc.metadata.get("area_name", "")
            if area_name and hotel_area and hotel_area.strip() != area_name:
                continue
            
            # Post-filter: keyword filters
            if not self._matches_keyword_filters(doc.metadata, doc.page_content, extracted_keywords):
                continue
            
            # Format result
            hotels.append(VectorStoreHelper.format_hotel_result(
                doc.metadata,
                similarity_score,
                doc.page_content
            ))
            
            if len(hotels) >= top_k:
                break
        
        return hotels
    
    def _matches_keyword_filters(self, payload: Dict, page_content: str, extracted_keywords: Dict) -> bool:
        """Check if hotel matches extracted keyword filters"""
        # Check rank filter
        if extracted_keywords.get("rank") and payload.get("hotel_rank"):
            if payload.get("hotel_rank") != extracted_keywords["rank"]:
                return False
        
        # Check price_range filter
        if extracted_keywords.get("price_range"):
            hotel_price_category = payload.get("price_category", "")
            if extracted_keywords["price_range"] == "budget" and hotel_price_category not in ["budget", "economy"]:
                return False
            elif extracted_keywords["price_range"] == "luxury" and hotel_price_category not in ["luxury", "premium"]:
                return False
        
        # Check brand filter
        if extracted_keywords.get("brand"):
            hotel_brand = payload.get("brand_name", "").lower()
            if extracted_keywords["brand"].lower() not in hotel_brand:
                return False
        
        # Check amenities filter (text-based)
        if extracted_keywords.get("amenities"):
            page_content_lower = page_content.lower()
            amenities_match = all(
                any(syn in page_content_lower for syn in self.query_extractor.get_amenity_synonyms(amenity))
                for amenity in extracted_keywords["amenities"]
            )
            if not amenities_match:
                return False
        
        return True

