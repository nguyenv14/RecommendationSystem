# CÁCH LƯU TRỮ CÁC CHUNK TRONG RAG

## 📋 Tổng Quan

Tài liệu này mô tả các phương pháp lưu trữ chunks trong hệ thống RAG, đặc biệt với LangChain và các vector databases.

---

## 🎯 **1. CÁC PHƯƠNG PHÁP LƯU TRỮ CHUNKS**

### **1.1 Vector Database (Khuyến Nghị)**

**Cách hoạt động:**
- Lưu trữ **vector embeddings** của chunks
- Lưu trữ **metadata** (hotel_id, hotel_name, etc.)
- Lưu trữ **original text** (page_content)

**Ưu điểm:**
- ✅ Tìm kiếm nhanh (semantic search)
- ✅ Hỗ trợ metadata filtering
- ✅ Scalable (hàng triệu chunks)
- ✅ Persistent storage

**Nhược điểm:**
- ⚠️ Cần setup vector database
- ⚠️ Tốn memory cho vectors

### **1.2 In-Memory Storage (Chỉ cho Testing)**

**Cách hoạt động:**
- Lưu trữ trong RAM (Python dict/list)
- Không persistent

**Ưu điểm:**
- ✅ Dễ setup
- ✅ Nhanh cho dataset nhỏ

**Nhược điểm:**
- ❌ Không persistent (mất khi restart)
- ❌ Không scalable (tốn RAM)
- ❌ Chỉ cho testing

### **1.3 File-Based Storage (Không Khuyến Nghị)**

**Cách hoạt động:**
- Lưu trữ vectors trong file (pickle, JSON, parquet)
- Load toàn bộ vào memory khi query

**Ưu điểm:**
- ✅ Đơn giản
- ✅ Persistent

**Nhược điểm:**
- ❌ Chậm (load toàn bộ)
- ❌ Không scalable
- ❌ Không hỗ trợ metadata filtering tốt

---

## 🗄️ **2. VECTOR DATABASES - SO SÁNH**

### **2.1 Qdrant (Khuyến Nghị - Bạn Đã Có)**

**Đặc điểm:**
- ✅ Open-source, tự host
- ✅ Hỗ trợ metadata filtering tốt
- ✅ REST API và gRPC
- ✅ LangChain integration tốt
- ✅ Scalable (hàng triệu vectors)

**Cách lưu trữ:**
```python
# Mỗi chunk = 1 point trong Qdrant
{
    "id": chunk_id,              # Unique ID
    "vector": [0.1, 0.2, ...],   # Embedding vector
    "payload": {                  # Metadata
        "hotel_id": 2,
        "hotel_name": "Meliá Vinpearl Riverfront",
        "chunk_index": 0,
        "text": "Tên: Meliá Vinpearl Riverfront | Mô tả: ..."
    }
}
```

**Storage Structure:**
```
Collection: "hotels"
├── Point 1: {id: 1, vector: [...], payload: {hotel_id: 2, chunk_index: 0}}
├── Point 2: {id: 2, vector: [...], payload: {hotel_id: 2, chunk_index: 1}}
├── Point 3: {id: 3, vector: [...], payload: {hotel_id: 3, chunk_index: 0}}
└── ...
```

### **2.2 Milvus**

**Đặc điểm:**
- ✅ Open-source
- ✅ Cloud-native
- ✅ Hỗ trợ distributed
- ⚠️ Setup phức tạp hơn Qdrant

**Cách lưu trữ:**
- Tương tự Qdrant
- Collection → Entities với vectors + metadata

### **2.3 Chroma**

**Đặc điểm:**
- ✅ Embedding database chuyên dụng
- ✅ Dễ setup
- ✅ LangChain integration tốt
- ⚠️ Ít features hơn Qdrant

**Cách lưu trữ:**
```python
# Collection → Documents với embeddings
collection.add(
    documents=["chunk text"],
    embeddings=[[0.1, 0.2, ...]],
    metadatas=[{"hotel_id": 2}]
)
```

### **2.4 Weaviate**

**Đặc điểm:**
- ✅ GraphQL API
- ✅ Hỗ trợ vector + graph
- ✅ Enterprise features
- ⚠️ Setup phức tạp

### **2.5 Pinecone (Cloud)**

**Đặc điểm:**
- ✅ Managed service
- ✅ Không cần setup
- ✅ Scalable
- ❌ Tốn tiền (paid service)

---

## 📦 **3. CẤU TRÚC LƯU TRỮ CHUNKS**

### **3.1 Cấu Trúc Cơ Bản**

