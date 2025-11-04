# 🚀 QUICK START - CÁCH CHẠY RAG PROJECT

## 📋 Tổng Quan

Hướng dẫn nhanh cách chạy RAG project từ đầu đến cuối.

---

## ⚡ **QUICK START (3 Bước)**

### **Bước 1: Setup Environment**

```bash
cd rag

# Tạo và activate venv
python3 -m venv venv_rag
source venv_rag/bin/activate

# Install dependencies
pip install langchain langchain-community langchain-core qdrant-client pandas numpy requests
```

### **Bước 2: Start Services**

```bash
# Start Qdrant và Redis
docker-compose up -d

# Verify
curl http://localhost:6333/health
```

### **Bước 3: Chạy RAG**

```bash
# Chạy RAG system (sẽ index data và test)
python3 simple_rag_system.py
```

---

## 🔧 **HOẶC DÙNG SCRIPT (All-in-One)**

```bash
cd rag
./run_project.sh
```

Script sẽ tự động:
1. ✅ Tạo venv
2. ✅ Install dependencies
3. ✅ Start services
4. ✅ Normalize data (nếu chưa có)
5. ✅ Test RAG system

---

## 📝 **CHI TIẾT TỪNG BƯỚC**

### **1. Setup Virtual Environment**

```bash
cd /Users/kdn/Documents/Workspace/nguyen/RecommendationSystem/rag

# Tạo venv
python3 -m venv venv_rag

# Activate
source venv_rag/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### **2. Install Dependencies**

```bash
# Install từ requirements
pip install -r requirements_rag.txt

# Hoặc install thủ công
pip install langchain langchain-community langchain-core qdrant-client pandas numpy requests
```

### **3. Start Docker Services**

```bash
# Start Qdrant và Redis
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### **4. Verify Services**

```bash
# Check Qdrant
curl http://localhost:6333/health

# Check Redis
docker exec redis_rag redis-cli ping

# Check Ollama (đã có sẵn)
curl http://localhost:11434/api/tags
```

### **5. Normalize Data (Nếu chưa có)**

```bash
# Chạy normalization
python3 hotel_data_normalization.py

# Output: normalized_data/normalized_hotels.csv
```

### **6. Index và Test RAG**

```bash
# Chạy RAG system
python3 simple_rag_system.py

# Hoặc test nhanh
python3 test_rag.py
```

---

## 🐛 **FIX LỖI THƯỜNG GẶP**

### **Lỗi: ModuleNotFoundError**

```bash
# Activate venv
source venv_rag/bin/activate

# Install dependencies
pip install langchain langchain-community langchain-core qdrant-client
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

## ✅ **CHECKLIST**

- [ ] Virtual environment created (`venv_rag`)
- [ ] Dependencies installed
- [ ] Qdrant running (docker-compose up -d)
- [ ] Redis running (optional)
- [ ] Ollama running với bge-m3 và llama2
- [ ] Normalized data exists
- [ ] RAG system chạy thành công

---

## 📚 **COMMANDS REFERENCE**

```bash
# Setup
cd rag
python3 -m venv venv_rag
source venv_rag/bin/activate
pip install -r requirements_rag.txt

# Services
docker-compose up -d
docker-compose ps
docker-compose logs -f
docker-compose down

# Run
python3 hotel_data_normalization.py  # Normalize data
python3 simple_rag_system.py          # Index và test RAG
python3 test_rag.py                   # Test nhanh
```

---

**TL;DR**: 
1. `source venv_rag/bin/activate`
2. `pip install -r requirements_rag.txt`
3. `docker-compose up -d`
4. `python3 simple_rag_system.py`

