"""
Recommender Service
Unified recommendation logic
"""

from typing import List, Dict, Optional, Any, Union
import pandas as pd
import numpy as np
from .embeddings import EmbeddingService
from .vectorstore import VectorStoreService
from .retriever import RetrieverService
from ..shared import get_logger

logger = get_logger(__name__)


class RecommenderService:
    """
    Unified recommender service
    Handles various recommendation strategies
    """
    
    def __init__(
        self,
        retriever_service: RetrieverService,
        embedding_service: EmbeddingService,
        vectorstore_service: VectorStoreService
    ):
        """
        Initialize recommender service
        
        Args:
            retriever_service: Retriever service instance
            embedding_service: Embedding service instance
            vectorstore_service: Vector store service instance
        """
        self.retriever = retriever_service
        self.embedding = embedding_service
        self.vectorstore = vectorstore_service
        
        logger.info(f"✅ RecommenderService initialized")
    
    def recommend_by_query(
        self,
        query: str,
        collection_name: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend items based on text query (semantic search)
        
        Args:
            query: User query (e.g. "khách sạn 5 sao gần biển")
            collection_name: Collection to search
            top_k: Number of recommendations
            filters: Optional filters
            
        Returns:
            List of recommended items
        """
        logger.info(f"Recommending by query: '{query[:50]}...'")
        
        results = self.retriever.retrieve(
            query=query,
            collection_name=collection_name,
            top_k=top_k,
            filters=filters
        )
        
        # Format for recommendation
        recommendations = []
        for result in results:
            rec = {
                "item_id": result.get("id"),
                "score": result.get("score"),
                **result.get("payload", {})
            }
            recommendations.append(rec)
        
        return recommendations
    
    def recommend_similar(
        self,
        item_id: Union[str, int],
        collection_name: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend similar items (item-to-item recommendation)
        
        Args:
            item_id: Reference item ID
            collection_name: Collection to search
            top_k: Number of recommendations
            filters: Optional filters
            
        Returns:
            List of similar items
        """
        logger.info(f"Recommending similar items for item_id={item_id}")
        
        results = self.retriever.retrieve_similar_items(
            item_id=item_id,
            collection_name=collection_name,
            top_k=top_k,
            filters=filters
        )
        
        # Format for recommendation
        recommendations = []
        for result in results:
            rec = {
                "item_id": result.get("id"),
                "similarity_score": result.get("score"),
                **result.get("payload", {})
            }
            recommendations.append(rec)
        
        return recommendations
    
    def recommend_popular(
        self,
        collection_name: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        use_weighted_rating: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Recommend popular items (popularity-based)
        
        Args:
            collection_name: Collection to search
            top_k: Number of recommendations
            filters: Optional filters
            use_weighted_rating: Use IMDb weighted rating formula
            
        Returns:
            List of popular items
        """
        logger.info(f"Recommending popular items (weighted={use_weighted_rating})")
        
        # Retrieve items with filters
        items = self.retriever.retrieve_by_filters(
            filters=filters or {},
            collection_name=collection_name,
            limit=1000  # Get more to sort
        )
        
        if not items:
            return []
        
        if use_weighted_rating:
            # Use IMDb weighted rating formula
            # Convert to DataFrame for easier calculation
            items_data = []
            for item in items:
                payload = item.get("payload", {})
                items_data.append({
                    "item_id": item.get("id"),
                    "rating": payload.get("hotel_rank", payload.get("rating", 0)),
                    "votes": payload.get("hotel_vote", payload.get("reviews", 1)),
                    "bookings": payload.get("bookings", 0),
                    "payload": payload
                })
            
            df = pd.DataFrame(items_data)
            
            # Calculate popularity (votes + bookings)
            df['popularity'] = df['votes'] + df['bookings'] * 0.5
            
            # Calculate weighted rating (IMDb formula)
            C = df['rating'].mean()  # Global mean
            m = df['popularity'].quantile(0.75)  # Minimum threshold
            
            def weighted_rating(row):
                v = row['popularity']
                R = row['rating']
                if v >= m:
                    return (v / (v + m)) * R + (m / (v + m)) * C
                else:
                    return 0  # Below threshold
            
            df['weighted_rating'] = df.apply(weighted_rating, axis=1)
            
            # Sort and take top K
            top_df = df.nlargest(top_k, 'weighted_rating')
            
            recommendations = []
            for _, row in top_df.iterrows():
                rec = {
                    "item_id": row['item_id'],
                    "weighted_rating": row['weighted_rating'],
                    "popularity": row['popularity'],
                    **row['payload']
                }
                recommendations.append(rec)
        
        else:
            # Simple popularity scoring
            def get_popularity_score(item):
                payload = item.get("payload", {})
                rating = payload.get("hotel_rank", payload.get("rating", 0))
                reviews = payload.get("hotel_vote", payload.get("reviews", 0))
                bookings = payload.get("bookings", 0)
                score = (rating * 10) + (reviews * 0.1) + (bookings * 0.01)
                return score
            
            items_sorted = sorted(items, key=get_popularity_score, reverse=True)
            top_items = items_sorted[:top_k]
            
            recommendations = []
            for item in top_items:
                rec = {
                    "item_id": item.get("id"),
                    "popularity_score": get_popularity_score(item),
                    **item.get("payload", {})
                }
                recommendations.append(rec)
        
        return recommendations
    
    def recommend_hybrid(
        self,
        query: Optional[str] = None,
        item_id: Optional[Union[str, int]] = None,
        collection_name: str = None,
        top_k: int = 10,
        semantic_weight: float = 0.7,
        popularity_weight: float = 0.3,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid recommendation combining multiple strategies
        
        Args:
            query: Optional query text
            item_id: Optional reference item ID
            collection_name: Collection to search
            top_k: Number of recommendations
            semantic_weight: Weight for semantic similarity
            popularity_weight: Weight for popularity
            filters: Optional filters
            
        Returns:
            List of recommended items
        """
        logger.info(f"Hybrid recommendation (semantic={semantic_weight}, popularity={popularity_weight})")
        
        recommendations = {}
        
        # Get semantic recommendations
        if query:
            semantic_recs = self.recommend_by_query(
                query=query,
                collection_name=collection_name,
                top_k=top_k * 2,  # Get more for re-ranking
                filters=filters
            )
            
            for rec in semantic_recs:
                item_id_key = rec.get("item_id")
                if item_id_key not in recommendations:
                    recommendations[item_id_key] = rec
                    recommendations[item_id_key]["scores"] = {}
                
                recommendations[item_id_key]["scores"]["semantic"] = rec.get("score", 0)
        
        elif item_id:
            semantic_recs = self.recommend_similar(
                item_id=item_id,
                collection_name=collection_name,
                top_k=top_k * 2,
                filters=filters
            )
            
            for rec in semantic_recs:
                item_id_key = rec.get("item_id")
                if item_id_key not in recommendations:
                    recommendations[item_id_key] = rec
                    recommendations[item_id_key]["scores"] = {}
                
                recommendations[item_id_key]["scores"]["semantic"] = rec.get("similarity_score", 0)
        
        # Get popularity scores
        popular_recs = self.recommend_popular(
            collection_name=collection_name,
            top_k=top_k * 2,
            filters=filters
        )
        
        # Normalize popularity scores
        max_pop = max([r.get("popularity_score", 0) for r in popular_recs]) if popular_recs else 1
        
        for rec in popular_recs:
            item_id_key = rec.get("item_id")
            if item_id_key not in recommendations:
                recommendations[item_id_key] = rec
                recommendations[item_id_key]["scores"] = {}
            
            pop_score = rec.get("popularity_score", 0) / max_pop if max_pop > 0 else 0
            recommendations[item_id_key]["scores"]["popularity"] = pop_score
        
        # Calculate hybrid scores
        for item_id_key, rec in recommendations.items():
            scores = rec.get("scores", {})
            semantic_score = scores.get("semantic", 0)
            popularity_score = scores.get("popularity", 0)
            
            hybrid_score = (semantic_score * semantic_weight) + (popularity_score * popularity_weight)
            rec["hybrid_score"] = hybrid_score
        
        # Sort by hybrid score
        recommendations_list = list(recommendations.values())
        recommendations_list.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
        
        # Take top_k
        top_recommendations = recommendations_list[:top_k]
        
        logger.info(f"Generated {len(top_recommendations)} hybrid recommendations")
        return top_recommendations
    
    def recommend_for_user(
        self,
        user_preferences: Dict[str, Any],
        collection_name: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend items based on user preferences
        (Demographic/profile-based recommendation)
        
        Args:
            user_preferences: User preferences dict
            collection_name: Collection to search
            top_k: Number of recommendations
            
        Returns:
            List of recommended items
        """
        logger.info(f"Recommending based on user preferences")
        
        # Build query from preferences
        query_parts = []
        
        if "preferred_location" in user_preferences:
            query_parts.append(user_preferences["preferred_location"])
        
        if "preferred_price_range" in user_preferences:
            price_range = user_preferences["preferred_price_range"]
            query_parts.append(f"giá {price_range}")
        
        if "preferred_amenities" in user_preferences:
            amenities = user_preferences["preferred_amenities"]
            if isinstance(amenities, list):
                query_parts.extend(amenities)
            else:
                query_parts.append(str(amenities))
        
        # Build query
        query = " ".join(query_parts) if query_parts else "khách sạn tốt"
        
        # Build filters
        filters = {}
        if "min_rating" in user_preferences:
            # Note: This would need proper filter implementation
            pass
        
        # Get recommendations
        return self.recommend_by_query(
            query=query,
            collection_name=collection_name,
            top_k=top_k,
            filters=filters if filters else None
        )

