# Dữ Liệu Được Sinh Ra Cho Hệ Thống Đặt Phòng Khách Sạn

## Tổng Quan

File `generated_hotel_data.sql` chứa dữ liệu được sinh ra một cách hợp lý và có tính thực tế cho các bảng trong hệ thống quản lý đặt phòng khách sạn. Dữ liệu này được thiết kế đặc biệt để huấn luyện mô hình recommendation system (hệ thống gợi ý).

## Cấu Trúc Dữ Liệu

### 1. **Khách Hàng (tbl_customers)**
- **Số lượng**: 40 khách hàng mới (ID: 11-50)
- **Đặc điểm**:
  - Tên khách hàng thực tế, đa dạng
  - Số điện thoại và email duy nhất
  - Phân bổ từ các thành phố lớn: Hà Nội, TP HCM, Đà Nẵng, Hải Phòng
  - Đa dạng thiết bị: iPhone, Android, Windows, MacOS
  - Thời gian đăng ký từ 01/2023 đến 09/2023

### 2. **Thanh Toán (tbl_payment)**
- **Số lượng**: 200 bản ghi (ID: 61-260)
- **Đặc điểm**:
  - Phương thức thanh toán đa dạng (1-4):
    - 1: Tiền mặt
    - 2: Chuyển khoản
    - 3: Ví điện tử
    - 4: Thẻ tín dụng
  - Tất cả trạng thái thanh toán thành công (status = 1)

### 3. **Người Đặt Phòng (tbl_orderer)**
- **Số lượng**: 100 bản ghi (ID: 51-150)
- **Đặc điểm**:
  - Liên kết với customer_id
  - Thông tin chi tiết: tên, số điện thoại, email
  - Yêu cầu đặc biệt đa dạng:
    - "Phòng tầng cao"
    - "View biển"
    - "Yên tĩnh"
    - "Gần thang máy"
    - "View sông"
    - "Phòng góc"
  - Loại giường: 1 (đơn), 2 (đôi), 3 (gia đình)
  - Thời gian đặt từ 06/2023 đến 11/2024

### 4. **Đơn Đặt Phòng (tbl_order)**
- **Số lượng**: 100 đơn hàng (ID: 51-150)
- **Đặc điểm**:
  - Thời gian lưu trú: 2-4 ngày
  - Phân bổ đều qua các tháng từ 06/2023 đến 11/2024
  - Mã coupon đa dạng:
    - "HELLOVKU": giảm ~15-20%
    - "CHAODANANG": giảm ~10-15%
    - NULL: không sử dụng mã giảm giá
  - Tổng giá trị từ 1.96 triệu đến 6.8 triệu VNĐ
  - Tất cả đơn hàng đã hoàn thành (order_status = 2)
  - Mã đơn hàng unique theo format MYHOTEL#### 

### 5. **Chi Tiết Đơn Hàng (tbl_order_details)**
- **Số lượng**: 100 bản ghi (ID: 51-150)
- **Đặc điểm**:
  - Liên kết chính xác với:
    - Khách sạn (hotel_id, hotel_name)
    - Phòng (room_id, room_name)
    - Loại phòng (type_room_id)
  - Sử dụng 17 khách sạn khác nhau (ID: 2-18)
  - Giá phòng từ 800,000 VNĐ đến 5,700,000 VNĐ/đêm
  - Phân bổ đều qua các loại phòng và khách sạn

### 6. **Đánh Giá (tbl_evaluate)**
- **Số lượng**: 50 đánh giá (ID: 1-50)
- **Đặc điểm**:
  - 5 tiêu chí đánh giá (thang điểm 10):
    - `evaluate_loaction_point`: Vị trí (8-10)
    - `evaluate_service_point`: Dịch vụ (8-10)
    - `evaluate_price_point`: Giá cả (7-9)
    - `evaluate_sanitary_point`: Vệ sinh (8-10)
    - `evaluate_convenient_point`: Tiện nghi (8-10)
  - Tiêu đề và nội dung đánh giá tiếng Việt thực tế
  - Thời gian đánh giá sau khi check-out 1-3 ngày
  - Đa dạng mức độ: "Tốt", "Rất tốt", "Tuyệt vời", "Xuất sắc", "Hoàn hảo"

