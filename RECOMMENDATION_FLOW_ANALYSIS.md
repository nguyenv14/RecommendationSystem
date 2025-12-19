# Phân Tích Luồng Recommendation System

## ⚠️ QUAN TRỌNG: Recommendation vs RAG

**Recommendation System** và **RAG System** là 2 hệ thống KHÁC NHAU:

### **Recommendation System** (Tài liệu này)
- **Mục đích:** Tìm kiếm và trả về danh sách items (hotels) phù hợp
- **Flow:** Query → Embed → Search → **Return Results** (KHÔNG có generation)
- **Output:** List of hotels với scores
- **Dùng khi:** User muốn xem danh sách khách sạn phù hợp

### **RAG System** (Retrieval-Augmented Generation)
- **Mục đích:** Tìm kiếm + Tạo câu trả lời tự nhiên bằng LLM
- **Flow:** Query → Embed → Search → **Generate Answer** (CÓ generation)
- **Output:** Câu trả lời text được generate từ LLM
- **Dùng khi:** User muốn hỏi và nhận câu trả lời tự nhiên

### **Tại sao cả 2 đều dùng `retrieve()` và `search()`?**
- Cả 2 đều cần **semantic search** để tìm documents phù hợp
- Cả 2 đều dùng chung **RetrieverService** để tái sử dụng code
- **Khác biệt:** RAG có thêm bước **GeneratorService** để tạo câu trả lời

---

## Tổng Quan

Luồng recommendation trong hệ thống này đi từ **embedding** (chuyển text thành vector) đến **lấy kết quả** (danh sách khách sạn được recommend). Hệ thống sử dụng **hybrid search** (kết hợp semantic search + keyword search) để tìm kiếm chính xác hơn.

**Lưu ý:** Đây là **Recommendation System** - chỉ search và return results, KHÔNG có LLM generation như RAG.

---

## 📊 Sơ Đồ Luồng Tổng Quan

### **Recommendation Flow (KHÔNG có Generation)**

```
User Query (Text)
    ↓
[1] Embedding Service (embed_query)
    ├─→ Dense Vector (Semantic)
    └─→ Sparse Vector (BM25 - Keyword)
    ↓
[2] Retriever Service (retrieve)
    ├─→ Build Qdrant Filter
    └─→ VectorStore Service (search)
    ↓
[3] Qdrant Vector Database
    ├─→ Hybrid Search (Prefetch + Merge)
    └─→ Return Scored Points
    ↓
[4] Recommender Service (recommend_by_query)
    └─→ Format Results (List of hotels)
    ↓
[5] API Response (JSON) ← DỪNG Ở ĐÂY (KHÔNG có LLM generation)
```

### **So sánh với RAG Flow (CÓ Generation)**

```
User Query (Text)
    ↓
[1] Embedding Service (embed_query)  ← GIỐNG NHAU
    ↓
[2] Retriever Service (retrieve)     ← GIỐNG NHAU
    ↓
[3] Qdrant Vector Database           ← GIỐNG NHAU
    ↓
[4] Generator Service (generate)     ← KHÁC: RAG có bước này
    └─→ LLM tạo câu trả lời từ context
    ↓
[5] API Response (Text answer)       ← KHÁC: Trả về text, không phải list
```

**Điểm khác biệt chính:**
- ✅ **Recommendation:** Search → Return list (không generation)
- ✅ **RAG:** Search → Generate answer (có generation)

---

## 🔍 Chi Tiết Từng Bước

### **BƯỚC 1: API Endpoint Nhận Request**

**File:** `app.py` (dòng 403-425)

```python
@app.route('/api/recommend/query', methods=['POST'])
def recommend_by_query():
    data = request.json
    query = data.get('query', '').strip()
    
    recommendations = recommender_service.recommend_by_query(
        query=query,
        collection_name=settings.REC_COLLECTION_HOTELS,
        top_k=top_k,
        filters=filters
    )
```

**Input:** 
- `query`: Text query từ user (vd: "khách sạn 5 sao gần biển")
- `top_k`: Số lượng kết quả cần lấy
- `filters`: Optional filters (vd: `{"area_id": 7}`)

---

### **BƯỚC 2: RecommenderService.recommend_by_query()**

**File:** `src/core/recommender.py` (dòng 47-85)

