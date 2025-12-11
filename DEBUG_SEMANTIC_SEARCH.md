# Debug Guide: Semantic Search Không Có Kết Quả

## 🔍 Các Bước Kiểm Tra

### 1. Kiểm tra Python Flask API có đang chạy không

```bash
# Kiểm tra process
# Windows:
tasklist | findstr python

# Hoặc test endpoint
curl http://localhost:5000/health
```

**Nếu không chạy:**
```bash
cd Recommendation/recommendation
python api_service.py
```

### 2. Kiểm tra Qdrant có dữ liệu không

```bash
# Test endpoint info
curl http://localhost:5000/api/hotels/info
```

**Nếu collection trống, cần index lại:**
```bash
curl -X POST http://localhost:5000/api/hotels/reload \
  -H "Content-Type: application/json" \
  -d '{"recreate_collection": false}'
```

### 3. Kiểm tra Logs

**Laravel logs:**
```bash
tail -f storage/logs/laravel.log
```

**Python API logs:**
- Xem console output khi chạy `python api_service.py`

### 4. Test Query Preprocessing

Test trực tiếp query preprocessing:

```python
from src.core.query_preprocessor import QueryPreprocessor

preprocessor = QueryPreprocessor()
result = preprocessor.process("Khách sạn ở Ngũ Hành Sơn giá tốt")
print(result)
```

**Kết quả mong đợi:**
```python
{
    "original_query": "Khách sạn ở Ngũ Hành Sơn giá tốt",
    "intent": {
        "price_range": "low",
        ...
    },
    "area_id": 7,  # Ngũ Hành Sơn
    "filters": {
        "area_id": 7,
        "max_price": 2000000
    }
}
```

### 5. Test Semantic Search Trực Tiếp

```bash
curl -X POST http://localhost:5000/api/hotels/semantic-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Khách sạn ở Ngũ Hành Sơn giá tốt",
    "top_k": 10
  }'
```

### 6. Kiểm tra Area Mapping

Xem file `src/core/query_preprocessor.py`:
- `AREA_MAPPING` có chứa "ngũ hành sơn": 7 không?
- Query có match với area name không?

### 7. Kiểm tra Filtering

Có thể filter quá strict:
- `max_price: 2000000` có thể loại bỏ quá nhiều hotels
- Thử tăng `max_price` hoặc bỏ filter này

## 🛠️ Các Vấn Đề Thường Gặp

### Vấn đề 1: Python API không chạy
**Giải pháp:** Start Python Flask API

### Vấn đề 2: Qdrant không có dữ liệu
**Giải pháp:** Index lại hotels:
```bash
POST /api/hotels/reload
```

### Vấn đề 3: Area ID không match
**Giải pháp:** 
- Kiểm tra area_id trong database
- Update AREA_MAPPING trong query_preprocessor.py

### Vấn đề 4: Filter quá strict
**Giải pháp:**
- Tăng `max_price` trong `_build_filters()`
- Hoặc bỏ filter khi không có kết quả (đã implement fallback)

### Vấn đề 5: Vector search không tìm thấy
**Giải pháp:**
- Kiểm tra embeddings có được tạo đúng không
- Thử query đơn giản hơn: "khách sạn đà nẵng"

## 📝 Test Cases

### Test 1: Query đơn giản
```json
{
  "query": "khách sạn đà nẵng",
  "top_k": 10
}
```

### Test 2: Query với area
```json
{
  "query": "khách sạn ở sơn trà",
  "top_k": 10
}
```

### Test 3: Query với price
```json
{
  "query": "khách sạn giá tốt",
  "top_k": 10
}
```

## 🔧 Quick Fix

Nếu vẫn không có kết quả, thử:

1. **Bỏ filter tạm thời:**
   - Comment out filter logic trong `apply_filters()`
   - Xem có kết quả không

2. **Test với query đơn giản:**
   - "khách sạn"
   - "đà nẵng"

3. **Kiểm tra response từ Python API:**
   - Xem logs trong console
   - Check response structure

