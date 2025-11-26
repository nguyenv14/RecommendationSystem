# 🗄️ Database Integration - Auto Data Sync

## ✅ Đã tích hợp đầy đủ

### 📦 Modules Created

```
src/data/
├── __init__.py
├── connector.py       # 🆕 Database connection (MySQL)
├── normalizer.py      # 🆕 Data normalization
└── processor.py       # 🆕 ETL pipeline & auto-indexing
```

## 🎯 Features

### 1. DatabaseConnector
**File**: `src/data/connector.py`

**Chức năng**: Kết nối MySQL và lấy dữ liệu

**Methods**:
```python
from src.data import DatabaseConnector

db = DatabaseConnector()

# Test connection
db.test_connection()

# Fetch hotels
hotels_df = db.get_hotels(
    hotel_ids=[1, 2, 3],  # Optional: specific IDs
    updated_after=datetime.now(),  # Optional: only updated hotels
    limit=100  # Optional: limit results
)

# Fetch rooms
rooms_df = db.get_rooms(hotel_ids=[1, 2, 3])

# Fetch evaluations
evals_df = db.get_evaluations(hotel_ids=[1, 2, 3])

# Fetch coupons
coupons_df = db.get_coupons(valid_only=True)

# Fetch orders
orders_df = db.get_orders(
    user_ids=[1, 2],
    hotel_ids=[1, 2, 3],
    date_from=datetime(2024, 1, 1),
    date_to=datetime(2024, 12, 31)
)

# Fetch user-hotel interactions (for collaborative filtering)
interactions_df = db.get_user_interactions(user_id=123)
```

**Configuration**:
- Uses settings from `src/config/settings.py`
- Or environment variables:
  - `MYSQL_HOST` (default: localhost)
  - `MYSQL_PORT` (default: 3308)
  - `MYSQL_USER` (default: root)
  - `MYSQL_PASSWORD` (default: root)
  - `MYSQL_DATABASE` (default: myhotel)

### 2. HotelDataNormalizer
**File**: `src/data/normalizer.py`

**Chức năng**: Chuẩn hóa dữ liệu và tạo semantic text

**Methods**:
```python
from src.data import HotelDataNormalizer

normalizer = HotelDataNormalizer()

# Normalize hotels
normalized_hotels = normalizer.normalize_hotels(hotels_df)
# Adds 'semantic_text' column

# Normalize coupons
normalized_coupons = normalizer.normalize_coupons(coupons_df)

# Extract features
features = normalizer.extract_features(hotel_data)

# Create semantic text
semantic_text = normalizer.create_semantic_text(hotel_data)
```

**Semantic Text Format**:
```
Tên: Hotel ABC. Khách sạn cao cấp. Đánh giá: 4.5 sao. 
Địa điểm: Nha Trang. Chi tiết vị trí: Gần biển. 
Mô tả: Khách sạn 5 sao với view biển đẹp...
Tiện nghi: hồ bơi, spa, gym, nhà hàng, wifi. 
Giá: Cao cấp. Từ khóa: biển, resort, sang trọng
```

### 3. DataProcessor
**File**: `src/data/processor.py`

**Chức năng**: ETL pipeline - Database → Normalize → Index

**Methods**:
```python
from src.data import DataProcessor

processor = DataProcessor()

# Process and index hotels
processor.process_and_index_hotels(
    hotel_ids=[1, 2, 3],  # Optional
    limit=100,  # Optional
    recreate_collection=False
)

# Process and index coupons
processor.process_and_index_coupons(
    valid_only=True,
    recreate_collection=False
)

# Auto-sync all
processor.auto_sync(
    sync_hotels=True,
    sync_coupons=True,
    incremental=True  # Don't recreate collections
)
```

**Pipeline Flow**:
```
Database (MySQL)
    ↓ fetch
Raw Data (DataFrame)
    ↓ normalize
Normalized Data + Semantic Text
    ↓ embed
Vector Embeddings
    ↓ index
Qdrant Collections
```

## 🚀 Auto-Sync on Startup

**In `app.py`**: Auto-sync được tích hợp sẵn!

**Enable Auto-Sync**:
```bash
# Set environment variable
export AUTO_SYNC_DATABASE=true

# Or in .env file
AUTO_SYNC_DATABASE=true
```

**Process on startup**:
1. ✅ Initialize all services
2. ✅ Test database connection
3. ✅ Fetch hotels from MySQL
4. ✅ Normalize data
5. ✅ Create semantic embeddings
6. ✅ Index to Qdrant (RAG collections)
7. ✅ Fetch coupons
8. ✅ Normalize and index coupons

