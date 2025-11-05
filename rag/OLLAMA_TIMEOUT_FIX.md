# 🔧 Fix Ollama Embedding Timeout

## ❌ Problem

Ollama embedding API bị timeout khi xử lý text dài:
```
Error raised by inference API HTTP code: 500
{"error":"do embedding request: Post \"http://127.0.0.1:XXXXX/embedding\": EOF"}
```

## ✅ Solutions Applied

### 1. **Truncate Text**
- Truncate text xuống **1500 characters** để tránh timeout
- Vẫn giữ được semantic meaning chính

### 2. **Batch Processing**
- Xử lý từng hotel một (batch_size=1)
- Delay giữa các batch (0.5s)

### 3. **Retry Logic**
- Retry tối đa 3 lần nếu lỗi
- Delay 2 giây giữa các retry

## 🔍 Alternative Solutions

### Option 1: Use Shorter Text
- Giảm `max_text_length` xuống 1000-1200 nếu vẫn timeout

### Option 2: Use Different Embedding Model
```python
# Thử model nhỏ hơn, nhanh hơn
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",  # Thay vì bge-m3
    base_url=ollama_url
)
```

### Option 3: Use Sentence Transformers (Local)
```python
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
```

### Option 4: Increase Ollama Timeout
- Restart Ollama với timeout lớn hơn
- Hoặc config Ollama timeout trong settings

## 📝 Current Implementation

```python
# Truncate text
max_text_length = 1500
if len(semantic_text) > max_text_length:
    semantic_text = semantic_text[:max_text_length] + "..."

# Batch processing with retry
for i in range(0, len(documents), batch_size):
    for retry in range(max_retries):
        try:
            self.vectorstore.add_texts(...)
            break
        except Exception as e:
            if retry < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise
```

## ✅ Status

- ✅ Text truncation: 1500 chars
- ✅ Batch processing: 1 document/batch
- ✅ Retry logic: 3 attempts
- ✅ Delay between batches: 0.5s

---

**TL;DR**: Text quá dài → Truncate xuống 1500 chars + Batch processing + Retry logic

