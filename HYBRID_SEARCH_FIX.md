# 🔧 Fix Hybrid Search - Đã Sửa

## ✅ Đã Sửa

### 1. **app.py** - Unset HF_HUB_OFFLINE trước khi import
- Unset `HF_HUB_OFFLINE` ngay đầu file, trước mọi import
- Restore sau khi services đã khởi tạo

### 2. **sparse_embeddings.py** - Lazy import fastembed
- Import `fastembed` chỉ khi cần, sau khi đã unset `HF_HUB_OFFLINE`
- Graceful fallback nếu model không load được

### 3. **run_app.sh** - Comment out HF_HUB_OFFLINE
- Comment out `export HF_HUB_OFFLINE=1` để allow model download
- App sẽ tự động restore nếu cần

## 🚀 Cách Sử Dụng

### Option 1: Chạy app bình thường (Khuyến nghị)
```bash
./run_app.sh
```

App sẽ tự động:
- Unset `HF_HUB_OFFLINE` tạm thời
- Download BM25 model nếu chưa có
- Enable hybrid search
- Restore `HF_HUB_OFFLINE` sau khi xong

### Option 2: Download model trước
```bash
python download_bm25_model.py
./run_app.sh
```

### Option 3: Unset thủ công
```bash
export HF_HUB_OFFLINE=0
python app.py
```

## 🔍 Kiểm Tra

Sau khi chạy app, kiểm tra logs:

### ✅ Hybrid Search Enabled
```
✅ Sparse embedding service initialized (Hybrid Search enabled)
✅ RetrieverService initialized with Hybrid Search (Semantic + Keyword)
```

### ⚠️ Fallback (Semantic Only)
```
⚠️  Sparse embedding model not available
✅ RetrieverService initialized (Semantic only)
```

## 📝 Notes

- Model được cache tại `~/.cache/fastembed/` sau lần download đầu tiên
- Nếu model đã có trong cache, không cần internet để load
- App vẫn chạy được nếu model không load được (fallback về semantic-only)

## 🐛 Troubleshooting

Nếu vẫn gặp lỗi:

1. **Kiểm tra internet connection**
   ```bash
   curl https://huggingface.co
   ```

2. **Xóa cache và download lại**
   ```bash
   rm -rf ~/.cache/fastembed
   python download_bm25_model.py
   ```

3. **Kiểm tra fastembed đã cài đặt**
   ```bash
   pip install fastembed
   ```

4. **Test thủ công**
   ```bash
   python test_hybrid_search.py
   ```
