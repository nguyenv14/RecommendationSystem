# RAG Project Structure

## 📁 Cấu Trúc Folder Mới

```
rag/
├── core/                          # Core RAG components
│   ├── __init__.py
│   ├── embeddings.py              # CachedOllamaEmbeddings
│   ├── query_extractor.py         # QueryExtractor
│   ├── retriever.py               # HotelRetriever (Layer 2)
│   ├── rag_chain.py               # RAGChain (Layer 3)
│   ├── vectorstore.py             # VectorStoreHelper
│   └── README.md
│
├── data/                          # Data processing components
│   ├── __init__.py
│   ├── normalizer.py              # HotelDataNormalizer (moved from hotel_data_normalization.py)
│   ├── connector.py               # DatabaseConnector (moved from database_connector.py)
│   └── chunker.py                 # SmartChunker (moved from smart_chunker.py)
│
├── api/                           # API server
│   ├── __init__.py
│   └── chat_api.py                # Flask API (moved from rag_chat_api.py)
│
├── docs/                          # Documentation
│   ├── README.md
│   ├── RAG_ARCHITECTURE.md
│   ├── RAG_FLOW_EXPLANATION.md
│   ├── QUERY_EXTRACTION.md
│   ├── LM_STUDIO_SETUP.md
│   └── REFACTOR_GUIDE.md
│
├── scripts/                       # Utility scripts (optional)
│   └── (có thể move các shell scripts vào đây)
│
├── config/                        # Configuration files (optional)
│   └── (có thể move config files vào đây)
│
├── simple_rag_system.py           # Main orchestrator
├── requirements_rag.txt
├── docker-compose.yml
└── ...
```

## 📦 Packages

### 1. `core/` - Core RAG Components
**Purpose**: Core components cho RAG system (Layer 2 & 3)

**Components**:
- `embeddings.py`: Cached embeddings wrapper
- `query_extractor.py`: Keyword extraction
- `retriever.py`: Search & retrieval logic
- `rag_chain.py`: RAG chain for generation
- `vectorstore.py`: Qdrant helpers

**Import**:
```python
from core import CachedOllamaEmbeddings, QueryExtractor, HotelRetriever, RAGChain
```

### 2. `data/` - Data Processing
**Purpose**: Data processing components (Layer 1: Ingestion)

**Components**:
- `normalizer.py`: HotelDataNormalizer - Chuẩn hóa và semantic mapping
- `connector.py`: DatabaseConnector - Fetch data từ MySQL
- `chunker.py`: SmartChunker - Chia nhỏ documents

**Import**:
```python
from data import HotelDataNormalizer, DatabaseConnector, SmartChunker
```

### 3. `api/` - API Server
**Purpose**: Flask API server cho chat interface

**Components**:
- `chat_api.py`: Flask app với endpoints `/api/chat`, `/api/search`

**Import**:
```python
from api import app
# hoặc
from api.chat_api import app
```

## 🔄 Migration Notes

### Import Changes

**Trước:**
```python
from database_connector import DatabaseConnector
from smart_chunker import SmartChunker
from hotel_data_normalization import HotelDataNormalizer
from rag_chat_api import app
```

**Sau:**
```python
from data import DatabaseConnector, SmartChunker, HotelDataNormalizer
from api import app
```

### File Moves

1. ✅ `hotel_data_normalization.py` → `data/normalizer.py`
2. ✅ `database_connector.py` → `data/connector.py`
3. ✅ `smart_chunker.py` → `data/chunker.py`
4. ✅ `rag_chat_api.py` → `api/chat_api.py`
5. ✅ `*.md` → `docs/`

### Update Imports

**Files cần update:**
- ✅ `simple_rag_system.py` - Đã update imports
- ⚠️ `api/chat_api.py` - Cần check imports
- ⚠️ Shell scripts - Cần update paths nếu có

## 📝 Benefits

1. **Clear Separation**: Mỗi folder có chức năng rõ ràng
2. **Easy Navigation**: Dễ tìm code theo chức năng
3. **Scalable**: Dễ thêm components mới
4. **Maintainable**: Code được tổ chức tốt hơn

## 🚀 Next Steps

1. ✅ Tạo folder structure
2. ✅ Move files vào folders
3. ✅ Tạo `__init__.py` files
4. ✅ Update imports trong `simple_rag_system.py`
5. ⚠️ Update imports trong `api/chat_api.py`
6. ⚠️ Test imports và functionality
7. ⚠️ Update shell scripts paths nếu cần