## Đặc Điểm Dữ Liệu Cho Recommendation System

### 1. **Đa Dạng Hành Vi Người Dùng**
- Khách hàng đặt phòng tại nhiều khách sạn khác nhau
- Khách hàng quay lại đặt phòng (repeat customers)
- Mẫu booking theo mùa: cao điểm hè, lễ tết

### 2. **Đa Dạng Sở Thích**
- Phạm vi giá: từ budget (800K) đến luxury (5.7M)
- Loại khách sạn: 3 sao, 4 sao, 5 sao
- Loại phòng: Standard, Deluxe, Suite, Premium
- View: biển, sông, thành phố

### 3. **Dữ Liệu Rating Phong Phú**
- 5 chiều đánh giá khác nhau
- Điểm số từ 7-10 (realistic, không quá perfect)
- Phản ánh chất lượng thực tế của từng khách sạn

### 4. **Mối Quan Hệ Dữ Liệu Rõ Ràng**
```
customer → orderer → order → order_details → hotel/room/type_room
                                             ↓
                                         evaluate
```

## Cách Sử Dụng

### Bước 1: Backup Database Hiện Tại
```sql
-- Backup database trước khi import
mysqldump -u username -p myhotel > myhotel_backup.sql
```

### Bước 2: Import Dữ Liệu
```sql
-- Option 1: Từ MySQL command line
mysql -u username -p myhotel < generated_hotel_data.sql

-- Option 2: Trong MySQL Workbench
-- File → Run SQL Script → chọn generated_hotel_data.sql
```

### Bước 3: Kiểm Tra Dữ Liệu
```sql
-- Kiểm tra số lượng bản ghi
SELECT COUNT(*) FROM tbl_customers WHERE customer_id >= 11;  -- Expect: 40
SELECT COUNT(*) FROM tbl_payment WHERE payment_id >= 61;     -- Expect: 200
SELECT COUNT(*) FROM tbl_orderer WHERE orderer_id >= 51;     -- Expect: 100
SELECT COUNT(*) FROM tbl_order WHERE order_id >= 51;         -- Expect: 100
SELECT COUNT(*) FROM tbl_order_details WHERE order_details_id >= 51; -- Expect: 100
SELECT COUNT(*) FROM tbl_evaluate WHERE evaluate_id >= 1;    -- Expect: 50
```

## Ứng Dụng Trong Recommendation System

### 1. **Collaborative Filtering**
- User-based: tìm khách hàng tương tự dựa trên lịch sử đặt phòng
- Item-based: gợi ý khách sạn/phòng tương tự với những gì khách đã đặt

### 2. **Content-Based Filtering**
- Đặc trưng khách sạn: vị trí, hạng sao, giá, view
- Đặc trưng phòng: loại giường, diện tích, tiện nghi
- Sở thích người dùng: khoảng giá, loại phòng, vị trí

### 3. **Hybrid Approach**
- Kết hợp rating scores với booking history
- Xem xét temporal patterns (mùa, thời gian đặt)
- Feature engineering từ các yêu cầu đặc biệt

### 4. **Features Có Thể Trích Xuất**

#### User Features:
- `user_avg_price`: Giá trung bình khách hàng thường đặt
- `user_preferred_hotel_rank`: Hạng sao ưa thích
- `user_booking_frequency`: Tần suất đặt phòng
- `user_location`: Vị trí của khách hàng
- `user_device`: Thiết bị sử dụng

#### Item Features:
- `hotel_avg_rating`: Điểm đánh giá trung bình
- `hotel_price_range`: Phạm vi giá
- `hotel_rank`: Hạng sao
- `room_view`: Loại view
- `room_bed_type`: Loại giường

