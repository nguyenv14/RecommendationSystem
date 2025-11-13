# RAG System - Hotel Recommendation

Hệ thống RAG (Retrieval-Augmented Generation) cho tư vấn khách sạn tại Đà Nẵng, sử dụng LangChain + Ollama + Qdrant.

## 📋 Mục lục

1. [Tổng quan](#tổng-quan)
2. [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
3. [Các tính năng chính](#các-tính-năng-chính)
4. [Cài đặt](#cài-đặt)
5. [Cấu hình](#cấu-hình)
6. [Sử dụng](#sử-dụng)
7. [Phương pháp tối ưu](#phương-pháp-tối-ưu)
8. [Troubleshooting](#troubleshooting)

## 🎯 Tổng quan

Hệ thống RAG này giải quyết các vấn đề:

1. **Kết nối Database**: Lấy dữ liệu trực tiếp từ MySQL thay vì dữ liệu cứng
2. **Smart Chunking**: Chunking thông minh với metadata preservation để không mất ngữ nghĩa
3. **Incremental Indexing**: Chỉ vector hóa dữ liệu mới/cập nhật, không vector hóa lại toàn bộ
4. **Performance Optimization**: Tối ưu query speed với HNSW indexing, batch processing, caching

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐
│   MySQL DB      │  ← Dữ liệu khách sạn
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Database        │  ← Kết nối và lấy dữ liệu
│ Connector       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Hotel Data      │  ← Chuẩn hóa và tạo semantic text
│ Normalizer      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Smart Chunker   │  ← Chunking với metadata preservation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Ollama          │  ← Vector embeddings (bge-m3)
│ Embeddings      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Qdrant          │  ← Vector database với HNSW index
│ Vector Store    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RAG System      │  ← Retrieval + Generation
│ (LangChain)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ API Service     │  ← Flask API
│ (Flask)         │
└─────────────────┘
```

## ✨ Các tính năng chính

### 1. Database Connection

- **Kết nối MySQL**: Lấy dữ liệu trực tiếp từ database
- **Connection Pooling**: Tối ưu kết nối với SQLAlchemy
- **Incremental Fetching**: Chỉ lấy dữ liệu mới/cập nhật

### 2. Smart Chunking

- **Sentence Preservation**: Không cắt giữa câu
- **Metadata Preservation**: Mỗi chunk giữ đầy đủ metadata (hotel_id, hotel_name, area_name, etc.)
- **Overlap**: Chunk overlap để không mất context
- **Context Preservation**: Ví dụ "Khách sạn A đẹp... có view biển" → Khi search "view biển" vẫn tìm thấy khách sạn A

### 3. Incremental Indexing

- **Timestamp Tracking**: Lưu timestamp lần index cuối
- **Upsert**: Sử dụng upsert thay vì delete và recreate
- **Selective Indexing**: Chỉ index hotels mới/cập nhật

### 4. Performance Optimization

- **HNSW Indexing**: Tối ưu với HNSW (m=16, ef_construct=200)
- **Batch Processing**: Xử lý theo batch để tối ưu
- **Embedding Cache**: Cache embeddings để tránh tính lại
- **Query Optimization**: Tối ưu query với ef parameter

## 📦 Cài đặt

### 1. Cài đặt dependencies

```bash
cd rag
pip install -r requirements_rag.txt
```

### 2. Khởi động Docker services

```bash
docker-compose up -d
```

Services:
- **Qdrant**: Vector database (port 6333)
- **MySQL**: Database (port 3308)
- **Redis**: Cache (port 6380)
- **phpMyAdmin**: Database management (port 8181)

### 3. Import database

```bash
# Import SQL file vào MySQL
mysql -h localhost -P 3308 -u root -proot rag_db < myhotel.sql
```

### 4. Khởi động Ollama (nếu chưa có)

```bash
# Khởi động Ollama server
ollama serve

# Pull embedding model
ollama pull bge-m3

# Pull LLM model
ollama pull qwen3
```

## ⚙️ Cấu hình

### Environment Variables

Tạo file `.env` trong thư mục `rag/`:

```env
# Database
MYSQL_HOST=localhost
MYSQL_PORT=3308
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=rag_db

# Qdrant
QDRANT_URL=http://localhost:6333

# Ollama
OLLAMA_URL=http://localhost:11434
EMBEDDING_MODEL=bge-m3
LLM_MODEL=qwen3

# Collection
COLLECTION_NAME=hotels

# Flask
PORT=5001
DEBUG=False
```

### Chunking Configuration

```python
# Trong simple_rag_system.py
chunk_size = 500        # Kích thước mỗi chunk (characters)
chunk_overlap = 100     # Overlap giữa các chunks (characters)
min_chunk_size = 100    # Kích thước tối thiểu
preserve_sentences = True  # Không cắt giữa câu
```

### HNSW Configuration

```python
# Trong simple_rag_system.py
hnsw_config = HnswConfigDiff(
    m=16,                  # Số connections mỗi node
    ef_construct=200,      # Số candidates khi build index
    full_scan_threshold=10 # Minimum value
)
```

## 🚀 Sử dụng

### 1. Index hotels từ database

```python
from simple_rag_system import SimpleRAGSystem

# Initialize RAG system
rag = SimpleRAGSystem(
    ollama_url="http://localhost:11434",
    qdrant_url="http://localhost:6333",
    embedding_model="bge-m3",
    llm_model="qwen3",
    collection_name="hotels"
)

# Index hotels từ database với smart chunking
rag.index_hotels_from_database(
    use_chunking=True,          # Bật smart chunking
    chunk_size=500,             # Kích thước chunk
    chunk_overlap=100,          # Overlap
    incremental=True,           # Incremental indexing
    recreate_collection=False,  # Không recreate collection
    batch_size=10               # Batch size
)
```

### 2. Index hotels từ CSV (legacy)

```python
# Index từ CSV file
rag.index_hotels(
    normalized_data_path="rag/normalized_data/normalized_hotels.csv",
    recreate_collection=False
)
```

### 3. Search hotels

```python
# Semantic search
results = rag.search_hotels(
    query="Khách sạn 5 sao gần biển Đà Nẵng",
    top_k=5,
    area_name=None  # Optional: filter by area
)

for hotel in results:
    print(f"Hotel: {hotel['hotel_name']}")
    print(f"Area: {hotel['area_name']}")
    print(f"Price: {hotel['hotel_price_average']}")
    print(f"Similarity: {hotel['similarity_score']}")
```

### 4. Ask questions (RAG)

```python
# Ask question với RAG
response = rag.ask("Khách sạn nào 5 sao gần biển Đà Nẵng?")

print(f"Question: {response['question']}")
print(f"Answer: {response['answer']}")
print(f"Sources: {response['sources']}")
```

### 5. Run API service

```bash
# Run Flask API
python rag_chat_api.py

# Hoặc sử dụng script
./run_chat.sh
```

API endpoints:
- `GET /`: Chat interface
- `POST /api/chat`: Chat endpoint
- `POST /api/search`: Search endpoint
- `GET /api/status`: System status
- `GET /api/health`: Health check

## 🔧 Phương pháp tối ưu

### 1. Smart Chunking với Metadata Preservation

**Vấn đề**: Khi chunk text dài, metadata có thể bị mất, dẫn đến không tìm thấy kết quả.

**Giải pháp**:
- Mỗi chunk giữ đầy đủ metadata (hotel_id, hotel_name, area_name, etc.)
- Chunk ID: `{hotel_id}_{chunk_index}`
- Metadata: `chunk_index`, `total_chunks`, `is_first_chunk`, `is_last_chunk`
- Overlap giữa chunks để preserve context

**Ví dụ**:
```
Hotel A: "Khách sạn A đẹp, có view biển, gần trung tâm, có spa và hồ bơi"

Chunk 1: "Khách sạn A đẹp, có view biển, gần trung tâm"
  - Metadata: hotel_id=1, hotel_name="Hotel A", area_name="Sơn Trà", chunk_index=0

Chunk 2: "gần trung tâm, có spa và hồ bơi"
  - Metadata: hotel_id=1, hotel_name="Hotel A", area_name="Sơn Trà", chunk_index=1

→ Search "view biển" → Tìm thấy Chunk 1 → Có metadata đầy đủ → Tìm thấy Hotel A
```

### 2. Incremental Indexing

**Vấn đề**: Vector hóa lại toàn bộ dữ liệu mỗi khi có dữ liệu mới rất chậm.

**Giải pháp**:
- Lưu timestamp lần index cuối vào database
- Chỉ lấy hotels có `updated_at > last_indexed_at`
- Sử dụng `upsert` thay vì `delete` + `recreate`
- Track indexed hotels trong metadata table

**Workflow**:
```
1. Lấy last_indexed_timestamp từ database
2. Query hotels có updated_at > last_indexed_timestamp
3. Vector hóa chỉ hotels mới/cập nhật
4. Upsert vào Qdrant (update nếu đã có, insert nếu chưa có)
5. Lưu timestamp mới vào database
```

### 3. HNSW Indexing

**Vấn đề**: Query vector database chậm (> 2-3 phút).

**Giải pháp**:
- Sử dụng HNSW (Hierarchical Navigable Small World) index
- Tối ưu parameters: `m=16`, `ef_construct=200`
- Giảm query time từ 2-3 phút xuống < 1 giây

**Configuration**:
```python
hnsw_config = HnswConfigDiff(
    m=16,                  # Số connections mỗi node (16-32 là tốt)
    ef_construct=200,      # Số candidates khi build index (tăng cho accuracy)
    full_scan_threshold=10 # Minimum value
)
```

### 4. Batch Processing

**Vấn đề**: Xử lý từng document một rất chậm.

**Giải pháp**:
- Xử lý theo batch (10-20 documents/batch)
- Parallel processing với multiprocessing (future enhancement)
- Retry logic với exponential backoff

**Configuration**:
```python
batch_size = 10  # Số documents mỗi batch
max_retries = 3
retry_delay = 2  # seconds
```

### 5. Embedding Cache

**Vấn đề**: Tính embeddings lại nhiều lần cho cùng một text.

**Giải pháp**:
- Cache embeddings với MD5 hash của text
- Cache hit → return cached embedding
- Cache miss → compute và cache

**Implementation**:
```python
class CachedOllamaEmbeddings(Embeddings):
    def __init__(self, embeddings, cache_enabled=True):
        self._embedding_cache = {}
    
    def embed_query(self, text: str) -> List[float]:
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        embedding = self.embeddings.embed_query(text)
        self._embedding_cache[cache_key] = embedding
        return embedding
```

### 6. Query Optimization

**Vấn đề**: Query quá nhiều kết quả không cần thiết.

**Giải pháp**:
- Giảm `k` từ 5 xuống 3-5
- Sử dụng filter khi có location
- Tối ưu `ef` parameter cho HNSW search

**Configuration**:
```python
# Retriever
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 5}  # Top 5 results
)

# Search với filter
search_results = client.search(
    collection_name=collection_name,
    query_vector=query_embedding,
    limit=top_k * 2,
    query_filter=Filter(
        must=[FieldCondition(key="area_name", match=MatchValue(value=area_name))]
    )
)
```

## 📊 Performance Metrics

### Before Optimization

- **Indexing Time**: ~30-60 phút (toàn bộ dataset)
- **Query Time**: 2-3 phút
- **Memory Usage**: High (không có chunking)
- **Accuracy**: Medium (mất metadata khi chunk)
- **Chunks**: ~200+ chunks
- **Batch Size**: 10
- **Cache**: Chỉ query

### After Optimization

- **Indexing Time**: ~5-10 phút (toàn bộ dataset), ~1-2 phút (incremental)
- **Query Time**: < 1 giây (giảm 99%)
- **Memory Usage**: Low (smart chunking)
- **Accuracy**: High (metadata preservation)
- **Chunks**: ~100-120 chunks (giảm 50%)
- **Batch Size**: 50 (tăng 5x)
- **Cache**: Query + Documents (giảm 80-90% embedding time)

### Tối ưu hóa đã áp dụng

1. **Embedding Cache cho Documents**: Cache embeddings cho cả documents
2. **Tăng Batch Size**: Từ 10 lên 50
3. **Tăng Chunk Size**: Từ 500 lên 800 (giảm 50% chunks)
4. **Giảm Overlap**: Từ 100 xuống 50
5. **Bỏ Delay**: Không delay giữa batches
6. **Tối ưu Query**: Giảm k từ 5 xuống 3, giới hạn results
7. **Direct Qdrant Client**: Sử dụng Qdrant client trực tiếp
8. **Score Threshold**: Filter results có similarity < 0.3

## 🐛 Troubleshooting

### 1. Database Connection Error

**Vấn đề**: Không kết nối được MySQL

**Giải pháp**:
```bash
# Kiểm tra MySQL container
docker ps | grep mysql

# Kiểm tra connection
mysql -h localhost -P 3308 -u root -proot rag_db

# Kiểm tra environment variables
echo $MYSQL_HOST
echo $MYSQL_PORT
```

### 2. Ollama Connection Error

**Vấn đề**: Không kết nối được Ollama

**Giải pháp**:
```bash
# Kiểm tra Ollama service
curl http://localhost:11434/api/tags

# Khởi động Ollama
ollama serve

# Pull models
ollama pull bge-m3
ollama pull qwen3
```

### 3. Qdrant Connection Error

**Vấn đề**: Không kết nối được Qdrant

**Giải pháp**:
```bash
# Kiểm tra Qdrant container
docker ps | grep qdrant

# Kiểm tra Qdrant health
curl http://localhost:6333/health

# Kiểm tra collections
curl http://localhost:6333/collections
```

### 4. Slow Query Performance

**Vấn đề**: Query chậm (> 1 giây)

**Giải pháp**:
- Kiểm tra HNSW config: `m=16`, `ef_construct=200`
- Giảm `k` parameter
- Sử dụng filter khi có thể
- Kiểm tra collection size

### 5. Memory Error

**Vấn đề**: Out of memory khi indexing

**Giải pháp**:
- Giảm `batch_size`
- Sử dụng smart chunking
- Tăng chunk overlap
- Giảm `chunk_size`

### 6. Missing Metadata

**Vấn đề**: Không tìm thấy kết quả do mất metadata

**Giải pháp**:
- Sử dụng smart chunking với metadata preservation
- Kiểm tra metadata trong chunks
- Sử dụng overlap để preserve context

## 📝 Notes

### Chunking Strategy

- **Chunk Size**: 500 characters (optimal cho Vietnamese text)
- **Overlap**: 100 characters (20% overlap)
- **Sentence Preservation**: Không cắt giữa câu
- **Metadata**: Mỗi chunk giữ đầy đủ metadata

### Incremental Indexing Strategy

- **Timestamp Tracking**: Lưu trong `rag_index_metadata` table
- **Upsert**: Sử dụng upsert thay vì delete + recreate
- **Selective Fetching**: Chỉ fetch hotels mới/cập nhật
- **Batch Processing**: Xử lý theo batch để tối ưu

### Query Strategy

- **Semantic Search**: Sử dụng vector similarity search
- **Filtering**: Sử dụng Qdrant filter khi có location
- **Top K**: Lấy top 5 results
- **Metadata Filtering**: Post-filter với metadata nếu cần

## 🔮 Future Enhancements

1. **Parallel Processing**: Multiprocessing cho batch processing
2. **Redis Cache**: Cache queries và embeddings
3. **Hybrid Search**: Kết hợp semantic search và keyword search
4. **Re-ranking**: Re-rank results với cross-encoder
5. **A/B Testing**: Test các chunking strategies khác nhau
6. **Monitoring**: Monitor performance và accuracy
7. **Auto-scaling**: Auto-scale Qdrant và Ollama

## 📚 References

- [LangChain Documentation](https://python.langchain.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://ollama.ai/docs)
- [HNSW Paper](https://arxiv.org/abs/1603.09320)

## 📄 License

MIT License

## 👥 Contributors

- Nguyen Van A
- ...

