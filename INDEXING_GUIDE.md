# Hướng dẫn Index Data với Hybrid Search

## 📋 Tổng quan

Để sử dụng Hybrid Search (Semantic + Keyword), bạn cần index dữ liệu với cả **dense vectors** (semantic) và **sparse vectors** (BM25 keyword).

## 🚀 Cách Index

### Option 1: Index với Hybrid Search (Khuyến nghị)

Sử dụng script `index_with_hybrid.py` để index với cả dense và sparse vectors:

```bash
# Chạy script
python index_with_hybrid.py
```

Script này sẽ:
1. ✅ Tạo dense embeddings (semantic) từ Ollama
2. ✅ Tạo sparse embeddings (BM25) từ fastembed
3. ✅ Upload lên Qdrant với cả 2 loại vectors
4. ✅ Hỗ trợ hybrid search ngay sau khi index

### Option 2: Index cơ bản (Dense only)

Sử dụng `setup_collections.py` (chỉ có dense vectors):

```bash
# Set AUTO_INDEX_DATA=true hoặc chạy thủ công
python setup_collections.py
```

**Lưu ý**: Option này chỉ tạo dense vectors, không có sparse vectors. Hybrid search sẽ không hoạt động tối ưu.

## 📊 So sánh

| Feature | `setup_collections.py` | `index_with_hybrid.py` |
|---------|----------------------|----------------------|
| Dense Vectors | ✅ | ✅ |
| Sparse Vectors | ❌ | ✅ |
| Hybrid Search | ⚠️ Limited | ✅ Full |
| Keyword Matching | ❌ | ✅ |
| Tốc độ | Nhanh | Chậm hơn (tạo 2 loại vectors) |

## 🔧 Chi tiết

### 1. Index với Hybrid Search

```bash
# Đảm bảo services đang chạy
# - Qdrant: http://localhost:6333
# - Ollama: http://localhost:11434
# - MySQL: đã có dữ liệu

# Chạy index
python index_with_hybrid.py
```

**Output**:
```
🎯 Indexing Hotels with Hybrid Search
Initializing services...
✅ Sparse embedding service initialized
Fetching hotels from database...
Fetched 150 hotels
Prepared 150 hotels for indexing

📊 Creating dense embeddings...
Embedded 10/150
...

📊 Creating sparse embeddings (BM25)...
Created 150 sparse embeddings

📊 Creating points with hybrid vectors...
Created 150 points

📊 Uploading to Qdrant...
✅ Uploaded 150 points to hotels_recommendation

✅ Indexing completed successfully!
```

### 2. Kiểm tra kết quả

```python
from src.core import VectorStoreService
from src.config import get_settings

vs = VectorStoreService(url=get_settings().QDRANT_URL)
info = vs.get_collection_info("hotels_recommendation")
print(f"Points: {info.points_count}")
print(f"Vectors config: {info.config.params.vectors}")
```

### 3. Test Hybrid Search

```python
from src.core import (
    EmbeddingService, SparseEmbeddingService,
    VectorStoreService, RetrieverService
)

# Initialize services
embedding = EmbeddingService(...)
sparse = SparseEmbeddingService(...)
vectorstore = VectorStoreService(...)

retriever = RetrieverService(
    embedding_service=embedding,
    vectorstore_service=vectorstore,
    sparse_embedding_service=sparse,
    use_hybrid_search=True
)

# Search với hybrid
results = retriever.retrieve(
    query="Khách sạn ABC ở Ngũ Hành Sơn",
    top_k=10
)
# Kết quả sẽ kết hợp semantic + keyword
```

## ⚠️ Lưu ý

### 1. Collections cần có Sparse Vectors

Collections phải được tạo với sparse vectors support:

```python
# Đúng
client.create_collection(
    collection_name="hotels_recommendation",
    vectors_config={"dense": VectorParams(...)},
    sparse_vectors_config={"sparse": SparseVectorParams()}
)

# Sai (chỉ có dense)
client.create_collection(
    collection_name="hotels_recommendation",
    vectors_config=VectorParams(...)
)
```

### 2. Re-index nếu cần

Nếu collections đã có data nhưng chỉ có dense vectors:

```bash
# Option 1: Xóa và tạo lại (mất data cũ)
# Xóa collection trong Qdrant dashboard hoặc:
python -c "from src.core import VectorStoreService; vs = VectorStoreService(); vs.client.delete_collection('hotels_recommendation')"

# Sau đó chạy lại index_with_hybrid.py

# Option 2: Migrate (giữ data, thêm sparse)
# Cần script migration riêng
```

### 3. Performance

- **Dense embeddings**: ~1-2s per batch (10 items) với Ollama
- **Sparse embeddings**: ~0.1s per batch (32 items) với fastembed
- **Total time**: ~5-10 phút cho 1000 hotels

## 🐛 Troubleshooting

### 1. SparseEmbeddingService không khởi tạo

```
Error: Failed to initialize sparse embedding service
```

**Giải pháp**:
- Cài đặt: `pip install fastembed==0.2.11`
- Kiểm tra internet (model download lần đầu)
- Script sẽ fallback về dense-only

### 2. Collections không có sparse vectors

```
Error: Collection doesn't support sparse vectors
```

**Giải pháp**:
- Recreate collections với `enable_sparse=True`
- Hoặc dùng `setup_collections.py` với sparse support

### 3. Index chậm

**Giải pháp**:
- Giảm batch_size
- Tăng cache cho embeddings
- Sử dụng GPU cho Ollama (nếu có)

## 📝 Next Steps

Sau khi index xong:

1. ✅ Test hybrid search qua API
2. ✅ So sánh kết quả semantic vs hybrid
3. ✅ Tune weights nếu cần (trong retriever)

## 🔄 Re-index

Để re-index sau khi có data mới:

```bash
# Chạy lại script
python index_with_hybrid.py
```

Script sẽ upsert (update hoặc insert) points, không duplicate.


