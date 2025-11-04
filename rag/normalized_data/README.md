# NORMALIZED DATA - GIẢI THÍCH

## 📋 Tổng Quan

Folder `normalized_data` chứa **dữ liệu đã được chuẩn hóa và map lại dạng text** để embedding model có thể đọc và hiểu ngữ nghĩa tốt hơn.

---

## ✅ **ĐÚNG RỒI! ĐÂY LÀ DATA ĐÃ MAP LẠI DẠNG TEXT ĐỂ EMBEDDING ĐỌC**

### **1. normalized_hotels.csv**

**File này chứa hotels đã được chuẩn hóa với column quan trọng:**

#### **Column `semantic_text` - Đây chính là text để embedding đọc!**

**Cấu trúc `semantic_text`:**
```
Tên khách sạn: {hotel_name} | 
Tên chuẩn hóa: {normalized_name} | 
Mô tả: {original_desc} | 
Mô tả mở rộng: {expanded_desc với synonyms} | 
Địa chỉ: {address} | 
Khu vực trích xuất: {area} | 
Khu vực: {area_name} | 
Khu vực mở rộng: {area_synonyms} | 
Thương hiệu: {brand_name} | 
Từ khóa: {keywords} | 
Từ khóa mở rộng: {expanded_keywords với synonyms} | 
Hạng: {rank} sao | 
Hạng mở rộng: {rank_synonyms} | 
Giá trung bình: {price} VND | 
Phân loại giá: {price_category}
```

**Ví dụ thực tế (Hotel ID 2):**
```
Tên khách sạn: Meliá Vinpearl Riverfront | 
Tên chuẩn hóa: meliá vinpearl riverfront | 
Mô tả: Meliá Vinpearl Riverfront Đà Nẵng là khách sạn 5 sao cao cấp... | 
Mô tả mở rộng: ... 5 sao năm sao 5 stars luxury cao cấp sang trọng hồ bơi bể bơi pool swimming pool spa massage thư giãn gym phòng gym thể hình fitness nhà hàng restaurant quán ăn | 
Địa chỉ: 341, Trần Hưng Đạo, Quận Sơn Trà... | 
Khu vực trích xuất: Sơn Trà | 
Khu vực: Sơn Trà | 
Khu vực mở rộng: Sơn Trà Son Tra quận Sơn Trà | 
Thương hiệu: Furama | 
Từ khóa: Khách Sạn Đà Nẵng , Khách Sạn Căn Hộ , Khách Sạn 5 Sao , Furama | 
Từ khóa mở rộng: ... 5 sao năm sao 5 stars luxury cao cấp sang trọng | 
Hạng: 5 sao | 
Hạng mở rộng: luxury cao cấp sang trọng | 
Giá trung bình: 1,311,127 VND | 
Phân loại giá: giá trung bình
```

**Tại sao cần `semantic_text`?**
- ✅ **Embedding đọc text này** để tạo vector
- ✅ **Đã được expand với synonyms** → "5 sao" → "luxury cao cấp sang trọng"
- ✅ **Đã được normalize** → lowercase, consistent format
- ✅ **Đã được enrich** → thêm metadata, area, brand, price category

#### **Các columns khác:**

- `normalized_name`: Tên đã normalize (lowercase)
- `price_category`: Phân loại giá (giá rẻ, giá trung bình, giá cao, giá rất cao)
- `extracted_area`: Khu vực trích xuất từ địa chỉ

---

### **2. hotel_similarity_map.json**

**File này map các hotels có ngữ nghĩa tương đồng với nhau.**

**Format:**
```json
{
  "hotel_id": [
    ["similar_hotel_id", similarity_score],
    ...
  ]
}
```

**Ví dụ:**
```json
{
  "2": [
    ["6", 0.338],
    ["5", 0.306],
    ["8", 0.302]
  ],
  "5": [
    ["7", 0.428],
    ["8", 0.378],
    ["11", 0.334]
  ]
}
```

**Ý nghĩa:**
- Hotel 2 tương đồng với Hotel 6 (similarity: 0.338)
- Hotel 5 tương đồng với Hotel 7 (similarity: 0.428)
- Có thể dùng để recommend hotels tương đồng

---

### **3. semantic_clusters.json**

**File này chứa clusters của hotels tương đồng.**

**Format:**
```json
{
  "cluster_id": [hotel_id1, hotel_id2, ...]
}
```

**Ví dụ:**
```json
{
  "0": [5, 7],    # Cluster 0: Hotels 5 và 7 tương đồng
  "1": [8, 14],   # Cluster 1: Hotels 8 và 14 tương đồng
  "2": [11]       # Cluster 2: Hotel 11 đơn lẻ
}
```

**Ý nghĩa:**
- Hotels trong cùng cluster có ngữ nghĩa tương đồng
- Có thể dùng để group hotels tương tự

---

## 🔄 **QUY TRÌNH SỬ DỤNG**

