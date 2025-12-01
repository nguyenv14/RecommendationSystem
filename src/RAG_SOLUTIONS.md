# Giải Pháp Tối Ưu Hóa RAG - Chi Tiết Implementation

## 1. 🔄 Embedding Cache Persistent

### Vấn Đề Hiện Tại
- Cache chỉ lưu trong memory (`self._cache = {}`)
- Mất cache khi restart application
- Không tận dụng được cache từ lần chạy trước
- Memory leak nếu cache không được clear

### Giải Pháp Đề Xuất

#### Option 1: Disk Cache (Đơn Giản, Không Cần Dependencies)

**Cách hoạt động:**
- Lưu embeddings vào files trong thư mục `.embedding_cache/`
- Mỗi embedding = 1 file (hash của text làm tên file)
- Format: pickle hoặc JSON

**Ưu điểm:**
- ✅ Không cần external service (Redis)
- ✅ Dễ implement
- ✅ Persistent giữa các sessions
- ✅ Có thể backup/restore

**Nhược điểm:**
- ❌ Chậm hơn Redis (disk I/O)
- ❌ Tốn disk space
- ❌ Cần quản lý file cleanup

**Cấu trúc:**
```
.embedding_cache/
├── a1b2c3d4e5f6... (hash của text)
├── f6e5d4c3b2a1...
└── ...
```

**Implementation Strategy:**
1. Tạo class `PersistentEmbeddingCache`
2. Method `get(text)` → đọc file nếu exists
3. Method `set(text, embedding)` → ghi file
4. Method `clear()` → xóa tất cả files
5. Method `cleanup_old(ttl_days)` → xóa files cũ

**Cache Key Strategy:**
- Dùng MD5 hash của text: `hashlib.md5(text.encode()).hexdigest()`
- Hoặc SHA256 để tránh collision
- Lưu metadata (timestamp, model_name) trong filename hoặc separate metadata file

**File Format:**
- Option A: Pickle (nhanh, binary)
- Option B: JSON (readable, nhưng chậm hơn)
- Option C: NumPy array file (`.npy`) - tối ưu cho vectors

**Cleanup Strategy:**
- Background thread định kỳ xóa files cũ (>30 days)
- Hoặc LRU cache với max size (xóa files ít dùng nhất)

#### Option 2: Redis Cache (Nhanh, Scalable)

**Cách hoạt động:**
- Lưu embeddings trong Redis
- Key = hash(text), Value = embedding vector (JSON hoặc binary)
- Có TTL tự động

**Ưu điểm:**
- ✅ Rất nhanh (in-memory)
- ✅ Có TTL tự động
- ✅ Có thể share giữa nhiều instances
- ✅ Có thể monitor qua Redis CLI

**Nhược điểm:**
- ❌ Cần Redis server
- ❌ Tốn memory của Redis
- ❌ Phức tạp hơn disk cache

**Implementation Strategy:**
1. Tạo class `RedisEmbeddingCache`
2. Connect đến Redis (dùng `redis-py`)
3. Key format: `embedding:{hash}` hoặc `embedding:{model}:{hash}`
4. Value: JSON array hoặc pickle
5. TTL: 30 days (2592000 seconds)

**Redis Structure:**
```
Key: embedding:bge-m3:a1b2c3d4...
Value: [0.123, 0.456, ...] (JSON array)
TTL: 2592000
```

**Memory Management:**
- Set maxmemory policy: `allkeys-lru`
- Monitor memory usage
- Có thể compress vectors (quantization) nếu cần

#### Option 3: Hybrid (Disk + Memory)

**Cách hoạt động:**
- Memory cache cho hot data (LRU)
- Disk cache cho persistent storage
- Khi miss memory → check disk → load vào memory

**Ưu điểm:**
- ✅ Nhanh cho hot data (memory)
- ✅ Persistent (disk)
- ✅ Best of both worlds

**Nhược điểm:**
- ❌ Phức tạp hơn
- ❌ Cần quản lý 2 layers

### Recommendation

**Cho development/small scale:** Disk cache (Option 1)
- Đơn giản, không cần setup
- Đủ nhanh cho use case

**Cho production/large scale:** Redis cache (Option 2)
- Nhanh hơn, scalable
- Có thể share giữa services

---

## 2. ⚡ Indexing Chậm - Batch Embedding

### Vấn Đề Hiện Tại
- Embed từng document một (sequential)
- Mỗi document = 1 API call đến Ollama
- Rất chậm: ~200ms/document → 1000 documents = 200 giây

### Giải Pháp Đề Xuất

