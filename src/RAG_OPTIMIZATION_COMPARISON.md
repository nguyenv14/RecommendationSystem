# So Sánh Trước & Sau Tối Ưu Hóa RAG

## 🔄 Flow Hiện Tại vs Flow Tối Ưu

### Flow Hiện Tại (Có Vấn Đề)

```
User Query
    ↓
[1] Embed Query (không cache persistent)
    ↓
[2] Vector Search (k=5, không re-rank)
    ↓
[3] Build Context (combine tất cả, không check token limit)
    ↓
[4] Generate Answer (prompt dài, không cache response)
    ↓
Response
```

**Vấn đề:**
- ❌ Embedding không cache persistent
- ❌ Không có query preprocessing
- ❌ Context có thể quá dài
- ❌ Response không cache
- ❌ Không có re-ranking

### Flow Tối Ưu (Đề Xuất)

```
User Query
    ↓
[1] Check Response Cache → Hit? → Return (0.1s)
    ↓ (Miss)
[2] Preprocess Query (normalize, expand synonyms)
    ↓
[3] Check Embedding Cache → Hit? → Use cached
    ↓ (Miss)
[4] Batch Embed Query (nếu nhiều queries)
    ↓
[5] Hybrid Search (semantic + keyword)
    ↓
[6] Re-rank Results (cross-encoder)
    ↓
[7] Build Context (với token limit, sort by relevance)
    ↓
[8] Generate Answer (optimized prompt)
    ↓
[9] Cache Response
    ↓
Response
```

**Cải thiện:**
- ✅ Persistent embedding cache
- ✅ Query preprocessing
- ✅ Context window management
- ✅ Response caching
- ✅ Re-ranking
- ✅ Hybrid search

## 📊 Performance Comparison

### Scenario 1: First Query (Cold Start)

| Step | Before | After | Improvement |
|------|--------|-------|-------------|
| Query preprocessing | ❌ None | ✅ 10ms | - |
| Embedding (cache miss) | 200ms | 200ms | - |
| Vector search | 50ms | 50ms | - |
| Re-ranking | ❌ None | ✅ 100ms | - |
| Context building | 10ms | 20ms | +10ms (token counting) |
| LLM generation | 2000ms | 1800ms | -200ms (optimized prompt) |
| **Total** | **2260ms** | **2180ms** | **-80ms (3.5%)** |

### Scenario 2: Repeated Query (Hot Cache)

| Step | Before | After | Improvement |
|------|--------|-------|-------------|
| Response cache | ❌ None | ✅ 5ms | - |
| **Total** | **2260ms** | **5ms** | **-2255ms (99.8%)** |

### Scenario 3: Similar Query (Embedding Cache Hit)

| Step | Before | After | Improvement |
|------|--------|-------|-------------|
| Embedding (cache hit) | 200ms | ✅ 5ms | -195ms |
| **Total** | **2260ms** | **2070ms** | **-190ms (8.4%)** |

### Scenario 4: Indexing 1000 Documents

| Step | Before | After | Improvement |
|------|--------|-------|-------------|
| Embedding (sequential) | 200s | ✅ 10s | -190s |
| Upsert | 30s | 30s | - |
| **Total** | **230s** | **40s** | **-190s (82.6%)** |

## 🎯 Code Changes Summary

### 1. Remove Duplication

**Before:**
```python
# core/embeddings.py
class EmbeddingService:
    def embed_query(self, text: str) -> List[float]:
        ...

# shared/embedding_manager.py  
class EmbeddingManager:
    def embed_query(self, text: str) -> List[float]:
        ...  # Duplicate code!
```

**After:**
```python
# core/embeddings.py
class EmbeddingService:
    def embed_query(self, text: str) -> List[float]:
        ...

# shared/embedding_manager.py - DELETED
```

### 2. Remove Dead Code

**Before:**
```python
class RAGService:
    def __init__(self):
        self.qa_chain = None  # LangChain QA chain
        self._initialize_qa_chain()  # Created but never used!
    
    def ask(self, question: str):
        # Uses RetrieverService + GeneratorService
        # Does NOT use self.qa_chain
        ...
```

**After:**
```python
class RAGService:
    def __init__(self):
        # No QA chain - only use RetrieverService + GeneratorService
        ...
    
    def ask(self, question: str):
        # Uses RetrieverService + GeneratorService
        ...
```

### 3. Persistent Cache

