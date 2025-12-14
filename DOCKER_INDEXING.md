# Hướng dẫn Index Data trong Docker

## 🐳 Index trong Docker Container

Khi chạy hệ thống trong Docker, bạn cần index data từ bên trong container.

## 🚀 Quick Start

### Option 1: Index với Hybrid Search (Khuyến nghị)

Index với cả dense (semantic) và sparse (keyword) vectors:

```bash
# Windows
docker-index-hybrid.bat

# Linux/Mac
chmod +x docker-index-hybrid.sh
./docker-index-hybrid.sh
```

Hoặc chạy trực tiếp:

```bash
docker-compose exec unified_api python index_with_hybrid.py
```

### Option 2: Index cơ bản (Dense only)

Chỉ index với dense vectors (nhanh hơn):

```bash
docker-compose exec unified_api python setup_collections.py
```

## 📋 Yêu cầu

Trước khi index, đảm bảo:

1. ✅ **Container đang chạy**:
   ```bash
   docker-compose ps
   ```

2. ✅ **Qdrant đã sẵn sàng**:
   ```bash
   curl http://localhost:6333/health
   ```

3. ✅ **Ollama đang chạy** (nếu dùng external Ollama):
   ```bash
   curl http://localhost:11434/api/tags
   ```

4. ✅ **MySQL có dữ liệu**:
   ```bash
   docker-compose exec mysql mysql -uroot -proot -e "USE myhotel; SELECT COUNT(*) FROM tbl_hotel WHERE hotel_status = 1;"
   ```

## 🔧 Chi tiết

### 1. Vào container

```bash
# Vào bash trong container
docker-compose exec unified_api bash

# Bây giờ bạn đang ở trong container
# Có thể chạy các lệnh Python
python index_with_hybrid.py
```

### 2. Chạy script index

```bash
# Hybrid search indexing
docker-compose exec unified_api python index_with_hybrid.py

# Hoặc basic indexing
docker-compose exec unified_api python setup_collections.py
```

### 3. Xem logs

```bash
# Xem logs real-time
docker-compose logs -f unified_api

# Xem logs của indexing
docker-compose exec unified_api python index_with_hybrid.py 2>&1 | tee indexing.log
```

## 📊 Kiểm tra kết quả

### Kiểm tra collections

```bash
# Vào container
docker-compose exec unified_api python -c "
from src.core import VectorStoreService
from src.config import get_settings

vs = VectorStoreService(url=get_settings().QDRANT_URL)
for col in vs.client.get_collections().collections:
    info = vs.client.get_collection(col.name)
    print(f'{col.name}: {info.points_count} points')
"
```

### Kiểm tra qua API

```bash
# Health check
curl http://localhost:5000/health

# Status
curl http://localhost:5000/api/status
```

## ⚠️ Lưu ý

### 1. Environment Variables

Scripts trong container sử dụng environment variables từ `docker-compose.yml`:
- `QDRANT_URL=http://qdrant:6333` (dùng service name, không phải localhost)
- `OLLAMA_URL=http://host.docker.internal:11434` (external Ollama)
- `MYSQL_HOST=mysql` (dùng service name)

### 2. Ollama Connection

Nếu Ollama chạy trên host (không trong Docker):
- Windows/Mac: `host.docker.internal:11434` ✅
- Linux: Có thể cần `172.17.0.1:11434` hoặc thêm `extra_hosts`

### 3. FastEmbed Model Download

Lần đầu chạy, fastembed sẽ download model BM25 (~50MB):
- Cần internet connection
- Model được cache trong container volume
- Nếu không có internet, script sẽ fallback về dense-only

### 4. Performance

- **Dense embeddings**: ~1-2s per batch (10 items) với Ollama
- **Sparse embeddings**: ~0.1s per batch (32 items) với fastembed
- **Total time**: ~5-10 phút cho 1000 hotels

## 🐛 Troubleshooting

### 1. Container không chạy

```bash
# Kiểm tra status
docker-compose ps

# Start containers
docker-compose up -d

# Xem logs
docker-compose logs unified_api
```

### 2. Không kết nối được Qdrant

```bash
# Kiểm tra Qdrant container
docker-compose ps qdrant

# Test connection từ container
docker-compose exec unified_api python -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='http://qdrant:6333')
print(client.get_collections())
"
```

### 3. Không kết nối được Ollama

```bash
# Kiểm tra Ollama trên host
curl http://localhost:11434/api/tags

# Test từ container
docker-compose exec unified_api python -c "
import requests
r = requests.get('http://host.docker.internal:11434/api/tags')
print(r.status_code)
"
```

### 4. Không kết nối được MySQL

```bash
# Kiểm tra MySQL container
docker-compose ps mysql

# Test connection
docker-compose exec unified_api python -c "
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root:root@mysql:3306/myhotel')
print(engine.connect())
"
```

### 5. FastEmbed download fail

Nếu không có internet hoặc download fail:
- Script sẽ fallback về dense-only
- Hybrid search sẽ không hoạt động
- Có thể chạy lại sau khi có internet

### 6. Index chậm

**Giải pháp**:
- Kiểm tra Ollama performance
- Giảm batch_size trong script
- Sử dụng GPU cho Ollama (nếu có)

## 🔄 Re-index

Để re-index sau khi có data mới:

```bash
# Chạy lại script (sẽ upsert, không duplicate)
docker-compose exec unified_api python index_with_hybrid.py
```

## 📝 Scripts có sẵn

- `docker-index-hybrid.sh` / `.bat`: Index với hybrid search
- `index_with_hybrid.py`: Script Python chính
- `setup_collections.py`: Index cơ bản (dense only)

## 💡 Tips

1. **Lần đầu**: Chạy hybrid indexing để có đầy đủ tính năng
2. **Development**: Có thể dùng dense-only cho nhanh
3. **Production**: Nên dùng hybrid search cho độ chính xác cao
4. **Monitoring**: Xem logs để theo dõi tiến trình