#### Strategy 1: Batch API Calls

**Cách hoạt động:**
- Ollama API hỗ trợ batch embedding
- Gửi nhiều texts trong 1 request
- Nhận về nhiều vectors cùng lúc

**Implementation:**
1. Chia documents thành batches (batch_size=32)
2. Gọi `embed_documents()` thay vì loop `embed_query()`
3. Process batches song song (nếu có)

**Batch Size Tuning:**
- Start với 32 (safe)
- Test với 64, 128 (nếu Ollama handle được)
- Monitor memory usage
- Balance giữa speed và memory

**Code Flow:**
```
Before:
for doc in documents:
    vector = embed_query(doc.text)  # 1000 calls

After:
batches = chunk(documents, batch_size=32)  # 32 batches
for batch in batches:
    vectors = embed_documents(batch)  # 32 calls
```

**Expected Improvement:**
- 32x faster (nếu batch_size=32)
- Giảm network overhead
- Giảm Ollama server load

#### Strategy 2: Parallel Processing

**Cách hoạt động:**
- Process nhiều batches song song
- Dùng ThreadPoolExecutor hoặc asyncio

**Implementation:**
1. Chia documents thành batches
2. Tạo worker pool (4-8 workers)
3. Mỗi worker process 1 batch
4. Collect results

**Concurrency Level:**
- Start với 4 workers
- Tăng dần nếu Ollama handle được
- Monitor Ollama server load

**Code Flow:**
```
batches = chunk(documents, batch_size=32)
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(embed_batch, batch) for batch in batches]
    results = [f.result() for f in futures]
```

**Expected Improvement:**
- 4-8x faster (với 4-8 workers)
- Tận dụng được multi-core CPU

#### Strategy 3: Async/Await

**Cách hoạt động:**
- Dùng async/await cho non-blocking I/O
- Process nhiều requests đồng thời

**Implementation:**
1. Convert embedding calls thành async
2. Dùng `asyncio.gather()` để chạy parallel
3. Batch requests để tránh overwhelm server

**Code Flow:**
```
async def embed_batch_async(texts):
    return await ollama_client.embed_batch(texts)

batches = chunk(documents, batch_size=32)
results = await asyncio.gather(*[
    embed_batch_async(batch) for batch in batches
])
```

**Expected Improvement:**
- 10-20x faster (tùy vào Ollama capacity)
- Efficient I/O handling

### Recommendation

**Phase 1:** Batch API calls (Strategy 1)
- Dễ implement
- 20-30x improvement
- Low risk

**Phase 2:** Add parallel processing (Strategy 2)
- 4-8x additional improvement
- Monitor Ollama server

**Phase 3:** Async/await (Strategy 3)
- Maximum performance
- Cần refactor code

---

## 3. 🔍 Query Preprocessing

### Vấn Đề Hiện Tại
- Query được embed trực tiếp không xử lý
- Không normalize text
- Không expand synonyms
- Không handle typos
- Không extract intent

### Giải Pháp Đề Xuất

#### Step 1: Text Normalization

**Các bước:**
1. **Lowercase conversion**
   - "Khách Sạn" → "khách sạn"
   - Giữ nguyên proper nouns nếu cần

2. **Remove extra whitespace**
   - "khách  sạn  5 sao" → "khách sạn 5 sao"

3. **Remove special characters** (optional)
   - "khách sạn 5 sao!!!" → "khách sạn 5 sao"

4. **Unicode normalization**
   - "khách sạn" (NFC) → "khách sạn" (NFD) nếu cần

**Implementation:**
- Dùng `str.lower()`, `re.sub()` cho whitespace
- Dùng `unicodedata.normalize()` cho unicode

#### Step 2: Stopword Removal

**Cách hoạt động:**
- Loại bỏ các từ không có ý nghĩa (stopwords)
- Giữ lại keywords quan trọng

**Vietnamese Stopwords:**
- "là", "của", "và", "có", "tại", "ở", "với", "cho", "về"
- "nào", "gì", "đâu", "sao" (nhưng giữ nếu là question words)

**Implementation:**
- Tạo list stopwords
- Filter words không trong stopwords
- Cẩn thận với question words

#### Step 3: Synonym Expansion

**Cách hoạt động:**
- Thay thế từ viết tắt/thông dụng bằng từ đầy đủ
- Expand synonyms để tăng recall

**Synonym Dictionary:**
```python
{
    "ks": "khách sạn",
    "resort": "khách sạn resort",
    "5 sao": "năm sao",
    "4 sao": "bốn sao",
    "gần biển": ["ven biển", "sát biển", "view biển"],
    "hồ bơi": ["bể bơi", "pool"],
    "spa": ["massage", "thư giãn"]
}
```

