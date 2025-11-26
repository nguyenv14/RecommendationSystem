"""
Constants for the application
"""

class Collections:
    """Qdrant collection names"""
    # RAG collections
    RAG_HOTELS = "hotels_rag"
    RAG_COUPONS = "coupons_rag"
    
    # Recommendation collections
    RECOMMENDATION_HOTELS = "hotels_recommendation"
    RECOMMENDATION_SEMANTIC = "hotels_semantic"
    
    # Legacy collections (for backward compatibility)
    LEGACY_RAG = "hotels"
    LEGACY_RECOMMENDATION = "hotel_recommendations"


class Models:
    """Model names"""
    # Embedding models
    EMBEDDING_BGE_M3 = "bge-m3"
    EMBEDDING_PARAPHRASE = "paraphrase-multilingual-MiniLM-L12-v2"
    
    # LLM models
    LLM_QWEN3 = "qwen3"
    LLM_GEMMA = "google/gemma-3n-e4b"
    LLM_MISTRAL = "mistral"


class Ports:
    """Default ports"""
    API = 5000
    QDRANT = 6333
    QDRANT_GRPC = 6334
    OLLAMA = 11434
    MYSQL = 3308
    REDIS = 6380
    PHPMYADMIN = 8181


class DocumentTypes:
    """Document types for metadata filtering"""
    HOTEL = "hotel"
    ROOM = "room"
    COUPON = "coupon"
    RESTAURANT = "restaurant"


class SourceSystems:
    """Source system identifiers"""
    RAG = "rag"
    RECOMMENDATION = "recommendation"
    HYBRID = "hybrid"

