"""
VectorStore Service
Unified Qdrant operations cho cả RAG và Recommendation
"""

from typing import List, Dict, Optional, Any, Tuple, Union
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, SparseVectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    SearchRequest, ScoredPoint, Prefetch, SparseVector
)
from ..shared import get_logger
from ..config import Collections

logger = get_logger(__name__)


class VectorStoreService:
    """
    Unified vector store service using Qdrant
    Used by both RAG and Recommendation systems
    """
    
    def __init__(
        self,
        url: str = "http://localhost:6333",
        default_collection: Optional[str] = None
    ):
        """
        Initialize vector store service
        
        Args:
            url: Qdrant server URL
            default_collection: Default collection name
        """
        self.url = url
        self.client = QdrantClient(url=url)
        self.default_collection = default_collection
        
        logger.info(f"✅ VectorStoreService initialized: {url}")
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE,
        recreate: bool = False,
        enable_sparse: bool = True
    ) -> bool:
        """
        Create or recreate collection with optional sparse vectors support
        
        Args:
            collection_name: Collection name
            vector_size: Vector dimension
            distance: Distance metric
            recreate: Force recreate if exists
            enable_sparse: Enable sparse vectors (BM25) for hybrid search
            
        Returns:
            True if successful
        """
        try:
            existing = self.list_collections()
            
            if collection_name in existing:
                if recreate:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.client.delete_collection(collection_name)
                else:
                    logger.info(f"Collection already exists: {collection_name}")
                    return True
            
            # Build vectors config
            if enable_sparse:
                logger.info(f"Creating collection with hybrid search: {collection_name} (dense={vector_size}, sparse=BM25)")
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "dense": VectorParams(size=vector_size, distance=distance)
                    },
                    sparse_vectors_config={
                        "sparse": SparseVectorParams()  # BM25 sparse vector
                    }
                )
            else:
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
    
    def list_collections(self) -> List[str]:
        """
        List all collections
        
        Returns:
            List of collection names
        """
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        return collection_name in self.list_collections()
    
    def get_collection_info(self, collection_name: str) -> Optional[Any]:
        """
        Get collection information
        
        Args:
            collection_name: Collection name
            
        Returns:
            Collection info or None
        """
        try:
            return self.client.get_collection(collection_name)
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None
    
    def upsert_points(
        self,
        collection_name: str,
        points: List[PointStruct],
        batch_size: int = 100
    ) -> bool:
        """
        Upsert points to collection
        
        Args:
            collection_name: Collection name
            points: List of points
            batch_size: Batch size
            
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
                logger.debug(f"Upserted {min(i + batch_size, total)}/{total} points")
            
            logger.info(f"✅ Upserted {total} points to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting points: {e}")
            return False
    
    def search(
        self,
        query_vector: List[float],
        collection_name: Optional[str] = None,
        limit: int = 10,
        filters: Optional[Filter] = None,
        score_threshold: Optional[float] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
        query_sparse_vector: Optional[Dict[str, float]] = None,
        prefetch_limit: Optional[int] = None
    ) -> List[ScoredPoint]:
        """
        Search for similar vectors (supports hybrid search with sparse vectors)
        
        Args:
            query_vector: Dense query embedding vector
            collection_name: Collection to search (uses default if None)
            limit: Number of results
            filters: Optional filters
            score_threshold: Minimum score
            with_payload: Include payload in results
            with_vectors: Include vectors in results
            query_sparse_vector: Optional sparse vector (BM25) for hybrid search
            prefetch_limit: Limit for prefetch in hybrid search (default: limit * 2)
            
        Returns:
            List of scored points
        """
        if collection_name is None:
            collection_name = self.default_collection
            
        if collection_name is None:
            raise ValueError("No collection specified and no default collection set")
        
        try:
            # Hybrid search with prefetch
            if query_sparse_vector:
                prefetch_limit = prefetch_limit or (limit * 2)
                sparse_vec = SparseVector(**query_sparse_vector)
                
                prefetch = [
                    Prefetch(
                        query=query_vector,
                        using="dense",
                        limit=prefetch_limit,
                    ),
                    Prefetch(
                        query=sparse_vec,
                        using="sparse",
                        limit=prefetch_limit,
                    ),
                ]
                
                results = self.client.query_points(
                    collection_name=collection_name,
                    prefetch=prefetch,
                    query_filter=filters,
                    limit=limit,
                    score_threshold=score_threshold,
                    with_payload=with_payload,
                    with_vectors=with_vectors
                )
            else:
                # Standard dense vector search
                results = self.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit,
                    query_filter=filters,
                    score_threshold=score_threshold,
                    with_payload=with_payload,
                    with_vectors=with_vectors
                )
            
            logger.debug(f"Search returned {len(results)} results from {collection_name}")
            return results
            
        except AttributeError as e:
            logger.error(f"Attribute error searching in {collection_name}: {e}")
            logger.error(f"Client type: {type(self.client)}, Client: {self.client}")
            # Log available methods for debugging
            available_methods = [m for m in dir(self.client) if not m.startswith('_') and callable(getattr(self.client, m, None))]
            logger.error(f"Available QdrantClient methods: {available_methods[:20]}")
            return []
        except Exception as e:
            logger.error(f"Error searching in {collection_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def search_groups(
        self,
        query_vector: List[float],
        collection_name: Optional[str] = None,
        group_by: str = "hotel_id",
        limit: int = 10,
        group_size: int = 1,
        filters: Optional[Filter] = None,
        score_threshold: Optional[float] = None,
        query_sparse_vector: Optional[Dict[str, Any]] = None,
        with_payload: bool = True,
        with_vectors: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search with grouping by a field (e.g., hotel_id)
        This ensures diverse results - each group (hotel) only appears once
        
        Args:
            query_vector: Query vector
            collection_name: Collection to search
            group_by: Field name to group by (e.g., "hotel_id")
            limit: Number of groups to return
            group_size: Number of results per group (default: 1 - best match only)
            filters: Optional filters
            score_threshold: Minimum score
            query_sparse_vector: Optional sparse vector for hybrid search
            with_payload: Include payload in results
            with_vectors: Include vectors in results
            
        Returns:
            List of groups, each containing the best matches for that group
        """
        if collection_name is None:
            collection_name = self.default_collection
        
        if collection_name is None:
            raise ValueError("No collection specified and no default collection set")
        
        try:
            # Check if Qdrant client supports search_groups (requires Qdrant 1.7+)
            if not hasattr(self.client, 'search_groups'):
                logger.warning("Qdrant client does not support search_groups, falling back to regular search")
                # Fallback to regular search
                results = self.search(
                    query_vector=query_vector,
                    collection_name=collection_name,
                    limit=limit * group_size,  # Get more to manually group
                    filters=filters,
                    score_threshold=score_threshold,
                    query_sparse_vector=query_sparse_vector,
                    with_payload=with_payload,
                    with_vectors=with_vectors
                )
                # Manual grouping fallback
                return self._manual_group_results(results, group_by, limit, group_size)
            
            # Use Qdrant native grouping
            if query_sparse_vector:
                # Hybrid search with grouping
                from qdrant_client.models import SparseVector
                sparse_vec = SparseVector(**query_sparse_vector)
                
                groups = self.client.search_groups(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    query_sparse_vector=sparse_vec,
                    group_by=group_by,
                    limit=limit,
                    group_size=group_size,
                    query_filter=filters,
                    score_threshold=score_threshold,
                    with_payload=with_payload,
                    with_vectors=with_vectors
                )
            else:
                # Dense vector search with grouping
                groups = self.client.search_groups(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    group_by=group_by,
                    limit=limit,
                    group_size=group_size,
                    query_filter=filters,
                    score_threshold=score_threshold,
                    with_payload=with_payload,
                    with_vectors=with_vectors
                )
            
            # Format results
            formatted_groups = []
            for group in groups.groups:
                if group.hits:
                    # Get best hit from this group
                    best_hit = group.hits[0]
                    formatted_groups.append({
                        "id": best_hit.id,
                        "score": best_hit.score,
                        "payload": best_hit.payload if with_payload else {},
                        "group_id": group.id,  # The value of group_by field (e.g., hotel_id)
                        "group_size": len(group.hits)
                    })
            
            logger.info(f"Search groups returned {len(formatted_groups)} groups from {collection_name} (grouped by {group_by})")
            return formatted_groups
            
        except Exception as e:
            logger.error(f"Error in search_groups for {collection_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback to regular search
            logger.warning("Falling back to regular search due to grouping error")
            results = self.search(
                query_vector=query_vector,
                collection_name=collection_name,
                limit=limit * group_size,
                filters=filters,
                score_threshold=score_threshold,
                query_sparse_vector=query_sparse_vector,
                with_payload=with_payload,
                with_vectors=with_vectors
            )
            return self._manual_group_results(results, group_by, limit, group_size)
    
    def _manual_group_results(
        self,
        results: List[ScoredPoint],
        group_by: str,
        limit: int,
        group_size: int
    ) -> List[Dict[str, Any]]:
        """
        Manual grouping fallback when Qdrant grouping is not available
        """
        groups_map = {}  # group_id -> list of results
        
        for result in results:
            group_id = result.payload.get(group_by) if result.payload else None
            if group_id is None:
                continue
            
            if group_id not in groups_map:
                groups_map[group_id] = []
            groups_map[group_id].append(result)
        
        # Sort each group by score and take top group_size
        formatted_groups = []
        for group_id, group_results in list(groups_map.items())[:limit]:
            group_results.sort(key=lambda x: x.score, reverse=True)
            best_hit = group_results[0]
            formatted_groups.append({
                "id": best_hit.id,
                "score": best_hit.score,
                "payload": best_hit.payload or {},
                "group_id": group_id,
                "group_size": len(group_results)
            })
        
        return formatted_groups
    
    def search_by_text(
        self,
        query_text: str,
        embedding_service,  # EmbeddingService instance
        collection_name: Optional[str] = None,
        limit: int = 10,
        filters: Optional[Filter] = None,
        score_threshold: Optional[float] = None
    ) -> List[ScoredPoint]:
        """
        Search by text query (convenience method)
        
        Args:
            query_text: Text query
            embedding_service: EmbeddingService to embed query
            collection_name: Collection to search
            limit: Number of results
            filters: Optional filters
            score_threshold: Minimum score
            
        Returns:
            List of scored points
        """
        # Embed query
        query_vector = embedding_service.embed_query(query_text)
        
        # Search
        return self.search(
            query_vector=query_vector,
            collection_name=collection_name,
            limit=limit,
            filters=filters,
            score_threshold=score_threshold
        )
    
    def count_points(
        self,
        collection_name: Optional[str] = None,
        filters: Optional[Filter] = None
    ) -> int:
        """
        Count points in collection
        
        Args:
            collection_name: Collection name
            filters: Optional filters
            
        Returns:
            Number of points
        """
        if collection_name is None:
            collection_name = self.default_collection
            
        try:
            result = self.client.count(
                collection_name=collection_name,
                count_filter=filters
            )
            return result.count
        except Exception as e:
            logger.error(f"Error counting points: {e}")
            return 0
    
    def get_point(
        self,
        collection_name: str,
        point_id: Union[str, int],
        with_vectors: bool = False
    ) -> Optional[Any]:
        """
        Get single point by ID
        
        Args:
            collection_name: Collection name
            point_id: Point ID (can be string or int)
            with_vectors: Whether to include vectors in response
            
        Returns:
            Point or None
        """
        # Normalize point_id: Qdrant accepts unsigned integers or UUIDs
        # Convert numeric strings to int for better compatibility
        normalized_id = point_id
        if isinstance(point_id, str):
            # If it's a numeric string, convert to int
            if point_id.isdigit():
                normalized_id = int(point_id)
            # UUIDs and other non-numeric strings are kept as-is
        
        # Try with normalized ID first
        try:
            results = self.client.retrieve(
                collection_name=collection_name,
                ids=[normalized_id],
                with_vectors=with_vectors
            )
            if results and len(results) > 0:
                return results[0]
        except Exception as e:
            # If normalized_id is different from original, try original format
            if normalized_id != point_id:
                try:
                    logger.debug(f"Trying original point ID format: {point_id}")
                    results = self.client.retrieve(
                        collection_name=collection_name,
                        ids=[point_id],
                        with_vectors=with_vectors
                    )
                    if results and len(results) > 0:
                        return results[0]
                except Exception as e2:
                    logger.debug(f"Error trying original ID format: {e2}")
            
            logger.error(f"Error getting point {point_id} (normalized: {normalized_id}): {e}")
        
        logger.warning(f"Point {point_id} not found in collection {collection_name}")
        return None
    
    def delete_points(
        self,
        collection_name: str,
        point_ids: List[Union[str, int]]
    ) -> bool:
        """
        Delete points by IDs
        
        Args:
            collection_name: Collection name
            point_ids: List of point IDs
            
        Returns:
            True if successful
        """
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids
            )
            logger.info(f"✅ Deleted {len(point_ids)} points from {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting points: {e}")
            return False
    
    def scroll_all(
        self,
        collection_name: str,
        batch_size: int = 100,
        filters: Optional[Filter] = None
    ) -> List[Any]:
        """
        Scroll through all points in collection
        
        Args:
            collection_name: Collection name
            batch_size: Batch size
            filters: Optional filters
            
        Returns:
            List of all points
        """
        all_points = []
        offset = None
        
        try:
            while True:
                points, offset = self.client.scroll(
                    collection_name=collection_name,
                    limit=batch_size,
                    offset=offset,
                    scroll_filter=filters
                )
                
                if not points:
                    break
                
                all_points.extend(points)
                
                if offset is None:
                    break
            
            logger.info(f"Scrolled {len(all_points)} points from {collection_name}")
            return all_points
            
        except Exception as e:
            logger.error(f"Error scrolling points: {e}")
            return all_points

