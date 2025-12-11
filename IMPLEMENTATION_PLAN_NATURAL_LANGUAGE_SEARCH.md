# Implementation Plan: Natural Language Hotel Search
## "Tìm kiếm khách sạn ở Ngũ Hành Sơn giá tốt"

---

## 📋 Tổng quan

Implement chức năng tìm kiếm khách sạn bằng ngôn ngữ tự nhiên, tích hợp với hệ thống RAG/Recommendation hiện có.

**Ví dụ query:** "Tìm kiếm khách sạn ở Ngũ Hành Sơn giá tốt"

**Kết quả mong đợi:** Danh sách khách sạn ở Ngũ Hành Sơn với giá tốt, được sắp xếp theo relevance score.

---

## 🏗️ Architecture Overview

```
┌─────────────────┐
│   Frontend      │
│   (Nuxt.js)     │
│                 │
│  Search Input   │
│  "Tìm khách sạn │
│   ở Ngũ Hành    │
│   Sơn giá tốt"  │
└────────┬────────┘
         │ HTTP POST
         │ /api/hotel/semantic-search
         ▼
┌─────────────────┐
│   Backend       │
│   (Laravel)     │
│                 │
│  ApiHotelController │
│  └─> AIService  │
└────────┬────────┘
         │ HTTP POST
         │ /api/hotels/search
         ▼
┌─────────────────┐
│  Python Flask   │
│  API Service    │
│                 │
│  Semantic       │
│  Recommendation │
│  System         │
│                 │
│  - Query        │
│    Preprocessing│
│  - Vector       │
│    Search       │
│  - Filtering    │
│  - Ranking      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Qdrant        │
│   Vector DB     │
│                 │
│  Hotel          │
│  Embeddings     │
└─────────────────┘
```

---

## 📦 Phase 1: Backend - Python Flask API Enhancement

### 1.1. Enhance Query Processing

**File:** `recommendation/api_service.py`

**Thêm endpoint mới:**

```python
@app.route('/api/hotels/semantic-search', methods=['POST'])
def semantic_search_hotels():
    """
    Semantic search với query preprocessing và filtering
    
    Request body:
    {
        "query": "Tìm kiếm khách sạn ở Ngũ Hành Sơn giá tốt",
        "top_k": 10,
        "filters": {
            "area_id": 7,  # Optional: Ngũ Hành Sơn
            "max_price": 2000000,  # Optional
            "min_rank": 3  # Optional
        }
    }
    """
    try:
        sys = initialize_system()
        data = request.json
        
        if 'query' not in data:
            return ApiResponse.error(
                message='Missing required field: "query"',
                code=400
            )
        
        query = data['query']
        top_k = data.get('top_k', 10)
        filters = data.get('filters', {})
        
        # Step 1: Query preprocessing (extract intent, entities)
        from src.core.query_preprocessor import QueryPreprocessor
        preprocessor = QueryPreprocessor()
        processed_query = preprocessor.process(query)
        
        # Step 2: Semantic search
        results = sys.search_similar_hotels(
            query=query,
            top_k=top_k * 2  # Get more results for filtering
        )
        
        # Step 3: Apply filters
        filtered_results = apply_filters(results, filters)
        
        # Step 4: Re-rank based on query intent
        ranked_results = rerank_by_intent(
            filtered_results, 
            processed_query,
            top_k=top_k
        )
        
        return ApiResponse.success(
            data={
                'query': query,
                'processed_query': processed_query,
                'results': ranked_results,
                'count': len(ranked_results)
            },
            message='Semantic search completed successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return ApiResponse.error(
            message=f'Error in semantic search: {str(e)}',
            code=500
        )
```

### 1.2. Create Query Preprocessor

**File:** `src/core/query_preprocessor.py` (nếu chưa có)