### **Bước 1: Load normalized data**

```python
import pandas as pd

# Load normalized hotels
normalized_df = pd.read_csv("rag/normalized_data/normalized_hotels.csv")

# Lấy semantic_text để embedding
for idx, hotel in normalized_df.iterrows():
    semantic_text = hotel["semantic_text"]  # Đây là text để embedding đọc!
    hotel_id = hotel["hotel_id"]
```

### **Bước 2: Embed semantic_text**

```python
from langchain_community.embeddings import OllamaEmbeddings

# Initialize embeddings
embeddings = OllamaEmbeddings(model="bge-m3")

# Embed semantic_text
semantic_texts = normalized_df["semantic_text"].tolist()
vectors = embeddings.embed_documents(semantic_texts)
```

### **Bước 3: Store in Qdrant**

```python
from langchain_community.vectorstores import Qdrant
from langchain.schema import Document

# Create documents với semantic_text
documents = []
for idx, hotel in normalized_df.iterrows():
    doc = Document(
        page_content=hotel["semantic_text"],  # Embedding đọc text này!
        metadata={
            "hotel_id": hotel["hotel_id"],
            "hotel_name": hotel["hotel_name"],
            "normalized_name": hotel["normalized_name"],
            "price_category": hotel["price_category"],
            "extracted_area": hotel["extracted_area"]
        }
    )
    documents.append(doc)

# Store in Qdrant
vectorstore = Qdrant.from_documents(
    documents=documents,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="hotels"
)
```

### **Bước 4: Use similarity map (optional)**

```python
import json

# Load similarity map
with open("rag/normalized_data/hotel_similarity_map.json") as f:
    similarity_map = json.load(f)

# Get similar hotels
hotel_id = "2"
similar_hotels = similarity_map.get(hotel_id, [])
print(f"Hotels similar to {hotel_id}: {similar_hotels}")
```

---

## 💡 **TẠI SAO CẦN NORMALIZE?**

### **Vấn đề với data gốc:**

```
"Khách sạn gần biển" → Embedding không match với "Khách sạn ven biển"
"5 sao" → Embedding không match với "luxury"
"Giá rẻ" → Embedding không match với "giá tốt"
```

### **Sau khi normalize:**

```
"Khách sạn gần biển ven biển sát biển cách biển view biển hướng biển" 
→ Embedding match tốt hơn!

"5 sao năm sao 5 stars luxury cao cấp sang trọng" 
→ Embedding hiểu được nhiều cách diễn đạt!

"Giá rẻ giá tốt giá hợp lý giá phải chăng" 
→ Embedding match với nhiều query hơn!
```

---

## 📊 **SO SÁNH: DATA GỐC vs NORMALIZED DATA**

### **Data Gốc:**
```
hotel_name: "Meliá Vinpearl Riverfront"
hotel_desc: "Khách sạn 5 sao cao cấp..."
hotel_tag_keyword: "Khách Sạn Đà Nẵng , Khách Sạn 5 Sao"
```

**Vấn đề:**
- ❌ Không có synonyms
- ❌ Không có normalized text
- ❌ Không có expanded keywords
- ❌ Embedding có thể không hiểu đúng

### **Normalized Data:**
```
semantic_text: "Tên khách sạn: Meliá Vinpearl Riverfront | 
Tên chuẩn hóa: meliá vinpearl riverfront | 
Mô tả: ... | 
Mô tả mở rộng: ... 5 sao năm sao 5 stars luxury cao cấp sang trọng ... | 
Từ khóa mở rộng: ... 5 sao năm sao 5 stars luxury cao cấp sang trọng | 
Hạng mở rộng: luxury cao cấp sang trọng | ..."
```

**Ưu điểm:**
- ✅ Có synonyms (5 sao → luxury cao cấp sang trọng)
- ✅ Có normalized text (lowercase, consistent)
- ✅ Có expanded keywords
- ✅ Embedding hiểu đúng ngữ nghĩa

---

## ✅ **KẾT LUẬN**

**Câu trả lời:**
- ✅ **Đúng rồi!** Đây là data đã được map lại dạng text để embedding đọc
- ✅ **Column `semantic_text`** chứa toàn bộ thông tin đã được:
  - Normalize (lowercase, consistent format)
  - Expand với synonyms ("5 sao" → "luxury cao cấp sang trọng")
  - Enrich với metadata (area, brand, price category)
- ✅ **Embedding đọc `semantic_text`** để tạo vector
- ✅ **Tìm kiếm chính xác hơn** vì có nhiều synonyms và context

**Sử dụng:**
```python
# Dùng semantic_text để embedding
semantic_text = normalized_df["semantic_text"][0]
vector = embedding_model.encode(semantic_text)
```

---

**TL;DR: `semantic_text` column chứa text đã được normalize + expand synonyms + enrich context → Embedding đọc text này để tạo vector → Tìm kiếm chính xác hơn!**