#### Interaction Features:
- `booking_count`: Số lần đặt khách sạn này
- `rating_given`: Điểm đánh giá đã cho
- `coupon_usage`: Có sử dụng coupon không
- `special_requirements`: Yêu cầu đặc biệt

### 5. **Mô Hình Có Thể Xây Dựng**

```python
# Example: Simple matrix factorization
from sklearn.decomposition import TruncatedSVD

# User-Item rating matrix
# Rows: customers, Columns: hotels
# Values: average rating score

# Predict rating cho (user, hotel) chưa có
```

## Queries Hữu Ích Cho Phân Tích

### Tìm khách hàng trung thành:
```sql
SELECT c.customer_name, COUNT(o.order_id) as booking_count
FROM tbl_customers c
JOIN tbl_orderer od ON c.customer_id = od.customer_id
JOIN tbl_order o ON od.orderer_id = o.orderer_id
GROUP BY c.customer_id
HAVING booking_count > 1
ORDER BY booking_count DESC;
```

### Khách sạn được đánh giá cao nhất:
```sql
SELECT h.hotel_name, 
       AVG((e.evaluate_loaction_point + e.evaluate_service_point + 
            e.evaluate_price_point + e.evaluate_sanitary_point + 
            e.evaluate_convenient_point) / 5) as avg_rating,
       COUNT(e.evaluate_id) as review_count
FROM tbl_hotel h
LEFT JOIN tbl_evaluate e ON h.hotel_id = e.hotel_id
GROUP BY h.hotel_id
ORDER BY avg_rating DESC, review_count DESC;
```

### Phân tích giá theo mùa:
```sql
SELECT 
    MONTH(STR_TO_DATE(start_day, '%d-%m-%Y')) as month,
    AVG(total_price) as avg_price,
    COUNT(*) as booking_count
FROM tbl_order
WHERE order_id >= 51
GROUP BY month
ORDER BY month;
```

### User-Item interaction matrix:
```sql
SELECT 
    c.customer_id,
    od.hotel_id,
    COUNT(DISTINCT o.order_id) as booking_count,
    AVG((e.evaluate_loaction_point + e.evaluate_service_point + 
         e.evaluate_price_point + e.evaluate_sanitary_point + 
         e.evaluate_convenient_point) / 5) as avg_rating
FROM tbl_customers c
JOIN tbl_orderer odr ON c.customer_id = odr.customer_id
JOIN tbl_order o ON odr.orderer_id = o.orderer_id
JOIN tbl_order_details od ON o.order_code = od.order_code
LEFT JOIN tbl_evaluate e ON c.customer_id = e.customer_id 
    AND od.hotel_id = e.hotel_id
WHERE o.order_id >= 51
GROUP BY c.customer_id, od.hotel_id;
```

## Mở Rộng Dữ Liệu

Nếu cần nhiều dữ liệu hơn, có thể:
1. Chạy lại script với ID khác
2. Thêm pattern mua theo nhóm (group booking)
3. Thêm dữ liệu negative (cancelled orders)
4. Thêm session data (view without booking)

## Lưu Ý Quan Trọng

⚠️ **Trước khi chạy script:**
- Backup database hiện tại
- Kiểm tra các DELETE statements ở đầu file
- Đảm bảo không có conflict với dữ liệu hiện tại

⚠️ **Sau khi import:**
- Verify data integrity
- Check foreign key constraints
- Update auto_increment values nếu cần

## Liên Hệ & Hỗ Trợ

Nếu gặp vấn đề với dữ liệu được sinh ra, vui lòng:
1. Kiểm tra log errors từ MySQL
2. Verify các foreign key relationships
3. Check data types và formats

---
**Tạo bởi**: AI Assistant
**Ngày tạo**: 2025-10-11
**Phiên bản**: 1.0