```python
import re
from typing import Dict, List, Optional

class QueryPreprocessor:
    """Preprocess user query để extract intent và entities"""
    
    # Intent patterns
    INTENT_PATTERNS = {
        "price": [
            r"giá\s+tốt", r"giá\s+rẻ", r"giá\s+hợp\s+lý",
            r"giá\s+phải\s+chăng", r"giá\s+thấp", r"giá\s+cao"
        ],
        "location": [
            r"ở\s+([A-Za-zÀ-ỹ\s]+)", r"tại\s+([A-Za-zÀ-ỹ\s]+)",
            r"khu\s+vực\s+([A-Za-zÀ-ỹ\s]+)", r"quận\s+([A-Za-zÀ-ỹ\s]+)"
        ],
        "amenities": [
            r"hồ\s+bơi", r"spa", r"gym", r"nhà\s+hàng",
            r"view\s+biển", r"view\s+sông"
        ],
        "rank": [
            r"(\d+)\s+sao", r"(\d+)\s+star"
        ]
    }
    
    # Area mapping
    AREA_MAPPING = {
        "ngũ hành sơn": 7,
        "sơn trà": 1,
        "hải châu": 2,
        # ... thêm các area khác
    }
    
    def process(self, query: str) -> Dict:
        """Process query và extract intent, entities"""
        query_lower = query.lower()
        
        # Extract intent
        intent = self._extract_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Extract area
        area_id = self._extract_area(query_lower)
        
        return {
            "original_query": query,
            "intent": intent,
            "entities": entities,
            "area_id": area_id,
            "filters": self._build_filters(intent, entities, area_id)
        }
    
    def _extract_intent(self, query: str) -> Dict:
        """Extract user intent"""
        intent = {
            "type": "search",  # default
            "price_range": None,
            "amenities": [],
            "rank": None
        }
        
        # Check price intent
        if any(re.search(pattern, query) for pattern in self.INTENT_PATTERNS["price"]):
            if "giá tốt" in query or "giá rẻ" in query or "giá hợp lý" in query:
                intent["price_range"] = "low"
            elif "giá cao" in query:
                intent["price_range"] = "high"
        
        # Check amenities
        for amenity_pattern in self.INTENT_PATTERNS["amenities"]:
            if re.search(amenity_pattern, query):
                intent["amenities"].append(amenity_pattern)
        
        # Check rank
        rank_match = re.search(r"(\d+)\s+sao", query)
        if rank_match:
            intent["rank"] = int(rank_match.group(1))
        
        return intent
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entities từ query"""
        entities = []
        
        # Extract location entities
        location_match = re.search(r"ở\s+([A-Za-zÀ-ỹ\s]+)", query)
        if location_match:
            entities.append(location_match.group(1).strip())
        
        return entities
    
    def _extract_area(self, query: str) -> Optional[int]:
        """Extract area_id từ query"""
        query_lower = query.lower()
        
        for area_name, area_id in self.AREA_MAPPING.items():
            if area_name in query_lower:
                return area_id
        
        return None
    
    def _build_filters(self, intent: Dict, entities: List, area_id: Optional[int]) -> Dict:
        """Build filter dict từ intent và entities"""
        filters = {}
        
        if area_id:
            filters["area_id"] = area_id
        
        if intent.get("price_range") == "low":
            filters["max_price"] = 2000000  # Default max price for "giá tốt"
        
        if intent.get("rank"):
            filters["min_rank"] = intent["rank"]
        
        return filters
```

### 1.3. Create Filter & Rerank Functions

**File:** `recommendation/api_service.py` (thêm functions)

```python
def apply_filters(results: List[Dict], filters: Dict) -> List[Dict]:
    """Apply filters to search results"""
    filtered = results
    
    # Filter by area_id
    if "area_id" in filters:
        filtered = [
            r for r in filtered 
            if r.get("payload", {}).get("area_id") == filters["area_id"]
        ]
    
    # Filter by max_price
    if "max_price" in filters:
        filtered = [
            r for r in filtered 
            if r.get("payload", {}).get("hotel_price_average", float('inf')) <= filters["max_price"]
        ]
    
    # Filter by min_rank
    if "min_rank" in filters:
        filtered = [
            r for r in filtered 
            if r.get("payload", {}).get("hotel_rank", 0) >= filters["min_rank"]
        ]
    
    return filtered

def rerank_by_intent(results: List[Dict], processed_query: Dict, top_k: int) -> List[Dict]:
    """Re-rank results based on query intent"""
    intent = processed_query.get("intent", {})
    
    # Boost score for price-related queries
    if intent.get("price_range") == "low":
        # Sort by price ascending, then by relevance score
        results = sorted(
            results,
            key=lambda x: (
                x.get("payload", {}).get("hotel_price_average", float('inf')),
                -x.get("score", 0)  # Higher score = better
            )
        )
    
    # Boost score for hotels with matching tags
    if "giá tốt" in processed_query.get("original_query", "").lower():
        for result in results:
            tags = result.get("payload", {}).get("hotel_tag_keyword", "").lower()
            if "giá tốt" in tags or "khách sạn giá tốt" in tags:
                result["score"] = result.get("score", 0) * 1.2  # Boost 20%
    
    # Sort by final score
    results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    
    return results[:top_k]
```

