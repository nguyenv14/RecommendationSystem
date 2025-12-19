# 🚀 Tối Ưu Hóa Nhanh - Quick Start Guide

## 📋 Tóm Tắt Các Tối Ưu Quan Trọng

### RAG System - Top 5 Optimizations

1. **Re-ranking với Cross-Encoder** ⭐⭐⭐
   - **Impact**: +15-20% precision
   - **Effort**: 2-3 ngày
   - **File**: `src/core/reranker.py` (cần tạo)

2. **Tiktoken cho Token Counting** ⭐⭐
   - **Impact**: Tránh context overflow
   - **Effort**: 1 ngày
   - **File**: `src/core/generator.py` (cập nhật)

3. **Similarity-Based Response Cache** ⭐⭐⭐
   - **Impact**: +20-30% cache hit rate
   - **Effort**: 1 tuần
   - **File**: `src/core/response_cache.py` (cập nhật)

4. **Prompt Optimization** ⭐
   - **Impact**: -15% tokens, faster
   - **Effort**: 1 ngày
   - **File**: `src/core/generator.py` (cập nhật)

5. **Async Processing** ⭐⭐
   - **Impact**: -20-30% latency
   - **Effort**: 1 tuần
   - **File**: `src/core/rag.py` (refactor)

### Recommendation System - Top 5 Optimizations

1. **Diversity Re-ranking** ⭐⭐⭐
   - **Impact**: More diverse recommendations
   - **Effort**: 2-3 ngày
   - **File**: `src/core/recommender.py` (cập nhật)

2. **Cold Start Handler** ⭐⭐
   - **Impact**: Better cho new users/items
   - **Effort**: 2 ngày
   - **File**: `src/core/recommender.py` (cập nhật)

3. **Adaptive Hybrid Scoring** ⭐⭐⭐
   - **Impact**: Personalized recommendations
   - **Effort**: 1-2 tuần
   - **File**: `src/core/recommender.py` (cập nhật)

4. **Real-time Updates** ⭐⭐
   - **Impact**: More relevant recommendations
   - **Effort**: 1 tuần
   - **File**: `src/core/recommender.py` (cập nhật)

5. **A/B Testing Framework** ⭐
   - **Impact**: Systematic optimization
   - **Effort**: 2 tuần
   - **File**: `src/core/ab_testing.py` (cần tạo)

## 🎯 Bắt Đầu Ngay - Priority 1

### 1. Re-ranking cho RAG (2-3 ngày)

**Bước 1**: Cài đặt dependencies
```bash
pip install sentence-transformers
```

**Bước 2**: Tạo file `src/core/reranker.py`
```python
from sentence_transformers import CrossEncoder
from typing import List, Dict

class Reranker:
    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        # Extract texts
        texts = [doc.get('payload', {}).get('text', '') for doc in documents]
        
        # Create query-document pairs
        pairs = [(query, text) for text in texts]
        
        # Get scores
        scores = self.model.predict(pairs)
        
        # Combine and sort
        reranked = sorted(
            zip(documents, scores),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Update scores in documents
        result = []
        for doc, score in reranked:
            doc['rerank_score'] = float(score)
            result.append(doc)
        
        return result
```

**Bước 3**: Tích hợp vào `src/core/rag.py`
```python
from .reranker import Reranker

class RAGService:
    def __init__(self, ...):
        # ... existing code ...
        self.reranker = Reranker()  # Add reranker
    
    def ask(self, question: str, ...):
        # ... existing retrieval code ...
        
        # Add re-ranking step
        if len(documents) > 0:
            documents = self.reranker.rerank(question, documents)
        
        # Continue with generation
        ...
```

### 2. Tiktoken cho Token Counting (1 ngày)

**Bước 1**: Cài đặt
```bash
pip install tiktoken
```

**Bước 2**: Cập nhật `src/core/generator.py`
```python
import tiktoken

class GeneratorService:
    def __init__(self, ...):
        # ... existing code ...
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def _build_context(self, documents, max_tokens=4000):
        # Use tiktoken for accurate counting
        context_parts = []
        current_tokens = 0
        
        sorted_docs = sorted(documents, key=lambda x: x.get("score", 0), reverse=True)
        
        for doc in sorted_docs:
            text = self._extract_text(doc.get("payload", {}))
            tokens = len(self.tokenizer.encode(text))
            
            if current_tokens + tokens > max_tokens:
                # Truncate to fit
                remaining = max_tokens - current_tokens
                if remaining > 100:
                    encoded = self.tokenizer.encode(text)[:remaining]
                    text = self.tokenizer.decode(encoded)
                    context_parts.append(text)
                break
            
            context_parts.append(text)
            current_tokens += tokens
        
        return "\n\n".join(context_parts)
```

### 3. Diversity Re-ranking cho Recommendation (2-3 ngày)

