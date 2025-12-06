"""
Persistent Cache
Disk-based persistent cache for embeddings
"""

import os
import pickle
import hashlib
import time
from typing import Optional, List, Dict, Any
from pathlib import Path
from ..shared import get_logger

logger = get_logger(__name__)


class PersistentEmbeddingCache:
    """
    Persistent embedding cache using disk storage
    Each embedding is stored as a pickle file
    """
    
    def __init__(self, cache_dir: str = ".embedding_cache", ttl_days: int = 30):
        """
        Initialize persistent cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_days: Time-to-live in days (default: 30 days)
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_days * 24 * 60 * 60
        
        # Create cache directory if not exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ PersistentEmbeddingCache initialized (dir={cache_dir}, TTL={ttl_days} days)")
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, text: str) -> Optional[List[float]]:
        """
        Get cached embedding
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Cached embedding or None
        """
        cache_key = self._get_cache_key(text)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            # Check file age
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age > self.ttl_seconds:
                # Expired, delete file
                cache_file.unlink()
                logger.debug(f"Cache expired for key: {cache_key[:8]}...")
                return None
            
            # Load from file
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
                
            # Validate data structure
            if isinstance(data, dict) and 'embedding' in data:
                embedding = data['embedding']
                logger.debug(f"Cache hit for key: {cache_key[:8]}...")
                return embedding
            elif isinstance(data, list):
                # Legacy format (just embedding list)
                logger.debug(f"Cache hit (legacy format) for key: {cache_key[:8]}...")
                return data
            else:
                logger.warning(f"Invalid cache data format for key: {cache_key[:8]}...")
                return None
                
        except Exception as e:
            logger.error(f"Error reading cache file {cache_file}: {e}")
            # Delete corrupted file
            try:
                cache_file.unlink()
            except:
                pass
            return None
    
    def set(self, text: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None):
        """
        Cache embedding
        
        Args:
            text: Text that was embedded
            embedding: Embedding vector
            metadata: Optional metadata (model_name, timestamp, etc.)
        """
        cache_key = self._get_cache_key(text)
        cache_file = self._get_cache_file(cache_key)
        
        try:
            # Prepare data
            data = {
                'embedding': embedding,
                'text': text,  # Store original text for debugging
                'timestamp': time.time(),
                'metadata': metadata or {}
            }
            
            # Write to file
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"Cached embedding for key: {cache_key[:8]}...")
            
        except Exception as e:
            logger.error(f"Error writing cache file {cache_file}: {e}")
    
    def clear(self):
        """Clear all cached embeddings"""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            logger.info(f"Cleared all cache files in {self.cache_dir}")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache files
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        now = time.time()
        
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                file_age = now - cache_file.stat().st_mtime
                if file_age > self.ttl_seconds:
                    cache_file.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} expired cache files")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired cache: {e}")
            return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob("*.pkl"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            # Count expired files
            now = time.time()
            expired_count = sum(
                1 for f in cache_files
                if now - f.stat().st_mtime > self.ttl_seconds
            )
            
            return {
                'total_files': len(cache_files),
                'total_size_mb': total_size / (1024 * 1024),
                'expired_files': expired_count,
                'cache_dir': str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'expired_files': 0,
                'cache_dir': str(self.cache_dir)
            }

