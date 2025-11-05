import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

# -----------------------
# Cấu hình
# -----------------------
DATA_DIR = Path(".")
EVAL_CSV = DATA_DIR / "dataset_evaluates.csv"
ORDERS_CSV = DATA_DIR / "dataset_orders.csv"
ROOMS_CSV = DATA_DIR / "dataset_rooms.csv"
HOTELS_CSV = DATA_DIR / "dataset_hotels.csv"
ORDER_DETAILS_CSV = DATA_DIR / "dataset_order_details.csv"
ORDER_ORDERERS_CSV = DATA_DIR / "dataset_orderers.csv"

OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_DIR.mkdir(exist_ok=True)

# -----------------------
# 1) Đọc file an toàn
# -----------------------
def load_and_prepare_data():
    try:
        df_eval = pd.read_csv(EVAL_CSV, on_bad_lines='skip')
        df_orders = pd.read_csv(ORDERS_CSV, on_bad_lines='skip')
        df_rooms = pd.read_csv(ROOMS_CSV, on_bad_lines='skip')
        df_hotels = pd.read_csv(HOTELS_CSV, on_bad_lines='skip')
        df_order_details = pd.read_csv(ORDER_DETAILS_CSV, on_bad_lines='skip')
        df_orderers = pd.read_csv(ORDER_ORDERERS_CSV, on_bad_lines='skip')
    except Exception as e:
        print(f"[ERROR] Lỗi đọc file: {e}")
        return None, None, None, None, None, None

    # Chuẩn hóa tên cột
    for df in (df_eval, df_orders, df_rooms, df_hotels, df_order_details, df_orderers):
        if df is not None:
            df.columns = df.columns.str.strip()

    return df_eval, df_orders, df_rooms, df_hotels, df_order_details, df_orderers

# -----------------------
# 2) Tính điểm đánh giá cho mỗi đánh giá (và Bayesian average)
# -----------------------
def calculate_hotel_ratings(df_eval, m_prior=50, C_prior=3.5):
    """
    df_eval: DataFrame có các cột điểm (location/service/price/sanitary/convenient)
    Trả về: hotel_stats DataFrame gồm hotel_id, R (mean), v (count), bayes_score
    m_prior, C_prior: tham số cho Bayesian average (m: prior count, C: global mean)
    """
    if df_eval is None or df_eval.empty:
        print("[WARN] df_eval trống")
        return pd.DataFrame(columns=['hotel_id','R','v','bayes_score'])

    # Kiểm tra cột điểm tồn tại
    expected_cols = [
        'evaluate_loaction_point','evaluate_service_point',
        'evaluate_price_point','evaluate_sanitary_point',
        'evaluate_convenient_point'
    ]
    missing = [c for c in expected_cols if c not in df_eval.columns]
    if missing:
        raise ValueError(f"Thiếu cột điểm trong evaluate: {missing}")

    # Tính điểm trung bình trên mỗi đánh giá (normalization nếu cần)
    df_eval = df_eval.copy()
    df_eval['total_point'] = (
        df_eval['evaluate_loaction_point'].astype(float) +
        df_eval['evaluate_service_point'].astype(float) +
        df_eval['evaluate_price_point'].astype(float) +
        df_eval['evaluate_sanitary_point'].astype(float) +
        df_eval['evaluate_convenient_point'].astype(float)
    ) / 5.0

    # tính R (mean) và v (count) cho mỗi hotel
    hotel_stats = df_eval.groupby('hotel_id')['total_point'].agg(R='mean', v='count').reset_index()

    # global mean C (hoặc dùng C_prior nếu bạn muốn)
    C = df_eval['total_point'].mean() if 'total_point' in df_eval else C_prior

    # Bayesian average: (v/(v+m))*R + (m/(v+m))*C
    hotel_stats['bayes_score'] = (hotel_stats['v'] / (hotel_stats['v'] + m_prior)) * hotel_stats['R'] + \
                                 (m_prior / (hotel_stats['v'] + m_prior)) * C

    return hotel_stats