**Mỗi chunk cần lưu:**
```
{
    "id": unique_id,              # Unique identifier
    "vector": [0.1, 0.2, ...],    # Embedding vector
    "text": "chunk content",      # Original text
    "metadata": {                  # Metadata
        "hotel_id": 2,
        "hotel_name": "Meliá Vinpearl Riverfront",
        "chunk_index": 0,
        "source": "tbl_hotel.csv",
        "area_id": 8,
        "brand_id": 3,
        "hotel_rank": 5,
        "hotel_price_average": 1311127
    }
}
```

### **3.2 Với Dataset Khách Sạn**

**Option 1: Mỗi Hotel = 1 Chunk (Recommended cho dataset nhỏ)**
```
Hotel 1 → 1 chunk
Hotel 2 → 1 chunk
Hotel 3 → 1 chunk
...
```

**Ưu điểm:**
- ✅ Đơn giản
- ✅ Dễ maintain
- ✅ Phù hợp nếu hotel description không quá dài

**Cấu trúc:**
```python
{
    "id": hotel_id,  # hotel_id = chunk_id
    "vector": [...],
    "text": "Tên: {hotel_name} | Mô tả: {hotel_desc} | Địa chỉ: {hotel_placedetails} | ...",
    "metadata": {
        "hotel_id": 2,
        "hotel_name": "Meliá Vinpearl Riverfront",
        "area_id": 8,
        "brand_id": 3,
        "hotel_rank": 5,
        "hotel_price_average": 1311127,
        "chunk_index": 0,
        "chunk_type": "full_hotel"
    }
}
```

**Option 2: Mỗi Hotel = Nhiều Chunks (Nếu description dài)**
```
Hotel 1 → Chunk 0 (description part 1)
Hotel 1 → Chunk 1 (description part 2)
Hotel 1 → Chunk 2 (room info)
Hotel 2 → Chunk 0 (description part 1)
...
```

**Ưu điểm:**
- ✅ Phù hợp với description dài
- ✅ Chính xác hơn (mỗi chunk tập trung vào 1 phần)

**Nhược điểm:**
- ⚠️ Phức tạp hơn
- ⚠️ Cần join chunks khi retrieve

**Cấu trúc:**
```python
# Chunk 0: Basic info
{
    "id": f"{hotel_id}_0",
    "vector": [...],
    "text": "Tên: {hotel_name} | Mô tả phần 1: {desc_part1}",
    "metadata": {
        "hotel_id": 2,
        "chunk_index": 0,
        "chunk_type": "basic_info"
    }
}

# Chunk 1: Description detail
{
    "id": f"{hotel_id}_1",
    "vector": [...],
    "text": "Mô tả phần 2: {desc_part2} | Địa chỉ: {hotel_placedetails}",
    "metadata": {
        "hotel_id": 2,
        "chunk_index": 1,
        "chunk_type": "description"
    }
}

# Chunk 2: Room info
{
    "id": f"{hotel_id}_2",
    "vector": [...],
    "text": "Phòng: {room_name} | Giá: {price} | View: {room_view}",
    "metadata": {
        "hotel_id": 2,
        "chunk_index": 2,
        "chunk_type": "room_info"
    }
}
```

---

## 🏗️ **4. LƯU TRỮ VỚI LANGCHAIN**

### **4.1 Qdrant (Khuyến Nghị)**

**Setup:**
```python
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document

# 1. Initialize embeddings
embeddings = OllamaEmbeddings(
    model="bge-m3",
    base_url="http://localhost:11434"
)

# 2. Create documents
documents = []
for hotel in hotels_df:
    doc = Document(
        page_content=f"Tên: {hotel_name} | Mô tả: {hotel_desc} | ...",
        metadata={
            "hotel_id": hotel["hotel_id"],
            "hotel_name": hotel["hotel_name"],
            "area_id": hotel["area_id"],
            "brand_id": hotel["brand_id"],
            "hotel_rank": hotel["hotel_rank"],
            "hotel_price_average": hotel["hotel_price_average"]
        }
    )
    documents.append(doc)

# 3. Store in Qdrant
vectorstore = Qdrant.from_documents(
    documents=documents,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="hotels",
    prefer_grpc=True
)

# 4. Save (persistent)
# Qdrant tự động lưu vào disk, không cần save thêm
```

**Cách lưu trữ trong Qdrant:**
```
Collection: "hotels"
├── Point ID: hotel_id (hoặc chunk_id)
├── Vector: embedding vector (1024 dims cho BGE-M3)
└── Payload: metadata (hotel_id, hotel_name, etc.)
```

### **4.2 Chroma**

