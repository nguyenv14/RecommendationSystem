# Hướng dẫn sử dụng LM Studio với RAG System

## 📋 Cấu hình

- **LM Studio URL**: `http://192.168.10.42:1234`
- **Model**: `qwen/qwen3-4b-2507`
- **Embeddings**: Vẫn sử dụng Ollama (`bge-m3`)

## 🚀 Cách sử dụng

### Option 1: Sử dụng script tự động

```bash
cd rag
./run_with_lm_studio.sh
```

Script này sẽ:
- ✅ Kiểm tra LM Studio đang chạy
- ✅ Kiểm tra Ollama (cho embeddings)
- ✅ Kiểm tra Qdrant
- ✅ Khởi động Flask API với cấu hình LM Studio

### Option 2: Sử dụng environment variables

```bash
cd rag
source venv_rag/bin/activate

export LLM_PROVIDER="lm_studio"
export LM_STUDIO_URL="http://192.168.10.42:1234"
export LLM_MODEL="qwen/qwen3-4b-2507"
export OLLAMA_URL="http://localhost:11434"  # For embeddings
export QDRANT_URL="http://localhost:6333"

python rag_chat_api.py
```

### Option 3: Sử dụng script run_chat.sh

```bash
cd rag
source venv_rag/bin/activate

export LLM_PROVIDER="lm_studio"
export LM_STUDIO_URL="http://192.168.10.42:1234"
export LLM_MODEL="qwen/qwen3-4b-2507"

./run_chat.sh
```

## 🧪 Test connection

Test LM Studio connection:

```bash
cd rag
source venv_rag/bin/activate

export LM_STUDIO_URL="http://192.168.10.42:1234"
export LLM_MODEL="qwen/qwen3-4b-2507"

python test_lm_studio.py
```

## ⚙️ Cấu hình trong code

Bạn có thể cấu hình trực tiếp trong code:

```python
from simple_rag_system import SimpleRAGSystem

rag_system = SimpleRAGSystem(
    ollama_url="http://localhost:11434",  # For embeddings
    qdrant_url="http://localhost:6333",
    embedding_model="bge-m3",
    llm_model="qwen/qwen3-4b-2507",
    collection_name="hotels",
    llm_provider="lm_studio",  # Use LM Studio
    lm_studio_url="http://192.168.10.42:1234"
)
```

## 📝 Lưu ý

1. **LM Studio phải đang chạy**: Đảm bảo LM Studio đang chạy và model `qwen/qwen3-4b-2507` đã được load
2. **Ollama vẫn cần cho embeddings**: Hệ thống vẫn sử dụng Ollama để tạo embeddings, chỉ LLM dùng LM Studio
3. **Qdrant phải chạy**: Vector database Qdrant phải đang chạy
4. **Model name chính xác**: Model name phải khớp với tên trong LM Studio (có thể là `qwen/qwen3-4b-2507` hoặc `qwen3-4b-2507`)

## 🔍 Troubleshooting

### LM Studio không kết nối được

```bash
# Test connection
curl http://192.168.10.42:1234/v1/models

# Test model
curl -X POST http://192.168.10.42:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen/qwen3-4b-2507",
    "messages": [{"role": "user", "content": "test"}]
  }'
```

### Model không tìm thấy

- Kiểm tra model đã được load trong LM Studio chưa
- Kiểm tra tên model chính xác (có thể cần `qwen/qwen3-4b-2507` thay vì `qwen3-4b-2507`)

### Lỗi ChatOpenAI initialization

- Kiểm tra LangChain version: `pip install --upgrade langchain-community`
- Thử với `openai_api_base` thay vì `base_url` (code đã có fallback)

## 🎯 So sánh với Ollama

| Feature | Ollama | LM Studio |
|---------|--------|-----------|
| **Setup** | Dễ dàng | Cần cài LM Studio |
| **Models** | Nhiều models | Models từ Hugging Face |
| **Performance** | CPU optimized | GPU/CPU support |
| **API Format** | Ollama API | OpenAI-compatible |
| **Embeddings** | Có sẵn | Cần setup riêng |

## 💡 Lợi ích của LM Studio

1. **GUI dễ sử dụng**: Quản lý models qua giao diện đồ họa
2. **Nhiều models**: Dễ dàng tải và chuyển đổi models từ Hugging Face
3. **GPU support**: Hỗ trợ GPU tốt hơn (nếu có)
4. **OpenAI-compatible**: API tương thích với OpenAI, dễ tích hợp

