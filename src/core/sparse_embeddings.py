"""
Sparse Embedding Service
BM25-based sparse embeddings for keyword search
Uses fastembed for fast sparse vector generation
"""

from typing import List, Dict, Optional, Union
import hashlib
import os
# Lazy import - import only when needed to allow unsetting HF_HUB_OFFLINE first
# from fastembed import SparseTextEmbedding, SparseEmbedding
from ..shared import get_logger
from .persistent_cache import PersistentEmbeddingCache

logger = get_logger(__name__)


class SparseEmbeddingService:
    """
    Sparse embedding service using BM25
    Used for keyword-based search (exact matches, hotel names, voucher codes)
    """
    
    def __init__(
        self,
        model_name: str = "Qdrant/bm25",
        cache_enabled: bool = True,
        cache_dir: Optional[str] = None,
        allow_download: bool = True
    ):
        """
        Initialize sparse embedding service
        
        Args:
            model_name: FastEmbed sparse model name (default: Qdrant/bm25)
            cache_enabled: Enable caching
            cache_dir: Cache directory path
            allow_download: Allow downloading model if not available (temporarily unset HF_HUB_OFFLINE)
        """
        self.model_name = model_name
        self.cache_enabled = cache_enabled
        self.cache_dir = cache_dir
        self.model = None
        self.is_available = False
        
        # Initialize model
        try:
            logger.info(f"Loading sparse embedding model: {model_name}")
            
            # IMPORTANT: Unset HF_HUB_OFFLINE BEFORE importing fastembed
            # fastembed checks this env var when the module is imported
            original_offline = None
            if allow_download:
                original_offline = os.environ.get('HF_HUB_OFFLINE')
                if original_offline:
                    logger.info("Temporarily unsetting HF_HUB_OFFLINE to allow model download...")
                    del os.environ['HF_HUB_OFFLINE']
                    # Also unset in parent process if possible
                    if 'HF_HUB_OFFLINE' in os.environ:
                        del os.environ['HF_HUB_OFFLINE']
            
            # Lazy import - import only now, after unsetting HF_HUB_OFFLINE
            try:
                from fastembed import SparseTextEmbedding, SparseEmbedding
            except ImportError as e:
                logger.error(f"fastembed not installed: {e}")
                logger.error("Install with: pip install fastembed")
                raise
            
            try:
                self.model = SparseTextEmbedding(model_name=model_name)
                self.is_available = True
                logger.info(f"✅ SparseEmbeddingService initialized with {model_name}")
            finally:
                # Restore original HF_HUB_OFFLINE value
                if original_offline is not None:
                    os.environ['HF_HUB_OFFLINE'] = original_offline
                    logger.debug(f"Restored HF_HUB_OFFLINE={original_offline}")
                    
        except Exception as e:
            logger.warning(f"⚠️  Failed to load sparse embedding model: {e}")
            logger.warning("   Hybrid search will fallback to semantic search only")
            logger.warning("   To enable hybrid search:")
            logger.warning("   1. Run: python download_bm25_model.py")
            logger.warning("   2. Or unset HF_HUB_OFFLINE: export HF_HUB_OFFLINE=0")
            self.model = None
            self.is_available = False
            # Don't raise - allow graceful fallback
        
        # Initialize cache if enabled
        self.cache = None
        if cache_enabled:
            cache_path = cache_dir or ".embedding_cache/sparse"
            self.cache = PersistentEmbeddingCache(cache_path)
            logger.info(f"Sparse embedding cache enabled: {cache_path}")
    
    def embed_query(self, text: str) -> Dict[str, float]:
        """
        Generate sparse embedding (BM25) for query text
        
        Args:
            text: Query text
            
        Returns:
            Dictionary mapping token indices to weights (sparse vector)
            Returns empty dict if model not available
        """
        if not self.is_available or self.model is None:
            logger.debug("Sparse embedding model not available, returning empty dict")
            return {}
        
        if not text or not text.strip():
            return {}
        
        # Check cache
        if self.cache:
            cache_key = self._get_cache_key(text)
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            # Import here if not already imported
            from fastembed import SparseEmbedding
            
            # Generate sparse embedding
            # fastembed returns list of SparseEmbedding, we take the first one
            embeddings: List[SparseEmbedding] = list(self.model.embed([text]))
            
            if not embeddings:
                return {}
            
            emb = embeddings[0]
            # Convert to dict format: {token_index: weight}
            # SparseEmbedding has indices and values attributes
            if hasattr(emb, 'as_dict'):
                sparse_vector = emb.as_dict()
            elif hasattr(emb, 'indices') and hasattr(emb, 'values'):
                sparse_vector = {str(emb.indices[i]): float(emb.values[i]) 
                               for i in range(len(emb.indices))}
            else:
                # Try to convert directly
                sparse_vector = dict(emb) if hasattr(emb, '__iter__') else {}
            
            # Cache result
            if self.cache:
                self.cache.set(cache_key, sparse_vector)
            
            return sparse_vector
            
        except Exception as e:
            logger.error(f"Error generating sparse embedding: {e}")
            return {}
    
    def embed_documents(self, texts: List[str], batch_size: int = 32) -> List[Dict[str, float]]:
        """
        Generate sparse embeddings for multiple documents
        
        Args:
            texts: List of document texts
            batch_size: Batch size for processing
            
        Returns:
            List of sparse vectors (dicts)
            Returns list of empty dicts if model not available
        """
        if not self.is_available or self.model is None:
            logger.debug("Sparse embedding model not available, returning empty dicts")
            return [{}] * len(texts) if texts else []
        
        if not texts:
            return []
        
        results = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Generate embeddings
                embeddings: List[SparseEmbedding] = list(self.model.embed(batch))
                
                # Convert to dict format
                for emb in embeddings:
                    if hasattr(emb, 'as_dict'):
                        sparse_vector = emb.as_dict()
                    elif hasattr(emb, 'indices') and hasattr(emb, 'values'):
                        sparse_vector = {str(emb.indices[j]): float(emb.values[j]) 
                                       for j in range(len(emb.indices))}
                    else:
                        sparse_vector = dict(emb) if hasattr(emb, '__iter__') else {}
                    results.append(sparse_vector)
                    
            except Exception as e:
                logger.error(f"Error generating sparse embeddings for batch {i}: {e}")
                # Add empty dicts for failed batch
                results.extend([{}] * len(batch))
        
        return results
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(f"sparse_{self.model_name}_{text}".encode()).hexdigest()
    
    def clear_cache(self):
        """Clear embedding cache"""
        if self.cache:
            self.cache.clear()
            logger.info("Sparse embedding cache cleared")

