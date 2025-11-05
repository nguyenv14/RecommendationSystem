# HƯỚNG DẪN CHUẨN HÓA DỮ LIỆU VÀ MAP HOTELS

## 📋 Tổng Quan

Tài liệu này mô tả phương pháp chuẩn hóa dữ liệu khách sạn và map các hotels có ngữ nghĩa tương đồng để cải thiện chất lượng tìm kiếm semantic.

---

## 🎯 **1. TẠI SAO CẦN CHUẨN HÓA DỮ LIỆU?**

### **1.1 Vấn Đề**

Khi tìm kiếm semantic, các vấn đề sau có thể xảy ra:

- ❌ "Khách sạn gần biển" không match với "Khách sạn ven biển Mỹ Khê"
- ❌ "Khách sạn 5 sao" không match với "Khách sạn luxury cao cấp"
- ❌ "Giá rẻ" không match với "Giá tốt" hoặc "Giá hợp lý"
- ❌ "Sơn Trà" không match với "Son Tra" hoặc "quận Sơn Trà"

### **1.2 Giải Pháp: Chuẩn Hóa Dữ Liệu**

Chuẩn hóa dữ liệu giúp:
- ✅ Map các từ đồng nghĩa với nhau
- ✅ Normalize text (loại bỏ accents, lowercase)
- ✅ Enrich context với synonyms
- ✅ Tạo semantic clusters
- ✅ Map hotels tương đồng

---

## 🔧 **2. PHƯƠNG PHÁP CHUẨN HÓA**

### **2.1 Text Normalization**

**Chuẩn hóa text:**
- Loại bỏ khoảng trắng thừa
- Convert to lowercase
- (Optional) Loại bỏ accents
- Chuẩn hóa ký tự đặc biệt

**Ví dụ:**
```
"Khách Sạn 5 Sao" → "khách sạn 5 sao"
"Sơn Trà" → "sơn trà"
```

### **2.2 Synonym Expansion**

**Tạo synonym mappings:**

```python
synonym_mappings = {
    "gần biển": ["ven biển", "sát biển", "cách biển", "view biển", "hướng biển"],
    "5 sao": ["5 sao", "năm sao", "luxury", "cao cấp", "sang trọng"],
    "giá rẻ": ["giá rẻ", "giá tốt", "giá hợp lý", "giá phải chăng"],
    "Sơn Trà": ["Sơn Trà", "Son Tra", "quận Sơn Trà"],
    "Mỹ Khê": ["Mỹ Khê", "My Khe", "bãi biển Mỹ Khê"],
}
```

**Expand text:**
```
"Khách sạn gần biển" 
→ "Khách sạn gần biển ven biển sát biển cách biển view biển hướng biển"
```

### **2.3 Context Enrichment**

**Enrich hotel text với metadata:**

```
Original: "Meliá Vinpearl Riverfront | Mô tả: ..."

Enriched:
"Tên: Meliá Vinpearl Riverfront | 
Tên chuẩn hóa: meliá vinpearl riverfront | 
Mô tả: ... | 
Mô tả mở rộng: ... ven biển sát biển ... | 
Địa chỉ: ... | 
Khu vực: Sơn Trà | 
Khu vực mở rộng: Son Tra quận Sơn Trà | 
Hạng: 5 sao | 
Hạng mở rộng: luxury cao cấp sang trọng | 
Phân loại giá: giá cao"
```

### **2.4 Semantic Similarity Calculation**

**Tính similarity giữa hotels:**

```python
def calculate_similarity(text1, text2):
    # Normalize both texts
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    # SequenceMatcher similarity
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    
    # Jaccard similarity (common words)
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    jaccard = len(words1.intersection(words2)) / len(words1.union(words2))
    
    # Combined similarity
    combined = (similarity * 0.6) + (jaccard * 0.4)
    
    return combined
```

### **2.5 Semantic Clustering**

**Tạo clusters của hotels tương đồng:**

