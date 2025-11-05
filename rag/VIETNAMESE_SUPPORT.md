# 🇻🇳 Hỗ Trợ Tiếng Việt cho RAG System

## 🎯 Vấn Đề

Model `llama2` không hỗ trợ tiếng Việt tốt, dẫn đến câu trả lời lẫn lộn giữa tiếng Anh và tiếng Việt.

## ✅ Giải Pháp

### 1. **Sử dụng Model Hỗ Trợ Tiếng Việt Tốt Hơn**

Đã cập nhật default model từ `llama2` sang `qwen3` vì:
- ✅ Qwen3 hỗ trợ tiếng Việt rất tốt (model của Alibaba)
- ✅ Hiểu ngữ cảnh tiếng Việt tốt hơn
- ✅ Trả lời nhất quán và tự nhiên hơn
- ✅ Đã có sẵn trong Ollama của bạn

### 2. **Cải Thiện Prompt Template**

Đã cập nhật prompt template với:
- Yêu cầu rõ ràng: "PHẢI trả lời HOÀN TOÀN bằng tiếng Việt"
- Nhấn mạnh nhiều lần về yêu cầu tiếng Việt
- Hướng dẫn chi tiết về cách trả lời

### 3. **Điều Chỉnh Temperature**

Giảm temperature từ `0.7` xuống `0.3` để:
- Câu trả lời tập trung hơn
- Giảm sự lẫn lộn ngôn ngữ
- Trả lời nhất quán hơn

## 🚀 Cách Sử Dụng

### **Bước 1: Kiểm Tra Model Qwen3**

```bash
# Kiểm tra model đã có
ollama list

# Nếu chưa có qwen3, pull model:
ollama pull qwen3
```

### **Bước 2: Chạy Test**

```bash
cd rag
python test_rag.py
```

Hoặc:

```bash
python simple_rag_system.py
```

## 📝 Các Model Khác Hỗ Trợ Tiếng Việt

Nếu `mistral` vẫn chưa đủ tốt, có thể thử:

### **Option 1: Llama3**
```bash
ollama pull llama3
```

Cập nhật trong code:
```python
llm_model="llama3"
```

### **Option 2: Phi3** (Nhẹ, nhanh)
```bash
ollama pull phi3
```

Cập nhật trong code:
```python
llm_model="phi3"
```

### **Option 3: Gemma** (Google)
```bash
ollama pull gemma
```

Cập nhật trong code:
```python
llm_model="gemma"
```

## 🔧 Cấu Hình Nâng Cao

### **Thay Đổi Model**

Trong `simple_rag_system.py` hoặc khi khởi tạo:

```python
rag = SimpleRAGSystem(
    ollama_url="http://localhost:11434",
    qdrant_url="http://localhost:6333",
    embedding_model="bge-m3",
    llm_model="mistral"  # Thay đổi model ở đây
)
```

### **Điều Chỉnh Temperature**

Nếu cần điều chỉnh độ sáng tạo của câu trả lời:

```python
self.llm = Ollama(
    model=llm_model,
    base_url=ollama_url,
    temperature=0.3  # 0.0-1.0: Thấp = tập trung, Cao = sáng tạo
)
```

## 📊 So Sánh Models

| Model | Tiếng Việt | Tốc Độ | Kích Thước | Đề Xuất |
|-------|------------|--------|------------|---------|
| llama2 | ⭐⭐ | ⚡⚡⚡ | 3.8GB | ❌ Không |
| qwen3 | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | 5.2GB | ✅ **Mặc định** |
| mistral | ⭐⭐⭐⭐ | ⚡⚡⚡ | 4.1GB | ✅ Tốt |
| llama3 | ⭐⭐⭐⭐ | ⚡⚡ | 4.7GB | ✅ Tốt |
| phi3 | ⭐⭐⭐ | ⚡⚡⚡⚡ | 2.3GB | ✅ Nhanh |
| gemma | ⭐⭐⭐ | ⚡⚡⚡ | 2.0GB | ✅ Nhẹ |

## ✅ Checklist

- [ ] Kiểm tra model qwen3: `ollama list` (nên có sẵn)
- [ ] Nếu chưa có, pull model: `ollama pull qwen3`
- [ ] Chạy test: `python test_rag.py`
- [ ] Kiểm tra câu trả lời có hoàn toàn bằng tiếng Việt không
- [ ] Nếu chưa tốt, thử model khác (mistral, llama3, phi3, gemma)

## 🐛 Troubleshooting

### **Lỗi: Model không tìm thấy**
```bash
# Kiểm tra Ollama đang chạy
curl http://localhost:11434/api/tags

# Pull model qwen3
ollama pull qwen3
```

### **Lỗi: Câu trả lời vẫn lẫn lộn**
1. Kiểm tra prompt template đã được cập nhật chưa
2. Thử model khác (llama3, phi3)
3. Giảm temperature xuống 0.1-0.2

### **Lỗi: Trả lời quá chậm**
- Thử model nhẹ hơn: `phi3` hoặc `gemma`
- Giảm `k` trong retriever (số documents retrieved)

---

**Lưu ý:** Model `qwen3` là default mới và đã có sẵn trong Ollama của bạn. Qwen3 hỗ trợ tiếng Việt rất tốt!

