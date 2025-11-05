import pandas as pd
import json

def analyze_user_preferences():
    """Phân tích sở thích của users từ clean interactions"""
    
    # Load clean interactions
    clean_interactions = pd.read_parquet('processed/models/clean_ncf/clean_interactions.parquet')
    
    # Load mappings
    with open('processed/models/clean_ncf/user2idx.json', 'r') as f:
        user2idx = json.load(f)
    with open('processed/models/clean_ncf/hotel2idx.json', 'r') as f:
        hotel2idx = json.load(f)
    
    # Reverse mappings
    idx2user = {v: k for k, v in user2idx.items()}
    idx2hotel = {v: k for k, v in hotel2idx.items()}
    
    # Load hotel information
    hotels_df = pd.read_csv('dataset_hotels.csv')
    
    print('🏨 HOTEL INFORMATION:')
    print('=' * 80)
    print(hotels_df[['hotel_id', 'hotel_name', 'hotel_rank', 'hotel_type']].to_string())
    
    print('\n🔍 DETAILED USER PREFERENCE ANALYSIS')
    print('=' * 80)
    
    # Analyze all users
    for user_idx in range(len(user2idx)):
        user_id = idx2user[user_idx]
        user_interactions = clean_interactions[clean_interactions['user_idx'] == user_idx]
        
        if len(user_interactions) == 0:
            continue
            
        liked_hotels = user_interactions[user_interactions['label'] == 1]['hotel_idx'].tolist()
        disliked_hotels = user_interactions[user_interactions['label'] == 0]['hotel_idx'].tolist()
        
        print(f'\n👤 USER {user_id} (Index: {user_idx}):')
        print('-' * 60)
        
        # Liked hotels
        if len(liked_hotels) > 0:
            print('✅ LIKED HOTELS:')
            for hotel_idx in liked_hotels:
                hotel_id = idx2hotel[hotel_idx]
                hotel_info = hotels_df[hotels_df['hotel_id'] == int(hotel_id)]
                if not hotel_info.empty:
                    row = hotel_info.iloc[0]
                    print(f'  Hotel {hotel_id}: {row["hotel_name"]} (Rank: {row["hotel_rank"]}, Type: {row["hotel_type"]})')
        
        # Disliked hotels
        if len(disliked_hotels) > 0:
            print('❌ DISLIKED HOTELS:')
            for hotel_idx in disliked_hotels:
                hotel_id = idx2hotel[hotel_idx]
                hotel_info = hotels_df[hotels_df['hotel_id'] == int(hotel_id)]
                if not hotel_info.empty:
                    row = hotel_info.iloc[0]
                    print(f'  Hotel {hotel_id}: {row["hotel_name"]} (Rank: {row["hotel_rank"]}, Type: {row["hotel_type"]})')
        
        # Pattern analysis
        if len(liked_hotels) > 0:
            liked_hotel_ids = [int(idx2hotel[h]) for h in liked_hotels]
            liked_data = hotels_df[hotels_df['hotel_id'].isin(liked_hotel_ids)]
            
            print(f'\n📊 PREFERENCE PATTERN:')
            print(f'  ✅ Liked - Count: {len(liked_hotels)}')
            print(f'  ✅ Liked - Avg Rank: {liked_data["hotel_rank"].mean():.1f}')
            print(f'  ✅ Liked - Types: {liked_data["hotel_type"].value_counts().to_dict()}')
            
            # Determine preference type
            avg_rank = liked_data["hotel_rank"].mean()
            common_type = liked_data["hotel_type"].mode().iloc[0] if len(liked_data) > 0 else None
            
            if avg_rank >= 4.5:
                rank_pref = "High-end (Rank 4-5)"
            elif avg_rank >= 3.5:
                rank_pref = "Mid-range (Rank 3-4)"
            else:
                rank_pref = "Budget (Rank 1-3)"
            
            type_names = {1: "City Hotels", 2: "Resort Hotels", 3: "Beach Resorts"}
            type_pref = type_names.get(common_type, f"Type {common_type}") if common_type else "Mixed"
            
            print(f'  🎯 Preference: {rank_pref} + {type_pref}')
        
        if len(disliked_hotels) > 0:
            disliked_hotel_ids = [int(idx2hotel[h]) for h in disliked_hotels]
            disliked_data = hotels_df[hotels_df['hotel_id'].isin(disliked_hotel_ids)]
            
            print(f'  ❌ Disliked - Count: {len(disliked_hotels)}')
            print(f'  ❌ Disliked - Avg Rank: {disliked_data["hotel_rank"].mean():.1f}')
            print(f'  ❌ Disliked - Types: {disliked_data["hotel_type"].value_counts().to_dict()}')
        
        print(f'  📈 Total Interactions: {len(user_interactions)}')

