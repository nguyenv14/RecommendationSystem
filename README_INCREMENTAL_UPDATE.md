# Incremental Updates - Thêm Hotels Mới Không Cần Chạy Lại Toàn Bộ

## Vấn đề

Khi có thêm hotels mới, hệ thống cũ sẽ:
- ❌ Chạy lại model cho TẤT CẢ hotels (22 hotels cũ + hotels mới)
- ❌ Tạo lại embeddings cho toàn bộ
- ❌ Mất thời gian và tài nguyên không cần thiết

## Giải pháp

Với incremental update:
- ✅ Chỉ tạo embeddings cho hotels mới
- ✅ Không xóa hotels cũ
- ✅ Chỉ add hotels mới vào Qdrant
- ✅ Nhanh và hiệu quả hơn nhiều

## Cách sử dụng

### 1. Lần đầu tiên (Create collection)

```python
from semantic_recommendation_system import SemanticRecommendationSystem

system = SemanticRecommendationSystem(use_ollama=True)

# Load data
hotels_df = pd.read_csv('datasets_extracted/tbl_hotel.csv')

# Index all hotels (creates new collection)
system.index_hotels(hotels_df, recreate_collection=True)
```

### 2. Thêm hotels mới (Incremental)

```python
from semantic_recommendation_system import SemanticRecommendationSystem

system = SemanticRecommendationSystem(use_ollama=True)

# Load hotels mới
new_hotels_df = pd.DataFrame({
    'hotel_id': [101, 102],
    'hotel_name': ['New Hotel 1', 'New Hotel 2'],
    'hotel_desc': ['Description...', 'Description...'],
    # ... other fields
})

# Chỉ add hotels mới, không recreate collection
system.add_new_hotels(new_hotels_df)
```

### 3. Chạy example

```bash
python example_incremental_update.py
```

## So sánh hiệu suất

### Cũ (Không tối ưu):
```
22 hotels cũ → Embeddings: 22 requests
2 hotels mới → Embeddings: 24 requests (create lại tất cả)
Total: 24 requests
Time: ~60 seconds
```

### Mới (Incremental):
```
22 hotels cũ → Đã có sẵn trong Qdrant
2 hotels mới → Embeddings: 2 requests
Total: 2 requests  
Time: ~5 seconds
```

## Ưu điểm

1. **Nhanh hơn**: Chỉ xử lý hotels mới
2. **Tiết kiệm**: Không waste resources cho hotels đã có
3. **Cache friendly**: Sử dụng cache embeddings trong memory
4. **Scalable**: Dễ scale khi có nhiều hotels mới

## Notes

- Hotels mới phải có `hotel_id` khác với hotels đã có
- Hệ thống tự động detect hotels nào là mới
- Embeddings được cache trong memory để nhất quán