---

## 📦 Phase 2: Backend - Laravel Integration

### 2.1. Create AIService Method

**File:** `app/Services/Api/AIService.php`

```php
<?php

namespace App\Services\Api;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class AIService
{
    private string $recommendationApiUrl;

    public function __construct()
    {
        $this->recommendationApiUrl = env('RECOMMENDATION_API_URL', 'http://localhost:5000');
    }

    /**
     * Semantic search hotels by natural language query
     * 
     * @param string $query Natural language query
     * @param int $topK Number of results
     * @param array $filters Additional filters
     * @return array
     */
    public function semanticSearchHotels(string $query, int $topK = 10, array $filters = []): array
    {
        try {
            $response = Http::timeout(10)->post("{$this->recommendationApiUrl}/api/hotels/semantic-search", [
                'query' => $query,
                'top_k' => $topK,
                'filters' => $filters
            ]);

            if ($response->successful()) {
                $data = $response->json();
                
                if ($data['success'] ?? false) {
                    // Map Python API results to Laravel format
                    return $this->mapSearchResults($data['data']['results'] ?? []);
                }
            }

            Log::error('Semantic search failed', [
                'query' => $query,
                'response' => $response->body()
            ]);

            return [];
        } catch (\Exception $e) {
            Log::error('Semantic search exception', [
                'query' => $query,
                'error' => $e->getMessage()
            ]);

            return [];
        }
    }

    /**
     * Map Python API results to Laravel hotel format
     */
    private function mapSearchResults(array $results): array
    {
        $mapped = [];

        foreach ($results as $result) {
            $payload = $result['payload'] ?? [];
            
            $mapped[] = [
                'hotel_id' => $payload['hotel_id'] ?? null,
                'hotel_name' => $payload['hotel_name'] ?? '',
                'hotel_rank' => $payload['hotel_rank'] ?? null,
                'hotel_price_average' => $payload['hotel_price_average'] ?? null,
                'hotel_desc' => $payload['hotel_desc'] ?? '',
                'hotel_placedetails' => $payload['hotel_placedetails'] ?? '',
                'hotel_image' => $payload['hotel_image'] ?? '',
                'area_id' => $payload['area_id'] ?? null,
                'area_name' => $payload['area_name'] ?? '',
                'brand_id' => $payload['brand_id'] ?? null,
                'brand_name' => $payload['brand_name'] ?? '',
                'hotel_tag_keyword' => $payload['hotel_tag_keyword'] ?? '',
                'relevance_score' => $result['score'] ?? 0,
                'section_type' => $result.get('section_type', null), // From structured chunking
            ];
        }

        return $mapped;
    }
}
```

### 2.2. Create API Controller Method

**File:** `app/Http/Controllers/ApiHotelController.php`

```php
public function semanticSearch(Request $request)
{
    try {
        $query = $request->input('query', '');
        $topK = $request->input('top_k', 10);
        
        // Extract filters from query or request
        $filters = [
            'area_id' => $request->input('area_id'),
            'max_price' => $request->input('max_price'),
            'min_rank' => $request->input('min_rank'),
        ];
        
        // Remove null filters
        $filters = array_filter($filters, fn($value) => $value !== null);
        
        if (empty($query)) {
            return response()->json([
                'success' => false,
                'message' => 'Query is required',
                'data' => null
            ], 400);
        }
        
        $aiService = app(AIService::class);
        $results = $aiService->semanticSearchHotels($query, $topK, $filters);
        
        // Enrich with database data if needed
        $enrichedResults = $this->enrichHotelResults($results);
        
        return response()->json([
            'success' => true,
            'message' => 'Search completed successfully',
            'data' => [
                'query' => $query,
                'results' => $enrichedResults,
                'count' => count($enrichedResults)
            ]
        ]);
        
    } catch (\Exception $e) {
        return response()->json([
            'success' => false,
            'message' => 'Error searching hotels: ' . $e->getMessage(),
            'data' => null
        ], 500);
    }
}

private function enrichHotelResults(array $results): array
{
    // Optionally enrich with additional data from database
    // e.g., ratings, availability, etc.
    return $results;
}
```

