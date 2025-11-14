# Giải thích RAG System và Query Flow

## 📋 Tổng quan RAG (Retrieval-Augmented Generation)

RAG = **Retrieval** (Tìm kiếm) + **Augmented** (Bổ sung) + **Generation** (Tạo câu trả lời)

RAG system này hoạt động theo 2 mode:
1. **Semantic Search** (`search_hotels()`) - Chỉ tìm kiếm, không dùng LLM
2. **RAG Query** (`ask()`) - Tìm kiếm + LLM generation để tạo câu trả lời

---

## 🔍 1. SEMANTIC SEARCH FLOW (`search_hotels()`)

### Flow diagram:
```
User Query
    ↓
[1] Extract location (optional)
    ↓
[2] Generate Query Embedding (Ollama bge-m3)
    ↓
[3] Vector Search in Qdrant
    ├─ With location filter (if provided)
    └─ Without filter (general search)
    ↓
[4] Similarity Scoring & Ranking
    ↓
[5] Format Results (hotel metadata)
    ↓
Return List[Dict] of hotels
```

### Code Flow:

#### Bước 1: Extract Location (Optional)
```python
# Line 800-802
if area_name is None:
    area_name = self._extract_location_from_query(query)
# Extract location từ query: "Sơn Trà", "Ngũ Hành Sơn", etc.
```

#### Bước 2: Generate Query Embedding
```python
# Line 815 (với filter) hoặc Line 874 (không filter
query_embedding = self.embeddings.embed_query(query)
# → Vector 1024 dimensions từ Ollama bge-m3 model
# → Cached để tối ưu performance
```

#### Bước 3: Vector Search trong Qdrant

**Option A: Với Location Filter**
```python
# Line 819-830
search_results = client.search(
    collection_name=self.collection_name,
    query_vector=query_embedding,
    limit=min(top_k + 1, 5),  # Top 5 results
    query_filter=Filter(
        must=[
            FieldCondition(key="area_name", match=MatchValue(value=area_name))
        ]
    ),
    with_payload=True,
    with_vectors=False  # Không cần vectors trong response
)
```

**Option B: Không có Filter (General Search)**
```python
# Line 874-876
results = self.vectorstore.similarity_search_with_score(
    query,
    k=min(top_k + 1, 5)  # Top 5 results
)
```

#### Bước 4: Similarity Scoring
```python
# Line 886-887 (Cosine Distance → Similarity)
similarity_score = max(0, 1 - score)  # Normalize to [0, 1]
# Filter: chỉ lấy similarity > 0.3 (Line 891)
```

#### Bước 5: Format Results
```python
# Line 905-915
hotels.append({
    "hotel_id": doc.metadata.get("hotel_id"),
    "hotel_name": hotel_name,
    "hotel_rank": doc.metadata.get("hotel_rank"),
    "hotel_price_average": doc.metadata.get("hotel_price_average"),
    "area_name": doc.metadata.get("area_name", ""),
    "similarity_score": float(similarity_score),
    "text_preview": doc.page_content[:200] + "..."
})
```

### Kết quả:
- Trả về `List[Dict]` với top_k hotels
- Mỗi hotel có metadata: ID, tên, giá, đánh giá, similarity score
- **Không có LLM generation** - chỉ vector search

---

## 💬 2. RAG QUERY FLOW (`ask()`)

### Flow diagram:
```
User Question
    ↓
[1] Generate Query Embedding
    ↓
[2] Vector Search (Retriever) → Top 5 documents
    ↓
[3] Combine Context từ 5 documents
    ↓
[4] Build Prompt với Context + Question
    ↓
[5] LLM Generation (LM Studio qwen3-4b-2507)
    ├─ max_tokens: 2048
    ├─ temperature: 0.3
    └─ Prompt: Chi tiết, so sánh hotels
    ↓
[6] Parse Response + Extract Sources
    ↓
Return Dict {answer, sources}
```

### Code Flow:

#### Bước 1-2: Retrieval (Tìm kiếm relevant documents)
```python
# Line 939
result = self.qa_chain({"query": question})
# → qa_chain tự động:
#    1. Generate query embedding
#    2. Search top k=5 documents trong vectorstore
#    3. Combine documents thành context
```

