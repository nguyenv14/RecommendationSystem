import pandas as pd
import matplotlib.pyplot as plt

# Bước 1: Đọc và chuẩn bị dữ liệu
def load_and_prepare_data():
    # Đọc các file CSV (xử lý lỗi định dạng)
    try:
        df_eval = pd.read_csv('dataset_evaluates.csv', on_bad_lines='skip')
        df_orders = pd.read_csv('dataset_orders.csv', on_bad_lines='skip') 
        df_rooms = pd.read_csv('dataset_rooms.csv', on_bad_lines='skip')
        df_hotels = pd.read_csv('dataset_hotels.csv', on_bad_lines='skip')
        df_order_details = pd.read_csv('dataset_order_details.csv', on_bad_lines='skip')
        
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return None, None, None, None, None
    
    # Chuẩn hóa tên cột (loại bỏ khoảng trắng thừa)
    df_eval.columns = df_eval.columns.str.strip()
    df_orders.columns = df_orders.columns.str.strip()
    df_rooms.columns = df_rooms.columns.str.strip()
    df_hotels.columns = df_hotels.columns.str.strip()
    df_order_details.columns = df_order_details.columns.str.strip()

    return df_eval, df_orders, df_rooms, df_hotels, df_order_details

# Bước 2: Tính điểm đánh giá trung bình cho mỗi khách sạn
def calculate_hotel_ratings(df_eval):
    # Tính điểm tổng hợp cho mỗi đánh giá
    df_eval['total_point'] = (
        df_eval['evaluate_loaction_point'] +
        df_eval['evaluate_service_point'] + 
        df_eval['evaluate_price_point'] +
        df_eval['evaluate_sanitary_point'] +
        df_eval['evaluate_convenient_point']
    ) / 5.0
    
    # Tính R (điểm trung bình) và v (số đánh giá) cho mỗi khách sạn
    hotel_stats = df_eval.groupby('hotel_id')['total_point'].agg(
        R='mean',
        v='count'
    ).reset_index()
    
    return hotel_stats

# Bước 3: Tính số lượng đơn đặt cho mỗi khách sạn
def calculate_booking_popularity(df_orders, df_rooms, df_order_details):
    print("🔧 Đang tính số đơn đặt cho mỗi khách sạn...")
    
    
    try:
        # Đếm số đơn đặt theo hotel_id từ order_details
        order_counts = df_order_details.groupby('hotel_id').size().reset_index(name='num_orders')
        
        print(f"   📊 Kết quả: {len(order_counts)} khách sạn có đơn đặt")
        print(f"   📈 Tổng số đơn: {order_counts['num_orders'].sum()}")
        
        # Hiển thị top 5 khách sạn có nhiều đơn nhất
        top5 = order_counts.nlargest(5, 'num_orders')
        print(f"\n   🏆 Top 5 khách sạn có nhiều đơn:")
        for _, row in top5.iterrows():
            print(f"      Hotel ID {int(row['hotel_id'])}: {int(row['num_orders'])} đơn")
        
        return order_counts
        
    except Exception as e:
        print(f"❌ Lỗi khi đếm đơn đặt: {e}")
        # Trả về DataFrame rỗng
        return pd.DataFrame(columns=['hotel_id', 'num_orders'])

# Bước 4: Kết hợp đánh giá và đơn đặt, tính popularity
def combine_ratings_and_orders(hotel_stats, order_counts, alpha=1.0):
    # Gộp dữ liệu đánh giá và đơn đặt
    combined = hotel_stats.merge(order_counts, on='hotel_id', how='left')
    combined['num_orders'] = combined['num_orders'].fillna(0)  # Thay thế NaN bằng 0
    
    # Tính chỉ số popularity kết hợp
    combined['popularity'] = combined['v'] + alpha * combined['num_orders']
    
    return combined

# Bước 5: Tính điểm đề xuất WR (Weighted Rating)
def calculate_weighted_rating(combined_data, quantile=0.75):
    # Tính C - điểm trung bình toàn hệ thống
    C = combined_data['R'].mean()
    
    # Tính m - ngưỡng popularity tối thiểu (phân vị 75)
    m = combined_data['popularity'].quantile(quantile)
    
    # Lọc khách sạn đủ điều kiện
    qualified = combined_data[combined_data['popularity'] >= m].copy()
    
    print(f"Điểm trung bình toàn hệ thống (C): {C:.2f}")
    print(f"Ngưỡng popularity tối thiểu (m): {m:.2f}")
    print(f"Số khách sạn đủ điều kiện: {len(qualified)}")
    
    # Tính Weighted Rating
    def weighted_rating(row, m=m, C=C):
        R = row['R']
        popularity = row['popularity']
        return (popularity / (popularity + m)) * R + (m / (popularity + m)) * C
    
    qualified['WR'] = qualified.apply(weighted_rating, axis=1)
    return qualified