**Implementation:**
- Tạo synonym mapping
- Replace từng từ trong query
- Có thể expand (thêm synonyms) hoặc replace (thay thế)

**Strategy:**
- **Replace:** "ks" → "khách sạn" (1 từ)
- **Expand:** "gần biển" → "gần biển ven biển sát biển" (nhiều từ)

#### Step 4: Spell Checking (Optional)

**Cách hoạt động:**
- Sửa lỗi chính tả trong query
- Dùng library như `pyspellchecker` hoặc custom dictionary

**Implementation:**
- Tạo dictionary từ hotel names, locations
- Check từng từ trong query
- Suggest corrections nếu confidence > threshold

**Example:**
- "khach san" → "khách sạn"
- "da nang" → "đà nẵng"

#### Step 5: Intent Extraction

**Cách hoạt động:**
- Phân loại intent của query
- Adjust retrieval strategy dựa trên intent

**Intent Types:**
- **Search:** "tìm khách sạn", "khách sạn nào"
- **Compare:** "so sánh", "khác nhau"
- **Detail:** "thông tin", "chi tiết"
- **Price:** "giá", "rẻ", "đắt"
- **Location:** "gần", "ở", "tại"

**Implementation:**
- Rule-based: Check keywords
- ML-based: Dùng classifier (nếu có)

**Usage:**
- Search intent → semantic search
- Compare intent → retrieve multiple hotels
- Detail intent → retrieve specific hotel

### Implementation Flow

```
Original Query: "Tìm ks 5 sao gần biển ở ĐN"

Step 1: Normalize
→ "tìm ks 5 sao gần biển ở đn"

Step 2: Remove Stopwords
→ "ks 5 sao gần biển đn"

Step 3: Expand Synonyms
→ "khách sạn năm sao gần biển ven biển sát biển đà nẵng"

Step 4: Spell Check (if needed)
→ "khách sạn năm sao gần biển ven biển sát biển đà nẵng"

Step 5: Extract Intent
→ Intent: SEARCH
→ Keywords: ["khách sạn", "năm sao", "gần biển", "đà nẵng"]
```

### Recommendation

**Phase 1:** Normalization + Synonym Expansion
- Dễ implement
- High impact
- Low risk

**Phase 2:** Stopword Removal + Intent Extraction
- Medium complexity
- Medium impact

**Phase 3:** Spell Checking
- Complex
- Lower priority

---

## 4. 💾 Response Caching

### Vấn Đề Hiện Tại
- Mỗi query đều phải:
  1. Embed query
  2. Vector search
  3. LLM generation
- Tốn resources cho repeated/similar queries
- Latency cao

### Giải Pháp Đề Xuất

#### Strategy 1: Exact Match Cache

**Cách hoạt động:**
- Cache responses cho exact queries
- Key = hash(query), Value = response

**Implementation:**
1. Check cache trước khi process
2. If hit → return cached response
3. If miss → process và cache result

**Cache Key:**
- MD5/SHA256 hash của normalized query
- Hoặc query string sau preprocessing

**Cache Value:**
```json
{
    "question": "original query",
    "answer": "generated answer",
    "sources": [...],
    "timestamp": "2024-01-01T00:00:00",
    "ttl": 3600
}
```

**TTL Strategy:**
- Default: 1 hour (3600 seconds)
- Configurable per query type
- Longer TTL cho stable data (hotel info)
- Shorter TTL cho dynamic data (prices)

#### Strategy 2: Similarity-Based Cache

**Cách hoạt động:**
- Cache cho similar queries (không chỉ exact)
- Dùng embedding similarity để tìm cached responses

**Implementation:**
1. Embed query
2. Search trong cache embeddings (vector search)
3. If similarity > threshold (0.95) → return cached
4. Else → process và cache

**Cache Structure:**
```
cache_vectors: {
    "query_embedding": [0.123, ...],
    "response": {...}
}
```

**Similarity Threshold:**
- 0.95: Very similar (almost same)
- 0.90: Similar (minor differences)
- 0.85: Somewhat similar (may not be accurate)

**Trade-off:**
- Higher threshold → more cache misses
- Lower threshold → may return wrong answers

#### Strategy 3: Semantic Cache (Advanced)

**Cách hoạt động:**
- Cache dựa trên semantic meaning
- Group similar queries → same answer

**Implementation:**
1. Extract semantic key từ query (intent + entities)
2. Check cache với semantic key
3. If match → return cached

