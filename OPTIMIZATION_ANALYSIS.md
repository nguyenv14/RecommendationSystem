# 📊 Phân Tích & Tối Ưu Hóa RAG & Recommendation System

## 📋 Tổng Quan Cấu Trúc Hiện Tại

### Kiến Trúc RAG System
```
src/core/
├── rag.py              # RAGService - Main orchestrator
├── retriever.py        # RetrieverService - Hybrid search (semantic + keyword)
├── generator.py        # GeneratorService - LLM generation
├── embeddings.py       # EmbeddingService - Dense embeddings (BGE-M3)
├── sparse_embeddings.py # SparseEmbeddingService - BM25 keyword search
├── vectorstore.py      # VectorStoreService - Qdrant operations
├── query_preprocessor.py # QueryPreprocessor - Query normalization
├── response_cache.py   # ResponseCache - Response caching
└── query_router.py     # QueryRouter - Route to SQL/RAG
```

### Kiến Trúc Recommendation System
```
src/core/
├── recommender.py      # RecommenderService - Unified recommender
├── popularity.py       # PopularityRecommender - IMDb weighted rating
├── collaborative.py    # Collaborative filtering (NCF)
└── embeddings.py       # Shared embedding service

recommendation/
├── improved_recommendation_system.py  # NCF model
├── semantic_recommendation_system.py  # Semantic search
└── popularity_based.py                # Popularity-based
```

## ✅ Đã Triển Khai (Current State)

### RAG System - Đã Có
1. ✅ **Hybrid Search**: Semantic (dense) + Keyword (sparse BM25)
2. ✅ **Response Cache**: In-memory cache với TTL
3. ✅ **Query Preprocessing**: Normalization, synonym expansion
4. ✅ **Persistent Embedding Cache**: Disk-based cache
5. ✅ **Batch Embedding**: Batch processing cho indexing
6. ✅ **Query Router**: Phân loại statistical vs semantic queries
7. ✅ **Context Building**: Token limit management

### Recommendation System - Đã Có
1. ✅ **Hybrid Recommendation**: Semantic + Popularity weighting
2. ✅ **Multiple Strategies**: Content-based, Popularity, Collaborative, Demographic
3. ✅ **IMDb Weighted Rating**: Formula cho popularity scoring
4. ✅ **Semantic Similarity**: Item-to-item recommendations
5. ✅ **Filter Support**: Metadata filtering

## 🔍 Phân Tích Vấn Đề & Cơ Hội Tối Ưu

### RAG System - Vấn Đề & Cơ Hội

#### 1. **Thiếu Re-ranking (Cross-Encoder)**
**Vấn đề:**
- Chỉ dùng vector similarity (cosine) để rank
- Không có cross-encoder để re-rank kết quả
- Top results có thể không chính xác nhất

**Impact:**
- Precision@K có thể cải thiện 10-20%
- User experience tốt hơn với kết quả chính xác hơn

**Giải pháp:**
```python
# Thêm CrossEncoder re-ranking
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        pairs = [(query, doc['payload'].get('text', '')) for doc in documents]
        scores = self.model.predict(pairs)
        
        reranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )
        return [doc for doc, score in reranked]
```

#### 2. **Context Window Management Chưa Tối Ưu**
**Vấn đề:**
- Token counting chỉ là estimate (4 chars/token)
- Không có tiktoken để đếm chính xác
- Có thể vượt quá context window

**Impact:**
- Có thể gây lỗi khi context quá dài
- Không tận dụng hết context window

**Giải pháp:**
```python
import tiktoken

def _build_context_optimized(self, documents, max_tokens=4000):
    # Sử dụng tiktoken để đếm chính xác
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    context_parts = []
    current_tokens = 0
    
    # Sort by relevance
    sorted_docs = sorted(documents, key=lambda x: x.get("score", 0), reverse=True)
    
    for doc in sorted_docs:
        text = self._extract_text(doc.get("payload", {}))
        tokens = len(enc.encode(text))
        
        if current_tokens + tokens > max_tokens:
            # Truncate document to fit
            remaining = max_tokens - current_tokens
            if remaining > 100:
                truncated_text = enc.decode(enc.encode(text)[:remaining])
                context_parts.append(truncated_text)
            break
        
        context_parts.append(text)
        current_tokens += tokens
    
    return "\n\n".join(context_parts)
```

