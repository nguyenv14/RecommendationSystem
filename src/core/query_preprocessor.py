"""
Query Preprocessor
Preprocess user queries for better retrieval
"""

import re
from typing import List, Dict, Optional
from ..shared import get_logger

logger = get_logger(__name__)


class QueryPreprocessor:
    """
    Query preprocessor for RAG
    Normalizes, expands synonyms, removes stopwords
    """
    
    def __init__(self):
        """Initialize query preprocessor"""
        self.stopwords = self._load_stopwords()
        self.synonyms = self._load_synonyms()
        logger.info("✅ QueryPreprocessor initialized")
    
    def _load_stopwords(self) -> set:
        """Load Vietnamese stopwords"""
        return {
            "là", "của", "và", "có", "tại", "ở", "với", "cho", "về",
            "được", "bị", "sẽ", "đã", "đang", "mà", "nhưng", "hoặc"
            # Note: Giữ lại question words như "nào", "gì", "đâu", "sao"
        }
    
    def _load_synonyms(self) -> Dict[str, str]:
        """Load synonym mappings"""
        return {
            # Hotel abbreviations
            "ks": "khách sạn",
            "resort": "khách sạn resort",
            
            # Star ratings
            "5 sao": "năm sao",
            "4 sao": "bốn sao",
            "3 sao": "ba sao",
            
            # Locations
            "đn": "đà nẵng",
            "dn": "đà nẵng",
            "da nang": "đà nẵng",
            
            # Features
            "hồ bơi": "bể bơi",
            "pool": "bể bơi",
            "spa": "massage thư giãn",
            
            # Location descriptions
            "gần biển": "ven biển sát biển view biển",
            "ven biển": "gần biển sát biển view biển",
            "sát biển": "gần biển ven biển view biển",
        }
    
    def preprocess(self, query: str) -> str:
        """
        Preprocess query
        
        Args:
            query: Original query
            
        Returns:
            Preprocessed query
        """
        if not query or not query.strip():
            return query
        
        # Step 1: Normalize
        processed = self._normalize(query)
        
        # Step 2: Expand synonyms
        processed = self._expand_synonyms(processed)
        
        # Step 3: Remove stopwords (optional, có thể skip để giữ context)
        # processed = self._remove_stopwords(processed)
        
        logger.debug(f"Query preprocessing: '{query}' → '{processed}'")
        return processed
    
    def _normalize(self, text: str) -> str:
        """
        Normalize text
        - Lowercase
        - Remove extra whitespace
        - Unicode normalization
        """
        # Lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Trim
        text = text.strip()
        
        return text
    
    def _expand_synonyms(self, text: str) -> str:
        """
        Expand synonyms in text
        Replace abbreviations and expand synonyms
        """
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Check for exact match
            if word in self.synonyms:
                expanded_words.append(self.synonyms[word])
            else:
                expanded_words.append(word)
        
        # Also check for multi-word phrases
        text_lower = text.lower()
        for phrase, replacement in self.synonyms.items():
            if phrase in text_lower:
                # Replace phrase with expanded version
                text_lower = text_lower.replace(phrase, replacement)
        
        # Combine single word replacements and phrase replacements
        result = " ".join(expanded_words)
        
        # Apply phrase replacements
        for phrase, replacement in self.synonyms.items():
            if phrase in result:
                result = result.replace(phrase, replacement)
        
        # Clean up extra spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result if result else text
    
    def _remove_stopwords(self, text: str) -> str:
        """
        Remove stopwords from text
        Note: This is optional, may reduce context
        """
        words = text.split()
        filtered_words = [w for w in words if w not in self.stopwords]
        return " ".join(filtered_words)
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from query
        
        Args:
            query: Query text
            
        Returns:
            List of keywords
        """
        processed = self.preprocess(query)
        words = processed.split()
        
        # Filter out stopwords
        keywords = [w for w in words if w not in self.stopwords and len(w) > 2]
        
        return keywords
    
    def extract_intent(self, query: str) -> str:
        """
        Extract intent from query
        
        Args:
            query: Query text
            
        Returns:
            Intent type: 'search', 'compare', 'detail', 'price', 'location', 'other'
        """
        query_lower = query.lower()
        
        # Search intent
        if any(word in query_lower for word in ["tìm", "tìm kiếm", "khách sạn nào", "hotel nào"]):
            return "search"
        
        # Compare intent
        if any(word in query_lower for word in ["so sánh", "khác nhau", "khác biệt"]):
            return "compare"
        
        # Detail intent
        if any(word in query_lower for word in ["thông tin", "chi tiết", "giới thiệu"]):
            return "detail"
        
        # Price intent
        if any(word in query_lower for word in ["giá", "rẻ", "đắt", "giá cả", "phí"]):
            return "price"
        
        # Location intent
        if any(word in query_lower for word in ["gần", "ở", "tại", "vị trí", "địa điểm"]):
            return "location"
        
        return "other"

