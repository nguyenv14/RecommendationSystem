# Source Code Structure

Cấu trúc source code mới với clean architecture và separation of concerns.

## 📁 Cấu trúc

```
src/
├── __init__.py
├── config/                    # Configuration module
│   ├── __init__.py
│   ├── constants.py          # Constants (collections, models, ports)
│   └── settings.py           # Centralized settings management
│
├── shared/                    # Shared utilities
│   ├── __init__.py
│   ├── logger.py             # Centralized logging
│   ├── qdrant_manager.py     # Qdrant client manager
│   └── embedding_manager.py  # Embedding manager with caching
│
├── rag/                      # RAG system (Coming soon)
│   ├── __init__.py
│   ├── system.py
│   ├── chain.py
│   └── retriever.py
│
├── recommendation/           # Recommendation system (Coming soon)
│   ├── __init__.py
│   ├── semantic.py
│   ├── collaborative.py
│   └── popularity.py
│
└── api/                      # API layer (Coming soon)
    ├── __init__.py
    ├── app.py
    └── routes/
```

## 🎯 Mục đích

### 1. Clean Architecture
- **Separation of Concerns**: Tách biệt rõ ràng giữa config, shared utilities, business logic
- **Dependency Injection**: Config và dependencies có thể inject dễ dàng
- **Testability**: Dễ dàng test từng component riêng lẻ

### 2. Centralized Configuration
- **Single Source of Truth**: Tất cả config ở 1 nơi
- **Environment-based**: Config từ environment variables
- **Type-safe**: Settings được type-hint rõ ràng

### 3. Shared Utilities
- **DRY Principle**: Không duplicate code giữa RAG và Recommendation
- **Reusable**: Components có thể reuse ở nhiều nơi
- **Maintainable**: Sửa 1 lần, apply cho tất cả

## 📖 Usage

### Config

```python
from src.config import get_settings, Collections, Models

# Get settings
settings = get_settings()

# Access config
print(settings.QDRANT_URL)
print(settings.RAG_COLLECTION_HOTELS)

# Use constants
print(Collections.RAG_HOTELS)
print(Models.EMBEDDING_BGE_M3)
```

### Logging

```python
from src.shared import get_logger, setup_logging

# Setup logging (once at startup)
setup_logging(level=logging.INFO, log_file='app.log')

# Get logger for your module
logger = get_logger(__name__)
logger.info("Hello world!")
```

### Qdrant Manager

```python
from src.shared import QdrantManager
from src.config import get_settings

settings = get_settings()
qdrant = QdrantManager(url=settings.QDRANT_URL)

# Create collection
qdrant.create_collection("my_collection", vector_size=1024)

# Check if exists
if qdrant.collection_exists("my_collection"):
    print("Collection exists!")

# Get info
info = qdrant.get_collection_info("my_collection")
print(f"Points count: {info.points_count}")
```

### Embedding Manager

```python
from src.shared import EmbeddingManager
from src.config import get_settings

settings = get_settings()

# Initialize with Ollama
embedder = EmbeddingManager(
    provider="ollama",
    model_name=settings.EMBEDDING_MODEL,
    ollama_url=settings.OLLAMA_URL,
    cache_enabled=True
)

# Embed query
vector = embedder.embed_query("Khách sạn 5 sao gần biển")

# Embed documents
texts = ["Hotel 1", "Hotel 2", "Hotel 3"]
vectors = embedder.embed_documents(texts)

# Get vector size
size = embedder.get_vector_size()
print(f"Vector size: {size}")
```

## 🔧 Configuration Management

### Collections

Collections được tách biệt rõ ràng:

| Collection | Purpose | System |
|------------|---------|--------|
| `hotels_rag` | Hotels for RAG chatbot | RAG |
| `coupons_rag` | Coupons for RAG chatbot | RAG |
| `hotels_recommendation` | Hotels for semantic search | Recommendation |

Không còn xung đột giữa các collections!

### Environment Variables

Tất cả config đều có thể override bằng environment variables:

```bash
# RAG collections
export RAG_COLLECTION_HOTELS=hotels_rag
export RAG_COLLECTION_COUPONS=coupons_rag

# Recommendation collections
export REC_COLLECTION_HOTELS=hotels_recommendation

# Services
export QDRANT_URL=http://localhost:6333
export OLLAMA_URL=http://localhost:11434
```

## 🚀 Migration Guide

### From Old Code

**Before:**
```python
# Old way - hardcoded
collection_name = "hotels"
ollama_url = "http://localhost:11434"
```

**After:**
```python
# New way - centralized config
from src.config import get_settings

settings = get_settings()
collection_name = settings.RAG_COLLECTION_HOTELS
ollama_url = settings.OLLAMA_URL
```

### Backward Compatibility

Unified service vẫn hỗ trợ cả old và new config:
- Nếu có `src.config` → Dùng new config
- Nếu không → Fallback to environment variables

## 📝 Best Practices

1. **Always use get_settings()** instead of os.getenv() trực tiếp
2. **Use constants** từ `src.config.constants` thay vì hardcode strings
3. **Use shared utilities** thay vì duplicate code
4. **Log properly** với shared logger
5. **Type hints** cho tất cả functions

## 🔜 Coming Soon

- `src/rag/` - RAG system refactored
- `src/recommendation/` - Recommendation system refactored  
- `src/api/` - API layer với proper routing
- Unit tests cho tất cả modules
- Integration tests

## 📖 Documentation

- [Configuration Guide](../docs/CONFIGURATION.md)
- [Collections Management](../ANALYSIS_COLLECTIONS.md)
- [Migration Guide](../MIGRATION_GUIDE.md)

