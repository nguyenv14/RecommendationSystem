# Hotel Recommendation API Service

Flask API service cho hệ thống semantic hotel recommendation sử dụng BGE-M3 + Ollama + Qdrant.

## 🚀 Khởi động

### 1. Chạy với Docker

```bash
# Start all services
docker-compose up -d

# Check logs
docker logs hotel_recommendation_api
```

### 2. Chạy standalone (local)

```bash
# Install dependencies
pip install -r requirements_api.txt

# Start service
python api_service.py
```

Service sẽ chạy tại: `http://localhost:5000`

## 📋 API Endpoints

### 1. Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "message": "Semantic Recommendation Service is running"
}
```

---

### 2. Process New Hotel

Thêm một hotel mới và tạo embeddings.

```bash
POST /api/hotels/process
Content-Type: application/json

{
  "hotel_id": 123,
  "hotel_name": "Luxury Beach Hotel",
  "hotel_desc": "A beautiful 5-star hotel near the beach",
  "hotel_placedetails": "Nha Trang, Vietnam",
  "hotel_tag_keyword": "beach, luxury, resort",
  "hotel_rank": 5,
  "hotel_price_average": 5000000
}
```

**Response:**
```json
{
  "success": true,
  "message": "Hotel 123 processed successfully",
  "hotel_id": 123
}
```

---

### 3. Process Multiple Hotels (Batch)

Thêm nhiều hotels cùng lúc.

```bash
POST /api/hotels/batch
Content-Type: application/json

{
  "hotels": [
    {
      "hotel_id": 101,
      "hotel_name": "Hotel 1",
      "hotel_desc": "Description 1",
      ...
    },
    {
      "hotel_id": 102,
      "hotel_name": "Hotel 2",
      "hotel_desc": "Description 2",
      ...
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Processed 2 hotels",
  "count": 2
}
```

---

### 4. Get Similar Hotels

Lấy danh sách hotels tương tự cho một hotel_id.

```bash
GET /api/hotels/123/similar?top_k=10
```

**Response:**
```json
{
  "success": true,
  "hotel_id": 123,
  "recommendations": [
    {
      "hotel_id": 456,
      "hotel_name": "Similar Hotel",
      "similarity_score": 0.8523,
      "cosine_similarity": 0.8523,
      "cosine_distance": 0.1477,
      "hotel_rank": 5,
      "hotel_price_average": 4500000
    },
    ...
  ],
  "count": 10
}
```

---

### 5. Search Hotels by Query

Tìm hotels bằng câu query tự nhiên.

```bash
POST /api/hotels/search
Content-Type: application/json

{
  "query": "Khách sạn gần biển Nha Trang",
  "top_k": 5
}
```

**Response:**
```json
{
  "success": true,
  "query": "Khách sạn gần biển Nha Trang",
  "results": [
    {
      "hotel_id": 789,
      "hotel_name": "Beach Resort",
      "similarity_score": 0.9234,
      "hotel_rank": 5,
      "hotel_price_average": 3800000
    },
    ...
  ],
  "count": 5
}
```

---

### 6. Reload Database

Load lại toàn bộ hotels từ CSV file.

```bash
POST /api/hotels/reload
Content-Type: application/json

{
  "csv_path": "datasets_extracted/tbl_hotel.csv",
  "recreate_collection": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reloaded 22 hotels from datasets_extracted/tbl_hotel.csv",
  "count": 22,
  "recreated": true
}
```

---

### 7. Calculate Distances

Tính toán khoảng cách cosine giữa tất cả hotels.

```bash
POST /api/hotels/calculate-distances
Content-Type: application/json

{
  "top_n": 10
}
```

**Response:**
```json
{
  "success": true,
  "message": "Calculated distances for 110 hotel pairs",
  "output_file": "hotel_distances.csv",
  "count": 110
}
```

---

### 8. Get Collection Info

Xem thông tin collection hiện tại.

```bash
GET /api/hotels/info
```

**Response:**
```json
{
  "success": true,
  "collection_name": "hotel_recommendations",
  "points_count": 22,
  "vectors_count": 1024
}
```

## 🔧 Configuration

Môi trường biến (Environment Variables):

```bash
OLLAMA_URL=http://localhost:11434  # Ollama API URL
QDRANT_URL=http://localhost:6333    # Qdrant URL
API_HOST=0.0.0.0                     # API host
API_PORT=5000                         # API port
```

## 📝 Usage Examples

### Example 1: Add new hotel

```bash
curl -X POST http://localhost:5000/api/hotels/process \
  -H "Content-Type: application/json" \
  -d '{
    "hotel_id": 999,
    "hotel_name": "New Luxury Hotel",
    "hotel_desc": "Beautiful hotel description",
    "hotel_placedetails": "District 1, Ho Chi Minh City",
    "hotel_tag_keyword": "luxury, downtown",
    "hotel_rank": 5,
    "hotel_price_average": 5000000
  }'
```

### Example 2: Get similar hotels

```bash
curl http://localhost:5000/api/hotels/2/similar?top_k=5
```

### Example 3: Search by query

```bash
curl -X POST http://localhost:5000/api/hotels/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Khách sạn sang trọng ở trung tâm",
    "top_k": 10
  }'
```

### Example 4: Reload database

```bash
curl -X POST http://localhost:5000/api/hotels/reload \
  -H "Content-Type: application/json" \
  -d '{
    "csv_path": "datasets_extracted/tbl_hotel.csv",
    "recreate_collection": true
  }'
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Flask API     │ (Port 5000)
│   api_service.py│
└────────┬────────┘
         │
         ├─────────> Ollama + BGE-M3 (Port 11434)
         │           - Generate embeddings
         │           
         └─────────> Qdrant (Port 6333)
                     - Store vectors
                     - Search similar
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker logs -f hotel_recommendation_api

# Stop services
docker-compose down

# Rebuild API
docker-compose build api
docker-compose up -d api
```

## ⚡ Performance

- **Process 1 hotel**: ~5 seconds
- **Batch 10 hotels**: ~30 seconds
- **Get similar**: ~0.1 seconds
- **Search**: ~0.2 seconds
- **Reload**: Depends on data size

## 🔍 Testing

```bash
# Health check
curl http://localhost:5000/health

# Test with provided test hotel
curl -X POST http://localhost:5000/api/hotels/process \
  -H "Content-Type: application/json" \
  -d @test_hotel.json
```

## 📊 Monitoring

- Logs: `docker logs hotel_recommendation_api`
- Health: `curl http://localhost:5000/health`
- Collection info: `curl http://localhost:5000/api/hotels/info`

