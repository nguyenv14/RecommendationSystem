"""
Data processing module
Database connection, normalization, and ETL
"""

from .connector import DatabaseConnector
from .normalizer import HotelDataNormalizer

# Lazy import DataProcessor to avoid circular import with src.core
# DataProcessor imports RAGService from src.core, which imports from src.data
def _get_processor():
    """Lazy import DataProcessor"""
    from .processor import DataProcessor
    return DataProcessor

# Import RAG-specific modules (moved from rag/data/)
try:
    from .chunker import SmartChunker
except ImportError:
    SmartChunker = None

try:
    from .coupon_normalizer import CouponDataNormalizer
except ImportError:
    CouponDataNormalizer = None

__all__ = [
    'DatabaseConnector',
    'HotelDataNormalizer',
    'DataProcessor',
    'SmartChunker',
    'CouponDataNormalizer',
]

# Make DataProcessor available via lazy import
def __getattr__(name):
    if name == 'DataProcessor':
        return _get_processor()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


