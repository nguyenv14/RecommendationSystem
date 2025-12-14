# Docker Setup Guide - Unified API Service

Hướng dẫn container hóa và chạy API service cho Recommendation và RAG system.

## 📋 Yêu cầu

- Docker Engine 20.10+
- Docker Compose 2.0+
- Tối thiểu 4GB RAM
- Tối thiểu 10GB dung lượng ổ cứng

## 🚀 Quick Start

### 1. Build và chạy tất cả services

```bash
docker-compose up -d
```

Lệnh này sẽ khởi động:
- **Qdrant** (Vector Database) - Port 6333
- **Redis** (Cache) - Port 6380
- **MySQL** (Database) - Port 3308
- **phpMyAdmin** - Port 8181
- **Unified API** (RAG + Recommendation) - Port 5000

### 2. Chỉ build và chạy API service

```bash
# Build image
docker-compose build unified_api

# Chạy service
docker-compose up -d unified_api
```

### 3. Xem logs

```bash
# Tất cả services
docker-compose logs -f

# Chỉ API service
docker-compose logs -f unified_api
```

### 4. Dừng services

```bash
# Dừng tất cả
docker-compose down

# Dừng và xóa volumes (⚠️ Xóa dữ liệu)
docker-compose down -v
```

## 🔧 Cấu hình

### Environment Variables

Các biến môi trường có thể được cấu hình trong `docker-compose.yml` hoặc tạo file `.env`:

```env
# Service
PORT=5000
HOST=0.0.0.0
DEBUG=False

# Qdrant
QDRANT_URL=http://qdrant:6333

# MySQL
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=myhotel

# Redis
REDIS_URL=redis://redis:6379

# Ollama (external)
OLLAMA_URL=http://host.docker.internal:11434
EMBEDDING_MODEL=bge-m3
LLM_MODEL=qwen3
```

### Ollama Configuration

Nếu bạn chạy Ollama trên host machine (không trong Docker), sử dụng:
- `OLLAMA_URL=http://host.docker.internal:11434` (Windows/Mac)
- `OLLAMA_URL=http://172.17.0.1:11434` (Linux)

Nếu muốn chạy Ollama trong Docker, uncomment phần `ollama` service trong `docker-compose.yml` và đổi:
- `OLLAMA_URL=http://ollama:11434`

## 📡 API Endpoints

Sau khi container chạy, các API endpoints có sẵn tại:

### Health Check
```bash
GET http://localhost:5000/health
GET http://localhost:5000/api/health
```

### RAG Endpoints
```bash
# Chat
POST http://localhost:5000/api/chat
POST http://localhost:5000/api/rag/chat

# Search
POST http://localhost:5000/api/search
POST http://localhost:5000/api/rag/search
```

### Recommendation Endpoints
```bash
# Recommend by query
POST http://localhost:5000/api/recommend/query
POST http://localhost:5000/api/hotels/search

# Semantic search
POST http://localhost:5000/api/hotels/semantic-search

# Similar hotels
GET http://localhost:5000/api/recommend/similar/<item_id>
GET http://localhost:5000/api/hotels/<item_id>/similar

# Popular hotels
GET http://localhost:5000/api/recommend/popular
GET http://localhost:5000/api/hotels/popular

# Hybrid recommendation
POST http://localhost:5000/api/recommend/hybrid
```

## 🗄️ Database Setup

### 1. MySQL Database

Database sẽ tự động được import từ `myhotel.sql` khi container MySQL khởi động lần đầu.

### 2. Qdrant Collections

Collections sẽ tự động được tạo khi API service khởi động (nhưng **KHÔNG tự động index data**).

#### Cách 1: Index với Hybrid Search (Khuyến nghị)

Index data với cả dense và sparse vectors cho hybrid search:

```bash
# Windows
docker-index-hybrid.bat

# Linux/Mac
chmod +x docker-index-hybrid.sh
./docker-index-hybrid.sh

# Hoặc chạy trực tiếp trong container
docker-compose exec unified_api python index_with_hybrid.py
```

**Lưu ý**: Index với hybrid search sẽ tạo cả semantic (dense) và keyword (sparse) vectors, mất khoảng 5-10 phút tùy số lượng data.

#### Cách 2: Index cơ bản (Dense only)

Index chỉ với dense vectors (nhanh hơn nhưng không có keyword search):

```bash
# Chạy trực tiếp trong container
docker-compose exec unified_api python setup_collections.py
```

#### Cách 3: Tự động index khi container khởi động

Thêm vào `docker-compose.yml` trong phần `environment` của `unified_api`:

```yaml
- AUTO_INDEX_DATA=true
```

Sau đó rebuild và restart:

```bash
docker-compose up -d --build unified_api
```

**Lưu ý**: Auto-index có thể mất nhiều thời gian và tốn tài nguyên. Nên chạy thủ công lần đầu, sau đó chỉ index khi cần.

## 🔍 Troubleshooting

### 1. Container không start

```bash
# Kiểm tra logs
docker-compose logs unified_api

# Kiểm tra health
docker-compose ps
```

### 2. API không kết nối được Qdrant

```bash
# Kiểm tra Qdrant đã chạy chưa
docker-compose ps qdrant

# Test connection
curl http://localhost:6333/health
```

### 3. API không kết nối được MySQL

```bash
# Kiểm tra MySQL đã chạy chưa
docker-compose ps mysql

# Test connection từ container
docker-compose exec unified_api python -c "import pymysql; pymysql.connect(host='mysql', port=3306, user='root', password='root')"
```

### 4. Ollama connection issues

Nếu dùng Ollama trên host:
- Windows/Mac: Đảm bảo `host.docker.internal` hoạt động
- Linux: Có thể cần dùng IP của host hoặc `172.17.0.1`

### 5. Rebuild container sau khi thay đổi code

```bash
# Rebuild và restart
docker-compose up -d --build unified_api
```

## 📦 Volumes

Các volumes được tạo:

- `qdrant_storage`: Dữ liệu Qdrant
- `redis_data`: Dữ liệu Redis cache
- `mysql_data`: Dữ liệu MySQL
- `embedding_cache`: Cache embeddings của API service

## 🧹 Cleanup

```bash
# Dừng và xóa containers
docker-compose down

# Xóa containers, networks và volumes
docker-compose down -v

# Xóa images
docker-compose down --rmi all
```

## 📝 Notes

- API service sẽ tự động tạo collections trong Qdrant khi khởi động
- Để index dữ liệu vào Qdrant, cần chạy các scripts riêng (xem README.md)
- Embedding cache được lưu trong volume để tăng tốc độ
- Logs được mount vào `./logs` directory

