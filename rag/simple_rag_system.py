#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple RAG System cho Hotel Recommendation
Sử dụng LangChain + Ollama + Qdrant
"""

import pandas as pd
import os
import json
import hashlib
from typing import List, Dict, Optional
from functools import lru_cache
import logging
from pathlib import Path
from datetime import datetime
import time

from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLanguageModel
from qdrant_client import QdrantClient

# Import custom modules
try:
    from database_connector import DatabaseConnector
    from smart_chunker import SmartChunker
    from hotel_data_normalization import HotelDataNormalizer
except ImportError:
    logger.warning("Could not import database_connector, smart_chunker, or hotel_data_normalization")
    DatabaseConnector = None
    SmartChunker = None
    HotelDataNormalizer = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CachedOllamaEmbeddings(Embeddings):
    """
    Wrapper cho OllamaEmbeddings với cache để tối ưu performance
    Inherit từ Embeddings base class để tương thích với LangChain
    """
    def __init__(self, embeddings: OllamaEmbeddings, cache_enabled: bool = True):
        """
        Initialize cached embeddings wrapper
        
        Args:
            embeddings: OllamaEmbeddings instance
            cache_enabled: Enable caching
        """
        super().__init__()
        self.embeddings = embeddings
        self._embedding_cache = {}
        self._cache_enabled = cache_enabled
    
    def embed_query(self, text: str) -> List[float]:
        """Embed query với cache"""
        if not self._cache_enabled:
            return self.embeddings.embed_query(text)
        
        # Tạo cache key từ text
        cache_key = hashlib.md5(text.encode()).hexdigest()
        
        # Check cache
        if cache_key in self._embedding_cache:
            logger.debug(f"Embedding cache hit for: {text[:50]}...")
            return self._embedding_cache[cache_key]
        
        # Cache miss - embed và cache
        logger.debug(f"Embedding cache miss for: {text[:50]}...")
        embedding = self.embeddings.embed_query(text)
        self._embedding_cache[cache_key] = embedding
        return embedding
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents với cache để tối ưu performance"""
        if not self._cache_enabled:
            return self.embeddings.embed_documents(texts)
        
        # Check cache for each text và build result
        result = []
        texts_to_embed = []
        indices_to_embed = []
        
        for idx, text in enumerate(texts):
            cache_key = hashlib.md5(text.encode()).hexdigest()
            if cache_key in self._embedding_cache:
                # Use cached embedding
                result.append(self._embedding_cache[cache_key])
            else:
                # Need to embed this text
                result.append(None)  # Placeholder
                texts_to_embed.append(text)
                indices_to_embed.append(idx)
        
        # Embed texts that are not in cache
        if texts_to_embed:
            new_embeddings = self.embeddings.embed_documents(texts_to_embed)
            # Cache new embeddings and update result
            for i, (text, embedding) in enumerate(zip(texts_to_embed, new_embeddings)):
                cache_key = hashlib.md5(text.encode()).hexdigest()
                self._embedding_cache[cache_key] = embedding
                # Update result at correct index
                result[indices_to_embed[i]] = embedding
        
        return result
    
    # Delegate các methods khác từ base embeddings
    def __getattr__(self, name):
        """Delegate unknown attributes to base embeddings"""
        return getattr(self.embeddings, name)


