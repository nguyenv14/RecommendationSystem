"""
Qdrant Manager
Centralized Qdrant client management
"""

from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    SearchRequest, CollectionInfo
)
from .logger import get_logger

logger = get_logger(__name__)


class QdrantManager:
    """
    Centralized Qdrant client manager
    Handles collection creation, deletion, and basic operations
    """
    
    def __init__(self, url: str = "http://localhost:6333"):
        """
        Initialize Qdrant manager
        
        Args:
            url: Qdrant server URL
        """
        self.url = url
        self.client = QdrantClient(url=url)
        logger.info(f"Initialized Qdrant client: {url}")
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
        recreate: bool = False
    ) -> bool:
        """
        Create collection if not exists
        
        Args:
            collection_name: Name of the collection
            vector_size: Vector dimension size
            distance: Distance metric
            recreate: Force recreate collection
            
        Returns:
            True if created or already exists
        """
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if collection_name in collection_names:
                if recreate:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.client.delete_collection(collection_name=collection_name)
                else:
                    logger.info(f"Collection already exists: {collection_name}")
                    return True
            
            logger.info(f"Creating collection: {collection_name} (size={vector_size})")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance)
            )
            logger.info(f"✅ Collection created: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"✅ Collection deleted: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if collection exists
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if exists
        """
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            return collection_name in collection_names
        except Exception as e:
            logger.error(f"Error checking collection {collection_name}: {e}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """
        Get collection information
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection info or None
        """
        try:
            return self.client.get_collection(collection_name=collection_name)
        except Exception as e:
            logger.error(f"Error getting collection info {collection_name}: {e}")
            return None
    
    def upsert_points(
        self,
        collection_name: str,
        points: List[PointStruct],
        batch_size: int = 100
    ) -> bool:
        """
        Upsert points to collection in batches
        
        Args:
            collection_name: Name of the collection
            points: List of points to upsert
            batch_size: Batch size for upsert
            
        Returns:
            True if successful
        """
        try:
            total = len(points)
            for i in range(0, total, batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch
                )
                logger.info(f"Upserted {min(i + batch_size, total)}/{total} points")
            
            logger.info(f"✅ Upserted {total} points to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error upserting points to {collection_name}: {e}")
            return False
    
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filter_conditions: Optional[Filter] = None,
        score_threshold: Optional[float] = None
    ) -> List[Any]:
        """
        Search for similar vectors
        
        Args:
            collection_name: Name of the collection
            query_vector: Query vector
            limit: Number of results
            filter_conditions: Optional filter
            score_threshold: Minimum score threshold
            
        Returns:
            List of search results
        """
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter_conditions,
                score_threshold=score_threshold
            )
            return results
        except Exception as e:
            logger.error(f"Error searching in {collection_name}: {e}")
            return []
    
    def count_points(self, collection_name: str, filter_conditions: Optional[Filter] = None) -> int:
        """
        Count points in collection
        
        Args:
            collection_name: Name of the collection
            filter_conditions: Optional filter
            
        Returns:
            Number of points
        """
        try:
            result = self.client.count(
                collection_name=collection_name,
                count_filter=filter_conditions
            )
            return result.count
        except Exception as e:
            logger.error(f"Error counting points in {collection_name}: {e}")
            return 0

