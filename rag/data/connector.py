#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Connector Module
Kết nối MySQL và lấy dữ liệu khách sạn
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Kết nối database MySQL và lấy dữ liệu khách sạn"""
    
    def __init__(self,
                 host: str = None,
                 port: int = None,
                 user: str = None,
                 password: str = None,
                 database: str = None,
                 charset: str = 'utf8mb4'):
        """
        Initialize database connector
        
        Args:
            host: MySQL host (default: from env or localhost)
            port: MySQL port (default: from env or 3308)
            user: MySQL user (default: from env or root)
            password: MySQL password (default: from env or root)
            database: Database name (default: from env or rag_db)
            charset: Character set (default: utf8mb4)
        """
        # Get config from environment or use defaults
        self.host = host or os.environ.get('MYSQL_HOST', 'localhost')
        self.port = port or int(os.environ.get('MYSQL_PORT', '3308'))
        self.user = user or os.environ.get('MYSQL_USER', 'root')
        self.password = password or os.environ.get('MYSQL_PASSWORD', 'root')
        self.database = database or os.environ.get('MYSQL_DATABASE', 'rag_db')
        self.charset = charset
        
        # Create connection string
        self.connection_string = (
            f"mysql+pymysql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}?charset={charset}"
        )
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=False
        )
        
        logger.info(f"Database connector initialized: {self.host}:{self.port}/{self.database}")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            
            # Ensure metadata table exists on connection test
            try:
                self._ensure_metadata_table_exists()
            except Exception as e:
                logger.warning(f"Could not ensure metadata table exists: {e}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def get_hotels(self, 
                   hotel_ids: Optional[List[int]] = None,
                   updated_after: Optional[datetime] = None,
                   limit: Optional[int] = None) -> pd.DataFrame:
        """
        Lấy dữ liệu khách sạn từ database
        
        Args:
            hotel_ids: List of hotel IDs to fetch (None = all)
            updated_after: Only fetch hotels updated after this datetime
            limit: Maximum number of hotels to fetch
            
        Returns:
            DataFrame với thông tin khách sạn
        """
        logger.info("Fetching hotels from database...")
        
        # Build query
        query = """
        SELECT 
            h.hotel_id,
            h.hotel_name,
            h.hotel_desc,
            h.hotel_rank,
            h.hotel_price_average,
            h.hotel_placedetails,
            h.hotel_tag_keyword,
            h.hotel_image,
            h.area_id,
            h.brand_id,
            h.created_at,
            h.updated_at,
            a.area_name,
            a.area_desc,
            b.brand_name,
            b.brand_desc
        FROM tbl_hotel h
        LEFT JOIN tbl_area a ON h.area_id = a.area_id
        LEFT JOIN tbl_brand b ON h.brand_id = b.brand_id
        WHERE 1=1
        """
        
        params = {}
        
        # Filter by hotel IDs
        if hotel_ids:
            placeholders = ','.join([':hotel_id_' + str(i) for i in range(len(hotel_ids))])
            query += f" AND h.hotel_id IN ({placeholders})"
            for i, hotel_id in enumerate(hotel_ids):
                params[f'hotel_id_{i}'] = hotel_id
        
        # Filter by updated_at
        if updated_after:
            query += " AND (h.updated_at > :updated_after OR h.created_at > :updated_after)"
            params['updated_after'] = updated_after
        
        # Order by hotel_id
        query += " ORDER BY h.hotel_id"
        
        # Limit
        if limit:
            query += " LIMIT :limit"
            params['limit'] = limit
        
        try:
            # Execute query
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
            
            logger.info(f"Fetched {len(df)} hotels from database")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching hotels: {e}")
            raise
    
    def get_hotel_count(self) -> int:
        """Get total number of hotels"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) as count FROM tbl_hotel"))
                count = result.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"Error getting hotel count: {e}")
            return 0
    
    def _ensure_metadata_table_exists(self):
        """Ensure rag_index_metadata table exists"""
        try:
            with self.engine.connect() as conn:
                # Create table if not exists
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS rag_index_metadata (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        last_indexed_at DATETIME NOT NULL,
                        indexed_hotels INT DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_last_indexed (last_indexed_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """))
                conn.commit()
                logger.debug("✅ rag_index_metadata table ensured")
        except Exception as e:
            logger.error(f"Error creating rag_index_metadata table: {e}")
            raise
    
    def get_last_indexed_timestamp(self) -> Optional[datetime]:
        """
        Get timestamp of last indexing
        Lưu timestamp vào database hoặc file để track lần index cuối
        """
        try:
            # Ensure table exists
            self._ensure_metadata_table_exists()
            
            with self.engine.connect() as conn:
                # Get latest timestamp
                result = conn.execute(text("""
                    SELECT last_indexed_at 
                    FROM rag_index_metadata 
                    ORDER BY id DESC 
                    LIMIT 1
                """))
                row = result.fetchone()
                
                if row:
                    return row[0]
                return None
                
        except Exception as e:
            logger.warning(f"Could not get last indexed timestamp: {e}")
            return None
    
    def save_indexed_timestamp(self, timestamp: datetime, indexed_count: int = 0):
        """
        Save timestamp of indexing
        
        Args:
            timestamp: Timestamp of indexing
            indexed_count: Number of hotels indexed
        """
        try:
            # Ensure table exists
            self._ensure_metadata_table_exists()
            
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO rag_index_metadata (last_indexed_at, indexed_hotels)
                    VALUES (:timestamp, :count)
                """), {
                    'timestamp': timestamp,
                    'count': indexed_count
                })
                conn.commit()
                logger.info(f"✅ Saved indexed timestamp: {timestamp}, count: {indexed_count}")
        except Exception as e:
            logger.error(f"Error saving indexed timestamp: {e}")
            raise
    
    def get_new_or_updated_hotels(self, last_indexed_at: Optional[datetime] = None) -> pd.DataFrame:
        """
        Get hotels that are new or updated since last indexing
        
        Args:
            last_indexed_at: Timestamp of last indexing
            
        Returns:
            DataFrame với hotels mới hoặc đã cập nhật
        """
        if last_indexed_at is None:
            # Get all hotels if no last_indexed_at
            return self.get_hotels()
        else:
            return self.get_hotels(updated_after=last_indexed_at)
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()
        logger.info("Database connection closed")


def main():
    """Test database connector"""
    print("🧪 Testing Database Connector...")
    
    # Initialize connector
    connector = DatabaseConnector()
    
    # Test connection
    if not connector.test_connection():
        print("❌ Connection failed. Please check database configuration.")
        return
    
    # Get hotel count
    count = connector.get_hotel_count()
    print(f"📊 Total hotels in database: {count}")
    
    # Get first 5 hotels
    print("\n📦 Fetching first 5 hotels...")
    hotels_df = connector.get_hotels(limit=5)
    print(f"Fetched {len(hotels_df)} hotels")
    print("\nSample data:")
    print(hotels_df[['hotel_id', 'hotel_name', 'area_name', 'hotel_rank']].head())
    
    # Test incremental fetching
    print("\n🔄 Testing incremental fetching...")
    last_timestamp = connector.get_last_indexed_timestamp()
    if last_timestamp:
        print(f"Last indexed: {last_timestamp}")
        new_hotels = connector.get_new_or_updated_hotels(last_timestamp)
        print(f"New/updated hotels: {len(new_hotels)}")
    else:
        print("No previous indexing found")
    
    connector.close()
    print("\n✅ Test complete!")


if __name__ == "__main__":
    main()

