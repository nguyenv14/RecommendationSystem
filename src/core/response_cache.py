"""
Response Cache
Cache RAG responses for faster retrieval
"""

import hashlib
import time
import json
from typing import Dict, Optional, Any
from functools import lru_cache
from ..shared import get_logger

logger = get_logger(__name__)


class ResponseCache:
    """
    Response cache for RAG
    Caches query-answer pairs with TTL
    """
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        """
        Initialize response cache
        
        Args:
            ttl: Time-to-live in seconds (default: 1 hour)
            max_size: Maximum cache size (LRU eviction)
        """
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"✅ ResponseCache initialized (TTL={ttl}s, max_size={max_size})")
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key from query"""
        # Normalize query for consistent hashing
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response
        
        Args:
            query: User query
            
        Returns:
            Cached response or None
        """
        cache_key = self._get_cache_key(query)
        
        if cache_key not in self._cache:
            return None
        
        entry = self._cache[cache_key]
        
        # Check TTL
        if time.time() - entry['timestamp'] > self.ttl:
            # Expired, remove from cache
            del self._cache[cache_key]
            logger.debug(f"Cache expired for query: '{query[:50]}...'")
            return None
        
        logger.debug(f"Cache hit for query: '{query[:50]}...'")
        return entry['response']
    
    def set(self, query: str, response: Dict[str, Any]):
        """
        Cache response
        
        Args:
            query: User query
            response: Response dict
        """
        cache_key = self._get_cache_key(query)
        
        # LRU eviction if cache is full
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k]['timestamp']
            )
            del self._cache[oldest_key]
            logger.debug(f"Cache evicted oldest entry (max_size={self.max_size})")
        
        self._cache[cache_key] = {
            'response': response,
            'timestamp': time.time(),
            'query': query
        }
        
        logger.debug(f"Cached response for query: '{query[:50]}...'")
    
    def clear(self):
        """Clear all cached responses"""
        self._cache.clear()
        logger.info("Response cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = time.time()
        expired_count = sum(
            1 for entry in self._cache.values()
            if now - entry['timestamp'] > self.ttl
        )
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'ttl': self.ttl,
            'expired_entries': expired_count,
            'hit_rate': 0.0  # Would need to track hits/misses
        }
    
    def cleanup_expired(self):
        """Remove expired entries from cache"""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now - entry['timestamp'] > self.ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

