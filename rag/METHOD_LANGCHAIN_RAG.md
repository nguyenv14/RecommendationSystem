# Phương Pháp Sử Dụng LangChain với Local Models cho Hệ Thống RAG Khách Sạn

## 📋 Tổng Quan

Tài liệu này mô tả phương pháp xây dựng hệ thống RAG (Retrieval-Augmented Generation) sử dụng **LangChain** với **local embedding models** và **local LLM models** cho dataset khách sạn.

---

## 🎯 1. CÓ THỂ SỬ DỤNG LANGCHAIN VỚI LOCAL MODELS KHÔNG?

### ✅ **CÓ - Hoàn toàn có thể!**

LangChain hỗ trợ rất tốt các local models thông qua:

#### **1.1 Local Embedding Models**
- **Ollama** (qua `langchain_community.embeddings.OllamaEmbeddings`)
- **Sentence Transformers** (qua `langchain_community.embeddings.HuggingFaceEmbeddings`)
- **BGE-M3, BGE-Large, Multilingual-E5** (qua HuggingFace)
- **Custom models** (qua wrapper tùy chỉnh)

#### **1.2 Local LLM Models**
- **Ollama** (`llama2`, `mistral`, `phi`, `gemma`, v.v.)
- **LM Studio** (qua API local)
- **vLLM** (qua local server)
- **Transformers** (trực tiếp load model)

---

## 🧠 2. LÀM THẾ NÀO ĐỂ EMBEDDING HIỂU NGỮ NGHĨA VÀ TÌM KIẾM ĐÚNG?

### **2.1 Vấn Đề Chính**

Embedding có thể không hiểu đúng ngữ nghĩa nếu:
- ❌ Dữ liệu không được chuẩn hóa tốt
- ❌ Chọn sai embedding model
- ❌ Không có context đầy đủ
- ❌ Query không được xử lý đúng cách
- ❌ Không có re-ranking sau khi search

### **2.2 Phương Pháp Cải Thiện**

#### **A. Chuẩn Hóa Dữ Liệu (Data Preprocessing)**

**Với dataset khách sạn của bạn:**

1. **Kết hợp đa chiều dữ liệu:**
   ```
   Text = "Tên: {hotel_name} | "
          "Mô tả: {hotel_desc} | "
          "Địa chỉ: {hotel_placedetails} | "
          "Khu vực: {area_name} | "
          "Thương hiệu: {brand_name} | "
          "Từ khóa: {hotel_tag_keyword} | "
          "Hạng: {hotel_rank} sao | "
          "Giá trung bình: {hotel_price_average}"
   ```

2. **Thêm metadata quan trọng:**
   - Thông tin phòng (room_name, room_view, room_acreage)
   - Thông tin giá (type_room_price, type_room_price_sale)
   - Thông tin khu vực (area_name, area_desc)
   - Thông tin thương hiệu (brand_name, brand_desc)

3. **Chuẩn hóa ngôn ngữ:**
   - Loại bỏ ký tự đặc biệt thừa
   - Xử lý encoding (UTF-8)
   - Chuẩn hóa khoảng trắng

#### **B. Chọn Đúng Embedding Model**

**Cho tiếng Việt:**
- ✅ **BGE-M3** (Best): Đa ngôn ngữ, hỗ trợ tiếng Việt tốt, 1024 dimensions
- ✅ **paraphrase-multilingual-MiniLM-L12-v2** (Good): Nhẹ, nhanh
- ✅ **multilingual-e5-large** (Excellent): Rất tốt cho tiếng Việt
- ✅ **vietnamese-bert-base** (Specialized): Chuyên cho tiếng Việt

**Khuyến nghị:** BGE-M3 qua Ollama (bạn đã có)

#### **C. Context Enrichment (Làm Giàu Context)**

**Vấn đề:** Một câu "Khách sạn gần biển" có thể không match với "Khách sạn ven biển Mỹ Khê" nếu embedding không đủ context.

**Giải pháp:**

1. **Thêm synonyms và biến thể:**
   ```
   "gần biển" → "ven biển, sát biển, cách biển, view biển, hướng biển"
   "5 sao" → "5 sao, luxury, cao cấp, sang trọng"
   "giá rẻ" → "giá rẻ, giá tốt, giá hợp lý, giá phải chăng"
   ```

2. **Expand query (mở rộng truy vấn):**
   - Sử dụng LLM để mở rộng query người dùng
   - Ví dụ: "Khách sạn gần biển" → "Khách sạn ven biển, sát biển, view biển, hướng biển"

3. **Hybrid Search (tìm kiếm lai):**
   - Kết hợp **semantic search** (embedding) + **keyword search** (BM25)
   - LangChain hỗ trợ qua `VectorStoreRetriever` + `BM25Retriever`