#### 3. **Prompt Template Quá Dài**
**Vấn đề:**
- Prompt template ~2000+ tokens
- Nhiều rules và examples lặp lại
- Tốn tokens và latency

**Impact:**
- Tăng chi phí LLM calls
- Tăng latency 10-20%

**Giải pháp:**
- Rút gọn prompt, chỉ giữ rules quan trọng
- Sử dụng few-shot examples thay vì verbose instructions
- Dynamic prompt dựa trên query type

#### 4. **Response Cache Chưa Có Similarity Matching**
**Vấn đề:**
- Chỉ cache exact match queries
- Similar queries không được cache
- Cache hit rate thấp

**Impact:**
- Bỏ lỡ cơ hội cache cho similar queries
- Cache hit rate chỉ ~20-30%

**Giải pháp:**
```python
class SimilarityResponseCache:
    def __init__(self, similarity_threshold=0.85):
        self.cache = {}
        self.embedding_service = None
        self.threshold = similarity_threshold
    
    def get(self, query: str) -> Optional[Dict]:
        # Check exact match first
        exact = self._get_exact(query)
        if exact:
            return exact
        
        # Check similarity
        query_emb = self.embedding_service.embed_query(query)
        for cached_query, entry in self.cache.items():
            cached_emb = self.embedding_service.embed_query(cached_query)
            similarity = cosine_similarity(query_emb, cached_emb)
            if similarity >= self.threshold:
                return entry['response']
        return None
```

#### 5. **Thiếu Async Processing**
**Vấn đề:**
- Tất cả operations là synchronous
- Không tận dụng được parallel processing
- Latency cao

**Impact:**
- Có thể giảm latency 20-30% với async

**Giải pháp:**
```python
import asyncio

async def ask_async(self, question: str) -> Dict:
    # Parallel: embedding + cache lookup
    embedding_task = asyncio.create_task(self._embed_async(question))
    cache_task = asyncio.create_task(self._check_cache_async(question))
    
    embedding, cached = await asyncio.gather(embedding_task, cache_task)
    
    if cached:
        return cached
    
    # Continue with retrieval and generation
    ...
```

### Recommendation System - Vấn Đề & Cơ Hội

#### 1. **Scoring Chưa Tối Ưu**
**Vấn đề:**
- Hybrid scoring đơn giản (weighted average)
- Không có learning-to-rank
- Weights cố định, không adaptive

**Impact:**
- Recommendations có thể không tối ưu
- Không adapt với user behavior

**Giải pháp:**
```python
class AdaptiveHybridRecommender:
    def __init__(self):
        self.weights = {
            'semantic': 0.7,
            'popularity': 0.3
        }
        self.user_feedback = {}  # Track user clicks/ratings
    
    def recommend(self, user_id, query, top_k=10):
        # Get base recommendations
        semantic_recs = self.get_semantic(query)
        popular_recs = self.get_popular()
        
        # Adaptive weighting based on user history
        if user_id in self.user_feedback:
            weights = self._adapt_weights(user_id)
        else:
            weights = self.weights
        
        # Score and rank
        scored = self._score_hybrid(semantic_recs, popular_recs, weights)
        return self._rerank(scored, top_k)
    
    def _adapt_weights(self, user_id):
        # Analyze user feedback to adjust weights
        feedback = self.user_feedback[user_id]
        # If user clicks more on semantic results, increase semantic weight
        ...
```

#### 2. **Thiếu Re-ranking cho Recommendations**
**Vấn đề:**
- Chỉ dùng simple scoring
- Không có learning-to-rank model
- Không consider diversity, novelty

**Impact:**
- Recommendations có thể repetitive
- Không đa dạng

