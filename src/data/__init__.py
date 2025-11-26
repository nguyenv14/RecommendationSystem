"""
Data processing module
Database connection, normalization, and ETL
"""

from .connector import DatabaseConnector
from .normalizer import HotelDataNormalizer
from .processor import DataProcessor

__all__ = [
    'DatabaseConnector',
    'HotelDataNormalizer',
    'DataProcessor',
]

