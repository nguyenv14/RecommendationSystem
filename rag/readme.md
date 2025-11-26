# Realtime RAG Pipeline for Hotel Recommendation

## 1. Data Source Integration
- Kết nối hệ thống với nguồn dữ liệu khách sạn (DB hoặc API) theo mô hình **event-driven/CDC** (Debezium, webhooks, message queue) kết hợp **batch fallback** (cron/ETL).  
- Worker tiếp nhận event, truy vấn DB lấy bản ghi mới/cập nhật dựa `updated_at`, đảm bảo không thực hiện trong luồng người dùng.

## 2. Normalization Layer
- Tách logic chuẩn hóa (tái sử dụng `hotel_data_normalization.py`) thành hàm thuần: input `hotel_record`, output dict chuẩn hóa + `semantic_text`.  
- Lưu kết quả vào bảng `normalized_hotels` (hoặc file) với `normalized_hash` để bỏ qua bản ghi không đổi.  
- Thiết lập batch định kỳ để so sánh và đồng bộ lại nếu bỏ lỡ event.

## 3. Chunk Management
- Chia mỗi bản ghi chuẩn hóa thành nhiều chunk (200–500 token) theo từng trường: mô tả, tiện ích, vị trí…  
- Lưu chunk vào kho riêng với `chunk_id`, `hotel_id`, `chunk_type`, `chunk_text`, `content_hash`, `updated_at`.  
- Ba hành động chính:
  - Chunk mới: insert vào kho + queue để embed.  
  - Chunk thay đổi: cập nhật `chunk_text` và `content_hash`, đưa vào queue.  
  - Chunk xóa: đánh dấu và gửi event xóa vector.
- Trong quá trình chunk hóa, thêm metadata `keywords` (ví dụ: `{"amenities": ["hồ bơi", "gym"]}`) để khi truy vấn có thể filter hoặc boost theo tiện ích.
- Giảm context gửi vào LLM bằng cách chỉ lấy top `k` chunk phù hợp nhất (ví dụ `k=3`) hoặc áp dụng reranker/context compression để tránh đưa nguyên mô tả dài, giúp tốc độ trả lời nhanh hơn.

### 3.1 Chunk Storage với MinIO
- Dựng MinIO cluster riêng cho pipeline RAG; mỗi bucket đại diện cho môi trường (`rag-dev`, `rag-prod`).  
- Lưu chunk dưới dạng file JSON (hoặc Parquet) với cấu trúc `hotel_id=<id>/chunk_id=<uuid>.json`, nội dung gồm text và metadata.  
- Ghi thêm file index (VD: `chunks/index.parquet`) liệt kê `chunk_id`, `hotel_id`, `chunk_type`, `content_hash`, `last_modified` để worker tra cứu nhanh.  
- Worker embedding truy cập MinIO qua SDK, chỉ tải những chunk có `content_hash` khác lần sync trước.  
- Sử dụng MinIO versioning/lifecycle để giữ lịch sử và dọn dẹp chunk cũ.

## 4. Vectorization & Storage
- Worker embedding đọc chunk cần xử lý, gọi Ollama (hoặc dịch vụ khác) để tạo vector.  
- Dùng `QdrantClient.upsert` với `chunk_id` làm vector ID, metadata gồm `hotel_id`, `chunk_type`, `summary`.  
- Song song hóa worker (Celery, RQ, Kafka consumer) để giảm thời gian chờ; gom micro-batch nếu phù hợp.  
- Batch job hằng ngày so sánh `hotel_chunks` với Qdrant để đồng bộ.

## 5. Retrieval & Answering
- Retriever tìm vector theo `hotel_id`/`chunk_type`, lấy chunk text từ metadata hoặc từ kho chunk để làm nguồn.  
- Kết hợp dữ liệu thời gian thực (giá, tình trạng phòng) bằng cách truy DB trực tiếp trong bước tạo câu trả lời, không embed.

## 6. Operations & Monitoring
- Log thời gian sync, queue lag, tỷ lệ chunk chưa embed, lỗi embedding/Qdrant.  
- Lưu `last_sync` để job batch incremental biết điểm bắt đầu.  
- Kiểm thử end-to-end: tạo/cập nhật/xóa khách sạn → chunk → vector → truy vấn RAG.  
- Thiết lập alert khi việc đồng bộ thất bại hoặc chậm.

## 7. Lộ trình triển khai đề xuất
1. Chuẩn bị hạ tầng event/CDC và queue.  
2. Trọng tâm hóa hàm normalization + chunking.  
3. Xây worker ingestion (chunk store + embedding + Qdrant upsert).  
4. Viết batch incremental & fallback.  
5. Cập nhật retriever/LLM để dùng chunk store.  
6. Thêm quan sát (metrics, logs, alert).  

Tuân theo lộ trình này, hệ thống RAG sẽ hỗ trợ cập nhật dữ liệu khách sạn gần realtime, dễ bảo trì và mở rộng.