```
Cluster 0: [Hotel 2, Hotel 3]  # Similar hotels
Cluster 1: [Hotel 4, Hotel 5]  # Similar hotels
Cluster 2: [Hotel 6]           # Single hotel
...
```

---

## 📊 **3. CẤU TRÚC DỮ LIỆU SAU CHUẨN HÓA**

### **3.1 Normalized Hotel Data**

**Mỗi hotel sau khi chuẩn hóa:**

```json
{
    "hotel_id": 2,
    "hotel_name": "Meliá Vinpearl Riverfront",
    "normalized_name": "meliá vinpearl riverfront",
    "semantic_text": "Tên: Meliá Vinpearl Riverfront | Tên chuẩn hóa: ... | Mô tả: ... | ...",
    "price_category": "giá cao",
    "extracted_area": "Sơn Trà",
    "similar_hotels": [
        {"hotel_id": 3, "similarity": 0.65},
        {"hotel_id": 4, "similarity": 0.52}
    ],
    "cluster_id": 0
}
```

### **3.2 Similarity Map**

**Map hotels tương đồng:**

```json
{
    "2": [
        {"hotel_id": 3, "similarity": 0.65},
        {"hotel_id": 4, "similarity": 0.52}
    ],
    "3": [
        {"hotel_id": 2, "similarity": 0.65},
        {"hotel_id": 5, "similarity": 0.48}
    ]
}
```

### **3.3 Semantic Clusters**

**Clusters của hotels:**

```json
{
    "0": [2, 3, 4],
    "1": [5, 6],
    "2": [7]
}
```

---

## 🔍 **4. CÁC BƯỚC CHUẨN HÓA**

### **Bước 1: Load Data**

```python
hotels_df = pd.read_csv("tbl_hotel.csv")
areas_df = pd.read_csv("tbl_area.csv")
brands_df = pd.read_csv("tbl_brand.csv")

# Join tables
hotels_df = hotels_df.merge(areas_df, on="area_id")
hotels_df = hotels_df.merge(brands_df, on="brand_id")
```

### **Bước 2: Normalize Text**

```python
# Normalize hotel names
hotels_df["normalized_name"] = hotels_df["hotel_name"].apply(normalize_text)

# Normalize descriptions
hotels_df["normalized_desc"] = hotels_df["hotel_desc"].apply(normalize_text)
```

### **Bước 3: Expand Synonyms**

```python
# Expand descriptions with synonyms
hotels_df["expanded_desc"] = hotels_df["hotel_desc"].apply(expand_synonyms)
```

### **Bước 4: Create Semantic Text**

```python
# Create enriched semantic text
hotels_df["semantic_text"] = hotels_df.apply(create_semantic_text, axis=1)
```

### **Bước 5: Find Similar Hotels**

```python
# Calculate similarities
similarities = find_similar_hotels(hotels_df, threshold=0.3)
```

### **Bước 6: Create Clusters**

```python
# Create semantic clusters
clusters = create_semantic_clusters(hotels_df, threshold=0.4)
```

### **Bước 7: Save Results**

```python
# Save normalized data
normalized_df.to_csv("normalized_hotels.csv")

# Save mappings
save_mappings("normalized_data/")
```

---

## 💡 **5. VÍ DỤ CỤ THỂ**

### **5.1 Hotel Example**

**Original Hotel:**
```
Hotel ID: 2
Name: "Meliá Vinpearl Riverfront"
Description: "Khách sạn 5 sao cao cấp tọa lạc tại 341 Trần Hưng Đạo, Quận Sơn Trà, Đà Nẵng..."
Address: "341, Trần Hưng Đạo, Quận Sơn Trà, Đà Nẵng"
Area: "Sơn Trà"
Rank: 5
Price: 1,311,127 VND
```