```python
def recommend_by_query(self, query, collection_name, top_k=10, filters=None):
    # Gọi RetrieverService để tìm kiếm
    results = self.retriever.retrieve(
        query=query,
        collection_name=collection_name,
        top_k=top_k,
        filters=filters
    )
    
    # Format kết quả
    recommendations = []
    for result in results:
        rec = {
            "item_id": result.get("id"),
            "score": result.get("score"),
            **result.get("payload", {})
        }
        recommendations.append(rec)
    
    return recommendations  # ← DỪNG Ở ĐÂY, KHÔNG có generation
```

**Chức năng:**
- Gọi `RetrieverService.retrieve()` để tìm kiếm (giống RAG)
- Format kết quả từ Qdrant thành format recommendation
- **KHÔNG có bước generation** - chỉ return list of items

**So sánh với RAG:**
- **Recommendation:** `retrieve()` → Format → Return (dừng)
- **RAG:** `retrieve()` → `generator.generate_from_documents()` → Return answer

---

### **BƯỚC 3: RetrieverService.retrieve() - Tạo Embeddings**

**File:** `src/core/retriever.py` (dòng 59-159)

#### **❓ TẠI SAO CẦN EMBEDDING QUERY?**

**Câu hỏi:** Tại sao không search trực tiếp bằng text mà phải embedding query thành vector?

**Trả lời:**

1. **Hotels trong Qdrant đã được lưu dưới dạng VECTORS:**
   ```python
   # Khi indexing, hotels đã được embed:
   hotel_text = "Grand Tourane Hotel, khách sạn 5 sao gần biển..."
   hotel_vector = [0.123, 0.456, 0.789, ...]  # 1024 dimensions
   
   # Lưu vào Qdrant:
   PointStruct(
       id=123,
       vector=hotel_vector,  # ← Đã là vector rồi
       payload={...}
   )
   ```

2. **Qdrant chỉ có thể so sánh VECTOR với VECTOR:**
   - Qdrant tính **cosine similarity** giữa 2 vectors
   - Không thể so sánh text với vector
   - → Cần chuyển query text thành vector để so sánh

3. **Semantic Search (Tìm kiếm theo ý nghĩa):**
   - **Không phải keyword matching:** "khách sạn 5 sao" ≠ chỉ tìm text chứa "5 sao"
   - **Tìm theo ý nghĩa:** "khách sạn 5 sao" ≈ "resort cao cấp" ≈ "luxury hotel"
   - Vector embedding hiểu được ngữ nghĩa, không chỉ từ khóa

4. **Ví dụ cụ thể:**
   ```
   Query: "khách sạn gần biển"
   
   ❌ Keyword search: Chỉ tìm hotels có text chứa "gần biển"
      → Bỏ sót: "resort ven biển", "hotel beachfront", "khách sạn view biển"
   
   ✅ Semantic search (embedding):
      Query vector: [0.1, 0.2, 0.3, ...]
      Hotel vectors: 
        - "resort ven biển": [0.12, 0.21, 0.29, ...] → Similarity: 0.95
        - "hotel beachfront": [0.11, 0.19, 0.31, ...] → Similarity: 0.93
        - "khách sạn view biển": [0.13, 0.22, 0.28, ...] → Similarity: 0.94
      → Tìm được tất cả hotels liên quan đến biển, dù không có từ "gần biển"
   ```

5. **So sánh Vector Similarity:**
   ```python
   # Qdrant tính cosine similarity:
   similarity = cosine_similarity(query_vector, hotel_vector)
   # similarity ∈ [0, 1]
   # similarity càng cao → càng giống nhau về ý nghĩa
   ```

**Kết luận:** 
- ✅ Cần embedding query để chuyển text → vector
- ✅ Vector này được so sánh với vectors của hotels trong Qdrant
- ✅ Tìm được hotels tương tự về **ý nghĩa**, không chỉ **từ khóa**

---

#### **3.1. Embed Query Text → Dense Vector**

```python
# Dòng 96: Tạo dense embedding (semantic vector)
query_vector = self.embedding_service.embed_query(query)
```

**Luồng trong EmbeddingService:**

**File:** `src/core/embeddings.py` (dòng 123-157)

```python
def embed_query(self, text: str) -> List[float]:
    # 1. Check cache trước
    cached = self._check_cache(text)
    if cached is not None:
        return cached
    
    # 2. Gọi Ollama API để tạo embedding
    if self.provider == "ollama":
        embedding = self.model.embed_query(text)  # LangChain OllamaEmbeddings
    
    # 3. Lưu vào cache (memory + disk)
    self._store_cache(text, embedding)
    
    return embedding  # ← Vector 1024 dimensions
```

