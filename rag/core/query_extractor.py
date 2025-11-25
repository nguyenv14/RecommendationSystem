#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Extractor

Extract keywords from user queries for better search performance.
Supports both LLM-based and rule-based extraction.
"""

import json
import re
import logging
from typing import Dict, Optional, List

from langchain_community.chat_models import ChatOpenAI

logger = logging.getLogger(__name__)


class QueryExtractor:
    """Extract keywords from queries"""
    
    # Location mapping for Đà Nẵng
    LOCATIONS = {
        "ngũ hành sơn": "Ngũ Hành Sơn",
        "ngu hanh son": "Ngũ Hành Sơn",
        "quận ngũ hành sơn": "Ngũ Hành Sơn",
        "sơn trà": "Sơn Trà",
        "son tra": "Sơn Trà",
        "quận sơn trà": "Sơn Trà",
        "cẩm lệ": "Cẩm Lệ",
        "cam le": "Cẩm Lệ",
        "quận cẩm lệ": "Cẩm Lệ",
        "hải châu": "Hải Châu",
        "hai chau": "Hải Châu",
        "quận hải châu": "Hải Châu",
        "liên chiểu": "Liên Chiểu",
        "lien chieu": "Liên Chiểu",
        "quận liên chiểu": "Liên Chiểu",
        "thanh khê": "Thanh Khê",
        "thanh khe": "Thanh Khê",
        "quận thanh khê": "Thanh Khê",
        "hòa vang": "Hòa Vang",
        "hoa vang": "Hòa Vang",
        "huyện hòa vang": "Hòa Vang",
    }
    
    # Rank patterns
    RANK_PATTERNS = {
        5: ["5 sao", "năm sao", "5 stars", "luxury", "cao cấp", "sang trọng", "premium"],
        4: ["4 sao", "bốn sao", "4 stars"],
        3: ["3 sao", "ba sao", "3 stars"],
        2: ["2 sao", "hai sao", "2 stars"],
        1: ["1 sao", "một sao", "1 stars"]
    }
    
    # Price patterns
    BUDGET_PATTERNS = ["giá rẻ", "giá tốt", "giá hợp lý", "giá phải chăng", "giá thấp", "rẻ", "tầm thấp"]
    LUXURY_PATTERNS = ["giá cao", "giá đắt", "giá đắt đỏ", "premium", "đắt", "tầm cao", "luxury"]
    
    # Amenities mapping
    AMENITIES_MAPPING = {
        "hồ bơi": ["hồ bơi", "bể bơi", "pool", "swimming pool", "bơi"],
        "spa": ["spa", "massage", "thư giãn", "massage spa"],
        "gym": ["gym", "phòng gym", "thể hình", "fitness", "phòng tập"],
        "nhà hàng": ["nhà hàng", "restaurant", "quán ăn"],
        "wifi": ["wifi", "internet", "mạng"],
        "parking": ["bãi đỗ xe", "parking", "đậu xe", "đỗ xe", "chỗ đậu xe"],
        "breakfast": ["bữa sáng", "breakfast", "ăn sáng", "sáng"],
        "airport": ["sân bay", "airport", "gần sân bay", "cách sân bay"],
        "beach": ["gần biển", "ven biển", "sát biển", "cách biển", "bờ biển", "beach"],
        "center": ["trung tâm", "center", "gần trung tâm", "trong trung tâm"]
    }
    
    # Brand patterns
    BRAND_PATTERNS = {
        "Sheraton": ["sheraton"],
        "InterContinental": ["intercontinental", "inter continental"],
        "Melia": ["melia", "meliá"],
        "Vinpearl": ["vinpearl"],
        "Furama": ["furama"],
        "Pullman": ["pullman"],
        "Novotel": ["novotel"],
        "Hyatt": ["hyatt"],
        "Hilton": ["hilton"],
        "Marriott": ["marriott"]
    }
    
    # Keyword patterns
    KEYWORD_PATTERNS = {
        "view biển": ["view biển", "hướng biển", "nhìn ra biển", "tầm nhìn biển", "view beach"],
        "view sông": ["view sông", "hướng sông", "nhìn ra sông", "tầm nhìn sông", "view river"],
        "view thành phố": ["view thành phố", "hướng thành phố", "nhìn ra thành phố", "view city"],
        "family": ["gia đình", "family", "cho gia đình", "phù hợp gia đình"],
        "romantic": ["lãng mạn", "romantic", "cặp đôi", "honeymoon"],
        "business": ["công tác", "business", "doanh nhân"]
    }
    
    def __init__(self, llm=None, use_llm: bool = True):
        """
        Initialize Query Extractor
        
        Args:
            llm: LLM instance for extraction (optional)
            use_llm: Whether to use LLM for extraction
        """
        self.llm = llm
        self.use_llm = use_llm and llm is not None
    
    def extract_location(self, query: str) -> Optional[str]:
        """Extract location from query"""
        query_lower = query.lower().strip()
        
        for location_key, location_name in self.LOCATIONS.items():
            if location_key in query_lower:
                logger.info(f"Extracted location: {location_name}")
                return location_name
        
        return None
    
    def extract_keywords(self, query: str) -> Dict:
        """
        Extract keywords from query
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with extracted keywords
        """
        if self.use_llm:
            return self._extract_with_llm(query)
        else:
            return self._extract_rule_based(query)
    
    def _extract_with_llm(self, query: str) -> Dict:
        """Extract keywords using LLM"""
        try:
            extraction_prompt = """Bạn là hệ thống trích xuất từ khóa từ câu hỏi tìm kiếm khách sạn.
