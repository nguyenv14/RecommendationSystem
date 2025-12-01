# Phân Tích & Tối Ưu Hóa RAG System

## 📋 Tổng Quan Cấu Trúc Hiện Tại

### Kiến Trúc Hiện Tại
```
src/
├── core/
│   ├── rag.py              # RAGService - Main RAG orchestrator
│   ├── retriever.py        # RetrieverService - Vector search
│   ├── generator.py        # GeneratorService - LLM generation
│   ├── embeddings.py       # EmbeddingService - Text embeddings
│   └── vectorstore.py      # VectorStoreService - Qdrant operations
├── shared/
│   ├── embedding_manager.py # EmbeddingManager (duplicate với EmbeddingService?)
│   └── qdrant_manager.py   # QdrantManager (duplicate với VectorStoreService?)
├── data/
│   ├── normalizer.py       # Data normalization
│   └── processor.py        # ETL pipeline
└── config/
    └── settings.py         # Configuration
```

## 🔍 Phân Tích Vấn Đề

### 1. **Code Duplication (Trùng Lặp Code)**

#### Vấn đề:
- `EmbeddingService` (core/embeddings.py) và `EmbeddingManager` (shared/embedding_manager.py) có chức năng tương tự
- `VectorStoreService` (core/vectorstore.py) và `QdrantManager` (shared/qdrant_manager.py) trùng lặp
- Cả hai đều wrap QdrantClient với logic tương tự

#### Ảnh hưởng:
- Khó maintain (phải sửa 2 nơi)
- Tăng memory footprint
- Confusion về nên dùng class nào

### 2. **RAGService Có 2 Implementation Paths**

#### Vấn đề:
Trong `rag.py`, có 2 cách xử lý:
- **Path 1**: LangChain RetrievalQA chain (được khởi tạo nhưng không dùng)
- **Path 2**: Custom flow với RetrieverService + GeneratorService (đang dùng)

```python
# Line 85-91: Khởi tạo QA chain nhưng không dùng
self.qa_chain: Optional[RetrievalQA] = None
self._initialize_qa_chain()  # Tạo nhưng không dùng trong ask()

# Line 178-247: ask() method dùng RetrieverService + GeneratorService
# KHÔNG dùng self.qa_chain
```

#### Ảnh hưởng:
- Dead code (QA chain không được sử dụng)
- Tăng memory (khởi tạo LLM 2 lần)
- Confusion về flow

### 3. **Embedding Cache Không Hiệu Quả**

#### Vấn đề:
- Cache chỉ lưu trong memory (`self._cache = {}`)
- Không persistent giữa các sessions
- Không có TTL (time-to-live)
- Cache key chỉ dùng MD5 hash (có thể collision)

#### Ảnh hưởng:
- Mất cache khi restart
- Memory leak nếu cache không được clear
- Không tận dụng được cache từ lần chạy trước

### 4. **Context Building Không Tối Ưu**

#### Vấn đề:
Trong `generator.py`, `_build_context()`:
```python
# Line 157-185: Combine tất cả documents thành 1 string
# Không có:
# - Token counting (có thể vượt quá context window)
# - Relevance re-ranking
# - Deduplication
# - Priority ordering
```

#### Ảnh hưởng:
- Có thể vượt quá context window của LLM
- Không tận dụng được relevance scores
- Có thể có duplicate information

### 5. **Retrieval Không Có Re-ranking**

#### Vấn đề:
- Chỉ dùng vector similarity (cosine)
- Không có cross-encoder re-ranking
- Không có hybrid search (keyword + semantic)

#### Ảnh hưởng:
- Kết quả có thể không chính xác
- Không tận dụng được metadata filters hiệu quả

### 6. **Prompt Template Quá Dài**

#### Vấn đề:
Prompt template trong `generator.py` (line 247-284) rất dài (~2000+ tokens):
- Nhiều rules và examples
- Lặp lại instructions
- Có thể optimize bằng cách rút gọn

#### Ảnh hưởng:
- Tốn tokens (chi phí)
- Tăng latency
- Có thể confuse LLM với quá nhiều instructions

### 7. **Indexing Không Batch Embedding**

#### Vấn đề:
Trong `rag.py`, `index_documents()`:
```python
# Line 324-325: Embed từng document một
vector = self.embedding.embed_query(text)  # Sequential
```