**Chi tiết:**
- **Model:** Sử dụng Ollama với model `bge-m3` (hoặc model được config)
- **API Call:** `POST http://localhost:11434/api/embeddings`
- **Input:** Text query (vd: "khách sạn 5 sao gần biển")
- **Output:** Dense vector (vd: 1024 dimensions) - biểu diễn semantic meaning
- **Cache:** Có cache để tránh gọi lại API cho cùng một text

**Ví dụ:**
```python
query = "khách sạn 5 sao gần biển"
query_vector = embed_query(query)
# → [0.123, 0.456, 0.789, ..., 0.234]  # 1024 số thực
# Vector này biểu diễn ý nghĩa của query
```

#### **3.2. Embed Query Text → Sparse Vector (BM25)**

```python
# Dòng 108: Tạo sparse embedding (keyword vector) nếu dùng hybrid search
if use_hybrid_search and self.sparse_embedding_service:
    sparse_dict = self.sparse_embedding_service.embed_query(query)
    query_sparse_vector = sparse_dict
```

**File:** `src/core/sparse_embeddings.py`

**Chức năng:**
- Tokenize query text
- Tính BM25 weights cho từng token
- Output: Dictionary `{token_index: weight}` (vd: `{"123": 2.5, "456": 1.8}`)
- Dùng cho keyword matching chính xác

**Ví dụ:**
- Query: "khách sạn 5 sao"
- Sparse vector: `{"khách": 1.2, "sạn": 1.2, "5": 0.8, "sao": 1.5}`

---

### **BƯỚC 4: VectorStoreService.search() - Query Qdrant**

**File:** `src/core/vectorstore.py` (dòng 169-258)

#### **4.1. Hybrid Search (Dense + Sparse)**

```python
if query_sparse_vector:
    # Hybrid search với prefetch
    prefetch = [
        Prefetch(
            query=query_vector,      # Dense vector
            using="dense",
            limit=prefetch_limit,    # Lấy nhiều hơn để merge
        ),
        Prefetch(
            query=sparse_vec,        # Sparse vector (BM25)
            using="sparse",
            limit=prefetch_limit,
        ),
    ]
    
    results = self.client.query_points(
        collection_name=collection_name,
        prefetch=prefetch,           # Qdrant sẽ merge 2 kết quả
        query_filter=filters,
        limit=limit,
        with_payload=True
    )
```

**Cơ chế Hybrid Search:**
1. **Prefetch Dense:** Tìm top-K vectors gần nhất với query vector (semantic similarity)
2. **Prefetch Sparse:** Tìm top-K vectors match keywords (BM25 scores)
3. **Merge:** Qdrant tự động merge 2 kết quả, ưu tiên items xuất hiện ở cả 2
4. **Final Results:** Top-K items sau khi merge

#### **4.2. Semantic Search Only (nếu không có sparse vector)**

```python
else:
    # Chỉ dùng dense vector search
    results = self.client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=limit,
        query_filter=filters,
        score_threshold=score_threshold
    )
```

**Cơ chế:**
- Cosine similarity giữa query vector và vectors trong collection
- Trả về top-K items có similarity score cao nhất

---

### **BƯỚC 5: Qdrant Database - Vector Search**

**Qdrant Operations:**

1. **Collection Structure:**
   ```python
   {
       "dense": VectorParams(size=1024, distance=Distance.COSINE),
       "sparse": SparseVectorParams()  # BM25
   }
   ```

2. **Point Structure:**
   ```python
   PointStruct(
       id=hotel_id,
       vector={
           "dense": [0.123, 0.456, ...],  # 1024 dimensions
           "sparse": SparseVector(indices=[123, 456], values=[2.5, 1.8])
       },
       payload={
           "hotel_id": 123,
           "hotel_name": "Grand Tourane Hotel",
           "hotel_rank": 4.5,
           "hotel_price_average": 1500000,
           ...
       }
   )
   ```

3. **Search Process:**
   - Qdrant tính similarity scores
   - Apply filters (nếu có)
   - Sort by score (descending)
   - Return top-K `ScoredPoint` objects

**Output từ Qdrant:**
```python
[
    ScoredPoint(
        id=123,
        score=0.89,  # Similarity score
        payload={"hotel_name": "...", "hotel_rank": 4.5, ...}
    ),
    ScoredPoint(id=456, score=0.85, payload={...}),
    ...
]
```

---

### **BƯỚC 6: Format Results → API Response**

**RetrieverService.retrieve()** (dòng 141-153):

```python
# Format results từ Qdrant
documents = []
for result in results:
    doc = {
        "id": result.id,
        "score": result.score,
        "payload": result.payload
    }
    documents.append(doc)

return documents
```