#### **D. Query Processing (Xử Lý Truy Vấn)**

**Trước khi embedding query:**

1. **Chuẩn hóa query:**
   - Loại bỏ stop words không cần thiết
   - Giữ lại từ khóa quan trọng
   - Xử lý lỗi chính tả (nếu có)

2. **Query expansion:**
   ```python
   # Ví dụ với LangChain
   from langchain.retrievers import ContextualCompressionRetriever
   from langchain.retrievers.document_compressors import LLMChainExtractor
   
   # Expand query với LLM
   expanded_query = llm.expand_query("Khách sạn gần biển")
   # → "Khách sạn ven biển, sát biển Mỹ Khê, view biển, hướng biển"
   ```

3. **Query understanding:**
   - Phân loại intent: "Tìm khách sạn" vs "So sánh giá" vs "Xem đánh giá"
   - Extract entities: "Đà Nẵng", "5 sao", "gần biển"

#### **E. Re-ranking (Sắp Xếp Lại Kết Quả)**

**Vấn đề:** Top-k results từ embedding search có thể không chính xác 100%.

**Giải pháp:**

1. **Cross-encoder re-ranking:**
   - Sử dụng model cross-encoder (như `ms-marco-MiniLM`) để re-rank
   - So sánh query với từng document một cách chính xác hơn

2. **Multi-stage retrieval:**
   ```
   Stage 1: Embedding search → Top 50 results
   Stage 2: Re-rank với cross-encoder → Top 10 results
   Stage 3: LLM refine → Top 5 results
   ```

3. **Hybrid scoring:**
   - Kết hợp: `final_score = 0.7 * semantic_score + 0.3 * keyword_score`

---

## 🏗️ 3. PHƯƠNG PHÁP THIẾT KẾ PIPELINE RAG VỚI LANGCHAIN

### **3.1 Kiến Trúc Tổng Quan**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                               │
│          "Khách sạn 5 sao gần biển Đà Nẵng"                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              QUERY PROCESSING LAYER                        │
│  • Query normalization                                      │
│  • Query expansion (LLM)                                    │
│  • Intent classification                                     │
│  • Entity extraction                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              EMBEDDING LAYER                                 │
│  • Local Embedding Model (BGE-M3 via Ollama)                │
│  • Query → Vector                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              RETRIEVAL LAYER                                 │
│  • Vector Store (Qdrant) - Semantic Search                  │
│  • BM25 Retriever (optional) - Keyword Search                │
│  • Hybrid Search (combine both)                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              RE-RANKING LAYER (Optional)                     │
│  • Cross-encoder re-ranking                                 │
│  • Score refinement                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              CONTEXT ENRICHMENT                              │
│  • Join with related tables (room, type_room, area, brand)  │
│  • Format context for LLM                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM GENERATION LAYER                            │
│  • Local LLM (Ollama: llama2, mistral, etc.)               │
│  • Prompt template với context                               │
│  • Generate natural language response                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              RESPONSE                                        │
│  • Natural language answer                                   │
│  • Structured data (hotel list)                              │
└─────────────────────────────────────────────────────────────┘
```

### **3.2 Các Thành Phần LangChain Cần Dùng**

#### **A. Document Loaders & Processors**
```python
# Load CSV files
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Tạo documents từ CSV
documents = []
for hotel in hotels_df:
    # Combine multiple fields
    text = f"Tên: {hotel_name} | Mô tả: {hotel_desc} | ..."
    documents.append(Document(page_content=text, metadata={hotel_id, ...}))
```

#### **B. Embeddings**
```python
from langchain_community.embeddings import OllamaEmbeddings

# Local embedding via Ollama
embeddings = OllamaEmbeddings(
    model="bge-m3",
    base_url="http://localhost:11434"
)
```

#### **C. Vector Store**
```python
from langchain_community.vectorstores import Qdrant
from langchain.vectorstores import Qdrant

# Connect to Qdrant
vectorstore = Qdrant.from_documents(
    documents=documents,
    embedding=embeddings,
    url="http://localhost:6333",
    collection_name="hotels"
)
```

#### **D. Retrievers**
```python
from langchain.retrievers import VectorStoreRetriever
from langchain.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

# Semantic retriever
vector_retriever = VectorStoreRetriever(vectorstore=vectorstore)

# Keyword retriever (optional)
bm25_retriever = BM25Retriever.from_documents(documents)

# Hybrid retriever
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.7, 0.3]  # 70% semantic, 30% keyword
)
```

#### **E. LLM**
```python
from langchain_community.llms import Ollama

