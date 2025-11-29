"""
RAG Service
Unified RAG (Retrieval-Augmented Generation) service
Sử dụng LangChain RetrievalQA chain giống simple_rag_system.py
"""

from typing import List, Dict, Optional, Any
from langchain_community.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
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
    Sử dụng LangChain RetrievalQA chain giống simple_rag_system.py
    Flow: Query → Embedding → Vector Search (k=5) → Combine Context → Build Prompt → LLM Generation → Parse Response
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
        self.vectorstore_service = vectorstore_service
        self.retriever_service = retriever_service
        self.generator = generator_service
        self.collection_name = collection_name or settings.RAG_COLLECTION_HOTELS
        
        # LangChain Qdrant vectorstore (for RetrievalQA chain)
        self.vectorstore: Optional[Qdrant] = None
        self.retriever = None
        self.qa_chain: Optional[RetrievalQA] = None
        
        # Initialize QA chain
        self._initialize_qa_chain()
        
        logger.info(f"✅ RAGService initialized (collection={self.collection_name})")
    
    def _initialize_qa_chain(self):
        """Initialize QA chain với LangChain RetrievalQA (giống simple_rag_system.py)"""
        try:
            # Create LangChain Qdrant vectorstore
            from qdrant_client import QdrantClient
            
            client = QdrantClient(url=self.vectorstore_service.url)
            
            # Check if collection exists
            if not self.vectorstore_service.collection_exists(self.collection_name):
                logger.warning(f"Collection '{self.collection_name}' does not exist. Please index documents first.")
                return
            
            # Create LangChain Qdrant vectorstore wrapper
            # Note: LangChain Qdrant wrapper cần embeddings và client
            self.vectorstore = Qdrant(
                client=client,
                collection_name=self.collection_name,
                embeddings=self.embedding.model  # LangChain embeddings
            )
            
            # Create retriever với k=5 (theo RAG_FLOW_EXPLANATION.md)
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 5}  # Top 5 documents
            )
            
            # Prompt template (giống simple_rag_system.py)
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
            
            # Create QA chain với chain_type="stuff" (giống simple_rag_system.py)
            # chain_type="stuff": Combine tất cả 5 documents vào 1 prompt
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.generator.llm,
                chain_type="stuff",  # Combine tất cả context vào 1 prompt
                retriever=self.retriever,  # k=5
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True,
                verbose=False
            )
            
            logger.info("✅ QA chain initialized (k=5, chain_type='stuff')")
            
        except Exception as e:
            logger.error(f"Error initializing QA chain: {e}")
            logger.warning("QA chain not initialized. Please ensure collection exists and documents are indexed.")
    
    def ask(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        prompt_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask a question and get answer (main RAG flow)
        Sử dụng LangChain RetrievalQA chain giống simple_rag_system.py
        
        Args:
            question: User question
            top_k: Number of documents to retrieve (ignored, uses k=5 from retriever)
            filters: Optional filters (not used in RetrievalQA chain, kept for compatibility)
            prompt_template: Optional custom prompt (not used, kept for compatibility)
            
        Returns:
            Dict with question, answer, sources
        """
        logger.info(f"RAG question: '{question[:50]}...'")
        
        if self.qa_chain is None:
            logger.error("QA chain not initialized. Please ensure collection exists and documents are indexed.")
            return {
                "question": question,
                "answer": "Xin lỗi, hệ thống chưa được khởi tạo. Vui lòng thử lại sau.",
                "sources": [],
                "num_sources": 0
            }
        
        try:
            # Use RetrievalQA chain (giống simple_rag_system.py)
            # Flow: Query → Embedding → Vector Search (k=5) → Combine Context → Build Prompt → LLM Generation
            result = self.qa_chain({"query": question})
            
            # Format response (giống simple_rag_system.py)
            response = {
                "question": question,
                "answer": result["result"],  # LLM generated answer
                "sources": []
            }
            
            # Extract source documents
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
            
            logger.info(f"✅ RAG answer generated (sources: {len(response['sources'])})")
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG flow: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
            success = self.vectorstore_service.upsert_points(
                collection_name=self.collection_name,
                points=points
            )
            
            # Re-initialize QA chain after indexing
            if success:
                self._initialize_qa_chain()
            
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
                    "default_top_k": self.retriever_service.default_top_k,
                    "qa_chain_k": 5  # k=5 for QA chain
                },
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

