"""
Embedding Service
Unified embedding service cho cả RAG và Recommendation
Uses Ollama for embeddings (no PyTorch required)
"""

from typing import List, Union, Optional
import hashlib
from langchain_community.embeddings import OllamaEmbeddings
import requests
from ..shared import get_logger
from .persistent_cache import PersistentEmbeddingCache

logger = get_logger(__name__)


class EmbeddingService:
    """
    Unified embedding service
    Uses Ollama for embeddings (no PyTorch required)
    Used by both RAG and Recommendation systems
    """
    
    def __init__(
        self,
        provider: str = "ollama",
        model_name: str = "bge-m3",
        ollama_url: str = "http://localhost:11434",
        device: str = None,  # Not used, kept for compatibility
        cache_enabled: bool = True
    ):
        """
        Initialize embedding service
        
        Args:
            provider: 'ollama' or 'ollama_direct' (only supported providers, no PyTorch needed)
            model_name: Ollama model name (e.g., 'bge-m3')
            ollama_url: Ollama server URL
            device: Not used (kept for compatibility)
            cache_enabled: Enable caching
        """
        # Force ollama if other provider specified
        if provider not in ["ollama", "ollama_direct"]:
            logger.warning(f"Provider '{provider}' not supported. Using 'ollama' instead.")
            provider = "ollama"
        
        self.provider = provider
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.cache_enabled = cache_enabled
        self.device = device  # Not used but kept for compatibility
        
        # In-memory cache (for fast access)
        self._cache = {}
        
        # Persistent cache (disk-based)
        self._persistent_cache = PersistentEmbeddingCache(
            cache_dir=".embedding_cache",
            ttl_days=30
        ) if cache_enabled else None
        
        # Initialize model
        self._init_model()
        
        logger.info(f"✅ EmbeddingService initialized: {provider}/{model_name}")
    
    def _init_model(self):
        """Initialize embedding model (Ollama only)"""
        if self.provider == "ollama":
            self.model = OllamaEmbeddings(
                model=self.model_name,
                base_url=self.ollama_url
            )
            logger.info(f"Using Ollama embeddings: {self.model_name}")
            
        elif self.provider == "ollama_direct":
            # Direct API call (for compatibility with old code)
            self.model = None
            logger.info(f"Using Ollama direct API: {self.model_name}")
            
        else:
            raise ValueError(f"Unknown provider: {self.provider}. Only 'ollama' and 'ollama_direct' are supported.")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _check_cache(self, text: str) -> Optional[List[float]]:
        """Check cache for embedding"""
        if not self.cache_enabled:
            return None
        
        # Check in-memory cache first
        cache_key = self._get_cache_key(text)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Check persistent cache
        if self._persistent_cache:
            cached = self._persistent_cache.get(text)
            if cached is not None:
                # Store in memory cache for faster access
                self._cache[cache_key] = cached
                return cached
        
        return None
    
    def _store_cache(self, text: str, embedding: List[float]):
        """Store embedding in cache"""
        if self.cache_enabled:
            cache_key = self._get_cache_key(text)
            # Store in memory cache
            self._cache[cache_key] = embedding
            # Store in persistent cache
            if self._persistent_cache:
                self._persistent_cache.set(
                    text, 
                    embedding,
                    metadata={'model': self.model_name, 'provider': self.provider}
                )
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed single query text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Check cache
        cached = self._check_cache(text)
        if cached is not None:
            logger.debug(f"Cache hit: {text[:50]}...")
            return cached
        
        # Embed based on provider
        try:
            if self.provider == "ollama":
                embedding = self.model.embed_query(text)
                
            elif self.provider == "ollama_direct":
                embedding = self._embed_ollama_direct(text)
                
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            # Store in cache
            self._store_cache(text, embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise
    
    def embed_documents(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> List[List[float]]:
        """
        Embed multiple documents
        
        Args:
            texts: List of texts
            batch_size: Batch size for processing
            show_progress: Show progress
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)
        
        for i in range(0, total, batch_size):
            batch = texts[i:i + batch_size]
            
            if show_progress and i % (batch_size * 5) == 0:
                logger.info(f"Embedding progress: {i}/{total}")
            
            # Check cache for batch first
            texts_to_embed = []
            cached_embeddings = {}
            
            for text in batch:
                cached = self._check_cache(text)
                if cached is not None:
                    cached_embeddings[text] = cached
                else:
                    texts_to_embed.append(text)
            
            # Batch embed texts that are not cached
            if texts_to_embed:
                if self.provider == "ollama":
                    # Use batch embedding if available
                    try:
                        batch_emb = self.model.embed_documents(texts_to_embed)
                        for text, emb in zip(texts_to_embed, batch_emb):
                            cached_embeddings[text] = emb
                            # Store in cache
                            self._store_cache(text, emb)
                    except Exception as e:
                        # Fallback to individual embedding
                        logger.warning(f"Batch embedding failed, falling back to individual: {e}")
                        for text in texts_to_embed:
                            emb = self.embed_query(text)
                            cached_embeddings[text] = emb
                else:
                    # Fallback to individual embedding
                    for text in texts_to_embed:
                        emb = self.embed_query(text)
                        cached_embeddings[text] = emb
            
            # Reconstruct batch in original order
            batch_embeddings = [cached_embeddings[text] for text in batch]
            embeddings.extend(batch_embeddings)
        
        if show_progress:
            logger.info(f"✅ Embedded {total} documents")
        
        return embeddings
    
    def _embed_ollama_direct(self, text: str) -> List[float]:
        """Embed using direct Ollama API call"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            logger.error(f"Ollama direct API error: {e}")
            raise
    
    def get_vector_size(self) -> int:
        """
        Get embedding vector dimension
        
        Returns:
            Vector size
        """
        try:
            test_emb = self.embed_query("test")
            return len(test_emb)
        except Exception as e:
            logger.warning(f"Could not determine vector size: {e}")
            # Return default based on model
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
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "enabled": self.cache_enabled,
            "provider": self.provider,
            "model": self.model_name
        }