#### Bước 3-4: Context Preparation & Prompt Building
```python
# Line 708-718 (Prompt Template)
prompt_template = """Bạn là trợ lý tư vấn khách sạn tại Đà Nẵng...

Thông tin khách sạn:
{context}  # ← 5 documents được combine ở đây

Câu hỏi: {question}

Trả lời chi tiết... So sánh các khách sạn nếu có nhiều lựa chọn...
"""
```

**Context từ 5 documents:**
- Mỗi document là 1 chunk của hotel data
- LangChain tự động combine: `doc1.page_content + doc2.page_content + ...`
- Tổng context có thể ~4000-5000 characters (với k=5, chunk_size=800)

#### Bước 5: LLM Generation
```python
# Line 727-734 (QA Chain)
self.qa_chain = RetrievalQA.from_chain_type(
    llm=self.llm,  # ChatOpenAI với LM Studio
    chain_type="stuff",  # Combine tất cả context vào 1 prompt
    retriever=self.retriever,  # k=5
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True
)

# LLM Config:
# - max_tokens: 2048 (Line 173, 188)
# - temperature: 0.3 (Line 172, 187)
# - timeout: 120s (Line 175, 190)
```

**Chain Type = "stuff":**
- Combine tất cả 5 documents vào 1 prompt
- LLM xử lý toàn bộ context 1 lần
- Nhanh hơn "refine" hoặc "map_reduce"

#### Bước 6: Parse Response & Extract Sources
```python
# Line 942-965
response = {
    "question": question,
    "answer": result["result"],  # LLM generated answer
    "sources": []
}

# Extract source documents
for doc in result.get("source_documents", []):
    response["sources"].append({
        "hotel_id": doc.metadata.get("hotel_id"),
        "hotel_name": doc.metadata.get("hotel_name", ""),
        "hotel_rank": doc.metadata.get("hotel_rank"),
        "hotel_price_average": doc.metadata.get("hotel_price_average"),
        "area_name": doc.metadata.get("area_name", ""),
        "text_preview": page_content[:300] + "..."
    })
```

### Kết quả:
- Trả về `Dict` với:
  - `answer`: Câu trả lời được LLM generate (tối đa 2048 tokens)
  - `sources`: List 5 hotels được dùng làm context

---

## 🔄 3. RETRIEVER CONFIGURATION

### Retriever Setup:
```python
# Line 702-706 (_initialize_qa_chain)
self.retriever = self.vectorstore.as_retriever(
    search_kwargs={
        "k": 5  # Top 5 documents
    }
)
```

**Retriever hoạt động như thế nào:**
1. Nhận query text
2. Tự động generate embedding qua `self.embeddings`
3. Search trong Qdrant với vector similarity
4. Trả về top k=5 documents có similarity cao nhất
5. Combine documents thành context string

---

## 📊 4. COMPARISON: Search vs RAG

| Feature | `search_hotels()` | `ask()` |
|---------|------------------|---------|
| **LLM** | ❌ Không dùng | ✅ Dùng (LM Studio) |
| **Output** | List hotels | Câu trả lời tự nhiên |
| **Speed** | ~1-2s | ~5-15s |
| **Use case** | Tìm danh sách hotels | Hỏi đáp tự nhiên |
| **Sources** | top_k hotels | top 5 hotels |
| **Context** | Không có | Có (5 documents combined) |

### Ví dụ:

**Search:**
```python
results = rag.search_hotels("Khách sạn 5 sao gần biển")
# Returns: [{hotel_name: "...", price: ..., ...}, ...]
```

**RAG:**
```python
response = rag.ask("Khách sạn nào 5 sao gần biển?")
# Returns: {
#   answer: "Dựa trên thông tin tìm được, có một số khách sạn 5 sao gần biển...",
#   sources: [{hotel_id: 1, hotel_name: "...", ...}, ...]
# }
```

---

## 🔧 5. KEY COMPONENTS

### A. Embeddings (bge-m3)
```python
# Line 155-160
base_embeddings = OllamaEmbeddings(model="bge-m3", base_url=ollama_url)
self.embeddings = CachedOllamaEmbeddings(base_embeddings, cache_enabled=True)
```
- **Model**: bge-m3 (BAAI General Embedding)
- **Dimension**: 1024
- **Cache**: Có cache để tối ưu (tránh re-embedding)

### B. Vector Store (Qdrant)
```python
# Line 590-594
self.vectorstore = Qdrant(
    client=client,
    collection_name=self.collection_name,
    embeddings=self.embeddings
)
```
- **Distance**: Cosine
- **Index**: HNSW (m=16, ef_construct=200)
- **Storage**: Hotel documents với metadata

