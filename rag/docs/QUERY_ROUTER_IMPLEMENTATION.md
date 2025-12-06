# Query Router Implementation

## Tổng quan

Đã implement **QueryRouter** để phân loại câu hỏi thành 3 loại:
- **Statistical**: Câu hỏi cần đếm/thống kê → Dùng SQL
- **Semantic**: Câu hỏi tìm kiếm mô tả → Dùng RAG
- **Hybrid**: Câu hỏi cần cả 2 → Kết hợp SQL + RAG

## Cách hoạt động

### Hybrid Approach (Rule-based + LLM)

1. **Bước 1: Rule-based classification** (nhanh, <1ms)
   - Dùng regex patterns để nhận diện keywords
   - Tính confidence score
   - Nếu confidence >= 0.7 → Return kết quả

2. **Bước 2: LLM classification** (nếu confidence < 0.7)
   - Gọi LLM để phân loại thông minh hơn
   - So sánh confidence và chọn kết quả tốt hơn

## Files đã tạo/sửa

### 1. `rag/core/query_router.py`
- Class `QueryRouter` với 2 methods chính:
  - `classify_query()`: Main method (hybrid approach)
  - `_classify_rule_based()`: Rule-based classification
  - `_classify_with_llm()`: LLM-based classification

### 2. `rag/simple_rag_system.py`
- Thêm import `QueryRouter`
- Khởi tạo `query_router` trong `__init__()`
- Modify `ask()` method để:
  - Phân loại câu hỏi trước
  - Route đến handler phù hợp (hiện tại chỉ có RAG, SQL sẽ implement sau)

## Patterns nhận diện

### Statistical Patterns
- Đếm: "có bao nhiêu", "tổng số", "số lượng", "đếm", "có mấy"
- Thống kê: "trung bình", "giá trung bình", "nhiều nhất", "ít nhất"
- Boolean: "có ... không", "có ... chưa", "tồn tại"

### Semantic Patterns
- Tìm kiếm: "khách sạn nào", "tìm khách sạn", "giới thiệu"
- Mô tả: "mô tả", "thông tin", "đặc điểm", "tiện ích"
- Câu hỏi: "có gì", "như thế nào"

## Ví dụ sử dụng

```python
from rag.core.query_router import QueryRouter

# Initialize (có thể dùng với hoặc không có LLM)
router = QueryRouter(use_llm=True, llm=llm_instance)

# Phân loại câu hỏi
result = router.classify_query("Có bao nhiêu khách sạn trong khu vực Ngũ Hành Sơn?")
# → {"type": "statistical", "confidence": 0.8, "method": "rule-based", ...}

result = router.classify_query("Khách sạn nào có view biển đẹp?")
# → {"type": "semantic", "confidence": 0.85, "method": "rule-based", ...}

result = router.classify_query("Có bao nhiêu khách sạn 5 sao có hồ bơi?")
# → {"type": "hybrid", "confidence": 0.7, "method": "rule-based", ...}
```

## Tích hợp vào SimpleRAGSystem

```python
# Trong ask() method
classification = self.query_router.classify_query(question)
query_type = classification["type"]

if query_type == "statistical":
    # TODO: Implement SQL query handler
    return self._ask_with_sql(question)
elif query_type == "hybrid":
    # TODO: Implement hybrid handler
    return self._ask_hybrid(question)
else:  # semantic
    return self._ask_with_rag(question)
```

## Test

Chạy test script:
```bash
python test_query_router_simple.py
```

Hoặc test trong code:
```python
from rag.core.query_router import QueryRouter

router = QueryRouter(use_llm=False)
result = router.classify_query("Có bao nhiêu khách sạn?")
print(result)
```

## Next Steps

1. ✅ **Hoàn thành**: QueryRouter với rule-based + LLM
2. ⏳ **Tiếp theo**: Implement SQL query generator
3. ⏳ **Tiếp theo**: Implement `_ask_with_sql()` method
4. ⏳ **Tiếp theo**: Implement `_ask_hybrid()` method

## Lưu ý

- Hiện tại statistical/hybrid queries vẫn dùng RAG fallback
- Cần implement SQL query generator để trả lời chính xác câu hỏi thống kê
- Confidence threshold có thể điều chỉnh (mặc định: 0.7)

