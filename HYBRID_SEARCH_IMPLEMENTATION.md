# Hybrid Search Implementation Guide

## 📋 Tổng quan

Đã nâng cấp hệ thống lên **Hybrid Search** kết hợp:
- **Semantic Search** (Dense Vectors): Tìm kiếm theo ý nghĩa ngữ nghĩa
- **Keyword Search** (Sparse Vectors - BM25): Tìm kiếm theo từ khóa chính xác

## ✅ Đã triển khai

### 1. **SparseEmbeddingService** (`src/core/sparse_embeddings.py`)
- Sử dụng `fastembed` với model `Qdrant/bm25`
- Tạo sparse vectors (BM25) cho keyword search
- Hỗ trợ caching để tăng tốc độ

### 2. **Qdrant Collections với Sparse Vectors**
- Collections được tạo với cả `dense` và `sparse` vectors
- Dense: 1024 dims (bge-m3) cho semantic search
- Sparse: BM25 cho keyword search

### 3. **Hybrid Search trong RetrieverService**
- Tự động kết hợp semantic + keyword search
- Sử dụng Qdrant `prefetch` để merge kết quả
- Có thể tắt/bật hybrid search

### 4. **Cập nhật Services**
- `app.py`: Khởi tạo SparseEmbeddingService
- `setup_collections.py`: Tạo collections với sparse vectors
- `vectorstore.py`: Hỗ trợ hybrid search queries

## 🚀 Cách sử dụng

### Tự động (Mặc định)

Hybrid search được bật tự động khi:
- `SparseEmbeddingService` khởi tạo thành công
- Collections có sparse vectors

```python
# RetrieverService tự động sử dụng hybrid search
results = retriever_service.retrieve(
    query="Khách sạn ở Ngũ Hành Sơn",
    top_k=10
)
```

### Tắt Hybrid Search

```python
# Chỉ dùng semantic search
results = retriever_service.retrieve(
    query="Khách sạn ở Ngũ Hành Sơn",
    top_k=10,
    use_hybrid=False
)
```

## 📊 Lợi ích

### 1. **Tìm kiếm chính xác hơn**
- **Semantic**: Hiểu ý nghĩa ("khách sạn gần biển" → tìm hotels có view biển)
- **Keyword**: Bắt từ khóa chính xác ("Khách sạn ABC" → tìm đúng tên)

### 2. **Tốt cho các trường hợp**
- ✅ Tên riêng khách sạn
- ✅ Mã voucher/coupon
- ✅ Địa danh cụ thể
- ✅ Từ khóa kỹ thuật

### 3. **Kết hợp tốt nhất**
- Semantic bắt được ý nghĩa tổng thể
- Keyword đảm bảo độ chính xác cho từ khóa cụ thể

## 🔧 Cấu hình

### Environment Variables

```env
# Sparse embedding cache (optional)
EMBEDDING_CACHE_ENABLED=true
```

### Tạo Collections mới

Collections được tạo tự động với hybrid search khi:
- Chạy `app.py` (tự động tạo collections)
- Chạy `setup_collections.py`

### Re-index với Sparse Vectors

**Lưu ý**: Collections hiện tại chỉ có dense vectors. Để thêm sparse vectors:

1. **Option 1: Recreate collections** (mất dữ liệu cũ)
```python
# Xóa và tạo lại collections
vectorstore_service.create_collection(
    collection_name="hotels_rag",
    vector_size=1024,
    recreate=True,
    enable_sparse=True
)
# Sau đó re-index data
```

2. **Option 2: Migrate collections** (giữ dữ liệu)
- Cần script migration riêng để thêm sparse vectors vào points hiện có

## 📝 API Endpoints

Tất cả search endpoints tự động sử dụng hybrid search:

```bash
# RAG Chat
POST /api/chat
{
  "question": "Khách sạn ABC ở đâu?"
}

# Recommendation
POST /api/recommend/query
{
  "query": "Khách sạn ở Ngũ Hành Sơn"
}

# Semantic Search
POST /api/hotels/semantic-search
{
  "query": "Khách sạn giá tốt"
}
```

## 🐛 Troubleshooting

### 1. SparseEmbeddingService không khởi tạo

**Lỗi**: `Failed to initialize sparse embedding service`

**Giải pháp**:
- Cài đặt `fastembed`: `pip install fastembed==0.2.11`
- Kiểm tra internet connection (model sẽ download lần đầu)
- Hệ thống sẽ fallback về semantic search only

### 2. Collections không có sparse vectors

**Kiểm tra**:
```python
from src.core import VectorStoreService
vs = VectorStoreService(url="http://localhost:6333")
info = vs.get_collection_info("hotels_rag")
print(info.config.params.vectors)  # Should show both dense and sparse
```

**Giải pháp**: Recreate collections với `enable_sparse=True`

### 3. Hybrid search không hoạt động

**Kiểm tra**:
- `sparse_embedding_service` không None
- Collections có sparse vectors
- Logs có message "Using hybrid search"

**Giải pháp**: Kiểm tra logs để xem lỗi cụ thể

## 📚 Tài liệu tham khảo

- [Qdrant Hybrid Search](https://qdrant.tech/documentation/search-precision/reranking-hybrid-search/)
- [FastEmbed Documentation](https://github.com/qdrant/fastembed)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)

## 🔄 Migration từ Semantic-only

Nếu bạn đã có collections với chỉ dense vectors:

1. **Backup data** (nếu cần)
2. **Recreate collections** với `enable_sparse=True`
3. **Re-index data** với `setup_collections.py`

Hoặc giữ nguyên và chỉ dùng semantic search (hybrid sẽ tự động tắt).


