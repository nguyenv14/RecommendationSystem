# 📊 Phân Tích Xung Đột Collections

## Vấn đề phát hiện

### 1. RAG System
- **File**: `rag/simple_rag_system.py` (line 128)
- **Collection**: `"hotels"` (mặc định, có thể config)
- **Mục đích**: Lưu hotels, rooms, coupons với semantic text cho RAG chatbot

### 2. Recommendation System
- **File**: `recommendation/semantic_recommendation_system.py` (line 68)
- **Collection**: `"hotel_recommendations"` (hard-coded)
- **Mục đích**: Lưu hotel embeddings cho semantic similarity search

### 3. Unified Service
- **File**: `unified_api_service.py` (line 91)
- **Collection**: Dùng `COLLECTION_NAME` env var, mặc định = `"hotels"`
- **Vấn đề**: Chỉ config cho RAG, không config cho Recommendation!

## ⚠️ Xung đột tiềm ẩn

### Hiện tại: KHÔNG xung đột trực tiếp
- RAG dùng: `"hotels"`
- Recommendation dùng: `"hotel_recommendations"`
- ✅ 2 collections khác nhau → Không xung đột data

### Nhưng có vấn đề:
1. ❌ **Hard-coded** collection name trong Recommendation
2. ❌ **Không config được** từ environment
3. ❌ **Khó maintain** khi scale
4. ❌ **Tốn tài nguyên** khi 2 hệ thống index cùng data
5. ❌ **Cấu trúc folder** không rõ ràng, khó maintain

## 💡 Giải pháp đề xuất

### Option 1: Unified Collection (Recommended)
Gộp cả 2 vào 1 collection `"hotels_unified"` với metadata phân biệt:
- `document_type = "hotel"` → RAG hotel data
- `document_type = "coupon"` → RAG coupon data
- `document_type = "room"` → RAG room data
- `source_system = "recommendation"` → Recommendation embeddings

**Ưu điểm**:
- ✅ Tiết kiệm tài nguyên (1 collection thay vì 2-3)
- ✅ Dễ maintain và backup
- ✅ Có thể filter theo metadata
- ✅ Tránh duplicate data

**Nhược điểm**:
- ⚠️ Cần refactor cả 2 systems
- ⚠️ Cần cẩn thận với metadata filtering

### Option 2: Separate Collections với Config (Current + Improvements)
Giữ 2 collections riêng nhưng làm configurable:
- `"hotels_rag"` → RAG system
- `"hotels_recommendation"` → Recommendation system

**Ưu điểm**:
- ✅ Tách biệt rõ ràng
- ✅ Ít phải refactor
- ✅ Mỗi system độc lập

**Nhược điểm**:
- ⚠️ Tốn tài nguyên hơn
- ⚠️ Duplicate hotel data

## 🎯 Quyết định: Option 2 + Restructure

Tôi sẽ:
1. ✅ Tái cấu trúc folder theo clean architecture
2. ✅ Tạo shared modules cho common utilities
3. ✅ Config riêng cho từng collection
4. ✅ Centralized configuration management
5. ✅ Clear separation of concerns

