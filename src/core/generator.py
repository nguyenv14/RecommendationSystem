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
        temperature: float = 0.3  # Theo RAG_FLOW_EXPLANATION.md: temperature=0.3
    ):
        """
        Initialize generator service
        
        Args:
            provider: 'ollama' or 'lm_studio'
            model_name: Model name
            ollama_url: Ollama URL
            lm_studio_url: LM Studio URL
            temperature: Generation temperature (default: 0.3 theo RAG_FLOW_EXPLANATION.md)
        """
        self.provider = provider
        self.model_name = model_name
        self.temperature = temperature
        
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
            
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        logger.info(f"✅ GeneratorService initialized: {provider}/{model_name} (temperature={temperature}, max_tokens=2048)")
    
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
            
            logger.info(f"Generated answer for query: '{query[:50]}...'")
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi: {str(e)}"
    
    def generate_from_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        prompt_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate answer from list of retrieved documents
        
        Args:
            query: User query
            documents: List of retrieved documents
            prompt_template: Optional custom prompt
            
        Returns:
            Dict with answer and sources
        """
        # Build context from documents
        context = self._build_context(documents)
        
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
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Build context string from documents
        
        Args:
            documents: List of documents
            
        Returns:
            Context string
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            payload = doc.get("payload", {})
            
            # Try to extract meaningful text
            text = self._extract_text(payload)
            
            if text:
                context_parts.append(f"[Document {i}]\n{text}")
        
        return "\n\n".join(context_parts) if context_parts else "Không có thông tin."
    
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
        """Extract source information from documents"""
        sources = []
        
        for doc in documents:
            payload = doc.get("payload", {})
            score = doc.get("score", 0.0)
            
            source = {
                "id": doc.get("id"),
                "score": score,
            }
            
            # Add useful fields
            useful_fields = [
                'hotel_id', 'hotel_name', 'document_type',
                'coupon_id', 'coupon_code', 'source_system'
            ]
            
            for field in useful_fields:
                if field in payload:
                    source[field] = payload[field]
            
            sources.append(source)
        
        return sources
    
    def _get_default_prompt(self) -> str:
        """Get default RAG prompt template"""
        return """Bạn là trợ lý AI thông minh chuyên về khách sạn và du lịch tại Việt Nam.

Dựa trên thông tin sau đây, hãy trả lời câu hỏi của khách hàng một cách chính xác và hữu ích.

Thông tin tham khảo:
{context}

Câu hỏi: {question}

Hướng dẫn:
- Trả lời bằng tiếng Việt
- Dựa trên thông tin được cung cấp
- Nếu không có thông tin, hãy nói rõ
- Trả lời ngắn gọn, rõ ràng, hữu ích
- Có thể đề xuất thêm nếu phù hợp

Trả lời:"""