## 📊 Usage Examples

### Example 1: Manual sync from database

```python
from src.data import DatabaseConnector, DataProcessor
from src.core import RAGService

# Initialize
db = DatabaseConnector()
rag = RAGService()
processor = DataProcessor(db_connector=db, rag_service=rag)

# Sync all hotels
processor.process_and_index_hotels()

# Sync specific hotels
processor.process_and_index_hotels(hotel_ids=[1, 2, 3])

# Sync only new/updated hotels
from datetime import datetime, timedelta
processor.process_and_index_hotels(
    updated_after=datetime.now() - timedelta(days=7)
)
```

### Example 2: Scheduled sync (cron job)

```python
# sync_data.py
from src.data import DataProcessor
from src.core import RAGService

def main():
    rag = RAGService()
    processor = DataProcessor(rag_service=rag)
    
    # Incremental sync
    processor.auto_sync(
        sync_hotels=True,
        sync_coupons=True,
        incremental=True
    )

if __name__ == '__main__':
    main()
```

Run periodically:
```bash
# Crontab: sync every hour
0 * * * * cd /path/to/project && python sync_data.py
```

### Example 3: API endpoint for manual trigger

```python
# In app.py, add endpoint:

@app.route('/api/admin/sync', methods=['POST'])
def trigger_sync():
    """Manually trigger data sync"""
    try:
        from src.data import DatabaseConnector, DataProcessor
        
        db = DatabaseConnector()
        processor = DataProcessor(
            db_connector=db,
            rag_service=rag_service
        )
        
        data = request.json or {}
        sync_hotels = data.get('sync_hotels', True)
        sync_coupons = data.get('sync_coupons', True)
        incremental = data.get('incremental', True)
        
        success = processor.auto_sync(
            sync_hotels=sync_hotels,
            sync_coupons=sync_coupons,
            incremental=incremental
        )
        
        return jsonify({
            'success': success,
            'message': 'Data sync completed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## ⚙️ Configuration

### Environment Variables

```bash
# Database
MYSQL_HOST=localhost
MYSQL_PORT=3308
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=myhotel

# Auto-sync
AUTO_SYNC_DATABASE=true

# Collections
RAG_COLLECTION_HOTELS=hotels_rag
RAG_COLLECTION_COUPONS=coupons_rag
```

### In code

```python
from src.config import get_settings

settings = get_settings()

# Access database config
db_config = {
    'host': settings.MYSQL_HOST,
    'port': settings.MYSQL_PORT,
    'user': settings.MYSQL_USER,
    'password': settings.MYSQL_PASSWORD,
    'database': settings.MYSQL_DATABASE
}

# Or get connection string
conn_string = settings.get_mysql_connection_string()
```

## 🔧 Troubleshooting

### Database connection fails

```bash
# Check MySQL is running
docker ps | grep mysql

# Test connection
python -c "from src.data import DatabaseConnector; db = DatabaseConnector(); db.test_connection()"

# Check credentials
echo $MYSQL_HOST $MYSQL_PORT $MYSQL_USER
```

### Auto-sync not running

```bash
# Check AUTO_SYNC_DATABASE is set
echo $AUTO_SYNC_DATABASE

# Check logs
# Look for: "🔄 Auto-syncing data from database..."

# Run manually
python -c "from src.data import DataProcessor; p = DataProcessor(); p.auto_sync()"
```

### No data indexed

```bash
# Check database has data
mysql -h localhost -P 3308 -u root -proot myhotel -e "SELECT COUNT(*) FROM tbl_hotel"

# Check Qdrant collections
curl http://localhost:6333/collections
```

## ✅ Checklist

- [x] Database connector implemented
- [x] Data normalizer implemented
- [x] ETL processor implemented
- [x] Auto-sync on startup
- [x] Incremental sync support
- [x] Hotels sync
- [x] Coupons sync
- [x] Configuration via settings
- [x] Error handling
- [x] Logging

## 🎉 Benefits

✅ **Tự động hóa** - Auto-sync on startup
✅ **Chuẩn hóa** - Clean, semantic text
✅ **Linh hoạt** - Manual or auto sync
✅ **Incremental** - Only sync changes
✅ **Configurable** - Via environment
✅ **Production-ready** - Error handling, logging

---

**Version**: 3.0 Complete  
**Status**: ✅ Fully Integrated  
**Database**: MySQL → Qdrant via ETL

