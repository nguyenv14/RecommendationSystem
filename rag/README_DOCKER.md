# Docker Compose Setup cho RAG System

## 📋 Tổng Quan

Docker Compose file này setup các services cần thiết cho hệ thống RAG:
- **Qdrant**: Vector database cho embeddings
- **Redis**: Caching (optional, improve performance)
- **RAG API**: Flask API service (optional, có thể chạy local)

**Lưu ý**: Ollama đã chạy sẵn trên host, không cần trong docker-compose.

---

## 🚀 Quick Start

### **1. Start Services**

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### **2. Verify Services**

```bash
# Check Qdrant
curl http://localhost:6333/health

# Check Redis
docker exec redis_rag redis-cli ping

# Check Qdrant dashboard
open http://localhost:6333/dashboard
```

### **3. Stop Services**

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: will delete data)
docker-compose down -v
```

---

## 📦 Services

### **1. Qdrant (Vector Database)**

**Ports:**
- `6333`: HTTP API
- `6334`: gRPC API

**Access:**
```bash
# HTTP API
http://localhost:6333

# Dashboard
http://localhost:6333/dashboard

# gRPC (from Python)
qdrant://localhost:6334
```

**Volume:**
- `qdrant_storage`: Persistent storage for vectors

**Health Check:**
```bash
curl http://localhost:6333/health
```

### **2. Redis (Caching - Optional)**

**Port:**
- `6380`: Redis server (external port, mapped from internal 6379)

**Access:**
```bash
# Connect from Python
redis://localhost:6380

# CLI
docker exec -it redis_rag redis-cli
```

**Volume:**
- `redis_data`: Persistent storage for cache

### **3. RAG API (Optional)**

Nếu muốn chạy API trong Docker, uncomment service `rag_api` trong docker-compose.yml.

**Port:**
- `5000`: Flask API

**Access:**
```bash
http://localhost:5000/health
```

---

## 🔧 Configuration

### **Environment Variables**

Các services có thể config qua environment variables hoặc docker-compose.yml:

**Qdrant:**
```yaml
environment:
  - QDRANT__SERVICE__HTTP_PORT=6333
  - QDRANT__SERVICE__GRPC_PORT=6334
  - QDRANT__LOG_LEVEL=INFO
```

**Redis:**
```yaml
command: redis-server --appendonly yes
```

**RAG API:**
```yaml
environment:
  - QDRANT_URL=http://qdrant:6333
  - OLLAMA_URL=http://host.docker.internal:11434
  - REDIS_URL=redis://redis:6379
```

### **Volumes**

**Persistent Storage:**
- `qdrant_storage`: Qdrant data
- `redis_data`: Redis cache data

**Location:**
```bash
# Docker volumes
docker volume ls

# Inspect volume
docker volume inspect qdrant_rag_storage
```

---

## 🔌 Connecting to Ollama (Host)

### **Từ Container**

Nếu chạy API trong Docker, cần connect đến Ollama trên host:

```python
# In Docker container
OLLAMA_URL = "http://host.docker.internal:11434"
```

**Docker Compose:**
```yaml
environment:
  - OLLAMA_URL=http://host.docker.internal:11434
```

### **Từ Local Machine**

```python
# Local Python
OLLAMA_URL = "http://localhost:11434"
```

---

## 📊 Usage Examples

### **1. Connect to Qdrant from Python**

```python
from qdrant_client import QdrantClient

# Connect to Qdrant
client = QdrantClient(
    url="http://localhost:6333",
    # or use gRPC
    # grpc_port=6334
)

# Check health
health = client.get_collections()
print(health)
```

### **2. Connect to Redis from Python**

```python
import redis

# Connect to Redis
r = redis.Redis(
    host='localhost',
    port=6380,  # Changed to 6380
    decode_responses=True
)

# Test connection
r.ping()
```

### **3. Use LangChain with Qdrant**

```python
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings

# Initialize embeddings (Ollama on host)
embeddings = OllamaEmbeddings(
    model="bge-m3",
    base_url="http://localhost:11434"  # Host Ollama
)

# Connect to Qdrant
vectorstore = Qdrant(
    client=QdrantClient(url="http://localhost:6333"),
    collection_name="hotels",
    embeddings=embeddings
)
```

---

## 🛠️ Troubleshooting

### **Qdrant không start**

```bash
# Check logs
docker-compose logs qdrant

# Check port conflict
netstat -an | grep 6333

# Restart service
docker-compose restart qdrant
```

### **Redis connection failed**

```bash
# Check Redis logs
docker-compose logs redis

# Test connection
docker exec redis_rag redis-cli ping

# Restart Redis
docker-compose restart redis
```

### **Cannot connect to Ollama from container**

**Problem**: `host.docker.internal` không hoạt động trên Linux.

**Solution**:
```yaml
# Use host network mode (Linux)
network_mode: "host"

# Or use host IP
environment:
  - OLLAMA_URL=http://172.17.0.1:11434
```

### **Volume permissions**

```bash
# Check volume permissions
docker volume inspect qdrant_rag_storage

# Fix permissions (if needed)
sudo chown -R $USER:$USER /var/lib/docker/volumes/qdrant_rag_storage
```

---

## 📈 Monitoring

### **Qdrant Metrics**

```bash
# Qdrant stats
curl http://localhost:6333/metrics

# Collection info
curl http://localhost:6333/collections/{collection_name}
```

### **Redis Stats**

```bash
# Connect to Redis CLI
docker exec -it redis_rag redis-cli

# Get stats
INFO stats

# Get memory usage
INFO memory
```

---

## 🔐 Security

### **Production Setup**

1. **Change default ports** (optional):
```yaml
ports:
  - "127.0.0.1:6333:6333"  # Only localhost
```

2. **Add authentication** (Qdrant):
```yaml
environment:
  - QDRANT__SERVICE__API_KEY=your-api-key
```

3. **Redis password**:
```yaml
command: redis-server --requirepass yourpassword
```

---

## 📝 Commands Cheat Sheet

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart service
docker-compose restart [service_name]

# Check status
docker-compose ps

# Execute command in container
docker exec -it [container_name] [command]

# Remove everything (including volumes)
docker-compose down -v

# Rebuild services
docker-compose build

# View resource usage
docker stats
```

---

## ✅ Checklist

- [x] Qdrant running on port 6333
- [x] Redis running on port 6379 (optional)
- [x] Ollama running on host (port 11434)
- [x] Volumes mounted correctly
- [x] Health checks passing
- [x] Can connect from Python code

---

## 📚 References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Redis Documentation](https://redis.io/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**TL;DR**: Run `docker-compose up -d` to start Qdrant and Redis. Ollama runs separately on host.

