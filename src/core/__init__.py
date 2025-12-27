"""
Core business logic modules
Unified logic cho cả RAG và Recommendation
"""

from .embeddings import EmbeddingService
from .sparse_embeddings import SparseEmbeddingService
from .vectorstore import VectorStoreService
from .retriever import RetrieverService
from .generator import GeneratorService
from .recommender import RecommenderService
from .rag import RAGService
from .indexing import IndexingService

# Import RAG-specific modules (moved from rag/core/)
try:
    from .query_router import QueryRouter
except ImportError:
    QueryRouter = None

try:
    from .sql_query_generator import SQLQueryGenerator
except ImportError:
    SQLQueryGenerator = None

# Import SimpleRAGSystem (moved from rag/)
try:
    from .simple_rag_system import SimpleRAGSystem
except ImportError:
    SimpleRAGSystem = None

__all__ = [
    'EmbeddingService',
    'SparseEmbeddingService',
    'VectorStoreService',
    'RetrieverService',
    'GeneratorService',
    'RecommenderService',
    'RAGService',
    'IndexingService',
    'QueryRouter',
    'SQLQueryGenerator',
    'SimpleRAGSystem',
]

