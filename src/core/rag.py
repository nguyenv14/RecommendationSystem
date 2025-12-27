"""
RAG Service
Unified RAG (Retrieval-Augmented Generation) service
Sử dụng LangChain RetrievalQA chain giống simple_rag_system.py
"""

from typing import List, Dict, Optional, Any
from .embeddings import EmbeddingService
from .vectorstore import VectorStoreService
from .retriever import RetrieverService
from .generator import GeneratorService
from .query_preprocessor import QueryPreprocessor
from .response_cache import ResponseCache
from .reranker import Reranker
from ..shared import get_logger
from ..config import get_settings

# Import QueryRouter and SQLQueryGenerator
try:
    from rag.core.query_router import QueryRouter
    from rag.core.sql_query_generator import SQLQueryGenerator
except ImportError:
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'rag'))
        from core.query_router import QueryRouter
        from core.sql_query_generator import SQLQueryGenerator
    except ImportError:
        logger = get_logger(__name__)
        logger.warning("Could not import QueryRouter or SQLQueryGenerator")
        QueryRouter = None
        SQLQueryGenerator = None

# Import DatabaseConnector for fallback room/type_room retrieval
try:
    from rag.data.connector import DatabaseConnector
    from rag.data.normalizer import HotelDataNormalizer
except ImportError:
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'rag'))
        from data.connector import DatabaseConnector
        from data.normalizer import HotelDataNormalizer
    except ImportError:
        logger.warning("Could not import DatabaseConnector or HotelDataNormalizer for room retrieval")
        DatabaseConnector = None
        HotelDataNormalizer = None

logger = get_logger(__name__)


