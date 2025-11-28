# Setup Guide - Unified System

## 🎯 Kiến trúc hệ thống

Hệ thống được chia làm **2 phần độc lập**:

### 1. **RAG System** (Chatbot)
- **Folder**: `rag/`
- **Collection**: `hotels_rag`, `coupons_rag`
- **Embedding model**: `bge-m3` (1024 dims)
- **Mục đích**: Chatbot trả lời câu hỏi về khách sạn

### 2. **Recommendation System** (Gợi ý)
- **Folder**: `recommendation/`
- **Collection**: `hotels_recommendation`
- **Embedding model**: `paraphrase-multilingual-MiniLM-L12-v2` (384 dims)
- **Mục đích**: Gợi ý khách sạn tương tự

---

## 🚀 Quick Start - Chỉ 1 Lệnh!

### Chạy toàn bộ hệ thống:

```bash
# Linux/Mac
./run_app.sh

# Windows
run_app.bat
```

**Script tự động làm:**
1. ✅ Start Docker (Qdrant, MySQL, Redis)
2. ✅ Tạo virtual environment
3. ✅ Install dependencies
4. ✅ Tạo collections (RAG + Recommendation)
5. ✅ Khởi động app

### (Tùy chọn) Auto-index data

Nếu muốn tự động index data khi start:

```bash
# Linux/Mac
export AUTO_INDEX_DATA=true
./run_app.sh

# Windows
set AUTO_INDEX_DATA=true
run_app.bat
```

### Hoặc index thủ công sau:

#### A. RAG Data (Chatbot)

```bash
cd rag/
python simple_rag_system.py
```

#### B. Recommendation Data (Gợi ý)

```bash
cd recommendation/
python semantic_recommendation_system.py
```

---

## 📊 Kiểm tra Collections

```bash
python scripts/verify_collections.py
```

Output mong đợi:

```
Collection               | System          | Points
-------------------------|-----------------|--------
hotels_rag               | RAG            | 22
coupons_rag              | RAG            | 4
hotels_recommendation    | Recommendation | 22
```

---

## 🔧 Cấu trúc Project

```
Recommendation/
├── app.py                      # Main unified app
├── run_app.sh                  # Start script
├── docker-compose.yml          # Docker services
│
├── rag/                        # RAG system (độc lập)
│   ├── simple_rag_system.py   # Index RAG data
│   ├── data/                  # Data processors
│   └── core/                  # RAG core logic
│
├── recommendation/             # Recommendation system (độc lập)
│   ├── semantic_recommendation_system.py  # Index recommendation data
│   ├── collabritive_filtering.py         # Collaborative filtering
│   └── api_service.py                     # Recommendation API
│
└── src/                        # Shared unified code
    ├── core/                  # Core services
    ├── data/                  # Data connectors
    ├── config/                # Configuration
    └── shared/                # Shared utilities
```

---

## 📝 API Endpoints

### RAG (Chatbot)
- `POST /api/chat` - Chat với chatbot
- `GET /api/rag/stats` - Stats của RAG system

### Recommendation (Gợi ý)
- `GET /api/recommend/hotel/<hotel_id>` - Gợi ý tương tự
- `GET /api/recommend/user/<user_id>` - Gợi ý cho user

### Health
- `GET /health` - Health check
- `GET /api/status` - Detailed status

---

## ⚙️ Configuration

### Environment Variables

```bash
# Qdrant
QDRANT_URL=http://localhost:6333

# Ollama (Local)
OLLAMA_URL=http://localhost:11434

# Models
EMBEDDING_MODEL=bge-m3          # For RAG
LLM_MODEL=qwen3                 # For generation

# Database
MYSQL_HOST=localhost
MYSQL_PORT=3308
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=myhotel
```

---

## 🐛 Troubleshooting

### Collections trống

```bash
# RAG
cd rag/ && python simple_rag_system.py

# Recommendation
cd recommendation/ && python semantic_recommendation_system.py
```

### Ollama không connect

```bash
# Check Ollama
ollama list

# Pull models nếu chưa có
ollama pull bge-m3
ollama pull qwen3
```

### Port conflicts

```bash
# Check ports
netstat -ano | findstr "6333"  # Qdrant
netstat -ano | findstr "11434" # Ollama
netstat -ano | findstr "5000"  # App
```

---

## 📚 Documentation

- **RAG**: `rag/README.md`
- **Recommendation**: `recommendation/README_QUICK_START.md`
- **API**: `COMPLETE_RECOMMENDATION_SYSTEMS.md`

