# HƯỚNG DẪN CHẠY RAG PROJECT

## 📋 Tổng Quan

Hướng dẫn chạy RAG system từ đầu đến cuối.

---

## 🚀 **BƯỚC 1: SETUP ENVIRONMENT**

### **1.1 Tạo Virtual Environment**

```bash
cd rag

# Tạo venv
python3 -m venv venv_rag

# Hoặc dùng script
./setup_venv.sh
```

### **1.2 Activate Virtual Environment**

```bash
source venv_rag/bin/activate
```

### **1.3 Install Dependencies**

```bash
pip install -r requirements_rag.txt
```

Hoặc nếu không có requirements file:
```bash
pip install langchain langchain-community langchain-core qdrant-client pandas numpy requests
```

---

## 🐳 **BƯỚC 2: START SERVICES**

### **2.1 Start Qdrant và Redis**

```bash
# Từ folder rag/
docker-compose up -d

# Hoặc dùng script
./start_docker.sh
```

**Verify services:**
```bash
# Check Qdrant
curl http://localhost:6333/health

# Check Redis
docker exec redis_rag redis-cli ping

# Check status
docker-compose ps
```

### **2.2 Verify Ollama**

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama (đã có sẵn)
```

---

## 📊 **BƯỚC 3: NORMALIZE DATA (Nếu chưa có)**

### **3.1 Chạy Normalization**

```bash
# Từ folder rag/
python3 hotel_data_normalization.py

# Hoặc dùng script
./run_normalization.sh
```

**Output:** `normalized_data/normalized_hotels.csv`

---

## 🔍 **BƯỚC 4: INDEX DATA VÀO QDRANT**

### **4.1 Chạy RAG System để Index**

```bash
# Từ folder rag/
python3 simple_rag_system.py
```

**Lần đầu sẽ:**
- Load normalized data
- Index vào Qdrant
- Tạo vectorstore và retriever

**Lần sau:**
- Load existing vectorstore từ Qdrant

---

## 🧪 **BƯỚC 5: TEST RAG SYSTEM**

### **5.1 Test Semantic Search**

```python
from simple_rag_system import SimpleRAGSystem

# Initialize
rag = SimpleRAGSystem()

# Load existing vectorstore
rag.load_vectorstore()

# Test search
results = rag.search_hotels("Khách sạn 5 sao gần biển", top_k=5)
for hotel in results:
    print(f"{hotel['hotel_name']} - Similarity: {hotel['similarity_score']:.3f}")
```

### **5.2 Test RAG (với LLM)**

```python
# Test RAG
response = rag.ask("Khách sạn nào 5 sao gần biển Đà Nẵng?")
print(response["answer"])
print("\nSources:")
for source in response["sources"]:
    print(f"- {source['hotel_name']}")
```

### **5.3 Chạy Test Script**

```bash
python3 test_rag.py
```

---

## 📝 **QUICK START - TẤT CẢ TRONG 1**

### **Script Run All-in-One**

```bash
#!/bin/bash
# Quick start script

cd rag

# 1. Setup venv (nếu chưa có)
if [ ! -d "venv_rag" ]; then
    python3 -m venv venv_rag
fi

# 2. Activate venv
source venv_rag/bin/activate

# 3. Install dependencies
pip install -r requirements_rag.txt

# 4. Start services
docker-compose up -d

# 5. Wait for services
sleep 5

# 6. Normalize data (nếu chưa có)
if [ ! -f "normalized_data/normalized_hotels.csv" ]; then
    python3 hotel_data_normalization.py
fi

# 7. Test RAG
python3 test_rag.py
```

---

## 🔧 **TROUBLESHOOTING**

### **Lỗi: ModuleNotFoundError**

```bash
# Activate venv
source venv_rag/bin/activate

# Install dependencies
pip install -r requirements_rag.txt
```

### **Lỗi: Qdrant connection failed**

```bash
# Check Qdrant is running
docker-compose ps

# Start Qdrant
docker-compose up -d qdrant

# Check health
curl http://localhost:6333/health
```

### **Lỗi: Ollama connection failed**

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama (đã có sẵn)
```

### **Lỗi: Normalized data not found**

```bash
# Run normalization
python3 hotel_data_normalization.py
```

---

## ✅ **CHECKLIST CHẠY PROJECT**

- [ ] Virtual environment created và activated
- [ ] Dependencies installed
- [ ] Qdrant running (docker-compose up -d)
- [ ] Redis running (optional)
- [ ] Ollama running với bge-m3 và llama2
- [ ] Normalized data exists (normalized_hotels.csv)
- [ ] Data indexed vào Qdrant
- [ ] Test RAG system thành công

---

## 📚 **COMMANDS CHEAT SHEET**

```bash
# Setup
cd rag
python3 -m venv venv_rag
source venv_rag/bin/activate
pip install -r requirements_rag.txt

# Start services
docker-compose up -d

# Normalize data
python3 hotel_data_normalization.py

# Index và test
python3 simple_rag_system.py

# Test nhanh
python3 test_rag.py

# Stop services
docker-compose down
```

---

**TL;DR**: 
1. `source venv_rag/bin/activate`
2. `pip install -r requirements_rag.txt`
3. `docker-compose up -d`
4. `python3 simple_rag_system.py`