**RecommenderService.recommend_by_query()** (dòng 75-83):

```python
# Format cho recommendation
recommendations = []
for result in results:
    rec = {
        "item_id": result.get("id"),
        "score": result.get("score"),
        **result.get("payload", {})  # Flatten payload
    }
    recommendations.append(rec)

return recommendations
```

**Final API Response:**
```json
{
    "success": true,
    "code": 200,
    "message": "Recommendations generated successfully",
    "data": {
        "recommendations": [
            {
                "item_id": 123,
                "score": 0.89,
                "hotel_name": "Grand Tourane Hotel",
                "hotel_rank": 4.5,
                "hotel_price_average": 1500000,
                "area_id": 7
            },
            ...
        ],
        "count": 10
    }
}
```

---

## 🔄 Luồng Indexing (Chuẩn Bị Dữ Liệu)

### **Index Hotels với Hybrid Vectors**

**File:** `index_with_hybrid.py`

#### **Bước 1: Load Data từ Database**
```python
query = "SELECT * FROM tbl_hotel WHERE hotel_status = 1"
hotels_df = pd.read_sql(text(query), engine)
```

#### **Bước 2: Prepare Text cho Embedding**
```python
for hotel in hotels_df:
    description_parts = [
        f"Tên: {hotel['hotel_name']}",
        hotel['hotel_desc'][:500],
        f"Địa chỉ: {hotel['hotel_placedetails']}"
    ]
    full_description = ' '.join(description_parts)
    hotel_texts.append(full_description)
```

#### **Bước 3: Tạo Dense Embeddings**
```python
# Batch processing
for i in range(0, len(hotel_texts), batch_size):
    batch = hotel_texts[i:i + batch_size]
    batch_embeddings = embedding_service.embed_documents(batch)
    dense_embeddings.extend(batch_embeddings)
```

**Luồng trong EmbeddingService.embed_documents():**
- Gọi Ollama API cho từng batch
- Cache embeddings
- Return list of vectors

#### **Bước 4: Tạo Sparse Embeddings (BM25)**
```python
sparse_embeddings = sparse_service.embed_documents(
    hotel_texts, 
    batch_size=32
)
```

**Luồng trong SparseEmbeddingService:**
- Tokenize mỗi text
- Tính BM25 weights
- Return list of sparse vectors (dict format)

#### **Bước 5: Tạo Points và Upload lên Qdrant**
```python
for dense_emb, sparse_emb, metadata in zip(...):
    point = create_hybrid_point(
        point_id=metadata['hotel_id'],
        dense_vector=dense_list,
        sparse_vector=sparse_emb,
        payload=metadata
    )
    points.append(point)

vectorstore.upsert_points(
    collection_name=collection_name,
    points=points,
    batch_size=10
)
```

---

## 📈 Các Loại Recommendation

### **1. Recommend by Query (Semantic Search)**
- **Input:** Text query
- **Flow:** Query → Embed → Search → Results
- **Use case:** "khách sạn 5 sao gần biển"

### **2. Recommend Similar (Item-to-Item)**
- **Input:** Item ID
- **Flow:** Get item vector → Search similar → Results
- **Use case:** "Khách sạn tương tự khách sạn ID 123"

### **3. Recommend Popular (Popularity-based)**
- **Input:** Filters (optional)
- **Flow:** Filter items → Calculate popularity score → Sort → Top-K
- **Use case:** "Top 10 khách sạn phổ biến nhất"

### **4. Recommend Hybrid (Semantic + Popularity)**
- **Input:** Query + optional item_id
- **Flow:** 
  1. Get semantic recommendations
  2. Get popularity scores
  3. Combine scores: `hybrid_score = semantic * 0.7 + popularity * 0.3`
  4. Optional: Diversity re-ranking
- **Use case:** "Khách sạn vừa phù hợp vừa phổ biến"

---

## 🎯 Điểm Quan Trọng

### **1. Embedding Cache**
- **Memory cache:** Fast access cho cùng session
- **Persistent cache:** Disk-based, TTL 30 days
- **Lợi ích:** Giảm API calls, tăng tốc độ

### **2. Hybrid Search**
- **Dense (Semantic):** Hiểu ý nghĩa, tìm items tương tự về concept
- **Sparse (Keyword):** Match chính xác keywords
- **Kết hợp:** Vừa semantic vừa keyword matching → Kết quả tốt hơn

### **3. Filters**
- **Qdrant Filters:** Filter trước khi search (efficient)
- **Post-filtering:** Filter sau khi search (nếu cần logic phức tạp)

