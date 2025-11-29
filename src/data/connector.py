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
        Fetch hotels from database
        
        Args:
            hotel_ids: Specific hotel IDs to fetch
            updated_after: Only fetch hotels updated after this date
            limit: Maximum number of hotels
            
        Returns:
            DataFrame with hotel data
        """
        logger.info("Fetching hotels from database...")
        
        query = "SELECT * FROM tbl_hotel WHERE 1=1"
        params = {}
        
        if hotel_ids:
            placeholders = ','.join([f':id{i}' for i in range(len(hotel_ids))])
            query += f" AND hotel_id IN ({placeholders})"
            params.update({f'id{i}': hotel_id for i, hotel_id in enumerate(hotel_ids)})
        
        if updated_after:
            query += " AND hotel_updatetime >= :updated_after"
            params['updated_after'] = updated_after
        
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
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


