#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate realistic hotel booking data for recommendation system training
Generates data for: customers, orders, order_details, orderers, evaluations, payments
"""

import random
import datetime
from datetime import timedelta
from faker import Faker
import json

# Initialize Faker for Vietnamese names
fake = Faker('vi_VN')
Faker.seed(42)
random.seed(42)

# Hotel data từ database (hotel_id, hotel_name, hotel_rank, average_price)
HOTELS = [
    (2, 'Meliá Vinpearl Riverfront', 5, 1311127),
    (3, 'Mường Thanh Luxury', 5, 1490564),
    (4, 'Sheraton Grand Resort', 5, 1381737),
    (5, 'The Nalod', 5, 1274957),
    (6, 'Khách sạn Grand Tourane', 5, 1523515),
    (7, 'Khách Sạn Radisson', 5, 3520000),
    (8, 'Khách Sạn Greenery', 4, 1573333),
    (9, 'Mikazuki Japanese', 5, 3851149),
    (10, 'Le Sands Oceanfront', 4, 4397606),
    (11, 'Khách Sạn Dana Marina', 4, 3643033),
    (12, 'Khách Sạn Mỹ Khê 2', 3, 2907143),
    (13, 'Khách Sạn Bình Dương', 3, 2867667),
    (14, 'Khách Sạn FIVITEL Queen', 3, 2290768),
    (15, 'Four Points by Sheraton', 5, 2921454),
    (16, 'Khách sạn Mandila Beach', 5, 3088288),
    (17, 'Đà Nẵng Golden Bay', 5, 3057143),
    (18, 'Cicilia Hotels & Spa Danang', 4, 2625000),
    (19, 'The Blossom Resort Island', 4, 2320250),
    (20, 'Khách Sạn Eden Ocean View', 4, 2026580),
    (21, 'Risemount Premier Resort', 5, 1715143),
    (22, 'Hải Âu Hotel', 3, 1000000),
]

# Room data (hotel_id -> list of (room_id, room_name, capacity))
ROOMS = {
    2: [(6, 'Deluxe Room', 2), (7, 'Deluxe Room Horizon View', 2), (8, 'Grand Premium Room', 2)],
    3: [(2, 'Phòng Grand Suite', 2), (3, 'Phòng Deluxe King', 2), (5, 'Phòng Premier Deluxe Twin', 2)],
    4: [(9, 'Phòng Deluxe King', 1), (10, 'Phòng Premier Deluxe Twin', 2), (11, 'Deluxe Room', 3)],
    5: [(12, 'Phòng Deluxe King', 1), (13, 'Phòng Premier Deluxe Twin', 2), (14, 'Phòng Deluxe Twin', 3)],
    6: [(15, 'Superior City View Twin', 2), (16, 'Superior City View Queen Bed', 2), (17, 'Superior Ocean View Twin', 2)],
    7: [(18, 'Deluxe Twin Room', 2), (19, 'Deluxe Double City View', 2), (20, 'Premium Ocean View', 2)],
    8: [(21, 'Superior Twin', 2), (22, 'Deluxe Twin', 2), (23, 'Suite Double', 2)],
    9: [(24, 'Deluxe Double Panoramic Ocean View', 2), (25, 'Deluxe Twin Panoramic Ocean View', 2), (26, 'Premium Deluxe Double Panoramic Ocean View', 2)],
    10: [(27, 'Deluxe Ocean Twin', 2), (28, 'Deluxe Ocean Double', 2), (29, 'Premier Oceanfront Twin', 2)],
    11: [(30, 'Superior Twin', 2), (31, 'Superior King', 2), (32, 'Deluxe King', 2)],
    12: [(33, 'Superior I Double/Twin', 2), (34, 'Superior II Double/Twin', 2), (35, 'SENIOR DOUBLE', 2)],
    13: [(36, 'Superior Double Or Twin Room', 2), (37, 'Deluxe Double Or Twin Balcony Room', 2), (38, 'Deluxe Triple Balcony Room', 2)],
    14: [(39, 'Superior Double city View', 2), (40, 'Superior Twin', 2), (41, 'Deluxe Double', 2)],
    15: [(42, 'Superior King Ocean View', 2), (43, 'Superior Twin Bay View', 2), (44, 'Deluxe King/Twin Ocean View', 2)],
    16: [(45, 'Deluxe Twin', 2), (46, 'Deluxe Partial Ocean Twin', 2), (47, 'Deluxe Partial Ocean King', 2)],
    17: [(48, 'Superior Twin/King', 2), (49, 'Deluxe Twin/King', 2), (50, 'Deluxe Golden Bay King/Twin', 2)],
    18: [(51, 'Deluxe City View', 2), (52, 'Deluxe Partial Ocean View', 2), (53, 'Junior Suite Ocean View', 2)],
    19: [(54, 'Superior King Room', 2), (55, 'Deluxe King Room', 2), (56, 'Deluxe King Room with Street View', 2)],
    20: [(57, 'Classic Double', 2), (58, 'Deluxe Twin city view', 2), (59, 'Premium Sea Side Twin', 2)],
    21: [(60, 'Superior King Room', 2), (61, 'Deluxe King Có Ban Công', 2), (62, 'Superior Twin Room', 2)],
    22: [(63, 'Standard Double', 2), (64, 'Superior Double', 2), (65, 'Deluxe Double', 2)],
}

# Type room prices (room_id -> list of (type_room_id, bed_type, price, has_sale))
TYPE_ROOMS = {
    6: [(7, 1, 1305636, True), (8, 2, 1500000, False), (16, 1, 1100000, False)],
    7: [(9, 1, 1400000, True), (11, 2, 1305636, False)],
    8: [(13, 1, 1200000, False), (15, 2, 1500000, True)],
    2: [(1, 2, 1400000, True), (4, 2, 1500000, False), (42, 3, 1305636, True)],
    3: [(2, 1, 1500000, True), (37, 3, 1600000, True), (38, 3, 1700000, True)],
    5: [(3, 3, 1500000, False), (39, 3, 1700000, False), (40, 3, 1700000, True)],
    9: [(17, 1, 1530000, False), (18, 2, 999999, True), (19, 3, 1500000, True)],
    10: [(20, 1, 1400000, False), (21, 2, 1200000, True), (22, 3, 1500000, True)],
    11: [(23, 1, 1500000, False), (24, 2, 1500000, True), (25, 3, 1305636, True)],
    12: [(26, 1, 800000, True), (27, 2, 1500000, True), (28, 3, 1500000, True)],
    13: [(29, 1, 1234440, False), (30, 2, 1500000, True), (31, 3, 1200000, True)],
    14: [(32, 1, 1235555, False), (33, 2, 1200000, True), (34, 3, 1454533, True)],
    15: [(43, 3, 1200000, True), (44, 1, 1700000, True), (45, 2, 1800000, True)],
    18: [(73, 2, 1700000, False), (72, 2, 3500000, True)],
    19: [(72, 2, 3500000, False)],
    24: [(62, 2, 3450000, True)],
    27: [(75, 2, 3400000, False)],
    29: [(79, 2, 3055064, False)],
    30: [(81, 2, 3400000, False)],
    33: [(87, 2, 2700000, False)],
    42: [(109, 2, 1700000, False), (110, 2, 3068939, False)],
    45: [(117, 2, 1703000, False)],
    48: [(125, 2, 2300000, False)],
    51: [(132, 2, 1200000, False)],
    54: [(140, 2, 2200000, False)],
    56: [(147, 2, 2075000, False)],
    57: [(148, 2, 1400000, False)],
    60: [(156, 2, 2200000, False)],
    62: [(161, 2, 1500000, False)],
    63: [(170, 2, 800000, False)],
    64: [(171, 2, 1000000, False)],
    65: [(172, 2, 1200000, False)],
}

# Vietnamese names
FIRST_NAMES = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý']
MIDDLE_NAMES = ['Văn', 'Thị', 'Hữu', 'Đức', 'Minh', 'Thanh', 'Quốc', 'Hải', 'Thu', 'Hoàng']
LAST_NAMES = ['Anh', 'Bình', 'Cường', 'Dũng', 'Hùng', 'Lan', 'Linh', 'Mai', 'Nga', 'Trang', 'Long', 'Nam', 'Phong', 'Hạnh', 'Hương']

LOCATIONS = ['Đà Nẵng', 'Hà Nội', 'TP.HCM', 'Hải Phòng', 'Cần Thơ', 'Huế', 'Nha Trang', 'Đà Lạt', 'Vũng Tàu', 'Quy Nhơn']

# Evaluation templates
EVAL_TITLES = [
    'Tuyệt vời', 'Rất tốt', 'Hài lòng', 'Ổn', 'Không tốt lắm', 'Xuất sắc', 'Tốt',
    'Khá ổn', 'Thất vọng', 'Hoàn hảo', 'Đáng giá tiền', 'Sẽ quay lại', 'Tuyệt với',
    'Dịch vụ tốt', 'Phòng đẹp', 'Vị trí thuận lợi', 'Giá hợp lý', 'Sạch sẽ'
]

EVAL_CONTENTS = [
    'Khách sạn rất tuyệt vời, dịch vụ chu đáo, nhân viên thân thiện.',
    'Phòng sạch sẽ, tiện nghi đầy đủ, view đẹp.',
    'Vị trí thuận lợi, gần biển, dễ đi lại.',
    'Giá cả hợp lý so với chất lượng.',
    'Nhân viên phục vụ rất tốt, nhiệt tình.',
    'Bữa sáng ngon, đa dạng món ăn.',
    'Phòng hơi chật, tiện nghi chưa đầy đủ lắm.',
    'Không gian thoáng đãng, thoải mái.',
    'Đồ ăn ngon, view đẹp, sẽ quay lại.',
    'Hồ bơi sạch sẽ, khu vực giải trí đa dạng.',
    'Phục vụ nhanh chóng, chuyên nghiệp.',
    'Phòng cách âm tốt, yên tĩnh.',
    'Giá hơi cao so với chất lượng.',
    'Wifi nhanh, ổn định.',
    'Vệ sinh sạch sẽ, khăn trải giường mới.',
]

COUPONS = [
    ('HELLOVKU', 0.05),
    ('CHAODANANG', 0.09),
    ('SEPNGUYEN', 0.14),
    (None, 0)
]

PAYMENT_METHODS = [1, 2, 3, 4]  # 1: cash, 2: card, 3: momo, 4: banking
ORDER_STATUSES = [0, 1, 2, -2]  # 0: pending, 1: confirmed, 2: completed, -2: cancelled

class HotelBookingDataGenerator:
    def __init__(self):
        self.customer_id_start = 250  # Tránh conflict với customers hiện có
        self.order_id_start = 1000    # Database có orders đến 775
        self.orderer_id_start = 1000  # Database có orderers đến 775
        self.payment_id_start = 1000  # Database có payments đến 775
        self.order_details_id_start = 1000  # Bắt đầu từ 1000
        self.evaluate_id_start = 1000       # Bắt đầu từ 1000
        
        self.customers = []
        self.orders = []
        self.orderers = []
        self.payments = []
        self.order_details = []
        self.evaluates = []
        
        # Start from 2024-01-01 to 2024-12-31
        self.start_date = datetime.datetime(2024, 1, 1)
        self.end_date = datetime.datetime(2024, 12, 31)
    
    def generate_customer_name(self):
        """Generate Vietnamese name"""
        first = random.choice(FIRST_NAMES)
        middle = random.choice(MIDDLE_NAMES)
        last = random.choice(LAST_NAMES)
        return f"{first} {middle} {last}"
    
    def generate_phone(self):
        """Generate Vietnamese phone number"""
        return random.randint(300000000, 999999999)
    
    def generate_email(self, name):
        """Generate email from name"""
        # Convert Vietnamese name to ascii
        name_parts = name.lower().split()
        email_name = ''.join(name_parts)
        # Remove Vietnamese characters (simplified)
        replacements = {
            'đ': 'd', 'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        }
        for vn, en in replacements.items():
            email_name = email_name.replace(vn, en)
        
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'vku.udn.vn']
        return f"{email_name}{random.randint(1, 999)}@{random.choice(domains)}"
    
    def generate_random_date(self, start, end):
        """Generate random date between start and end"""
        delta = end - start
        random_days = random.randint(0, delta.days)
        return start + timedelta(days=random_days)
    
    def generate_customers(self, num_customers=100):
        """Generate customer data"""
        print(f"Generating {num_customers} customers...")
        
        for i in range(num_customers):
            customer_id = self.customer_id_start + i
            name = self.generate_customer_name()
            phone = self.generate_phone()
            email = self.generate_email(name)
            created_at = self.generate_random_date(self.start_date, self.end_date)
            location = random.choice(LOCATIONS)
            
            self.customers.append({
                'customer_id': customer_id,
                'customer_name': name,
                'customer_phone': phone,
                'customer_email': email,
                'customer_password': 'e10adc3949ba59abbe56e057f20f883e',  # MD5 of '123456'
                'customer_status': 1,
                'customer_ip': '127.0.0.1',
                'customer_located': location,
                'customer_device': 'Mozilla/5.0',
                'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
    
    def generate_orders(self, num_orders=2000):
        """Generate order data with related orderer, payment, order_details, evaluate"""
        print(f"Generating {num_orders} orders with related data...")
        
        # Get all customer IDs (existing + new)
        existing_customer_ids = list(range(3, 150))  # Existing customers from DB
        new_customer_ids = [c['customer_id'] for c in self.customers]
        all_customer_ids = existing_customer_ids + new_customer_ids
        
        # Pre-filter hotels that have valid room and type_room data
        valid_hotels = []
        for hotel in HOTELS:
            hotel_id = hotel[0]
            if hotel_id in ROOMS:
                for room in ROOMS[hotel_id]:
                    room_id = room[0]
                    if room_id in TYPE_ROOMS:
                        valid_hotels.append(hotel)
                        break
        
        if not valid_hotels:
            print("Error: No valid hotels with room data!")
            return
        
        print(f"Found {len(valid_hotels)} hotels with valid room data")
        
        generated_count = 0
        attempts = 0
        max_attempts = num_orders * 3  # Allow more attempts
        
        while generated_count < num_orders and attempts < max_attempts:
            attempts += 1
            
            order_id = self.order_id_start + generated_count
            orderer_id = self.orderer_id_start + generated_count
            payment_id = self.payment_id_start + generated_count
            
            # Random customer
            customer_id = random.choice(all_customer_ids)
            
            # Random hotel (from valid hotels only)
            hotel = random.choice(valid_hotels)
            hotel_id, hotel_name, hotel_rank, _ = hotel
            
            # Random room for this hotel
            if hotel_id not in ROOMS:
                continue
            room = random.choice(ROOMS[hotel_id])
            room_id, room_name, capacity = room
            
            # Random type room for this room
            if room_id not in TYPE_ROOMS:
                continue
            type_room = random.choice(TYPE_ROOMS[room_id])
            type_room_id, bed_type, base_price, has_sale = type_room
            
            # Calculate price with potential sale
            if has_sale:
                price = base_price * random.uniform(0.7, 0.95)
            else:
                price = base_price
            
            # Hotel fee (random 0-200k)
            hotel_fee = random.choice([0, 100000, 150000, 200000])
            
            # Random dates
            start_date = self.generate_random_date(self.start_date, self.end_date)
            num_nights = random.randint(1, 7)
            end_date = start_date + timedelta(days=num_nights)
            
            # Calculate total price
            room_total = price * num_nights + hotel_fee
            
            # Random coupon
            coupon_code, coupon_discount = random.choice(COUPONS)
            coupon_sale_price = room_total * coupon_discount if coupon_code else 0
            total_price = int(room_total - coupon_sale_price)
            
            # Random order status
            order_status = random.choices(
                ORDER_STATUSES,
                weights=[10, 15, 60, 15],  # More completed orders for training
                k=1
            )[0]
            
            # Random payment
            payment_method = random.choice(PAYMENT_METHODS)
            payment_status = 1 if order_status in [1, 2] else 0
            
            # Order code
            order_code = f"MYHOTEL{random.randint(1000, 9999)}"
            
            # Get customer info for orderer
            if customer_id in new_customer_ids:
                customer = next(c for c in self.customers if c['customer_id'] == customer_id)
                customer_name = customer['customer_name']
                customer_email = customer['customer_email']
                customer_phone = str(customer['customer_phone'])
            else:
                # For existing customers, generate random data
                customer_name = self.generate_customer_name()
                customer_email = self.generate_email(customer_name)
                customer_phone = str(self.generate_phone())
            
            # Create orderer
            self.orderers.append({
                'orderer_id': orderer_id,
                'customer_id': customer_id,
                'orderer_name': customer_name,
                'orderer_phone': customer_phone,
                'orderer_email': customer_email,
                'orderer_type_bed': random.randint(1, 3),
                'orderer_special_requirements': random.choice([0, 0, 0, 1, 2, 3]),
                'orderer_own_require': 'Không có',
                'orderer_bill_require': 1,
                'created_at': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            })
            
            # Create payment
            self.payments.append({
                'payment_id': payment_id,
                'payment_method': payment_method,
                'payment_status': payment_status,
            })
            
            # Create order
            self.orders.append({
                'order_id': order_id,
                'start_day': start_date.strftime('%d-%m-%Y'),
                'end_day': end_date.strftime('%d-%m-%Y'),
                'orderer_id': orderer_id,
                'payment_id': payment_id,
                'order_status': order_status,
                'order_code': order_code,
                'coupon_name_code': coupon_code if coupon_code else 'Không có',
                'coupon_sale_price': int(coupon_sale_price) if coupon_code else None,
                'total_price': total_price,
                'created_at': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                'order_type': 0,  # 0: hotel booking
            })
            
            # Create order details
            order_details_id = self.order_details_id_start + generated_count
            self.order_details.append({
                'order_details_id': order_details_id,
                'order_code': order_code,
                'hotel_id': hotel_id,
                'hotel_name': hotel_name,
                'room_id': room_id,
                'room_name': room_name,
                'type_room_id': type_room_id,
                'price_room': int(price * num_nights),
                'hotel_fee': hotel_fee,
                'created_at': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            })
            
            # Create evaluation for completed orders (70% chance)
            if order_status == 2 and random.random() < 0.7:
                evaluate_id = self.evaluate_id_start + len(self.evaluates)
                
                # Generate realistic ratings based on hotel rank
                base_rating = hotel_rank  # 3-5 stars hotel
                
                # Add some variance
                location_point = max(1, min(5, base_rating + random.randint(-1, 1)))
                service_point = max(1, min(5, base_rating + random.randint(-1, 1)))
                price_point = max(1, min(5, base_rating + random.randint(-2, 0)))  # Price usually lower
                sanitary_point = max(1, min(5, base_rating + random.randint(-1, 1)))
                convenient_point = max(1, min(5, base_rating + random.randint(-1, 1)))
                
                self.evaluates.append({
                    'evaluate_id': evaluate_id,
                    'customer_id': customer_id,
                    'customer_name': customer_name,
                    'hotel_id': hotel_id,
                    'room_id': room_id,
                    'type_room_id': type_room_id,
                    'evaluate_title': random.choice(EVAL_TITLES),
                    'evaluate_content': random.choice(EVAL_CONTENTS),
                    'evaluate_loaction_point': location_point,
                    'evaluate_service_point': service_point,
                    'evaluate_price_point': price_point,
                    'evaluate_sanitary_point': sanitary_point,
                    'evaluate_convenient_point': convenient_point,
                    'created_at': (end_date + timedelta(days=random.randint(0, 3))).strftime('%Y-%m-%d %H:%M:%S'),
                })
            
            # Increment generated count
            generated_count += 1
        
        print(f"Generated {generated_count} orders (attempted {attempts} times)")
    
    def generate_sql(self, output_file='generated_hotel_booking_data.sql'):
        """Generate SQL file"""
        print(f"\nGenerating SQL file: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("-- Generated Hotel Booking Data for Recommendation System Training\n")
            f.write("-- Generated on: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
            
            # Customers
            f.write("-- ====================================\n")
            f.write("-- CUSTOMERS\n")
            f.write("-- ====================================\n\n")
            if self.customers:
                f.write("INSERT INTO `tbl_customers` (`customer_id`, `customer_name`, `customer_phone`, `customer_email`, `customer_password`, `customer_status`, `customer_ip`, `customer_located`, `customer_device`, `created_at`, `updated_at`, `deleted_at`) VALUES\n")
                for i, customer in enumerate(self.customers):
                    values = f"({customer['customer_id']}, '{customer['customer_name']}', {customer['customer_phone']}, '{customer['customer_email']}', '{customer['customer_password']}', {customer['customer_status']}, '{customer['customer_ip']}', '{customer['customer_located']}', '{customer['customer_device']}', '{customer['created_at']}', '{customer['updated_at']}', NULL)"
                    if i < len(self.customers) - 1:
                        f.write(values + ",\n")
                    else:
                        f.write(values + ";\n\n")
            
            # Orderers
            f.write("-- ====================================\n")
            f.write("-- ORDERERS\n")
            f.write("-- ====================================\n\n")
            if self.orderers:
                f.write("INSERT INTO `tbl_orderer` (`orderer_id`, `customer_id`, `orderer_name`, `orderer_phone`, `orderer_email`, `orderer_type_bed`, `orderer_special_requirements`, `orderer_own_require`, `orderer_bill_require`, `created_at`, `updated_at`) VALUES\n")
                for i, orderer in enumerate(self.orderers):
                    values = f"({orderer['orderer_id']}, {orderer['customer_id']}, '{orderer['orderer_name']}', '{orderer['orderer_phone']}', '{orderer['orderer_email']}', {orderer['orderer_type_bed']}, {orderer['orderer_special_requirements']}, '{orderer['orderer_own_require']}', {orderer['orderer_bill_require']}, '{orderer['created_at']}', NULL)"
                    if i < len(self.orderers) - 1:
                        f.write(values + ",\n")
                    else:
                        f.write(values + ";\n\n")
            
            # Payments
            f.write("-- ====================================\n")
            f.write("-- PAYMENTS\n")
            f.write("-- ====================================\n\n")
            if self.payments:
                f.write("INSERT INTO `tbl_payment` (`payment_id`, `payment_method`, `payment_status`) VALUES\n")
                for i, payment in enumerate(self.payments):
                    values = f"({payment['payment_id']}, {payment['payment_method']}, {payment['payment_status']})"
                    if i < len(self.payments) - 1:
                        f.write(values + ",\n")
                    else:
                        f.write(values + ";\n\n")
            
            # Orders
            f.write("-- ====================================\n")
            f.write("-- ORDERS\n")
            f.write("-- ====================================\n\n")
            if self.orders:
                f.write("INSERT INTO `tbl_order` (`order_id`, `start_day`, `end_day`, `orderer_id`, `payment_id`, `order_status`, `order_code`, `coupon_name_code`, `coupon_sale_price`, `total_price`, `created_at`, `updated_at`, `deleted_at`, `order_type`, `restaurant_id`) VALUES\n")
                for i, order in enumerate(self.orders):
                    coupon_price = f"{order['coupon_sale_price']}" if order['coupon_sale_price'] is not None else "NULL"
                    values = f"({order['order_id']}, '{order['start_day']}', '{order['end_day']}', {order['orderer_id']}, {order['payment_id']}, {order['order_status']}, '{order['order_code']}', '{order['coupon_name_code']}', {coupon_price}, {order['total_price']}, '{order['created_at']}', NULL, NULL, {order['order_type']}, NULL)"
                    if i < len(self.orders) - 1:
                        f.write(values + ",\n")
                    else:
                        f.write(values + ";\n\n")
            
            # Order Details
            f.write("-- ====================================\n")
            f.write("-- ORDER DETAILS\n")
            f.write("-- ====================================\n\n")
            if self.order_details:
                f.write("INSERT INTO `tbl_order_details` (`order_details_id`, `order_code`, `hotel_id`, `hotel_name`, `room_id`, `room_name`, `type_room_id`, `price_room`, `hotel_fee`, `created_at`, `updated_at`) VALUES\n")
                for i, detail in enumerate(self.order_details):
                    values = f"({detail['order_details_id']}, '{detail['order_code']}', {detail['hotel_id']}, '{detail['hotel_name']}', {detail['room_id']}, '{detail['room_name']}', {detail['type_room_id']}, {detail['price_room']}, {detail['hotel_fee']}, '{detail['created_at']}', NULL)"
                    if i < len(self.order_details) - 1:
                        f.write(values + ",\n")
                    else:
                        f.write(values + ";\n\n")
            
            # Evaluations
            f.write("-- ====================================\n")
            f.write("-- EVALUATIONS\n")
            f.write("-- ====================================\n\n")
            if self.evaluates:
                f.write("INSERT INTO `tbl_evaluate` (`evaluate_id`, `customer_id`, `customer_name`, `hotel_id`, `room_id`, `type_room_id`, `evaluate_title`, `evaluate_content`, `evaluate_loaction_point`, `evaluate_service_point`, `evaluate_price_point`, `evaluate_sanitary_point`, `evaluate_convenient_point`, `created_at`, `updated_at`, `deleted_at`) VALUES\n")
                for i, evaluate in enumerate(self.evaluates):
                    values = f"({evaluate['evaluate_id']}, {evaluate['customer_id']}, '{evaluate['customer_name']}', {evaluate['hotel_id']}, {evaluate['room_id']}, {evaluate['type_room_id']}, '{evaluate['evaluate_title']}', '{evaluate['evaluate_content']}', {evaluate['evaluate_loaction_point']}, {evaluate['evaluate_service_point']}, {evaluate['evaluate_price_point']}, {evaluate['evaluate_sanitary_point']}, {evaluate['evaluate_convenient_point']}, '{evaluate['created_at']}', NULL, NULL)"
                    if i < len(self.evaluates) - 1:
                        f.write(values + ",\n")
                    else:
                        f.write(values + ";\n\n")
            
            # Summary
            f.write("\n-- ====================================\n")
            f.write("-- SUMMARY\n")
            f.write("-- ====================================\n")
            f.write(f"-- Customers: {len(self.customers)}\n")
            f.write(f"-- Orders: {len(self.orders)}\n")
            f.write(f"-- Orderers: {len(self.orderers)}\n")
            f.write(f"-- Payments: {len(self.payments)}\n")
            f.write(f"-- Order Details: {len(self.order_details)}\n")
            f.write(f"-- Evaluations: {len(self.evaluates)}\n")
        
        print(f"✓ Generated {len(self.customers)} customers")
        print(f"✓ Generated {len(self.orders)} orders")
        print(f"✓ Generated {len(self.orderers)} orderers")
        print(f"✓ Generated {len(self.payments)} payments")
        print(f"✓ Generated {len(self.order_details)} order details")
        print(f"✓ Generated {len(self.evaluates)} evaluations")
        print(f"\n✓ SQL file saved: {output_file}")

def main():
    print("="*60)
    print("HOTEL BOOKING DATA GENERATOR FOR RECOMMENDATION SYSTEM")
    print("="*60)
    print()
    
    generator = HotelBookingDataGenerator()
    
    # Generate data
    print("Generating training data for recommendation system...")
    print("This will create diverse and realistic booking patterns\n")
    
    generator.generate_customers(num_customers=150)  # More customers for diversity
    generator.generate_orders(num_orders=5000)  # 5000 orders for better training
    
    # Generate SQL file
    generator.generate_sql('generated_hotel_booking_data.sql')
    
    print("\n" + "="*60)
    print("COMPLETED!")
    print("="*60)
    print("\nYou can now import this SQL file into your database:")
    print("mysql -u your_user -p your_database < generated_hotel_booking_data.sql")

if __name__ == "__main__":
    main()

