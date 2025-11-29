"""
Popularity-Based Recommendation
IMDb/Bayesian Average method
"""

from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
from ..shared import get_logger

logger = get_logger(__name__)


class PopularityRecommender:
    """
    Popularity-based recommendation using weighted rating (IMDb formula)
    WR = (v/(v+m)) × R + (m/(v+m)) × C
    Where:
    - v = number of votes/ratings
    - m = minimum votes required
    - R = average rating
    - C = global mean rating
    """
    
    def __init__(self, quantile: float = 0.75, alpha: float = 1.0):
        """
        Initialize popularity recommender
        
        Args:
            quantile: Quantile for minimum popularity threshold (0-1)
            alpha: Weight for booking count in popularity calculation
        """
        self.quantile = quantile
        self.alpha = alpha
        logger.info(f"✅ PopularityRecommender initialized (quantile={quantile}, alpha={alpha})")
    
    def calculate_popularity_scores(
        self,
        hotels_df: pd.DataFrame,
        rating_col: str = 'rating',
        vote_col: str = 'votes',
        booking_col: Optional[str] = 'bookings'
    ) -> pd.DataFrame:
        """
        Calculate popularity scores for hotels
        
        Args:
            hotels_df: DataFrame with hotel data
            rating_col: Column name for ratings (R)
            vote_col: Column name for vote counts (v)
            booking_col: Optional column for booking counts
            
        Returns:
            DataFrame with popularity scores
        """
        df = hotels_df.copy()
        
        # Calculate popularity index
        if booking_col and booking_col in df.columns:
            df['popularity'] = df[vote_col] + self.alpha * df[booking_col].fillna(0)
        else:
            df['popularity'] = df[vote_col]
        
        # Calculate global mean (C)
        C = df[rating_col].mean()
        
        # Calculate minimum threshold (m)
        m = df['popularity'].quantile(self.quantile)
        
        logger.info(f"Global mean rating (C): {C:.2f}")
        logger.info(f"Minimum popularity threshold (m): {m:.2f}")
        
        # Calculate weighted rating (WR)
        def weighted_rating(row):
            v = row['popularity']
            R = row[rating_col]
            return (v / (v + m)) * R + (m / (v + m)) * C
        
        df['weighted_rating'] = df.apply(weighted_rating, axis=1)
        
        # Filter qualified hotels
        qualified = df[df['popularity'] >= m].copy()
        logger.info(f"Qualified hotels: {len(qualified)}/{len(df)}")
        
        return qualified.sort_values('weighted_rating', ascending=False)
    
    def recommend_popular(
        self,
        hotels_df: pd.DataFrame,
        top_k: int = 10,
        rating_col: str = 'hotel_rank',
        vote_col: str = 'hotel_vote',
        booking_col: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get popular hotel recommendations
        
        Args:
            hotels_df: DataFrame with hotel data
            top_k: Number of recommendations
            rating_col: Column name for ratings
            vote_col: Column name for votes/reviews
            booking_col: Optional column for bookings
            
        Returns:
            List of popular hotels
        """
        logger.info(f"Generating {top_k} popular recommendations")
        
        try:
            # Calculate scores
            scored = self.calculate_popularity_scores(
                hotels_df=hotels_df,
                rating_col=rating_col,
                vote_col=vote_col,
                booking_col=booking_col
            )
            
            # Take top K
            top_hotels = scored.head(top_k)
            
            # Convert to list of dicts
            recommendations = []
            for idx, row in top_hotels.iterrows():
                rec = {
                    'hotel_id': row.get('hotel_id', idx),
                    'weighted_rating': row['weighted_rating'],
                    'popularity': row['popularity'],
                    'rating': row[rating_col],
                    'votes': row[vote_col]
                }
                
                # Add other columns
                for col in hotels_df.columns:
                    if col not in rec:
                        rec[col] = row[col]
                
                recommendations.append(rec)
            
            logger.info(f"✅ Generated {len(recommendations)} popular recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating popular recommendations: {e}")
            return []
    
    def recommend_by_demographic(
        self,
        hotels_df: pd.DataFrame,
        user_demographic: Dict[str, Any],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend hotels based on demographic filtering
        (Filter hotels by demographic preferences, then rank by popularity)
        
        Args:
            hotels_df: DataFrame with hotel data
            user_demographic: User demographic info (e.g. {'age_group': '25-35', 'location': 'Nha Trang'})
            top_k: Number of recommendations
            
        Returns:
            List of recommended hotels
        """
        logger.info(f"Demographic-based recommendation for: {user_demographic}")
        
        df = hotels_df.copy()
        
        # Apply demographic filters
        # Example filters based on user preferences
        if 'location' in user_demographic:
            location = user_demographic['location']
            if 'hotel_place' in df.columns:
                df = df[df['hotel_place'].str.contains(location, case=False, na=False)]
        
        if 'price_range' in user_demographic:
            price_range = user_demographic['price_range']
            # Assume price_range is like 'low', 'medium', 'high'
            if 'hotel_price_average' in df.columns:
                if price_range == 'low':
                    df = df[df['hotel_price_average'] < df['hotel_price_average'].quantile(0.33)]
                elif price_range == 'high':
                    df = df[df['hotel_price_average'] > df['hotel_price_average'].quantile(0.67)]
                else:  # medium
                    df = df[
                        (df['hotel_price_average'] >= df['hotel_price_average'].quantile(0.33)) &
                        (df['hotel_price_average'] <= df['hotel_price_average'].quantile(0.67))
                    ]
        
        if 'min_rating' in user_demographic:
            min_rating = user_demographic['min_rating']
            if 'hotel_rank' in df.columns:
                df = df[df['hotel_rank'] >= min_rating]
        
        logger.info(f"After demographic filtering: {len(df)} hotels")
        
        if df.empty:
            logger.warning("No hotels match demographic criteria")
            return []
        
        # Rank by popularity within filtered set
        return self.recommend_popular(df, top_k=top_k)