### 2.3. Add Route

**File:** `routes/api.php`

```php
Route::post('/hotel/semantic-search', [ApiHotelController::class, 'semanticSearch']);
```

### 2.4. Add Environment Variable

**File:** `.env`

```env
RECOMMENDATION_API_URL=http://localhost:5000
```

---

## 📦 Phase 3: Frontend - Nuxt Integration

### 3.1. Update API Service

**File:** `services/apiService.ts`

```typescript
const semanticSearchHotels = async (query: string, options?: {
  top_k?: number;
  area_id?: number;
  max_price?: number;
  min_rank?: number;
}) => {
  const res = await $fetch('/api/hotel/semantic-search', {
    method: 'POST',
    body: {
      query,
      top_k: options?.top_k || 10,
      ...options
    },
  });
  return res as any;
};

return {
  // ... existing methods
  semanticSearchHotels,
};
```

### 3.2. Create Search Component

**File:** `components/Search/NaturalLanguageSearch.vue`

```vue
<template>
  <div class="natural-language-search">
    <div class="search-input-wrapper">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Ví dụ: Tìm khách sạn ở Ngũ Hành Sơn giá tốt"
        class="search-input"
        @keyup.enter="handleSearch"
      />
      <button @click="handleSearch" class="search-button">
        <i class="fa-solid fa-magnifying-glass"></i>
      </button>
    </div>
    
    <!-- Search Results -->
    <div v-if="results.length > 0" class="search-results">
      <div class="results-header">
        <h3>Tìm thấy {{ results.length }} khách sạn</h3>
        <p class="query-info">Kết quả cho: "{{ lastQuery }}"</p>
      </div>
      
      <div class="hotels-grid">
        <HotelCard
          v-for="hotel in results"
          :key="hotel.hotel_id"
          :hotel="hotel"
        />
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Đang tìm kiếm...</p>
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && results.length === 0 && hasSearched" class="empty-state">
      <p>Không tìm thấy khách sạn nào phù hợp</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useApiService } from '~/services/apiService';

const { semanticSearchHotels } = useApiService();

const searchQuery = ref('');
const results = ref([]);
const loading = ref(false);
const hasSearched = ref(false);
const lastQuery = ref('');

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return;
  
  loading.value = true;
  hasSearched.value = true;
  lastQuery.value = searchQuery.value;
  
  try {
    const response = await semanticSearchHotels(searchQuery.value, {
      top_k: 10
    });
    
    if (response.success) {
      results.value = response.data.results || [];
    } else {
      results.value = [];
    }
  } catch (error) {
    console.error('Search error:', error);
    results.value = [];
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.natural-language-search {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.search-input-wrapper {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input {
  flex: 1;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.search-button {
  padding: 1rem 2rem;
  background: #ff3366;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}

.results-header {
  margin-bottom: 2rem;
}

.query-info {
  color: #6b7280;
  font-size: 0.875rem;
}

.hotels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
</style>
```

### 3.3. Integrate into Search Page

**File:** `pages/khach-san/tim-kiem/index.vue`

Thêm tab hoặc toggle để switch giữa:
- Traditional search (filters)
- Natural language search

```vue
<template>
  <div>
    <!-- Search Mode Toggle -->
    <div class="search-mode-toggle">
      <button 
        @click="searchMode = 'filter'"
        :class="{ active: searchMode === 'filter' }"
      >
        Tìm kiếm bằng bộ lọc
      </button>
      <button 
        @click="searchMode = 'natural'"
        :class="{ active: searchMode === 'natural' }"
      >
        Tìm kiếm bằng câu hỏi
      </button>
    </div>
    
    <!-- Natural Language Search -->
    <NaturalLanguageSearch v-if="searchMode === 'natural'" />
    
    <!-- Traditional Filter Search -->
    <div v-else>
      <!-- Existing filter search UI -->
    </div>
  </div>
</template>

<script setup>
const searchMode = ref('filter');
</script>
```

---

## 🧪 Phase 4: Testing

### 4.1. Unit Tests

**File:** `tests/Unit/QueryPreprocessorTest.py`