**Bước 1**: Cập nhật `src/core/recommender.py`
```python
class RecommenderService:
    def recommend_hybrid(self, ..., diversity_weight=0.3):
        # ... existing code to get recommendations ...
        
        # Add diversity re-ranking
        reranked = self._rerank_with_diversity(
            recommendations_list,
            diversity_weight=diversity_weight
        )
        
        return reranked[:top_k]
    
    def _rerank_with_diversity(self, recommendations, diversity_weight=0.3):
        """Re-rank considering diversity"""
        reranked = []
        used_features = set()
        
        for rec in recommendations:
            # Extract features (amenities, location, price range, etc.)
            features = self._extract_features(rec)
            
            # Calculate diversity score
            diversity_score = self._calculate_diversity(features, used_features)
            
            # Combine relevance and diversity
            relevance_score = rec.get('hybrid_score', rec.get('score', 0))
            final_score = (1 - diversity_weight) * relevance_score + \
                         diversity_weight * diversity_score
            
            rec['final_score'] = final_score
            reranked.append(rec)
            used_features.update(features)
        
        return sorted(reranked, key=lambda x: x['final_score'], reverse=True)
    
    def _extract_features(self, rec):
        """Extract features for diversity calculation"""
        payload = rec.get('payload', {})
        return {
            'area_id': payload.get('area_id'),
            'hotel_rank': payload.get('hotel_rank'),
            'price_range': self._get_price_range(payload.get('hotel_price_average')),
            'amenities': payload.get('amenities', [])
        }
    
    def _calculate_diversity(self, features, used_features):
        """Calculate diversity score (higher = more diverse)"""
        if not used_features:
            return 1.0
        
        # Count how many features are new
        new_features = 0
        total_features = len(features)
        
        for key, value in features.items():
            if key not in used_features or value not in used_features.get(key, set()):
                new_features += 1
        
        return new_features / total_features if total_features > 0 else 0.0
```

### 4. Cold Start Handler (2 ngày)

**Bước 1**: Cập nhật `src/core/recommender.py`
```python
class RecommenderService:
    def recommend_for_user(self, user_id, user_preferences=None, top_k=10):
        """Recommend with cold start handling"""
        # Check if user is new (no interactions)
        is_new_user = self._is_new_user(user_id)
        
        if is_new_user:
            # Cold start: use demographic or popularity
            if user_preferences:
                return self.recommend_by_demographic(user_preferences, top_k)
            else:
                return self.recommend_popular(top_k=top_k)
        else:
            # Warm user: use collaborative or hybrid
            return self.recommend_hybrid(
                item_id=None,  # Will use user history
                top_k=top_k
            )
    
    def _is_new_user(self, user_id):
        """Check if user has interactions"""
        # Check database or cache for user interactions
        # Return True if new user
        ...
```

## 📊 Metrics để Track

### RAG System
- Precision@K (K=1, 3, 5)
- Latency (p50, p95, p99)
- Cache hit rate
- Token usage per query
- Context length distribution

### Recommendation System
- Precision@K (K=5, 10, 20)
- Diversity (intra-list diversity)
- Coverage (item coverage)
- Click-through rate (CTR)
- Conversion rate

## 🔧 Testing

### Unit Tests
```python
def test_reranker():
    reranker = Reranker()
    query = "khách sạn 5 sao"
    documents = [...]
    reranked = reranker.rerank(query, documents)
    assert len(reranked) == len(documents)
    assert reranked[0]['rerank_score'] >= reranked[-1]['rerank_score']

def test_diversity_reranking():
    recommender = RecommenderService(...)
    recs = recommender.recommend_hybrid(..., diversity_weight=0.3)
    # Check diversity
    areas = [r['payload']['area_id'] for r in recs]
    assert len(set(areas)) > 1  # Should have diverse areas
```

### Integration Tests
```python
def test_rag_with_reranking():
    rag = RAGService(...)
    result = rag.ask("khách sạn nào có view biển?")
    assert 'answer' in result
    assert len(result['sources']) > 0
    # Check that sources are re-ranked
```

## 📝 Next Steps

1. **Week 1**: Implement Priority 1 optimizations
   - Re-ranking
   - Tiktoken
   - Diversity re-ranking
   - Cold start handler

2. **Week 2**: Testing & Monitoring
   - Write tests
   - Set up metrics tracking
   - A/B testing setup

3. **Week 3-4**: Priority 2 optimizations
   - Similarity-based cache
   - Async processing
   - Adaptive scoring

4. **Month 2-3**: Advanced optimizations
   - Learning-to-rank
   - Deep learning models
   - A/B testing framework

## 🎯 Success Criteria

### RAG System
- ✅ Precision@5 tăng 15%+
- ✅ Latency giảm 20%+
- ✅ Cache hit rate tăng 20%+

### Recommendation System
- ✅ Precision@10 tăng 10%+
- ✅ Diversity tăng 20%+
- ✅ Cold start accuracy tăng 15%+
