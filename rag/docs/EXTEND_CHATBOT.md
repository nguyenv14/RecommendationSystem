# Mở Rộng Chatbot - Khuyến Mãi, Giá Phòng, Tiện Ích Phòng

## 📋 Tổng Quan

Hiện tại chatbot chỉ trả lời về thông tin chung của khách sạn (tên, địa điểm, giá trung bình, đánh giá sao, tiện ích chung). Để mở rộng để trả lời về:
1. **Khuyến mãi và coupon**
2. **Giá cả cho từng phòng và loại phòng**
3. **Tiện ích của các phòng**

**✅ Database đã có sẵn các tables cần thiết!** Chỉ cần extend RAG system để sử dụng data này.

## 🗄️ Database Schema Hiện Có

### **Tables Đã Có:**

1. **`tbl_coupon`** - Coupon/Promotion codes
   - `coupon_id`, `coupon_name`, `coupon_name_code`, `coupon_desc`
   - `coupon_qty_code` (số lượng còn lại), `coupon_condition` (điều kiện)
   - `coupon_price_sale` (giảm giá %), `coupon_start_date`, `coupon_end_date`

2. **`tbl_room`** - Thông tin phòng
   - `room_id`, `hotel_id` (FK), `room_name`
   - `room_amount_of_people` (số người), `room_acreage` (diện tích m²)
   - `room_view` (hướng: "Hướng Sông", "Hướng Thành Phố", etc.)
   - `room_status` (1 = active)

3. **`tbl_type_room`** - Loại phòng và giá
   - `type_room_id`, `room_id` (FK)
   - `type_room_bed` (số giường), `type_room_price` (giá gốc)
   - `type_room_price_sale` (giá sale %), `type_room_condition` (có sale không: 1 = có)
   - `type_room_quantity` (số phòng còn), `type_room_status` (1 = active)

4. **`tbl_facilitiesroom`** - Tiện ích phòng (master data)
   - `facilitiesroom_id`, `facilitiesroom_name` (tên tiện ích)
   - `facilitiesroom_desc` (mô tả), `facilitiesroom_image`
   - Ví dụ: "Vòi Sen", "Truyền Hình", "Trà Cafe", "Tivi", "Wi-fi 5.0", etc.

5. **`tbl_order`** - Orders (có thể dùng để link coupon với hotel qua order)
   - `order_id`, `coupon_name_code` (link với tbl_coupon)
   - `coupon_sale_price`, `total_price`

6. **`tbl_order_details`** - Order details (có thể dùng để get historical prices)
   - `order_details_id`, `hotel_id`, `room_id`, `type_room_id`
   - `price_room` (giá đã đặt), `hotel_fee`

### **Relationships:**
- `tbl_room.hotel_id` → `tbl_hotel.hotel_id`
- `tbl_type_room.room_id` → `tbl_room.room_id`
- `tbl_order.coupon_name_code` → `tbl_coupon.coupon_name_code`
- `tbl_order_details.hotel_id` → `tbl_hotel.hotel_id`
- `tbl_order_details.room_id` → `tbl_room.room_id`
- `tbl_order_details.type_room_id` → `tbl_type_room.type_room_id`

### **⚠️ Missing Relationships:**
- **Room ↔ Facilities**: Không thấy junction table. Có thể:
  - Facilities được store trong field khác (cần check)
  - Hoặc cần tạo junction table `tbl_room_facilities` (room_id, facilitiesroom_id)
  - Hoặc facilities là global, không gắn với room cụ thể

- **Coupon ↔ Hotel**: Coupon không có `hotel_id`. Có thể:
  - Coupon là global (áp dụng cho tất cả hotels)
  - Hoặc link qua `tbl_order` (orders có hotel_id qua order_details)

---

## 🎯 1. Khuyến Mãi và Coupon

### **Vấn Đề Hiện Tại**
- Chatbot không có thông tin về khuyến mãi, coupon, promotion codes
- Không có thời gian hiệu lực, điều kiện áp dụng

### **Giải Pháp**

#### **A. Database Schema (Đã Có Sẵn)**

**Table `tbl_coupon` đã có:**
- `coupon_id` (primary key)
- `coupon_name` (tên coupon: "Chào Đà Nẵng", "Hello VKU")
- `coupon_name_code` (mã code: "CHAODANANG", "HELLOVKU")
- `coupon_desc` (mô tả)
- `coupon_qty_code` (số lượng còn lại)
- `coupon_condition` (điều kiện: 1 = có điều kiện)
- `coupon_price_sale` (giảm giá %: 9, 19, 14, 99)
- `coupon_start_date` (ngày bắt đầu: "2022-11-09")
- `coupon_end_date` (ngày kết thúc: "2026-12-31")