**Semantic Key:**
```
Query: "Khách sạn 5 sao gần biển"
Semantic Key: {
    "intent": "search",
    "entities": {
        "hotel_rank": 5,
        "location": "gần biển"
    }
}
```

**Example:**
- "Tìm khách sạn 5 sao gần biển" → same key
- "Khách sạn nào 5 sao ven biển" → same key
- → Same cached answer

### Cache Storage Options

#### Option 1: In-Memory Cache (Simple)

**Implementation:**
- Python dict với TTL
- Dùng `cachetools` library (TTLCache)

**Pros:**
- ✅ Rất nhanh
- ✅ Dễ implement
- ✅ Không cần external service

**Cons:**
- ❌ Mất khi restart
- ❌ Không share giữa instances
- ❌ Memory limit

**Use Case:** Development, single instance

#### Option 2: Redis Cache (Production)

**Implementation:**
- Lưu trong Redis với TTL
- Key = hash(query), Value = JSON response

**Pros:**
- ✅ Persistent (nếu Redis persistent)
- ✅ Share giữa instances
- ✅ Auto TTL
- ✅ Có thể monitor

**Cons:**
- ❌ Cần Redis server
- ❌ Network latency (nhưng rất nhỏ)

**Use Case:** Production, multiple instances

#### Option 3: Disk Cache (Hybrid)

**Implementation:**
- Lưu responses vào files
- Similar to embedding cache

**Pros:**
- ✅ Persistent
- ✅ Không cần external service
- ✅ Có thể backup

**Cons:**
- ❌ Chậm hơn Redis
- ❌ Tốn disk space

**Use Case:** Small scale, single instance

### Cache Invalidation Strategy

**When to invalidate:**
1. **Time-based:** TTL expires
2. **Data-based:** Hotel data updated → invalidate related caches
3. **Manual:** Admin clear cache

**Invalidation Patterns:**
- **Full clear:** Clear all caches
- **Pattern-based:** Clear caches matching pattern (e.g., "hotel:*")
- **Semantic-based:** Clear caches for specific hotel/location

**Implementation:**
- Store cache metadata (hotel_ids, locations)
- When data updates → find and invalidate related caches

### Cache Key Design

**Option 1: Simple Hash**
```
Key: response:{md5(query)}
```

**Option 2: With Metadata**
```
Key: response:{md5(query)}:{model}:{collection}
```

**Option 3: Hierarchical**
```
Key: response:{intent}:{entities_hash}
```

### Recommendation

**Phase 1:** Exact Match Cache với In-Memory
- Dễ implement
- High impact cho repeated queries
- Low risk

**Phase 2:** Move to Redis
- Persistent
- Shareable
- Production-ready

**Phase 3:** Similarity-Based Cache
- Handle similar queries
- Higher complexity
- Need tuning

---

## 📊 Tổng Hợp Implementation Priority

### Priority 1 (Quick Wins - 1 ngày)
1. ✅ Batch Embedding (2-3 giờ)
   - Impact: 20-30x faster indexing
   - Risk: Low

2. ✅ Exact Match Response Cache (2 giờ)
   - Impact: 10-15x faster cho repeated queries
   - Risk: Low

3. ✅ Query Preprocessing - Basic (2 giờ)
   - Impact: 10-15% accuracy improvement
   - Risk: Low

### Priority 2 (Medium Term - 1 tuần)
4. ✅ Persistent Embedding Cache (1 ngày)
   - Impact: Faster cold starts
   - Risk: Low

5. ✅ Similarity-Based Response Cache (2 ngày)
   - Impact: Handle similar queries
   - Risk: Medium

6. ✅ Advanced Query Preprocessing (1 ngày)
   - Impact: Better retrieval
   - Risk: Low

### Priority 3 (Long Term - 2-4 tuần)
7. ✅ Semantic Cache (1 tuần)
   - Impact: Smart caching
   - Risk: High

8. ✅ Parallel/Async Indexing (1 tuần)
   - Impact: Maximum performance
   - Risk: Medium

---

## 🎯 Expected Overall Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Indexing (1000 docs) | 200s | 10s | 20x |
| Query (cached) | 2-3s | 0.1s | 20-30x |
| Query (uncached) | 2-3s | 1.5-2s | 25-33% |
| Accuracy | Baseline | +10-15% | - |
| Cache hit rate | 0% | 30-50% | - |

## 📝 Notes

- Tất cả optimizations nên có feature flags
- Measure before/after metrics
- Gradual rollout
- Monitor for regressions
- Test với real data

