"""
Collaborative Filtering
Support for NCF (Neural Collaborative Filtering) models
"""

from typing import List, Dict, Optional, Any, Tuple
import numpy as np
import pandas as pd
from pathlib import Path
from ..shared import get_logger

logger = get_logger(__name__)


class CollaborativeRecommender:
    """
    Collaborative filtering recommendation
    Supports pre-trained NCF models
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        user2idx_path: Optional[str] = None,
        hotel2idx_path: Optional[str] = None
    ):
        """
        Initialize collaborative recommender
        
        Args:
            model_path: Path to trained model
            user2idx_path: Path to user2idx mapping
            hotel2idx_path: Path to hotel2idx mapping
        """
        self.model = None
        self.user2idx = None
        self.hotel2idx = None
        self.idx2hotel = None
        
        if model_path and user2idx_path and hotel2idx_path:
            self.load_model(model_path, user2idx_path, hotel2idx_path)
        
        logger.info(f"✅ CollaborativeRecommender initialized")
    
    def load_model(
        self,
        model_path: str,
        user2idx_path: str,
        hotel2idx_path: str
    ) -> bool:
        """
        Load pre-trained NCF model and mappings
        
        Args:
            model_path: Path to model (TensorFlow SavedModel or .h5)
            user2idx_path: Path to user2idx JSON
            hotel2idx_path: Path to hotel2idx JSON
            
        Returns:
            True if successful
        """
        try:
            import json
            import tensorflow as tf
            
            # Load model
            logger.info(f"Loading model from {model_path}")
            
            model_path_obj = Path(model_path)
            if model_path_obj.is_dir():
                # SavedModel format
                self.model = tf.keras.models.load_model(model_path)
            elif model_path.endswith('.h5'):
                # HDF5 format
                self.model = tf.keras.models.load_model(model_path)
            else:
                raise ValueError(f"Unsupported model format: {model_path}")
            
            # Load mappings
            with open(user2idx_path, 'r') as f:
                self.user2idx = json.load(f)
            
            with open(hotel2idx_path, 'r') as f:
                self.hotel2idx = json.load(f)
            
            # Create reverse mapping
            self.idx2hotel = {int(v): k for k, v in self.hotel2idx.items()}
            
            logger.info(f"✅ Model loaded: {len(self.user2idx)} users, {len(self.hotel2idx)} hotels")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def predict_for_user(
        self,
        user_id: Any,
        top_k: int = 10,
        exclude_seen: bool = True,
        seen_hotels: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Predict recommendations for a user
        
        Args:
            user_id: User ID
            top_k: Number of recommendations
            exclude_seen: Exclude hotels user has seen/booked
            seen_hotels: List of hotel IDs user has interacted with
            
        Returns:
            List of recommended hotels with predicted scores
        """
        if self.model is None:
            logger.error("Model not loaded")
            return []
        
        # Convert user_id to string for mapping
        user_id_str = str(user_id)
        
        if user_id_str not in self.user2idx:
            logger.warning(f"User {user_id} not in training data (cold start)")
            return []
        
        user_idx = self.user2idx[user_id_str]
        
        try:
            # Get all hotel indices
            num_hotels = len(self.hotel2idx)
            hotel_indices = np.arange(num_hotels)
            
            # Create user-hotel pairs
            user_indices = np.full(num_hotels, user_idx)
            
            # Predict scores
            predictions = self.model.predict([user_indices, hotel_indices], verbose=0)
            predictions = predictions.flatten()
            
            # Create DataFrame for sorting
            results = pd.DataFrame({
                'hotel_idx': hotel_indices,
                'score': predictions
            })
            
            # Exclude seen hotels if requested
            if exclude_seen and seen_hotels:
                seen_hotel_strs = [str(h) for h in seen_hotels]
                seen_indices = [self.hotel2idx[h] for h in seen_hotel_strs if h in self.hotel2idx]
                results = results[~results['hotel_idx'].isin(seen_indices)]
            
            # Sort by score and take top K
            top_results = results.nlargest(top_k, 'score')
            
            # Convert to recommendations
            recommendations = []
            for _, row in top_results.iterrows():
                hotel_idx = int(row['hotel_idx'])
                hotel_id = self.idx2hotel.get(hotel_idx, hotel_idx)
                
                rec = {
                    'hotel_id': hotel_id,
                    'predicted_score': float(row['score']),
                    'method': 'collaborative_filtering'
                }
                recommendations.append(rec)
            
            logger.info(f"✅ Generated {len(recommendations)} CF recommendations for user {user_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error predicting for user {user_id}: {e}")
            return []
    
    def predict_interaction(
        self,
        user_id: Any,
        hotel_id: Any
    ) -> Optional[float]:
        """
        Predict interaction score for a specific user-hotel pair
        
        Args:
            user_id: User ID
            hotel_id: Hotel ID
            
        Returns:
            Predicted score or None if not possible
        """
        if self.model is None:
            return None
        
        user_id_str = str(user_id)
        hotel_id_str = str(hotel_id)
        
        if user_id_str not in self.user2idx or hotel_id_str not in self.hotel2idx:
            return None
        
        try:
            user_idx = self.user2idx[user_id_str]
            hotel_idx = self.hotel2idx[hotel_id_str]
            
            prediction = self.model.predict([[user_idx], [hotel_idx]], verbose=0)
            return float(prediction[0][0])
            
        except Exception as e:
            logger.error(f"Error predicting interaction: {e}")
            return None
    
    def get_similar_users(
        self,
        user_id: Any,
        top_k: int = 10
    ) -> List[Tuple[Any, float]]:
        """
        Find similar users based on embedding similarity
        (Requires access to user embeddings from model)
        
        Args:
            user_id: User ID
            top_k: Number of similar users
            
        Returns:
            List of (user_id, similarity_score) tuples
        """
        # This would require extracting user embeddings from the model
        # Implementation depends on model architecture
        logger.warning("get_similar_users not yet implemented")
        return []

