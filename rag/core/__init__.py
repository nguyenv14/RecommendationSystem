"""
Core RAG Components

This package contains the core components of the RAG system:
- embeddings: Cached embeddings wrapper
- query_extractor: Keyword extraction from queries
- retriever: Search and retrieval logic (Layer 2)
- rag_chain: RAG chain setup for generation (Layer 3)
- vectorstore: Qdrant vector store helpers
"""

from .embeddings import CachedOllamaEmbeddings
from .query_extractor import QueryExtractor
from .retriever import HotelRetriever
from .rag_chain import RAGChain
from .vectorstore import VectorStoreHelper

__version__ = "1.0.0"

__all__ = [
    'CachedOllamaEmbeddings',
    'QueryExtractor',
    'HotelRetriever',
    'RAGChain',
    'VectorStoreHelper',
]

