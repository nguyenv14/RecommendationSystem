# Hướng dẫn sử dụng BGE-M3 với Ollama

## Tổng quan

Hệ thống semantic recommendation đã được tích hợp với Ollama để sử dụng BGE-M3 embeddings. BGE-M3 là model embedding mạnh mẽ với:
- **1024 dimensions**: Vector embedding dài hơn (vs 384 của MiniLM)
- **Multi-lingual**: Hỗ trợ 100+ ngôn ngữ
- **Multi-functionality**: Có thể dùng cho nhiều tác vụ
- **GPU support**: Tự động sử dụng GPU nếu có

## Cài đặt

### 1. Khởi động services

```bash
# Khởi động Qdrant và Ollama
docker-compose up -d

# Hoặc chỉ khởi động Ollama
docker-compose up -d ollama
```

### 2. Pull BGE-M3 model

```bash
# Pull BGE-M3 vào Ollama
docker exec ollama ollama pull bge-m3
```

### 3. Kiểm tra model đã sẵn sàng

```bash
# Test BGE-M3 embeddings
python test_ollama_bge.py
```

## Sử dụng

### Chạy hệ thống với Ollama

```bash
python semantic_recommendation_system.py
```

Hệ thống sẽ:
1. Load hotel data
2. Sử dụng Ollama API để tạo embeddings từ BGE-M3
3. Index vào Qdrant với vectors 1024 chiều
4. Tính cosine distances giữa các hotels
5. Lưu kết quả vào `hotel_distances.csv`

### Programmatic usage

```python
from semantic_recommendation_system import SemanticRecommendationSystem

# Initialize với Ollama
system = SemanticRecommendationSystem(
    use_ollama=True,
    ollama_url='http://localhost:11434'
)

# Load data
import pandas as pd
hotels_df = pd.read_csv('datasets_extracted/tbl_hotel.csv')

# Index hotels
system.index_hotels(hotels_df)

# Tính distances
distances = system.calculate_hotel_distances(top_n=5)

# Recommend similar hotels
recommendations = system.recommend_for_hotel(hotel_id=2, top_k=5)
for rec in recommendations:
    print(f"Hotel: {rec['hotel_name']}, Similarity: {rec['cosine_similarity']:.4f}")
```

## So sánh

### Trước (MiniLM):
- Embeddings: 384 dimensions
- Model: paraphrase-multilingual-MiniLM-L12-v2
- Load trực tiếp trong Python
- Memory: Cần load toàn bộ model vào RAM

### Sau (BGE-M3 + Ollama):
- Embeddings: **1024 dimensions**
- Model: BAAI/bge-m3
- Chạy trên Ollama (GPU-supported)
- Memory: Model chạy trên Ollama container
- **GPU support**: Tự động sử dụng GPU nếu có
- **Better quality**: Embeddings chất lượng cao hơn

## Kiểm tra GPU

```bash
# Kiểm tra Ollama có dùng GPU không
docker exec ollama nvidia-smi
```

Nếu có GPU, Ollama sẽ tự động sử dụng GPU để tăng tốc embeddings.

## Troubleshooting

### Ollama không khởi động

```bash
# Kiểm tra container
docker ps | grep ollama

# Xem logs
docker logs ollama

# Restart
docker restart ollama
```

### Model chưa pull

```bash
# Pull model
docker exec ollama ollama pull bge-m3

# List models
docker exec ollama ollama list
```

### Port bị chiếm

```bash
# Stop container
docker stop ollama

# Remove container
docker rm ollama

# Khởi động lại
docker-compose up -d ollama
```

## References

- [Ollama Documentation](https://ollama.ai/docs)
- [BGE-M3 Model](https://huggingface.co/BAAI/bge-m3)
- [Ollama BGE-M3](https://ollama.ai/library/bge-m3)

## Output

Sau khi chạy, bạn sẽ có:
- `hotel_distances.csv`: Ma trận khoảng cách giữa các hotels
- Mỗi hotel có embedding 1024 chiều trong Qdrant
- Recommendations với similarity scores chính xác hơn