class RAGService:
    """
    Unified RAG service với optimized flow
    Flow: Response Cache → Query Preprocessing → Embedding Cache → Batch Embed → 
          Hybrid Search → Re-rank → Build Context (token limit) → Generate → Cache Response
    """
    
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vectorstore_service: Optional[VectorStoreService] = None,
        retriever_service: Optional[RetrieverService] = None,
        generator_service: Optional[GeneratorService] = None,
        collection_name: Optional[str] = None,
        response_cache_ttl: int = 3600
    ):
        """
        Initialize RAG service
        
        Args:
            embedding_service: Optional embedding service (creates if None)
            vectorstore_service: Optional vectorstore service (creates if None)
            retriever_service: Optional retriever service (creates if None)
            generator_service: Optional generator service (creates if None)
            collection_name: Collection to use for RAG
            response_cache_ttl: Response cache TTL in seconds (default: 1 hour)
        """
        settings = get_settings()
        
        # Initialize services if not provided
        if embedding_service is None:
            embedding_service = EmbeddingService(
                provider="ollama",
                model_name=settings.EMBEDDING_MODEL,
                ollama_url=settings.OLLAMA_URL,
                cache_enabled=settings.EMBEDDING_CACHE_ENABLED
            )
        
        if vectorstore_service is None:
            vectorstore_service = VectorStoreService(
                url=settings.QDRANT_URL,
                default_collection=collection_name or settings.RAG_COLLECTION_HOTELS
            )
        
        if retriever_service is None:
            retriever_service = RetrieverService(
                embedding_service=embedding_service,
                vectorstore_service=vectorstore_service,
                default_collection=collection_name or settings.RAG_COLLECTION_HOTELS,
                default_top_k=settings.RAG_TOP_K
            )
        
        if generator_service is None:
            logger.info(
                f"🔧 Creating GeneratorService with "
                f"LLM_PROVIDER={settings.LLM_PROVIDER}, "
                f"LM_STUDIO_URL={settings.LM_STUDIO_URL}"
            )
            # Truyền thêm cấu hình OpenRouter (nếu provider=openrouter thì sẽ dùng)
            generator_service = GeneratorService(
                provider=settings.LLM_PROVIDER,
                model_name=settings.LLM_MODEL,
                ollama_url=settings.OLLAMA_URL,
                lm_studio_url=settings.LM_STUDIO_URL,
                openrouter_api_key=settings.OPENROUTER_API_KEY,
                openrouter_model=settings.OPENROUTER_MODEL,
                openrouter_base_url=settings.OPENROUTER_BASE_URL,
            )
        
        self.embedding = embedding_service
        self.vectorstore_service = vectorstore_service 
        self.retriever_service = retriever_service
        self.generator = generator_service
        self.collection_name = collection_name or settings.RAG_COLLECTION_HOTELS
        
        # Initialize optimizations
        self.query_preprocessor = QueryPreprocessor()
        self.response_cache = ResponseCache(ttl=response_cache_ttl)
        
        # Initialize re-ranker for better retrieval quality
        self.reranker = Reranker(enable_reranking=True)
        
        # Initialize query router and SQL generator (for statistical queries)
        self.query_router = None
        self.sql_generator = None
        self.db_connector = None
        
        if QueryRouter is not None:
            try:
                # Get LLM from generator service for query router
                llm_for_router = generator_service.llm if hasattr(generator_service, 'llm') else None
                self.query_router = QueryRouter(use_llm=True, llm=llm_for_router)
                logger.info("✅ Query Router initialized in RAGService")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize QueryRouter: {e}")
        
        if SQLQueryGenerator is not None:
            try:
                # Với các câu hỏi thống kê đơn giản (đếm, trung bình, max/min),
                # rule-based SQL đã đủ chính xác và **nhanh hơn rất nhiều** so với gọi LLM.
                # Vì lý do hiệu năng, mặc định TẮT LLM cho SQL generator.
                # Nếu sau này cần các câu SQL phức tạp hơn, có thể đổi use_llm=True.
                llm_for_sql = generator_service.llm if hasattr(generator_service, 'llm') else None
                self.sql_generator = SQLQueryGenerator(use_llm=True, llm=llm_for_sql)
                logger.info("✅ SQL Query Generator initialized in RAGService")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize SQLQueryGenerator: {e}")
        
        logger.info(f"✅ RAGService initialized (collection={self.collection_name})")
    
    
    def ask(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        prompt_template: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Ask a question and get answer (optimized RAG flow)
        
        Flow:
        1. Check Response Cache → Hit? → Return (0.1s)
        2. Preprocess Query (normalize, expand synonyms)
        3. Check Embedding Cache → Hit? → Use cached
        4. Batch Embed Query (nếu nhiều queries)
        5. Hybrid Search (semantic + keyword) - TODO: implement
        6. Re-rank Results (cross-encoder) - TODO: implement
        7. Build Context (với token limit, sort by relevance)
        8. Generate Answer (optimized prompt)
        9. Cache Response
        
        Args:
            question: User question
            top_k: Number of documents to retrieve (default: 5)
            filters: Optional filters for retrieval
            prompt_template: Optional custom prompt template
            use_cache: Whether to use response cache
            
        Returns:
            Dict with question, answer, sources
        """
        logger.info(f"RAG question: '{question[:50]}...'")
        
        # Step 0: Classify query and route to appropriate handler
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
            
            # Route to SQL handler if statistical
            if query_type == "statistical":
                logger.info("🔍 Routing to SQL handler...")
                if self.sql_generator is not None:
                    return self._ask_with_sql(question, classification, use_cache=use_cache)
                else:
                    logger.warning("⚠️  SQL generator not available, using RAG fallback")
            elif query_type == "hybrid":
                # Hybrid queries: Ưu tiên semantic RAG (vì thường là tìm kiếm + filter)
                # Chỉ dùng SQL nếu thực sự cần đếm/thống kê
                logger.info("🔍 Hybrid query detected, using semantic RAG (better for search queries)")
                # Continue with normal RAG flow below (don't route to SQL)
        
        # Step 1: Check Response Cache (for semantic queries)
        if use_cache:
            cached_response = self.response_cache.get(question)
            if cached_response is not None:
                logger.info("✅ Response cache hit")
                return cached_response
        
        try:
            # Step 2: Preprocess Query
            processed_query = self.query_preprocessor.preprocess(question)
            logger.debug(f"Processed query: '{processed_query}'")
            
            # Step 3-4: Embedding (with cache check) + Vector Search
            if top_k is None:
                top_k = 5  # Default k=5
            
            # Use Qdrant grouping to ensure diverse hotels (1 chunk per hotel)
            # This is more efficient than manual deduplication
            # Note: Embedding cache is handled inside RetrieverService.retrieve()
            # which calls EmbeddingService.embed_query() which checks cache
            documents = self.retriever_service.retrieve(
                query=processed_query,  # Use processed query
                collection_name=self.collection_name,
                top_k=top_k,  # Number of unique hotels to return
                filters=filters,
                use_grouping=True,  # Use Qdrant grouping to ensure diversity
                group_by="hotel_id"  # Group by hotel_id to get diverse hotels
            )
            
            logger.info(f"Retrieved {len(documents)} documents from {len(documents)} unique hotels (using Qdrant grouping)")
            
            # Check if question is about hotel rooms and extract hotel_id from search results
            hotel_id = self._extract_hotel_id_from_documents(documents, question)
            hotel_rooms_docs = []
            hotel_type_rooms_docs = []
            
            if hotel_id:
                logger.info(f"🔍 Detected hotel_id={hotel_id} in question, fetching rooms and type_rooms...")
                # Get rooms for this hotel
                hotel_rooms_docs = self._get_hotel_rooms(hotel_id, top_k=20)
                # Get type_rooms used by this hotel
                hotel_type_rooms_docs = self._get_hotel_type_rooms(hotel_id, top_k=10)
                logger.info(f"   Found {len(hotel_rooms_docs)} rooms and {len(hotel_type_rooms_docs)} type_rooms")
            
            # Merge hotel info with rooms and type_rooms if available
            if hotel_rooms_docs or hotel_type_rooms_docs:
                # Add rooms and type_rooms to documents for context
                documents.extend(hotel_rooms_docs)
                documents.extend(hotel_type_rooms_docs)
                # Sort by score (rooms/type_rooms might not have scores, put them after)
                documents = sorted(documents, key=lambda x: x.get('score', -1), reverse=True)
                logger.info(f"Total documents after adding rooms: {len(documents)}")
            
            if not documents:
                logger.warning("No documents retrieved for question")
                result = {
                    "question": question,
                    "answer": "Xin lỗi, tôi không tìm thấy thông tin phù hợp trong hệ thống cho câu hỏi này.",
                    "sources": [],
                    "num_sources": 0
                }
                # Cache negative result too (shorter TTL could be used)
                if use_cache:
                    self.response_cache.set(question, result)
                return result
            
            logger.info(f"Retrieved {len(documents)} documents (expected: {top_k})")
            
            # Step 5: Hybrid Search - TODO: implement
            # For now, just use semantic search results
            
            # Step 6: Re-rank Results using Cross-Encoder for better precision
            if len(documents) > 0 and self.reranker.is_available():
                logger.info(f"Re-ranking {len(documents)} documents with cross-encoder")
                documents = self.reranker.rerank(
                    query=question,
                    documents=documents,
                    top_k=top_k * 2  # Re-rank more, then take top_k in context building
                )
                logger.info(f"✅ Re-ranked documents (top score: {documents[0].get('rerank_score', 0):.4f})")
            else:
                if not self.reranker.is_available():
                    logger.debug("Re-ranker not available, using original ranking")
                # Keep original ranking if reranker not available
            
            # Step 7-8: Build Context (với token limit) + Generate Answer
            result = self.generator.generate_from_documents(
                query=question,  # Use original question for generation
                documents=documents,
                prompt_template=prompt_template,
                max_context_tokens=4000  # Token limit
            )
            
            # Step 9: Cache Response
            if use_cache:
                self.response_cache.set(question, result)
            
            logger.info(f"✅ RAG answer generated (sources: {len(result.get('sources', []))})")
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG flow: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "question": question,
                "answer": f"Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi: {str(e)}",
                "sources": [],
                "num_sources": 0
            }
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents (retrieval only, no generation)
        
        Args:
            query: Search query
            top_k: Number of results
            filters: Optional filters
            
        Returns:
            List of relevant documents
        """
        logger.info(f"RAG search: '{query[:50]}...'")
        
        # Use retriever_service for search (not LangChain retriever)
        documents = self.retriever_service.retrieve(
            query=query,
            collection_name=self.collection_name,
            top_k=top_k,
            filters=filters
        )
        
        return documents
    
    def _ask_with_sql(self, question: str, classification: Dict = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Ask question với SQL query (cho statistical queries)
        
        Args:
            question: User question
            classification: Query classification result
            use_cache: Whether to use response cache
            question: User question
            classification: Classification result từ query router
            
        Returns:
            Dictionary with answer and sources
        """
        if self.sql_generator is None:
            logger.error("SQL generator not initialized")
            return {
                "question": question,
                "answer": "Xin lỗi, hệ thống SQL chưa sẵn sàng.",
                "sources": [],
                "num_sources": 0
            }
        
        logger.info(f"🔍 Generating SQL query for: '{question}'")
        
        # Initialize database connector if needed
        if self.db_connector is None:
            try:
                from rag.data.connector import DatabaseConnector
                self.db_connector = DatabaseConnector()
                if not self.db_connector.test_connection():
                    logger.error("❌ Database connection failed")
                    return {
                        "question": question,
                        "answer": "Xin lỗi, không thể kết nối database.",
                        "sources": [],
                        "num_sources": 0
                    }
                logger.info("✅ Database connector initialized")
            except Exception as e:
                logger.error(f"❌ Error initializing database connector: {e}")
                return {
                    "question": question,
                    "answer": "Xin lỗi, không thể kết nối database.",
                    "sources": [],
                    "num_sources": 0
                }
        
        # Extract keywords (simple extraction for SQL)
        question_lower = question.lower()
        location = None
        rank = None
        
        # Extract location
        locations = {
            "ngũ hành sơn": "Ngũ Hành Sơn", "ngu hanh son": "Ngũ Hành Sơn",
            "sơn trà": "Sơn Trà", "son tra": "Sơn Trà",
            "cẩm lệ": "Cẩm Lệ", "cam le": "Cẩm Lệ",
            "hải châu": "Hải Châu", "hai chau": "Hải Châu",
        }
        for key, value in locations.items():
            if key in question_lower:
                location = value
                break
        
        # Extract rank
        if "5 sao" in question_lower or "năm sao" in question_lower:
            rank = 5
        elif "4 sao" in question_lower or "bốn sao" in question_lower:
            rank = 4
        elif "3 sao" in question_lower or "ba sao" in question_lower:
            rank = 3
        
        extracted_info = {"location": location, "rank": rank}
        
        # Generate SQL query
        sql_info = self.sql_generator.generate_sql(question, extracted_info)
        sql = sql_info["sql"]
        query_type = sql_info["query_type"]
        
        logger.info(f"📊 Generated SQL ({query_type}): {sql}")
        
        # Validate SQL query - check for invalid columns
        invalid_columns = ["room_type", "room_name", "room_price"]  # Common invalid columns
        sql_lower = sql.lower()
        for col in invalid_columns:
            if col in sql_lower:
                logger.warning(f"⚠️  SQL query contains invalid column '{col}', falling back to RAG")
                return self._ask_with_rag_fallback(question, use_cache)
        
        # Execute SQL query
        try:
            from sqlalchemy import text
            
            with self.db_connector.engine.connect() as conn:
                result = conn.execute(text(sql))
                row = result.fetchone()
                
                if row is None:
                    count = 0
                else:
                    if query_type == "count":
                        count = row[0] if row[0] is not None else 0
                    elif query_type == "avg":
                        avg_price = float(row[0]) if row[0] is not None else 0
                        answer = f"Giá trung bình của khách sạn"
                        if location:
                            answer += f" ở {location}"
                        if rank:
                            answer += f" {rank} sao"
                        answer += f" là {avg_price:,.0f} VND"
                        
                        return {
                            "question": question,
                            "answer": answer,
                            "sources": [],
                            "num_sources": 0,
                            "query_type": "statistical"
                        }
                    else:
                        count = row[0] if row[0] is not None else 0
                
                # Format answer for count query
                answer = f"Có {count} khách sạn"
                if location:
                    answer += f" trong khu vực {location}"
                if rank:
                    answer += f" {rank} sao"
                answer += " trong hệ thống."
                
                logger.info(f"✅ SQL query executed successfully: {count} hotels found")
                
                return {
                    "question": question,
                    "answer": answer,
                    "sources": [],
                    "num_sources": 0,
                    "query_type": "statistical",
                    "count": count
                }
                
        except Exception as e:
            logger.error(f"❌ Error executing SQL query: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Fallback to RAG
            logger.warning("⚠️  Falling back to RAG due to SQL error")
            # Continue with normal RAG flow below
            pass
        
        # If SQL fails, fall through to normal RAG flow
        return self._ask_with_rag_fallback(question, use_cache)
    
    def _ask_with_rag_fallback(self, question: str, use_cache: bool = True) -> Dict[str, Any]:
        """Fallback to normal RAG flow"""
        # This is the original ask() logic without query routing
        # Step 1: Check Response Cache
        if use_cache:
            cached_response = self.response_cache.get(question)
            if cached_response is not None:
                logger.info("✅ Response cache hit")
                return cached_response
        
        try:
            # Step 2: Preprocess Query
            processed_query = self.query_preprocessor.preprocess(question)
            logger.debug(f"Processed query: '{processed_query}'")
            
            # Step 3-4: Embedding + Vector Search
            documents = self.retriever_service.retrieve(
                query=processed_query,
                collection_name=self.collection_name,
                top_k=5,
                filters=None
            )
            
            if not documents:
                return {
                    "question": question,
                    "answer": "Xin lỗi, tôi không tìm thấy thông tin phù hợp trong hệ thống cho câu hỏi này.",
                    "sources": [],
                    "num_sources": 0
                }
            
            # Generate answer
            result = self.generator.generate_from_documents(
                query=question,
                documents=documents,
                prompt_template=None,
                max_context_tokens=4000
            )
            
            if use_cache:
                self.response_cache.set(question, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG flow: {e}")
            return {
                "question": question,
                "answer": f"Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi: {str(e)}",
                "sources": [],
                "num_sources": 0
            }
    
    def index_documents(
        self,
        documents: List[Dict[str, Any]],
        id_field: str = "id",
        text_field: str = "text",
        metadata_fields: Optional[List[str]] = None,
        recreate_collection: bool = False
    ) -> bool:
        """
        Index documents into vector store
        
        Args:
            documents: List of documents to index
            id_field: Field name for document ID
            text_field: Field name for text content
            metadata_fields: Additional fields to store as metadata
            recreate_collection: Recreate collection if exists
            
        Returns:
            True if successful
        """
        logger.info(f"Indexing {len(documents)} documents to {self.collection_name}")
        
        try:
            # Get vector size
            vector_size = self.embedding.get_vector_size()
            
            # Create collection if needed
            if recreate_collection or not self.vectorstore_service.collection_exists(self.collection_name):
                self.vectorstore_service.create_collection(
                    collection_name=self.collection_name,
                    vector_size=vector_size,
                    recreate=recreate_collection
                )
            
            # Prepare texts for batch embedding
            texts = []
            doc_metadata = []
            
            for doc in documents:
                doc_id = doc.get(id_field)
                text = doc.get(text_field, "")
                
                if not doc_id or not text:
                    logger.warning(f"Skipping document without ID or text: {doc}")
                    continue
                
                texts.append(text)
                doc_metadata.append({
                    'id': doc_id,
                    'doc': doc,
                    'text_field': text_field,
                    'metadata_fields': metadata_fields
                })
            
            # Batch embed all texts (optimized)
            logger.info(f"Batch embedding {len(texts)} documents...")
            vectors = self.embedding.embed_documents(texts, batch_size=32, show_progress=True)
            
            # Prepare points
            from qdrant_client.models import PointStruct
            points = []
            
            for i, (vector, meta) in enumerate(zip(vectors, doc_metadata)):
                doc_id = meta['id']
                doc = meta['doc']
                text_field = meta['text_field']
                metadata_fields = meta['metadata_fields']
                
                # Prepare payload
                payload = {text_field: texts[i]}
                
                # Add metadata fields
                if metadata_fields:
                    for field in metadata_fields:
                        if field in doc:
                            payload[field] = doc[field]
                else:
                    # Add all fields
                    payload.update(doc)
                
                # Create point
                point = PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload
                )
                points.append(point)
            
            # Upsert points
            success = self.vectorstore_service.upsert_points(
                collection_name=self.collection_name,
                points=points
            )
            
            if success:
                logger.info(f"✅ Indexed {len(points)} documents")
            
            return success
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG service statistics
        
        Returns:
            Statistics dict
        """
        try:
            collection_info = self.vectorstore_service.get_collection_info(self.collection_name)
            cache_stats = self.embedding.get_cache_stats()
            
            return {
                "collection": {
                    "name": self.collection_name,
                    "points_count": collection_info.points_count if collection_info else 0,
                    "vector_size": collection_info.config.params.vectors.size if collection_info else 0
                },
                "embedding": cache_stats,
                "retriever": {
                    "default_top_k": self.retriever_service.default_top_k
                },
                "query_preprocessor": {
                    "enabled": True
                },
                "response_cache": self.response_cache.get_stats(),
                "generator": {
                    "provider": self.generator.provider,
                    "model": self.generator.model_name,
                    "temperature": self.generator.temperature,
                    "max_tokens": 2048  # max_tokens for LM Studio
                }
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def _extract_hotel_id_from_result(self, result: Dict[str, Any]) -> Optional[int]:
        """
        Extract hotel_id from a single result (can be in payload or derived from id)
        
        Args:
            result: Result dict with 'id' and 'payload' fields
            
        Returns:
            hotel_id if found, None otherwise
        """
        payload = result.get('payload', {})
        # Try to get hotel_id from payload first
        hotel_id = payload.get('hotel_id')
        if hotel_id is not None:
            try:
                return int(hotel_id)
            except (ValueError, TypeError):
                pass
        
        # If not in payload, try to parse from id (if id is chunk_id format: hotel_id * 1000000 + chunk_index)
        result_id = result.get('id')
        if result_id is not None:
            try:
                result_id_int = int(result_id)
                # If id is very large, it might be chunk_id format
                # Try to extract hotel_id by dividing by 1000000
                if result_id_int > 1000000:
                    potential_hotel_id = result_id_int // 1000000
                    # Validate: if we multiply back and it's close, it's likely correct
                    if potential_hotel_id * 1000000 <= result_id_int < (potential_hotel_id + 1) * 1000000:
                        return potential_hotel_id
                # Otherwise, id might be hotel_id directly
                return result_id_int
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _deduplicate_by_hotel_id(
        self, 
        documents: List[Dict[str, Any]], 
        max_chunks_per_hotel: int = 2,
        min_hotels: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate documents by hotel_id, keeping top N chunks per hotel
        
        Args:
            documents: List of document results
            max_chunks_per_hotel: Maximum number of chunks to keep per hotel (default: 2)
            min_hotels: Minimum number of unique hotels to aim for (default: 5)
            
        Returns:
            Deduplicated list of documents with diverse hotels
        """
        # Group documents by hotel_id
        hotel_docs_map = {}  # hotel_id -> list of documents (sorted by score)
        
        for doc in documents:
            hotel_id = self._extract_hotel_id_from_result(doc)
            if hotel_id is None:
                # If we can't extract hotel_id, keep it (might be room/type_room or other type)
                # Add to a special key
                if 'unknown' not in hotel_docs_map:
                    hotel_docs_map['unknown'] = []
                hotel_docs_map['unknown'].append(doc)
                continue
            
            if hotel_id not in hotel_docs_map:
                hotel_docs_map[hotel_id] = []
            hotel_docs_map[hotel_id].append(doc)
        
        # Sort documents within each hotel by score (descending)
        for hotel_id in hotel_docs_map:
            hotel_docs_map[hotel_id].sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Calculate how many chunks per hotel to keep
        # If we have many hotels, keep fewer chunks per hotel
        # If we have few hotels, keep more chunks per hotel
        num_hotels = len([k for k in hotel_docs_map.keys() if k != 'unknown'])
        
        if num_hotels >= min_hotels:
            # We have enough hotels, keep max_chunks_per_hotel chunks per hotel
            chunks_per_hotel = max_chunks_per_hotel
        else:
            # We have fewer hotels, keep more chunks per hotel to reach min_hotels
            # But still limit to avoid too many chunks from same hotel
            chunks_per_hotel = min(max_chunks_per_hotel * 2, 5)
        
        # Collect top chunks from each hotel
        deduplicated = []
        for hotel_id, hotel_docs in hotel_docs_map.items():
            if hotel_id == 'unknown':
                # Keep all unknown documents (rooms, type_rooms, etc.)
                deduplicated.extend(hotel_docs)
            else:
                # Keep top N chunks for this hotel
                deduplicated.extend(hotel_docs[:chunks_per_hotel])
        
        # Sort all by score to maintain relevance order
        deduplicated.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        logger.info(f"Deduplication: {len(documents)} chunks -> {len(deduplicated)} chunks "
                   f"from {num_hotels} unique hotels (keeping {chunks_per_hotel} chunks per hotel)")
        
        return deduplicated
    
    def _extract_hotel_id_from_documents(self, documents: List[Dict[str, Any]], question: str) -> Optional[int]:
        """
        Extract hotel_id from search results or question
        
        Args:
            documents: Search results documents
            question: Original question
            
        Returns:
            hotel_id if found, None otherwise
        """
        try:
            # First, check if any document in results is a hotel
            for doc in documents:
                # Use the new helper function to extract hotel_id
                hotel_id = self._extract_hotel_id_from_result(doc)
                if hotel_id is not None:
                    return hotel_id
            
            # If no hotel found in results, check question patterns
            # Look for patterns like "KS X", "khách sạn X", "hotel X"
            question_lower = question.lower()
            
            # Check if question mentions "có các phòng", "phòng nào", "giới thiệu"
            # These patterns suggest user wants room information
            room_keywords = ["phòng", "room", "có các phòng", "phòng nào", "giới thiệu"]
            if any(keyword in question_lower for keyword in room_keywords):
                # Try to search for hotel one more time with hotel filter
                try:
                    hotel_docs = self.retriever_service.retrieve(
                        query=question,
                        collection_name=self.collection_name,
                        top_k=3,
                        filters={"document_type": "hotel"}
                    )
                    
                    if hotel_docs:
                        top_hotel = hotel_docs[0]
                        hotel_id = top_hotel.get('payload', {}).get('hotel_id')
                        if hotel_id:
                            try:
                                return int(hotel_id)
                            except (ValueError, TypeError):
                                pass
                except:
                    pass
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting hotel_id from documents: {e}")
            return None
    
    def _get_hotel_rooms(self, hotel_id: int, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Get rooms for a specific hotel
        
        Args:
            hotel_id: Hotel ID
            top_k: Maximum number of rooms to return
            
        Returns:
            List of room documents
        """
        try:
            # First, try to get from vector store
            rooms = self.retriever_service.retrieve_by_filters(
                filters={"document_type": "room", "hotel_id": hotel_id},
                collection_name=self.collection_name,
                limit=top_k
            )
            
            # If no rooms found in vector store, try database fallback
            if not rooms and DatabaseConnector is not None and HotelDataNormalizer is not None:
                logger.info(f"No rooms found in vector store for hotel_id={hotel_id}, trying database fallback...")
                try:
                    # Initialize connector and normalizer if needed
                    if self.room_db_connector is None:
                        self.room_db_connector = DatabaseConnector()
                    if self.room_normalizer is None:
                        self.room_normalizer = HotelDataNormalizer()
                    
                    # Get rooms from database
                    rooms_df = self.room_db_connector.get_rooms_enriched(hotel_ids=[hotel_id], limit=top_k)
                    if not rooms_df.empty:
                        # Normalize and convert to document format
                        normalized_df = self.room_normalizer.normalize_rooms(rooms_df)
                        rooms = []
                        for _, row in normalized_df.iterrows():
                            room_doc = {
                                'id': 2000000 + int(row.get('room_id', 0)),  # Room ID offset
                                'score': 0.8,
                                'payload': {
                                    'document_type': 'room',
                                    'hotel_id': int(row.get('hotel_id', hotel_id)),
                                    'hotel_name': str(row.get('hotel_name', '')),
                                    'room_id': int(row.get('room_id', 0)),
                                    'price': float(row.get('search_price', 0)),
                                    'type_name': str(row.get('type_room_name', '')),
                                    'text': str(row.get('semantic_text', ''))
                                }
                            }
                            rooms.append(room_doc)
                        logger.info(f"Retrieved {len(rooms)} rooms from database fallback")
                except Exception as e:
                    logger.warning(f"Database fallback failed: {e}")
            
            # Add default score for rooms (they don't have semantic scores)
            for room in rooms:
                if 'score' not in room:
                    room['score'] = 0.8  # Default relevance score
            
            logger.info(f"Found {len(rooms)} rooms for hotel_id={hotel_id}")
            return rooms
            
        except Exception as e:
            logger.error(f"Error getting hotel rooms: {e}")
            return []
    
    def _get_hotel_type_rooms(self, hotel_id: int, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get type_rooms used by a specific hotel
        
        Args:
            hotel_id: Hotel ID
            top_k: Maximum number of type_rooms to return
            
        Returns:
            List of type_room documents
        """
        try:
            # Get all type_rooms first
            all_type_rooms = self.retriever_service.retrieve_by_filters(
                filters={"document_type": "type_room"},
                collection_name=self.collection_name,
                limit=100  # Get more to filter
            )
            
            # Filter type_rooms that have this hotel_id in their hotel_ids list
            matching_type_rooms = []
            for type_room in all_type_rooms:
                payload = type_room.get('payload', {})
                hotel_ids = payload.get('hotel_ids', [])
                
                # hotel_ids can be a list or a string representation
                if isinstance(hotel_ids, list):
                    if hotel_id in hotel_ids:
                        matching_type_rooms.append(type_room)
                elif isinstance(hotel_ids, str) and hotel_ids.strip():
                    # Parse string representation (e.g., "1,2,3")
                    try:
                        ids_list = [int(x.strip()) for x in hotel_ids.split(',') if x.strip().isdigit()]
                        if hotel_id in ids_list:
                            matching_type_rooms.append(type_room)
                    except:
                        pass
            
            # If no type_rooms found in vector store, try database fallback
            if not matching_type_rooms and DatabaseConnector is not None and HotelDataNormalizer is not None:
                logger.info(f"No type_rooms found in vector store for hotel_id={hotel_id}, trying database fallback...")
                try:
                    # Initialize connector and normalizer if needed
                    if self.room_db_connector is None:
                        self.room_db_connector = DatabaseConnector()
                    if self.room_normalizer is None:
                        self.room_normalizer = HotelDataNormalizer()
                    
                    # Get type_rooms from database
                    type_rooms_df = self.room_db_connector.get_type_rooms_enriched(hotel_ids=[hotel_id], limit=top_k)
                    if not type_rooms_df.empty:
                        # Normalize and convert to document format
                        normalized_df = self.room_normalizer.normalize_type_rooms(type_rooms_df)
                        matching_type_rooms = []
                        for _, row in normalized_df.iterrows():
                            # Parse hotel_ids string to list
                            hotel_ids_str = str(row.get('hotel_ids', ''))
                            hotel_ids_list = []
                            if hotel_ids_str and hotel_ids_str != 'nan':
                                try:
                                    hotel_ids_list = [int(hid) for hid in hotel_ids_str.split(',') if hid.strip().isdigit()]
                                except:
                                    hotel_ids_list = []
                            
                            # Only include if this hotel_id is in the list
                            if hotel_id in hotel_ids_list:
                                type_room_doc = {
                                    'id': 3000000 + int(row.get('type_room_id', 0)),  # Type room ID offset
                                    'score': 0.7,
                                    'payload': {
                                        'document_type': 'type_room',
                                        'type_room_id': int(row.get('type_room_id', 0)),
                                        'type_room_name': str(row.get('type_room_name', '')),
                                        'hotel_ids': hotel_ids_list,
                                        'hotel_names': str(row.get('hotel_names', '')),
                                        'min_price': float(row.get('search_min_price', 0)),
                                        'max_price': float(row.get('search_max_price', 0)),
                                        'avg_price': float(row.get('search_avg_price', 0)),
                                        'room_count': int(row.get('room_count', 0)),
                                        'text': str(row.get('semantic_text', ''))
                                    }
                                }
                                matching_type_rooms.append(type_room_doc)
                        logger.info(f"Retrieved {len(matching_type_rooms)} type_rooms from database fallback")
                except Exception as e:
                    logger.warning(f"Database fallback failed: {e}")
            
            # Limit results
            matching_type_rooms = matching_type_rooms[:top_k]
            
            # Add default score
            for type_room in matching_type_rooms:
                if 'score' not in type_room:
                    type_room['score'] = 0.7  # Default relevance score
            
            logger.info(f"Found {len(matching_type_rooms)} type_rooms for hotel_id={hotel_id}")
            return matching_type_rooms
            
        except Exception as e:
            logger.error(f"Error getting hotel type_rooms: {e}")
            return []

