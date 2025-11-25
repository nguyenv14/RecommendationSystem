#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cached Embeddings Wrapper

Wrapper for OllamaEmbeddings with caching to optimize performance.
"""

import hashlib
import logging
from typing import List

from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)


class CachedOllamaEmbeddings(Embeddings):
    """
    Wrapper cho OllamaEmbeddings với cache để tối ưu performance
    Inherit từ Embeddings base class để tương thích với LangChain
    """
    def __init__(self, embeddings: OllamaEmbeddings, cache_enabled: bool = True):
        """
        Initialize cached embeddings wrapper
        
        Args:
            embeddings: OllamaEmbeddings instance
            cache_enabled: Enable caching
        """
        super().__init__()
        self.embeddings = embeddings
        self._embedding_cache = {}
        self._cache_enabled = cache_enabled
    
    def embed_query(self, text: str) -> List[float]:
        """Embed query với cache"""
        if not self._cache_enabled:
            return self.embeddings.embed_query(text)
        
        # Tạo cache key từ text
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache
        if cache_key in self._embedding_cache:
            logger.debug(f"Embedding cache hit for: {text[:50]}...")
            return self._embedding_cache[cache_key]
        
        # Cache miss - embed và cache
        logger.debug(f"Embedding cache miss for: {text[:50]}...")
        embedding = self.embeddings.embed_query(text)
        self._embedding_cache[cache_key] = embedding
        return embedding
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents với cache để tối ưu performance"""
        if not self._cache_enabled:
            return self.embeddings.embed_documents(texts)
        
        # Check cache for each text và build result
        result = []
        texts_to_embed = []
        indices_to_embed = []
        
        for idx, text in enumerate(texts):
            cache_key = hashlib.md5(text.encode()).hexdigest()
            if cache_key in self._embedding_cache:
                # Use cached embedding
                result.append(self._embedding_cache[cache_key])
            else:
                # Need to embed this text
                result.append(None)  # Placeholder
                texts_to_embed.append(text)
                indices_to_embed.append(idx)
        
        # Embed texts that are not in cache
        if texts_to_embed:
            new_embeddings = self.embeddings.embed_documents(texts_to_embed)
            # Cache new embeddings and update result
            for i, (text, embedding) in enumerate(zip(texts_to_embed, new_embeddings)):
                cache_key = hashlib.md5(text.encode()).hexdigest()
                self._embedding_cache[cache_key] = embedding
                # Update result at correct index
                result[indices_to_embed[i]] = embedding
        
        return result
    
    # Delegate các methods khác từ base embeddings
    def __getattr__(self, name):
        """Delegate unknown attributes to base embeddings"""
        return getattr(self.embeddings, name)

