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
    
    # Intent patterns for detailed extraction
    INTENT_PATTERNS = {
        "price": [
            r"giá\s+tốt", r"giá\s+rẻ", r"giá\s+hợp\s+lý",
            r"giá\s+phải\s+chăng", r"giá\s+thấp", r"giá\s+cao"
        ],
        "location": [
            r"ở\s+([A-Za-zÀ-ỹ\s]+)", r"tại\s+([A-Za-zÀ-ỹ\s]+)",
            r"khu\s+vực\s+([A-Za-zÀ-ỹ\s]+)", r"quận\s+([A-Za-zÀ-ỹ\s]+)"
        ],
        "amenities": [
            r"hồ\s+bơi", r"spa", r"gym", r"nhà\s+hàng",
            r"view\s+biển", r"view\s+sông"
        ],
        "rank": [
            r"(\d+)\s+sao", r"(\d+)\s+star"
        ]
    }
    
    # Area mapping (based on common area names in Đà Nẵng)
    AREA_MAPPING = {
        "ngũ hành sơn": 7,
        "sơn trà": 1,
        "hải châu": 2,
        "liên chiểu": 3,
        "thanh khê": 4,
        "cẩm lệ": 5,
        "hòa vang": 6,
    }
    
    def process(self, query: str) -> Dict:
        """
        Process query và extract intent, entities, filters
        Enhanced version for semantic search
        
        Args:
            query: Original query
            
        Returns:
            Dictionary with processed query information
        """
        query_lower = query.lower()
        
        # Extract detailed intent
        intent = self._extract_detailed_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Extract area
        area_id = self._extract_area(query_lower)
        
        return {
            "original_query": query,
            "intent": intent,
            "entities": entities,
            "area_id": area_id,
            "filters": self._build_filters(intent, entities, area_id)
        }
    
    def _extract_detailed_intent(self, query: str) -> Dict:
        """Extract detailed user intent"""
        intent = {
            "type": "search",  # default
            "price_range": None,
            "amenities": [],
            "rank": None
        }
        
        # Check price intent
        if any(re.search(pattern, query) for pattern in self.INTENT_PATTERNS["price"]):
            if "giá tốt" in query or "giá rẻ" in query or "giá hợp lý" in query:
                intent["price_range"] = "low"
            elif "giá cao" in query:
                intent["price_range"] = "high"
        
        # Check amenities
        for amenity_pattern in self.INTENT_PATTERNS["amenities"]:
            if re.search(amenity_pattern, query):
                intent["amenities"].append(amenity_pattern.replace(r"\s+", " "))
        
        # Check rank
        rank_match = re.search(r"(\d+)\s+sao", query)
        if rank_match:
            intent["rank"] = int(rank_match.group(1))
        
        return intent
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entities từ query"""
        entities = []
        
        # Extract location entities
        location_match = re.search(r"ở\s+([A-Za-zÀ-ỹ\s]+)", query)
        if location_match:
            entities.append(location_match.group(1).strip())
        
        return entities
    
    def _extract_area(self, query: str) -> Optional[int]:
        """Extract area_id từ query"""
        query_lower = query.lower()
        
        # Normalize query: remove accents and special chars for better matching
        import unicodedata
        query_normalized = unicodedata.normalize('NFD', query_lower)
        query_normalized = ''.join(c for c in query_normalized if unicodedata.category(c) != 'Mn')
        
        # Try exact match first
        for area_name, area_id in self.AREA_MAPPING.items():
            if area_name in query_lower:
                return area_id
        
        # Try normalized match
        for area_name, area_id in self.AREA_MAPPING.items():
            area_normalized = unicodedata.normalize('NFD', area_name)
            area_normalized = ''.join(c for c in area_normalized if unicodedata.category(c) != 'Mn')
            if area_normalized in query_normalized:
                return area_id
        
        # Try partial match (e.g., "ngu hanh son" matches "ngũ hành sơn")
        for area_name, area_id in self.AREA_MAPPING.items():
            area_words = area_name.split()
            if all(word in query_lower for word in area_words):
                return area_id
        
        return None
    
    def _build_filters(self, intent: Dict, entities: List, area_id: Optional[int]) -> Dict:
        """Build filter dict từ intent và entities"""
        filters = {}
        
        if area_id:
            filters["area_id"] = area_id
        
        if intent.get("price_range") == "low":
            filters["max_price"] = 2000000  # Default max price for "giá tốt"
        
        if intent.get("rank"):
            filters["min_rank"] = intent["rank"]
        
        return filters