Từ câu hỏi sau, trích xuất các từ khóa quan trọng (keywords) để tìm kiếm tốt hơn.

Câu hỏi: {query}

Nhiệm vụ: Trích xuất các từ khóa quan trọng từ câu hỏi (bỏ qua các từ ngữ pháp, từ thừa).
Ví dụ:
- "Khách sạn nào có view biển đẹp ở Ngũ Hành Sơn?" → ["view biển", "Ngũ Hành Sơn"]
- "Tìm khách sạn 5 sao có hồ bơi giá rẻ" → ["5 sao", "hồ bơi", "giá rẻ"]
- "Resort sang trọng gần biển có spa" → ["resort", "sang trọng", "gần biển", "spa"]

Trả về JSON format:
{{
    "keywords": ["từ khóa 1", "từ khóa 2", ...]
}}

CHỈ trả về JSON, không có text khác."""

            prompt = extraction_prompt.format(query=query)
            
            # Call LLM
            if isinstance(self.llm, ChatOpenAI):
                from langchain.schema import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                response_text = response.content if hasattr(response, 'content') else str(response)
            elif hasattr(self.llm, 'predict'):
                response_text = self.llm.predict(prompt)
            else:
                response_text = self.llm.invoke(prompt)
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            result = json.loads(response_text)
            
            if not isinstance(result, dict) or "keywords" not in result:
                logger.warning("LLM returned invalid format, falling back to rule-based")
                return self._extract_rule_based(query)
            
            extracted_keywords_list = result.get("keywords", [])
            if not isinstance(extracted_keywords_list, list):
                extracted_keywords_list = []
            
            location = self.extract_location(query)
            
            keywords = {
                "location": location,
                "rank": None,
                "price_range": None,
                "amenities": [],
                "brand": None,
                "keywords": extracted_keywords_list
            }
            
            logger.info(f"Extracted keywords with LLM: {extracted_keywords_list}")
            return keywords
            
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}, falling back to rule-based")
            return self._extract_rule_based(query)
    
    def _extract_rule_based(self, query: str) -> Dict:
        """Extract keywords using rule-based patterns"""
        query_lower = query.lower().strip()
        keywords = {
            "location": None,
            "rank": None,
            "price_range": None,
            "amenities": [],
            "brand": None,
            "keywords": []
        }
        
        # Extract location
        keywords["location"] = self.extract_location(query)
        
        # Extract rank
        for rank, patterns in self.RANK_PATTERNS.items():
            if any(pattern in query_lower for pattern in patterns):
                keywords["rank"] = rank
                break
        
        # Extract price_range
        if any(pattern in query_lower for pattern in self.BUDGET_PATTERNS):
            keywords["price_range"] = "budget"
        elif any(pattern in query_lower for pattern in self.LUXURY_PATTERNS):
            keywords["price_range"] = "luxury"
        
        # Extract amenities
        for amenity, patterns in self.AMENITIES_MAPPING.items():
            if any(pattern in query_lower for pattern in patterns):
                keywords["amenities"].append(amenity)
        
        # Extract brand
        for brand, patterns in self.BRAND_PATTERNS.items():
            if any(pattern in query_lower for pattern in patterns):
                keywords["brand"] = brand
                break
        
        # Extract keywords
        for keyword, patterns in self.KEYWORD_PATTERNS.items():
            if any(pattern in query_lower for pattern in patterns):
                keywords["keywords"].append(keyword)
        
        if any(v for v in keywords.values() if v):
            logger.info(f"Extracted keywords (rule-based): {keywords}")
        
        return keywords
    
    def get_amenity_synonyms(self, amenity: str) -> List[str]:
        """Get synonyms for amenity"""
        return self.AMENITIES_MAPPING.get(amenity, [amenity])

