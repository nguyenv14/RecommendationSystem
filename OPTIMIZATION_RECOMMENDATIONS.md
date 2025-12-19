# Đề Xuất Tối Ưu Hóa Source Code

## 🔴 Priority 1: Critical Issues (Fix Ngay)

### 1. **Database Connection Leak trong IndexingService**

**Vấn đề:**
```python
# src/core/indexing.py:70-79
def _get_db_engine(self):
    if self._db_engine is None:
        settings = get_settings()
        self._db_engine = create_engine(...)
    return self._db_engine
```

**Vấn đề:**
- Engine không được dispose sau khi dùng
- Connection pool có thể bị leak
- Không có cleanup method

**Giải pháp:**
```python
def _get_db_engine(self):
    if self._db_engine is None:
        settings = get_settings()
        self._db_engine = create_engine(
            f"mysql+pymysql://...",
            pool_pre_ping=True,
            pool_size=5,  # Limit pool size
            max_overflow=10
        )
    return self._db_engine

def cleanup(self):
    """Cleanup resources"""
    if self._db_engine:
        self._db_engine.dispose()
        self._db_engine = None
```

**Impact:** Tránh connection leak, tăng stability

---

### 2. **Vector Size Mismatch trong app.py**

**Vấn đề:**
```python
# app.py:87
(Collections.RECOMMENDATION_HOTELS, "Recommendation (Similar Hotels)", 384, "🎯"),
```

Nhưng trong code thực tế dùng 1024 (bge-m3 model).

**Giải pháp:**
```python
(Collections.RECOMMENDATION_HOTELS, "Recommendation (Similar Hotels)", 1024, "🎯"),
```

**Impact:** Tránh lỗi khi tạo collection

---

### 3. **Tạo VectorStoreService Mới Mỗi Lần trong ensure_collections_ready()**

**Vấn đề:**
```python
# app.py:80
temp_vectorstore = VectorStoreService(url=settings.QDRANT_URL)
```

Tạo mới mỗi lần gọi, không tái sử dụng global service.

**Giải pháp:**
```python
def ensure_collections_ready():
    global vectorstore_service
    if vectorstore_service is None:
        vectorstore_service = VectorStoreService(url=settings.QDRANT_URL)
    client = vectorstore_service.client
    # ...
```

**Impact:** Giảm overhead, tái sử dụng connection

---

### 4. **Gọi get_settings() Nhiều Lần**

**Vấn đề:**
`get_settings()` được gọi nhiều lần trong cùng một function, có thể cache.

**Giải pháp:**
```python
# Cache settings trong function scope
settings = get_settings()  # Gọi 1 lần
# Dùng settings cho tất cả operations
```

**Impact:** Giảm overhead nhỏ

---

## 🟡 Priority 2: Performance Optimizations

### 5. **IndexingService: Không Dispose Engine Sau Khi Dùng**

**Vấn đề:**
```python
# src/core/indexing.py:155-157
engine = self._get_db_engine()
query = "SELECT * FROM tbl_hotel WHERE hotel_status = 1"
hotels_df = pd.read_sql(text(query), engine)
# Engine không được dispose
```

**Giải pháp:**
```python
# Option 1: Dispose sau khi dùng (nếu không cần reuse)
engine = self._get_db_engine()
try:
    hotels_df = pd.read_sql(text(query), engine)
finally:
    # Không dispose nếu muốn reuse connection pool
    pass  # Connection pool tự quản lý

# Option 2: Dùng context manager
with engine.connect() as conn:
    hotels_df = pd.read_sql(text(query), conn)
```

**Impact:** Quản lý connection tốt hơn

---

### 6. **RetrieverService: Có Thể Cache Item Text Extraction**

**Vấn đề:**
```python
# src/core/retriever.py:300-326
def _get_item_text(self, payload: Dict[str, Any]) -> str:
    # Extract text mỗi lần
```

**Giải pháp:**
```python
# Cache extracted text trong payload nếu có thể
# Hoặc cache trong memory với LRU cache
from functools import lru_cache

@lru_cache(maxsize=1000)
def _get_item_text_cached(self, payload_str: str) -> str:
    payload = json.loads(payload_str)
    # ... extraction logic
```

**Impact:** Giảm CPU cho repeated queries

---

### 7. **IndexingService: Có Thể Parallelize Embedding**

**Vấn đề:**
```python
# src/core/indexing.py:200-204
for i in range(0, len(hotel_texts), batch_size):
    batch = hotel_texts[i:i + batch_size]
    batch_embeddings = self.embedding_service.embed_documents(batch)
    # Sequential processing
```