**⚠️ Lưu ý:**
- Coupon **KHÔNG có `hotel_id`** → Coupon là **global** (áp dụng cho tất cả hotels)
- Có thể link coupon với hotel qua `tbl_order` (orders có `coupon_name_code` và link đến hotel qua `tbl_order_details.hotel_id`)

**Cách xác định coupon nào dùng cho hotel nào:**
- Option 1: Coupon global → Tất cả hotels đều có thể dùng
- Option 2: Query `tbl_order` để xem coupon nào đã được dùng cho hotel nào
- Option 3: Nếu cần coupon riêng cho hotel → Cần thêm `hotel_id` vào `tbl_coupon` (ALTER TABLE)

#### **B. Data Connector Extension**

**1. Trong `data/connector.py` - Extend `DatabaseConnector`:**

**Thêm method `get_coupons(active_only=True, hotel_id=None)`:**
- Query `tbl_coupon` để lấy coupons
- Filter:
  - `active_only=True`: Chỉ lấy coupons còn hiệu lực (today >= start_date AND today <= end_date)
  - `coupon_qty_code > 0`: Còn số lượng
- Nếu `hotel_id` provided: Query `tbl_order` để xem coupon nào đã dùng cho hotel đó (optional)
- Return: DataFrame với coupon info

**SQL Query:**
```sql
SELECT * FROM tbl_coupon 
WHERE coupon_qty_code > 0
  AND coupon_start_date <= CURDATE()
  AND coupon_end_date >= CURDATE()
```

**2. Thêm method `get_coupons_by_hotel(hotel_id)`:**
- Query `tbl_order` JOIN `tbl_order_details` để tìm coupons đã dùng cho hotel
- Hoặc return tất cả global coupons (nếu coupon là global)

#### **C. Data Normalization**

**1. Trong `data/normalizer.py` - Extend `HotelDataNormalizer`:**

**Thêm method `create_coupon_semantic_text(coupon)`:**
- Tạo text mô tả coupon từ `tbl_coupon`:
  - Format: `"[COUPON] Tên: {coupon_name}, Mã code: {coupon_name_code}, Mô tả: {coupon_desc}, Giảm giá: {coupon_price_sale}%, Thời gian: từ {start_date} đến {end_date}, Số lượng còn: {coupon_qty_code}"`
  - Ví dụ: "[COUPON] Tên: Chào Đà Nẵng, Mã code: CHAODANANG, Mô tả: Voucher ưu đãi khu vực Đà Nẵng, Giảm giá: 9%, Thời gian: từ 2022-11-09 đến 2026-12-31, Số lượng còn: 9991"

**2. Tạo Semantic Text cho Coupon:**
- Format: `"[COUPON] ..."` để LLM dễ nhận biết
- Include tất cả thông tin quan trọng: tên, mã, giảm giá, thời gian, điều kiện

#### **D. Indexing Strategy**

**1. Option A: Index riêng Collection `coupons` (recommended):**
- Tạo collection riêng trong Qdrant: `coupons`
- Chứa vectors của coupon descriptions
- Metadata: 
  - `coupon_id`, `coupon_name`, `coupon_name_code`
  - `coupon_price_sale` (discount %)
  - `coupon_start_date`, `coupon_end_date`
  - `coupon_qty_code` (số lượng còn)
  - `hotel_id` (nếu có, hoặc NULL nếu global)
- **Ưu điểm**: 
  - Tách biệt, dễ query riêng
  - Dễ update khi coupon thay đổi
  - Có thể filter theo dates, quantity
- **Nhược điểm**: Cần 2 queries (hotels + coupons), merge results

**2. Option B: Index vào collection `hotels` (hybrid):**
- Thêm coupon info vào hotel chunks
- Khi index hotel, thêm các active coupons vào semantic text
- **Ưu điểm**: 1 query duy nhất, context đầy đủ
- **Nhược điểm**: 
  - Context lớn hơn (nhiều coupons)
  - Cần re-index khi coupon thay đổi
  - Khó maintain nếu có nhiều coupons

**3. Option C: Hybrid - Summary trong hotels, chi tiết trong coupons (best):**
- Hotels collection: Chỉ index summary của active coupons (tên, mã, giảm giá %)
- Coupons collection: Index chi tiết đầy đủ
- Query: Search hotels trước → nếu cần chi tiết → search coupons
- **Ưu điểm**: Balance giữa context size và detail