**Setup:**
```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# 1. Initialize embeddings
embeddings = OllamaEmbeddings(model="bge-m3")

# 2. Create documents
documents = [...]  # Same as above

# 3. Store in Chroma
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./chroma_db"  # Persistent storage
)

# 4. Load later
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
```

**Cách lưu trữ:**
```
./chroma_db/
├── chroma.sqlite3          # SQLite database
├── index/                  # Index files
└── data/                   # Data files
```

### **4.3 FAISS (In-Memory - Không Khuyến Nghị)**

**Setup:**
```python
from langchain_community.vectorstores import FAISS

# Store in memory
vectorstore = FAISS.from_documents(
    documents=documents,
    embedding=embeddings
)

# Save to disk
vectorstore.save_local("./faiss_index")

# Load from disk
vectorstore = FAISS.load_local(
    "./faiss_index",
    embeddings=embeddings
)
```

**Cách lưu trữ:**
```
./faiss_index/
├── index.faiss              # FAISS index
└── index.pkl                # Metadata
```

---

## 📊 **5. KHUYẾN NGHỊ CHO DATASET KHÁCH SẠN**

### **5.1 Chọn Vector Database**

**✅ Qdrant (Khuyến Nghị):**
- Bạn đã có Qdrant setup
- Hỗ trợ metadata filtering tốt
- Persistent storage
- LangChain integration tốt

### **5.2 Chunking Strategy**

**✅ Option 1: Mỗi Hotel = 1 Chunk (Khuyến Nghị)**

**Lý do:**
- Dataset của bạn có ~24 hotels
- Hotel descriptions không quá dài (<512 tokens)
- Đơn giản, dễ maintain

**Cấu trúc:**
```python
# Mỗi hotel = 1 document/chunk
document = Document(
    page_content=f"""
    Tên: {hotel_name}
    Mô tả: {hotel_desc}
    Địa chỉ: {hotel_placedetails}
    Khu vực: {area_name}
    Thương hiệu: {brand_name}
    Từ khóa: {hotel_tag_keyword}
    Hạng: {hotel_rank} sao
    Giá trung bình: {hotel_price_average} VND
    """,
    metadata={
        "hotel_id": hotel_id,
        "hotel_name": hotel_name,
        "area_id": area_id,
        "brand_id": brand_id,
        "hotel_rank": hotel_rank,
        "hotel_price_average": hotel_price_average,
        "chunk_type": "full_hotel"
    }
)
```

**✅ Option 2: Nhiều Chunks (Nếu cần chi tiết hơn)**

**Chia thành:**
- Chunk 0: Basic info (name, address, rank)
- Chunk 1: Description
- Chunk 2: Room info (join với tbl_room)
- Chunk 3: Price info (join với tbl_type_room)

**Lý do:**
- Nếu muốn tìm kiếm chi tiết hơn (ví dụ: "phòng view biển")
- Nếu description dài

### **5.3 Metadata Strategy**

**Lưu metadata quan trọng:**
```python
metadata = {
    # Primary keys
    "hotel_id": hotel_id,
    "hotel_name": hotel_name,
    
    # For filtering
    "area_id": area_id,
    "brand_id": brand_id,
    "hotel_rank": hotel_rank,
    "hotel_price_average": hotel_price_average,
    
    # For chunking
    "chunk_index": 0,
    "chunk_type": "full_hotel",
    
    # For joining
    "source": "tbl_hotel.csv"
}
```

**Lý do:**
- Metadata filtering: Filter by area_id, brand_id, rank
- Price filtering: Filter by price range
- Chunk management: Join chunks của cùng hotel

---

## 🔧 **6. IMPLEMENTATION VỚI LANGCHAIN**

### **6.1 Complete Example**

