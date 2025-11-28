"""
Embedding Manager
Centralized embedding management with caching
Uses Ollama for embeddings (no PyTorch required)
"""

import hashlib
from typing import List, Union, Optional, Dict
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.embeddings import Embeddings
import requests
from .logger import get_logger

logger = get_logger(__name__)


class EmbeddingManager:
    """
    Centralized embedding manager with caching
    Uses Ollama for embeddings (no PyTorch required)
    """
    
    def __init__(
        self,
        provider: str = "ollama",
        model_name: str = "bge-m3",
        ollama_url: str = "http://localhost:11434",
        cache_enabled: bool = True,
        device: str = "cpu"  # Not used, kept for compatibility
    ):
        """
        Initialize embedding manager
        
        Args:
            provider: 'ollama' (only supported provider, no PyTorch needed)
            model_name: Ollama model name (e.g., 'bge-m3')
            ollama_url: Ollama server URL
            cache_enabled: Enable caching
            device: Not used (kept for compatibility)
        """
        if provider != "ollama":
            logger.warning(f"Provider '{provider}' not supported. Using 'ollama' instead.")
            provider = "ollama"
        
        self.provider = "ollama"  # Force ollama
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.cache_enabled = cache_enabled
        self.device = device  # Not used but kept for compatibility
        
        # Cache
        self._cache: Dict[str, List[float]] = {}
        
        # Initialize model
        self._init_model()
        
        logger.info(f"Initialized EmbeddingManager: ollama - {model_name}")
    
    def _init_model(self):
        """Initialize embedding model (Ollama only)"""
        try:
            self.model = OllamaEmbeddings(
                model=self.model_name,
                base_url=self.ollama_url
            )
            logger.info(f"✅ Ollama embeddings initialized: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing Ollama embeddings: {e}")
            raise
    
    def _get_cache_key(self, text: str) -> str:
        """Get cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed single query text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if self.cache_enabled:
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                logger.debug(f"Cache hit for: {text[:50]}...")
                return self._cache[cache_key]
        
        try:
            # Only Ollama is supported
            embedding = self.model.embed_query(text)
            
            if self.cache_enabled:
                cache_key = self._get_cache_key(text)
                self._cache[cache_key] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise
    
    def embed_documents(self, texts: List[str], show_progress: bool = True) -> List[List[float]]:
        """
        Embed multiple documents
        
        Args:
            texts: List of texts to embed
            show_progress: Show progress bar
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)
        
        for idx, text in enumerate(texts):
            if show_progress and idx % 10 == 0:
                logger.info(f"Embedding progress: {idx}/{total}")
            
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        
        if show_progress:
            logger.info(f"✅ Embedded {total} documents")
        
        return embeddings
    
    def get_vector_size(self) -> int:
        """
        Get embedding vector size
        
        Returns:
            Vector dimension
        """
        try:
            test_embedding = self.embed_query("test")
            return len(test_embedding)
        except Exception as e:
            logger.error(f"Error getting vector size: {e}")
            # Default sizes
            if "bge-m3" in self.model_name.lower():
                return 1024
            elif "minilm" in self.model_name.lower():
                return 384
            else:
                return 768
    
    def clear_cache(self):
        """Clear embedding cache"""
        self._cache.clear()
        logger.info("Embedding cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of cached embeddings"""
        return len(self._cache)