#### **E. Query Processing**

**1. Query Detection:**
- Detect queries về coupon/promotion:
  - Keywords: "khuyến mãi", "coupon", "promotion", "giảm giá", "discount", "mã code", "voucher", "ưu đãi", "đang có chương trình gì", "có mã giảm giá không"
- Nếu detect → route đến coupon search

**2. Search Flow:**

**Query Type 1: "Khách sạn nào đang có khuyến mãi?"**
  1. Extract keywords: ["khuyến mãi"]
  2. Search trong collection `coupons` (không filter hotel_id vì coupon global)
  3. Filter active coupons: `start_date <= today <= end_date`, `coupon_qty_code > 0`
  4. Get unique coupon codes
  5. Return: List coupons với thông tin (tên, mã, giảm giá, thời gian)
  6. Note: Vì coupon global, không cần group by hotel_id

**Query Type 2: "Sheraton có coupon nào không?"**
  1. Extract hotel name: "Sheraton"
  2. Search hotels để get hotel_id
  3. Search coupons:
     - Option A: Return tất cả global coupons (vì coupon không gắn hotel)
     - Option B: Query `tbl_order` để xem coupon nào đã dùng cho hotel đó
  4. Return: List coupons available

**Query Type 3: "Mã CHAODANANG giảm bao nhiêu?"**
  1. Extract coupon code: "CHAODANANG"
  2. Search coupons với filter: `coupon_name_code = "CHAODANANG"`
  3. Return: Chi tiết coupon (tên, mô tả, giảm giá %, thời gian, điều kiện)

**3. Response Generation:**
- LLM prompt cần update để handle coupon context:
  - Nếu có coupon info trong context → trả lời về coupons
  - Format: "Hiện có các mã coupon: [Tên] - Mã: [CODE] - Giảm [X]% - Áp dụng từ [start] đến [end]"
  - Nếu query về coupon cụ thể → Trả lời chi tiết: tên, mô tả, giảm giá, thời gian, số lượng còn, điều kiện

---

## 💰 2. Giá Cả Cho Từng Phòng và Loại Phòng

### **Vấn Đề Hiện Tại**
- Chatbot chỉ có `hotel_price_average` (giá trung bình chung)
- Không có thông tin giá từng loại phòng
- Không biết giá thay đổi theo ngày/tháng

### **Giải Pháp**

#### **A. Database Schema (Đã Có Sẵn)**

**Tables đã có:**

**1. `tbl_room` - Thông tin phòng:**
- `room_id`, `hotel_id` (FK)
- `room_name` (tên phòng: "Phòng Grand Suite", "Phòng Deluxe King")
- `room_amount_of_people` (số người: 2, 3)
- `room_acreage` (diện tích: 45 m²)
- `room_view` (hướng: "Hướng Sông", "Hướng Thành Phố Và Sông")
- `room_status` (1 = active)

**2. `tbl_type_room` - Loại phòng và giá:**
- `type_room_id`, `room_id` (FK → tbl_room)
- `type_room_bed` (số giường: 1, 2, 3)
- `type_room_price` (giá gốc: 1,400,000 VND)
- `type_room_price_sale` (giá sale %: 9, 8, 10)
- `type_room_condition` (có sale không: 1 = có sale, 0 = không)
- `type_room_quantity` (số phòng còn: 19, 0, 15)
- `type_room_status` (1 = active)

**Relationships:**
- `tbl_room.hotel_id` → `tbl_hotel.hotel_id`
- `tbl_type_room.room_id` → `tbl_room.room_id`
- Một `room` có thể có nhiều `type_room` (nhiều loại giường, giá khác nhau)

**⚠️ Lưu ý:**
- Giá được store trong `tbl_type_room.type_room_price` (giá gốc)
- Có `type_room_price_sale` (giảm giá %) nếu `type_room_condition = 1`
- Giá tính: `final_price = type_room_price * (1 - type_room_price_sale/100)`
- Không có giá theo ngày/tháng → Giá là cố định (có thể update manual)
- Có thể dùng `tbl_order_details.price_room` để xem giá historical (giá đã đặt)

#### **B. Data Connector Extension**

**1. Trong `data/connector.py` - Extend `DatabaseConnector`:**

