# 🚀 Quick Start - 1 Lệnh Duy Nhất!

## Chạy toàn bộ hệ thống:

```bash
# Linux/Mac
./run_app.sh

# Windows
run_app.bat
```

**Xong!** Chỉ 1 lệnh, hệ thống tự động:
1. ✅ Start Docker (Qdrant, MySQL, Redis)
2. ✅ Tạo collections (RAG + Recommendation)
3. ✅ Index data từ database (nếu AUTO_INDEX_DATA=true)
4. ✅ Khởi động app trên `http://localhost:5000`

---

## 🎯 Chi tiết

### Mặc định (Nhanh):
```bash
./run_app.sh  # Chỉ tạo collections, KHÔNG index data
```

- Collections được tạo nhưng trống
- App khởi động ngay lập tức
- Có thể index data sau

### Auto-index data (Đầy đủ):
```bash
export AUTO_INDEX_DATA=true  # Enable auto-index
./run_app.sh                  # Tạo + index + khởi động
```

- Collections được tạo VÀ filled với data
- **RAG**: Index hotels + coupons cho chatbot
- **Recommendation**: Index hotels cho gợi ý tương tự
- Mất thêm ~5-10 phút để index

---

## 📊 Kiểm tra

### Health check:
```bash
curl http://localhost:5000/health
```

### Verify collections:
```bash
python scripts/verify_collections.py
```

Kết quả mong đợi:
```
hotels_rag              | RAG            | 22 points
coupons_rag             | RAG            | 4 points
hotels_recommendation   | Recommendation | 22 points
```

---

## 🔧 Troubleshooting

### Collections trống?
```bash
# Chạy lại với AUTO_INDEX_DATA=true
export AUTO_INDEX_DATA=true
./run_app.sh
```

### Hoặc index thủ công:
```bash
# RAG
cd rag/ && python simple_rag_system.py

# Recommendation
cd recommendation/ && python semantic_recommendation_system.py
```

### Port conflicts?
```bash
# Thay đổi port
export PORT=8000
./run_app.sh
```

---

## 📚 Tài liệu

- **Chi tiết**: `SETUP_GUIDE.md`
- **API**: `COMPLETE_RECOMMENDATION_SYSTEMS.md`
- **Database**: `DATABASE_INTEGRATION.md`

