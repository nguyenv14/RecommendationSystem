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
from ..shared import get_logger
from ..config import get_settings, Collections

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
            generator_service = GeneratorService(
                provider=settings.LLM_PROVIDER,
                model_name=settings.LLM_MODEL,
                ollama_url=settings.OLLAMA_URL,
                lm_studio_url=settings.LM_STUDIO_URL
            )
        
        self.embedding = embedding_service
        self.vectorstore_service = vectorstore_service
        self.retriever_service = retriever_service
        self.generator = generator_service
        self.collection_name = collection_name or settings.RAG_COLLECTION_HOTELS
        
        # Initialize optimizations
        self.query_preprocessor = QueryPreprocessor()
        self.response_cache = ResponseCache(ttl=response_cache_ttl)
        
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
            
            # Step 3-4: Embedding (with cache check) + Vector Search
            if top_k is None:
                top_k = 5  # Default k=5
            
            # Note: Embedding cache is handled inside RetrieverService.retrieve()
            # which calls EmbeddingService.embed_query() which checks cache
            documents = self.retriever_service.retrieve(
                query=processed_query,  # Use processed query
                collection_name=self.collection_name,
                top_k=top_k,
                filters=filters
            )
            
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
            
            # Step 6: Re-rank Results - TODO: implement
            # For now, documents are already sorted by score from Qdrant
            
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