**Thêm method `get_rooms(hotel_id=None)`:**
- Query `tbl_room` JOIN `tbl_type_room` để lấy rooms với prices
- SQL:
  ```sql
  SELECT 
    r.room_id, r.hotel_id, r.room_name,
    r.room_amount_of_people, r.room_acreage, r.room_view,
    tr.type_room_id, tr.type_room_bed, 
    tr.type_room_price, tr.type_room_price_sale, tr.type_room_condition,
    tr.type_room_quantity, tr.type_room_status
  FROM tbl_room r
  LEFT JOIN tbl_type_room tr ON r.room_id = tr.room_id
  WHERE r.room_status = 1 
    AND (tr.type_room_status = 1 OR tr.type_room_status IS NULL)
    AND (hotel_id = ? OR ? IS NULL)
  ```
- Return: DataFrame với room info + type_room info

**2. Thêm method `get_room_prices(room_id=None, hotel_id=None)`:**
- Query `tbl_type_room` để lấy giá
- Calculate final price: `final_price = type_room_price * (1 - type_room_price_sale/100)` nếu có sale
- Return: DataFrame với room_id, type_room_id, base_price, sale_price, final_price, quantity

#### **C. Data Normalization**

**1. Trong `data/normalizer.py` - Extend `HotelDataNormalizer`:**

**Thêm method `create_room_semantic_text(room, type_rooms)`:**
- Tạo text mô tả phòng và giá từ `tbl_room` + `tbl_type_room`:
  - Format: `"[ROOM] Tên phòng: {room_name}, Diện tích: {acreage}m², Số người: {amount_of_people}, Hướng: {view}, Loại giường: {bed} giường, Giá gốc: {price} VND/đêm, Giảm giá: {sale}%, Giá sau giảm: {final_price} VND/đêm, Số phòng còn: {quantity}"`
  - Ví dụ: "[ROOM] Tên phòng: Phòng Grand Suite, Diện tích: 45m², Số người: 2, Hướng: Hướng Sông, Loại giường: 2 giường, Giá gốc: 1400000 VND/đêm, Giảm giá: 9%, Giá sau giảm: 1274000 VND/đêm, Số phòng còn: 19"

**2. Semantic Text Format:**
- Format: `"[ROOM] ..."` để LLM dễ nhận biết
- Include: tên phòng, diện tích, số người, hướng, số giường, giá (gốc + sale + final), số phòng còn
- Nếu có nhiều `type_room` cho 1 `room` → List tất cả options

#### **D. Indexing Strategy**

**1. Option A: Index vào collection `hotels` (recommended):**
- Khi index hotel, fetch rooms + type_rooms từ database
- Thêm room info vào hotel semantic text
- Format: Hotel info + "[ROOM] ..." cho mỗi room
- **Ưu điểm**: 
  - 1 query duy nhất, context đầy đủ
  - Dễ maintain (1 collection)
- **Nhược điểm**: 
  - Chunks lớn hơn (nhiều rooms)
  - Cần chunking tốt để không mất semantic meaning
  - Re-index khi room/price thay đổi

**2. Option B: Index riêng Collection `rooms`:**
- Tạo collection `rooms` riêng
- Mỗi document = 1 room với type_room info
- Metadata: 
  - `hotel_id`, `room_id`, `type_room_id`
  - `room_name`, `room_view`, `room_acreage`, `room_amount_of_people`
  - `type_room_bed`, `type_room_price`, `type_room_price_sale`, `final_price`
  - `type_room_quantity`
- **Ưu điểm**: 
  - Query riêng, dễ filter theo giá (range filter)
  - Dễ update khi price thay đổi
  - Có thể search rooms độc lập
- **Nhược điểm**: 
  - Cần 2 queries (hotels + rooms), merge results
  - Phức tạp hơn

**3. Option C: Hybrid - Summary trong hotels, chi tiết trong rooms (best):**
- Hotels collection: Chỉ index summary của rooms (tên phòng, giá range: min-max)
- Rooms collection: Index chi tiết từng room với type_room
- Query: 
  - Search hotels trước → get hotel_id
  - Nếu query về giá/phòng cụ thể → search rooms với hotel_id filter
- **Ưu điểm**: 
  - Balance giữa context size và detail
  - Hotels query nhanh (summary)
  - Rooms query chi tiết khi cần

#### **E. Query Processing**

**1. Query Detection:**
- Detect queries về giá phòng:
  - Keywords: "giá phòng", "giá từng phòng", "loại phòng", "deluxe", "suite", "grand suite", "giá rẻ nhất", "phòng nào rẻ", "phòng bao nhiêu tiền", "giá bao nhiêu"

**2. Query Types:**