class SimpleRAGSystem:
    """Simple RAG System cho Hotel Recommendation"""
    
    def __init__(self,
                 ollama_url="http://localhost:11434",
                 qdrant_url="http://localhost:6333",
                 embedding_model="bge-m3",
                 llm_model="qwen3",
                 collection_name="hotels",
                 llm_provider="ollama",
                 lm_studio_url=None):
        """
        Initialize RAG System
        
        Args:
            ollama_url: Ollama server URL (for embeddings and LLM if llm_provider="ollama")
            qdrant_url: Qdrant server URL
            embedding_model: Embedding model name
            llm_model: LLM model name
            collection_name: Qdrant collection name
            llm_provider: LLM provider ("ollama" or "lm_studio")
            lm_studio_url: LM Studio server URL (required if llm_provider="lm_studio")
        """
        self.ollama_url = ollama_url
        self.qdrant_url = qdrant_url
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.collection_name = collection_name
        self.llm_provider = llm_provider
        self.lm_studio_url = lm_studio_url or ollama_url  # Default to ollama_url if not provided
        
        # Initialize embeddings với cache wrapper
        # Note: Embeddings still use Ollama for now
        logger.info(f"Initializing embeddings: {embedding_model}")
        base_embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_url
        )
        # Wrap với cache để tối ưu performance
        self.embeddings = CachedOllamaEmbeddings(base_embeddings, cache_enabled=True)
        
        # Initialize LLM với tối ưu performance
        logger.info(f"Initializing LLM: {llm_model} (provider: {llm_provider})")
        if llm_provider == "lm_studio":
            # Use ChatOpenAI for LM Studio (OpenAI-compatible API)
            # LM Studio uses OpenAI-compatible API format
            try:
                self.llm = ChatOpenAI(
                    model=llm_model,
                    openai_api_base=f"{self.lm_studio_url}/v1",
                    openai_api_key="lm-studio",  # LM Studio doesn't require real API key
                    temperature=0.3,
                    max_tokens=2048,  # Increased from 512 to allow longer, more detailed responses
                    streaming=False,
                    timeout=120.0,  # Increased timeout for longer generation
                    model_kwargs={}  # Additional model parameters
                )
                logger.info(f"✅ Initialized ChatOpenAI with LM Studio at {self.lm_studio_url}")
            except Exception as e:
                # Fallback: try with base_url if openai_api_base doesn't work
                logger.warning(f"⚠️ Failed to initialize with openai_api_base: {e}, trying base_url...")
                try:
                    self.llm = ChatOpenAI(
                        model=llm_model,
                        base_url=f"{self.lm_studio_url}/v1",
                        api_key="lm-studio",
                        temperature=0.3,
                        max_tokens=2048,  # Increased from 512 to allow longer, more detailed responses
                        streaming=False,
                        timeout=120.0  # Increased timeout for longer generation
                    )
                    logger.info(f"✅ Initialized ChatOpenAI with LM Studio (base_url) at {self.lm_studio_url}")
                except Exception as e2:
                    logger.error(f"❌ Failed to initialize ChatOpenAI with LM Studio: {e2}")
                    raise
            # Pre-load model for LM Studio
            self._preload_lm_studio_model(self.lm_studio_url, llm_model)
        else:
            # Use Ollama for LLM
            self.llm = Ollama(
                model=llm_model,
                base_url=ollama_url,
                temperature=0.3  # Lower temperature for more focused responses
            )
            # Pre-load model để tránh cold start (12s -> <1s)
            self._preload_model(ollama_url, llm_model)
        
        # Vector store (will be initialized after indexing)
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
        
        # Optional: Database connector and chunker
        self.db_connector = None
        self.chunker = None
        self.normalizer = None
        
        # Chunking configuration (optimized for speed)
        self.use_chunking = True
        self.chunk_size = 800  # Tăng chunk_size để giảm số lượng chunks
        self.chunk_overlap = 50  # Giảm overlap để nhanh hơn
    
    def _preload_model(self, ollama_url: str, llm_model: str):
        """Pre-load model bằng cách gọi Ollama API trực tiếp"""
        try:
            import requests
            preload_url = f"{ollama_url}/api/generate"
            preload_payload = {
                "model": llm_model,
                "prompt": "test",  # Simple prompt để trigger model load
                "stream": False,
                "keep_alive": "5m",  # Keep model in memory for 5 minutes
                "options": {
                    "num_ctx": 1048,  # Reduce context window (default 4096) để nhanh hơn
                    "num_predict": 10  # Limit response length để nhanh hơn (chỉ cần 10 tokens để trigger load)
                }
            }
            # Gọi API để pre-load model (timeout ngắn để không block)
            # Chỉ cần trigger load, không cần response
            try:
                response = requests.post(preload_url, json=preload_payload, timeout=3)
                if response.status_code == 200:
                    logger.info(f"✅ Model {llm_model} pre-loaded with keep_alive=5m")
                else:
                    logger.debug(f"Model pre-load returned status {response.status_code} (may still work)")
            except requests.exceptions.Timeout:
                # Timeout is OK - model is loading in background
                logger.info(f"✅ Model {llm_model} pre-load initiated (loading in background)")
            except requests.exceptions.RequestException as e:
                logger.debug(f"Model pre-load request failed: {e} (will load on first use)")
        except ImportError:
            logger.warning("⚠️ requests module not available, cannot pre-load model")
        except Exception as e:
            logger.debug(f"⚠️ Failed to pre-load model: {e}. Model will load on first use.")
    
    def _preload_lm_studio_model(self, lm_studio_url: str, llm_model: str):
        """Pre-load model bằng cách gọi LM Studio API (OpenAI-compatible)"""
        try:
            import requests
            preload_url = f"{lm_studio_url}/v1/chat/completions"
            preload_payload = {
                "model": llm_model,
                "messages": [
                    {"role": "user", "content": "test"}  # Simple prompt để trigger model load
                ],
                "max_tokens": 10,  # Limit response length để nhanh hơn
                "temperature": 0.3
            }
            # Gọi API để pre-load model (timeout ngắn để không block)
            try:
                response = requests.post(preload_url, json=preload_payload, timeout=3)
                if response.status_code == 200:
                    logger.info(f"✅ LM Studio model {llm_model} pre-loaded")
                else:
                    logger.debug(f"LM Studio model pre-load returned status {response.status_code} (may still work)")
            except requests.exceptions.Timeout:
                # Timeout is OK - model is loading in background
                logger.info(f"✅ LM Studio model {llm_model} pre-load initiated (loading in background)")
            except requests.exceptions.RequestException as e:
                logger.debug(f"LM Studio model pre-load request failed: {e} (will load on first use)")
        except ImportError:
            logger.warning("⚠️ requests module not available, cannot pre-load LM Studio model")
        except Exception as e:
            logger.debug(f"⚠️ Failed to pre-load LM Studio model: {e}. Model will load on first use.")
    
    def index_hotels(self, normalized_data_path: str = "rag/normalized_data/normalized_hotels.csv", 
                     recreate_collection: bool = False):
        """
        Index hotels vào Qdrant từ normalized data
        
        Args:
            normalized_data_path: Path to normalized_hotels.csv
            recreate_collection: If True, recreate collection
        """
        logger.info(f"Loading normalized data from: {normalized_data_path}")
        
        # Get absolute path
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        data_path = project_root / normalized_data_path
        
        # Load normalized data
        normalized_df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(normalized_df)} hotels")
        
        # Create documents
        documents = []
        for idx, hotel in normalized_df.iterrows():
            hotel_id = int(hotel["hotel_id"])
            
            # Use semantic_text for embedding
            semantic_text = hotel.get("semantic_text", "")
            
            if pd.isna(semantic_text) or not semantic_text.strip():
                logger.warning(f"Hotel {hotel_id} has no semantic_text, skipping")
                continue
            
            # Truncate text if too long (to avoid Ollama timeout)
            # Keep first 1500 characters to preserve main semantic meaning
            max_text_length = 1500
            if len(semantic_text) > max_text_length:
                logger.debug(f"Truncating hotel {hotel_id} text from {len(semantic_text)} to {max_text_length} chars")
                semantic_text = semantic_text[:max_text_length] + "..."
            
            # Create document
            doc = Document(
                page_content=semantic_text,
                metadata={
                    "hotel_id": hotel_id,
                    "hotel_name": str(hotel.get("hotel_name", "")),
                    "hotel_rank": int(hotel.get("hotel_rank", 0)) if pd.notna(hotel.get("hotel_rank")) else None,
                    "hotel_price_average": float(hotel.get("hotel_price_average", 0)) if pd.notna(hotel.get("hotel_price_average")) else None,
                    "area_name": str(hotel.get("area_name", "")) if pd.notna(hotel.get("area_name")) else "",
                    "brand_name": str(hotel.get("brand_name", "")) if pd.notna(hotel.get("brand_name")) else "",
                    "price_category": str(hotel.get("price_category", "")) if pd.notna(hotel.get("price_category")) else "",
                    "normalized_name": str(hotel.get("normalized_name", "")) if pd.notna(hotel.get("normalized_name")) else ""
                }
            )
            documents.append(doc)
        
        logger.info(f"Created {len(documents)} documents")
        
        # Store in Qdrant using shared method
        # Note: _store_documents_in_qdrant will handle collection creation
        self._store_documents_in_qdrant(
            documents,
            recreate_collection=recreate_collection,
            batch_size=1,  # Legacy: process one hotel at a time
            use_upsert=False
        )
        
        # Initialize retriever and QA chain
        self._initialize_qa_chain()
        
        logger.info("RAG system initialized successfully!")
    
    def index_hotels_from_database(self,
                                   use_chunking: bool = True,
                                   chunk_size: int = 800,  # Tăng chunk_size để giảm chunks
                                   chunk_overlap: int = 50,  # Giảm overlap
                                   incremental: bool = True,
                                   recreate_collection: bool = False,
                                   batch_size: int = 50):  # Tăng batch_size để nhanh hơn
        """
        Index hotels từ database MySQL với smart chunking và incremental indexing
        
        Args:
            use_chunking: If True, use smart chunking (recommended for long texts)
            chunk_size: Size of each chunk (characters)
            chunk_overlap: Overlap between chunks (characters)
            incremental: If True, only index new/updated hotels
            recreate_collection: If True, recreate collection (will delete all data)
            batch_size: Number of hotels to process in each batch
        """
        logger.info("🔄 Indexing hotels from database...")
        
        # Initialize database connector
        if DatabaseConnector is None:
            raise ImportError("DatabaseConnector not available. Please install pymysql and sqlalchemy.")
        
        if self.db_connector is None:
            self.db_connector = DatabaseConnector()
        
        # Test database connection
        if not self.db_connector.test_connection():
            raise ConnectionError("Failed to connect to database")
        
        # Initialize normalizer
        if HotelDataNormalizer is None:
            raise ImportError("HotelDataNormalizer not available.")
        
        if self.normalizer is None:
            self.normalizer = HotelDataNormalizer()
        
        # Initialize chunker if needed
        if use_chunking:
            if SmartChunker is None:
                raise ImportError("SmartChunker not available.")
            
            if self.chunker is None:
                self.chunker = SmartChunker(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    min_chunk_size=100,
                    preserve_sentences=True
                )
            self.use_chunking = True
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap
            logger.info(f"✅ Smart chunking enabled: chunk_size={chunk_size}, overlap={chunk_overlap}")
        else:
            self.use_chunking = False
            logger.info("⚠️  Smart chunking disabled - using full text")
        
        # Get hotels from database
        if incremental and not recreate_collection:
            # Get last indexed timestamp
            last_indexed = self.db_connector.get_last_indexed_timestamp()
            if last_indexed:
                logger.info(f"📅 Last indexed: {last_indexed}")
                logger.info("🔄 Fetching new/updated hotels only...")
                hotels_df = self.db_connector.get_new_or_updated_hotels(last_indexed)
            else:
                logger.info("📦 No previous indexing found - fetching all hotels...")
                hotels_df = self.db_connector.get_hotels()
        else:
            logger.info("📦 Fetching all hotels...")
            hotels_df = self.db_connector.get_hotels()
        
        if hotels_df.empty:
            logger.info("✅ No new/updated hotels to index")
            return
        
        logger.info(f"📊 Found {len(hotels_df)} hotels to index")
        
        # Create documents with chunking
        all_documents = []
        
        if use_chunking:
            # Use smart chunking
            logger.info("📝 Creating documents with smart chunking...")
            for idx, hotel in hotels_df.iterrows():
                hotel_id = int(hotel["hotel_id"])
                
                # Create semantic text
                semantic_text = self.normalizer.create_semantic_text(hotel)
                
                if not semantic_text or not semantic_text.strip():
                    logger.warning(f"Hotel {hotel_id} has no semantic_text, skipping")
                    continue
                
                # Create hotel data dict
                hotel_data = {
                    "hotel_id": hotel_id,
                    "hotel_name": str(hotel.get("hotel_name", "")),
                    "hotel_rank": int(hotel.get("hotel_rank", 0)) if pd.notna(hotel.get("hotel_rank")) else None,
                    "hotel_price_average": float(hotel.get("hotel_price_average", 0)) if pd.notna(hotel.get("hotel_price_average")) else None,
                    "area_name": str(hotel.get("area_name", "")) if pd.notna(hotel.get("area_name")) else "",
                    "brand_name": str(hotel.get("brand_name", "")) if pd.notna(hotel.get("brand_name")) else "",
                    "price_category": self.normalizer._categorize_price(
                        float(hotel.get("hotel_price_average", 0))
                    ) if pd.notna(hotel.get("hotel_price_average")) else "",
                    "normalized_name": self.normalizer.normalize_text(hotel.get("hotel_name", "")),
                }
                
                # Chunk hotel document
                chunks = self.chunker.chunk_hotel_document(hotel_data, semantic_text)
                all_documents.extend(chunks)
        else:
            # Use full text (no chunking)
            logger.info("📝 Creating documents without chunking...")
            for idx, hotel in hotels_df.iterrows():
                hotel_id = int(hotel["hotel_id"])
                
                # Create semantic text
                semantic_text = self.normalizer.create_semantic_text(hotel)
                
                if not semantic_text or not semantic_text.strip():
                    logger.warning(f"Hotel {hotel_id} has no semantic_text, skipping")
                    continue
                
                # Truncate if too long
                max_text_length = 2000
                if len(semantic_text) > max_text_length:
                    logger.debug(f"Truncating hotel {hotel_id} text from {len(semantic_text)} to {max_text_length} chars")
                    semantic_text = semantic_text[:max_text_length] + "..."
                
                # Create document
                doc = Document(
                    page_content=semantic_text,
                    metadata={
                        "hotel_id": hotel_id,
                        "hotel_name": str(hotel.get("hotel_name", "")),
                        "hotel_rank": int(hotel.get("hotel_rank", 0)) if pd.notna(hotel.get("hotel_rank")) else None,
                        "hotel_price_average": float(hotel.get("hotel_price_average", 0)) if pd.notna(hotel.get("hotel_price_average")) else None,
                        "area_name": str(hotel.get("area_name", "")) if pd.notna(hotel.get("area_name")) else "",
                        "brand_name": str(hotel.get("brand_name", "")) if pd.notna(hotel.get("brand_name")) else "",
                        "price_category": self.normalizer._categorize_price(
                            float(hotel.get("hotel_price_average", 0))
                        ) if pd.notna(hotel.get("hotel_price_average")) else "",
                        "normalized_name": self.normalizer.normalize_text(hotel.get("hotel_name", "")),
                    }
                )
                all_documents.append(doc)
        
        logger.info(f"✅ Created {len(all_documents)} documents from {len(hotels_df)} hotels")
        
        # Store in Qdrant
        self._store_documents_in_qdrant(
            all_documents,
            recreate_collection=recreate_collection,
            batch_size=batch_size,
            use_upsert=incremental and not recreate_collection
        )
        
        # Save indexed timestamp
        if incremental:
            indexed_at = datetime.now()
            self.db_connector.save_indexed_timestamp(indexed_at, len(hotels_df))
            logger.info(f"✅ Saved indexed timestamp: {indexed_at}")
        
        # Initialize retriever and QA chain
        self._initialize_qa_chain()
        
        logger.info("✅ Database indexing complete!")
    
    def _store_documents_in_qdrant(self,
                                   documents: List[Document],
                                   recreate_collection: bool = False,
                                   batch_size: int = 50,  # Tăng batch_size mặc định
                                   use_upsert: bool = False):
        """
        Store documents in Qdrant với batch processing
        
        Args:
            documents: List of Document objects
            recreate_collection: If True, recreate collection
            batch_size: Number of documents per batch
            use_upsert: If True, use upsert instead of add (for incremental updates)
        """
        if not documents:
            logger.warning("No documents to store")
            return
        
        logger.info(f"📦 Storing {len(documents)} documents in Qdrant collection: {self.collection_name}")
        
        # Create collection first if not exists
        from qdrant_client.models import Distance, VectorParams, PointStruct
        client = QdrantClient(url=self.qdrant_url)
        
        try:
            # Get embedding dimension by testing with first document
            test_embedding = self.embeddings.embed_query(documents[0].page_content)
            vector_size = len(test_embedding)
            
            # Check if collection exists
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            # Delete collection if recreate is requested
            if recreate_collection and self.collection_name in collection_names:
                logger.info(f"🗑️  Deleting existing collection: {self.collection_name}")
                client.delete_collection(collection_name=self.collection_name)
                collections = client.get_collections()
                collection_names = [col.name for col in collections.collections]
            
            # Create collection if it doesn't exist
            if self.collection_name not in collection_names:
                logger.info(f"🆕 Creating collection '{self.collection_name}' with vector size {vector_size}")
                
                # Optimized HNSW config
                from qdrant_client.models import HnswConfigDiff
                hnsw_config = HnswConfigDiff(
                    m=16,
                    ef_construct=200,
                    full_scan_threshold=10
                )
                
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                        hnsw_config=hnsw_config
                    )
                )
                logger.info(f"✅ Collection '{self.collection_name}' created with optimized HNSW index")
            
            # Initialize vectorstore
            self.vectorstore = Qdrant(
                client=client,
                collection_name=self.collection_name,
                embeddings=self.embeddings
            )
            
            # Store documents in batches
            total_batches = (len(documents) + batch_size - 1) // batch_size
            logger.info(f"🔄 Processing {total_batches} batches (batch_size={batch_size})")
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                batch_num = i // batch_size + 1
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)")
                
                # Retry logic
                max_retries = 3
                retry_delay = 2
                
                for retry in range(max_retries):
                    try:
                        # Generate unique IDs for chunks
                        batch_ids = []
                        batch_texts = []
                        batch_metadatas = []
                        
                        for doc in batch:
                            # Generate integer ID for Qdrant (Qdrant only accepts unsigned int or UUID)
                            hotel_id = doc.metadata.get("hotel_id", 0)
                            
                            # Get chunk_index if exists (for chunked documents), otherwise 0
                            chunk_idx = doc.metadata.get("chunk_index", 0)
                            
                            # Ensure hotel_id and chunk_idx are integers
                            try:
                                hotel_id = int(hotel_id) if hotel_id is not None else 0
                                chunk_idx = int(chunk_idx) if chunk_idx is not None else 0
                            except (ValueError, TypeError):
                                logger.warning(f"Invalid hotel_id or chunk_index: hotel_id={hotel_id}, chunk_idx={chunk_idx}")
                                hotel_id = 0
                                chunk_idx = 0
                            
                            # Create unique integer ID: hotel_id * 1000000 + chunk_index
                            # This allows up to 1,000,000 chunks per hotel (more than enough)
                            # Example: hotel_id=2, chunk_idx=0 -> 2000000
                            #          hotel_id=2, chunk_idx=1 -> 2000001
                            #          hotel_id=123, chunk_idx=0 -> 123000000
                            doc_id = hotel_id * 1000000 + chunk_idx
                            
                            # Store chunk_id as string in metadata for reference (if not exists)
                            if "chunk_id" not in doc.metadata:
                                doc.metadata["chunk_id"] = f"{hotel_id}_{chunk_idx}"
                            
                            # Ensure page_content is not None or empty
                            page_content = doc.page_content or ""
                            if not page_content:
                                logger.warning(f"Empty page_content for doc {doc_id}, skipping")
                                continue
                            
                            # Use metadata directly (LangChain will handle page_content storage)
                            # Don't include page_content in metadata as LangChain handles it separately
                            batch_ids.append(doc_id)
                            batch_texts.append(page_content)
                            batch_metadatas.append(doc.metadata.copy())  # Use metadata directly
                        
                        # Use LangChain's add_texts method to ensure proper payload structure
                        # This ensures page_content is stored correctly for retrieval
                        # LangChain's add_texts handles the payload structure automatically
                        try:
                            # Use LangChain's add_texts which handles payload structure correctly
                            # Note: LangChain might generate its own IDs if we don't provide them correctly
                            # Convert integer IDs to strings for LangChain compatibility
                            self.vectorstore.add_texts(
                                texts=batch_texts,
                                metadatas=batch_metadatas,
                                ids=[str(doc_id) for doc_id in batch_ids]  # Convert to string for LangChain
                            )
                        except Exception as e:
                            # If add_texts fails with IDs, try without IDs (LangChain will generate UUIDs)
                            logger.warning(f"Error adding texts with custom IDs: {e}. Trying without IDs...")
                            self.vectorstore.add_texts(
                                texts=batch_texts,
                                metadatas=batch_metadatas
                                # Let LangChain generate IDs
                            )
                        
                        break  # Success
                    except Exception as e:
                        if retry < max_retries - 1:
                            logger.warning(f"Error processing batch {batch_num} (attempt {retry+1}/{max_retries}): {e}")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"Error processing batch {batch_num} after {max_retries} attempts: {e}")
                            raise
                
                # No delay between batches for faster processing
                # Only small delay if there's an error
                # time.sleep(0.1)  # Minimal delay if needed
            
            logger.info(f"✅ Successfully stored {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error storing documents: {e}")
            raise
    
    def _initialize_qa_chain(self):
        """Initialize QA chain from vectorstore"""
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized")
        
        # Create retriever với 5 sources để có nhiều thông tin hơn
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={
                "k": 5  # Increased from 2 to 5 for more comprehensive responses
            }
        )
        
        # Create QA chain với prompt chi tiết hơn để có response dài hơn
        prompt_template = """Bạn là trợ lý tư vấn khách sạn tại Đà Nẵng. Trả lời HOÀN TOÀN bằng tiếng Việt.

Thông tin khách sạn:
{context}

Câu hỏi: {question}

QUAN TRỌNG: 
- CHỈ trả lời các câu hỏi liên quan đến khách sạn, nhà nghỉ, resort, homestay tại Đà Nẵng.
- Nếu câu hỏi KHÔNG liên quan đến khách sạn hoặc du lịch, bạn PHẢI trả lời: "Xin lỗi, tôi chỉ có thể tư vấn về khách sạn tại Đà Nẵng. Câu hỏi của bạn không liên quan đến dịch vụ này."
- Nếu thông tin khách sạn trên KHÔNG có câu trả lời phù hợp cho câu hỏi, bạn PHẢI trả lời: "Không tìm thấy khách sạn phù hợp với yêu cầu của bạn trong hệ thống."

Nếu câu hỏi liên quan đến khách sạn và có thông tin phù hợp, hãy trả lời chi tiết, tự nhiên bằng tiếng Việt. Nêu tên khách sạn, giá, đánh giá (sao), địa điểm, và các tiện ích nổi bật. So sánh các khách sạn nếu có nhiều lựa chọn.

Trả lời:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Sử dụng chain_type="stuff" với k=5 (context lớn hơn) để có response chi tiết hơn
        # Với k=5, "stuff" vẫn nhanh hơn "refine" hay "map_reduce" vì không cần multiple passes
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Giữ "stuff" vì vẫn nhanh và phù hợp với k=5
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            verbose=False  # Tắt verbose để giảm overhead
        )
        
        logger.info("✅ QA chain initialized")
    
    def _extract_location_from_query(self, query: str) -> Optional[str]:
        """
        Extract location (area_name) từ query
        
        Args:
            query: Search query
            
        Returns:
            Location name nếu tìm thấy, None nếu không
        """
        query_lower = query.lower().strip()
        
        # Danh sách các khu vực ở Đà Nẵng
        locations = {
            "ngũ hành sơn": "Ngũ Hành Sơn",
            "ngu hanh son": "Ngũ Hành Sơn",
            "quận ngũ hành sơn": "Ngũ Hành Sơn",
            "sơn trà": "Sơn Trà",
            "son tra": "Sơn Trà",
            "quận sơn trà": "Sơn Trà",
            "cẩm lệ": "Cẩm Lệ",
            "cam le": "Cẩm Lệ",
            "quận cẩm lệ": "Cẩm Lệ",
            "hải châu": "Hải Châu",
            "hai chau": "Hải Châu",
            "quận hải châu": "Hải Châu",
            "liên chiểu": "Liên Chiểu",
            "lien chieu": "Liên Chiểu",
            "quận liên chiểu": "Liên Chiểu",
            "thanh khê": "Thanh Khê",
            "thanh khe": "Thanh Khê",
            "quận thanh khê": "Thanh Khê",
            "hòa vang": "Hòa Vang",
            "hoa vang": "Hòa Vang",
            "huyện hòa vang": "Hòa Vang",
        }
        
        # Tìm location trong query
        for location_key, location_name in locations.items():
            if location_key in query_lower:
                logger.info(f"Extracted location from query: {location_name}")
                return location_name
        
        return None
    
    def search_hotels(self, query: str, top_k: int = 5, area_name: Optional[str] = None) -> List[Dict]:
        """
        Search hotels by query (semantic search with optional location filtering)
        
        Args:
            query: Search query
            top_k: Number of results
            area_name: Optional area name to filter (if None, will try to extract from query)
            
        Returns:
            List of hotel results
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call index_hotels first.")
        
        logger.info(f"Searching for: '{query}'")
        
        # Extract location from query if not provided
        if area_name is None:
            area_name = self._extract_location_from_query(query)
        
        # If location found, use filtering
        if area_name:
            logger.info(f"Filtering by location: {area_name}")
            # Use Qdrant filter to search only in specific area
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            # Search with location filter
            # Note: LangChain doesn't support filtering directly, so we need to use QdrantClient
            client = QdrantClient(url=self.qdrant_url)
            
            # Get embedding (cached)
            query_embedding = self.embeddings.embed_query(query)
            
            # Search with location filter và tối ưu performance
            # Giảm limit để giảm context size và tăng tốc độ
            search_results = client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=min(top_k + 1, 5),  # Giảm từ 10 xuống 5 để nhanh hơn
                query_filter=Filter(
                    must=[
                        FieldCondition(key="area_name", match=MatchValue(value=area_name))
                    ]
                ),
                with_payload=True,
                with_vectors=False  # Không cần vectors trong response để nhanh hơn
            )
            
            # Format results with post-filtering to ensure correct location
            hotels = []
            for result in search_results:
                payload = result.payload or {}
                
                # Get area_name from payload
                hotel_area = payload.get("area_name", "")
                
                # Post-filter: Only include hotels in the requested location
                # This ensures we don't get hotels from other areas
                if hotel_area and hotel_area.strip() == area_name:
                    # Get page_content from payload
                    page_content = payload.get("content") or payload.get("text") or ""
                    
                    hotels.append({
                        "hotel_id": payload.get("hotel_id"),
                        "hotel_name": payload.get("hotel_name", ""),
                        "hotel_rank": payload.get("hotel_rank"),
                        "hotel_price_average": payload.get("hotel_price_average"),
                        "area_name": payload.get("area_name", ""),
                        "brand_name": payload.get("brand_name", ""),
                        "price_category": payload.get("price_category", ""),
                        "similarity_score": float(result.score),
                        "text_preview": page_content[:200] + "..." if len(page_content) > 200 else page_content
                    })
                    
                    # Stop when we have enough results
                    if len(hotels) >= top_k:
                        break
            
            logger.info(f"Found {len(hotels)} hotels in {area_name} (after filtering)")
            
            # If no results with filter, try without filter but warn
            if len(hotels) == 0:
                logger.warning(f"No hotels found in {area_name} with filter. Trying without filter...")
                # Fall through to regular search below
            
            if len(hotels) > 0:
                return hotels
        
        # No location filter - use regular semantic search với tối ưu
        # Giảm k để giảm context size và tăng tốc độ
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=min(top_k + 1, 5)  # Giảm từ 10 xuống 5 để nhanh hơn (chỉ lấy top_k + 1)
        )
        
        # Format results with optional post-filtering
        # Note: LangChain similarity_search_with_score returns scores
        # For cosine distance: score is distance (lower = better, range 0-2)
        # Convert to similarity: similarity = 1 - distance (higher = better)
        hotels = []
        for doc, score in results:
            # Convert distance to similarity (cosine distance: lower = better)
            # similarity = 1 - distance, range [1, -1] -> normalize to [0, 1]
            similarity_score = max(0, 1 - score)  # Normalize to [0, 1]
            
            # Filter by similarity threshold (chỉ lấy results có similarity > 0.3)
            # Lower threshold để có nhiều results hơn
            if similarity_score < 0.3:
                continue
            
            hotel_area = doc.metadata.get("area_name", "")
            hotel_name = doc.metadata.get("hotel_name", "").strip()
            
            # Filter out hotels without valid name
            if not hotel_name or hotel_name == "":
                continue
            
            # If we have a location filter but it wasn't applied in search, post-filter here
            if area_name and hotel_area and hotel_area.strip() != area_name:
                continue  # Skip hotels not in the requested area
            
            hotels.append({
                "hotel_id": doc.metadata.get("hotel_id"),
                "hotel_name": hotel_name,
                "hotel_rank": doc.metadata.get("hotel_rank"),
                "hotel_price_average": doc.metadata.get("hotel_price_average"),
                "area_name": doc.metadata.get("area_name", ""),
                "brand_name": doc.metadata.get("brand_name", ""),
                "price_category": doc.metadata.get("price_category", ""),
                "similarity_score": float(similarity_score),  # Use converted similarity score
                "text_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
            
            # Stop when we have enough results
            if len(hotels) >= top_k:
                break
        
        return hotels
    
    def ask(self, question: str) -> Dict:
        """
        Ask question với RAG (Retrieval + Generation)
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and sources
        """
        if self.qa_chain is None:
            raise ValueError("QA chain not initialized. Call index_hotels first.")
        
        logger.info(f"Question: '{question}'")
        
        # Get answer with RAG
        result = self.qa_chain({"query": question})
        
        # Format response
        response = {
            "question": question,
            "answer": result["result"],
            "sources": []
        }
        
        # Add source documents
        for doc in result.get("source_documents", []):
            # Handle case where page_content might be None
            page_content = doc.page_content if doc.page_content else ""
            if not page_content:
                # Try to get from metadata if not in page_content
                page_content = doc.metadata.get("page_content") or doc.metadata.get("content") or doc.metadata.get("text") or ""
            
            response["sources"].append({
                "hotel_id": doc.metadata.get("hotel_id"),
                "hotel_name": doc.metadata.get("hotel_name", ""),
                "hotel_rank": doc.metadata.get("hotel_rank"),
                "hotel_price_average": doc.metadata.get("hotel_price_average"),
                "area_name": doc.metadata.get("area_name", ""),
                "text_preview": page_content[:300] + "..." if len(page_content) > 300 else page_content
            })
        
        return response
    
    def load_vectorstore(self):
        """Load existing vectorstore from Qdrant"""
        logger.info(f"Loading vectorstore from Qdrant: {self.collection_name}")
        
        # Create Qdrant client
        client = QdrantClient(url=self.qdrant_url)
        
        # Check if collection exists
        try:
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                raise ValueError(
                    f"Collection '{self.collection_name}' does not exist in Qdrant. "
                    f"Please run index_hotels() first."
                )
            
            logger.info(f"Collection '{self.collection_name}' exists")
        except Exception as e:
            logger.error(f"Error checking collection: {e}")
            raise
        
        # Load existing vectorstore
        self.vectorstore = Qdrant(
            client=client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )
        
        # Create retriever from vectorstore
        # Increased k to 5 for more comprehensive responses
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}  # Top 5 results (increased from 2 for more detailed responses)
        )
        
        # Create QA chain với prompt chi tiết hơn để có response dài hơn
        prompt_template = """Bạn là trợ lý tư vấn khách sạn tại Đà Nẵng. Trả lời HOÀN TOÀN bằng tiếng Việt.

Thông tin khách sạn:
{context}

Câu hỏi: {question}

QUAN TRỌNG: 
- CHỈ trả lời các câu hỏi liên quan đến khách sạn, nhà nghỉ, resort, homestay tại Đà Nẵng.
- Nếu câu hỏi KHÔNG liên quan đến khách sạn hoặc du lịch, bạn PHẢI trả lời: "Xin lỗi, tôi chỉ có thể tư vấn về khách sạn tại Đà Nẵng. Câu hỏi của bạn không liên quan đến dịch vụ này."
- Nếu thông tin khách sạn trên KHÔNG có câu trả lời phù hợp cho câu hỏi, bạn PHẢI trả lời: "Không tìm thấy khách sạn phù hợp với yêu cầu của bạn trong hệ thống."

Nếu câu hỏi liên quan đến khách sạn và có thông tin phù hợp, hãy trả lời chi tiết, tự nhiên bằng tiếng Việt. Nêu tên khách sạn, giá, đánh giá (sao), địa điểm, và các tiện ích nổi bật. So sánh các khách sạn nếu có nhiều lựa chọn.

Trả lời:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Sử dụng chain_type="stuff" với k=5 (context lớn hơn) để có response chi tiết hơn
        # Với k=5, "stuff" vẫn nhanh hơn "refine" hay "map_reduce" vì không cần multiple passes
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",  # Giữ "stuff" vì vẫn nhanh và phù hợp với k=5
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            verbose=False  # Tắt verbose để giảm overhead
        )
        
        logger.info("Vectorstore loaded successfully!")
    
    def verify_hnsw_config(self) -> Dict:
        """
        Verify HNSW configuration của collection hiện có
        
        Returns:
            Dictionary với HNSW config info
        """
        client = QdrantClient(url=self.qdrant_url)
        
        try:
            # Use raw HTTP call to avoid validation errors with newer Qdrant versions
            import requests
            response = requests.get(f"{self.qdrant_url}/collections/{self.collection_name}")
            response.raise_for_status()
            collection_info = response.json()["result"]
            
            result = {
                "collection_name": self.collection_name,
                "points_count": collection_info.get("points_count", 0),
                "vector_size": collection_info.get("config", {}).get("params", {}).get("vectors", {}).get("size"),
                "hnsw_configured": False
            }
            
            # Try to get HNSW config from vectors config
            vectors_config = collection_info.get("config", {}).get("params", {}).get("vectors", {})
            if isinstance(vectors_config, dict):
                hnsw_config = vectors_config.get("hnsw_config")
                if hnsw_config:
                    result["hnsw_configured"] = True
                    result["m"] = hnsw_config.get("m")
                    result["ef_construct"] = hnsw_config.get("ef_construct")
                    result["full_scan_threshold"] = hnsw_config.get("full_scan_threshold")
                else:
                    result.update({
                        "m": None,
                        "ef_construct": None,
                        "full_scan_threshold": None,
                        "warning": "HNSW config not found - collection may not be optimized"
                    })
            else:
                # Try direct access
                try:
                    collection = client.get_collection(self.collection_name)
                    config = collection.config
                    hnsw_config = getattr(config.params.vectors, 'hnsw_config', None) if hasattr(config.params.vectors, 'hnsw_config') else None
                    
                    if hnsw_config:
                        result["hnsw_configured"] = True
                        result["m"] = getattr(hnsw_config, 'm', None)
                        result["ef_construct"] = getattr(hnsw_config, 'ef_construct', None)
                        result["full_scan_threshold"] = getattr(hnsw_config, 'full_scan_threshold', None)
                    else:
                        result.update({
                            "m": None,
                            "ef_construct": None,
                            "full_scan_threshold": None,
                            "warning": "HNSW config not found - collection may not be optimized"
                        })
                except Exception:
                    # Fallback: return basic info
                    result.update({
                        "m": None,
                        "ef_construct": None,
                        "full_scan_threshold": None,
                        "warning": "Could not read HNSW config - may need to check manually"
                    })
            
            return result
            
        except Exception as e:
            logger.warning(f"Error verifying HNSW config (non-critical): {e}")
            # Return basic info even if there's an error
            return {
                "collection_name": self.collection_name,
                "points_count": 0,
                "vector_size": None,
                "hnsw_configured": False,
                "m": None,
                "ef_construct": None,
                "full_scan_threshold": None,
                "warning": f"Could not verify HNSW config: {str(e)}"
            }
    
    def optimize_collection(self, recreate_if_needed: bool = False) -> bool:
        """
        Optimize collection với HNSW config tối ưu
        
        Args:
            recreate_if_needed: Nếu True, recreate collection nếu HNSW config không tối ưu
            
        Returns:
            True nếu collection đã được optimize
        """
        client = QdrantClient(url=self.qdrant_url)
        
        try:
            # Verify current config
            config_info = self.verify_hnsw_config()
            
            # Check if HNSW is optimized
            is_optimized = (
                config_info.get("hnsw_configured") and
                config_info.get("m") == 16 and
                config_info.get("ef_construct") == 200
            )
            
            if is_optimized:
                logger.info("✅ Collection already has optimized HNSW config")
                logger.info(f"   m={config_info['m']}, ef_construct={config_info['ef_construct']}")
                return True
            
            logger.warning("⚠️  Collection does not have optimized HNSW config")
            logger.info(f"   Current: m={config_info.get('m')}, ef_construct={config_info.get('ef_construct')}")
            logger.info(f"   Expected: m=16, ef_construct=200")
            
            if recreate_if_needed:
                logger.warning("⚠️  Recreating collection with optimized HNSW config...")
                logger.warning("⚠️  This will delete all existing data!")
                
                # Recreate collection with optimized config
                # Note: User needs to call index_hotels() again after this
                client.delete_collection(collection_name=self.collection_name)
                logger.info("✅ Collection deleted. Please call index_hotels() to recreate with optimized config.")
                return True
            else:
                logger.warning("⚠️  Set recreate_if_needed=True to recreate collection with optimized config")
                logger.warning("⚠️  Note: Qdrant does not support updating HNSW config on existing collections")
                return False
                
        except Exception as e:
            logger.error(f"Error optimizing collection: {e}")
            raise
    
    def search_hotels_optimized(self, query: str, top_k: int = 3, ef: int = 100) -> List[Dict]:
        """
        Search hotels với optimized parameters (sử dụng ef parameter)
        
        Args:
            query: Search query
            top_k: Number of results
            ef: Number of candidates to consider during search (higher = better accuracy, slower)
                  - Recommended: 50-200
                  - Default: 100 (balanced)
                  - Higher ef = better recall but slower
            
        Returns:
            List of hotel results
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call index_hotels first.")
        
        logger.info(f"Searching for: '{query}' (ef={ef})")
        
        # Use LangChain vectorstore for proper metadata handling
        # Note: LangChain Qdrant automatically handles metadata correctly
        # We'll use similarity_search_with_score which is faster and preserves metadata
        
        # For now, use regular search_hotels() which works correctly
        # The ef parameter optimization can be done at Qdrant level if needed
        # But LangChain wrapper doesn't expose ef parameter directly
        
        # Use regular search_hotels() - it supports location filtering automatically
        # Extract location from query if not provided
        area_name = self._extract_location_from_query(query) if hasattr(self, '_extract_location_from_query') else None
        results = self.search_hotels(query, top_k=top_k, area_name=area_name)
        
        # Note: If you need ef parameter optimization, you can:
        # 1. Use search_hotels() (already optimized with cache and HNSW)
        # 2. Or configure ef at collection level
        # LangChain doesn't expose ef parameter per-query, but default ef works well
        
        return results


