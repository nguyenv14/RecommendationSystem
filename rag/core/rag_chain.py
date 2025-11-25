#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Chain

RAG chain setup for generation pipeline (Layer 3).
"""

import logging
from typing import Dict, Optional

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Qdrant

logger = logging.getLogger(__name__)


class RAGChain:
    """
    RAG Chain - Layer 3: Generation Pipeline
    Handles LLM-based answer generation with context retrieval
    """
    
    def __init__(self, vectorstore: Qdrant, llm, k: int = 5):
        """
        Initialize RAG Chain
        
        Args:
            vectorstore: LangChain Qdrant vectorstore
            llm: LLM instance
            k: Number of documents to retrieve
        """
        self.vectorstore = vectorstore
        self.llm = llm
        self.k = k
        self.qa_chain: Optional[RetrievalQA] = None
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize QA chain"""
        # Create retriever
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.k}
        )
        
        # Prompt template
        prompt_template = """Bạn là trợ lý tư vấn khách sạn tại Đà Nẵng. Trả lời HOÀN TOÀN bằng tiếng Việt.

Thông tin khách sạn:
{context}

Câu hỏi: {question}

QUAN TRỌNG: 
- CHỈ trả lời các câu hỏi liên quan đến khách sạn, nhà nghỉ, resort, homestay tại Đà Nẵng.
- Nếu câu hỏi KHÔNG liên quan đến khách sạn hoặc du lịch, bạn PHẢI trả lời: "Xin lỗi, tôi chỉ có thể tư vấn về khách sạn tại Đà Nẵng. Câu hỏi của bạn không liên quan đến dịch vụ này."
- Nếu thông tin khách sạn trên KHÔNG có câu trả lời phù hợp cho câu hỏi, bạn PHẢI trả lời: "Không tìm thấy khách sạn phù hợp với yêu cầu của bạn trong hệ thống."

QUAN TRỌNG VỀ TÊN KHÁCH SẠN:
- LUÔN trả lời với TÊN KHÁCH SẠN CỤ THỂ (hotel_name), KHÔNG trả lời với thương hiệu (brand_name).
- Nếu user hỏi về một thương hiệu (ví dụ: "Accor", "Meliá", "InterContinental"), bạn phải liệt kê TẤT CẢ các khách sạn cụ thể thuộc thương hiệu đó từ thông tin trên.
- Mỗi khách sạn phải được nêu rõ TÊN KHÁCH SẠN CỤ THỂ (ví dụ: "Meliá Vinpearl Riverfront", "Grand Tourane Hotel"), không chỉ nêu thương hiệu chung (ví dụ: KHÔNG chỉ nêu "Accor" hay "Meliá Hotels International").
- Trong context, "Tên khách sạn:" là tên cụ thể của khách sạn, "Thương hiệu:" là brand name (chỉ để tham khảo).

Nếu câu hỏi liên quan đến khách sạn và có thông tin phù hợp, hãy trả lời chi tiết, tự nhiên bằng tiếng Việt. Nêu TÊN KHÁCH SẠN CỤ THỂ, giá, đánh giá (sao), địa điểm, và các tiện ích nổi bật. So sánh các khách sạn nếu có nhiều lựa chọn.

Trả lời:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True,
            verbose=False
        )
        
        logger.info("✅ RAG Chain initialized")
    
    def ask(self, question: str) -> Dict:
        """
        Ask question với RAG
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and sources
        """
        if self.qa_chain is None:
            raise ValueError("QA chain not initialized")
        
        result = self.qa_chain({"query": question})
        
        response = {
            "question": question,
            "answer": result["result"],
            "sources": []
        }
        
        # Add source documents
        for doc in result.get("source_documents", []):
            page_content = doc.page_content if doc.page_content else ""
            if not page_content:
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