**Type 1: "Giá phòng của Sheraton là bao nhiêu?"**
  1. Extract hotel name: "Sheraton" → get hotel_id
  2. Search hotels collection → get hotel info
  3. Search rooms collection với filter: `hotel_id = X`
  4. Return: Tất cả rooms với prices (room_name, type_room_bed, final_price, quantity)

**Type 2: "Khách sạn nào có phòng dưới 2 triệu?"**
  1. Extract price range: < 2,000,000
  2. Search rooms collection với price filter:
     - Calculate final_price từ type_room_price và type_room_price_sale
     - Filter: `final_price < 2,000,000`
  3. Group by hotel_id
  4. Return: Hotels có phòng phù hợp + room details

**Type 3: "Phòng Grand Suite của Sheraton giá bao nhiêu?"**
  1. Extract hotel: "Sheraton" → hotel_id
  2. Extract room name: "Grand Suite"
  3. Search rooms với filter: `hotel_id = X`, `room_name LIKE "%Grand Suite%"`
  4. Return: Chi tiết phòng Grand Suite + giá (có thể có nhiều type_room với giá khác nhau)

**Type 4: "Phòng nào rẻ nhất ở Sheraton?"**
  1. Extract hotel: "Sheraton" → hotel_id
  2. Search rooms với filter: `hotel_id = X`
  3. Sort by final_price ASC
  4. Return: Room có giá thấp nhất

**3. Price Filtering in Qdrant:**
- Nếu dùng Option B (rooms collection riêng):
  - Store `final_price` trong metadata
  - Dùng Qdrant range filter:
    ```python
    # Pseudocode
    filter = Filter(
        must=[
            FieldCondition(key="hotel_id", match=MatchValue(value=hotel_id)),
            Range(key="final_price", gte=min_price, lte=max_price)
        ]
    )
    ```
- Nếu dùng Option A (rooms trong hotels): Post-filter sau khi search

#### **E. Response Generation**

**1. LLM Prompt Update:**
- Thêm instructions về format response cho giá phòng:
  - "Nếu câu hỏi về giá phòng, trả lời: Loại phòng, giá cơ bản, giá cuối tuần (nếu khác), giá cao điểm (nếu có), số người, diện tích..."

**2. Format Response:**
- Table format cho nhiều loại phòng
- So sánh giá giữa các loại phòng
- Highlight giá tốt nhất nếu query về "phòng rẻ nhất"

---

## 🛏️ 3. Tiện Ích Của Các Phòng

### **Vấn Đề Hiện Tại**
- Chatbot chỉ biết tiện ích chung của khách sạn (hồ bơi, spa, gym)
- Không biết tiện ích riêng của từng loại phòng (ban công, view, minibar, etc.)

### **Giải Pháp**

#### **A. Database Schema (Đã Có Sẵn)**

**Table `tbl_facilitiesroom` đã có:**
- `facilitiesroom_id` (primary key)
- `facilitiesroom_name` (tên tiện ích: "Vòi Sen", "Truyền Hình", "Trà Cafe", "Tivi", "Wi-fi 5.0", etc.)
- `facilitiesroom_desc` (mô tả)
- `facilitiesroom_image` (icon)
- `facilitiesroom_status` (1 = active)

**⚠️ Vấn Đề:**
- `tbl_facilitiesroom` là **master data** (danh sách tiện ích có thể có)
- **KHÔNG có junction table** giữa `tbl_room` và `tbl_facilitiesroom`
- Không biết phòng nào có tiện ích nào

**Giải Pháp:**

**Option 1: Tạo Junction Table (recommended nếu có quyền):**
- Tạo table `tbl_room_facilities`:
  - `room_facility_id` (primary key)
  - `room_id` (FK → tbl_room)
  - `facilitiesroom_id` (FK → tbl_facilitiesroom)
- Insert data: Mỗi phòng có những tiện ích nào

**Option 2: Dùng `tbl_room.room_view` (tạm thời):**
- `room_view` field đã có: "Hướng Sông", "Hướng Thành Phố Và Sông"
- Có thể extract "view" amenities từ field này
- Nhưng thiếu các amenities khác (Vòi Sen, Tivi, Wi-fi, etc.)

**Option 3: Assume All Rooms Have All Facilities (tạm thời):**
- Giả sử tất cả phòng đều có tất cả tiện ích trong `tbl_facilitiesroom`
- Hoặc dùng tiện ích chung của hotel (từ `tbl_facilitieshotel`)