# -----------------------
# 3) Tính độ phổ biến (số đơn đặt) cho mỗi khách sạn
#    - Hỗ trợ trường hợp order_details có/không có hotel_id
# -----------------------
def calculate_booking_popularity(df_orders, df_rooms, df_order_details, df_orderers):
    print("🔧 Đang tính số đơn đặt cho mỗi khách sạn...")

    if df_order_details is None or df_order_details.empty:
        print("[WARN] df_order_details trống")
        return pd.DataFrame(columns=['hotel_id', 'num_orders'])

    od = df_order_details.copy()

    # Nếu order_details không có hotel_id → nối với rooms để lấy hotel_id
    if 'hotel_id' not in od.columns:
        if df_rooms is None or 'room_id' not in df_rooms.columns or 'hotel_id' not in df_rooms.columns:
            raise ValueError("Không tìm thấy hotel_id trong order_details và không thể join từ rooms (thiếu cột).")
        print("   ℹ️ order_details không có hotel_id -> join với rooms để lấy hotel_id")
        od = od.merge(df_rooms[['room_id', 'hotel_id']], on='room_id', how='left')

    # 🧩 Liên kết qua orders -> orderers để lấy customer_id
    if df_orders is not None and 'order_code' in df_orders.columns:
        if 'orderer_id' in df_orders.columns:
            od = od.merge(df_orders[['order_code', 'orderer_id']], on='order_code', how='left')
            print("   ✅ Đã nối order_details với orders để lấy orderer_id")
        else:
            print("   ⚠️ Bảng orders thiếu cột orderer_id -> không thể lấy thông tin người đặt phòng")
    else:
        print("   ⚠️ Không thể nối với bảng orders (thiếu hoặc trống)")

    # Sau khi có orderer_id → nối với orderers để lấy customer_id
    if df_orderers is not None and not df_orderers.empty and 'orderer_id' in df_orderers.columns:
        if 'orderer_id' in od.columns:
            # Chuyển đổi kiểu dữ liệu để tránh lỗi merge
            od['orderer_id'] = od['orderer_id'].astype(str)
            df_orderers_clean = df_orderers[['orderer_id', 'customer_id']].copy()
            df_orderers_clean['orderer_id'] = df_orderers_clean['orderer_id'].astype(str)
            df_orderers_clean = df_orderers_clean.dropna(subset=['orderer_id'])
            
            od = od.merge(df_orderers_clean, on='orderer_id', how='left')
            print("   ✅ Đã nối order_details với orderers để lấy customer_id")
        else:
            print("   ⚠️ order_details chưa có orderer_id sau khi nối orders.")
    else:
        print("   ⚠️ Không thể nối với orderers (thiếu hoặc trống)")

    # Loại bỏ hotel_id bị NaN
    null_hotels = od['hotel_id'].isna().sum()
    if null_hotels:
        print(f"   ⚠️ Có {null_hotels} bản ghi không xác định được hotel_id -> loại bỏ")
        od = od[od['hotel_id'].notna()]

    # Đếm số lượng đơn đặt
    if 'order_id' in od.columns:
        order_counts = od.groupby('hotel_id')['order_id'].nunique().reset_index(name='num_orders')
    else:
        order_counts = od.groupby('hotel_id').size().reset_index(name='num_orders')

    order_counts['num_orders'] = order_counts['num_orders'].astype(int)
    order_counts = order_counts.sort_values('num_orders', ascending=False).reset_index(drop=True)

    total_orders = order_counts['num_orders'].sum() if not order_counts.empty else 0
    print(f"   📊 Kết quả: {len(order_counts)} khách sạn có đơn đặt")
    print(f"   📈 Tổng số đơn: {total_orders}")

    topn = min(5, len(order_counts))
    print(f"\n   🏆 Top {topn} khách sạn có nhiều đơn:")
    for _, row in order_counts.head(topn).iterrows():
        print(f"      Hotel ID {int(row['hotel_id'])}: {int(row['num_orders'])} đơn")

    return order_counts


