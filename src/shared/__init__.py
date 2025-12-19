"""
Shared utilities module
Common utilities used across RAG and Recommendation systems
"""

from .logger import get_logger, setup_logging
from .response import ApiResponse

__all__ = [
    'get_logger',
    'setup_logging',
    'ApiResponse',
]