**Option 4: Dùng `tbl_gallery_room` (có sẵn):**
- Table `tbl_gallery_room` có:
  - `gallery_room_id`, `room_id` (FK → tbl_room)
  - `gallery_room_name`, `gallery_room_image`, `gallery_room_content`
- Có thể extract thông tin tiện ích từ `gallery_room_content` hoặc `gallery_room_name`
- Nhưng data có thể không đầy đủ (ví dụ: "Chưa có nội dung !")

**Option 5: Dùng `tbl_facilitieshotel` (tiện ích chung của hotel):**
- Table `tbl_facilitieshotel` có tiện ích chung của hotel
- Có thể assume tất cả rooms của hotel đều có tiện ích chung này
- Nhưng không có junction table → Không biết hotel nào có tiện ích nào

**Recommendation:**
- **Tạm thời**: Dùng `tbl_room.room_view` để extract "view" amenities
- **Tạm thời**: Assume tất cả rooms có tất cả facilities trong `tbl_facilitiesroom` (hoặc facilitieshotel)
- **Long-term**: Tạo junction table `tbl_room_facilities` để map chính xác

#### **B. Data Connector Extension**

**1. Trong `data/connector.py` - Extend `DatabaseConnector`:**

**Thêm method `get_room_facilities(room_id=None, hotel_id=None)`:**
- Query `tbl_facilitiesroom` để lấy danh sách facilities (master data)
- Nếu có junction table → JOIN để lấy facilities của room cụ thể
- Nếu không có junction table → Return tất cả facilities (assume all rooms have all)
- Return: DataFrame với facilities info

**2. Thêm method `get_room_gallery(room_id=None)`:**
- Query `tbl_gallery_room` để lấy gallery images/descriptions
- Có thể extract amenities từ `gallery_room_content`

#### **C. Data Normalization**

**1. Trong `data/normalizer.py` - Extend `HotelDataNormalizer`:**

**Thêm method `create_room_amenities_text(room, facilities)`:**
- Tạo text mô tả tiện ích phòng:
  - Từ `tbl_room.room_view`: Extract "view" amenities ("Hướng Sông" → "view sông", "Hướng Thành Phố" → "view thành phố")
  - Từ `tbl_facilitiesroom`: List tất cả facilities (nếu assume all rooms have all)
  - Format: `"[ROOM_AMENITIES] Tiện ích: {facilities_list}, Hướng: {view}"`
  - Ví dụ: "[ROOM_AMENITIES] Tiện ích: Vòi Sen, Truyền Hình, Trà Cafe, Tivi, Wi-fi 5.0, Nước, Máy Sấy, Ghế Sofa, Đồ Vệ Sinh, Dọn Phòng, Cửa Sổ, Bình Nước, Bàn Trang Điểm, Hướng: Hướng Sông"

**2. Extend `create_room_semantic_text()` để include amenities:**
- Combine room info + price info + amenities info
- Format: `"[ROOM] ... [ROOM_AMENITIES] ..."`

**3. Semantic Text Format:**
- Format: `"[ROOM_AMENITIES] ..."` để LLM dễ nhận biết
- Dùng synonyms để match tốt hơn:
  - "Hướng Sông" → "view sông", "sông view", "river view"
  - "Hướng Thành Phố" → "view thành phố", "city view"
  - "Vòi Sen" → "vòi sen", "shower", "vòi tắm"
  - "Tivi" → "tivi", "TV", "truyền hình"

#### **D. Indexing Strategy**

**1. Index vào Room Chunks:**
- Khi index rooms, include amenities trong semantic text
- Metadata: Store amenities as JSON array để filter sau
- Nếu dùng Option A (rooms trong hotels): Include amenities trong hotel chunks
- Nếu dùng Option B (rooms collection riêng): Include amenities trong room chunks

**2. Filtering Support:**
- Qdrant có thể filter theo amenities nếu store trong metadata (JSON array)
- Hoặc dùng post-filtering (check text-based matching)
- Nếu amenities là text-based → Dùng text search + post-filter

#### **E. Query Processing**

**1. Query Detection:**
- Detect queries về tiện ích phòng:
  - Keywords: "phòng có", "tiện ích", "ban công", "view biển", "phòng nào có bồn tắm", "phòng view đẹp"

**2. Search Flow:**
- Query: "Phòng nào có ban công và view biển?"
  1. Extract amenities: ["ban công", "view biển"]
  2. Search rooms với amenities filter (hoặc text search)
  3. Filter rooms có cả 2 amenities
  4. Return: Rooms matching + hotel info

