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
from .reranker import DiversityReranker
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
        
        # Initialize diversity re-ranker for diverse recommendations
        self.diversity_reranker = DiversityReranker(diversity_weight=0.3)
        
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
        diversity_weight: float = 0.3,
        use_diversity: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid recommendation combining multiple strategies with optional diversity re-ranking
        
        Args:
            query: Optional query text
            item_id: Optional reference item ID
            collection_name: Collection to search
            top_k: Number of recommendations
            semantic_weight: Weight for semantic similarity
            popularity_weight: Weight for popularity
            diversity_weight: Weight for diversity (0.0-1.0, only used if use_diversity=True)
            use_diversity: Enable diversity re-ranking to avoid repetitive results
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
        
        # Apply diversity re-ranking if enabled
        if use_diversity and len(recommendations_list) > 1:
            # Update diversity weight if provided
            if diversity_weight != self.diversity_reranker.diversity_weight:
                self.diversity_reranker.diversity_weight = diversity_weight
            
            # Convert recommendations to document format for re-ranker
            # DiversityReranker expects documents with 'payload' and 'score' fields
            documents_for_rerank = []
            for rec in recommendations_list:
                doc = {
                    'id': rec.get('item_id'),
                    'score': rec.get('hybrid_score', 0.0),
                    'payload': {k: v for k, v in rec.items() if k not in ['scores', 'hybrid_score']}
                }
                documents_for_rerank.append(doc)
            
            # Apply diversity re-ranking
            reranked_docs = self.diversity_reranker.rerank(
                documents=documents_for_rerank,
                top_k=top_k
            )
            
            # Convert back to recommendation format
            top_recommendations = []
            for doc in reranked_docs:
                rec = doc['payload'].copy()
                rec['item_id'] = doc['id']
                rec['hybrid_score'] = doc.get('final_score', doc.get('score', 0.0))
                rec['diversity_score'] = doc.get('diversity_score', 0.0)
                top_recommendations.append(rec)
            
            logger.info(f"Generated {len(top_recommendations)} diverse hybrid recommendations")
        else:
            # Take top_k without diversity re-ranking
            top_recommendations = recommendations_list[:top_k]
            logger.info(f"Generated {len(top_recommendations)} hybrid recommendations")
        
        return top_recommendations
    
    def recommend_for_user(
        self,
        user_id: Optional[Union[str, int]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        collection_name: str = None,
        top_k: int = 10,
        check_cold_start: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Recommend items based on user preferences with cold start handling
        
        Args:
            user_id: Optional user ID to check for cold start
            user_preferences: User preferences dict
            collection_name: Collection to search
            top_k: Number of recommendations
            check_cold_start: Check if user is new and use cold start strategies
            
        Returns:
            List of recommended items
        """
        # Check for cold start (new user)
        if check_cold_start and user_id is not None:
            if self._is_new_user(user_id):
                logger.info(f"New user detected (user_id={user_id}), using cold start strategy")
                return self.recommend_for_new_user(
                    user_preferences=user_preferences,
                    collection_name=collection_name,
                    top_k=top_k
                )
        
        logger.info(f"Recommending based on user preferences")
        
        # Build query from preferences
        query_parts = []
        
        if user_preferences:
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
        if user_preferences and "min_rating" in user_preferences:
            # Note: This would need proper filter implementation
            pass
        
        # Get recommendations
        return self.recommend_by_query(
            query=query,
            collection_name=collection_name,
            top_k=top_k,
            filters=filters if filters else None
        )
    
    def _is_new_user(self, user_id: Union[str, int]) -> bool:
        """
        Check if user is new (has no interaction history)
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if user is new, False otherwise
        """
        # TODO: Implement actual check against database/cache
        # For now, this is a placeholder that always returns False
        # In production, you would check:
        # - User interaction history in database
        # - User ratings/reviews count
        # - User booking history
        
        # Example implementation (would need database connection):
        # from ..data.connector import DatabaseConnector
        # db = DatabaseConnector()
        # interactions = db.get_user_interactions(user_id)
        # return len(interactions) == 0
        
        logger.debug(f"Checking if user {user_id} is new (placeholder: returning False)")
        return False
    
    def recommend_for_new_user(
        self,
        user_preferences: Optional[Dict[str, Any]] = None,
        collection_name: str = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend items for new users (cold start)
        Strategy: Use demographic-based if preferences available, else popularity-based
        
        Args:
            user_preferences: Optional user preferences (demographic info)
            collection_name: Collection to search
            top_k: Number of recommendations
            
        Returns:
            List of recommended items
        """
        logger.info("Cold start: Recommending for new user")
        
        # Strategy 1: Demographic-based if preferences available
        if user_preferences and any(key in user_preferences for key in [
            'preferred_location', 'preferred_price_range', 'preferred_amenities',
            'age_group', 'travel_purpose', 'budget_range'
        ]):
            logger.info("Using demographic-based recommendation for new user")
            return self.recommend_for_user(
                user_id=None,
                user_preferences=user_preferences,
                collection_name=collection_name,
                top_k=top_k,
                check_cold_start=False  # Already in cold start, don't check again
            )
        
        # Strategy 2: Popularity-based fallback
        logger.info("Using popularity-based recommendation for new user (no preferences)")
        return self.recommend_popular(
            collection_name=collection_name,
            top_k=top_k,
            use_weighted_rating=True
        )
    
    def recommend_for_new_item(
        self,
        item_features: Dict[str, Any],
        collection_name: str = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend similar items for a new item (cold start)
        Strategy: Content-based similarity using item features
        
        Args:
            item_features: Item features dict (e.g., description, amenities, location)
            collection_name: Collection to search
            top_k: Number of recommendations
            
        Returns:
            List of similar items
        """
        logger.info("Cold start: Recommending similar items for new item")
        
        # Build query from item features
        query_parts = []
        
        # Extract text features for semantic search
        if 'description' in item_features:
            query_parts.append(item_features['description'])
        if 'hotel_name' in item_features:
            query_parts.append(item_features['hotel_name'])
        if 'amenities' in item_features:
            amenities = item_features['amenities']
            if isinstance(amenities, list):
                query_parts.extend(amenities)
            else:
                query_parts.append(str(amenities))
        if 'area_name' in item_features:
            query_parts.append(item_features['area_name'])
        
        # Build query
        query = " ".join(query_parts) if query_parts else "khách sạn"
        
        # Get semantic recommendations
        similar_items = self.recommend_by_query(
            query=query,
            collection_name=collection_name,
            top_k=top_k * 2,  # Get more for filtering
            filters=None
        )
        
        # If not enough similar items, supplement with popular items
        if len(similar_items) < top_k:
            logger.info(f"Only {len(similar_items)} similar items found, supplementing with popular items")
            popular_items = self.recommend_popular(
                collection_name=collection_name,
                top_k=top_k - len(similar_items),
                use_weighted_rating=True
            )
            
            # Avoid duplicates
            similar_ids = {item.get('item_id') for item in similar_items}
            for item in popular_items:
                if item.get('item_id') not in similar_ids:
                    similar_items.append(item)
                    if len(similar_items) >= top_k:
                        break
        
        return similar_items[:top_k]

