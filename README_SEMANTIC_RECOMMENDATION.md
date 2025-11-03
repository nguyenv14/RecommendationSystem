# Hệ thống Khuyến nghị Khách sạn dựa trên Semantic Search

## Tổng quan

Hệ thống này sử dụng **Embedding Models** và **Vector Database (Qdrant)** để tạo hệ thống khuyến nghị khách sạn thông minh dựa trên mô tả và đặc điểm của khách sạn.

## Kiến trúc

```
Hotel Data (CSV) 
    ↓
Preprocessing & Chunking
    ↓
Embedding Model (Sentence Transformer)
    ↓
Vector Database (Qdrant with HNSW Index)
    ↓
Similarity Search (Cosine Distance)
    ↓
Recommendations
```

## Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements_semantic.txt
```

### 2. Cài đặt Qdrant Server (Docker)

```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Hoặc sử dụng Qdrant Cloud (không cần cài đặt local).

### 3. Cấu hình GPU (Tùy chọn)

Nếu có GPU NVIDIA:
```bash
# Kiểm tra GPU
nvidia-smi

# Cài đặt CUDA
# Xem hướng dẫn tại: https://pytorch.org/get-started/locally/
```

## Sử dụng

### Chạy hệ thống

```bash
python semantic_recommendation_system.py
```

Script sẽ:
1. Load dữ liệu khách sạn từ `datasets_extracted/tbl_hotel.csv`
2. Tạo embeddings cho mỗi khách sạn
3. Lưu trữ vào Qdrant với HNSW indexing
4. Thực hiện tìm kiếm tương tự và hiển thị kết quả

### Sử dụng trong Code

```python
from semantic_recommendation_system import SemanticRecommendationSystem

# Initialize system
system = SemanticRecommendationSystem(
    model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
    device='cuda'  # or 'cpu'
)

# Load hotels
hotels_df = pd.read_csv('datasets_extracted/tbl_hotel.csv')

# Index hotels
system.index_hotels(hotels_df)

# Tìm kiếm tương tự
query = "Khách sạn gần biển, 5 sao, có spa"
results = system.search_similar_hotels(query, top_k=10)

# Khuyến nghị cho một khách sạn
recommendations = system.recommend_for_hotel(hotel_id=2, top_k=5)
```

## Tính năng

### 1. Preprocessing & Chunking
- Tự động phân đoạn mô tả dài thành các chunk nhỏ hơn
- Xử lý tiếng Việt và tiếng Anh
- Kết hợp nhiều trường dữ liệu: tên, mô tả, địa chỉ, từ khóa

### 2. Embedding Model
- Model: `paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions)
- Hỗ trợ tiếng Việt
- Batch processing để tăng tốc độ
- Auto-detect GPU/CPU

### 3. Vector Database (Qdrant)
- HNSW indexing cho tìm kiếm nhanh
- Cosine distance cho đo độ tương đồng
- Metadata filtering (rank, price, etc.)
- Scale horizontally

### 4. Similarity Search
- Cosine distance cho semantic similarity
- Top-K results với scoring
- Deduplication (một khách sạn chỉ xuất hiện một lần)

## Models khuyến nghị

### High Performance (GPU required)
- `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (768d)
- `intfloat/multilingual-e5-large` (1024d)

### Balanced (CPU-friendly)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384d) ⭐ Recommended
- `sentence-transformers/distiluse-base-multilingual-cased-v2` (512d)

### Lightweight (Mobile)
- `sentence-transformers/all-MiniLM-L6-v2` (384d)

## Advanced Usage

### Custom chunking
```python
chunks = system.preprocess_description(
    description, 
    chunk_size=256  # Smaller chunks
)
```

### Batch processing
```python
embeddings = system.create_embeddings(
    texts, 
    batch_size=64  # Increase for faster processing
)
```

### Custom Qdrant configuration
```python
system = SemanticRecommendationSystem(
    model_name='your-model',
    qdrant_url='http://your-qdrant-server:6333'
)

system.create_qdrant_collection(
    vector_size=512  # Match your model dimension
)
```

## Performance

### Benchmark (RTX 3080)
- Indexing 22 hotels: ~2 seconds
- Search query: ~10ms
- Model: paraphrase-multilingual-MiniLM-L12-v2
- Batch size: 32

### Optimization Tips
1. Sử dụng GPU cho model inference
2. Tăng batch_size cho large datasets
3. Sử dụng HNSW với M=32, ef_construct=200
4. Enable quantization cho production

## Troubleshooting

### Không kết nối được Qdrant
```bash
# Check Qdrant is running
curl http://localhost:6333/health

# Restart Qdrant
docker restart qdrant_container
```

### Out of Memory
- Giảm batch_size
- Sử dụng model nhẹ hơn
- Enable gradient checkpointing

### Slow indexing
- Sử dụng GPU
- Tăng batch_size
- Sử dụng multiprocessing

## API Integration Example

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
system = SemanticRecommendationSystem()

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    hotel_id = data['hotel_id']
    top_k = data.get('top_k', 10)
    
    results = system.recommend_for_hotel(hotel_id, top_k)
    return jsonify(results)

if __name__ == '__main__':
    app.run()
```

## License

MIT

## Credits

- Sentence Transformers: https://www.sbert.net/
- Qdrant: https://qdrant.tech/
- Hugging Face: https://huggingface.co/