def main():
    """Main function - Demo RAG system"""
    
    print("🚀 Initializing Simple RAG System...")
    
    # Initialize RAG system
    rag = SimpleRAGSystem(
        ollama_url="http://localhost:11434",
        qdrant_url="http://localhost:6333",
        embedding_model="bge-m3",
        llm_model="qwen3"  # qwen3 hỗ trợ tiếng Việt rất tốt
    )
    
    # Index hotels
    print("\n📦 Indexing hotels...")
    rag.index_hotels(
        normalized_data_path="rag/normalized_data/normalized_hotels.csv",
        recreate_collection=True
    )
    
    # Test semantic search
    print("\n🔍 Testing Semantic Search:")
    print("=" * 60)
    
    test_queries = [
        "Khách sạn 5 sao gần biển Đà Nẵng",
        "Khách sạn giá rẻ ở Sơn Trà",
        "Khách sạn luxury có spa"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag.search_hotels(query, top_k=3)
        
        for idx, hotel in enumerate(results, 1):
            print(f"\n{idx}. {hotel['hotel_name']}")
            print(f"   Hotel ID: {hotel['hotel_id']}")
            print(f"   Rank: {hotel['hotel_rank']} sao")
            print(f"   Price: {hotel['hotel_price_average']:,.0f} VND" if hotel['hotel_price_average'] else "   Price: N/A")
            print(f"   Area: {hotel['area_name']}")
            print(f"   Similarity: {hotel['similarity_score']:.3f}")
    
    # Test RAG (with LLM)
    print("\n\n💬 Testing RAG (with LLM):")
    print("=" * 60)
    
    test_questions = [
        "Khách sạn nào 5 sao gần biển Đà Nẵng?",
        "Tôi muốn tìm khách sạn giá rẻ ở Sơn Trà",
        "Khách sạn nào có spa và hồ bơi?"
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        response = rag.ask(question)
        
        print(f"\n💡 Answer:")
        print(response["answer"])
        
        print(f"\n📚 Sources ({len(response['sources'])} hotels):")
        for idx, source in enumerate(response["sources"][:3], 1):
            print(f"  {idx}. {source['hotel_name']} (ID: {source['hotel_id']})")
    
    print("\n✅ RAG System Demo Complete!")


if __name__ == "__main__":
    main()

