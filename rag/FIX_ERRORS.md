# 🔧 FIX ERRORS - Hướng Dẫn Sửa Lỗi

## ❌ Lỗi 1: Qdrant Constructor

**Lỗi:**
```
TypeError: __init__() got an unexpected keyword argument 'url'
```

**Đã sửa:** ✅ 
- Dùng `QdrantClient` trước, sau đó pass vào `Qdrant()`
- Sửa trong `load_vectorstore()` method

---

## ❌ Lỗi 2: Ollama Embedding API

**Lỗi:**
```
ValueError: Error raised by inference API HTTP code: 500
{"error":"do embedding request: Post \"http://127.0.0.1:53228/embedding\": EOF"}
```

**Nguyên nhân:**
- Model `bge-m3` chưa được pull trong Ollama
- Hoặc Ollama chưa đúng cấu hình
- Hoặc embedding API không hoạt động

---

## 🔧 CÁCH SỬA LỖI OLLAMA

### **Bước 1: Check Ollama Models**

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Hoặc dùng script
python3 check_ollama.py
```

### **Bước 2: Pull Required Models**

```bash
# Pull embedding model
ollama pull bge-m3

# Pull LLM model
ollama pull llama2

# Hoặc nếu không có, dùng model khác
ollama pull mistral
```

### **Bước 3: Verify Models**

```bash
# List models
ollama list

# Test embedding
curl http://localhost:11434/api/embeddings \
  -d '{"model": "bge-m3", "prompt": "test"}'
```

### **Bước 4: Test với Script**

```bash
python3 check_ollama.py
```

---

## 🔄 **ALTERNATIVE: Dùng Model Khác**

Nếu `bge-m3` không có, có thể dùng model khác:

### **Option 1: Dùng Sentence Transformers (Local)**

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

# Instead of OllamaEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
```

### **Option 2: Dùng Model Ollama Khác**

```python
# Thử model khác
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",  # Thay vì bge-m3
    base_url="http://localhost:11434"
)
```

**Pull model:**
```bash
ollama pull nomic-embed-text
```

---

## ✅ **CHECKLIST FIX**

- [ ] Ollama is running
- [ ] Model `bge-m3` pulled: `ollama pull bge-m3`
- [ ] Model `llama2` pulled: `ollama pull llama2`
- [ ] Test embedding API: `python3 check_ollama.py`
- [ ] Qdrant running: `docker-compose up -d`
- [ ] RAG system chạy thành công

---

## 🚀 **QUICK FIX**

```bash
# 1. Pull models
ollama pull bge-m3
ollama pull llama2

# 2. Check models
python3 check_ollama.py

# 3. Run RAG
python3 simple_rag_system.py
```

---

**TL;DR**: 
1. `ollama pull bge-m3`
2. `ollama pull llama2`
3. `python3 check_ollama.py`
4. `python3 simple_rag_system.py`