# Bước 6: Hiển thị kết quả
def display_results(qualified_hotels, df_hotels, top_n=10):
    # Gộp với thông tin khách sạn
    result = qualified_hotels.merge(
        df_hotels[['hotel_id', 'hotel_name']],
        on='hotel_id',
        how='left'
    ).sort_values('WR', ascending=False)
    
    # Top khách sạn được đề xuất
    top_recommendations = result.head(top_n)
    
    print(f"\n🎯 TOP {top_n} KHÁCH SẠN ĐỀ XUẤT:")
    print("=" * 80)
    for i, (_, row) in enumerate(top_recommendations.iterrows(), 1):
        print(f"{i:2d}. {row['hotel_name']:<30} | Điểm: {row['WR']:.2f} | "
              f"Đánh giá: {row['R']:.2f} | Số review: {row['v']} | "
              f"Số đơn: {row['num_orders']}")
    
    return result

# Bước 7: Vẽ biểu đồ so sánh
def plot_comparison(result, top_n=10):
    top_hotels = result.head(top_n)
    
    plt.figure(figsize=(14, 8))
    
    # Tạo subplot
    plt.subplot(1, 2, 1)
    bars = plt.barh(range(len(top_hotels)), top_hotels['WR'], color='skyblue')
    plt.yticks(range(len(top_hotels)), top_hotels['hotel_name'])
    plt.gca().invert_yaxis()
    plt.xlabel('Điểm WR (Weighted Rating)')
    plt.title('Top Khách Sạn - Điểm Đề Xuất')
    
    # Thêm giá trị trên mỗi cột
    for i, bar in enumerate(bars):
        plt.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{bar.get_width():.2f}', ha='left', va='center')
    
    plt.subplot(1, 2, 2)
    # So sánh điểm gốc (R) và điểm WR
    x = range(len(top_hotels))
    width = 0.35
    plt.bar([i - width/2 for i in x], top_hotels['R'], width, label='Điểm gốc (R)', alpha=0.7)
    plt.bar([i + width/2 for i in x], top_hotels['WR'], width, label='Điểm WR', alpha=0.7)
    plt.xticks(x, top_hotels['hotel_name'], rotation=45, ha='right')
    plt.ylabel('Điểm số')
    plt.legend()
    plt.title('So sánh: Điểm gốc vs Điểm WR')
    
    plt.tight_layout()
    plt.show()

# Hàm chính
def main():
    print("🚀 BẮT ĐẦU DEMOGRAPHIC FILTERING CHO HỆ THỐNG ĐỀ XUẤT KHÁCH SẠN")
    print("=" * 60)
    
    # 1. Đọc dữ liệu
    df_eval, df_orders, df_rooms, df_hotels, df_order_details = load_and_prepare_data()
    
    if df_eval is None:
        print("❌ Không thể đọc dữ liệu. Vui lòng kiểm tra file CSV.")
        return
    
    print("✅ Đọc dữ liệu thành công")
    
    # 2. Tính toán các chỉ số
    hotel_stats = calculate_hotel_ratings(df_eval)
    order_counts = calculate_booking_popularity(df_orders, df_rooms, df_order_details)
    
    # 3. Thử nghiệm với các giá trị alpha khác nhau
    alphas = [0.5, 1.0, 2.0]
    
    for alpha in alphas:
        print(f"\n🔧 Thử nghiệm với alpha = {alpha}:")
        print("-" * 40)
        
        combined_data = combine_ratings_and_orders(hotel_stats, order_counts, alpha)
        qualified_hotels = calculate_weighted_rating(combined_data)
        result = display_results(qualified_hotels, df_hotels, 3)
        
        # Vẽ biểu đồ cho alpha = 1.0 (có thể thay đổi)
        if alpha == 1.0:
            plot_comparison(result)
    
    print(f"\n🎉 HOÀN TẤT! Đã thử nghiệm {len(alphas)} chiến lược khác nhau.")
    print("💡 Gợi ý: Chọn alpha cho kết quả phù hợp nhất với business goal")

# Chạy chương trình
if __name__ == "__main__":
    main()