**Normalized Hotel:**
```
Hotel ID: 2
Normalized Name: "meliá vinpearl riverfront"
Semantic Text: "Tên: Meliá Vinpearl Riverfront | Tên chuẩn hóa: meliá vinpearl riverfront | 
Mô tả: Khách sạn 5 sao cao cấp... | 
Mô tả mở rộng: Khách sạn 5 sao năm sao luxury cao cấp sang trọng... ven biển sát biển... | 
Địa chỉ: 341, Trần Hưng Đạo, Quận Sơn Trà... | 
Khu vực trích xuất: Sơn Trà | 
Khu vực: Sơn Trà | 
Khu vực mở rộng: Son Tra quận Sơn Trà | 
Hạng: 5 sao | 
Hạng mở rộng: luxury cao cấp sang trọng | 
Giá trung bình: 1,311,127 VND | 
Phân loại giá: giá cao"
Price Category: "giá cao"
Extracted Area: "Sơn Trà"
```

### **5.2 Similar Hotels**

**Hotel 2 tương đồng với:**
```
Hotel 3: Mường Thanh Luxury (similarity: 0.65)
- Cùng 5 sao
- Cùng ven biển
- Cùng Sơn Trà area

Hotel 4: Sheraton Grand Resort (similarity: 0.52)
- Cùng 5 sao
- Cùng ven biển
- Cùng Ngũ Hành Sơn area
```

### **5.3 Semantic Cluster**

**Cluster 0: Luxury Beach Hotels**
```
- Hotel 2: Meliá Vinpearl Riverfront
- Hotel 3: Mường Thanh Luxury
- Hotel 4: Sheraton Grand Resort
```

---

## 🚀 **6. SỬ DỤNG TRONG RAG**

### **6.1 Index với Normalized Data**

**Khi index vào Qdrant:**

```python
# Use normalized semantic text for embedding
for hotel in normalized_df:
    document = Document(
        page_content=hotel["semantic_text"],  # Enriched text
        metadata={
            "hotel_id": hotel["hotel_id"],
            "hotel_name": hotel["hotel_name"],
            "normalized_name": hotel["normalized_name"],
            "price_category": hotel["price_category"],
            "cluster_id": hotel["cluster_id"]
        }
    )
    documents.append(document)
```

### **6.2 Query với Normalization**

**Khi query:**

```python
# Normalize query
normalized_query = normalize_text(query)

# Expand query with synonyms
expanded_query = expand_synonyms(query)

# Search with both
results = vectorstore.similarity_search(expanded_query)
```

### **6.3 Use Similar Hotels**

**Khi retrieve:**

```python
# Get similar hotels from mapping
similar_hotels = similarity_map[hotel_id]

# Include similar hotels in results
for similar_id, sim_score in similar_hotels:
    if sim_score > 0.5:
        # Add to recommendations
        recommendations.append(similar_id)
```

---

## 📈 **7. LỢI ÍCH**

### **7.1 Cải Thiện Tìm Kiếm**

- ✅ "Gần biển" → Match với "ven biển", "sát biển"
- ✅ "5 sao" → Match với "luxury", "cao cấp"
- ✅ "Giá rẻ" → Match với "giá tốt", "giá hợp lý"

### **7.2 Tăng Độ Chính Xác**

- ✅ Tìm kiếm semantic chính xác hơn
- ✅ Map hotels tương đồng tốt hơn
- ✅ Clustering hotels hợp lý hơn

### **7.3 Enrich Context**

- ✅ Thêm synonyms vào text
- ✅ Extract features (area, price category)
- ✅ Normalize text cho consistency

---

## ✅ **8. KẾT LUẬN**

**Chuẩn hóa dữ liệu giúp:**
1. ✅ Map synonyms với nhau
2. ✅ Normalize text cho consistency
3. ✅ Enrich context với metadata
4. ✅ Find similar hotels
5. ✅ Create semantic clusters

**Sử dụng trong RAG:**
- Index với normalized semantic text
- Query với normalized + expanded query
- Use similarity map để recommend

**Kết quả:**
- Tìm kiếm chính xác hơn
- Map hotels tương đồng tốt hơn
- Semantic search tốt hơn

---

**TL;DR: Chuẩn hóa dữ liệu = Normalize text + Expand synonyms + Enrich context + Find similar hotels + Create clusters**