# -----------------------
# 4) Tạo mapping id -> index (dùng cho embedding)
# -----------------------
def create_id_mappings(df_orders, df_eval, df_hotels, df_orderers):
    user_ids = set()
    hotel_ids = set()

    if df_orderers is not None and 'customer_id' in df_orderers.columns:
        user_ids.update(df_orderers['customer_id'].dropna().unique().tolist())
    if df_eval is not None and 'customer_id' in df_eval.columns:
        user_ids.update(df_eval['customer_id'].dropna().unique().tolist())

    if df_orders is not None and 'hotel_id' in df_orders.columns:
        hotel_ids.update(df_orders['hotel_id'].dropna().unique().tolist())
    if df_eval is not None and 'hotel_id' in df_eval.columns:
        hotel_ids.update(df_eval['hotel_id'].dropna().unique().tolist())
    if df_hotels is not None and 'id' in df_hotels.columns:
        hotel_ids.update(df_hotels['id'].dropna().unique().tolist())

    # 🔧 Ép kiểu về chuỗi (string)
    user_ids = sorted(list(map(str, user_ids)))
    hotel_ids = sorted(list(map(str, hotel_ids)))

    user2idx = {u: i for i, u in enumerate(user_ids)}
    hotel2idx = {h: i for i, h in enumerate(hotel_ids)}

    with open(OUTPUT_DIR / "user2idx.json", "w", encoding="utf-8") as f:
        json.dump(user2idx, f, ensure_ascii=False)
    with open(OUTPUT_DIR / "hotel2idx.json", "w", encoding="utf-8") as f:
        json.dump(hotel2idx, f, ensure_ascii=False)

    # Tính số customers thực sự có interactions
    real_customers = df_eval['customer_id'].dropna().unique() if df_eval is not None else []
    print(f"   🔖 Lưu mapping: {len(user2idx)} total users, {len(real_customers)} real customers, {len(hotel2idx)} hotels -> {OUTPUT_DIR}")
    return user2idx, hotel2idx


# -----------------------
# 5) Visualize top-K hotels by order count
# -----------------------
def plot_top_hotels(order_counts, top_k=20):
    if order_counts is None or order_counts.empty:
        print("[WARN] Không có dữ liệu để vẽ biểu đồ.")
        return

    top = order_counts.head(top_k).copy()
    # convert hotel_id to string for nicer labels
    top['hotel_id'] = top['hotel_id'].astype(str)
    plt.figure(figsize=(10,6))
    plt.barh(top['hotel_id'][::-1], top['num_orders'][::-1])
    plt.xlabel("Number of orders")
    plt.title(f"Top {top_k} hotels by number of orders")
    plt.tight_layout()
    plt.show()

# -----------------------
# 6) Tạo tập interaction từ evaluates
# -----------------------
def create_interactions_from_evaluates(df_eval, user2idx, hotel2idx):
    """
    Tạo interactions từ bảng evaluates
    """
    print("🔧 Tạo interactions từ bảng evaluates...")
    
    if df_eval is None or df_eval.empty:
        print("   ⚠️ Bảng evaluates trống")
        return pd.DataFrame(columns=['user_idx', 'hotel_idx', 'label'])
    
    print(f"   📊 evaluates có {len(df_eval)} dòng")
    
    # Lấy các cột cần thiết
    interactions = df_eval[['customer_id', 'hotel_id']].drop_duplicates()
    print(f"   📊 Sau drop_duplicates: {len(interactions)} dòng")
    
    # Convert to string để so sánh
    interactions['customer_id_str'] = interactions['customer_id'].astype(str)
    interactions['hotel_id_str'] = interactions['hotel_id'].astype(str)
    
    # Kiểm tra mapping
    hotel_in_mapping = interactions['hotel_id_str'].isin(hotel2idx.keys())
    customer_in_mapping = interactions['customer_id_str'].isin(user2idx.keys())
    print(f"   🔍 Hotel trong mapping: {hotel_in_mapping.sum()}")
    print(f"   🔍 Customer trong mapping: {customer_in_mapping.sum()}")
    
    interactions = interactions[
        hotel_in_mapping & customer_in_mapping
    ]
    print(f"   📊 Sau filter mapping: {len(interactions)} dòng")
    
    if len(interactions) > 0:
        interactions['user_idx'] = interactions['customer_id_str'].map(user2idx)
        interactions['hotel_idx'] = interactions['hotel_id_str'].map(hotel2idx)
        interactions['label'] = 1
        
        print(f"   ✅ Tạo được {len(interactions)} interactions từ evaluates")
        return interactions[['user_idx', 'hotel_idx', 'label']]
    else:
        print("   ⚠️ Không tạo được interactions nào từ evaluates")
        return pd.DataFrame(columns=['user_idx', 'hotel_idx', 'label'])