```python
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document
import pandas as pd

# 1. Load data
hotels_df = pd.read_csv("datasets_extracted/tbl_hotel.csv")
rooms_df = pd.read_csv("datasets_extracted/tbl_room.csv")
areas_df = pd.read_csv("datasets_extracted/tbl_area.csv")
brands_df = pd.read_csv("datasets_extracted/tbl_brand.csv")

# 2. Join tables
hotels_df = hotels_df.merge(areas_df, on="area_id", how="left")
hotels_df = hotels_df.merge(brands_df, on="brand_id", how="left")

# 3. Initialize embeddings
embeddings = OllamaEmbeddings(
    model="bge-m3",
    base_url="http://localhost:11434"
)

# 4. Create documents
documents = []
for _, hotel in hotels_df.iterrows():
    # Combine text
    text_parts = []
    if pd.notna(hotel.get("hotel_name")):
        text_parts.append(f"Tên: {hotel['hotel_name']}")
    if pd.notna(hotel.get("hotel_desc")):
        text_parts.append(f"Mô tả: {hotel['hotel_desc']}")
    if pd.notna(hotel.get("hotel_placedetails")):
        text_parts.append(f"Địa chỉ: {hotel['hotel_placedetails']}")
    if pd.notna(hotel.get("area_name")):
        text_parts.append(f"Khu vực: {hotel['area_name']}")
    if pd.notna(hotel.get("brand_name")):
        text_parts.append(f"Thương hiệu: {hotel['brand_name']}")
    if pd.notna(hotel.get("hotel_tag_keyword")):
        text_parts.append(f"Từ khóa: {hotel['hotel_tag_keyword']}")
    if pd.notna(hotel.get("hotel_rank")):
        text_parts.append(f"Hạng: {hotel['hotel_rank']} sao")
    if pd.notna(hotel.get("hotel_price_average")):
        text_parts.append(f"Giá trung bình: {hotel['hotel_price_average']} VND")
    
    text = " | ".join(text_parts)
    
    # Create document
    doc = Document(
        page_content=text,
        metadata={
            "hotel_id": int(hotel["hotel_id"]),
            "hotel_name": str(hotel.get("hotel_name", "")),
            "area_id": int(hotel["area_id"]) if pd.notna(hotel.get("area_id")) else None,
            "brand_id": int(hotel["brand_id"]) if pd.notna(hotel.get("brand_id")) else None,
            "hotel_rank": int(hotel["hotel_rank"]) if pd.notna(hotel.get("hotel_rank")) else None,
            "hotel_price_average": float(hotel["hotel_price_average"]) if pd.notna(hotel.get("hotel_price_average")) else None,
            "chunk_type": "full_hotel",
            "source": "tbl_hotel.csv"
        }
    )
    documents.append(doc)

# 5. Store in Qdrant
vectorstore = Qdrant.from_documents(
    documents=documents,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="hotels",
    prefer_grpc=True
)

print(f"Stored {len(documents)} hotels in Qdrant")
```

### **6.2 Query với Metadata Filtering**

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

# Query với filter
results = vectorstore.similarity_search(
    "Khách sạn 5 sao gần biển",
    k=10,
    filter=Filter(
        must=[
            FieldCondition(key="hotel_rank", match=MatchValue(value=5)),
            FieldCondition(key="area_id", match=MatchValue(value=8))
        ]
    )
)
```

---

## 💾 **7. PERSISTENT STORAGE**

### **7.1 Qdrant (Tự Động Persistent)**

**Qdrant tự động lưu:**
- Vectors và metadata vào disk
- Không cần save thêm
- Restart không mất data

**Storage location:**
```
# Qdrant data directory (default)
./qdrant_storage/
├── collections/
│   └── hotels/
│       ├── payload/
│       ├── vectors/
│       └── index/
```

### **7.2 Chroma (Cần Specify Path)**

```python
# Specify persist directory
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./chroma_db"  # Persistent
)

# Load later
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
```

### **7.3 FAISS (Cần Save/Load)**

```python
# Save
vectorstore.save_local("./faiss_index")

# Load
vectorstore = FAISS.load_local(
    "./faiss_index",
    embeddings=embeddings
)
```

---

## ✅ **8. KHUYẾN NGHỊ CUỐI CÙNG**

### **Cho Dataset Khách Sạn Của Bạn:**

**✅ Vector Database: Qdrant**
- Bạn đã có
- Persistent storage
- Metadata filtering tốt

**✅ Chunking Strategy: Mỗi Hotel = 1 Chunk**
- Dataset nhỏ (~24 hotels)
- Descriptions không quá dài
- Đơn giản, dễ maintain

**✅ Metadata: Đầy Đủ**
- hotel_id, hotel_name
- area_id, brand_id
- hotel_rank, hotel_price_average
- chunk_type, source

**✅ Storage: Persistent**
- Qdrant tự động persistent
- Không mất data khi restart

### **Workflow:**

```
1. Load CSV files
2. Join tables (hotel, area, brand)
3. Create documents (1 document = 1 hotel)
4. Embed documents
5. Store in Qdrant (persistent)
6. Query với metadata filtering
```

---

## 📚 **9. TÀI LIỆU THAM KHẢO**

- Qdrant: https://qdrant.tech/documentation/
- LangChain Vector Stores: https://python.langchain.com/docs/integrations/vectorstores/
- Chroma: https://docs.trychroma.com/
- Milvus: https://milvus.io/docs

---

**TL;DR: Dùng Qdrant (bạn đã có) để lưu chunks. Mỗi hotel = 1 chunk. Lưu đầy đủ metadata. Qdrant tự động persistent.**