#### Ảnh hưởng:
- Chậm khi index nhiều documents
- Không tận dụng được batch processing của Ollama

### 8. **Không Có Query Preprocessing**

#### Vấn đề:
- Query được embed trực tiếp không có preprocessing
- Không có query expansion
- Không có spell checking
- Không có intent extraction

#### Ảnh hưởng:
- Kết quả search kém chính xác
- Không handle được typos
- Không hiểu được user intent

### 9. **Không Có Response Caching**

#### Vấn đề:
- Mỗi query đều phải:
  1. Embed query
  2. Vector search
  3. LLM generation
- Không cache responses cho similar queries

#### Ảnh hưởng:
- Latency cao
- Tốn resources
- User experience kém

### 10. **Error Handling Không Đầy Đủ**

#### Vấn đề:
- Nhiều try-except nhưng không có retry logic
- Không có fallback mechanisms
- Không có circuit breaker pattern

#### Ảnh hưởng:
- System dễ fail khi có lỗi tạm thời
- Không resilient

## 🚀 Đề Xuất Tối Ưu Hóa

### Priority 1: Critical Optimizations (Làm ngay)

#### 1.1. **Loại Bỏ Code Duplication**

**Action:**
- Chọn 1 implementation cho embeddings: `EmbeddingService` hoặc `EmbeddingManager`
- Chọn 1 implementation cho vectorstore: `VectorStoreService` hoặc `QdrantManager`
- Deprecate và remove code không dùng

**Recommendation:**
- Giữ `EmbeddingService` (trong core/) vì đã được dùng nhiều
- Giữ `VectorStoreService` (trong core/) vì đã được dùng nhiều
- Remove `EmbeddingManager` và `QdrantManager` từ shared/

**Impact:** Giảm codebase, dễ maintain

#### 1.2. **Loại Bỏ Dead Code (QA Chain)**

**Action:**
- Remove `_initialize_qa_chain()` method
- Remove `self.qa_chain`, `self.vectorstore`, `self.retriever` (LangChain)
- Chỉ giữ custom flow với RetrieverService + GeneratorService

**Impact:** Giảm memory, giảm confusion

#### 1.3. **Implement Persistent Embedding Cache**

**Action:**
```python
# Sử dụng Redis hoặc disk cache
from functools import lru_cache
import pickle
import os

class EmbeddingCache:
    def __init__(self, cache_dir=".embedding_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, text: str) -> Optional[List[float]]:
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, text: str, embedding: List[float]):
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)
```

**Impact:** Tăng tốc độ, giảm API calls

#### 1.4. **Batch Embedding cho Indexing**

**Action:**
```python
# Trong rag.py, index_documents()
# Thay vì:
for doc in documents:
    vector = self.embedding.embed_query(text)

# Dùng:
texts = [doc.get(text_field, "") for doc in documents]
vectors = self.embedding.embed_documents(texts, batch_size=32)
```

**Impact:** Tăng tốc indexing 10-20x

### Priority 2: Performance Optimizations

#### 2.1. **Context Window Management**

**Action:**
```python
def _build_context(self, documents: List[Dict], max_tokens: int = 4000) -> str:
    """Build context với token limit"""
    from tiktoken import encoding_for_model
    
    enc = encoding_for_model("gpt-3.5-turbo")  # Approximate
    context_parts = []
    current_tokens = 0
    
    # Sort by score (relevance)
    sorted_docs = sorted(documents, key=lambda x: x.get("score", 0), reverse=True)
    
    for doc in sorted_docs:
        text = self._extract_text(doc.get("payload", {}))
        tokens = len(enc.encode(text))
        
        if current_tokens + tokens > max_tokens:
            break
        
        context_parts.append(text)
        current_tokens += tokens
    
    return "\n\n".join(context_parts)
```

**Impact:** Tránh vượt context window, tăng chất lượng

#### 2.2. **Query Preprocessing**

**Action:**
```python
class QueryPreprocessor:
    def preprocess(self, query: str) -> str:
        # 1. Normalize
        query = query.lower().strip()
        
        # 2. Remove stopwords (Vietnamese)
        stopwords = ["là", "của", "và", "có", "tại", "ở"]
        words = query.split()
        query = " ".join([w for w in words if w not in stopwords])
        
        # 3. Expand synonyms
        synonyms = {
            "ks": "khách sạn",
            "resort": "khách sạn resort",
            "5 sao": "năm sao"
        }
        for key, value in synonyms.items():
            query = query.replace(key, value)
        
        return query
```

