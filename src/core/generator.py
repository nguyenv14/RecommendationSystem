"""
Generator Service
LLM generation cho RAG system
"""

from typing import List, Dict, Optional, Any
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ..shared import get_logger

logger = get_logger(__name__)


class GeneratorService:
    """
    LLM Generator service for RAG
    Generates answers based on retrieved context
    """
    
    def __init__(
        self,
        provider: str = "ollama",
        model_name: str = "qwen3",
        ollama_url: str = "http://localhost:11434",
        lm_studio_url: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        openrouter_model: Optional[str] = None,
        openrouter_base_url: str = "https://openrouter.ai/api",
        temperature: float = 0.3  # Theo RAG_FLOW_EXPLANATION.md: temperature=0.3
    ):
        """
        Initialize generator service
        
        Args:
            provider: 'ollama', 'lm_studio' hoặc 'openrouter'
            model_name: Model name
            ollama_url: Ollama URL
            lm_studio_url: LM Studio URL
            openrouter_api_key: OpenRouter API key (đọc từ env)
            openrouter_model: Tên model trên OpenRouter (vd: 'qwen/qwen2.5-vl-72b-instruct')
            openrouter_base_url: OpenRouter base url (mặc định: https://openrouter.ai/api)
            temperature: Generation temperature (default: 0.3 theo RAG_FLOW_EXPLANATION.md)
        """
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature
        self.openrouter_model = openrouter_model or model_name
        
        # Log provider configuration
        logger.info(f"🔧 Initializing GeneratorService with provider: {provider}")
        if provider == "lm_studio":
            logger.info(f"   LM Studio URL: {lm_studio_url}")
        elif provider == "ollama":
            logger.info(f"   Ollama URL: {ollama_url}")
        elif provider == "openrouter":
            logger.info(f"   OpenRouter model: {self.openrouter_model}")
        
        # Initialize LLM
        if provider == "ollama":
            self.llm = Ollama(
                model=model_name,
                base_url=ollama_url,
                temperature=temperature  # 0.3 theo RAG_FLOW_EXPLANATION.md
            )
            logger.info(f"Using Ollama LLM: {model_name} (temperature={temperature})")
            
        elif provider == "lm_studio":
            # LM Studio uses OpenAI-compatible API but doesn't need real API key
            # Theo RAG_FLOW_EXPLANATION.md: max_tokens=2048, temperature=0.3
            if not lm_studio_url:
                raise ValueError("LM_STUDIO_URL is required when LLM_PROVIDER is 'lm_studio'")
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    openai_api_base=f"{lm_studio_url}/v1",
                    openai_api_key="lm-studio",  # Dummy key for LM Studio
                    temperature=temperature,  # 0.3 theo RAG_FLOW_EXPLANATION.md
                    max_tokens=2048,  # Theo RAG_FLOW_EXPLANATION.md: max_tokens=2048
                    timeout=120.0
                )
                logger.info(f"Using LM Studio LLM: {model_name} (temperature={temperature}, max_tokens=2048)")
            except Exception as e:
                # Fallback: try with base_url (newer API)
                logger.warning(f"Trying base_url instead of openai_api_base...")
                self.llm = ChatOpenAI(
                    model=model_name,
                    base_url=f"{lm_studio_url}/v1",
                    api_key="lm-studio",  # Dummy key for LM Studio
                    temperature=temperature,  # 0.3 theo RAG_FLOW_EXPLANATION.md
                    max_tokens=2048,  # Theo RAG_FLOW_EXPLANATION.md: max_tokens=2048
                    timeout=120.0
                )
                logger.info(f"Using LM Studio LLM (base_url): {model_name} (temperature={temperature}, max_tokens=2048)")

        elif provider == "openrouter":
            # Sử dụng OpenRouter (OpenAI-compatible) qua ChatOpenAI
            if not openrouter_api_key:
                raise ValueError("OPENROUTER_API_KEY is required when LLM_PROVIDER is 'openrouter'")
            try:
                # OpenRouter dùng OpenAI-compatible schema, base /v1
                self.llm = ChatOpenAI(
                    model=self.openrouter_model,
                    openai_api_base=f"{openrouter_base_url}/v1",
                    openai_api_key=openrouter_api_key,
                    temperature=temperature,
                    max_tokens=2048,
                    timeout=120.0,
                    extra_headers={
                        # Các header này là optional cho ranking trên openrouter.ai
                        "HTTP-Referer": "http://localhost",  # có thể override bằng env nếu muốn
                        "X-Title": "Hotel-RAG-System",
                    },
                )
                logger.info(f"Using OpenRouter LLM: {self.openrouter_model} (temperature={temperature}, max_tokens=2048)")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenRouter LLM: {e}")
                raise

        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        logger.info(f"✅ GeneratorService initialized: {provider}/{self.openrouter_model if provider == 'openrouter' else model_name} (temperature={temperature}, max_tokens=2048)")
    
    def generate(
        self,
        query: str,
        context: str,
        prompt_template: Optional[str] = None
    ) -> str:
        """
        Generate answer based on query and context
        
        Args:
            query: User query
            context: Retrieved context
            prompt_template: Optional custom prompt template
            
        Returns:
            Generated answer
        """
        logger.debug(f"🔧 Generating with provider: {self.provider}, model: {self.model_name}")
        
        if prompt_template is None:
            prompt_template = self._get_default_prompt()
        
        try:
            # Create prompt
            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Generate
            answer = chain.run(context=context, question=query)
            
            logger.info(f"✅ Generated answer for query: '{query[:50]}...' (provider: {self.provider})")
            return answer.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating answer with provider '{self.provider}': {e}")
            logger.error(f"   Model: {self.model_name}, LLM type: {type(self.llm).__name__}")
            return f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi: {str(e)}"
    
    def generate_from_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        prompt_template: Optional[str] = None,
        max_context_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Generate answer from list of retrieved documents
        
        Args:
            query: User query
            documents: List of retrieved documents
            prompt_template: Optional custom prompt
            max_context_tokens: Maximum tokens for context
            
        Returns:
            Dict with answer and sources
        """
        # Build context from documents với token limit
        context = self._build_context(documents, max_tokens=max_context_tokens)
        
        # Generate answer
        answer = self.generate(query, context, prompt_template)
        
        # Extract sources
        sources = self._extract_sources(documents)
        
        return {
            "question": query,
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources)
        }
    
    def _build_context(
        self, 
        documents: List[Dict[str, Any]], 
        max_tokens: int = 4000
    ) -> str:
        """
        Build context string from documents với token limit management
        Theo RAG_FLOW_EXPLANATION.md: Combine documents thành context string
        Optimized: Sort by relevance, respect token limit
        
        Args:
            documents: List of documents (expected: 5 documents theo RAG_FLOW_EXPLANATION.md)
            max_tokens: Maximum tokens for context (default: 4000)
            
        Returns:
            Context string (tổng context có thể ~4000-5000 characters với k=5, chunk_size=800)
        """
        # Sort documents by relevance score (highest first)
        sorted_docs = sorted(
            documents, 
            key=lambda x: x.get("score", 0.0), 
            reverse=True
        )
        
        context_parts = []
        current_tokens = 0
        
        # Approximate token counting (rough estimate: 1 token ≈ 4 characters for Vietnamese)
        # For more accurate counting, would need tiktoken or similar
        chars_per_token = 4
        
        for i, doc in enumerate(sorted_docs, 1):
            payload = doc.get("payload", {})
            
            # Try to extract meaningful text
            # Priority: page_content (from Qdrant) > semantic_text > other text fields
            text = payload.get("page_content") or self._extract_text(payload)
            
            if not text:
                continue
            
            # Estimate tokens for this document
            doc_text = f"[Document {i}]\n{text}"
            estimated_tokens = len(doc_text) / chars_per_token
            
            # Check if adding this document would exceed limit
            if current_tokens + estimated_tokens > max_tokens:
                # Try to truncate document to fit
                remaining_tokens = max_tokens - current_tokens
                if remaining_tokens > 100:  # Only if we have meaningful space left
                    max_chars = int(remaining_tokens * chars_per_token)
                    text = text[:max_chars] + "..."
                    doc_text = f"[Document {i}]\n{text}"
                    context_parts.append(doc_text)
                break
            
            context_parts.append(doc_text)
            current_tokens += estimated_tokens
        
        # Combine tất cả documents thành 1 context string
        # Theo RAG_FLOW_EXPLANATION.md: chain_type="stuff" combines all documents into 1 prompt
        result = "\n\n".join(context_parts) if context_parts else "Không có thông tin."
        
        logger.debug(f"Built context: {len(context_parts)} documents, ~{int(current_tokens)} tokens")
        return result
    
    def _extract_text(self, payload: Dict[str, Any]) -> str:
        """Extract text from document payload"""
        # Priority order for text fields
        text_fields = [
            'semantic_text', 'text', 'content', 'description',
            'hotel_desc', 'hotel_name', 'name', 'title'
        ]
        
        text_parts = []
        
        for field in text_fields:
            if field in payload and payload[field]:
                text_parts.append(str(payload[field]))
        
        # If no text fields, use all string values
        if not text_parts:
            for key, value in payload.items():
                if isinstance(value, str) and value and len(value) > 10:
                    text_parts.append(f"{key}: {value}")
        
        return "\n".join(text_parts) if text_parts else ""
    
    def _extract_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract source information from documents
        Theo RAG_FLOW_EXPLANATION.md: Extract sources từ top 5 documents
        """
        sources = []
        
        for doc in documents:
            payload = doc.get("payload", {})
            score = doc.get("score", 0.0)
            
            # Extract page_content for text_preview
            page_content = payload.get("page_content") or self._extract_text(payload)
            
            source = {
                "id": doc.get("id"),
                "score": score,
            }
            
            # Add useful fields (theo RAG_FLOW_EXPLANATION.md format)
            useful_fields = [
                'hotel_id', 'hotel_name', 'hotel_rank', 'hotel_price_average',
                'area_name', 'document_type',
                'coupon_id', 'coupon_code', 'source_system'
            ]
            
            for field in useful_fields:
                if field in payload:
                    source[field] = payload[field]
            
            # Add text_preview (theo RAG_FLOW_EXPLANATION.md: text_preview từ page_content)
            if page_content:
                source["text_preview"] = page_content[:300] + "..." if len(page_content) > 300 else page_content
            
            sources.append(source)
        
        return sources
    
    def _get_default_prompt(self) -> str:
        """
        Get default RAG prompt template
        Theo RAG_FLOW_EXPLANATION.md: Prompt chi tiết, so sánh hotels
        """
        return """Bạn là trợ lý tư vấn khách sạn tại Đà Nẵng. Trả lời HOÀN TOÀN bằng tiếng Việt.

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