- Query: "Sheraton có phòng nào có bồn tắm không?"
  1. Extract hotel: "Sheraton" → hotel_id
  2. Extract amenity: "bồn tắm"
  3. Search rooms với filter: hotel_id = X, amenities contains "bồn tắm"
  4. Return: Room types có bồn tắm

**3. Amenity Matching:**
- Dùng synonym mapping:
  - "view biển" → ["view biển", "view beach", "ocean view", "sea view", "hướng biển"]
  - "bồn tắm" → ["bồn tắm", "bathtub", "jacuzzi", "tub"]
- Text-based matching trong post-filtering

#### **F. Response Generation**

**1. LLM Prompt Update:**
- Instructions: "Nếu câu hỏi về tiện ích phòng, liệt kê đầy đủ các tiện ích: Vòi Sen, Tivi, Wi-fi, view, nội thất, phòng tắm..."
- Nếu query về "phòng có view biển" → Tìm rooms có "Hướng Sông" hoặc "view biển" trong room_view

**2. Format Response:**
- List format cho amenities
- Group by category (view, nội thất, phòng tắm, entertainment)
- So sánh amenities giữa các loại phòng
- Highlight amenities đặc biệt (view đẹp, tiện ích cao cấp)

---

## 🏗️ Architecture Changes

### **1. Data Layer (Layer 1: Ingestion)**

#### **A. Database Schema (Đã Có Sẵn)**
- ✅ `tbl_coupon` - Coupons/promotions
- ✅ `tbl_room` - Room information
- ✅ `tbl_type_room` - Room types and prices
- ✅ `tbl_facilitiesroom` - Room facilities (master data)
- ✅ `tbl_gallery_room` - Room gallery (có thể có amenities info)
- ⚠️ **Missing**: Junction table `tbl_room_facilities` (cần tạo nếu muốn map chính xác)

#### **B. Data Connector Updates**
- Extend `data/connector.py` - `DatabaseConnector`:
  - Method `get_coupons(active_only=True, hotel_id=None)`: Get coupons từ `tbl_coupon`
  - Method `get_rooms(hotel_id=None)`: Get rooms + type_rooms từ `tbl_room` JOIN `tbl_type_room`
  - Method `get_room_prices(room_id=None, hotel_id=None)`: Get prices từ `tbl_type_room`
  - Method `get_room_facilities(room_id=None, hotel_id=None)`: Get facilities từ `tbl_facilitiesroom`
  - Method `get_room_gallery(room_id=None)`: Get gallery từ `tbl_gallery_room`

#### **C. Normalizer Updates**
- Extend `data/normalizer.py` - `HotelDataNormalizer`:
  - Method `create_coupon_semantic_text(coupon)`: Tạo text cho coupon từ `tbl_coupon`
  - Method `create_room_semantic_text(room, type_rooms)`: Tạo text cho room + prices từ `tbl_room` + `tbl_type_room`
  - Method `create_room_amenities_text(room, facilities)`: Tạo text cho amenities từ `tbl_facilitiesroom` + `room_view`
  - Method `enrich_hotel_semantic_text(hotel, coupons, rooms, facilities)`: Combine tất cả vào hotel semantic text

#### **D. Indexing Updates**
- Update `simple_rag_system.py` - `index_hotels_from_database()`:
  - Fetch promotions, rooms cùng với hotels
  - Enrich semantic text với promotion + room info
  - Hoặc index riêng collections

### **2. Retrieval Layer (Layer 2: Retrieval)**

#### **A. Query Extractor Updates**
- Extend `core/query_extractor.py` - `QueryExtractor`:
  - Detect query type: "hotel", "promotion", "room", "price", "amenity"
  - Extract entities: promotion keywords, room type, price range, amenities

#### **B. Retriever Updates**
- Extend `core/retriever.py` - `HotelRetriever`:
  - Method `search_promotions(query, hotel_id=None)`: Search promotions
  - Method `search_rooms(query, hotel_id=None, price_range=None, amenities=None)`: Search rooms
  - Method `search_all(query)`: Search hotels + promotions + rooms, merge results

#### **C. Multi-Collection Search**
- Support search across multiple collections:
  - `hotels` collection: Hotel info
  - `promotions` collection: Promotion info
  - `rooms` collection: Room info
- Merge results intelligently

### **3. Generation Layer (Layer 3: Generation)**

#### **A. RAG Chain Updates**
- Update `core/rag_chain.py` - `RAGChain`:
  - Extend prompt template để handle promotion, room, price, amenity context
  - Instructions: "Nếu context có promotion info → trả lời về promotions. Nếu có room info → trả lời về rooms và giá..."

