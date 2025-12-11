# Structured Chunking - Chunking theo Format có Cấu trúc

## Tổng quan

`StructuredChunker` là một phương pháp chunking thông minh dành cho dữ liệu có format có cấu trúc (ví dụ: 1. Giới thiệu, 2. Tiện ích, 3. Vị trí, 4. Điểm nổi bật, 5. Summary).

## Lợi ích của Structured Chunking

### 1. **Ngữ nghĩa hoàn chỉnh**
- Mỗi chunk đại diện cho một phần thông tin hoàn chỉnh (introduction, amenities, location, etc.)
- Không bị cắt giữa chừng như chunking theo kích thước cố định
- Dễ dàng hiểu context của từng chunk

### 2. **Metadata phong phú**
- Mỗi chunk có metadata về `section_type` (introduction, amenities, location, highlights, summary)
- Có thể filter/search theo section type
- Biết được chunk thuộc section nào và vị trí của nó

### 3. **Tìm kiếm chính xác hơn**
- Khi user hỏi về "tiện ích", có thể tìm trực tiếp trong chunks có `section_type="amenities"`
- Giảm noise từ các section không liên quan
- Cải thiện precision trong retrieval

### 4. **Giảm số lượng chunks**
- Với format có cấu trúc, thay vì chia thành nhiều chunks nhỏ, mỗi section = 1 chunk
- Giảm overhead trong vector storage và retrieval
- Dễ quản lý và maintain

## So sánh với SmartChunker

### SmartChunker (chunking theo kích thước)
```
Text: 2000 ký tự
→ Chia thành 3 chunks (800, 800, 400 ký tự)
→ Mỗi chunk không có ngữ nghĩa rõ ràng
→ Khó biết chunk chứa thông tin gì
```

### StructuredChunker (chunking theo format)
```
Text: 2000 ký tự với 5 sections
→ Chia thành 5 chunks (mỗi section = 1 chunk)
→ Mỗi chunk có ngữ nghĩa rõ ràng (introduction, amenities, etc.)
→ Dễ dàng filter và tìm kiếm
```

## Cách sử dụng

### 1. Khởi tạo StructuredChunker

```python
from chunker import StructuredChunker

# Khởi tạo với max_section_size (nếu section quá dài sẽ chia nhỏ)
chunker = StructuredChunker(max_section_size=1500)
```

### 2. Chunk hotel document

```python
hotel_data = {
    "hotel_id": 1,
    "hotel_name": "Meliá Vinpearl Riverfront Đà Nẵng",
    "hotel_rank": 5,
    # ... other metadata
}

semantic_text = """
1. Giới thiệu tổng quan – Meliá Vinpearl Riverfront Đà Nẵng
Meliá Vinpearl Riverfront Đà Nẵng là khách sạn 5 sao...

2. Tiện ích & Dịch vụ – Meliá Vinpearl Riverfront Đà Nẵng
Meliá Vinpearl Riverfront Đà Nẵng cung cấp hệ thống tiện ích...
"""

documents = chunker.chunk_hotel_document(hotel_data, semantic_text)
```

### 3. Metadata của mỗi chunk

```python
for doc in documents:
    print(f"Section: {doc.metadata['section_number']}")
    print(f"Type: {doc.metadata['section_type']}")  # introduction, amenities, location, etc.
    print(f"Title: {doc.metadata['section_title']}")
    print(f"Content: {doc.page_content}")
```

## Section Type Mapping

| Section Number | Section Type | Mô tả |
|---------------|--------------|-------|
| 1 | `introduction` | Giới thiệu tổng quan |
| 2 | `amenities` | Tiện ích & Dịch vụ |
| 3 | `location` | Vị trí & kết nối |
| 4 | `highlights` | Điểm nổi bật |
| 5 | `summary` | Short Summary |

## Format được hỗ trợ

### Format 1: Số + dấu chấm
```
1. Giới thiệu tổng quan
Nội dung section 1...

2. Tiện ích & Dịch vụ
Nội dung section 2...
```

### Format 2: Số + dấu ngoặc
```
1) Giới thiệu tổng quan
Nội dung section 1...

2) Tiện ích & Dịch vụ
Nội dung section 2...
```

### Format 3: Keyword-based (fallback)
Nếu không tìm thấy số, sẽ detect bằng keywords:
- "Giới thiệu", "Tổng quan" → `introduction`
- "Tiện ích", "Dịch vụ" → `amenities`
- "Vị trí", "Kết nối" → `location`
- "Điểm nổi bật" → `highlights`
- "Summary", "Tóm tắt" → `summary`

## Xử lý Section quá dài

Nếu một section vượt quá `max_section_size`, nó sẽ được chia nhỏ bằng `SmartChunker`:

```python
# Section 2 có 2000 ký tự > max_section_size (1500)
# → Chia thành 2 sub-chunks

doc.metadata['is_sub_chunked'] = True
doc.metadata['sub_chunk_index'] = 0  # hoặc 1
doc.metadata['total_sub_chunks'] = 2
```

## Tích hợp vào RAG System

### 1. Sử dụng trong vectorstore

```python
from chunker import StructuredChunker
from data.normalizer import HotelDataNormalizer

# Initialize
chunker = StructuredChunker(max_section_size=1500)
normalizer = HotelDataNormalizer()

# Chunk hotels
documents = chunker.chunk_hotels_batch(hotels_df, normalizer)

# Add to vectorstore
vectorstore.add_documents(documents)
```

### 2. Filter trong retrieval

```python
# Tìm kiếm chỉ trong section "amenities"
results = vectorstore.similarity_search(
    query="hồ bơi và spa",
    filter={"section_type": "amenities"}
)
```

### 3. Boost section types quan trọng

```python
# Tăng trọng số cho introduction và summary
if doc.metadata['section_type'] in ['introduction', 'summary']:
    score *= 1.2
```

## Kết luận

Structured Chunking cải thiện đáng kể chất lượng chunking cho dữ liệu có format có cấu trúc:

✅ **Ngữ nghĩa hoàn chỉnh** - Mỗi chunk có ý nghĩa rõ ràng  
✅ **Metadata phong phú** - Dễ dàng filter và search  
✅ **Tìm kiếm chính xác** - Giảm noise, tăng precision  
✅ **Quản lý dễ dàng** - Ít chunks hơn, dễ maintain  

**Khuyến nghị**: Sử dụng `StructuredChunker` khi dữ liệu có format có cấu trúc (1., 2., 3., ...), và `SmartChunker` cho dữ liệu không có cấu trúc.

