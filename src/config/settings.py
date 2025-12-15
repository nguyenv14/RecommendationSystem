"""
Application settings
Centralized configuration management
"""

import os
from functools import lru_cache
from typing import Optional
from .constants import Collections, Models, Ports


class Settings:
    """Application settings"""
    
    def __init__(self):
        # ==================== Service Configuration ====================
        self.PORT = int(os.getenv('PORT', Ports.API))
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
        
        # ==================== Qdrant Configuration ====================
        self.QDRANT_URL = os.getenv('QDRANT_URL', f'http://localhost:{Ports.QDRANT}')
        
        # RAG collections
        self.RAG_COLLECTION_HOTELS = os.getenv('RAG_COLLECTION_HOTELS', Collections.RAG_HOTELS)
        self.RAG_COLLECTION_COUPONS = os.getenv('RAG_COLLECTION_COUPONS', Collections.RAG_COUPONS)
        
        # Recommendation collections
        self.REC_COLLECTION_HOTELS = os.getenv('REC_COLLECTION_HOTELS', Collections.RECOMMENDATION_HOTELS)
        
        # Legacy support
        self.COLLECTION_NAME = os.getenv('COLLECTION_NAME', Collections.LEGACY_RAG)
        
        # ==================== Ollama Configuration ====================
        self.OLLAMA_URL = os.getenv('OLLAMA_URL', f'http://localhost:{Ports.OLLAMA}')
        self.EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', Models.EMBEDDING_BGE_M3)
        self.LLM_MODEL = os.getenv('LLM_MODEL', Models.LLM_QWEN3)
        
        # ==================== LLM Provider ====================
        # Default to lm_studio, but can be overridden by environment variable
        # Supported providers: 'lm_studio', 'ollama', 'openrouter'
        env_llm_provider = os.getenv('LLM_PROVIDER')
        self.LLM_PROVIDER = env_llm_provider if env_llm_provider else 'lm_studio'

        # LM Studio (OpenAI-compatible local server)
        env_lm_studio_url = os.getenv('LM_STUDIO_URL')
        self.LM_STUDIO_URL = env_lm_studio_url if env_lm_studio_url else 'http://localhost:1234'

        # OpenRouter configuration (for cloud models like qwen/qwen2.5-vl-72b-instruct)
        # IMPORTANT: set these only via environment variables, never hard-code API keys.
        self.OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
        self.OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'qwen/qwen2.5-vl-72b-instruct')
        self.OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api')

        # Debug: Log LLM provider configuration at initialization (without exposing secrets)
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            "📋 LLM Configuration loaded: "
            f"provider='{self.LLM_PROVIDER}' (env: {env_llm_provider}), "
            f"lm_studio_url='{self.LM_STUDIO_URL}' (env: {env_lm_studio_url}), "
            f"openrouter_model='{self.OPENROUTER_MODEL}', "
            f"openrouter_base='{self.OPENROUTER_BASE_URL}'"
        )
        
        # ==================== Redis Configuration ====================
        self.REDIS_URL = os.getenv('REDIS_URL', f'redis://localhost:{Ports.REDIS}')
        self.REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
        
        # ==================== MySQL Configuration ====================
        self.MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
        self.MYSQL_PORT = int(os.getenv('MYSQL_PORT', Ports.MYSQL))
        self.MYSQL_USER = os.getenv('MYSQL_USER', 'root')
        self.MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
        self.MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'myhotel')
        
        # ==================== RAG Configuration ====================
        self.AUTO_INDEX_COUPONS = os.getenv('AUTO_INDEX_COUPONS', 'true').lower() == 'true'
        self.RAG_TOP_K = int(os.getenv('RAG_TOP_K', 5))
        self.RAG_CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', 1000))
        self.RAG_CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', 200))
        
        # ==================== Recommendation Configuration ====================
        self.REC_TOP_K = int(os.getenv('REC_TOP_K', 10))
        self.REC_USE_OLLAMA = os.getenv('REC_USE_OLLAMA', 'true').lower() == 'true'
        
        # ==================== Performance Configuration ====================
        self.EMBEDDING_CACHE_ENABLED = os.getenv('EMBEDDING_CACHE_ENABLED', 'true').lower() == 'true'
        self.MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
        
    def get_mysql_connection_string(self) -> str:
        """Get MySQL connection string"""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    def __repr__(self) -> str:
        """String representation (safe, without sensitive data)"""
        return f"Settings(host={self.HOST}, port={self.PORT}, debug={self.DEBUG})"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

