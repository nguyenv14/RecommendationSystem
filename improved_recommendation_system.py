#!/usr/bin/env python3
"""
Hệ thống gợi ý mới với model đã được cải thiện
"""

import json
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path

class ImprovedHotelRecommendationSystem:
    def __init__(self, model_dir, processed_dir):
        """
        Khởi tạo hệ thống gợi ý cải thiện
        """
        self.model_dir = Path(model_dir)
        self.processed_dir = Path(processed_dir)
        
        # Load mappings
        self.load_mappings()
        
        # Load model
        self.load_model()
        
        # Load hotel info
        self.load_hotel_info()
        
    def load_mappings(self):
        """Load user và hotel mappings"""
        with open(self.model_dir / "user2idx.json", "r", encoding="utf-8") as f:
            self.user2idx = json.load(f)
        with open(self.model_dir / "hotel2idx.json", "r", encoding="utf-8") as f:
            self.hotel2idx = json.load(f)
        
        # Tạo reverse mappings
        self.idx2user = {v: k for k, v in self.user2idx.items()}
        self.idx2hotel = {v: k for k, v in self.hotel2idx.items()}
        
        print(f"✅ Loaded clean mappings: {len(self.user2idx)} users, {len(self.hotel2idx)} hotels")
    
    def load_model(self):
        """Load model đã cải thiện"""
        model_path = self.model_dir / "saved_model"
        self.model = tf.keras.models.load_model(str(model_path))
        print(f"✅ Loaded improved model from {model_path}")
    
    def load_hotel_info(self):
        """Load thông tin khách sạn"""
        hotels_df = pd.read_csv("../dataset_hotels.csv", on_bad_lines='skip')
        self.hotel_info = hotels_df.set_index('hotel_id').to_dict('index')
        print(f"✅ Loaded info for {len(self.hotel_info)} hotels")
    
    def get_user_recommendations(self, customer_id, k=10):
        """
        Lấy gợi ý khách sạn cho một customer với model cải thiện
        """
        customer_id = str(customer_id)
        
        # Kiểm tra customer có trong clean mapping không
        if customer_id not in self.user2idx:
            print(f"⚠️ Customer {customer_id} không có trong clean dataset")
            print(f"🔄 Chuyển sang gợi ý dựa trên hotels phổ biến...")
            return self.get_popular_hotels(k)
        
        user_idx = self.user2idx[customer_id]
        
        # Load clean interactions để loại bỏ hotels đã thích
        clean_interactions = pd.read_parquet(self.model_dir / "clean_interactions.parquet")
        user_interactions = clean_interactions[clean_interactions['user_idx'] == user_idx]['hotel_idx'].tolist()
        
        # Lấy hotels chưa thích
        all_hotel_indices = list(self.hotel2idx.values())
        unvisited_hotels = [h for h in all_hotel_indices if h not in user_interactions]
        
        if not unvisited_hotels:
            print(f"⚠️ Customer {customer_id} đã thích tất cả hotels!")
            return self.get_popular_hotels(k)
        
        # Tạo predictions
        user_array = np.full(len(unvisited_hotels), user_idx, dtype=np.int32)
        hotel_array = np.array(unvisited_hotels, dtype=np.int32)
        
        scores = self.model.predict({
            'user_idx': user_array,
            'hotel_idx': hotel_array
        }, verbose=0).flatten()
        
        # Sắp xếp theo score
        sorted_indices = np.argsort(-scores)
        
        # Lấy top-k
        recommendations = []
        for i in range(min(k, len(sorted_indices))):
            hotel_idx = unvisited_hotels[sorted_indices[i]]
            hotel_id = self.idx2hotel[hotel_idx]
            score = scores[sorted_indices[i]]
            
            hotel_name = self.hotel_info.get(int(hotel_id), {}).get('hotel_name', f'Hotel {hotel_id}')
            recommendations.append((hotel_id, hotel_name, float(score)))
        
        return recommendations
    
    def get_similar_hotels(self, hotel_id, k=5):
        """Tìm khách sạn tương tự"""
        hotel_id = str(hotel_id)
        
        if hotel_id not in self.hotel2idx:
            print(f"⚠️ Hotel {hotel_id} không có trong clean dataset")
            return []
        
        # Load embeddings từ model cũ (vì model mới không có embeddings riêng)
        old_model_dir = Path("models/ncf_1760783570")
        if old_model_dir.exists():
            hotel_embeddings = np.load(old_model_dir / "item_embeddings.npy")
            
            target_hotel_idx = self.hotel2idx[hotel_id]
            target_embedding = hotel_embeddings[target_hotel_idx]
            
            similarities = []
            for hotel_idx, hotel_id_other in self.idx2hotel.items():
                if hotel_idx != target_hotel_idx:
                    other_embedding = hotel_embeddings[hotel_idx]
                    similarity = np.dot(target_embedding, other_embedding) / (
                        np.linalg.norm(target_embedding) * np.linalg.norm(other_embedding)
                    )
                    hotel_name = self.hotel_info.get(int(hotel_id_other), {}).get('hotel_name', f'Hotel {hotel_id_other}')
                    similarities.append((hotel_id_other, hotel_name, similarity))
            
            similarities.sort(key=lambda x: x[2], reverse=True)
            return similarities[:k]
        
        return []
    
    def get_popular_hotels(self, k=10):
        """Lấy khách sạn phổ biến nhất"""
        order_counts_df = pd.read_csv(self.processed_dir / "hotel_order_counts.csv")
        order_counts_df = order_counts_df.sort_values('num_orders', ascending=False)
        
        recommendations = []
        for _, row in order_counts_df.head(k).iterrows():
            hotel_id = str(int(row['hotel_id']))
            hotel_name = self.hotel_info.get(int(hotel_id), {}).get('hotel_name', f'Hotel {hotel_id}')
            order_count = int(row['num_orders'])
            recommendations.append((hotel_id, hotel_name, order_count))
        
        return recommendations