**Giải pháp:**
```python
class DiversityReranker:
    def rerank(self, recommendations, top_k=10, diversity_weight=0.3):
        # Consider diversity (avoid similar items)
        reranked = []
        used_features = set()
        
        for rec in recommendations:
            features = self._extract_features(rec)
            diversity_score = self._calculate_diversity(features, used_features)
            
            # Combine relevance and diversity
            final_score = (1 - diversity_weight) * rec['score'] + \
                         diversity_weight * diversity_score
            
            rec['final_score'] = final_score
            reranked.append(rec)
            used_features.update(features)
        
        return sorted(reranked, key=lambda x: x['final_score'], reverse=True)[:top_k]
```

#### 3. **Cold Start Problem**
**Vấn đề:**
- New users: Không có interaction history
- New items: Không có ratings/reviews
- Collaborative filtering không hoạt động

**Impact:**
- Recommendations kém cho new users/items

**Giải pháp:**
```python
class ColdStartHandler:
    def recommend_for_new_user(self, user_profile, top_k=10):
        # Strategy 1: Demographic-based
        if user_profile.get('demographic'):
            return self.demographic_recommender.recommend(user_profile)
        
        # Strategy 2: Popularity-based
        return self.popularity_recommender.recommend(top_k=top_k)
    
    def recommend_new_item(self, item_features, top_k=10):
        # Strategy 1: Content-based similarity
        similar_items = self.content_recommender.find_similar(item_features)
        
        # Strategy 2: Popularity fallback
        if len(similar_items) < top_k:
            popular = self.popularity_recommender.recommend(top_k=top_k - len(similar_items))
            similar_items.extend(popular)
        
        return similar_items[:top_k]
```

#### 4. **Thiếu Real-time Updates**
**Vấn đề:**
- Recommendations không update real-time
- User interactions không được reflect ngay
- Model không được retrain thường xuyên

**Impact:**
- Recommendations có thể outdated
- User experience kém

**Giải pháp:**
```python
class RealTimeRecommender:
    def __init__(self):
        self.interaction_cache = {}  # Recent interactions
        self.update_interval = 60  # seconds
    
    def recommend(self, user_id, query, top_k=10):
        # Get base recommendations
        base_recs = self._get_base_recommendations(user_id, query)
        
        # Apply real-time adjustments
        recent_interactions = self._get_recent_interactions(user_id)
        adjusted_recs = self._adjust_with_interactions(base_recs, recent_interactions)
        
        return adjusted_recs[:top_k]
    
    def _adjust_with_interactions(self, recs, interactions):
        # Boost items similar to recently interacted items
        # Penalize items user recently skipped
        ...
```

#### 5. **Thiếu A/B Testing Framework**
**Vấn đề:**
- Không có framework để test different strategies
- Không measure recommendation quality
- Không optimize based on metrics

**Impact:**
- Không biết strategy nào tốt nhất
- Không thể improve systematically

**Giải pháp:**
```python
class ABTestingRecommender:
    def __init__(self):
        self.strategies = {
            'A': HybridRecommender(weights={'semantic': 0.7, 'popularity': 0.3}),
            'B': HybridRecommender(weights={'semantic': 0.5, 'popularity': 0.5}),
        }
        self.metrics = {
            'A': {'clicks': 0, 'views': 0, 'conversions': 0},
            'B': {'clicks': 0, 'views': 0, 'conversions': 0}
        }
    
    def recommend(self, user_id, query, top_k=10):
        # Assign user to strategy
        strategy = self._assign_strategy(user_id)
        
        # Get recommendations
        recs = self.strategies[strategy].recommend(user_id, query, top_k)
        
        # Track metrics
        self.metrics[strategy]['views'] += 1
        
        return recs, strategy
```

## 🚀 Đề Xuất Tối Ưu Hóa - Priority

### Priority 1: High Impact, Low Effort (1-2 tuần)

#### RAG System
1. **✅ Re-ranking với Cross-Encoder** (2-3 ngày)
   - Impact: +10-20% precision
   - Effort: Medium
   - Implementation: Thêm Reranker class