# Local LLM via Ollama
llm = Ollama(
    model="llama2",  # or "mistral", "phi", "gemma"
    base_url="http://localhost:11434",
    temperature=0.7
)
```

#### **F. Chains**
```python
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate

# Prompt template
prompt_template = """
Bạn là trợ lý tư vấn khách sạn chuyên nghiệp.

Context: {context}

Câu hỏi: {question}

Hãy trả lời dựa trên context trên. Nếu không có thông tin, hãy nói "Tôi không có thông tin về điều này."
"""

# RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=ensemble_retriever,
    chain_type_kwargs={"prompt": PromptTemplate.from_template(prompt_template)}
)
```

---

## 📊 4. PHƯƠNG PHÁP XỬ LÝ DATASET KHÁCH SẠN

### **4.1 Chuẩn Bị Dữ Liệu**

#### **Bước 1: Load và Join Tables**
```
tbl_hotel (main)
    ├── JOIN tbl_room (hotel_id)
    │   └── JOIN tbl_type_room (room_id)
    ├── JOIN tbl_area (area_id)
    ├── JOIN tbl_brand (brand_id)
    └── JOIN tbl_coupon (nếu cần)
```

#### **Bước 2: Tạo Document cho mỗi Hotel**
```
Document Structure:
{
    "page_content": "Tên: Meliá Vinpearl Riverfront | 
                    Mô tả: Khách sạn 5 sao cao cấp... | 
                    Địa chỉ: 341 Trần Hưng Đạo... | 
                    Khu vực: Sơn Trà | 
                    Thương hiệu: Furama | 
                    Từ khóa: Khách Sạn Đà Nẵng, 5 Sao | 
                    Hạng: 5 sao | 
                    Giá: 1,311,127 VND | 
                    Phòng: Grand Suite (45m², Hướng Sông) | 
                    ...",
    "metadata": {
        "hotel_id": 2,
        "hotel_name": "Meliá Vinpearl Riverfront",
        "area_id": 8,
        "brand_id": 3,
        "hotel_rank": 5,
        "hotel_price_average": 1311127
    }
}
```

#### **Bước 3: Chunk Documents (nếu cần)**
- Nếu hotel description quá dài (>512 tokens), chia nhỏ
- Nhưng với dataset của bạn, mỗi hotel có thể fit trong 1 document

### **4.2 Index vào Vector Store**

```
1. Load documents từ CSV
2. Process và enrich với metadata
3. Embed với local model (BGE-M3)
4. Store vào Qdrant với metadata
```

### **4.3 Query Processing**

**Ví dụ queries:**
- "Khách sạn 5 sao gần biển Đà Nẵng"
- "Khách sạn giá rẻ ở Sơn Trà"
- "So sánh giá khách sạn Mường Thanh và Meliá"

**Xử lý:**
1. **Intent classification:**
   - Tìm kiếm → Semantic search
   - So sánh → Multi-document comparison
   - Tư vấn → RAG generation

2. **Entity extraction:**
   - "5 sao" → hotel_rank = 5
   - "gần biển" → room_view = "Hướng Sông" hoặc keyword "biển"
   - "Đà Nẵng" → area_name = "Sơn Trà" (có thể)
   - "giá rẻ" → price filter

3. **Query expansion:**
   ```
   "Khách sạn 5 sao gần biển" 
   → "Khách sạn 5 sao ven biển, sát biển, view biển, hướng biển"
   ```

### **4.4 Retrieval Strategy**

#### **Option 1: Pure Semantic Search**
```
Query → Embedding → Vector Search → Top-k results
```

#### **Option 2: Hybrid Search (Recommended)**
```
Query → {
    Semantic: Embedding → Vector Search (top 50)
    Keyword: BM25 Search (top 50)
} → Merge & Deduplicate → Top-k results
```

#### **Option 3: Multi-stage Retrieval**
```
Stage 1: Semantic Search (top 50)
Stage 2: Re-rank với cross-encoder (top 10)
Stage 3: LLM refine (top 5)
```

### **4.5 Response Generation**

**Prompt Template:**
```
Bạn là trợ lý tư vấn khách sạn chuyên nghiệp.

Dựa trên thông tin sau, hãy trả lời câu hỏi của người dùng:

{context}

Câu hỏi: {question}