# -----------------------
# 7) Tạo tập interaction (user_idx, hotel_idx, label=1) từ orders
# -----------------------
def build_interaction_table_from_orders(df_order_details, df_orders, df_orderers, df_rooms, user2idx, hotel2idx):
    """
    Trả về DataFrame: user_idx, hotel_idx, label=1
    """

    if df_order_details is None or df_order_details.empty:
        raise ValueError("order_details trống.")

    print(f"   🔍 Debug: order_details có {len(df_order_details)} dòng")
    print(f"   🔍 Debug: order_details columns: {list(df_order_details.columns)}")

    od = df_order_details.copy()

    # 1️⃣ join với orders để lấy orderer_id
    if df_orders is not None and 'order_code' in df_orders.columns and 'orderer_id' in df_orders.columns:
        print(f"   🔍 Debug: orders có {len(df_orders)} dòng")
        od = od.merge(
            df_orders[['order_code', 'orderer_id']],
            on='order_code', how='left'
        )
        print(f"   🔍 Debug: Sau join orders có {len(od)} dòng")
        print(f"   🔍 Debug: Có orderer_id: {od['orderer_id'].notna().sum()}")
    else:
        print(f"   ⚠️ Không thể join với orders")
        print(f"   🔍 Debug: orders columns: {list(df_orders.columns) if df_orders is not None else 'None'}")

    # 2️⃣ join với orderers để lấy customer_id
    if df_orderers is not None and 'orderer_id' in df_orderers.columns and 'customer_id' in df_orderers.columns:
        print(f"   🔍 Debug: orderers có {len(df_orderers)} dòng")
        od = od.merge(
            df_orderers[['orderer_id', 'customer_id']],
            on='orderer_id', how='left'
        )
        print(f"   🔍 Debug: Sau join orderers có {len(od)} dòng")
        print(f"   🔍 Debug: Có customer_id: {od['customer_id'].notna().sum()}")
    else:
        print(f"   ⚠️ Không thể join với orderers")
        print(f"   🔍 Debug: orderers columns: {list(df_orderers.columns) if df_orderers is not None else 'None'}")

    # 3️⃣ join với rooms để lấy hotel_id (nếu cần)
    if 'hotel_id' not in od.columns and df_rooms is not None and 'room_id' in df_rooms.columns and 'hotel_id' in df_rooms.columns:
        print(f"   🔍 Debug: rooms có {len(df_rooms)} dòng")
        od = od.merge(
            df_rooms[['room_id', 'hotel_id']],
            on='room_id', how='left'
        )
        print(f"   🔍 Debug: Sau join rooms có {len(od)} dòng")

    # Kiểm tra các cột cần thiết
    required_cols = ['hotel_id', 'customer_id']
    missing_cols = [col for col in required_cols if col not in od.columns]
    if missing_cols:
        raise ValueError(f"Thiếu cột sau khi join: {missing_cols}")

    od = od.dropna(subset=['hotel_id', 'customer_id'])
    print(f"   🔍 Debug: Sau dropna có {len(od)} dòng")

    interactions = od[['customer_id', 'hotel_id']].drop_duplicates()
    print(f"   🔍 Debug: Sau drop_duplicates có {len(interactions)} dòng")

    # Kiểm tra mapping
    hotel_in_mapping = interactions['hotel_id'].isin(hotel2idx.keys())
    customer_in_mapping = interactions['customer_id'].isin(user2idx.keys())
    print(f"   🔍 Debug: Hotel trong mapping: {hotel_in_mapping.sum()}")
    print(f"   🔍 Debug: Customer trong mapping: {customer_in_mapping.sum()}")

    interactions = interactions[
        hotel_in_mapping & customer_in_mapping
    ]
    print(f"   🔍 Debug: Sau filter mapping có {len(interactions)} dòng")

    interactions['user_idx'] = interactions['customer_id'].map(user2idx)
    interactions['hotel_idx'] = interactions['hotel_id'].map(hotel2idx)
    interactions['label'] = 1

    print(f"   📥 Tạo interaction từ orders: {len(interactions)} cặp customer-hotel (positive).")
    return interactions[['user_idx', 'hotel_idx', 'label']]