**Impact:** Tăng độ chính xác retrieval

#### 2.3. **Response Caching**

**Action:**
```python
# Sử dụng Redis hoặc in-memory cache với TTL
from functools import lru_cache
import hashlib
import json

class ResponseCache:
    def __init__(self, ttl=3600):  # 1 hour
        self.cache = {}
        self.ttl = ttl
    
    def get_key(self, question: str) -> str:
        return hashlib.md5(question.encode()).hexdigest()
    
    def get(self, question: str) -> Optional[Dict]:
        key = self.get_key(question)
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['response']
        return None
    
    def set(self, question: str, response: Dict):
        key = self.get_key(question)
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
```

**Impact:** Giảm latency 50-80% cho repeated queries

### Priority 3: Advanced Optimizations

#### 3.1. **Hybrid Search (Keyword + Semantic)**

**Action:**
```python
def hybrid_search(self, query: str, top_k: int = 5):
    # 1. Semantic search (vector)
    semantic_results = self.retriever_service.retrieve(query, top_k=top_k*2)
    
    # 2. Keyword search (BM25-like)
    keyword_results = self._keyword_search(query, top_k=top_k*2)
    
    # 3. Combine và re-rank
    combined = self._combine_and_rerank(semantic_results, keyword_results)
    
    return combined[:top_k]
```

**Impact:** Tăng recall và precision

#### 3.2. **Re-ranking với Cross-Encoder**

**Action:**
```python
# Sử dụng cross-encoder model để re-rank
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        pairs = [(query, doc['payload'].get('text', '')) for doc in documents]
        scores = self.model.predict(pairs)
        
        # Sort by scores
        reranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [doc for doc, score in reranked]
```

**Impact:** Tăng độ chính xác top results

#### 3.3. **Prompt Optimization**

**Action:**
- Rút gọn prompt template
- Sử dụng few-shot examples thay vì verbose instructions
- Dynamic prompt based on query type

**Impact:** Giảm tokens, tăng tốc độ

#### 3.4. **Async Processing**

**Action:**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def ask_async(self, question: str) -> Dict:
    # Parallel: embedding + cache lookup
    embedding_task = asyncio.create_task(self._embed_async(question))
    cache_task = asyncio.create_task(self._check_cache_async(question))
    
    # Wait for both
    embedding, cached = await asyncio.gather(embedding_task, cache_task)
    
    if cached:
        return cached
    
    # Continue with retrieval and generation
    ...
```

**Impact:** Giảm latency 20-30%

### Priority 4: Monitoring & Observability

#### 4.1. **Add Metrics**

**Action:**
```python
# Track:
# - Query latency
# - Cache hit rate
# - Embedding time
# - Retrieval time
# - Generation time
# - Token usage
```

#### 4.2. **Add Logging**

**Action:**
- Structured logging với context
- Log query, retrieved docs, generated answer
- Performance metrics

## 📊 Expected Improvements

| Optimization | Impact | Effort | Priority |
|-------------|--------|--------|----------|
| Remove duplication | High | Low | P1 |
| Remove dead code | Medium | Low | P1 |
| Persistent cache | High | Medium | P1 |
| Batch embedding | High | Low | P1 |
| Context management | Medium | Medium | P2 |
| Query preprocessing | Medium | Low | P2 |
| Response caching | High | Medium | P2 |
| Hybrid search | High | High | P3 |
| Re-ranking | Medium | High | P3 |
| Async processing | Medium | High | P3 |

## 🎯 Implementation Roadmap

### Phase 1 (Week 1): Cleanup
- [ ] Remove code duplication
- [ ] Remove dead code (QA chain)
- [ ] Add persistent embedding cache

### Phase 2 (Week 2): Performance
- [ ] Batch embedding
- [ ] Context window management
- [ ] Query preprocessing
- [ ] Response caching

### Phase 3 (Week 3-4): Advanced
- [ ] Hybrid search
- [ ] Re-ranking
- [ ] Prompt optimization
- [ ] Async processing

### Phase 4 (Ongoing): Monitoring
- [ ] Add metrics
- [ ] Add structured logging
- [ ] Performance monitoring dashboard

## 📝 Notes

- Tất cả optimizations nên có tests
- Measure before/after performance
- Gradual rollout với feature flags
- Monitor for regressions

