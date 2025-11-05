#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hotel Data Normalization and Semantic Mapping
Chuẩn hóa dữ liệu khách sạn và map các hotels có ngữ nghĩa tương đồng
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HotelDataNormalizer:
    """Chuẩn hóa và map các hotels có ngữ nghĩa tương đồng"""
    
    def __init__(self):
        """Initialize normalizer"""
        self.synonym_mappings = self._load_synonym_mappings()
        self.normalized_hotels = {}
        self.semantic_clusters = defaultdict(list)
        self.hotel_similarity_map = {}
    
    def _load_synonym_mappings(self) -> Dict[str, List[str]]:
        """Load synonym mappings for hotel domain"""
        return {
            # Location synonyms
            "gần biển": ["ven biển", "sát biển", "cách biển", "view biển", "hướng biển", 
                        "đối diện biển", "trực diện biển", "bên bờ biển", "bờ biển"],
            "gần sông": ["ven sông", "sát sông", "cách sông", "view sông", "hướng sông",
                        "bên bờ sông", "bờ sông"],
            "gần trung tâm": ["trung tâm", "trung tâm thành phố", "trong trung tâm",
                             "trung tâm Đà Nẵng"],
            "gần sân bay": ["cách sân bay", "gần sân bay", "sát sân bay"],
            
            # Star rating synonyms
            "5 sao": ["5 sao", "năm sao", "5 stars", "luxury", "cao cấp", "sang trọng"],
            "4 sao": ["4 sao", "bốn sao", "4 stars"],
            "3 sao": ["3 sao", "ba sao", "3 stars"],
            
            # Price synonyms
            "giá rẻ": ["giá rẻ", "giá tốt", "giá hợp lý", "giá phải chăng", "giá thấp"],
            "giá cao": ["giá cao", "giá đắt", "giá đắt đỏ", "premium"],
            
            # Features synonyms
            "hồ bơi": ["hồ bơi", "bể bơi", "pool", "swimming pool"],
            "spa": ["spa", "massage", "thư giãn"],
            "gym": ["gym", "phòng gym", "thể hình", "fitness"],
            "nhà hàng": ["nhà hàng", "restaurant", "quán ăn"],
            
            # View synonyms
            "view biển": ["view biển", "hướng biển", "nhìn ra biển", "tầm nhìn biển"],
            "view sông": ["view sông", "hướng sông", "nhìn ra sông", "tầm nhìn sông"],
            "view thành phố": ["view thành phố", "hướng thành phố", "nhìn ra thành phố"],
            
            # Area synonyms
            "Sơn Trà": ["Sơn Trà", "Son Tra", "quận Sơn Trà"],
            "Ngũ Hành Sơn": ["Ngũ Hành Sơn", "Ngu Hanh Son", "quận Ngũ Hành Sơn"],
            "Hải Châu": ["Hải Châu", "Hai Chau", "quận Hải Châu"],
            "Liên Chiểu": ["Liên Chiểu", "Lien Chieu", "quận Liên Chiểu"],
            
            # Beach synonyms
            "Mỹ Khê": ["Mỹ Khê", "My Khe", "bãi biển Mỹ Khê", "beach Mỹ Khê"],
            "Non Nước": ["Non Nước", "Non Nuoc", "bãi biển Non Nước"],
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
        
        # Remove accents (optional - can keep or remove)
        # text = unicodedata.normalize('NFD', text)
        # text = text.encode('ascii', 'ignore').decode('utf-8')
        
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
            if term in normalized_text:
                # Add synonyms to text
                synonym_list = " ".join(synonyms)
                expanded_text += f" {synonym_list}"
        
        return expanded_text
    
    def create_semantic_text(self, hotel: pd.Series) -> str:
        """
        Create semantic-enriched text for hotel
        
        Args:
            hotel: Hotel row from dataframe
            
        Returns:
            Semantic-enriched text
        """
        text_parts = []
        
        # Hotel name
        if pd.notna(hotel.get("hotel_name")):
            name = str(hotel["hotel_name"]).strip()
            text_parts.append(f"Tên khách sạn: {name}")
            # Add normalized name
            text_parts.append(f"Tên chuẩn hóa: {self.normalize_text(name)}")
        
        # Description with synonyms
        if pd.notna(hotel.get("hotel_desc")):
            desc = str(hotel["hotel_desc"]).strip()
            text_parts.append(f"Mô tả: {desc}")
            # Expand with synonyms
            expanded_desc = self.expand_synonyms(desc)
            if expanded_desc != desc:
                text_parts.append(f"Mô tả mở rộng: {expanded_desc}")
        
        # Address
        if pd.notna(hotel.get("hotel_placedetails")):
            address = str(hotel["hotel_placedetails"]).strip()
            text_parts.append(f"Địa chỉ: {address}")
            # Extract area from address
            area_extracted = self._extract_area_from_address(address)
            if area_extracted:
                text_parts.append(f"Khu vực trích xuất: {area_extracted}")
        
        # Area name
        if pd.notna(hotel.get("area_name")):
            area = str(hotel["area_name"]).strip()
            text_parts.append(f"Khu vực: {area}")
            # Add synonyms
            if area in self.synonym_mappings:
                text_parts.append(f"Khu vực mở rộng: {' '.join(self.synonym_mappings[area])}")
        
        # Brand
        if pd.notna(hotel.get("brand_name")):
            brand = str(hotel["brand_name"]).strip()
            text_parts.append(f"Thương hiệu: {brand}")
        
        # Keywords
        if pd.notna(hotel.get("hotel_tag_keyword")):
            keywords = str(hotel["hotel_tag_keyword"]).strip()
            text_parts.append(f"Từ khóa: {keywords}")
            # Expand keywords
            expanded_keywords = self.expand_synonyms(keywords)
            if expanded_keywords != keywords:
                text_parts.append(f"Từ khóa mở rộng: {expanded_keywords}")
        
        # Rank
        if pd.notna(hotel.get("hotel_rank")):
            rank = int(hotel["hotel_rank"])
            text_parts.append(f"Hạng: {rank} sao")
            # Add synonyms
            if rank == 5:
                text_parts.append("Hạng mở rộng: luxury cao cấp sang trọng")
            elif rank == 4:
                text_parts.append("Hạng mở rộng: 4 stars")
            elif rank == 3:
                text_parts.append("Hạng mở rộng: 3 stars")
        
        # Price range category
        if pd.notna(hotel.get("hotel_price_average")):
            price = float(hotel["hotel_price_average"])
            price_category = self._categorize_price(price)
            text_parts.append(f"Giá trung bình: {price:,.0f} VND")
            text_parts.append(f"Phân loại giá: {price_category}")
        
        return " | ".join(text_parts)
    
    def _extract_area_from_address(self, address: str) -> str:
        """Extract area name from address"""
        address_lower = address.lower()
        
        # Check for area names
        for area in ["Sơn Trà", "Ngũ Hành Sơn", "Hải Châu", "Liên Chiểu", 
                     "Cẩm Lệ", "Thanh Khê", "Hòa Vang"]:
            if area.lower() in address_lower:
                return area
        
        return ""
    
    def _categorize_price(self, price: float) -> str:
        """Categorize price into ranges"""
        if price < 1000000:
            return "giá rẻ"
        elif price < 2000000:
            return "giá trung bình"
        elif price < 3000000:
            return "giá cao"
        else:
            return "giá rất cao"
    
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
    
    def find_similar_hotels(self, hotels_df: pd.DataFrame, similarity_threshold: float = 0.3) -> Dict[int, List[Tuple[int, float]]]:
        """
        Find similar hotels based on semantic similarity
        
        Args:
            hotels_df: Hotels dataframe
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            Dictionary mapping hotel_id to list of (similar_hotel_id, similarity_score)
        """
        logger.info("Finding similar hotels...")
        
        hotel_similarities = defaultdict(list)
        
        # Create semantic texts for all hotels
        hotel_texts = {}
        for idx, hotel in hotels_df.iterrows():
            hotel_id = int(hotel["hotel_id"])
            semantic_text = self.create_semantic_text(hotel)
            hotel_texts[hotel_id] = semantic_text
        
        # Compare all pairs
        hotel_ids = list(hotel_texts.keys())
        n_hotels = len(hotel_ids)
        
        for i, hotel_id1 in enumerate(hotel_ids):
            if i % 5 == 0:
                logger.info(f"Processing {i+1}/{n_hotels} hotels...")
            
            for hotel_id2 in hotel_ids[i+1:]:
                text1 = hotel_texts[hotel_id1]
                text2 = hotel_texts[hotel_id2]
                
                similarity = self.calculate_similarity(text1, text2)
                
                if similarity >= similarity_threshold:
                    hotel_similarities[hotel_id1].append((hotel_id2, similarity))
                    hotel_similarities[hotel_id2].append((hotel_id1, similarity))
        
        # Sort by similarity
        for hotel_id in hotel_similarities:
            hotel_similarities[hotel_id].sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Found similarities for {len(hotel_similarities)} hotels")
        return hotel_similarities
    
    def create_semantic_clusters(self, hotels_df: pd.DataFrame, similarity_threshold: float = 0.4) -> Dict[int, List[int]]:
        """
        Create semantic clusters of similar hotels
        
        Args:
            hotels_df: Hotels dataframe
            similarity_threshold: Minimum similarity for clustering
            
        Returns:
            Dictionary mapping cluster_id to list of hotel_ids
        """
        logger.info("Creating semantic clusters...")
        
        # Find similar hotels
        similarities = self.find_similar_hotels(hotels_df, similarity_threshold)
        
        # Create clusters using simple greedy approach
        clusters = {}
        assigned = set()
        cluster_id = 0
        
        for hotel_id, similar_list in similarities.items():
            if hotel_id in assigned:
                continue
            
            # Create new cluster
            cluster = [hotel_id]
            assigned.add(hotel_id)
            
            # Add similar hotels to cluster
            for similar_id, sim_score in similar_list:
                if similar_id not in assigned and sim_score >= similarity_threshold:
                    cluster.append(similar_id)
                    assigned.add(similar_id)
            
            clusters[cluster_id] = cluster
            cluster_id += 1
        
        # Add unassigned hotels as single-item clusters
        for idx, hotel in hotels_df.iterrows():
            hotel_id = int(hotel["hotel_id"])
            if hotel_id not in assigned:
                clusters[cluster_id] = [hotel_id]
                cluster_id += 1
        
        logger.info(f"Created {len(clusters)} clusters")
        return clusters
    
    def normalize_hotels(self, hotels_df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize all hotels and create enriched dataframe
        
        Args:
            hotels_df: Original hotels dataframe
            
        Returns:
            Normalized dataframe with semantic text
        """
        logger.info("Normalizing hotels...")
        
        normalized_data = []
        
        for idx, hotel in hotels_df.iterrows():
            hotel_id = int(hotel["hotel_id"])
            
            # Create semantic text
            semantic_text = self.create_semantic_text(hotel)
            
            # Create normalized row
            normalized_row = hotel.to_dict()
            normalized_row["semantic_text"] = semantic_text
            normalized_row["normalized_name"] = self.normalize_text(hotel.get("hotel_name", ""))
            normalized_row["price_category"] = self._categorize_price(
                float(hotel.get("hotel_price_average", 0))
            )
            
            # Extract features
            normalized_row["extracted_area"] = self._extract_area_from_address(
                str(hotel.get("hotel_placedetails", ""))
            )
            
            normalized_data.append(normalized_row)
        
        normalized_df = pd.DataFrame(normalized_data)
        logger.info(f"Normalized {len(normalized_df)} hotels")
        
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
        with open(f"{output_dir}/hotel_similarity_map.json", "w", encoding="utf-8") as f:
            json.dump(self.hotel_similarity_map, f, ensure_ascii=False, indent=2)
        
        # Save clusters
        with open(f"{output_dir}/semantic_clusters.json", "w", encoding="utf-8") as f:
            json.dump(dict(self.semantic_clusters), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved mappings to {output_dir}")


def main():
    """Main function"""
    import os
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from rag/
    
    # Initialize normalizer
    normalizer = HotelDataNormalizer()
    
    # Load data
    logger.info("Loading hotel data...")
    data_dir = os.path.join(project_root, "datasets_extracted")
    hotels_df = pd.read_csv(os.path.join(data_dir, "tbl_hotel.csv"))
    areas_df = pd.read_csv(os.path.join(data_dir, "tbl_area.csv"))
    brands_df = pd.read_csv(os.path.join(data_dir, "tbl_brand.csv"))
    
    # Join tables
    hotels_df = hotels_df.merge(areas_df[["area_id", "area_name", "area_desc"]], 
                                on="area_id", how="left")
    hotels_df = hotels_df.merge(brands_df[["brand_id", "brand_name", "brand_desc"]], 
                                on="brand_id", how="left")
    
    logger.info(f"Loaded {len(hotels_df)} hotels")
    
    # Normalize hotels
    normalized_df = normalizer.normalize_hotels(hotels_df)
    
    # Save normalized data
    output_dir = os.path.join(script_dir, "normalized_data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "normalized_hotels.csv")
    normalized_df.to_csv(output_file, index=False, encoding="utf-8")
    logger.info(f"Saved normalized data to {output_file}")
    
    # Find similar hotels
    logger.info("\n=== Finding Similar Hotels ===")
    similarities = normalizer.find_similar_hotels(hotels_df, similarity_threshold=0.3)
    normalizer.hotel_similarity_map = {str(k): [(str(id), float(score)) for id, score in v] 
                                       for k, v in similarities.items()}
    
    # Print top similar hotels
    print("\n=== Top Similar Hotels ===")
    for hotel_id, similar_list in list(similarities.items())[:5]:
        hotel_name = hotels_df[hotels_df["hotel_id"] == hotel_id]["hotel_name"].values[0]
        print(f"\nHotel: {hotel_name} (ID: {hotel_id})")
        print("Similar hotels:")
        for similar_id, sim_score in similar_list[:5]:
            similar_name = hotels_df[hotels_df["hotel_id"] == similar_id]["hotel_name"].values[0]
            print(f"  - {similar_name} (ID: {similar_id}, similarity: {sim_score:.3f})")
    
    # Create semantic clusters
    logger.info("\n=== Creating Semantic Clusters ===")
    clusters = normalizer.create_semantic_clusters(hotels_df, similarity_threshold=0.4)
    normalizer.semantic_clusters = clusters
    
    # Print clusters
    print("\n=== Semantic Clusters ===")
    for cluster_id, hotel_ids in list(clusters.items())[:5]:
        print(f"\nCluster {cluster_id}:")
        for hotel_id in hotel_ids:
            hotel_name = hotels_df[hotels_df["hotel_id"] == hotel_id]["hotel_name"].values[0]
            print(f"  - {hotel_name} (ID: {hotel_id})")
    
    # Save mappings
    normalizer.save_mappings()
    
    print("\n=== Normalization Complete ===")
    print(f"Normalized {len(normalized_df)} hotels")
    print(f"Found similarities for {len(similarities)} hotels")
    print(f"Created {len(clusters)} clusters")


if __name__ == "__main__":
    main()