**Before:**
```python
class EmbeddingService:
    def __init__(self):
        self._cache = {}  # In-memory only
    
    def embed_query(self, text: str):
        if text in self._cache:
            return self._cache[text]  # Lost on restart!
        ...
```

**After:**
```python
class EmbeddingService:
    def __init__(self):
        self._cache = PersistentCache(cache_dir=".embedding_cache")
    
    def embed_query(self, text: str):
        cached = self._cache.get(text)
        if cached:
            return cached  # Persists across restarts!
        ...
```

### 4. Batch Embedding

**Before:**
```python
def index_documents(self, documents):
    for doc in documents:
        vector = self.embedding.embed_query(text)  # Sequential!
        points.append(PointStruct(id=doc_id, vector=vector))
```

**After:**
```python
def index_documents(self, documents):
    texts = [doc.get(text_field) for doc in documents]
    vectors = self.embedding.embed_documents(texts, batch_size=32)  # Batch!
    for doc, vector in zip(documents, vectors):
        points.append(PointStruct(id=doc_id, vector=vector))
```

### 5. Context Management

**Before:**
```python
def _build_context(self, documents):
    context_parts = []
    for doc in documents:
        text = self._extract_text(doc)
        context_parts.append(text)  # No token limit check!
    return "\n\n".join(context_parts)
```

**After:**
```python
def _build_context(self, documents, max_tokens=4000):
    # Sort by relevance
    sorted_docs = sorted(documents, key=lambda x: x.get("score", 0), reverse=True)
    
    context_parts = []
    current_tokens = 0
    
    for doc in sorted_docs:
        text = self._extract_text(doc)
        tokens = count_tokens(text)
        
        if current_tokens + tokens > max_tokens:
            break  # Stop if exceeds limit
        
        context_parts.append(text)
        current_tokens += tokens
    
    return "\n\n".join(context_parts)
```

### 6. Query Preprocessing

**Before:**
```python
def ask(self, question: str):
    documents = self.retriever_service.retrieve(question)  # Direct query
    ...
```

**After:**
```python
def ask(self, question: str):
    # Preprocess query
    processed_query = self.query_preprocessor.preprocess(question)
    
    documents = self.retriever_service.retrieve(processed_query)
    ...
```

### 7. Response Caching

**Before:**
```python
def ask(self, question: str):
    # Always do full pipeline
    documents = self.retriever_service.retrieve(question)
    result = self.generator.generate_from_documents(question, documents)
    return result
```

**After:**
```python
def ask(self, question: str):
    # Check cache first
    cached = self.response_cache.get(question)
    if cached:
        return cached
    
    # Full pipeline
    documents = self.retriever_service.retrieve(question)
    result = self.generator.generate_from_documents(question, documents)
    
    # Cache response
    self.response_cache.set(question, result)
    return result
```

## 📈 Expected Metrics Improvement

### Latency (P50)

| Query Type | Before | After | Improvement |
|------------|--------|-------|-------------|
| Cold query | 2.3s | 2.2s | -4% |
| Cached query | 2.3s | 0.05s | -98% |
| Similar query | 2.3s | 2.1s | -9% |

### Throughput

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Indexing (docs/sec) | 1 | 25-30 | 25-30x |
| Queries/sec (cached) | 0.4 | 20 | 50x |
| Queries/sec (uncached) | 0.4 | 0.5 | 25% |

### Resource Usage

| Resource | Before | After | Improvement |
|----------|--------|-------|-------------|
| Memory (idle) | 500MB | 350MB | -30% |
| CPU (indexing) | 100% | 80% | -20% |
| Disk I/O | Low | Medium | + (cache) |

## 🎓 Lessons Learned

1. **Cache Everything**: Embeddings, responses, và intermediate results
2. **Batch Operations**: Luôn batch khi có thể
3. **Remove Dead Code**: Giảm complexity và memory
4. **Preprocess Input**: Normalize và expand queries
5. **Monitor Context**: Tránh vượt token limits
6. **Re-rank Results**: Tăng precision với cross-encoder

## 🚦 Migration Path

### Phase 1: Safe Changes (No Breaking)
1. Add persistent cache (backward compatible)
2. Add query preprocessing (optional)
3. Add response cache (optional)

### Phase 2: Performance (Low Risk)
1. Batch embedding
2. Context management
3. Remove dead code

### Phase 3: Advanced (Higher Risk)
1. Hybrid search
2. Re-ranking
3. Async processing

**Recommendation:** Start with Phase 1, measure impact, then proceed to Phase 2.

