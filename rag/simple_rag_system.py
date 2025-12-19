#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple RAG System cho Hotel Recommendation
Sử dụng LangChain + Ollama + Qdrant
"""

# CRITICAL: Set environment variables BEFORE any imports to prevent PyTorch loading
# This must be done before importing pandas, langchain, or any other libraries
import os
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TORCH_DISABLE_IMPORT'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import pandas as pd
import json
import hashlib
from typing import List, Dict, Optional
from functools import lru_cache
import logging
from pathlib import Path
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

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
    from data import DatabaseConnector, SmartChunker, HotelDataNormalizer, CouponDataNormalizer
except ImportError:
    logger.warning("Could not import data modules (connector, chunker, normalizer)")
    DatabaseConnector = None
    SmartChunker = None
    HotelDataNormalizer = None
    CouponDataNormalizer = None

# Import query router
try:
    from rag.core.query_router import QueryRouter
    from rag.core.sql_query_generator import SQLQueryGenerator
except ImportError:
    try:
        from core.query_router import QueryRouter
        from core.sql_query_generator import SQLQueryGenerator
    except ImportError:
        logger.warning("Could not import QueryRouter or SQLQueryGenerator")
        QueryRouter = None
        SQLQueryGenerator = None

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
                    max_tokens=512,  # Increased from 512 to allow longer, more detailed responses
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
                        max_tokens=512,  # Increased from 512 to allow longer, more detailed responses
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
        
        # Keyword extraction configuration
        self.use_llm_for_extraction = True  # Use LLM for keyword extraction (smart, flexible)
        
        # Initialize query router (for classifying statistical vs semantic queries)
        if QueryRouter is not None:
            self.query_router = QueryRouter(
                use_llm=True,  # Use LLM when confidence is low
                llm=self.llm
            )
            logger.info("✅ Query Router initialized")
        else:
            self.query_router = None
            logger.warning("⚠️  Query Router not available")
        
        # Initialize SQL query generator (for statistical queries)
        if SQLQueryGenerator is not None:
            self.sql_generator = SQLQueryGenerator(
                use_llm=True,  # Use LLM for complex queries
                llm=self.llm
            )
            logger.info("✅ SQL Query Generator initialized")
        else:
            self.sql_generator = None
            logger.warning("⚠️  SQL Query Generator not available")
    
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
                                   batch_size: int = 100,  # Tăng batch_size để nhanh hơn (optimized default)
                                   index_rooms: bool = True,  # Index rooms và type_rooms cùng lúc
                                   index_type_rooms: bool = True):
        """
        Index hotels từ database MySQL với smart chunking và incremental indexing
        
        Args:
            use_chunking: If True, use smart chunking (recommended for long texts)
            chunk_size: Size of each chunk (characters)
            chunk_overlap: Overlap between chunks (characters)
            incremental: If True, only index new/updated hotels
            recreate_collection: If True, recreate collection (will delete all data)
            batch_size: Number of hotels to process in each batch
            index_rooms: If True, also index rooms (default: True)
            index_type_rooms: If True, also index type_rooms (default: True)
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
        
        logger.info("✅ Hotel indexing complete!")
        
        # Index rooms and type_rooms if requested
        if index_rooms or index_type_rooms:
            try:
                from data.processor import DataProcessor
                logger.info("")
                logger.info("=" * 70)
                logger.info("🔄 Indexing Rooms and Type Rooms...")
                logger.info("=" * 70)
                
                processor = DataProcessor(rag=self)
                
                if index_rooms:
                    logger.info("📊 Indexing rooms...")
                    processor.process_and_index_rooms(
                        recreate_collection=False,
                        batch_size=batch_size
                    )
                
                if index_type_rooms:
                    logger.info("📊 Indexing type_rooms...")
                    processor.process_and_index_type_rooms(
                        recreate_collection=False,
                        batch_size=batch_size
                    )
                
                logger.info("✅ Rooms and Type Rooms indexing complete!")
            except Exception as e:
                logger.warning(f"⚠️  Failed to index rooms/type_rooms: {e}")
                logger.warning("   Continuing...")
        
        logger.info("✅ Database indexing complete!")
    
    def index_coupons_from_database(self,
                                   use_chunking: bool = True,
                                   chunk_size: int = 800,
                                   chunk_overlap: int = 50,
                                   incremental: bool = True,
                                   recreate_collection: bool = False,
                                   batch_size: int = 100,  # Optimized default batch size
                                   valid_only: bool = False):
        """
        Index coupons từ database MySQL với smart chunking và incremental indexing
        
        Args:
            use_chunking: If True, use smart chunking (recommended for long texts)
            chunk_size: Size of each chunk (characters)
            chunk_overlap: Overlap between chunks (characters)
            incremental: If True, only index new/updated coupons
            recreate_collection: If True, recreate collection (will delete all data)
            batch_size: Number of coupons to process in each batch
            valid_only: If True, only index valid coupons (not expired, qty > 0)
        """
        logger.info("🔄 Indexing coupons from database...")
        
        # Initialize database connector
        if DatabaseConnector is None:
            raise ImportError("DatabaseConnector not available. Please install pymysql and sqlalchemy.")
        
        if self.db_connector is None:
            self.db_connector = DatabaseConnector()
        
        # Test database connection
        if not self.db_connector.test_connection():
            raise ConnectionError("Failed to connect to database")
        
        # Initialize coupon normalizer
        if CouponDataNormalizer is None:
            raise ImportError("CouponDataNormalizer not available.")
        
        coupon_normalizer = CouponDataNormalizer()
        
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
        
        # Get coupons from database
        if incremental and not recreate_collection:
            # For coupons, we'll fetch all for now (can add timestamp tracking later)
            logger.info("📦 Fetching all coupons...")
            coupons_df = self.db_connector.get_coupons(valid_only=valid_only)
        else:
            logger.info("📦 Fetching all coupons...")
            coupons_df = self.db_connector.get_coupons(valid_only=valid_only)
        
        if coupons_df.empty:
            logger.info("✅ No coupons to index")
            return
        
        logger.info(f"📊 Found {len(coupons_df)} coupons to index")
        
        # Create documents with chunking
        all_documents = []
        
        if use_chunking:
            # Use smart chunking
            logger.info("📝 Creating documents with smart chunking...")
            for idx, coupon in coupons_df.iterrows():
                coupon_id = int(coupon["coupon_id"])
                
                # Create semantic text
                semantic_text = coupon_normalizer.create_semantic_text(coupon)
                
                if not semantic_text or not semantic_text.strip():
                    logger.warning(f"Coupon {coupon_id} has no semantic_text, skipping")
                    continue
                
                # Create coupon data dict
                coupon_data = {
                    "coupon_id": coupon_id,
                    "coupon_name": str(coupon.get("coupon_name", "")),
                    "coupon_name_code": str(coupon.get("coupon_name_code", "")),
                    "coupon_desc": str(coupon.get("coupon_desc", "")),
                    "coupon_price_sale": float(coupon.get("coupon_price_sale", 0)) if pd.notna(coupon.get("coupon_price_sale")) else None,
                    "coupon_qty_code": int(coupon.get("coupon_qty_code", 0)) if pd.notna(coupon.get("coupon_qty_code")) else None,
                    "coupon_start_date": str(coupon.get("coupon_start_date", "")) if pd.notna(coupon.get("coupon_start_date")) else None,
                    "coupon_end_date": str(coupon.get("coupon_end_date", "")) if pd.notna(coupon.get("coupon_end_date")) else None,
                    "is_valid": coupon_normalizer._is_coupon_valid(coupon),
                    "location": coupon_normalizer._extract_location(coupon),
                    "target_audience": coupon_normalizer._extract_target_audience(coupon),
                    "discount_category": coupon_normalizer._categorize_discount(
                        float(coupon.get("coupon_price_sale", 0))
                    ) if pd.notna(coupon.get("coupon_price_sale")) else "",
                    "normalized_name": coupon_normalizer.normalize_text(coupon.get("coupon_name", "")),
                }
                
                # Chunk coupon document
                chunks = self.chunker.chunk_coupon_document(coupon_data, semantic_text)
                all_documents.extend(chunks)
        else:
            # Use full text (no chunking)
            logger.info("📝 Creating documents without chunking...")
            for idx, coupon in coupons_df.iterrows():
                coupon_id = int(coupon["coupon_id"])
                
                # Create semantic text
                semantic_text = coupon_normalizer.create_semantic_text(coupon)
                
                if not semantic_text or not semantic_text.strip():
                    logger.warning(f"Coupon {coupon_id} has no semantic_text, skipping")
                    continue
                
                # Truncate if too long
                max_text_length = 2000
                if len(semantic_text) > max_text_length:
                    logger.debug(f"Truncating coupon {coupon_id} text from {len(semantic_text)} to {max_text_length} chars")
                    semantic_text = semantic_text[:max_text_length] + "..."
                
                # Create document
                doc = Document(
                    page_content=semantic_text,
                    metadata={
                        "coupon_id": coupon_id,
                        "coupon_name": str(coupon.get("coupon_name", "")),
                        "coupon_name_code": str(coupon.get("coupon_name_code", "")),
                        "coupon_price_sale": float(coupon.get("coupon_price_sale", 0)) if pd.notna(coupon.get("coupon_price_sale")) else None,
                        "is_valid": coupon_normalizer._is_coupon_valid(coupon),
                        "location": coupon_normalizer._extract_location(coupon),
                        "target_audience": coupon_normalizer._extract_target_audience(coupon),
                        "discount_category": coupon_normalizer._categorize_discount(
                            float(coupon.get("coupon_price_sale", 0))
                        ) if pd.notna(coupon.get("coupon_price_sale")) else "",
                        "normalized_name": coupon_normalizer.normalize_text(coupon.get("coupon_name", "")),
                        "document_type": "coupon",
                    }
                )
                all_documents.append(doc)
        
        logger.info(f"✅ Created {len(all_documents)} documents from {len(coupons_df)} coupons")
        
        # Store in Qdrant (use same collection as hotels, but with document_type="coupon")
        self._store_documents_in_qdrant(
            all_documents,
            recreate_collection=recreate_collection,
            batch_size=batch_size,
            use_upsert=incremental and not recreate_collection
        )
        
        # Initialize retriever and QA chain
        self._initialize_qa_chain()
        
        logger.info("✅ Coupon database indexing complete!")
    
    def _embed_batch_parallel(self, texts: List[str], max_workers: int = 5) -> List[List[float]]:
        """
        Embed texts in parallel using ThreadPoolExecutor để tăng tốc độ
        
        Args:
            texts: List of texts to embed
            max_workers: Number of parallel workers (default: 5)
        
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        # Use embed_documents if available (may still be faster due to caching)
        # But if OllamaEmbeddings.embed_documents is sequential, use parallel embedding
        def embed_single(text: str) -> List[float]:
            """Embed single text - used for parallel processing"""
            return self.embeddings.embed_query(text)
        
        # For small batches, use sequential (overhead of threading not worth it)
        if len(texts) <= 3:
            return [embed_single(text) for text in texts]
        
        # Parallel embedding for larger batches
        results = [None] * len(texts)
        text_to_index = {text: idx for idx, text in enumerate(texts)}
        
        with ThreadPoolExecutor(max_workers=min(max_workers, len(texts))) as executor:
            # Submit all tasks
            future_to_text = {executor.submit(embed_single, text): text for text in texts}
            
            # Collect results as they complete
            for future in as_completed(future_to_text):
                text = future_to_text[future]
                idx = text_to_index[text]
                try:
                    embedding = future.result()
                    # Validate embedding is not None and is a valid list
                    if embedding is None:
                        logger.error(f"Embedding returned None for text '{text[:50]}...', trying fallback")
                        raise ValueError("Embedding is None")
                    if not isinstance(embedding, list) or len(embedding) == 0:
                        logger.error(f"Invalid embedding type for text '{text[:50]}...': {type(embedding)}, trying fallback")
                        raise ValueError(f"Invalid embedding type: {type(embedding)}")
                    results[idx] = embedding
                except Exception as e:
                    logger.error(f"Error embedding text '{text[:50]}...': {e}")
                    # Fallback to sequential embedding for this text
                    try:
                        embedding = embed_single(text)
                        if embedding is None:
                            logger.error(f"Fallback embedding also returned None for text '{text[:50]}...'")
                            results[idx] = None  # Will be skipped later
                        elif not isinstance(embedding, list) or len(embedding) == 0:
                            logger.error(f"Fallback embedding invalid for text '{text[:50]}...': {type(embedding)}")
                            results[idx] = None  # Will be skipped later
                        else:
                            results[idx] = embedding
                    except Exception as fallback_error:
                        logger.error(f"Fallback embedding also failed for text '{text[:50]}...': {fallback_error}")
                        results[idx] = None  # Will be skipped later
        
        return results
    
    def _calculate_optimal_batch_size(self, documents: List[Document], default: int = 100) -> int:
        """
        Calculate optimal batch size based on average text length
        
        Args:
            documents: List of documents
            default: Default batch size
        
        Returns:
            Optimal batch size
        """
        if not documents:
            return default
        
        # Calculate average text length
        total_length = sum(len(doc.page_content or "") for doc in documents)
        avg_length = total_length / len(documents)
        
        # Adjust batch size based on text length
        if avg_length < 500:
            return min(200, default * 2)  # Small texts → larger batches
        elif avg_length < 1000:
            return default  # Medium texts → default
        else:
            return max(50, default // 2)  # Large texts → smaller batches
    
    def _store_documents_in_qdrant(self,
                                   documents: List[Document],
                                   recreate_collection: bool = False,
                                   batch_size: int = 100,  # Tăng batch_size mặc định từ 50 lên 100
                                   use_upsert: bool = False,
                                   parallel_embedding: bool = True,
                                   max_embedding_workers: int = 5):
        """
        Store documents in Qdrant với batch processing và parallel embedding
        
        Args:
            documents: List of Document objects
            recreate_collection: If True, recreate collection
            batch_size: Number of documents per batch (default: 100, optimized)
            use_upsert: If True, use upsert instead of add (for incremental updates)
            parallel_embedding: If True, use parallel embedding (default: True)
            max_embedding_workers: Number of parallel workers for embedding (default: 5)
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
            
            # Calculate optimal batch size if not specified
            if batch_size == 100:  # Default value
                optimal_batch_size = self._calculate_optimal_batch_size(documents, default=batch_size)
                if optimal_batch_size != batch_size:
                    logger.info(f"📊 Adjusted batch_size from {batch_size} to {optimal_batch_size} based on text length")
                    batch_size = optimal_batch_size
            
            # Store documents in batches
            total_batches = (len(documents) + batch_size - 1) // batch_size
            logger.info(f"🔄 Processing {total_batches} batches (batch_size={batch_size}, parallel_embedding={parallel_embedding})")
            
            batch_start_time = time.time()
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                batch_num = i // batch_size + 1
                
                batch_iter_start = time.time()
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
                            # Support both hotels and coupons
                            document_type = doc.metadata.get("document_type", "hotel")
                            
                            # Check if ID is already provided in metadata (for room, type_room, etc.)
                            if "id" in doc.metadata:
                                # Use provided ID directly
                                try:
                                    doc_id = int(doc.metadata["id"])
                                except (ValueError, TypeError):
                                    logger.warning(f"Invalid ID in metadata: {doc.metadata.get('id')}, generating new ID")
                                    doc_id = None
                            else:
                                doc_id = None
                            
                            # Generate ID if not provided
                            if doc_id is None:
                                if document_type == "coupon":
                                    # For coupons: use coupon_id * 1000000 + chunk_index + 1000000000000 (1 trillion offset)
                                    # This ensures no conflict with hotels
                                    coupon_id = doc.metadata.get("coupon_id", 0)
                                    chunk_idx = doc.metadata.get("chunk_index", 0)
                                    
                                    try:
                                        coupon_id = int(coupon_id) if coupon_id is not None else 0
                                        chunk_idx = int(chunk_idx) if chunk_idx is not None else 0
                                    except (ValueError, TypeError):
                                        logger.warning(f"Invalid coupon_id or chunk_index: coupon_id={coupon_id}, chunk_idx={chunk_idx}")
                                        coupon_id = 0
                                        chunk_idx = 0
                                    
                                    # Create unique integer ID with offset: 1000000000000 + coupon_id * 1000000 + chunk_index
                                    # This allows up to 1,000,000 chunks per coupon
                                    # Example: coupon_id=5, chunk_idx=0 -> 1000000005000
                                    doc_id = 1000000000000 + (coupon_id * 1000000) + chunk_idx
                                    
                                    # Store chunk_id as string in metadata for reference (if not exists)
                                    if "chunk_id" not in doc.metadata:
                                        doc.metadata["chunk_id"] = f"coupon_{coupon_id}_{chunk_idx}"
                                elif document_type == "room":
                                    # For rooms: use room_id + 2000000 offset
                                    # Room ID range: 2,000,000 - 2,999,999
                                    room_id = doc.metadata.get("room_id", 0)
                                    try:
                                        room_id = int(room_id) if room_id is not None else 0
                                    except (ValueError, TypeError):
                                        logger.warning(f"Invalid room_id: {room_id}")
                                        room_id = 0
                                    
                                    doc_id = 2000000 + room_id
                                    
                                    # Store chunk_id as string in metadata for reference (if not exists)
                                    if "chunk_id" not in doc.metadata:
                                        doc.metadata["chunk_id"] = f"room_{room_id}"
                                elif document_type == "type_room":
                                    # For type_rooms: use type_room_id + 3000000 offset
                                    # Type Room ID range: 3,000,000 - 3,999,999
                                    type_room_id = doc.metadata.get("type_room_id", 0)
                                    try:
                                        type_room_id = int(type_room_id) if type_room_id is not None else 0
                                    except (ValueError, TypeError):
                                        logger.warning(f"Invalid type_room_id: {type_room_id}")
                                        type_room_id = 0
                                    
                                    doc_id = 3000000 + type_room_id
                                    
                                    # Store chunk_id as string in metadata for reference (if not exists)
                                    if "chunk_id" not in doc.metadata:
                                        doc.metadata["chunk_id"] = f"type_room_{type_room_id}"
                                else:
                                    # For hotels (default): use hotel_id * 1000000 + chunk_index (original logic)
                                    hotel_id = doc.metadata.get("hotel_id", 0)
                                    chunk_idx = doc.metadata.get("chunk_index", 0)
                                    
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
                            # OPTIMIZED: Avoid copying metadata if not needed (saves memory)
                            batch_ids.append(doc_id)
                            batch_texts.append(page_content)
                            # Use metadata directly - no need to copy if we're not modifying it
                            batch_metadatas.append(doc.metadata)  # Direct reference, no copy
                        
                        # Use Qdrant client directly to properly handle integer IDs
                        # Qdrant requires integer IDs to be passed as integers, not strings
                        # LangChain's add_texts converts IDs to strings which Qdrant rejects
                        try:
                            # Generate embeddings for all texts in batch
                            embed_start = time.time()
                            
                            if parallel_embedding and len(batch_texts) > 3:
                                # Use parallel embedding for better performance
                                embeddings_list = self._embed_batch_parallel(
                                    batch_texts, 
                                    max_workers=max_embedding_workers
                                )
                            else:
                                # Use sequential embedding (for small batches or if parallel disabled)
                                # embed_documents may use caching which is still beneficial
                                embeddings_list = self.embeddings.embed_documents(batch_texts)
                            
                            embed_time = time.time() - embed_start
                            logger.debug(f"Generated {len(embeddings_list)} embeddings in {embed_time:.2f}s (parallel={parallel_embedding and len(batch_texts) > 3})")
                            
                            # Validate embeddings before creating points
                            if len(embeddings_list) != len(batch_ids):
                                raise ValueError(f"Mismatch: {len(embeddings_list)} embeddings for {len(batch_ids)} documents")
                            
                            # Create PointStruct objects with integer IDs (OPTIMIZED: avoid unnecessary copying)
                            points = []
                            skipped_count = 0
                            for doc_id, embedding, text, metadata in zip(batch_ids, embeddings_list, batch_texts, batch_metadatas):
                                # Skip documents with None or invalid embeddings
                                if embedding is None:
                                    logger.warning(f"Skipping document {doc_id}: embedding is None")
                                    skipped_count += 1
                                    continue
                                
                                # Validate embedding is a list of numbers
                                if not isinstance(embedding, list) or len(embedding) == 0:
                                    logger.warning(f"Skipping document {doc_id}: invalid embedding type or empty (type={type(embedding)}, len={len(embedding) if hasattr(embedding, '__len__') else 'N/A'})")
                                    skipped_count += 1
                                    continue
                                
                                # Prepare payload - include page_content for retrieval
                                # OPTIMIZED: Direct unpacking instead of copy + update
                                payload = {
                                    'page_content': text,  # Required for retrieval
                                    **metadata  # Direct unpacking - more efficient than copy + update
                                }
                                
                                # Create point with integer ID (not string!)
                                point = PointStruct(
                                    id=doc_id,  # Use integer ID directly
                                    vector=embedding,
                                    payload=payload
                                )
                                points.append(point)
                            
                            if skipped_count > 0:
                                logger.warning(f"Skipped {skipped_count} documents with invalid embeddings in batch {batch_num}")
                            
                            if not points:
                                logger.warning(f"No valid points to insert in batch {batch_num}, skipping")
                                continue
                            
                            # Use upsert (works for both insert and update)
                            # OPTIMIZED: Use wait=False for faster processing, but ensure data persistence
                            upsert_start = time.time()
                            client.upsert(
                                collection_name=self.collection_name,
                                points=points,
                                wait=True  # Keep wait=True for data safety, but can be False for speed
                                # Note: wait=False is faster but may lose data on crash
                                # For production, consider batching confirmations instead
                            )
                            upsert_time = time.time() - upsert_start
                            
                            batch_iter_time = time.time() - batch_iter_start
                            logger.info(f"✅ Batch {batch_num}/{total_batches} completed in {batch_iter_time:.2f}s (embed: {embed_time:.2f}s, upsert: {upsert_time:.2f}s)")
                            
                        except Exception as e:
                            logger.error(f"Error adding points to Qdrant: {e}")
                            raise
                        
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
            
            total_time = time.time() - batch_start_time
            logger.info(f"✅ Successfully stored {len(documents)} documents in {total_time:.2f}s ({len(documents)/total_time:.1f} docs/sec)")
            
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
                "k": 3  # Increased from 2 to 5 for more comprehensive responses
            }
        )
        
        # Create QA chain với prompt chi tiết hơn để có response dài hơn
        prompt_template = """Bạn là trợ lý tư vấn khách sạn tại Đà Nẵng. Trả lời bằng tiếng Việt.

=== THÔNG TIN KHÁCH SẠN ===
{context}

=== CÂU HỎI ===
{question}

=== HƯỚNG DẪN TRẢ LỜI ===

BƯỚC 1 - PHÂN TÍCH CONTEXT:
Mỗi block thông tin khách sạn có cấu trúc:
- Dòng đầu tiên: "Khách sạn [TÊN]" hoặc "Tên khách sạn: [TÊN]" → Đây là TÊN CHÍNH THỨC
- Các dòng tiếp theo: Mô tả, Địa chỉ, Khu vực, Thương hiệu, Từ khóa, Hạng, Giá
- Dòng "Thương hiệu:" là thông tin PHỤ, CHỈ dùng để phân loại, KHÔNG phải tên khách sạn

BƯỚC 2 - TRÍCH XUẤT TÊN KHÁCH SẠN:
Với mỗi khách sạn trong context, BẮT BUỘC:
1. Tìm dòng "Khách sạn [TÊN]" hoặc "Tên khách sạn: [TÊN]" ở ĐẦU block
2. Copy CHÍNH XÁC [TÊN] đó, KHÔNG được thay đổi hoặc rút gọn
3. BỎ QUA hoàn toàn dòng "Thương hiệu:" khi đặt tên

BƯỚC 3 - TRẢ LỜI:
Với mỗi khách sạn phù hợp, viết theo format:
"Khách sạn: [TÊN CHÍNH XÁC từ bước 2]
- Địa chỉ: [từ context]
- Giá: [từ context]
- Hạng: [từ context]
- Tiện ích: [từ context]"

=== VÍ DỤ CỤ THỂ ===

VÍ DỤ CONTEXT:
"Khách sạn Grand Tourane | Tên khách sạn: Grand Tourane | Mô tả: ... | Địa chỉ: 252 Võ Nguyên Giáp | Thương hiệu: InterContinental Hotels Group | Hạng: 5 sao | Giá: 1,523,515 VND"

CÂU HỎI: "Khách sạn 5 sao nào?"

TRẢ LỜI ĐÚNG:
"Khách sạn: Grand Tourane
- Địa chỉ: 252 Võ Nguyên Giáp, Sơn Trà
- Giá: 1,523,515 VND
- Đánh giá: 5 sao"

TRẢ LỜI SAI (TUYỆT ĐỐI TRÁNH):
"Khách sạn: InterContinental Đà Nẵng" ← SAI vì dùng brand name
"Khách sạn: Grand Tourane thuộc InterContinental" ← SAI vì thêm brand vào tên

=== QUY TẮC BỔ SUNG ===
- Chỉ trả lời câu hỏi về khách sạn tại Đà Nẵng
- Nếu không tìm thấy khách sạn phù hợp: "Không tìm thấy khách sạn phù hợp trong hệ thống"
- Nếu câu hỏi không liên quan du lịch: "Xin lỗi, tôi chỉ tư vấn về khách sạn tại Đà Nẵng"

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
    
    def _build_qdrant_filter(self, location: Optional[str] = None, 
                            rank: Optional[int] = None,
                            price_range: Optional[str] = None,
                            brand: Optional[str] = None) -> Optional['Filter']:
        """
        Build Qdrant filter từ extracted keywords
        
        Args:
            location: Area name
            rank: Hotel rank (1-5)
            price_range: "budget" or "luxury"
            brand: Brand name
            
        Returns:
            Qdrant Filter object hoặc None nếu không có filters
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
        
        conditions = []
        
        if location:
            conditions.append(
                FieldCondition(key="area_name", match=MatchValue(value=location))
            )
        
        if rank:
            conditions.append(
                FieldCondition(key="hotel_rank", match=MatchValue(value=rank))
            )
        
        if price_range:
            # Map price_range to price_category
            price_category_map = {
                "budget": ["budget", "economy"],
                "luxury": ["luxury", "premium"]
            }
            # Note: Qdrant không hỗ trợ "in" filter trực tiếp cho string
            # Có thể dùng should với multiple conditions hoặc post-filter
            # Tạm thời chỉ filter nếu có price_category trong metadata
            # (Cần check xem price_category có được store không)
            pass  # Post-filter sẽ handle price_range
        
        if brand:
            # Brand matching cần fuzzy, không nên filter strict
            # Post-filter sẽ handle brand
            pass
        
        if not conditions:
            return None
        
        return Filter(must=conditions)
    
    def _get_amenity_synonyms(self, amenity: str) -> List[str]:
        """Get synonyms for amenity keyword"""
        amenity_synonyms = {
            "hồ bơi": ["hồ bơi", "bể bơi", "pool", "swimming pool", "bơi"],
            "spa": ["spa", "massage", "thư giãn", "massage spa"],
            "gym": ["gym", "phòng gym", "thể hình", "fitness", "phòng tập"],
            "nhà hàng": ["nhà hàng", "restaurant", "quán ăn"],
            "wifi": ["wifi", "internet", "mạng"],
            "parking": ["bãi đỗ xe", "parking", "đậu xe", "đỗ xe", "chỗ đậu xe"],
            "breakfast": ["bữa sáng", "breakfast", "ăn sáng", "sáng"],
            "airport": ["sân bay", "airport", "gần sân bay", "cách sân bay"],
            "beach": ["gần biển", "ven biển", "sát biển", "cách biển", "bờ biển", "beach", "view biển", "hướng biển"],
            "center": ["trung tâm", "center", "gần trung tâm", "trong trung tâm"]
        }
        return amenity_synonyms.get(amenity, [amenity])
    
    def _format_hotel_result(self, payload: Dict, similarity_score: float, page_content: str = "") -> Dict:
        """
        Format hotel result từ payload
        
        Args:
            payload: Qdrant payload hoặc metadata
            similarity_score: Similarity score
            page_content: Text content (optional)
            
        Returns:
            Formatted hotel dict
        """
        return {
            "hotel_id": payload.get("hotel_id"),
            "hotel_name": payload.get("hotel_name", ""),
            "hotel_rank": payload.get("hotel_rank"),
            "hotel_price_average": payload.get("hotel_price_average"),
            "area_name": payload.get("area_name", ""),
            "brand_name": payload.get("brand_name", ""),
            "price_category": payload.get("price_category", ""),
            "similarity_score": float(similarity_score),
            "text_preview": page_content[:200] + "..." if len(page_content) > 200 else page_content
        }
    
    def _matches_keyword_filters(self, payload: Dict, page_content: str, extracted_keywords: Dict) -> bool:
        """
        Check if hotel matches extracted keyword filters (rank, price, brand, amenities)
        
        Args:
            payload: Hotel payload/metadata
            page_content: Hotel text content
            extracted_keywords: Extracted keywords dict
            
        Returns:
            True if matches all filters, False otherwise
        """
        # Check rank filter
        if extracted_keywords.get("rank") and payload.get("hotel_rank"):
            if payload.get("hotel_rank") != extracted_keywords["rank"]:
                return False
        
        # Check price_range filter
        if extracted_keywords.get("price_range"):
            hotel_price_category = payload.get("price_category", "")
            if extracted_keywords["price_range"] == "budget" and hotel_price_category not in ["budget", "economy"]:
                return False
            elif extracted_keywords["price_range"] == "luxury" and hotel_price_category not in ["luxury", "premium"]:
                return False
        
        # Check brand filter
        if extracted_keywords.get("brand"):
            hotel_brand = payload.get("brand_name", "").lower()
            if extracted_keywords["brand"].lower() not in hotel_brand:
                return False
        
        # Check amenities filter (text-based)
        if extracted_keywords.get("amenities"):
            page_content_lower = page_content.lower()
            amenities_match = all(
                any(syn in page_content_lower for syn in self._get_amenity_synonyms(amenity))
                for amenity in extracted_keywords["amenities"]
            )
            if not amenities_match:
                return False
        
        return True
    
    def _extract_keywords_from_query(self, query: str, use_llm: bool = True) -> Dict:
        """
        Extract keywords từ query (location, rank, price, amenities, brand)
        
        Args:
            query: Search query
            use_llm: Nếu True, dùng LLM để extract (smart, flexible). Nếu False, dùng rule-based (fast, predictable)
            
        Returns:
            Dictionary với các keywords đã extract:
            {
                "location": "Ngũ Hành Sơn" or None,
                "rank": 5 or None,
                "price_range": "budget" or "luxury" or None,
                "amenities": ["hồ bơi", "spa"] or [],
                "brand": "Sheraton" or None,
                "keywords": ["gần biển", "view biển"] or []
            }
        """
        if use_llm and self.llm is not None:
            # Use LLM for smart extraction (hiểu ngữ nghĩa tự nhiên)
            return self._extract_keywords_with_llm(query)
        else:
            # Use rule-based extraction (fast, predictable)
            return self._extract_keywords_rule_based(query)
    
    def _extract_keywords_with_llm(self, query: str) -> Dict:
        """
        Extract keywords using LLM (smart, flexible)
        LLM hiểu ngữ nghĩa tự nhiên và handle variations tốt hơn
        """
        try:
            from langchain.prompts import PromptTemplate
            from langchain.schema import HumanMessage
            
            # Prompt đơn giản: chỉ extract keywords quan trọng để Qdrant search tốt hơn
            extraction_prompt = """Bạn là hệ thống trích xuất từ khóa từ câu hỏi tìm kiếm khách sạn.
Từ câu hỏi sau, trích xuất các từ khóa quan trọng (keywords) để tìm kiếm tốt hơn.

Câu hỏi: {query}

Nhiệm vụ: Trích xuất các từ khóa quan trọng từ câu hỏi (bỏ qua các từ ngữ pháp, từ thừa).
Ví dụ:
- "Khách sạn nào có view biển đẹp ở Ngũ Hành Sơn?" → ["view biển", "Ngũ Hành Sơn"]
- "Tìm khách sạn 5 sao có hồ bơi giá rẻ" → ["5 sao", "hồ bơi", "giá rẻ"]
- "Resort sang trọng gần biển có spa" → ["resort", "sang trọng", "gần biển", "spa"]

Trả về JSON format:
{{
    "keywords": ["từ khóa 1", "từ khóa 2", ...]
}}

CHỈ trả về JSON, không có text khác."""

            # Build prompt
            prompt = extraction_prompt.format(query=query)
            
            # Call LLM
            # ChatOpenAI và Ollama đều support invoke với messages
            if isinstance(self.llm, ChatOpenAI):
                # ChatOpenAI (LM Studio)
                from langchain.schema import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                response_text = response.content if hasattr(response, 'content') else str(response)
            elif hasattr(self.llm, 'predict'):
                # Ollama (có thể dùng predict)
                response_text = self.llm.predict(prompt)
            else:
                # Fallback: invoke trực tiếp
                response_text = self.llm.invoke(prompt)
            
            # Parse JSON response
            import json
            import re
            
            # Extract JSON từ response (có thể có text thêm)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            result = json.loads(response_text)
            
            # Validate và normalize
            if not isinstance(result, dict) or "keywords" not in result:
                logger.warning("LLM returned invalid format, falling back to rule-based")
                return self._extract_keywords_rule_based(query)
            
            extracted_keywords_list = result.get("keywords", [])
            if not isinstance(extracted_keywords_list, list):
                extracted_keywords_list = []
            
            # Vẫn cần extract location cho filtering (nếu có)
            location = self._extract_location_from_query(query)
            
            # Format về structure cũ để tương thích
            keywords = {
                "location": location,
                "rank": None,
                "price_range": None,
                "amenities": [],
                "brand": None,
                "keywords": extracted_keywords_list  # Keywords từ LLM
            }
            
            logger.info(f"Extracted keywords with LLM: {extracted_keywords_list}")
            return keywords
            
        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}, falling back to rule-based")
            return self._extract_keywords_rule_based(query)
    
    def _extract_keywords_rule_based(self, query: str) -> Dict:
        """
        Extract keywords using rule-based patterns (fast, predictable)
        Fallback khi LLM không available hoặc fail
        """
        query_lower = query.lower().strip()
        keywords = {
            "location": None,
            "rank": None,
            "price_range": None,
            "amenities": [],
            "brand": None,
            "keywords": []
        }
        
        # 1. Extract location (đã có method)
        keywords["location"] = self._extract_location_from_query(query)
        
        # 2. Extract rank (sao)
        rank_patterns = {
            5: ["5 sao", "năm sao", "5 stars", "luxury", "cao cấp", "sang trọng", "premium"],
            4: ["4 sao", "bốn sao", "4 stars"],
            3: ["3 sao", "ba sao", "3 stars"],
            2: ["2 sao", "hai sao", "2 stars"],
            1: ["1 sao", "một sao", "1 stars"]
        }
        
        for rank, patterns in rank_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                keywords["rank"] = rank
                logger.debug(f"Extracted rank: {rank} sao")
                break
        
        # 3. Extract price range
        budget_patterns = ["giá rẻ", "giá tốt", "giá hợp lý", "giá phải chăng", "giá thấp", "rẻ", "tầm thấp"]
        luxury_patterns = ["giá cao", "giá đắt", "giá đắt đỏ", "premium", "đắt", "tầm cao", "luxury"]
        
        if any(pattern in query_lower for pattern in budget_patterns):
            keywords["price_range"] = "budget"
            logger.debug("Extracted price_range: budget")
        elif any(pattern in query_lower for pattern in luxury_patterns):
            keywords["price_range"] = "luxury"
            logger.debug("Extracted price_range: luxury")
        
        # 4. Extract amenities
        amenities_mapping = {
            "hồ bơi": ["hồ bơi", "bể bơi", "pool", "swimming pool", "bơi"],
            "spa": ["spa", "massage", "thư giãn", "massage spa"],
            "gym": ["gym", "phòng gym", "thể hình", "fitness", "phòng tập"],
            "nhà hàng": ["nhà hàng", "restaurant", "quán ăn"],
            "wifi": ["wifi", "internet", "mạng"],
            "parking": ["bãi đỗ xe", "parking", "đậu xe", "đỗ xe", "chỗ đậu xe"],
            "breakfast": ["bữa sáng", "breakfast", "ăn sáng", "sáng"],
            "airport": ["sân bay", "airport", "gần sân bay", "cách sân bay"],
            "beach": ["gần biển", "ven biển", "sát biển", "cách biển", "bờ biển", "beach"],
            "center": ["trung tâm", "center", "gần trung tâm", "trong trung tâm"]
        }
        
        for amenity, patterns in amenities_mapping.items():
            if any(pattern in query_lower for pattern in patterns):
                keywords["amenities"].append(amenity)
                logger.debug(f"Extracted amenity: {amenity}")
        
        # 5. Extract brand (common hotel brands in Đà Nẵng)
        brand_patterns = {
            "Sheraton": ["sheraton"],
            "InterContinental": ["intercontinental", "inter continental"],
            "Melia": ["melia", "meliá"],
            "Vinpearl": ["vinpearl"],
            "Furama": ["furama"],
            "Pullman": ["pullman"],
            "Novotel": ["novotel"],
            "Hyatt": ["hyatt"],
            "Hilton": ["hilton"],
            "Marriott": ["marriott"]
        }
        
        for brand, patterns in brand_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                keywords["brand"] = brand
                logger.debug(f"Extracted brand: {brand}")
                break
        
        # 6. Extract additional keywords (view, features)
        keyword_patterns = {
            "view biển": ["view biển", "hướng biển", "nhìn ra biển", "tầm nhìn biển", "view beach"],
            "view sông": ["view sông", "hướng sông", "nhìn ra sông", "tầm nhìn sông", "view river"],
            "view thành phố": ["view thành phố", "hướng thành phố", "nhìn ra thành phố", "view city"],
            "family": ["gia đình", "family", "cho gia đình", "phù hợp gia đình"],
            "romantic": ["lãng mạn", "romantic", "cặp đôi", "honeymoon"],
            "business": ["công tác", "business", "doanh nhân"]
        }
        
        for keyword, patterns in keyword_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                keywords["keywords"].append(keyword)
                logger.debug(f"Extracted keyword: {keyword}")
        
        # Log extracted keywords
        if any(v for v in keywords.values() if v):
            logger.info(f"Extracted keywords (rule-based): {keywords}")
        
        return keywords
    
    def _search_with_qdrant_filter(self, query: str, query_embedding: List[float], 
                                   area_name: str, extracted_keywords: Dict, 
                                   top_k: int) -> List[Dict]:
        """
        Search hotels using QdrantClient with location filter (Layer 2: Retrieval Pipeline)
        
        Args:
            query: Search query
            query_embedding: Query embedding vector
            area_name: Location to filter
            extracted_keywords: Extracted keywords
            top_k: Number of results
            
        Returns:
            List of hotel results
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        client = QdrantClient(url=self.qdrant_url)
        
        # Build Qdrant filter
        qdrant_filter = self._build_qdrant_filter(
            location=area_name,
            rank=extracted_keywords.get("rank"),
            price_range=extracted_keywords.get("price_range"),
            brand=extracted_keywords.get("brand")
        )
        
        # Search with filter
        search_results = client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=min(top_k * 2, 10),  # Get more results for post-filtering
            query_filter=qdrant_filter,
            with_payload=True,
            with_vectors=False
        )
        
        # Format and post-filter results
        hotels = []
        for result in search_results:
            payload = result.payload or {}
            hotel_area = payload.get("area_name", "")
            
            # Post-filter: location must match
            if not hotel_area or hotel_area.strip() != area_name:
                continue
            
            # Get page_content
            page_content = payload.get("content") or payload.get("text") or ""
            
            # Post-filter: keyword filters (rank, price, brand, amenities)
            if not self._matches_keyword_filters(payload, page_content, extracted_keywords):
                continue
            
            # Format result
            hotels.append(self._format_hotel_result(payload, result.score, page_content))
            
            if len(hotels) >= top_k:
                break
        
        logger.info(f"Found {len(hotels)} hotels in {area_name} (after filtering)")
        return hotels
    
    def _search_without_filter(self, query: str, query_embedding: List[float],
                               area_name: Optional[str], extracted_keywords: Dict,
                               top_k: int) -> List[Dict]:
        """
        Search hotels using LangChain vectorstore without filter (Layer 2: Retrieval Pipeline)
        
        Args:
            query: Search query
            query_embedding: Query embedding vector (not used, but kept for consistency)
            area_name: Optional location for post-filtering
            extracted_keywords: Extracted keywords
            top_k: Number of results
            
        Returns:
            List of hotel results
        """
        # Use LangChain vectorstore for simple semantic search
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=min(top_k * 2, 10)  # Get more results for post-filtering
        )
        
        hotels = []
        for doc, score in results:
            # Convert distance to similarity
            similarity_score = max(0, 1 - score)
            
            # Filter by similarity threshold
            if similarity_score < 0.3:
                continue
            
            # Validate hotel name
            hotel_name = doc.metadata.get("hotel_name", "").strip()
            if not hotel_name:
                continue
            
            # Post-filter: location (if specified)
            hotel_area = doc.metadata.get("area_name", "")
            if area_name and hotel_area and hotel_area.strip() != area_name:
                continue
            
            # Post-filter: keyword filters
            if not self._matches_keyword_filters(doc.metadata, doc.page_content, extracted_keywords):
                continue
            
            # Format result
            hotels.append(self._format_hotel_result(
                doc.metadata, 
                similarity_score, 
                doc.page_content
            ))
            
            if len(hotels) >= top_k:
                break
        
        return hotels
    
    def search_hotels(self, query: str, top_k: int = 5, area_name: Optional[str] = None) -> List[Dict]:
        """
        Search hotels by query (semantic search with optional location filtering)
        
        Architecture: Layer 2 - Retrieval Pipeline
        - Uses QdrantClient for filtered search (location)
        - Uses LangChain vectorstore for simple search
        - Post-filters by extracted keywords
        
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
        
        # Extract keywords from query (use LLM nếu available, fallback to rule-based)
        extracted_keywords = self._extract_keywords_from_query(
            query, 
            use_llm=self.use_llm_for_extraction
        )
        
        # Extract location from query if not provided
        if area_name is None:
            area_name = extracted_keywords.get("location")
        
        # Attach extracted keywords to query để cải thiện semantic search
        enhanced_query = query
        if extracted_keywords.get("keywords"):
            keywords_str = " ".join(extracted_keywords["keywords"])
            enhanced_query = f"{query} {keywords_str}"
            logger.debug(f"Enhanced query with keywords: {enhanced_query}")
        
        # Generate query embedding (cached)
        query_embedding = self.embeddings.embed_query(enhanced_query)
        
        # Route to appropriate search method
        if area_name:
            logger.info(f"Filtering by location: {area_name}")
            # Use QdrantClient for filtered search (Layer 2: Retrieval Pipeline)
            hotels = self._search_with_qdrant_filter(
                enhanced_query, query_embedding, area_name, extracted_keywords, top_k
            )
            
            # If no results with filter, try without filter but warn
            if len(hotels) == 0:
                logger.warning(f"No hotels found in {area_name} with filter. Trying without filter...")
                hotels = self._search_without_filter(
                    enhanced_query, query_embedding, None, extracted_keywords, top_k
                )
        else:
            # Use LangChain vectorstore for simple search (Layer 2: Retrieval Pipeline)
            hotels = self._search_without_filter(
                enhanced_query, query_embedding, None, extracted_keywords, top_k
            )
        
        return hotels
    
    def ask(self, question: str) -> Dict:
        """
        Ask question với RAG hoặc SQL tùy loại câu hỏi
        
        Architecture: Layer 3 - Generation Pipeline với Query Routing
        - Phân loại câu hỏi: Statistical (SQL) vs Semantic (RAG)
        - Uses LangChain RetrievalQA chain cho semantic queries
        - TODO: Uses SQL query cho statistical queries
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and sources
        """
        if self.qa_chain is None:
            raise ValueError("QA chain not initialized. Call index_hotels first.")
        
        logger.info(f"Question: '{question}'")
        
        # 1. Phân loại câu hỏi (nếu có query router)
        query_type = "semantic"  # Default
        classification = None
        
        if self.query_router is not None:
            logger.info("✅ QueryRouter is available, classifying query...")
            classification = self.query_router.classify_query(question)
            query_type = classification["type"]
            confidence = classification["confidence"]
            
            logger.info(f"📊 Query classified as: {query_type} (confidence: {confidence:.2f})")
            logger.info(f"   Reason: {classification.get('reason', 'N/A')}")
            logger.info(f"   Method: {classification.get('method', 'N/A')}")
        else:
            logger.warning("⚠️  QueryRouter is None, defaulting to semantic (RAG)")
        
        # 2. Route to appropriate handler
        if query_type == "statistical":
            logger.info("🔍 Routing to SQL handler...")
            # Check if SQL generator and DB connector are available
            if self.sql_generator is None:
                logger.warning("⚠️  SQL generator is None, using RAG fallback")
                return self._ask_with_rag(question)
            
            # Initialize DB connector if not already done
            if self.db_connector is None:
                logger.info("🔄 Initializing database connector...")
                if DatabaseConnector is None:
                    logger.error("❌ DatabaseConnector not available, using RAG fallback")
                    return self._ask_with_rag(question)
                try:
                    self.db_connector = DatabaseConnector()
                    if not self.db_connector.test_connection():
                        logger.error("❌ Database connection failed, using RAG fallback")
                        return self._ask_with_rag(question)
                    logger.info("✅ Database connector initialized successfully")
                except Exception as e:
                    logger.error(f"❌ Error initializing database connector: {e}, using RAG fallback")
                    return self._ask_with_rag(question)
            
            # Use SQL query để trả lời chính xác
            logger.info("✅ Both SQL generator and DB connector available, executing SQL query...")
            return self._ask_with_sql(question, classification)
        
        elif query_type == "hybrid":
            # TODO: Implement hybrid handler (SQL + RAG)
            logger.warning("⚠️  Hybrid queries not yet implemented, using SQL for now")
            if self.sql_generator is not None and self.db_connector is not None:
                return self._ask_with_sql(question, classification)
            else:
                return self._ask_with_rag(question)
        
        else:  # semantic (default)
            # Use RAG như cũ
            return self._ask_with_rag(question)
    
    def _ask_with_rag(self, question: str) -> Dict:
        """
        Ask question với RAG (Retrieval + Generation)
        Helper method để tách logic RAG
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and sources
        """
        # Extract location from question (optional optimization)
        # If location found, we could use custom retriever with filter
        # For now, use standard QA chain (semantic search handles location well)
        extracted_keywords = self._extract_keywords_from_query(
            question,
            use_llm=self.use_llm_for_extraction
        )
        location = extracted_keywords.get("location")
        
        if location:
            logger.debug(f"Location detected in question: {location} (using semantic search)")
            # Note: RetrievalQA chain uses semantic search which handles location well
            # For strict filtering, would need custom retriever (future enhancement)
        
        # Get answer with RAG (Layer 3: Generation Pipeline)
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
    
    def _ask_with_sql(self, question: str, classification: Dict = None) -> Dict:
        """
        Ask question với SQL query (cho statistical queries)
        
        Args:
            question: User question
            classification: Classification result từ query router
            
        Returns:
            Dictionary with answer and sources
        """
        if self.sql_generator is None:
            raise ValueError("SQL generator not initialized")
        
        if self.db_connector is None:
            # Initialize database connector if not already done
            if DatabaseConnector is None:
                raise ValueError("DatabaseConnector not available. Cannot execute SQL queries.")
            self.db_connector = DatabaseConnector()
            if not self.db_connector.test_connection():
                raise ConnectionError("Failed to connect to database")
        
        logger.info(f"🔍 Generating SQL query for: '{question}'")
        
        # Extract keywords để pass vào SQL generator
        extracted_keywords = self._extract_keywords_from_query(
            question,
            use_llm=self.use_llm_for_extraction
        )
        
        # Generate SQL query
        sql_info = self.sql_generator.generate_sql(question, extracted_keywords)
        sql = sql_info["sql"]
        query_type = sql_info["query_type"]
        
        logger.info(f"📊 Generated SQL ({query_type}): {sql}")
        
        # Execute SQL query
        try:
            from sqlalchemy import text
            
            with self.db_connector.engine.connect() as conn:
                result = conn.execute(text(sql))
                row = result.fetchone()
                
                if row is None:
                    count = 0
                else:
                    # Get result based on query type
                    if query_type == "count":
                        count = row[0] if row[0] is not None else 0
                    elif query_type == "avg":
                        avg_price = float(row[0]) if row[0] is not None else 0
                        # Format answer for average price
                        answer = f"Giá trung bình của khách sạn"
                        if extracted_keywords.get("location"):
                            answer += f" ở {extracted_keywords['location']}"
                        if extracted_keywords.get("rank"):
                            answer += f" {extracted_keywords['rank']} sao"
                        answer += f" là {avg_price:,.0f} VND"
                        
                        return {
                            "question": question,
                            "answer": answer,
                            "sources": [],
                            "query_type": "statistical",
                            "sql": sql
                        }
                    elif query_type == "max":
                        max_price = float(row[0]) if row[0] is not None else 0
                        answer = f"Giá cao nhất của khách sạn"
                        if extracted_keywords.get("location"):
                            answer += f" ở {extracted_keywords['location']}"
                        answer += f" là {max_price:,.0f} VND"
                        
                        return {
                            "question": question,
                            "answer": answer,
                            "sources": [],
                            "query_type": "statistical",
                            "sql": sql
                        }
                    elif query_type == "min":
                        min_price = float(row[0]) if row[0] is not None else 0
                        answer = f"Giá thấp nhất của khách sạn"
                        if extracted_keywords.get("location"):
                            answer += f" ở {extracted_keywords['location']}"
                        answer += f" là {min_price:,.0f} VND"
                        
                        return {
                            "question": question,
                            "answer": answer,
                            "sources": [],
                            "query_type": "statistical",
                            "sql": sql
                        }
                    elif query_type == "exists":
                        exists = bool(row[0])
                        location = extracted_keywords.get("location", "")
                        answer = f"{'Có' if exists else 'Không có'} khách sạn"
                        if location:
                            answer += f" ở {location}"
                        answer += " trong hệ thống."
                        
                        return {
                            "question": question,
                            "answer": answer,
                            "sources": [],
                            "query_type": "statistical",
                            "sql": sql
                        }
                    else:
                        count = row[0] if row[0] is not None else 0
                
                # Format answer for count query
                answer = f"Có {count} khách sạn"
                if extracted_keywords.get("location"):
                    answer += f" trong khu vực {extracted_keywords['location']}"
                if extracted_keywords.get("rank"):
                    answer += f" {extracted_keywords['rank']} sao"
                answer += " trong hệ thống."
                
                logger.info(f"✅ SQL query executed successfully: {count} hotels found")
                
                return {
                    "question": question,
                    "answer": answer,
                    "sources": [],
                    "query_type": "statistical",
                    "sql": sql,
                    "count": count
                }
                
        except Exception as e:
            logger.error(f"❌ Error executing SQL query: {e}")
            # Fallback to RAG
            logger.warning("⚠️  Falling back to RAG due to SQL error")
            return self._ask_with_rag(question)
    
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

