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

from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.embeddings import Embeddings
from qdrant_client import QdrantClient

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
        """Embed documents (có thể cache sau)"""
        return self.embeddings.embed_documents(texts)
    
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
                 collection_name="hotels"):
        """
        Initialize RAG System
        
        Args:
            ollama_url: Ollama server URL
            qdrant_url: Qdrant server URL
            embedding_model: Embedding model name
            llm_model: LLM model name
            collection_name: Qdrant collection name
        """
        self.ollama_url = ollama_url
        self.qdrant_url = qdrant_url
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.collection_name = collection_name
        
        # Initialize embeddings với cache wrapper
        logger.info(f"Initializing embeddings: {embedding_model}")
        base_embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_url
        )
        # Wrap với cache để tối ưu performance
        self.embeddings = CachedOllamaEmbeddings(base_embeddings, cache_enabled=True)
        
        # Initialize LLM
        logger.info(f"Initializing LLM: {llm_model}")
        # Lower temperature for more consistent Vietnamese responses
        self.llm = Ollama(
            model=llm_model,
            base_url=ollama_url,
            temperature=0.3  # Lower temperature for more focused responses
        )
        
        # Vector store (will be initialized after indexing)
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
    
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
        
        # Store in Qdrant with batch processing to avoid timeout
        logger.info(f"Storing {len(documents)} documents in Qdrant collection: {self.collection_name}")
        
        # Create collection first if not exists
        from qdrant_client.models import Distance, VectorParams
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
                logger.info(f"Deleting existing collection: {self.collection_name}")
                client.delete_collection(collection_name=self.collection_name)
                # Refresh collection list after deletion
                collections = client.get_collections()
                collection_names = [col.name for col in collections.collections]
            
            # Create collection if it doesn't exist
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection '{self.collection_name}' with vector size {vector_size}")
                
                # Tối ưu HNSW index cho performance tốt hơn
                # m=16: Số connections mỗi node (16-32 là tốt, cân bằng giữa speed và accuracy)
                # ef_construct=200: Số candidates khi build index (tăng cho accuracy tốt hơn)
                # full_scan_threshold=10: Minimum value (Qdrant requires >= 10)
                #   Với dataset nhỏ (~24 hotels), HNSW sẽ được dùng vì > 10
                from qdrant_client.models import HnswConfigDiff
                hnsw_config = HnswConfigDiff(
                    m=16,              # Số connections mỗi node (16-32 là tốt)
                    ef_construct=200,  # Số candidates khi build index (tăng cho accuracy)
                    full_scan_threshold=10  # Minimum value (Qdrant requires >= 10)
                )
                
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE,
                        hnsw_config=hnsw_config  # Thêm HNSW config để tối ưu search
                    )
                )
                logger.info(f"✅ Collection '{self.collection_name}' created successfully with optimized HNSW index")
                logger.info(f"   HNSW Config: m=16, ef_construct=200, full_scan_threshold=10")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
                # Verify HNSW config
                try:
                    config_info = self.verify_hnsw_config()
                    if config_info.get("hnsw_configured") and config_info.get("m") == 16 and config_info.get("ef_construct") == 200:
                        logger.info(f"✅ Collection has optimized HNSW config (m={config_info['m']}, ef_construct={config_info['ef_construct']})")
                    else:
                        logger.warning(f"⚠️  Collection may not have optimized HNSW config")
                        logger.warning(f"   Current: m={config_info.get('m')}, ef_construct={config_info.get('ef_construct')}")
                        logger.warning(f"   Expected: m=16, ef_construct=200")
                        logger.warning(f"   To optimize: Set recreate_collection=True or call optimize_collection()")
                except Exception as e:
                    logger.warning(f"Could not verify HNSW config: {e}")
            
            # Initialize vectorstore
            self.vectorstore = Qdrant(
                client=client,
                collection_name=self.collection_name,
                embeddings=self.embeddings
            )
            
            # Add documents in small batches to avoid timeout
            batch_size = 1  # Process one hotel at a time
            import time
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1} ({len(batch)} documents)")
                
                # Retry logic for Ollama timeout
                max_retries = 3
                retry_delay = 2  # seconds
                
                for retry in range(max_retries):
                    try:
                        self.vectorstore.add_texts(
                            texts=[doc.page_content for doc in batch],
                            metadatas=[doc.metadata for doc in batch],
                            ids=[doc.metadata.get("hotel_id", i+j) for j, doc in enumerate(batch)]
                        )
                        break  # Success, exit retry loop
                    except Exception as e:
                        if retry < max_retries - 1:
                            logger.warning(f"Error processing batch {i//batch_size + 1} (attempt {retry+1}/{max_retries}): {e}")
                            logger.info(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"Error processing batch {i//batch_size + 1} after {max_retries} attempts: {e}")
                            raise
                
                # Small delay between batches to avoid overwhelming Ollama
                if i < len(documents) - batch_size:
                    time.sleep(0.5)
            
            logger.info(f"Successfully stored {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error storing documents: {e}")
            raise
        
        # Create retriever from vectorstore
        # Giảm k từ 5 xuống 3 để tối ưu performance (có thể config sau)
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 3}  # Top 3 results (giảm từ 5 xuống 3 để nhanh hơn)
        )
        
        # Create QA chain
        prompt_template = """
Bạn là trợ lý tư vấn khách sạn chuyên nghiệp tại Đà Nẵng. QUAN TRỌNG: Bạn PHẢI trả lời HOÀN TOÀN bằng tiếng Việt, KHÔNG được sử dụng tiếng Anh trong câu trả lời.

Dựa trên thông tin sau về các khách sạn, hãy trả lời câu hỏi của người dùng một cách tự nhiên và hữu ích BẰNG TIẾNG VIỆT.

Context:
{context}

Câu hỏi: {question}

YÊU CẦU TRẢ LỜI (QUAN TRỌNG):
1. TRẢ LỜI HOÀN TOÀN BẰNG TIẾNG VIỆT - KHÔNG SỬ DỤNG TIẾNG ANH
2. Trả lời tự nhiên, dễ hiểu, chuyên nghiệp
3. Nêu tên khách sạn, địa chỉ, giá nếu có trong context
4. Nếu không có thông tin phù hợp, hãy nói rõ "Tôi không tìm thấy khách sạn phù hợp với yêu cầu của bạn."
5. Nếu có nhiều khách sạn, hãy liệt kê top 3-5 khách sạn phù hợp nhất với thông tin chi tiết

LƯU Ý: Chỉ trả lời bằng tiếng Việt, không dịch ra tiếng Anh, không sử dụng từ tiếng Anh.

Trả lời (bằng tiếng Việt):
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        logger.info("RAG system initialized successfully!")
    
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
            
            # Search with location filter
            search_results = client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k * 2,  # Get more results to filter
                query_filter=Filter(
                    must=[
                        FieldCondition(key="area_name", match=MatchValue(value=area_name))
                    ]
                )
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
        
        # No location filter - use regular semantic search
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=top_k * 2  # Get more results to filter if needed
        )
        
        # Format results with optional post-filtering
        hotels = []
        for doc, score in results:
            hotel_area = doc.metadata.get("area_name", "")
            
            # If we have a location filter but it wasn't applied in search, post-filter here
            if area_name and hotel_area and hotel_area.strip() != area_name:
                continue  # Skip hotels not in the requested area
            
            hotels.append({
                "hotel_id": doc.metadata.get("hotel_id"),
                "hotel_name": doc.metadata.get("hotel_name", ""),
                "hotel_rank": doc.metadata.get("hotel_rank"),
                "hotel_price_average": doc.metadata.get("hotel_price_average"),
                "area_name": doc.metadata.get("area_name", ""),
                "brand_name": doc.metadata.get("brand_name", ""),
                "price_category": doc.metadata.get("price_category", ""),
                "similarity_score": float(score),
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
            response["sources"].append({
                "hotel_id": doc.metadata.get("hotel_id"),
                "hotel_name": doc.metadata.get("hotel_name", ""),
                "hotel_rank": doc.metadata.get("hotel_rank"),
                "hotel_price_average": doc.metadata.get("hotel_price_average"),
                "area_name": doc.metadata.get("area_name", ""),
                "text_preview": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
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
        # Giảm k từ 5 xuống 3 để tối ưu performance
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 3}  # Top 3 results (giảm từ 5 xuống 3 để nhanh hơn)
        )
        
        # Create QA chain
        prompt_template = """
