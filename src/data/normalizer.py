"""
Data Normalizer
Hotel data normalization and semantic text generation
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Optional
from ..shared import get_logger

logger = get_logger(__name__)


class HotelDataNormalizer:
    """
    Hotel data normalizer
    Clean and normalize hotel data for indexing
    """
    
    def __init__(self):
        """Initialize normalizer"""
        self.synonym_mappings = self._load_synonym_mappings()
        logger.info("✅ HotelDataNormalizer initialized")
    
    def _load_synonym_mappings(self) -> Dict[str, List[str]]:
        """Load synonym mappings for Vietnamese hotel domain"""
        return {
            # Location synonyms
            "gần biển": ["ven biển", "sát biển", "view biển", "hướng biển", "bờ biển"],
            "gần trung tâm": ["trung tâm", "trung tâm thành phố", "trong trung tâm"],
            
            # Star rating
            "5 sao": ["năm sao", "5 stars", "luxury", "cao cấp", "sang trọng"],
            "4 sao": ["bốn sao", "4 stars"],
            
            # Features
            "hồ bơi": ["bể bơi", "pool", "swimming pool"],
            "spa": ["massage", "thư giãn"],
            "gym": ["phòng gym", "thể hình", "fitness"],
            "nhà hàng": ["restaurant", "quán ăn"],
            
            # View
            "view biển": ["hướng biển", "nhìn ra biển", "tầm nhìn biển"],
            "view sông": ["hướng sông", "nhìn ra sông"],
        }
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if pd.isna(text) or not text:
            return ""
        
        text = str(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Convert to lowercase (for search)
        text = text.lower()
        
        return text
    
    def extract_features(self, hotel_data: Dict) -> List[str]:
        """
        Extract features from hotel data
        
        Args:
            hotel_data: Hotel data dict
            
        Returns:
            List of feature strings
        """
        features = []
        
        # Extract from facilities if available
        if 'hotel_facilities' in hotel_data and hotel_data['hotel_facilities']:
            facilities = str(hotel_data['hotel_facilities'])
            
            # Check for common features
            if any(w in facilities.lower() for w in ['pool', 'bể bơi', 'hồ bơi']):
                features.append('hồ bơi')
            if any(w in facilities.lower() for w in ['spa', 'massage']):
                features.append('spa')
            if any(w in facilities.lower() for w in ['gym', 'fitness', 'thể hình']):
                features.append('gym')
            if any(w in facilities.lower() for w in ['restaurant', 'nhà hàng']):
                features.append('nhà hàng')
            if any(w in facilities.lower() for w in ['wifi', 'wi-fi']):
                features.append('wifi')
        
        # Extract from keywords
        if 'hotel_tag_keyword' in hotel_data and hotel_data['hotel_tag_keyword']:
            keywords = str(hotel_data['hotel_tag_keyword'])
            features.extend([k.strip() for k in keywords.split(',') if k.strip()])
        
        return features
    
    def create_semantic_text(self, hotel_data: Dict) -> str:
        """
        Create semantic text for embedding
        
        Args:
            hotel_data: Hotel data dict
            
        Returns:
            Semantic text
        """
        parts = []
        
        # Hotel name
        if 'hotel_name' in hotel_data and hotel_data['hotel_name']:
            parts.append(f"Tên: {hotel_data['hotel_name']}")
        
        # Rating
        if 'hotel_rank' in hotel_data and hotel_data['hotel_rank']:
            rank = hotel_data['hotel_rank']
            if rank >= 4.5:
                parts.append("Khách sạn cao cấp")
            elif rank >= 4.0:
                parts.append("Khách sạn tốt")
            parts.append(f"Đánh giá: {rank} sao")
        
        # Location
        if 'hotel_place' in hotel_data and hotel_data['hotel_place']:
            parts.append(f"Địa điểm: {hotel_data['hotel_place']}")
        
        if 'hotel_placedetails' in hotel_data and hotel_data['hotel_placedetails']:
            parts.append(f"Chi tiết vị trí: {hotel_data['hotel_placedetails']}")
        
        # Description
        if 'hotel_desc' in hotel_data and hotel_data['hotel_desc']:
            desc = str(hotel_data['hotel_desc'])
            # Truncate if too long
            if len(desc) > 500:
                desc = desc[:500] + "..."
            parts.append(f"Mô tả: {desc}")
        
        # Features
        features = self.extract_features(hotel_data)
        if features:
            parts.append(f"Tiện nghi: {', '.join(features)}")
        
        # Price range
        if 'hotel_price_average' in hotel_data and hotel_data['hotel_price_average']:
            price = hotel_data['hotel_price_average']
            if price < 500000:
                parts.append("Giá: Hợp lý")
            elif price < 1000000:
                parts.append("Giá: Trung bình")
            else:
                parts.append("Giá: Cao cấp")
        
        # Keywords
        if 'hotel_tag_keyword' in hotel_data and hotel_data['hotel_tag_keyword']:
            parts.append(f"Từ khóa: {hotel_data['hotel_tag_keyword']}")
        
        semantic_text = ". ".join(parts)
        return semantic_text
    
    def normalize_hotels(self, hotels_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize hotels DataFrame
        
        Args:
            hotels_df: Hotels DataFrame
            
        Returns:
            Normalized DataFrame with semantic_text column
        """
        logger.info(f"Normalizing {len(hotels_df)} hotels...")
        
        df = hotels_df.copy()
        
        # Create semantic text for each hotel
        semantic_texts = []
        for idx, row in df.iterrows():
            semantic_text = self.create_semantic_text(row.to_dict())
            semantic_texts.append(semantic_text)
        
        df['semantic_text'] = semantic_texts
        
        # Fill NaN values
        df = df.fillna({
            'hotel_desc': '',
            'hotel_place': '',
            'hotel_placedetails': '',
            'hotel_tag_keyword': '',
            'hotel_rank': 0,
            'hotel_vote': 0,
            'hotel_price_average': 0
        })
        
        logger.info(f"✅ Normalized {len(df)} hotels")
        return df
    
    def normalize_coupons(self, coupons_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize coupons DataFrame
        
        Args:
            coupons_df: Coupons DataFrame
            
        Returns:
            Normalized DataFrame with semantic_text
        """
        logger.info(f"Normalizing {len(coupons_df)} coupons...")
        
        df = coupons_df.copy()
        
        # Create semantic text for coupons
        semantic_texts = []
        for idx, row in df.iterrows():
            parts = []
            
            if 'coupon_name' in row and row['coupon_name']:
                parts.append(f"Coupon: {row['coupon_name']}")
            
            if 'coupon_code' in row and row['coupon_code']:
                parts.append(f"Mã: {row['coupon_code']}")
            
            if 'coupon_price_sale' in row and row['coupon_price_sale']:
                parts.append(f"Giảm: {row['coupon_price_sale']}")
            
            if 'coupon_desc' in row and row['coupon_desc']:
                parts.append(f"Mô tả: {row['coupon_desc']}")
            
            semantic_text = ". ".join(parts)
            semantic_texts.append(semantic_text)
        
        df['semantic_text'] = semantic_texts
        df['document_type'] = 'coupon'
        
        logger.info(f"✅ Normalized {len(df)} coupons")
        return df


