"""
Database Connector
Unified database connection and data fetching
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from ..shared import get_logger
from ..config import get_settings

logger = get_logger(__name__)


class DatabaseConnector:
    """
    Database connector for MySQL
    Fetch hotels, rooms, orders, evaluations, coupons
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None
    ):
        """
        Initialize database connector
        
        Args:
            host: MySQL host (from settings if None)
            port: MySQL port (from settings if None)
            user: MySQL user (from settings if None)
            password: MySQL password (from settings if None)
            database: Database name (from settings if None)
        """
        settings = get_settings()
        
        self.host = host or settings.MYSQL_HOST
        self.port = port or settings.MYSQL_PORT
        self.user = user or settings.MYSQL_USER
        self.password = password or settings.MYSQL_PASSWORD
        self.database = database or settings.MYSQL_DATABASE
        
        # Create connection string
        self.connection_string = settings.get_mysql_connection_string()
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        
        logger.info(f"✅ DatabaseConnector initialized: {self.host}:{self.port}/{self.database}")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def get_hotels(
        self,
        hotel_ids: Optional[List[int]] = None,
        updated_after: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch hotels from database with enriched data (area, brand)
        
        Args:
            hotel_ids: Specific hotel IDs to fetch
            updated_after: Only fetch hotels updated after this date
            limit: Maximum number of hotels
            
        Returns:
            DataFrame with hotel data including area_name and brand_name
        """
        logger.info("Fetching hotels from database...")
        
        query = """
        SELECT 
            h.*,
            a.area_name,
            b.brand_name
        FROM tbl_hotel h
        LEFT JOIN tbl_area a ON h.area_id = a.area_id
        LEFT JOIN tbl_brand b ON h.brand_id = b.brand_id
        WHERE h.hotel_status = 1
        """
        params = {}
        
        if hotel_ids:
            placeholders = ','.join([f':id{i}' for i in range(len(hotel_ids))])
            query += f" AND h.hotel_id IN ({placeholders})"
            params.update({f'id{i}': hotel_id for i, hotel_id in enumerate(hotel_ids)})
        
        # Note: hotel_updatetime and hotel_createtime columns don't exist
        # If updated_after is provided, we'll fetch all hotels (incremental indexing not supported without timestamp columns)
        # if updated_after:
        #     query += " AND (h.hotel_updatetime >= :updated_after OR h.hotel_createtime >= :updated_after)"
        #     params['updated_after'] = updated_after
        
        query += " ORDER BY h.hotel_id DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params)
            logger.info(f"✅ Fetched {len(df)} hotels")
            return df
        except Exception as e:
            logger.error(f"Error fetching hotels: {e}")
            return pd.DataFrame()
    
    def get_rooms(
        self,
        hotel_ids: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """Fetch rooms from database"""
        logger.info("Fetching rooms from database...")
        
        query = "SELECT * FROM tbl_room WHERE 1=1"
        params = {}
        
        if hotel_ids:
            placeholders = ','.join([f':id{i}' for i in range(len(hotel_ids))])
            query += f" AND hotel_id IN ({placeholders})"
            params.update({f'id{i}': hotel_id for i, hotel_id in enumerate(hotel_ids)})
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params)
            logger.info(f"✅ Fetched {len(df)} rooms")
            return df
        except Exception as e:
            logger.error(f"Error fetching rooms: {e}")
            return pd.DataFrame()
    
    def get_evaluations(
        self,
        hotel_ids: Optional[List[int]] = None
    ) -> pd.DataFrame:
        """Fetch evaluations from database"""
        logger.info("Fetching evaluations from database...")
        
        query = "SELECT * FROM tbl_evaluate WHERE 1=1"
        params = {}
        
        if hotel_ids:
            placeholders = ','.join([f':id{i}' for i in range(len(hotel_ids))])
            query += f" AND hotel_id IN ({placeholders})"
            params.update({f'id{i}': hotel_id for i, hotel_id in enumerate(hotel_ids)})
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params)
            logger.info(f"✅ Fetched {len(df)} evaluations")
            return df
        except Exception as e:
            logger.error(f"Error fetching evaluations: {e}")
            return pd.DataFrame()
    
    def get_coupons(
        self,
        valid_only: bool = True
    ) -> pd.DataFrame:
        """Fetch coupons from database"""
        logger.info(f"Fetching coupons (valid_only={valid_only})...")
        
        query = "SELECT * FROM tbl_coupon WHERE 1=1"
        
        if valid_only:
            # Filter by end date only (coupon_status column doesn't exist)
            query += " AND (coupon_end_date IS NULL OR coupon_end_date >= NOW())"
        
        try:
            df = pd.read_sql(text(query), self.engine)
            logger.info(f"✅ Fetched {len(df)} coupons")
            return df
        except Exception as e:
            logger.error(f"Error fetching coupons: {e}")
            return pd.DataFrame()
    
    def get_orders(
        self,
        user_ids: Optional[List[int]] = None,
        hotel_ids: Optional[List[int]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Fetch orders from database"""
        logger.info("Fetching orders...")
        
        query = """
        SELECT o.*, od.hotel_id, od.room_id
        FROM tbl_order o
        LEFT JOIN tbl_order_details od ON o.order_id = od.order_id
        WHERE 1=1
        """
        params = {}
        
        if user_ids:
            placeholders = ','.join([f':uid{i}' for i in range(len(user_ids))])
            query += f" AND o.customer_id IN ({placeholders})"
            params.update({f'uid{i}': user_id for i, user_id in enumerate(user_ids)})
        
        if hotel_ids:
            placeholders = ','.join([f':hid{i}' for i in range(len(hotel_ids))])
            query += f" AND od.hotel_id IN ({placeholders})"
            params.update({f'hid{i}': hotel_id for i, hotel_id in enumerate(hotel_ids)})
        
        if date_from:
            query += " AND o.order_date >= :date_from"
            params['date_from'] = date_from
        
        if date_to:
            query += " AND o.order_date <= :date_to"
            params['date_to'] = date_to
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params)
            logger.info(f"✅ Fetched {len(df)} orders")
            return df
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return pd.DataFrame()
    
    def get_user_interactions(
        self,
        user_id: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get user-hotel interactions (orders + evaluations)
        For collaborative filtering
        """
        logger.info(f"Fetching user interactions{f' for user {user_id}' if user_id else ''}...")
        
        query = """
        SELECT 
            o.customer_id as user_id,
            od.hotel_id,
            COUNT(*) as num_bookings,
            AVG(e.total_point) as avg_rating
        FROM tbl_order o
        JOIN tbl_order_details od ON o.order_id = od.order_id
        LEFT JOIN (
            SELECT 
                hotel_id,
                customer_id,
                (evaluate_loaction_point + evaluate_service_point + 
                 evaluate_price_point + evaluate_sanitary_point + 
                 evaluate_convenient_point) / 5.0 as total_point
            FROM tbl_evaluate
        ) e ON od.hotel_id = e.hotel_id AND o.customer_id = e.customer_id
        WHERE 1=1
        """
        
        params = {}
        if user_id:
            query += " AND o.customer_id = :user_id"
            params['user_id'] = user_id
        
        query += " GROUP BY o.customer_id, od.hotel_id"
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params)
            logger.info(f"✅ Fetched {len(df)} user-hotel interactions")
            return df
        except Exception as e:
            logger.error(f"Error fetching interactions: {e}")
            return pd.DataFrame()
    
    def get_last_indexed_timestamp(self) -> Optional[datetime]:
        """
        Get last indexed timestamp from rag_index_metadata table
        
        Returns:
            Last indexed datetime or None if not found or table doesn't exist
        """
        try:
            # Check if table exists first
            check_table_query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = 'rag_index_metadata'
            """
            table_check = pd.read_sql(text(check_table_query), self.engine)
            if table_check.iloc[0]['count'] == 0:
                logger.debug("Table rag_index_metadata does not exist, returning None")
                return None
            
            query = """
            SELECT indexed_at 
            FROM rag_index_metadata 
            ORDER BY indexed_at DESC 
            LIMIT 1
            """
            result = pd.read_sql(text(query), self.engine)
            if not result.empty and result.iloc[0]['indexed_at'] is not None:
                return result.iloc[0]['indexed_at']
            return None
        except Exception as e:
            logger.debug(f"Could not get last indexed timestamp (table may not exist): {e}")
            return None
    
    def save_indexed_timestamp(self, indexed_at: datetime, count: int):
        """
        Save indexed timestamp to rag_index_metadata table
        
        Args:
            indexed_at: Timestamp when indexing completed
            count: Number of items indexed
        """
        try:
            query = """
            INSERT INTO rag_index_metadata (indexed_at, indexed_count, created_at)
            VALUES (:indexed_at, :count, NOW())
            ON DUPLICATE KEY UPDATE 
                indexed_at = :indexed_at,
                indexed_count = :count,
                updated_at = NOW()
            """
            with self.engine.connect() as conn:
                conn.execute(text(query), {
                    'indexed_at': indexed_at,
                    'count': count
                })
                conn.commit()
            logger.info(f"✅ Saved indexed timestamp: {indexed_at} ({count} items)")
        except Exception as e:
            logger.warning(f"Could not save indexed timestamp: {e}")
            # Try to create table if it doesn't exist
            try:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS rag_index_metadata (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    indexed_at DATETIME NOT NULL,
                    indexed_count INT DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_indexed_at (indexed_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
                with self.engine.connect() as conn:
                    conn.execute(text(create_table_query))
                    conn.commit()
                # Retry saving
                with self.engine.connect() as conn:
                    conn.execute(text(query), {
                        'indexed_at': indexed_at,
                        'count': count
                    })
                    conn.commit()
                logger.info(f"✅ Created table and saved indexed timestamp: {indexed_at}")
            except Exception as e2:
                logger.error(f"Could not create table or save timestamp: {e2}")
    
    def get_new_or_updated_hotels(self, last_indexed: datetime) -> pd.DataFrame:
        """
        Get hotels that are new or updated since last_indexed
        
        Note: Since hotel_updatetime and hotel_createtime columns don't exist,
        this method returns all hotels. Incremental indexing is not supported
        without timestamp columns.
        
        Args:
            last_indexed: Last indexed timestamp (ignored, kept for compatibility)
            
        Returns:
            DataFrame with all hotels
        """
        logger.warning("⚠️  hotel_updatetime column doesn't exist, fetching all hotels instead of incremental")
        logger.info(f"Fetching all hotels (incremental indexing not supported without timestamp columns)...")
        
        query = """
        SELECT h.*, a.area_name, b.brand_name
        FROM tbl_hotel h
        LEFT JOIN tbl_area a ON h.area_id = a.area_id
        LEFT JOIN tbl_brand b ON h.brand_id = b.brand_id
        WHERE h.hotel_status = 1
        ORDER BY h.hotel_id DESC
        """
        
        try:
            df = pd.read_sql(text(query), self.engine)
            logger.info(f"✅ Fetched {len(df)} hotels (all hotels, not incremental)")
            return df
        except Exception as e:
            logger.error(f"Error fetching hotels: {e}")
            return pd.DataFrame()
    
    def get_rooms_enriched(
        self,
        hotel_ids: Optional[List[int]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get rooms with enriched data (join with type_room, hotel, area)
        
        Args:
            hotel_ids: Filter by hotel IDs
            limit: Maximum number of rooms
            
        Returns:
            DataFrame with enriched room data
        """
        logger.info("Fetching enriched rooms from database...")
        
        query = """
        SELECT 
            r.room_id,
            r.hotel_id,
            h.hotel_name,
            a.area_name,
            r.room_name,
            r.room_amount_of_people,
            tr.type_room_id,
            tr.type_room_price as room_price,
            tr.type_room_price_sale,
            tr.type_room_bed,
            tr.type_room_quantity as room_amount,
            tr.type_room_condition,
            tr.type_room_status
        FROM tbl_room r
        JOIN tbl_hotel h ON r.hotel_id = h.hotel_id
        LEFT JOIN tbl_area a ON h.area_id = a.area_id
        JOIN tbl_type_room tr ON r.room_id = tr.room_id
        WHERE r.room_status = 1
          AND tr.type_room_status = 1
        """
        
        params = {}
        if hotel_ids:
            placeholders = ','.join([f':id{i}' for i in range(len(hotel_ids))])
            query += f" AND r.hotel_id IN ({placeholders})"
            params.update({f'id{i}': hotel_id for i, hotel_id in enumerate(hotel_ids)})
        
        query += " ORDER BY h.hotel_id, tr.type_room_price ASC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params)
            logger.info(f"✅ Fetched {len(df)} enriched rooms")
            return df
        except Exception as e:
            logger.error(f"Error fetching enriched rooms: {e}")
            return pd.DataFrame()
    
    def get_type_rooms_enriched(
        self,
        hotel_ids: Optional[List[int]] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get type_rooms with enriched data (grouped by type_room_id)
        
        Args:
            hotel_ids: Filter by hotel IDs
            limit: Maximum number of type_rooms
            
        Returns:
            DataFrame with enriched type_room data
        """
        logger.info("Fetching enriched type_rooms from database...")
        
        query = """
        SELECT 
            tr.type_room_id,
            r.room_name as type_room_name,
            tr.type_room_bed,
            tr.type_room_condition,
            GROUP_CONCAT(DISTINCT h.hotel_id) as hotel_ids,
            GROUP_CONCAT(DISTINCT h.hotel_name SEPARATOR ', ') as hotel_names,
            MIN(tr.type_room_price) as search_min_price,
            MAX(tr.type_room_price) as search_max_price,
            AVG(tr.type_room_price) as search_avg_price,
            COUNT(DISTINCT r.room_id) as room_count
        FROM tbl_type_room tr
        JOIN tbl_room r ON tr.room_id = r.room_id
        JOIN tbl_hotel h ON r.hotel_id = h.hotel_id
        WHERE r.room_status = 1
          AND tr.type_room_status = 1
        """
        
        params = {}
        if hotel_ids:
            placeholders = ','.join([f':id{i}' for i in range(len(hotel_ids))])
            query += f" AND h.hotel_id IN ({placeholders})"
            params.update({f'id{i}': hotel_id for i, hotel_id in enumerate(hotel_ids)})
        
        query += " GROUP BY tr.type_room_id, r.room_name, tr.type_room_bed, tr.type_room_condition"
        query += " ORDER BY tr.type_room_id"
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            df = pd.read_sql(text(query), self.engine, params=params)
            logger.info(f"✅ Fetched {len(df)} enriched type_rooms")
            return df
        except Exception as e:
            logger.error(f"Error fetching enriched type_rooms: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


