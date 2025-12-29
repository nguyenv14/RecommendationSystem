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
    
    def _categorize_price(self, price: float) -> str:
        """
        Categorize price into price ranges
        
        Args:
            price: Hotel average price (VND)
            
        Returns:
            Price category string
        """
        if not price or price <= 0:
            return "giá chưa xác định"
        
        if price < 500000:
            return "giá rẻ"
        elif price < 1000000:
            return "giá trung bình"
        elif price < 2000000:
            return "giá khá"
        elif price < 3000000:
            return "giá cao"
        else:
            return "giá rất cao"
    
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
            # Keep full description, don't truncate
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
    
    def normalize_rooms(self, rooms_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize rooms DataFrame
        
        Args:
            rooms_df: Rooms DataFrame with enriched data
            
        Returns:
            Normalized DataFrame with semantic_text column
        """
        logger.info(f"Normalizing {len(rooms_df)} rooms...")
        
        df = rooms_df.copy()
        
        # Create semantic text for each room
        semantic_texts = []
        for idx, row in df.iterrows():
            parts = []
            
            # Room name
            if pd.notna(row.get('room_name')) and str(row.get('room_name')).strip():
                parts.append(f"Tên phòng: {row['room_name']}")
            
            # Hotel info
            if pd.notna(row.get('hotel_name')) and str(row.get('hotel_name')).strip():
                parts.append(f"Khách sạn: {row['hotel_name']}")
            
            if pd.notna(row.get('area_name')) and str(row.get('area_name')).strip():
                parts.append(f"Khu vực: {row['area_name']}")
            
            # Room details
            if pd.notna(row.get('room_amount_of_people')):
                parts.append(f"Sức chứa: {int(row['room_amount_of_people'])} người")
            
            if pd.notna(row.get('room_price')):
                price = float(row['room_price'])
                parts.append(f"Giá: {price:,.0f} VND")
            
            if pd.notna(row.get('type_room_price_sale')):
                sale_price = float(row['type_room_price_sale'])
                parts.append(f"Giá khuyến mãi: {sale_price:,.0f} VND")
            
            if pd.notna(row.get('type_room_bed')):
                parts.append(f"Giường: {int(row['type_room_bed'])} giường")
            
            if pd.notna(row.get('type_room_condition')):
                condition = int(row['type_room_condition'])
                parts.append(f"Điều kiện: {'Có điều hòa' if condition == 1 else 'Không điều hòa'}")
            
            semantic_text = ". ".join(parts)
            semantic_texts.append(semantic_text)
        
        df['semantic_text'] = semantic_texts
        
        # Fill NaN values
        df = df.fillna({
            'room_name': '',
            'hotel_name': '',
            'area_name': '',
            'room_amount_of_people': 0,
            'room_price': 0,
            'type_room_price_sale': 0,
            'type_room_bed': 0,
            'type_room_condition': 0
        })
        
        logger.info(f"✅ Normalized {len(df)} rooms")
        return df
    
    def normalize_type_rooms(self, type_rooms_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize type_rooms DataFrame
        
        Args:
            type_rooms_df: Type rooms DataFrame with enriched data
            
        Returns:
            Normalized DataFrame with semantic_text column
        """
        logger.info(f"Normalizing {len(type_rooms_df)} type_rooms...")
        
        df = type_rooms_df.copy()
        
        # Create semantic text for each type_room
        semantic_texts = []
        for idx, row in df.iterrows():
            parts = []
            
            # Type room name
            if pd.notna(row.get('type_room_name')) and str(row.get('type_room_name')).strip():
                parts.append(f"Loại phòng: {row['type_room_name']}")
            
            # Hotels using this type
            if pd.notna(row.get('hotel_names')) and str(row.get('hotel_names')).strip():
                parts.append(f"Khách sạn: {row['hotel_names']}")
            
            # Price range
            if pd.notna(row.get('search_min_price')) and pd.notna(row.get('search_max_price')):
                min_price = float(row['search_min_price'])
                max_price = float(row['search_max_price'])
                if min_price == max_price:
                    parts.append(f"Giá: {min_price:,.0f} VND")
                else:
                    parts.append(f"Giá: {min_price:,.0f} - {max_price:,.0f} VND")
            
            if pd.notna(row.get('search_avg_price')):
                avg_price = float(row['search_avg_price'])
                parts.append(f"Giá trung bình: {avg_price:,.0f} VND")
            
            # Room details
            if pd.notna(row.get('type_room_bed')):
                parts.append(f"Giường: {int(row['type_room_bed'])} giường")
            
            if pd.notna(row.get('type_room_condition')):
                condition = int(row['type_room_condition'])
                parts.append(f"Điều kiện: {'Có điều hòa' if condition == 1 else 'Không điều hòa'}")
            
            if pd.notna(row.get('room_count')):
                parts.append(f"Số lượng phòng: {int(row['room_count'])} phòng")
            
            semantic_text = ". ".join(parts)
            semantic_texts.append(semantic_text)
        
        df['semantic_text'] = semantic_texts
        
        # Fill NaN values
        df = df.fillna({
            'type_room_name': '',
            'hotel_names': '',
            'search_min_price': 0,
            'search_max_price': 0,
            'search_avg_price': 0,
            'type_room_bed': 0,
            'type_room_condition': 0,
            'room_count': 0
        })
        
        logger.info(f"✅ Normalized {len(df)} type_rooms")
        return df