#### **B. Response Formatting**
- Format response based on query type:
  - Promotion queries → Format: Promotion name, code, discount, dates
  - Room/Price queries → Format: Room type, price, amenities (table/list)
  - Amenity queries → Format: Room types với amenities matching

---

## 📊 Data Flow

### **Indexing Flow (Offline)**
```
1. Fetch Hotels từ Database
2. Fetch Promotions cho mỗi hotel (active only)
3. Fetch Room Types cho mỗi hotel
4. Fetch Prices cho mỗi room type
5. Fetch Amenities cho mỗi room type
6. Normalize data:
   - Create hotel semantic text
   - Create promotion semantic text
   - Create room semantic text (combine type + price + amenities)
   - Enrich hotel text với promotions + rooms summary
7. Chunk enriched text
8. Generate embeddings
9. Index vào Qdrant:
   - Hotels collection: Hotel chunks + promotions summary + rooms summary
   - (Optional) Promotions collection: Promotion chunks
   - (Optional) Rooms collection: Room chunks
```

### **Query Flow (Online)**
```
1. User Query: "Sheraton có khuyến mãi gì không?"
2. Query Extractor:
   - Detect: Promotion query
   - Extract: Hotel name = "Sheraton"
3. Retrieval:
   - Search hotels → Get hotel_id
   - Search promotions với filter: hotel_id = X, is_active = True
   - Get active promotions
4. Context Building:
   - Combine: Hotel info + Promotion details
5. Generation:
   - LLM generate answer từ context
6. Response:
   - Format: List promotions với code, discount, dates
```

---

## 🔧 Implementation Steps

### **Phase 1: Database & Data Model**
1. Design database schema cho promotions, rooms, prices
2. Create migration scripts
3. Import/sync data vào database

### **Phase 2: Data Processing**
1. Update `data/connector.py` để fetch promotions, rooms
2. Update `data/normalizer.py` để create semantic text cho promotions, rooms
3. Test data normalization

### **Phase 3: Indexing**
1. Update indexing logic để include promotions, rooms
2. Decide: Single collection vs multi-collection
3. Test indexing với enriched data

### **Phase 4: Retrieval**
1. Update `core/query_extractor.py` để detect promotion/room queries
2. Update `core/retriever.py` để search promotions, rooms
3. Implement multi-collection search nếu cần
4. Test retrieval với various queries

### **Phase 5: Generation**
1. Update `core/rag_chain.py` prompt để handle new context types
2. Test generation với promotion/room queries
3. Fine-tune prompt nếu cần

### **Phase 6: Testing & Refinement**
1. Test end-to-end với real queries
2. Refine data normalization nếu search không tốt
3. Optimize chunking strategy
4. Monitor performance

---

## 📝 Key Considerations

### **1. Data Freshness**
- Promotions có thời gian hiệu lực → Cần re-index khi promotion hết hạn
- Prices có thể thay đổi → Cần incremental update
- **Solution**: Schedule job để re-index active promotions/current prices

### **2. Context Size**
- Nếu index tất cả promotions + rooms vào hotel chunks → Context lớn
- **Solution**: 
  - Chỉ index summary (tên promotion, room types, price ranges)
  - Chi tiết index riêng, query khi cần

### **3. Query Routing**
- Cần detect query type để route đúng collection
- **Solution**: Query extractor detect intent → route đến appropriate retriever

### **4. Filtering Performance**
- Filter theo price range, dates, amenities → Cần metadata indexing
- **Solution**: Store structured metadata trong Qdrant payload, dùng filters

### **5. Response Accuracy**
- LLM cần hiểu context types để format response đúng
- **Solution**: Clear prompt instructions + context markers (e.g., [PROMOTION], [ROOM_TYPE])

---

## ✅ Benefits

1. **Comprehensive Answers**: Chatbot trả lời đầy đủ về promotions, rooms, prices, amenities
2. **Better User Experience**: Users có thể hỏi cụ thể về giá phòng, coupon, tiện ích
3. **Sales Support**: Hỗ trợ sales tốt hơn với thông tin promotion và pricing
4. **Flexible Querying**: Support nhiều loại queries khác nhau

---

## 🚀 Next Steps

1. Review và approve database schema design
2. Implement database migrations
3. Update data processing components
4. Extend indexing logic
5. Update retrieval và generation layers
6. Test với real data và queries
7. Deploy và monitor

---

*Document này mô tả approach và methodology để mở rộng chatbot. Cần implement từng phase một để đảm bảo quality.*

