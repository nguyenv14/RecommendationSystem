"""
Retriever Service
Unified retrieval logic cho cả RAG và Recommendation
"""

from typing import List, Dict, Optional, Any
from qdrant_client.models import Filter, FieldCondition, MatchValue
from .embeddings import EmbeddingService
from .vectorstore import VectorStoreService
from ..shared import get_logger

logger = get_logger(__name__)


class RetrieverService:
    """
    Unified retriever service
    Handles semantic search và retrieval cho cả RAG và Recommendation
    """
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vectorstore_service: VectorStoreService,
        default_collection: Optional[str] = None,
        default_top_k: int = 5
    ):
        """
        Initialize retriever service
        
        Args:
            embedding_service: Embedding service instance
            vectorstore_service: Vector store service instance
            default_collection: Default collection to search
            default_top_k: Default number of results
        """
        self.embedding_service = embedding_service
        self.vectorstore_service = vectorstore_service
        self.default_collection = default_collection
        self.default_top_k = default_top_k
        
        logger.info(f"✅ RetrieverService initialized")
    
    def retrieve(
        self,
        query: str,
        collection_name: Optional[str] = None,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar documents by query text
        
        Args:
            query: Query text
            collection_name: Collection to search
            top_k: Number of results
            filters: Filters dict (e.g. {"document_type": "hotel"})
            score_threshold: Minimum similarity score
            
        Returns:
            List of retrieved documents with scores
        """
        if collection_name is None:
            collection_name = self.default_collection
        
        if top_k is None:
            top_k = self.default_top_k
        
        # Build Qdrant filter from dict
        qdrant_filter = self._build_filter(filters) if filters else None
        
        try:
            # Embed query
            query_vector = self.embedding_service.embed_query(query)
            
            # Search
            results = self.vectorstore_service.search(
                query_vector=query_vector,
                collection_name=collection_name,
                limit=top_k,
                filters=qdrant_filter,
                score_threshold=score_threshold
            )
            
            # Format results
            documents = []
            for result in results:
                doc = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents for query: '{query[:50]}...'")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def retrieve_similar_items(
        self,
        item_id: Union[str, int],
        collection_name: Optional[str] = None,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar items to a given item
        (for recommendation)
        
        Args:
            item_id: Item ID to find similar items for
            collection_name: Collection to search
            top_k: Number of results
            filters: Optional filters
            
        Returns:
            List of similar items with scores
        """
        if collection_name is None:
            collection_name = self.default_collection
        
        if top_k is None:
            top_k = self.default_top_k
        
        try:
            # Get item vector
            point = self.vectorstore_service.get_point(collection_name, item_id)
            if point is None:
                logger.warning(f"Item {item_id} not found in {collection_name}")
                return []
            
            # Get vector (may need to retrieve separately)
            # For now, we'll search by re-embedding if needed
            # This is a simplified version - in production you'd store vectors
            
            # Build filter
            qdrant_filter = self._build_filter(filters) if filters else None
            
            # Search using item's payload for similarity
            # (This is simplified - you may want to use the item's vector directly)
            if hasattr(point, 'vector') and point.vector:
                query_vector = point.vector
            else:
                # Fallback: re-embed item description
                item_text = self._get_item_text(point.payload)
                query_vector = self.embedding_service.embed_query(item_text)
            
            results = self.vectorstore_service.search(
                query_vector=query_vector,
                collection_name=collection_name,
                limit=top_k + 1,  # +1 to exclude self
                filters=qdrant_filter
            )
            
            # Format and exclude self
            documents = []
            for result in results:
                if result.id != item_id:  # Exclude the query item itself
                    doc = {
                        "id": result.id,
                        "score": result.score,
                        "payload": result.payload
                    }
                    documents.append(doc)
            
            # Limit to top_k
            documents = documents[:top_k]
            
            logger.info(f"Found {len(documents)} similar items for item {item_id}")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving similar items: {e}")
            return []
    
    def retrieve_by_filters(
        self,
        filters: Dict[str, Any],
        collection_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents by filters only (no semantic search)
        
        Args:
            filters: Filter dict
            collection_name: Collection to search
            limit: Maximum number of results
            
        Returns:
            List of documents
        """
        if collection_name is None:
            collection_name = self.default_collection
        
        try:
            qdrant_filter = self._build_filter(filters)
            
            # Scroll through filtered results
            points = self.vectorstore_service.scroll_all(
                collection_name=collection_name,
                batch_size=100,
                filters=qdrant_filter
            )
            
            # Format results
            documents = []
            for point in points[:limit]:
                doc = {
                    "id": point.id,
                    "payload": point.payload
                }
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents by filters")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving by filters: {e}")
            return []
    
    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """
        Build Qdrant filter from dict
        
        Args:
            filters: Filter dict (e.g. {"document_type": "hotel", "hotel_rank": 5})
            
        Returns:
            Qdrant Filter object
        """
        conditions = []
        
        for key, value in filters.items():
            condition = FieldCondition(
                key=key,
                match=MatchValue(value=value)
            )
            conditions.append(condition)
        
        return Filter(must=conditions) if conditions else None
    
    def _get_item_text(self, payload: Dict[str, Any]) -> str:
        """
        Extract text from item payload for embedding
        
        Args:
            payload: Item payload
            
        Returns:
            Text representation
        """
        # Try common text fields
        text_fields = [
            'text', 'content', 'description', 'semantic_text',
            'hotel_name', 'hotel_desc', 'name', 'title'
        ]
        
        for field in text_fields:
            if field in payload and payload[field]:
                return str(payload[field])
        
        # Fallback: concatenate all string values
        text_parts = []
        for value in payload.values():
            if isinstance(value, str) and value:
                text_parts.append(value)
        
        return " ".join(text_parts) if text_parts else "no description"

