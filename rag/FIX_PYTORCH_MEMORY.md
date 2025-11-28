# Fix PyTorch Memory Issues on Mac

## Vấn đề
Hệ thống RAG sử dụng Ollama cho embeddings và LLM (chạy trên server), không cần PyTorch local. Tuy nhiên, PyTorch có thể được cài đặt và gây ra vấn đề bộ nhớ trên Mac.

## Giải pháp

### 1. Uninstall PyTorch từ venv
```bash
cd rag
bash uninstall_pytorch.sh
```

Hoặc thủ công:
```bash
# Activate venv
source venv_rag/bin/activate  # hoặc source ../venv/bin/activate

# Uninstall
pip uninstall -y torch torchvision torchaudio sentence-transformers transformers
```

### 2. Đảm bảo biến môi trường được set
Các file Python đã được cập nhật để set biến môi trường TRƯỚC khi import:
- `simple_rag_system.py`
- `api/chat_api.py`

Biến môi trường:
- `TRANSFORMERS_OFFLINE=1`
- `HF_HUB_OFFLINE=1`
- `TORCH_DISABLE_IMPORT=1`
- `TOKENIZERS_PARALLELISM=false`

### 3. Kiểm tra requirements
File `requirements_rag.txt` đã được cập nhật để KHÔNG bao gồm:
- `sentence-transformers`
- `transformers`

### 4. Nếu vẫn gặp vấn đề

#### Kiểm tra venv nào đang được dùng:
```bash
which python
pip list | grep -i torch
```

#### Uninstall từ tất cả venv:
```bash
# Từ venv_rag
cd rag && source venv_rag/bin/activate && pip uninstall -y torch torchvision torchaudio sentence-transformers transformers

# Từ venv chính
cd .. && source venv/bin/activate && pip uninstall -y torch torchvision torchaudio sentence-transformers transformers
```

#### Kiểm tra LangChain không import PyTorch:
```bash
python -c "import os; os.environ['TRANSFORMERS_OFFLINE']='1'; from langchain_community.embeddings import OllamaEmbeddings; print('OK')"
```

## Lý do
- Hệ thống sử dụng **Ollama** cho embeddings (chạy trên server, không cần PyTorch local)
- Hệ thống sử dụng **Ollama/LM Studio** cho LLM (chạy trên server, không cần PyTorch local)
- PyTorch chỉ cần thiết nếu chạy models local (như sentence-transformers), nhưng chúng ta không dùng

## Kiểm tra sau khi fix
```bash
# Chạy script và kiểm tra không có warning về PyTorch
cd rag
source venv_rag/bin/activate
python -c "from simple_rag_system import SimpleRAGSystem; print('✅ OK - No PyTorch loaded')"
```

