#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coupon Data Normalization and Semantic Mapping
Chuẩn hóa dữ liệu coupon và map các coupons có ngữ nghĩa tương đồng
"""

import pandas as pd
import numpy as np
import re
import json
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import logging
from difflib import SequenceMatcher
import unicodedata
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CouponDataNormalizer:
    """Chuẩn hóa và map các coupons có ngữ nghĩa tương đồng"""
    
    def __init__(self):
        """Initialize normalizer"""
        self.synonym_mappings = self._load_synonym_mappings()
        self.normalized_coupons = {}
        self.semantic_clusters = defaultdict(list)
        self.coupon_similarity_map = {}
    
    def _load_synonym_mappings(self) -> Dict[str, List[str]]:
        """Load synonym mappings for coupon domain"""
        return {
            # Location synonyms
            "Đà Nẵng": ["Da Nang", "Danang", "DN", "khu vực Đà Nẵng", "thành phố Đà Nẵng"],
            "Sơn Trà": ["Son Tra", "quận Sơn Trà"],
            "Ngũ Hành Sơn": ["Ngu Hanh Son", "quận Ngũ Hành Sơn"],
            "Hải Châu": ["Hai Chau", "quận Hải Châu"],
            
            # Discount synonyms
            "giảm giá": ["giảm giá", "khuyến mãi", "ưu đãi", "discount", "sale", "promotion"],
            "voucher": ["voucher", "mã giảm giá", "coupon", "mã khuyến mãi"],
            "ưu đãi": ["ưu đãi", "khuyến mãi", "giảm giá", "promotion"],
            
            # Target audience synonyms
            "sinh viên": ["sinh viên", "student", "học sinh"],
            "khách hàng": ["khách hàng", "customer", "người dùng"],
            
            # Status synonyms
            "còn hiệu lực": ["còn hiệu lực", "đang áp dụng", "active", "valid"],
            "hết hạn": ["hết hạn", "expired", "không còn hiệu lực"],
        }
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text: remove accents, lowercase, remove special chars
        
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
        
        # Convert to lowercase
        text = text.lower()
        
        return text
    
    def expand_synonyms(self, text: str) -> str:
        """
        Expand text with synonyms
        
        Args:
            text: Input text
            
        Returns:
            Text with synonyms expanded
        """
        normalized_text = self.normalize_text(text)
        expanded_text = normalized_text
        
        # Add synonyms for each term
        for term, synonyms in self.synonym_mappings.items():
            if term.lower() in normalized_text:
                # Add synonyms to text
                synonym_list = " ".join(synonyms)
                expanded_text += f" {synonym_list}"
        
        return expanded_text
    
    def _is_coupon_valid(self, coupon: pd.Series) -> bool:
        """
        Check if coupon is currently valid
        
        Args:
            coupon: Coupon row from dataframe
            
        Returns:
            True if coupon is valid, False otherwise
        """
        try:
            now = datetime.now()
            
            # Check start date
            if pd.notna(coupon.get("coupon_start_date")):
                start_date = pd.to_datetime(coupon["coupon_start_date"])
                if now < start_date:
                    return False
            
            # Check end date
            if pd.notna(coupon.get("coupon_end_date")):
                end_date = pd.to_datetime(coupon["coupon_end_date"])
                if now > end_date:
                    return False
            
            # Check quantity
            if pd.notna(coupon.get("coupon_qty_code")):
                qty = int(coupon["coupon_qty_code"])
                if qty <= 0:
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"Error checking coupon validity: {e}")
            return True  # Default to valid if check fails
    
    def _categorize_discount(self, discount_price: float) -> str:
        """Categorize discount into ranges"""
        if discount_price < 10:
            return "giảm giá nhỏ"
        elif discount_price < 20:
            return "giảm giá trung bình"
        elif discount_price < 50:
            return "giảm giá lớn"
        else:
            return "giảm giá rất lớn"
    
    def create_semantic_text(self, coupon: pd.Series) -> str:
        """
        Create semantic-enriched text for coupon
        
        Args:
            coupon: Coupon row from dataframe
            
        Returns:
            Semantic-enriched text
        """
        text_parts = []
        
        # Coupon name - PRIORITY: Repeat multiple times to emphasize coupon name
        if pd.notna(coupon.get("coupon_name")):
            name = str(coupon["coupon_name"]).strip()
            text_parts.append(f"Coupon {name}")
            text_parts.append(f"Tên coupon: {name}")
            # Add normalized name
            normalized_name = self.normalize_text(name)
            text_parts.append(f"Tên chuẩn hóa: {normalized_name}")
            # Add coupon name again
            text_parts.append(f"Voucher {name}")
        
        # Coupon code
        if pd.notna(coupon.get("coupon_name_code")):
            code = str(coupon["coupon_name_code"]).strip()
            text_parts.append(f"Mã coupon: {code}")
            text_parts.append(f"Code: {code}")
        
        # Description with synonyms
        if pd.notna(coupon.get("coupon_desc")):
            desc = str(coupon["coupon_desc"]).strip()
            text_parts.append(f"Mô tả: {desc}")
            # Expand with synonyms
            expanded_desc = self.expand_synonyms(desc)
            if expanded_desc != desc:
                text_parts.append(f"Mô tả mở rộng: {expanded_desc}")
        
        # Discount price
        if pd.notna(coupon.get("coupon_price_sale")):
            discount = float(coupon["coupon_price_sale"])
            text_parts.append(f"Giảm giá: {discount:,.0f}%")
            discount_category = self._categorize_discount(discount)
            text_parts.append(f"Phân loại giảm giá: {discount_category}")
        
        # Validity period
        if pd.notna(coupon.get("coupon_start_date")) and pd.notna(coupon.get("coupon_end_date")):
            start_date = str(coupon["coupon_start_date"])
            end_date = str(coupon["coupon_end_date"])
            text_parts.append(f"Thời gian áp dụng: từ {start_date} đến {end_date}")
        
        # Quantity available
        if pd.notna(coupon.get("coupon_qty_code")):
            qty = int(coupon["coupon_qty_code"])
            text_parts.append(f"Số lượng còn lại: {qty}")
            if qty > 0:
                text_parts.append("Trạng thái: còn hiệu lực")
            else:
                text_parts.append("Trạng thái: hết hàng")
        
        # Validity status
        is_valid = self._is_coupon_valid(coupon)
        if is_valid:
            text_parts.append("Trạng thái: còn hiệu lực")
            text_parts.append("Có thể sử dụng")
        else:
            text_parts.append("Trạng thái: hết hạn")
            text_parts.append("Không thể sử dụng")
        
        # Extract location from description or name
        location = self._extract_location(coupon)
        if location:
            text_parts.append(f"Khu vực áp dụng: {location}")
            # Add location synonyms
            if location in self.synonym_mappings:
                text_parts.append(f"Khu vực mở rộng: {' '.join(self.synonym_mappings[location])}")
        
        # Extract target audience from description or name
        audience = self._extract_target_audience(coupon)
        if audience:
            text_parts.append(f"Đối tượng: {audience}")
        
        return " | ".join(text_parts)
    
    def _extract_location(self, coupon: pd.Series) -> str:
        """Extract location from coupon description or name"""
        text = ""
        if pd.notna(coupon.get("coupon_desc")):
            text += " " + str(coupon["coupon_desc"]).lower()
        if pd.notna(coupon.get("coupon_name")):
            text += " " + str(coupon["coupon_name"]).lower()
        
        # Check for location names
        locations = ["Đà Nẵng", "Sơn Trà", "Ngũ Hành Sơn", "Hải Châu", "Liên Chiểu"]
        for loc in locations:
            if loc.lower() in text:
                return loc
        
        return ""
    
    def _extract_target_audience(self, coupon: pd.Series) -> str:
        """Extract target audience from coupon description or name"""
        text = ""
        if pd.notna(coupon.get("coupon_desc")):
            text += " " + str(coupon["coupon_desc"]).lower()
        if pd.notna(coupon.get("coupon_name")):
            text += " " + str(coupon["coupon_name"]).lower()
        
        # Check for audience keywords
        if "sinh viên" in text or "vku" in text:
            return "sinh viên"
        elif "khách hàng" in text or "customer" in text:
            return "khách hàng"
        
        return ""
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        # Normalize both texts
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        
        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Also check for common words
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return 0.0
        
        # Jaccard similarity
        common_words = words1.intersection(words2)
        jaccard = len(common_words) / len(words1.union(words2))
        
        # Combined similarity
        combined_similarity = (similarity * 0.6) + (jaccard * 0.4)
        
        return combined_similarity
    
    def normalize_coupons(self, coupons_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize all coupons and create enriched dataframe
        
        Args:
            coupons_df: Original coupons dataframe
            
        Returns:
            Normalized dataframe with semantic text
        """
        logger.info("Normalizing coupons...")
        
        normalized_data = []
        
        for idx, coupon in coupons_df.iterrows():
            coupon_id = int(coupon["coupon_id"])
            
            # Create semantic text
            semantic_text = self.create_semantic_text(coupon)
            
            # Create normalized row
            normalized_row = coupon.to_dict()
            normalized_row["semantic_text"] = semantic_text
            normalized_row["normalized_name"] = self.normalize_text(coupon.get("coupon_name", ""))
            normalized_row["discount_category"] = self._categorize_discount(
                float(coupon.get("coupon_price_sale", 0))
            ) if pd.notna(coupon.get("coupon_price_sale")) else ""
            normalized_row["is_valid"] = self._is_coupon_valid(coupon)
            normalized_row["location"] = self._extract_location(coupon)
            normalized_row["target_audience"] = self._extract_target_audience(coupon)
            
            normalized_data.append(normalized_row)
        
        normalized_df = pd.DataFrame(normalized_data)
        logger.info(f"Normalized {len(normalized_df)} coupons")
        
        return normalized_df
    
    def save_mappings(self, output_dir: str = None):
        """Save all mappings to files"""
        import os
        if output_dir is None:
            # Default to rag/normalized_data relative to script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "normalized_data")
        os.makedirs(output_dir, exist_ok=True)
        
        # Save similarity map
        with open(f"{output_dir}/coupon_similarity_map.json", "w", encoding="utf-8") as f:
            json.dump(self.coupon_similarity_map, f, ensure_ascii=False, indent=2)
        
        # Save clusters
        with open(f"{output_dir}/coupon_semantic_clusters.json", "w", encoding="utf-8") as f:
            json.dump(dict(self.semantic_clusters), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved mappings to {output_dir}")


def main():
    """Main function"""
    import os
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from rag/
    
    # Initialize normalizer
    normalizer = CouponDataNormalizer()
    
    # Load data
    logger.info("Loading coupon data...")
    data_dir = os.path.join(project_root, "datasets_extracted")
    coupons_df = pd.read_csv(os.path.join(data_dir, "tbl_coupon.csv"))
    
    logger.info(f"Loaded {len(coupons_df)} coupons")
    
    # Normalize coupons
    normalized_df = normalizer.normalize_coupons(coupons_df)
    
    # Save normalized data
    output_dir = os.path.join(script_dir, "normalized_data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "normalized_coupons.csv")
    normalized_df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved normalized data to {output_file}")
    
    print("\n=== Normalization Complete ===")
    print(f"Normalized {len(normalized_df)} coupons")
    print("\nSample normalized coupons:")
    print(normalized_df[['coupon_id', 'coupon_name', 'is_valid', 'location', 'target_audience']].head())


if __name__ == "__main__":
    main()