**Giải pháp:**
```python
# Nếu Ollama hỗ trợ concurrent requests
from concurrent.futures import ThreadPoolExecutor

def embed_batch(batch):
    return self.embedding_service.embed_documents(batch)

with ThreadPoolExecutor(max_workers=3) as executor:
    batches = [hotel_texts[i:i+batch_size] 
               for i in range(0, len(hotel_texts), batch_size)]
    results = list(executor.map(embed_batch, batches))
    dense_embeddings = [emb for batch_embs in results for emb in batch_embs]
```

**Impact:** Tăng tốc indexing 2-3x (nếu Ollama hỗ trợ)

---

### 8. **app.py: ensure_collections_ready() Có Thể Tối Ưu**

**Vấn đề:**
```python
# app.py:91-92
existing_collections = client.get_collections()
existing_names = [col.name for col in existing_collections.collections]
```

**Giải pháp:**
```python
# Cache collection names để tránh gọi API nhiều lần
existing_collections = client.get_collections()
existing_names = {col.name for col in existing_collections.collections}  # Set thay vì list
```

**Impact:** O(1) lookup thay vì O(n)

---

## 🟢 Priority 3: Code Quality

### 9. **Unused Imports**

**Vấn đề:**
Một số file có imports không dùng.

**Giải pháp:**
```bash
# Dùng tool để check
pip install autoflake
autoflake --in-place --remove-all-unused-imports src/**/*.py
```

**Impact:** Clean code, giảm confusion

---

### 10. **Error Handling: Thiếu Retry Logic**

**Vấn đề:**
```python
# Nhiều chỗ có try-except nhưng không retry
try:
    result = some_operation()
except Exception as e:
    logger.error(f"Error: {e}")
    return None
```

**Giải pháp:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def some_operation():
    # ...
```

**Impact:** Tăng resilience cho network operations

---

### 11. **Type Hints: Thiếu Một Số Chỗ**

**Vấn đề:**
Một số methods thiếu return type hints.

**Giải pháp:**
```python
# Thêm type hints đầy đủ
def index_recommendation_hotels(
    self,
    collection_name: Optional[str] = None,
    recreate_collection: bool = False,
    batch_size: int = 10
) -> Dict[str, Any]:  # ✅ Có return type
```

**Impact:** Better IDE support, type checking

---

### 12. **Logging: Một Số Chỗ Log Quá Nhiều**

**Vấn đề:**
```python
# src/core/indexing.py:204
logger.info(f"Embedded {min(i + batch_size, len(hotel_texts))}/{len(hotel_texts)}")
# Log mỗi batch → quá nhiều logs
```

**Giải pháp:**
```python
# Chỉ log mỗi 10 batches hoặc dùng logger.debug
if i % (batch_size * 10) == 0:
    logger.info(f"Embedded {min(i + batch_size, len(hotel_texts))}/{len(hotel_texts)}")
else:
    logger.debug(f"Embedded {min(i + batch_size, len(hotel_texts))}/{len(hotel_texts)}")
```

**Impact:** Giảm log noise

---

## 📊 Tổng Kết

### Quick Wins (Làm Trong 1 Giờ):
1. ✅ Fix vector size mismatch (5 phút)
2. ✅ Tái sử dụng vectorstore_service (10 phút)
3. ✅ Cache get_settings() calls (15 phút)
4. ✅ Set lookup thay vì list (5 phút)
5. ✅ Reduce logging noise (10 phút)

**Total: ~45 phút**

### Medium Priority (Làm Trong 1 Ngày):
1. ✅ Fix database connection management (1 giờ)
2. ✅ Add cleanup methods (30 phút)
3. ✅ Add retry logic cho network calls (2 giờ)
4. ✅ Improve error handling (1 giờ)

**Total: ~4.5 giờ**

### Long Term (Làm Khi Có Thời Gian):
1. ✅ Parallelize embedding (nếu Ollama hỗ trợ)
2. ✅ Add connection pooling metrics
3. ✅ Implement circuit breaker pattern
4. ✅ Add performance monitoring

---

## 🎯 Recommended Action Plan

### Week 1: Critical Fixes
- [ ] Fix database connection leak
- [ ] Fix vector size mismatch
- [ ] Tái sử dụng services
- [ ] Cache settings calls

### Week 2: Performance
- [ ] Optimize collection lookup
- [ ] Reduce logging noise
- [ ] Add retry logic

### Week 3: Code Quality
- [ ] Remove unused imports
- [ ] Add missing type hints
- [ ] Improve error messages

---

*Tài liệu này tổng hợp các đề xuất tối ưu hóa dựa trên code review ngày [DATE]*