Hãy:
1. Trả lời tự nhiên, dễ hiểu
2. Nêu tên khách sạn, địa chỉ, giá nếu có
3. Nếu không có thông tin, hãy nói rõ
```

---

## 🔧 5. CẢI THIỆN ĐỘ CHÍNH XÁC TÌM KIẾM

### **5.1 Fine-tuning Embedding Model (Advanced)**

Nếu dataset đủ lớn, có thể fine-tune embedding model:
- Train trên cặp (query, relevant_hotel)
- Sử dụng contrastive learning
- Cải thiện đáng kể độ chính xác

### **5.2 Query Augmentation**

**Techniques:**
1. **Paraphrasing:** Tạo nhiều biến thể của query
2. **Back-translation:** Dịch query sang tiếng Anh rồi dịch lại
3. **Synonym expansion:** Mở rộng từ đồng nghĩa

### **5.3 Metadata Filtering**

Sử dụng metadata để filter trước khi search:
```python
# Filter by area, brand, rank, price range
filtered_results = vectorstore.similarity_search(
    query,
    filter={
        "area_id": 8,
        "hotel_rank": 5,
        "price_range": {"$gte": 1000000, "$lte": 2000000}
    }
)
```

### **5.4 Evaluation Metrics**

Để đánh giá chất lượng:
- **Precision@K:** % kết quả đúng trong top-k
- **Recall@K:** % kết quả đúng được tìm thấy
- **MRR (Mean Reciprocal Rank):** Vị trí trung bình của kết quả đúng đầu tiên
- **NDCG (Normalized Discounted Cumulative Gain):** Đánh giá chất lượng ranking

---

## 📝 6. LUỒNG XỬ LÝ CHI TIẾT

### **6.1 Initialization Phase**

```
1. Load embedding model (BGE-M3 via Ollama)
2. Load LLM model (llama2/mistral via Ollama)
3. Connect to Qdrant
4. Load documents từ CSV
5. Process và enrich documents
6. Embed documents
7. Index vào Qdrant
```

### **6.2 Query Phase**

```
1. Receive user query
2. Query preprocessing (normalize, expand)
3. Embed query
4. Semantic search in Qdrant
5. (Optional) Keyword search with BM25
6. Merge results
7. (Optional) Re-rank
8. Join with related tables (room, area, brand)
9. Format context
10. Generate response với LLM
11. Return response
```

### **6.3 Update Phase**

```
1. Receive new hotel data
2. Process và enrich
3. Embed
4. Add to Qdrant (incremental update)
```

---

## 🎯 7. KHUYẾN NGHỊ CHO DATASET CỦA BẠN

### **7.1 Embedding Model**
✅ **BGE-M3** (đã có) - Rất tốt cho tiếng Việt

### **7.2 LLM Model**
✅ **llama2:7b** hoặc **mistral:7b** - Đủ tốt cho RAG
- Nếu muốn tốt hơn: **llama2:13b** hoặc **mistral:8x7b**

### **7.3 Retrieval Strategy**
✅ **Hybrid Search** (Semantic + Keyword) - Best balance

### **7.4 Re-ranking**
⚠️ **Optional** - Nếu cần độ chính xác cao hơn

### **7.5 Document Structure**
✅ **Mỗi hotel = 1 document** với đầy đủ metadata

---

## 🚀 8. LỢI ÍCH KHI DÙNG LANGCHAIN

### **8.1 Modularity**
- Dễ thay đổi từng component (embedding, LLM, retriever)
- Dễ test và debug

### **8.2 Built-in Features**
- Prompt templates
- Chains (RAG, QA, Conversation)
- Memory management
- Callbacks & logging

### **8.3 Integration**
- Dễ tích hợp với các tools khác
- Hỗ trợ nhiều vector stores
- Hỗ trợ nhiều LLM providers

### **8.4 Community & Support**
- Tài liệu phong phú
- Nhiều examples
- Active community

---

## 📚 9. TÀI LIỆU THAM KHẢO

### **LangChain Documentation**
- https://python.langchain.com/
- https://python.langchain.com/docs/integrations/vectorstores/qdrant
- https://python.langchain.com/docs/integrations/llms/ollama

### **Embedding Models**
- BGE-M3: https://huggingface.co/BAAI/bge-m3
- Sentence Transformers: https://www.sbert.net/

### **Vector Databases**
- Qdrant: https://qdrant.tech/documentation/
- Milvus: https://milvus.io/docs

---

## ✅ KẾT LUẬN

**Câu trả lời:**
1. ✅ **Có thể dùng LangChain với local models** - Hoàn toàn khả thi
2. ✅ **Embedding sẽ hiểu ngữ nghĩa tốt** nếu:
   - Chuẩn hóa dữ liệu đúng cách
   - Chọn đúng model
   - Enrich context đầy đủ
   - Xử lý query tốt
   - (Optional) Re-ranking

3. ✅ **Phương pháp tốt nhất:**
   - LangChain + Ollama (embedding + LLM)
   - Qdrant (vector store)
   - Hybrid search (semantic + keyword)
   - RAG chain với prompt template

**Bước tiếp theo:** Implement theo phương pháp trên, test và fine-tune!