Bạn là trợ lý tư vấn khách sạn chuyên nghiệp tại Đà Nẵng. QUAN TRỌNG: Bạn PHẢI trả lời HOÀN TOÀN bằng tiếng Việt, KHÔNG được sử dụng tiếng Anh trong câu trả lời.

Dựa trên thông tin sau về các khách sạn, hãy trả lời câu hỏi của người dùng một cách tự nhiên và hữu ích BẰNG TIẾNG VIỆT.

Context:
{context}

Câu hỏi: {question}

YÊU CẦU TRẢ LỜI (QUAN TRỌNG):
1. TRẢ LỜI HOÀN TOÀN BẰNG TIẾNG VIỆT - KHÔNG SỬ DỤNG TIẾNG ANH
2. Trả lời tự nhiên, dễ hiểu, chuyên nghiệp
3. Nêu tên khách sạn, địa chỉ, giá nếu có trong context
4. Nếu không có thông tin phù hợp, hãy nói rõ "Tôi không tìm thấy khách sạn phù hợp với yêu cầu của bạn."
5. Nếu có nhiều khách sạn, hãy liệt kê top 3-5 khách sạn phù hợp nhất với thông tin chi tiết

LƯU Ý: Chỉ trả lời bằng tiếng Việt, không dịch ra tiếng Anh, không sử dụng từ tiếng Anh.

Trả lời (bằng tiếng Việt):
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
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