QUY TẮC BẮT BUỘC VỀ TÊN KHÁCH SẠN - TUYỆT ĐỐI KHÔNG ĐƯỢC VI PHẠM:
❌ NGHIÊM CẤM sử dụng tên thương hiệu (brand_name) như: "Meliá Hotels International", "Accor", "InterContinental Hotels Group"
✅ BẮT BUỘC sử dụng TÊN KHÁCH SẠN CỤ THỂ từ trường "Tên khách sạn:" hoặc "Khách sạn" ở ĐẦU mỗi block trong context

VÍ DỤ CÁCH TRẢ LỜI ĐÚNG VÀ SAI:
✅ ĐÚNG: "Grand Tourane Hotel" (lấy từ "Tên khách sạn: Grand Tourane Hotel")
✅ ĐÚNG: "Meliá Vinpearl Riverfront Đà Nẵng" (lấy từ "Tên khách sạn: Meliá Vinpearl Riverfront Đà Nẵng")
✅ ĐÚNG: "Pullman Danang Beach Resort" (lấy từ "Tên khách sạn: Pullman Danang Beach Resort")
❌ SAI: "Meliá Đà Nẵng – Xuân Thiều" (sai vì đây KHÔNG phải tên khách sạn trong database)
❌ SAI: "Accor Hotel tại Đà Nẵng" (sai vì đây là brand, không phải tên khách sạn cụ thể)
❌ SAI: "InterContinental Đà Nẵng" (sai nếu tên đầy đủ là "InterContinental Danang Sun Peninsula Resort")
❌ SAI: "Meliá Hotels International" (sai vì đây là brand name, phải dùng tên khách sạn cụ thể)

CÁCH XÁC ĐỊNH TÊN KHÁCH SẠN ĐÚNG (BẮT BUỘC):
1. Tìm dòng "Tên khách sạn:" hoặc "Khách sạn" ở ĐẦU TIÊN trong mỗi block thông tin của context
2. Sử dụng CHÍNH XÁC, NGUYÊN VĂN tên đó, KHÔNG RÚT GỌN, KHÔNG thay bằng brand name, KHÔNG tự bịa tên
3. Dòng "Thương hiệu:" CHỈ để tham khảo nhóm khách sạn, TUYỆT ĐỐI KHÔNG dùng để đặt tên khách sạn trong câu trả lời

Nếu câu hỏi liên quan đến khách sạn và có thông tin phù hợp, hãy trả lời chi tiết, tự nhiên bằng tiếng Việt. BẮT BUỘC nêu TÊN KHÁCH SẠN CỤ THỂ (lấy CHÍNH XÁC từ "Tên khách sạn:" trong context), giá, đánh giá (sao), địa điểm, và các tiện ích nổi bật. So sánh các khách sạn nếu có nhiều lựa chọn.

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

