# Hướng dẫn sử dụng BGE-M3 cho Semantic Recommendation System

## Tổng quan

Hệ thống đã được chuyển đổi để sử dụng **BGE-M3** (BAAI General Embedding) - một model embedding hiện đại với các đặc điểm:

- **Multi-lingual**: Hỗ trợ 100+ ngôn ngữ
- **High quality**: Đạt top performance trên các benchmark embedding
- **Long context**: Hỗ trợ context dài
- **1024 dimensions**: Embedding dimension cao hơn (vs 384 của MiniLM)

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements_semantic.txt
```

### 2. Khởi động Qdrant

```bash
# Windows
start_qdrant.bat

# Hoặc sử dụng docker-compose
docker-compose up -d
```

## Sử dụng

### Chạy hệ thống

```bash
python semantic_recommendation_system.py
```

## Thay đổi so với phiên bản cũ

### 1. Model
- **Cũ**: `paraphrase-multilingual-MiniLM-L12-v2` (384 dims)
- **Mới**: `BAAI/bge-m3` (1024 dims)

### 2. Vector size
- **Cũ**: 384 dimensions
- **Mới**: 1024 dimensions

### 3. Batch size
- **Cũ**: 32
- **Mới**: 16 (do model lớn hơn)

### 4. Normalization
- Thêm `normalize_embeddings=True` để cải thiện cosine similarity

## Tùy chỉnh

### Chọn device

```python
# CPU
system = SemanticRecommendationSystem(device='cpu')

# GPU
system = SemanticRecommendationSystem(device='cuda')
```

### Chọn model khác

```python
system = SemanticRecommendationSystem(model_name='BAAI/bge-large-en-v1.5')
```

## Kết quả

Sau khi chạy, bạn sẽ có:
- File `hotel_distances.csv`: Ma trận khoảng cách giữa tất cả hotels
- Mỗi hotel có vector 1024 chiều trong Qdrant
- Recommendations với cosine similarity chính xác hơn

## Lợi ích của BGE-M3

1. **Chất lượng tốt hơn**: Embeddings chính xác hơn
2. **Đa ngôn ngữ tốt hơn**: Xử lý tiếng Việt tốt hơn
3. **Longer context**: Có thể xử lý mô tả dài hơn
4. **Mature model**: Model được train tốt hơn

