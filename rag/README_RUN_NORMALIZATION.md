# Hướng Dẫn Chạy Hotel Data Normalization

## 🚀 Cách Chạy

### **Option 1: Sử dụng Script (Khuyến Nghị)**

```bash
cd rag
./run_normalization.sh
```

### **Option 2: Chạy Trực Tiếp với Python**

```bash
# Từ folder rag/
cd rag
python3 hotel_data_normalization.py

# Hoặc từ project root
python3 rag/hotel_data_normalization.py
```

### **Option 3: Chạy với Virtual Environment**

```bash
# Activate virtual environment
source venv/bin/activate  # hoặc source ../venv/bin/activate

# Chạy script
cd rag
python3 hotel_data_normalization.py
```

---

## 📋 Requirements

### **Python Packages**

```bash
pip install pandas numpy
```

Hoặc nếu có requirements file:
```bash
pip install -r requirements_rag.txt
```

### **Dependencies**

- `pandas`: Data processing
- `numpy`: Numerical operations
- `json`: JSON handling (built-in)
- `re`: Regular expressions (built-in)
- `difflib`: Similarity calculation (built-in)

---

## 📁 Input Files

Script cần các file sau trong `datasets_extracted/`:

- `tbl_hotel.csv` - Hotel data
- `tbl_area.csv` - Area data
- `tbl_brand.csv` - Brand data

---

## 📊 Output Files

Sau khi chạy, các file sau sẽ được tạo trong `rag/normalized_data/`:

1. **normalized_hotels.csv**
   - Hotels đã chuẩn hóa với semantic text
   - Có thêm columns: `semantic_text`, `normalized_name`, `price_category`, `extracted_area`

2. **hotel_similarity_map.json**
   - Map các hotels tương đồng với nhau
   - Format: `{hotel_id: [(similar_hotel_id, similarity_score), ...]}`

3. **semantic_clusters.json**
   - Clusters của hotels tương đồng
   - Format: `{cluster_id: [hotel_id1, hotel_id2, ...]}`

---

## 🔍 Ví Dụ Output

### **normalized_hotels.csv**

```csv
hotel_id,hotel_name,semantic_text,normalized_name,price_category,extracted_area
2,"Meliá Vinpearl Riverfront","Tên: Meliá Vinpearl Riverfront | Tên chuẩn hóa: meliá vinpearl riverfront | Mô tả: ... | ...","meliá vinpearl riverfront","giá cao","Sơn Trà"
```

### **hotel_similarity_map.json**

```json
{
  "2": [
    ["3", 0.65],
    ["4", 0.52]
  ],
  "3": [
    ["2", 0.65],
    ["5", 0.48]
  ]
}
```

### **semantic_clusters.json**

```json
{
  "0": [2, 3, 4],
  "1": [5, 6],
  "2": [7]
}
```

---

## ⚙️ Configuration

### **Similarity Threshold**

Có thể điều chỉnh trong code:

```python
# Find similar hotels (threshold: 0.3)
similarities = normalizer.find_similar_hotels(hotels_df, similarity_threshold=0.3)

# Create clusters (threshold: 0.4)
clusters = normalizer.create_semantic_clusters(hotels_df, similarity_threshold=0.4)
```

### **Price Categories**

Có thể điều chỉnh trong `_categorize_price()` method:

```python
def _categorize_price(self, price: float) -> str:
    if price < 1000000:
        return "giá rẻ"
    elif price < 2000000:
        return "giá trung bình"
    elif price < 3000000:
        return "giá cao"
    else:
        return "giá rất cao"
```

---

## 🐛 Troubleshooting

### **Lỗi: File not found**

```
FileNotFoundError: [Errno 2] No such file or directory: '../datasets_extracted/tbl_hotel.csv'
```

**Giải pháp:**
- Đảm bảo chạy từ folder `rag/`
- Hoặc kiểm tra path đến `datasets_extracted/`

### **Lỗi: Missing dependencies**

```
ModuleNotFoundError: No module named 'pandas'
```

**Giải pháp:**
```bash
pip install pandas numpy
```

### **Lỗi: Permission denied**

```
PermissionError: [Errno 13] Permission denied
```

**Giải pháp:**
```bash
# Tạo folder output
mkdir -p rag/normalized_data

# Hoặc check permissions
chmod 755 rag/normalized_data
```

---

## ✅ Checklist

- [ ] Python 3 installed
- [ ] Dependencies installed (pandas, numpy)
- [ ] Data files exist (`datasets_extracted/tbl_hotel.csv`, etc.)
- [ ] Output directory exists or will be created
- [ ] Script has execute permission (if using shell script)

---

## 📝 Quick Command

```bash
# One-liner
cd rag && python3 hotel_data_normalization.py
```

---

**TL;DR**: `cd rag && python3 hotel_data_normalization.py` hoặc `./run_normalization.sh`