def analyze_hotel_characteristics():
    """Phân tích đặc điểm của hotels"""
    
    hotels_df = pd.read_csv('dataset_hotels.csv')
    
    print('\n🏨 HOTEL CHARACTERISTICS ANALYSIS')
    print('=' * 80)
    
    # Rank analysis
    print('📊 RANK DISTRIBUTION:')
    rank_counts = hotels_df['hotel_rank'].value_counts().sort_index()
    for rank, count in rank_counts.items():
        print(f'  Rank {rank}: {count} hotels')
    
    # Type analysis
    print('\n🏷️ TYPE DISTRIBUTION:')
    type_counts = hotels_df['hotel_type'].value_counts().sort_index()
    type_names = {1: "City Hotels", 2: "Resort Hotels", 3: "Beach Resorts"}
    for hotel_type, count in type_counts.items():
        type_name = type_names.get(hotel_type, f"Type {hotel_type}")
        print(f'  {type_name}: {count} hotels')
    
    # Cross analysis
    print('\n🔍 RANK vs TYPE CROSS ANALYSIS:')
    cross_table = pd.crosstab(hotels_df['hotel_rank'], hotels_df['hotel_type'], margins=True)
    print(cross_table)

def analyze_preference_patterns():
    """Phân tích patterns tổng thể của sở thích users"""
    
    # Load clean interactions
    clean_interactions = pd.read_parquet('processed/models/clean_ncf/clean_interactions.parquet')
    
    # Load mappings
    with open('processed/models/clean_ncf/user2idx.json', 'r') as f:
        user2idx = json.load(f)
    with open('processed/models/clean_ncf/hotel2idx.json', 'r') as f:
        hotel2idx = json.load(f)
    
    # Load hotel information
    hotels_df = pd.read_csv('dataset_hotels.csv')
    
    print('\n🎯 OVERALL PREFERENCE PATTERNS')
    print('=' * 80)
    
    # Analyze positive interactions
    pos_interactions = clean_interactions[clean_interactions['label'] == 1]
    pos_hotel_ids = [int(hotel2idx[str(h)]) for h in pos_interactions['hotel_idx']]
    pos_data = hotels_df[hotels_df['hotel_id'].isin(pos_hotel_ids)]
    
    print('✅ POSITIVE INTERACTIONS (Liked Hotels):')
    print(f'  Total: {len(pos_interactions)} interactions')
    print(f'  Avg Rank: {pos_data["hotel_rank"].mean():.1f}')
    print(f'  Rank Distribution: {pos_data["hotel_rank"].value_counts().sort_index().to_dict()}')
    print(f'  Type Distribution: {pos_data["hotel_type"].value_counts().sort_index().to_dict()}')
    
    # Analyze negative interactions
    neg_interactions = clean_interactions[clean_interactions['label'] == 0]
    neg_hotel_ids = [int(hotel2idx[str(h)]) for h in neg_interactions['hotel_idx']]
    neg_data = hotels_df[hotels_df['hotel_id'].isin(neg_hotel_ids)]
    
    print('\n❌ NEGATIVE INTERACTIONS (Disliked Hotels):')
    print(f'  Total: {len(neg_interactions)} interactions')
    print(f'  Avg Rank: {neg_data["hotel_rank"].mean():.1f}')
    print(f'  Rank Distribution: {neg_data["hotel_rank"].value_counts().sort_index().to_dict()}')
    print(f'  Type Distribution: {neg_data["hotel_type"].value_counts().sort_index().to_dict()}')

if __name__ == "__main__":
    analyze_user_preferences()
    analyze_hotel_characteristics()
    analyze_preference_patterns()