def main():
    """Demo hệ thống gợi ý cải thiện"""
    print("🚀 Khởi tạo hệ thống gợi ý cải thiện...")
    
    # Sử dụng model clean
    model_dir = Path("models/clean_ncf")
    if not model_dir.exists():
        print(f"❌ Không tìm thấy model clean: {model_dir}")
        return
    
    # Khởi tạo hệ thống
    recommender = ImprovedHotelRecommendationSystem(
        model_dir=model_dir,
        processed_dir=Path(".")
    )
    
    print("\n" + "="*60)
    print("🎯 DEMO HỆ THỐNG GỢI Ý CẢI THIỆN")
    print("="*60)
    
    # Test với các customers khác nhau
    test_customers = ["13", "100", "200", "381"]
    
    for customer_id in test_customers:
        print(f"\n1️⃣ Gợi ý cho customer {customer_id}:")
        recommendations = recommender.get_user_recommendations(customer_id, k=5)
        
        if recommendations:
            for i, (hotel_id, hotel_name, score) in enumerate(recommendations, 1):
                print(f"   {i}. {hotel_name} (ID: {hotel_id}) - Score: {score:.4f}")
        else:
            print("   ⚠️ Không có gợi ý")
    
    # Demo similar hotels
    print(f"\n2️⃣ Khách sạn tương tự với Hotel ID 3:")
    similar_hotels = recommender.get_similar_hotels("3", k=5)
    for i, (hotel_id, hotel_name, similarity) in enumerate(similar_hotels, 1):
        print(f"   {i}. {hotel_name} (ID: {hotel_id}) - Similarity: {similarity:.4f}")
    
    # Demo popular hotels
    print(f"\n3️⃣ Top 5 khách sạn phổ biến:")
    popular_hotels = recommender.get_popular_hotels(k=5)
    for i, (hotel_id, hotel_name, order_count) in enumerate(popular_hotels, 1):
        print(f"   {i}. {hotel_name} (ID: {hotel_id}) - {order_count} đơn đặt")
    
    print("\n✅ Demo hoàn thành!")

if __name__ == "__main__":
    main()
