"""
RAG Service
Unified RAG (Retrieval-Augmented Generation) service
"""

from typing import List, Dict, Optional, Any
from .embeddings import EmbeddingService
from .vectorstore import VectorStoreService
from .retriever import RetrieverService
from .generator import GeneratorService
from ..shared import get_logger
from ..config import get_settings, Collections

logger = get_logger(__name__)


class RAGService:
    """
    Unified RAG service
    Combines retrieval and generation for question answering
    """
    
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vectorstore_service: Optional[VectorStoreService] = None,
        retriever_service: Optional[RetrieverService] = None,
        generator_service: Optional[GeneratorService] = None,
        collection_name: Optional[str] = None
    ):
        """
        Initialize RAG service
        
        Args:
            embedding_service: Optional embedding service (creates if None)
            vectorstore_service: Optional vectorstore service (creates if None)
            retriever_service: Optional retriever service (creates if None)
            generator_service: Optional generator service (creates if None)
            collection_name: Collection to use for RAG
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
        self.vectorstore = vectorstore_service
        self.retriever = retriever_service
        self.generator = generator_service
        self.collection_name = collection_name or settings.RAG_COLLECTION_HOTELS
        
        logger.info(f"✅ RAGService initialized (collection={self.collection_name})")
    
    def ask(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        prompt_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask a question and get answer (main RAG flow)
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            filters: Optional filters (e.g. {"document_type": "hotel"})
            prompt_template: Optional custom prompt
            
        Returns:
            Dict with question, answer, sources
        """
        logger.info(f"RAG question: '{question[:50]}...'")
        
        try:
            # Retrieve relevant documents
            documents = self.retriever.retrieve(
                query=question,
                collection_name=self.collection_name,
                top_k=top_k,
                filters=filters
            )
            
            if not documents:
                return {
                    "question": question,
                    "answer": "Xin lỗi, tôi không tìm thấy thông tin liên quan để trả lời câu hỏi này.",
                    "sources": [],
                    "num_sources": 0
                }
            
            # Generate answer from documents
            result = self.generator.generate_from_documents(
                query=question,
                documents=documents,
                prompt_template=prompt_template
            )
            
            logger.info(f"✅ RAG answer generated (sources: {result['num_sources']})")
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG flow: {e}")
            return {
                "question": question,
                "answer": f"Xin lỗi, đã xảy ra lỗi: {str(e)}",
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
        
        documents = self.retriever.retrieve(
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
            if recreate_collection or not self.vectorstore.collection_exists(self.collection_name):
                self.vectorstore.create_collection(
                    collection_name=self.collection_name,
                    vector_size=vector_size,
                    recreate=recreate_collection
                )
            
            # Prepare points
            points = []
            
            for doc in documents:
                doc_id = doc.get(id_field)
                text = doc.get(text_field, "")
                
                if not doc_id or not text:
                    logger.warning(f"Skipping document without ID or text: {doc}")
                    continue
                
                # Embed text
                vector = self.embedding.embed_query(text)
                
                # Prepare payload
                payload = {text_field: text}
                
                # Add metadata fields
                if metadata_fields:
                    for field in metadata_fields:
                        if field in doc:
                            payload[field] = doc[field]
                else:
                    # Add all fields
                    payload.update(doc)
                
                # Create point
                from qdrant_client.models import PointStruct
                point = PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload=payload
                )
                points.append(point)
            
            # Upsert points
            success = self.vectorstore.upsert_points(
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
            collection_info = self.vectorstore.get_collection_info(self.collection_name)
            cache_stats = self.embedding.get_cache_stats()
            
            return {
                "collection": {
                    "name": self.collection_name,
                    "points_count": collection_info.points_count if collection_info else 0,
                    "vector_size": collection_info.config.params.vectors.size if collection_info else 0
                },
                "embedding": cache_stats,
                "retriever": {
                    "default_top_k": self.retriever.default_top_k
                },
                "generator": {
                    "provider": self.generator.provider,
                    "model": self.generator.model_name
                }
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