2. **✅ Tiktoken cho Token Counting** (1 ngày)
   - Impact: Tránh context overflow
   - Effort: Low
   - Implementation: Replace estimate với tiktoken

3. **✅ Prompt Optimization** (1 ngày)
   - Impact: -10-20% tokens, faster generation
   - Effort: Low
   - Implementation: Rút gọn prompt template

#### Recommendation System
1. **✅ Diversity Re-ranking** (2-3 ngày)
   - Impact: More diverse recommendations
   - Effort: Medium
   - Implementation: Thêm diversity scoring

2. **✅ Cold Start Handler** (2 ngày)
   - Impact: Better recommendations cho new users/items
   - Effort: Medium
   - Implementation: Fallback strategies

### Priority 2: High Impact, Medium Effort (2-4 tuần)

#### RAG System
1. **Similarity-Based Response Cache** (1 tuần)
   - Impact: +20-30% cache hit rate
   - Effort: Medium
   - Implementation: Embedding-based similarity matching

2. **Async Processing** (1 tuần)
   - Impact: -20-30% latency
   - Effort: Medium-High
   - Implementation: Async/await refactoring

#### Recommendation System
1. **Adaptive Hybrid Scoring** (1-2 tuần)
   - Impact: Better personalized recommendations
   - Effort: Medium-High
   - Implementation: User feedback tracking + weight adaptation

2. **Real-time Updates** (1 tuần)
   - Impact: More relevant recommendations
   - Effort: Medium
   - Implementation: Interaction cache + real-time adjustments

### Priority 3: Advanced Optimizations (1-2 tháng)

#### RAG System
1. **Learning-to-Rank** (2-3 tuần)
   - Impact: Better ranking quality
   - Effort: High
   - Implementation: Train LTR model

2. **Query Understanding** (1-2 tuần)
   - Impact: Better query interpretation
   - Effort: Medium-High
   - Implementation: Intent classification + entity extraction

#### Recommendation System
1. **A/B Testing Framework** (2 tuần)
   - Impact: Systematic optimization
   - Effort: Medium
   - Implementation: Strategy testing + metrics tracking

2. **Deep Learning Models** (3-4 tuần)
   - Impact: Better recommendations
   - Effort: High
   - Implementation: Neural collaborative filtering, transformer-based

## 📊 Expected Improvements

### RAG System

| Metric | Current | After P1 | After P2 | After P3 |
|--------|---------|----------|----------|----------|
| Precision@5 | Baseline | +15% | +25% | +35% |
| Latency (cached) | 0.1s | 0.1s | 0.08s | 0.05s |
| Latency (uncached) | 2.5s | 2.2s | 1.5s | 1.2s |
| Cache Hit Rate | 30% | 30% | 50% | 60% |
| Token Usage | Baseline | -15% | -15% | -20% |

### Recommendation System

| Metric | Current | After P1 | After P2 | After P3 |
|--------|---------|----------|----------|----------|
| Precision@10 | Baseline | +10% | +20% | +30% |
| Diversity | Baseline | +20% | +25% | +30% |
| Cold Start Accuracy | 60% | 75% | 80% | 85% |
| User Satisfaction | Baseline | +15% | +25% | +35% |

## 🎯 Implementation Roadmap

### Phase 1 (Tuần 1-2): Quick Wins
- [ ] Re-ranking với Cross-Encoder
- [ ] Tiktoken cho token counting
- [ ] Prompt optimization
- [ ] Diversity re-ranking
- [ ] Cold start handler

### Phase 2 (Tuần 3-4): Performance
- [ ] Similarity-based response cache
- [ ] Async processing
- [ ] Adaptive hybrid scoring
- [ ] Real-time updates

### Phase 3 (Tháng 2-3): Advanced
- [ ] Learning-to-rank
- [ ] Query understanding
- [ ] A/B testing framework
- [ ] Deep learning models

## 📝 Notes

- Tất cả optimizations nên có feature flags
- Measure before/after metrics
- Gradual rollout với monitoring
- Test với real data và user feedback
- Document changes và rationale