# -----------------------
# 7) Simple negative sampling (random)
# -----------------------
def negative_sampling(interactions, num_hotels, neg_ratio=4, seed=42):
    rng = np.random.RandomState(seed)
    user_pos = interactions.groupby('user_idx')['hotel_idx'].apply(set).to_dict()
    neg_rows = []
    all_hotels = np.arange(num_hotels)
    for u, pos_set in user_pos.items():
        n_pos = len(pos_set)
        n_neg = n_pos * neg_ratio
        sampled = set()
        attempts = 0
        max_attempts = n_neg * 10  # Tránh vòng lặp vô hạn
        
        while len(sampled) < n_neg and attempts < max_attempts:
            cand = rng.randint(0, num_hotels)
            if cand not in pos_set:
                sampled.add(cand)
            attempts += 1
        
        for h in sampled:
            neg_rows.append({'user_idx': u, 'hotel_idx': h, 'label': 0})
    
    neg_df = pd.DataFrame(neg_rows)
    combined = pd.concat([interactions, neg_df], ignore_index=True)
    return combined.sample(frac=1, random_state=seed).reset_index(drop=True)

# -----------------------
# Main
# -----------------------
def main():
    df_eval, df_orders, df_rooms, df_hotels, df_order_details, df_orderers = load_and_prepare_data()

    # 1) Ratings per hotel (bayesian)
    try:
        hotel_stats = calculate_hotel_ratings(df_eval)
        hotel_stats.to_csv(OUTPUT_DIR / "hotel_ratings.csv", index=False)
    except Exception as e:
        print(f"[ERROR] Khi tính hotel ratings: {e}")
        hotel_stats = pd.DataFrame()

    # 2) Booking popularity
    try:
        order_counts = calculate_booking_popularity(df_orders, df_rooms, df_order_details, df_orderers)
        order_counts.to_csv(OUTPUT_DIR / "hotel_order_counts.csv", index=False)
    except Exception as e:
        print(f"[ERROR] Khi tính order_counts: {e}")
        order_counts = pd.DataFrame()

    # 3) Mapping ids
    user2idx, hotel2idx = create_id_mappings(df_orders, df_eval, df_hotels, df_orderers)

    # 4) Tạo interaction từ evaluates (positive) + negative sampling
    try:
        interactions_pos = create_interactions_from_evaluates(df_eval, user2idx, hotel2idx)
        if len(interactions_pos) > 0:
            # negative sampling
            num_hotels = len(hotel2idx)
            interactions_all = negative_sampling(interactions_pos, num_hotels=num_hotels, neg_ratio=4)
            interactions_all.to_parquet(OUTPUT_DIR / "interactions_parquet.snappy", index=False)
            print(f"   ✅ Lưu interactions (~{len(interactions_all)}) vào {OUTPUT_DIR}")
        else:
            print("   ⚠️ Không có interactions nào để lưu")
            interactions_all = pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] Khi tạo interactions: {e}")
        interactions_all = pd.DataFrame()

    # 5) Vẽ top hotels
    try:
        plot_top_hotels(order_counts, top_k=20)
    except Exception as e:
        print(f"[WARN] Vẽ biểu đồ thất bại: {e}")

    print("Hoàn tất tiền xử lý. Các file xuất ra:", list(OUTPUT_DIR.iterdir()))

if __name__ == "__main__":
    main()
