# 🏨 Hướng Dẫn Setup - Unified Hotel Recommendation & RAG System

## 📋 Mục Lục

1. [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
2. [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
3. [Cài đặt công cụ cần thiết](#-cài-đặt-công-cụ-cần-thiết)
4. [Cách 1: Setup với Ollama (Khuyến nghị)](#-cách-1-setup-với-ollama-khuyến-nghị)
5. [Cách 2: Setup với LM Studio](#-cách-2-setup-với-lm-studio)
6. [Index dữ liệu](#-index-dữ-liệu)
7. [Kiểm tra hệ thống](#-kiểm-tra-hệ-thống)
8. [API Endpoints](#-api-endpoints)
9. [Troubleshooting](#-troubleshooting)

---

## 🎯 Kiến trúc hệ thống

Hệ thống được chia làm **2 phần độc lập**:

### 1. **RAG System** (Chatbot)
- **Folder**: `rag/`
- **Collection**: `hotels_rag`, `coupons_rag`
- **Embedding model**: `bge-m3` (1024 dims) - **Bắt buộc dùng Ollama**
- **LLM model**: `qwen3` hoặc model từ LM Studio
- **Mục đích**: Chatbot trả lời câu hỏi về khách sạn

### 2. **Recommendation System** (Gợi ý)
- **Folder**: `recommendation/`
- **Collection**: `hotels_recommendation`
- **Embedding model**: `paraphrase-multilingual-MiniLM-L12-v2` (384 dims)
- **Mục đích**: Gợi ý khách sạn tương tự

---

## 💻 Yêu cầu hệ thống

- **Python**: 3.9+ (khuyến nghị Python 3.9)
- **Docker**: Để chạy Qdrant, MySQL, Redis
- **Git**: Để clone repository
- **Ollama**: Bắt buộc (cho embedding model `bge-m3`)
- **LM Studio** (tùy chọn): Nếu muốn dùng LM Studio thay vì Ollama cho LLM

---

## 🔧 Cài đặt công cụ cần thiết

### 1. Docker

**Windows/Mac:**
- Tải Docker Desktop: https://www.docker.com/products/docker-desktop
- Cài đặt và khởi động Docker Desktop

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 2. Ollama (Bắt buộc)

Ollama **BẮT BUỘC** vì hệ thống cần model `bge-m3` cho embedding.

**Cách 1: Cài đặt trực tiếp**
- Tải về: https://ollama.com/
- Cài đặt theo hướng dẫn
- Sau khi cài xong, chạy:
```bash
ollama pull bge-m3
```

**Cách 2: Chạy bằng Docker (nhanh hơn)**
```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama
# Sau đó pull model
docker exec -it ollama ollama pull bge-m3
```

**Kiểm tra:**
```bash
ollama list
# Phải thấy: bge-m3
```

### 3. LM Studio (Tùy chọn - Chỉ cần nếu dùng Cách 2)

**Chỉ cần cài nếu bạn muốn dùng LM Studio thay vì Ollama cho LLM**

- Tải về: https://lmstudio.ai/
- Cài đặt và mở LM Studio
- Tải model `qwen/qwen3-4b-2507`:
  1. Mở LM Studio
  2. Vào tab "Search"
  3. Tìm kiếm: `qwen/qwen3-4b-2507`
  4. Click "Download"
  5. Đợi tải xong

---

## 🚀 Cách 1: Setup với Ollama (Khuyến nghị)

### Bước 1: Clone repository và vào thư mục

```bash
cd Recommendation
```

### Bước 2: Đảm bảo Ollama đang chạy

```bash
# Kiểm tra Ollama
ollama list

# Nếu chưa có model bge-m3, pull nó
ollama pull bge-m3

# Nếu muốn dùng Ollama cho LLM (không bắt buộc)
ollama pull qwen3
```

### Bước 3: Chạy hệ thống

**Linux/Mac:**
```bash
chmod +x run_app.sh
./run_app.sh
```

**Windows:**
```cmd
run_app.bat
```

**Script tự động làm:**
1. ✅ Kiểm tra Python 3.9+
2. ✅ Start Docker (Qdrant, MySQL, Redis)
3. ✅ Tạo virtual environment
4. ✅ Install dependencies
5. ✅ Tạo collections (RAG + Recommendation)
6. ✅ Khởi động app tại `http://localhost:5000`

### Bước 4: Index dữ liệu (nếu chưa có)

Xem phần [Index dữ liệu](#-index-dữ-liệu) bên dưới.

---

## 🎨 Cách 2: Setup với LM Studio

**Lưu ý:** Vẫn cần Ollama cho embedding model `bge-m3`. LM Studio chỉ thay thế Ollama cho LLM.

### Bước 1: Cài đặt Ollama (bắt buộc)

```bash
# Cài đặt Ollama (xem phần trên)
ollama pull bge-m3
```

### Bước 2: Cài đặt và khởi động LM Studio

1. Tải và cài đặt LM Studio: https://lmstudio.ai/
2. Mở LM Studio
3. Tải model `qwen/qwen3-4b-2507` (xem phần cài đặt LM Studio ở trên)
4. Vào tab "Local Server"
5. Chọn model `qwen/qwen3-4b-2507`
6. Click **"Start Server"**
7. Đảm bảo server chạy tại: `http://127.0.0.1:1234`

### Bước 3: Chạy hệ thống với LM Studio

**Linux/Mac:**
```bash
chmod +x run_app_lmstudio.sh
./run_app_lmstudio.sh
```

**Windows:**
```cmd
run_app_lmstudio.bat
```

**Script tự động:**
1. ✅ Kiểm tra Python 3.9+
2. ✅ Kiểm tra LM Studio đang chạy
3. ✅ Start Docker (Qdrant, MySQL, Redis)
4. ✅ Tạo virtual environment
5. ✅ Install dependencies
6. ✅ Tạo collections
7. ✅ Khởi động app với LM Studio

### Bước 4: Index dữ liệu (nếu chưa có)

Xem phần [Index dữ liệu](#-index-dữ-liệu) bên dưới.

---

## 📊 Index dữ liệu

### Tự động index (khi chạy app)

Nếu muốn tự động index khi start:

```bash
# Linux/Mac
export AUTO_INDEX_DATA=true
./run_app_lmsstudio.sh

# Windows
set AUTO_INDEX_DATA=true
run_app_lmsstudio.bat
```

### Index thủ công

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

## ✅ Kiểm tra hệ thống

### 1. Kiểm tra Collections

```bash
python scripts/verify_collections.py
```

**Output mong đợi:**
```
Collection               | System          | Points
-------------------------|-----------------|--------
hotels_rag               | RAG            | 22
coupons_rag              | RAG            | 4
hotels_recommendation    | Recommendation | 22
```

### 2. Kiểm tra Health

Mở trình duyệt:
- Health check: http://localhost:5000/health
- Status: http://localhost:5000/api/status

### 3. Test API

**RAG Chat:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Khách sạn nào gần biển?"}'
```

**Recommendation:**
```bash
curl http://localhost:5000/api/recommend/similar/2
```

---

## 📝 API Endpoints

### RAG (Chatbot)
- `POST /api/chat` - Chat với chatbot
- `POST /api/search` - Tìm kiếm semantic
- `GET /api/status` - Thông tin chi tiết

### Recommendation (Gợi ý)
- `POST /api/recommend/query` - Gợi ý theo query
- `GET /api/recommend/similar/<item_id>` - Gợi ý tương tự
- `GET /api/recommend/popular` - Gợi ý phổ biến
- `POST /api/recommend/hybrid` - Hybrid recommendation

### Health
- `GET /health` - Health check
- `GET /api/health` - Health check (alias)

---

## ⚙️ Configuration

### Environment Variables

Tạo file `.env` (hoặc export trong terminal):

```bash
# Qdrant
QDRANT_URL=http://localhost:6333

# Ollama (Bắt buộc cho embedding)
OLLAMA_URL=http://localhost:11434
EMBEDDING_MODEL=bge-m3

# LLM Provider (chọn 1 trong 2)
# Cách 1: Dùng Ollama
LLM_PROVIDER=ollama
LLM_MODEL=qwen3

# Cách 2: Dùng LM Studio
LLM_PROVIDER=lm_studio
LM_STUDIO_URL=http://127.0.0.1:1234

# Database
MYSQL_HOST=localhost
MYSQL_PORT=3308
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=myhotel

# Redis
REDIS_URL=redis://localhost:6379
```

---

## 🐛 Troubleshooting

### 1. Collections trống

```bash
# Index RAG data
cd rag/ && python simple_rag_system.py

# Index Recommendation data
cd recommendation/ && python semantic_recommendation_system.py
```

### 2. Ollama không kết nối

```bash
# Kiểm tra Ollama đang chạy
ollama list

# Nếu không chạy, start lại
ollama serve

# Pull model nếu chưa có
ollama pull bge-m3
```

### 3. LM Studio không kết nối

- Mở LM Studio
- Vào tab "Local Server"
- Chọn model `qwen/qwen3-4b-2507`
- Click "Start Server"
- Kiểm tra: http://127.0.0.1:1234/v1/models

### 4. Port conflicts

**Windows:**
```cmd
netstat -ano | findstr "6333"  # Qdrant
netstat -ano | findstr "11434" # Ollama
netstat -ano | findstr "1234"  # LM Studio
netstat -ano | findstr "5000"  # App
```

**Linux/Mac:**
```bash
lsof -i :6333   # Qdrant
lsof -i :11434  # Ollama
lsof -i :1234   # LM Studio
lsof -i :5000   # App
```

### 5. Docker không chạy

```bash
# Kiểm tra Docker
docker ps

# Start Docker services
docker-compose up -d
```

### 6. Python version không đúng

```bash
# Kiểm tra version
python --version  # Phải là 3.9+

# Nếu không đúng, cài Python 3.9
# Windows: https://www.python.org/downloads/
# Linux: sudo apt install python3.9
# Mac: brew install python@3.9
```

---

## 📚 Documentation

- **RAG System**: `rag/README.md`
- **Recommendation System**: `recommendation/README_QUICK_START.md`
- **API Documentation**: `COMPLETE_RECOMMENDATION_SYSTEMS.md`
- **Project Structure**: Xem `src/README.md`

---

## 🔄 So sánh 2 cách setup

| Tính năng | Cách 1: Ollama | Cách 2: LM Studio |
|-----------|----------------|-------------------|
| **Embedding** | Ollama (bge-m3) | Ollama (bge-m3) - Bắt buộc |
| **LLM** | Ollama (qwen3) | LM Studio (qwen3-4b-2507) |
| **Tốc độ** | Nhanh | Rất nhanh (GPU) |
| **Dễ setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Yêu cầu GPU** | Không | Có (khuyến nghị) |
| **Khuyến nghị** | ✅ Cho người mới | ✅ Cho production |

---

## 💡 Tips

1. **Lần đầu setup**: Dùng Cách 1 (Ollama) vì đơn giản hơn
2. **Production**: Dùng Cách 2 (LM Studio) nếu có GPU
3. **Embedding**: Luôn dùng Ollama (bắt buộc)
4. **LLM**: Có thể chọn Ollama hoặc LM Studio tùy nhu cầu

---

**Chúc bạn setup thành công! 🎉**