### C. LLM (qwen3-4b-2507 via LM Studio)
```python
# Line 168-177
self.llm = ChatOpenAI(
    model="qwen/qwen3-4b-2507",
    openai_api_base="http://192.168.10.42:1234/v1",
    max_tokens=2048,
    temperature=0.3
)
```
- **Model**: Qwen3-4B
- **Max tokens**: 2048 (tăng từ 512)
- **Temperature**: 0.3 (focused, consistent)

---

## 🎯 6. OPTIMIZATION FEATURES

### 1. Embedding Cache
```python
# Line 82-113
def embed_documents(self, texts: List[str]) -> List[List[float]]:
    # Check cache trước khi embed
    # Cache miss mới gọi Ollama
```

### 2. Batch Processing
```python
# Line 600-688
# Process documents theo batch (batch_size=50)
# Retry logic nếu lỗi
```

### 3. Smart Chunking
```python
# Line 466-467
chunks = self.chunker.chunk_hotel_document(hotel_data, semantic_text)
# Chunk hotel data để preserve semantic meaning
```

### 4. HNSW Index
```python
# Line 572-586
hnsw_config = HnswConfigDiff(m=16, ef_construct=200)
# Fast approximate nearest neighbor search
```

---

## 📝 7. EXAMPLE QUERY FLOW

### Query: "Khách sạn nào có view biển đẹp ở Ngũ Hành Sơn?"

#### Step 1: Query Processing
```python
# Extract location
area_name = "Ngũ Hành Sơn"  # Từ _extract_location_from_query()
```

#### Step 2: Embedding
```python
query_embedding = embed("Khách sạn nào có view biển đẹp ở Ngũ Hành Sơn?")
# → [0.123, -0.456, ..., 0.789] (1024 dims)
```

#### Step 3: Vector Search (RAG mode)
```python
# Retriever search với k=5
documents = retriever.get_relevant_documents(query)
# → [
#   Document(page_content="Sheraton Đà Nẵng... view biển...", metadata={hotel_id: 1, ...}),
#   Document(page_content="InterContinental... hướng biển...", metadata={hotel_id: 2, ...}),
#   ... (5 documents total)
# ]
```

#### Step 4: Context Building
```python
context = """
Document 1: Sheraton Đà Nẵng... view biển đẹp... 5 sao... 2.026.580 VND...
Document 2: InterContinental Đà Nẵng... hướng biển... 5 sao... 2.625.000 VND...
...
"""
```

#### Step 5: Prompt to LLM
```python
prompt = """
Bạn là trợ lý tư vấn khách sạn tại Đà Nẵng...

Thông tin khách sạn:
[context từ step 4]

Câu hỏi: Khách sạn nào có view biển đẹp ở Ngũ Hành Sơn?

Trả lời chi tiết, tự nhiên bằng tiếng Việt...
"""
```

#### Step 6: LLM Generation
```python
# LM Studio generate response (max 2048 tokens)
answer = "Dựa trên thông tin tìm được, có một số khách sạn có view biển đẹp ở Ngũ Hành Sơn:

1. **Sheraton Đà Nẵng** - Khách sạn 5 sao với view biển tuyệt đẹp, giá trung bình 2.026.580 VND...

2. **InterContinental Đà Nẵng** - Khách sạn 5 sao hướng biển, giá trung bình 2.625.000 VND...

[So sánh và tư vấn thêm...]"
```

#### Step 7: Response
```python
{
    "question": "Khách sạn nào có view biển đẹp ở Ngũ Hành Sơn?",
    "answer": "[LLM generated answer]",
    "sources": [
        {hotel_id: 1, hotel_name: "Sheraton Đà Nẵng", ...},
        {hotel_id: 2, hotel_name: "InterContinental Đà Nẵng", ...},
        ... (5 sources)
    ]
}
```

---

## 🔑 Key Points

1. **RAG = Retrieval + Generation**: Tìm kiếm documents trước, rồi mới generate answer
2. **k=5**: Lấy top 5 documents làm context (tăng từ 2 để chi tiết hơn)
3. **max_tokens=2048**: Cho phép response dài và chi tiết hơn
4. **Embedding cache**: Tối ưu performance, tránh re-embedding
5. **Smart chunking**: Chia nhỏ hotel data nhưng preserve semantic meaning
6. **Location filtering**: Tự động extract và filter theo location nếu có

