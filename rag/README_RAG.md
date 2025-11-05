# Simple RAG System - Hướng Dẫn

## 📋 Tổng Quan

RAG system nhỏ gọn cho hotel recommendation sử dụng:
- **LangChain** - Framework RAG
- **Ollama** - Local embeddings (BGE-M3) + LLM (llama2/mistral)
- **Qdrant** - Vector database
- **Normalized Data** - Data đã chuẩn hóa với semantic_text

---

## 🚀 Quick Start

### **1. Chạy RAG System**

```bash
cd rag
python3 simple_rag_system.py
```

Hoặc test nhanh:
```bash
python3 test_rag.py
```

### **2. Sử dụng trong Code**

```python
from simple_rag_system import SimpleRAGSystem

# Initialize
rag = SimpleRAGSystem(
    ollama_url="http://localhost:11434",
    qdrant_url="http://localhost:6333",
    embedding_model="bge-m3",
    llm_model="llama2"
)

# Index hotels (chỉ cần chạy 1 lần)
rag.index_hotels(
    normalized_data_path="rag/normalized_data/normalized_hotels.csv",
    recreate_collection=False
)

# Search hotels
results = rag.search_hotels("Khách sạn 5 sao gần biển", top_k=5)

# Ask question với RAG
response = rag.ask("Khách sạn nào 5 sao gần biển Đà Nẵng?")
print(response["answer"])
```

---

## 🔧 Features

### **1. Semantic Search**

Tìm kiếm hotels bằng semantic search (không dùng LLM):

```python
results = rag.search_hotels("Khách sạn 5 sao gần biển", top_k=5)

# Returns:
# [
#   {
#     "hotel_id": 2,
#     "hotel_name": "Meliá Vinpearl Riverfront",
#     "hotel_rank": 5,
#     "similarity_score": 0.85,
#     ...
#   },
#   ...
# ]
```

### **2. RAG (Retrieval + Generation)**

Hỏi đáp với LLM:

```python
response = rag.ask("Khách sạn nào 5 sao gần biển Đà Nẵng?")

# Returns:
# {
#   "question": "...",
#   "answer": "Dựa trên thông tin, tôi tìm thấy các khách sạn 5 sao gần biển...",
#   "sources": [...]
# }
```

---

## 📊 Workflow

```
User Query
    ↓
Embed Query (BGE-M3)
    ↓
Search in Qdrant (Semantic Search)
    ↓
Retrieve Top-k Hotels
    ↓
[Optional] Generate Answer với LLM
    ↓
Response
```

---

## ✅ Checklist

- [ ] Qdrant running (docker-compose up)
- [ ] Ollama running với model bge-m3 và llama2
- [ ] Normalized data đã có (normalized_hotels.csv)
- [ ] Dependencies installed

---

**TL;DR**: `python3 simple_rag_system.py` để chạy RAG system!

