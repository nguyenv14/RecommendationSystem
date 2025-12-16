# 🔍 Enable Hybrid Search - Hướng Dẫn

## Vấn Đề

Khi chạy ứng dụng, bạn có thể thấy lỗi:
```
ERROR - Could not download model from HuggingFace: offline mode is enabled
ERROR - Error loading sparse embedding model: Could not load model Qdrant/bm25
```

Điều này xảy ra vì:
- `HF_HUB_OFFLINE=1` được set trong environment
- Model BM25 chưa được download
- Hybrid search bị disable, chỉ dùng semantic search

## ✅ Giải Pháp

### Cách 1: Download Model Tự Động (Khuyến Nghị)

Chạy script helper để download model:

```bash
python download_bm25_model.py
```

Script này sẽ:
- Tạm thời unset `HF_HUB_OFFLINE`
- Download model `Qdrant/bm25` từ HuggingFace
- Test model để đảm bảo hoạt động
- Restore `HF_HUB_OFFLINE` sau khi xong

### Cách 2: Unset HF_HUB_OFFLINE Tạm Thời

```bash
# Unset trong terminal hiện tại
unset HF_HUB_OFFLINE

# Hoặc set = 0
export HF_HUB_OFFLINE=0

# Chạy app
python app.py
```

Model sẽ được download tự động khi app khởi động.

### Cách 3: Download Model Thủ Công

```bash
# Unset HF_HUB_OFFLINE
export HF_HUB_OFFLINE=0

# Download model
python -c "from fastembed import SparseTextEmbedding; SparseTextEmbedding('Qdrant/bm25')"

# Restore HF_HUB_OFFLINE nếu cần
export HF_HUB_OFFLINE=1
```

## 🔍 Kiểm Tra Hybrid Search Đã Enable

Sau khi download model, restart app và kiểm tra logs:

### ✅ Hybrid Search Enabled
```
✅ Sparse embedding service initialized (Hybrid Search enabled)
✅ RetrieverService initialized with Hybrid Search (Semantic + Keyword)
```

### ⚠️ Hybrid Search Disabled (Fallback)
```
⚠️  Sparse embedding model not available
✅ RetrieverService initialized (Semantic only)
```

## 📊 Lợi Ích Hybrid Search

Hybrid search kết hợp:
- **Semantic Search** (Dense Vectors): Hiểu ý nghĩa ngữ nghĩa
- **Keyword Search** (Sparse Vectors - BM25): Tìm kiếm từ khóa chính xác

**Ví dụ:**
- Query: "Khách sạn ABC" → Keyword search tìm đúng tên
- Query: "khách sạn gần biển" → Semantic search hiểu ý nghĩa

## 🛠️ Troubleshooting

### Lỗi: "Cannot reach https://huggingface.co"
- Kiểm tra internet connection
- Kiểm tra firewall/proxy settings
- Thử truy cập https://huggingface.co trong browser

### Lỗi: "Model not found"
- Đảm bảo `fastembed` đã được cài đặt: `pip install fastembed`
- Kiểm tra model name: `Qdrant/bm25`

### Model đã download nhưng vẫn báo lỗi
- Xóa cache và download lại:
  ```bash
  rm -rf ~/.cache/fastembed
  python download_bm25_model.py
  ```

## 📝 Notes

- Model được cache tại `~/.cache/fastembed/` sau lần download đầu tiên
- Nếu `HF_HUB_OFFLINE=1`, app vẫn chạy được nhưng chỉ dùng semantic search
- Hybrid search tự động fallback về semantic-only nếu BM25 không available