```python
def test_extract_area():
    preprocessor = QueryPreprocessor()
    result = preprocessor.process("Tìm khách sạn ở Ngũ Hành Sơn")
    assert result["area_id"] == 7

def test_extract_price_intent():
    preprocessor = QueryPreprocessor()
    result = preprocessor.process("Khách sạn giá tốt")
    assert result["intent"]["price_range"] == "low"
```

### 4.2. Integration Tests

**File:** `tests/Integration/SemanticSearchTest.php`

```php
public function test_semantic_search_endpoint()
{
    $response = $this->postJson('/api/hotel/semantic-search', [
        'query' => 'Tìm khách sạn ở Ngũ Hành Sơn giá tốt',
        'top_k' => 10
    ]);
    
    $response->assertStatus(200)
             ->assertJsonStructure([
                 'success',
                 'data' => [
                     'query',
                     'results',
                     'count'
                 ]
             ]);
}
```

### 4.3. Manual Testing Checklist

- [ ] Query: "Tìm khách sạn ở Ngũ Hành Sơn giá tốt"
  - [ ] Returns hotels in Ngũ Hành Sơn (area_id = 7)
  - [ ] Results sorted by price (ascending)
  - [ ] Hotels with "giá tốt" tag have higher scores
  
- [ ] Query: "Khách sạn 5 sao gần biển"
  - [ ] Returns 5-star hotels
  - [ ] Hotels near beach prioritized
  
- [ ] Query: "Khách sạn có hồ bơi và spa"
  - [ ] Returns hotels with pool and spa amenities

---

## 📊 Phase 5: Performance Optimization

### 5.1. Caching

- Cache query preprocessing results
- Cache search results for common queries (TTL: 5 minutes)

### 5.2. Indexing

- Ensure Qdrant collection is properly indexed
- Use structured chunking for better retrieval

### 5.3. Response Time

- Target: < 500ms for search response
- Use async processing for heavy queries

---

## 🚀 Deployment Checklist

### Backend (Laravel)
- [ ] Add `RECOMMENDATION_API_URL` to `.env`
- [ ] Deploy updated `AIService.php`
- [ ] Deploy updated `ApiHotelController.php`
- [ ] Add route to `api.php`

### Python API
- [ ] Deploy updated `api_service.py`
- [ ] Ensure Qdrant is running
- [ ] Ensure embeddings are indexed
- [ ] Test endpoint: `POST /api/hotels/semantic-search`

### Frontend
- [ ] Deploy updated `apiService.ts`
- [ ] Deploy `NaturalLanguageSearch.vue` component
- [ ] Update search page with mode toggle

---

## 📝 API Documentation

### Endpoint: `POST /api/hotel/semantic-search`

**Request:**
```json
{
  "query": "Tìm khách sạn ở Ngũ Hành Sơn giá tốt",
  "top_k": 10,
  "area_id": 7,
  "max_price": 2000000,
  "min_rank": 3
}
```

**Response:**
```json
{
  "success": true,
  "message": "Search completed successfully",
  "data": {
    "query": "Tìm khách sạn ở Ngũ Hành Sơn giá tốt",
    "results": [
      {
        "hotel_id": 123,
        "hotel_name": "Mường Thanh Luxury Đà Nẵng",
        "hotel_rank": 5,
        "hotel_price_average": 1490564,
        "area_name": "Ngũ Hành Sơn",
        "relevance_score": 0.95,
        ...
      }
    ],
    "count": 10
  }
}
```

---

## 🎯 Success Metrics

- **Accuracy**: > 80% relevant results in top 5
- **Response Time**: < 500ms
- **User Satisfaction**: Positive feedback on search quality
- **Coverage**: Support for common query patterns

---

## 📚 Next Steps

1. Implement Phase 1 (Python API)
2. Test with sample queries
3. Implement Phase 2 (Laravel Integration)
4. Implement Phase 3 (Frontend)
5. End-to-end testing
6. Performance optimization
7. Deploy to production

---

## 🔗 Related Files

- `recommendation/api_service.py` - Python Flask API
- `app/Services/Api/AIService.php` - Laravel Service
- `app/Http/Controllers/ApiHotelController.php` - Laravel Controller
- `services/apiService.ts` - Frontend API Service
- `components/Search/NaturalLanguageSearch.vue` - Frontend Component