### **4. Batch Processing**
- **Indexing:** Process theo batch để tối ưu memory và API calls
- **Embedding:** Batch size 10-32 tùy model

---

## 🔧 Cấu Hình Quan Trọng

### **Embedding Model**
- **Provider:** Ollama
- **Model:** `bge-m3` (default) hoặc model khác
- **Vector Size:** 1024 dimensions (tùy model)

### **Qdrant Collection**
- **Distance Metric:** Cosine similarity
- **Vectors:** Dense (1024) + Sparse (BM25)

### **Search Parameters**
- **top_k:** Số lượng kết quả (default: 10)
- **prefetch_limit:** Số candidates cho hybrid search (default: top_k * 2)
- **score_threshold:** Minimum similarity score (optional)

---

## 📝 Tóm Tắt Luồng

### **Recommendation Flow (Tài liệu này)**

1. **User gửi query** → API endpoint (`/api/recommend/query`)
2. **Embedding Service** → Chuyển query thành dense vector (semantic) + sparse vector (keyword)
3. **Retriever Service** → Gọi VectorStore để search
4. **VectorStore Service** → Query Qdrant với hybrid search
5. **Qdrant** → Tìm top-K items, trả về ScoredPoints
6. **Recommender Service** → Format kết quả (List of hotels)
7. **API Response** → Trả về JSON cho user ← **DỪNG Ở ĐÂY**

**Tổng thời gian:** ~100-500ms (tùy cache, network, Qdrant performance)

### **RAG Flow (Để so sánh)**

1. **User gửi query** → API endpoint (`/api/rag/ask`)
2. **Embedding Service** → Chuyển query thành vector (giống recommendation)
3. **Retriever Service** → Gọi VectorStore để search (giống recommendation)
4. **VectorStore Service** → Query Qdrant (giống recommendation)
5. **Qdrant** → Tìm top-K documents (giống recommendation)
6. **Generator Service** → **LLM tạo câu trả lời từ context** ← **KHÁC**
7. **API Response** → Trả về text answer cho user

**Tổng thời gian:** ~2000-3000ms (bao gồm LLM generation)

**Điểm khác biệt:**
- ✅ Recommendation: Chỉ search, không generation → Nhanh hơn
- ✅ RAG: Search + Generation → Chậm hơn nhưng có câu trả lời tự nhiên

---

## 🚀 Tối Ưu Hóa

1. **Cache embeddings** → Giảm API calls
2. **Batch processing** → Tăng throughput
3. **Hybrid search** → Kết quả chính xác hơn
4. **Index optimization** → Qdrant HNSW index
5. **Connection pooling** → Tái sử dụng connections

---

## 🔄 Tại Sao Cả 2 Đều Dùng RetrieverService?

**Câu hỏi:** Nếu Recommendation không phải RAG, tại sao lại dùng `retrieve()` và `search()`?

**Trả lời:**

1. **Cả 2 đều cần Semantic Search:**
   - Recommendation: Tìm hotels phù hợp với query
   - RAG: Tìm documents phù hợp với question
   - → Cùng một công nghệ: Vector similarity search

2. **Code Reuse (Tái sử dụng code):**
   - `RetrieverService` là shared service cho cả 2
   - Tránh duplicate code
   - Dễ maintain và optimize

3. **Khác biệt ở bước cuối:**
   - **Recommendation:** `retrieve()` → Format → Return (dừng)
   - **RAG:** `retrieve()` → `generate()` → Return (có thêm generation)

4. **Ví dụ code:**

```python
# Recommendation (KHÔNG có generation)
def recommend_by_query(self, query):
    results = self.retriever.retrieve(query)  # ← Dùng RetrieverService
    return format_results(results)  # ← Dừng ở đây

# RAG (CÓ generation)
def ask(self, question):
    documents = self.retriever.retrieve(question)  # ← Dùng RetrieverService (giống)
    answer = self.generator.generate(documents)  # ← Thêm bước này
    return answer
```

**Kết luận:** 
- ✅ Cả 2 đều dùng `RetrieverService` vì đều cần semantic search
- ✅ Khác biệt: Recommendation không có generation, RAG có generation
- ✅ `retrieve()` và `search()` là operations chung, không phải đặc thù của RAG

---

*Tài liệu này mô tả chi tiết luồng **Recommendation System** (không có generation) từ embedding đến kết quả cuối cùng. Để xem RAG flow, tham khảo `rag/docs/RAG_FLOW_EXPLANATION.md`.*
