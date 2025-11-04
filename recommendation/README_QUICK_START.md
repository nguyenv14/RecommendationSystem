# 🚀 Quick Start - Hotel Recommendation API

Hệ thống semantic hotel recommendation sử dụng **BGE-M3** (via Ollama) + **Qdrant** với Flask API.

## 📋 Tổng quan

- **Embedding Model**: BAAI/bge-m3 (1024 dimensions)
- **Vector Database**: Qdrant
- **API Framework**: Flask
- **Storage**: Persistent trong Qdrant

## ⚡ Quick Start (3 bước)

### Bước 1: Khởi động services

```bash
# Khởi động Qdrant + Ollama
docker-compose up -d qdrant ollama

# Đợi 5 giây để Ollama khởi động
timeout /t 5
```

### Bước 2: Pull BGE-M3 model

```bash
docker exec ollama ollama pull bge-m3
```

### Bước 3: Khởi động API service

```bash
python api_service.py
```

**API sẽ chạy tại**: `http://localhost:5000`

---

## 🎯 Setup lần đầu (Full setup)

```bash
# 1. Khởi động services
docker-compose up -d

# 2. Pull BGE-M3
docker exec ollama ollama pull bge-m3

# 3. Load dữ liệu hotels ban đầu
curl -X POST http://localhost:5000/api/hotels/reload \
  -H "Content-Type: application/json" \
  -d '{
    "csv_path": "datasets_extracted/tbl_hotel.csv",
    "recreate_collection": true
  }'
```

## 📡 API Endpoints chính

### 1. Thêm hotel mới

```bash
POST /api/hotels/process
```

### 2. Lấy hotels tương tự

```bash
GET /api/hotels/{hotel_id}/similar?top_k=10
```

### 3. Search bằng query

```bash
POST /api/hotels/search
```

### 4. Reload database

```bash
POST /api/hotels/reload
```

## 🧪 Testing

```bash
# Test API
python test_api.py

# Hoặc manual
curl http://localhost:5000/health
```

## 📁 Files

- `api_service.py` - Flask API service
- `semantic_recommendation_system.py` - Core recommendation engine
- `docker-compose.yml` - Services orchestration
- `README_API_SERVICE.md` - Chi tiết API docs
- `test_api.py` - Test script

## 🔧 Config

Environment variables:

```bash
OLLAMA_URL=http://localhost:11434
QDRANT_URL=http://localhost:6333
API_PORT=5000
```

## 💡 Example Usage

```python
import requests

# Add new hotel
response = requests.post(
    'http://localhost:5000/api/hotels/process',
    json={
        'hotel_id': 999,
        'hotel_name': 'Luxury Resort',
        'hotel_desc': 'Beautiful hotel description',
        'hotel_placedetails': 'Beach Road, Nha Trang',
        'hotel_tag_keyword': 'luxury, beach, resort',
        'hotel_rank': 5,
        'hotel_price_average': 5000000
    }
)

# Get similar hotels
response = requests.get(
    'http://localhost:5000/api/hotels/2/similar?top_k=5'
)
print(response.json())

# Search by query
response = requests.post(
    'http://localhost:5000/api/hotels/search',
    json={
        'query': 'Khách sạn gần biển Nha Trang',
        'top_k': 10
    }
)
print(response.json())
```

## 🏗️ Architecture

```
┌─────────────────┐
│  Flask API      │ Port 5000
│  (REST API)     │
└────────┬────────┘
         │
         ├── Ollama + BGE-M3 ──> Port 11434
         │   (Embeddings)
         │
         └── Qdrant ──────────────> Port 6333
             (Vector Storage)
```

## 📊 Performance

- **Add 1 hotel**: ~5s
- **Get similar**: ~0.1s
- **Search**: ~0.2s
- **Batch 10**: ~30s

## 🐳 Docker (Optional)

```bash
# Build và start tất cả
docker-compose up --build

# View logs
docker logs hotel_recommendation_api

# Stop
docker-compose down
```

## 📚 Documentation

- [README_API_SERVICE.md](README_API_SERVICE.md) - API chi tiết
- [README_OLLAMA_BGE_M3.md](README_OLLAMA_BGE_M3.md) - BGE-M3 setup
- [README_INCREMENTAL_UPDATE.md](README_INCREMENTAL_UPDATE.md) - Incremental updates

## ✅ Checklist

- [x] Ollama chạy với BGE-M3
- [x] Qdrant chạy và store vectors
- [x] Flask API exposed
- [x] Endpoints hoạt động
- [x] Incremental updates
- [x] Search & recommendations

## 🎉 Hoàn thành!

Hệ thống sẵn sàng sử dụng. Chạy `python api_service.py` và test với `python test_api.py`

