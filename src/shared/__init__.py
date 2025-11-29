"""
Shared utilities module
Common utilities used across RAG and Recommendation systems
"""

from .logger import get_logger, setup_logging
from .qdrant_manager import QdrantManager
from .embedding_manager import EmbeddingManager

__all__ = [
    'get_logger',
    'setup_logging',
    'QdrantManager',
    'EmbeddingManager',
]

