#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Query Router
Phân loại câu hỏi: Statistical (SQL) vs Semantic (RAG)
Hybrid approach: Rule-based trước, nếu confidence thấp thì gọi LLM
"""

import re
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class QueryRouter:
    """Phân loại câu hỏi thành Statistical hoặc Semantic"""
    
    # Patterns cho câu hỏi thống kê (statistical)
    STATISTICAL_PATTERNS = {
        # Đếm số lượng
        "count": [
            r"có\s+bao\s+nhiêu",
            r"tổng\s+số",
            r"số\s+lượng",
            r"đếm",
            r"count",
            r"có\s+mấy",
            r"có\s+.*\s+khách\s+sạn",
            r"bao\s+nhiêu\s+khách\s+sạn",
        ],
        # So sánh, thống kê
        "statistics": [
            r"trung\s+bình",
            r"giá\s+trung\s+bình",
            r"giá\s+cao\s+nhất",
            r"giá\s+thấp\s+nhất",
            r"nhiều\s+nhất",
            r"ít\s+nhất",
            r"tổng",
            r"tổng\s+cộng",
        ],
        # Câu hỏi có/không (boolean)
        "boolean": [
            r"có\s+.*\s+không",
            r"có\s+.*\s+chưa",
            r"tồn\s+tại",
        ]
    }
    
    # Patterns cho câu hỏi ngữ nghĩa (semantic)
    SEMANTIC_PATTERNS = [
        r"khách\s+sạn\s+nào",
        r"tìm\s+khách\s+sạn",
        r"giới\s+thiệu",
        r"mô\s+tả",
        r"thông\s+tin",
        r"đặc\s+điểm",
        r"tiện\s+ích",
        r"có\s+gì",
        r"như\s+thế\s+nào",
    ]
    
    # Confidence threshold để quyết định có gọi LLM không
    LLM_THRESHOLD = 0.7  # Nếu confidence < 0.7, gọi LLM
    
    def __init__(self, use_llm: bool = True, llm=None):
        """
        Initialize Query Router
        
        Args:
            use_llm: Nếu True, dùng LLM khi confidence thấp
            llm: LLM instance (optional)
        """
        self.use_llm = use_llm and llm is not None
        self.llm = llm
    
    def classify_query(self, question: str) -> Dict:
        """
        Phân loại câu hỏi với Hybrid approach:
        - Bước 1: Rule-based (nhanh)
        - Bước 2: Nếu confidence thấp, gọi LLM
        
        Args:
            question: Câu hỏi của user
            
        Returns:
            Dictionary với:
            {
                "type": "statistical" | "semantic" | "hybrid",
                "confidence": 0.0-1.0,
                "reason": "Lý do phân loại",
                "method": "rule-based" | "llm"
            }
        """
        # Bước 1: Rule-based classification (nhanh)
        result = self._classify_rule_based(question)
        
        # Bước 2: Nếu confidence thấp và có LLM, gọi LLM
        if result["confidence"] < self.LLM_THRESHOLD and self.use_llm:
            logger.info(f"Rule-based confidence ({result['confidence']:.2f}) < threshold ({self.LLM_THRESHOLD}), using LLM")
            llm_result = self._classify_with_llm(question)
            
            # Chọn kết quả có confidence cao hơn
            if llm_result["confidence"] > result["confidence"]:
                logger.info(f"LLM result ({llm_result['confidence']:.2f}) better than rule-based ({result['confidence']:.2f})")
                return llm_result
            else:
                logger.info(f"Rule-based result ({result['confidence']:.2f}) better than LLM ({llm_result['confidence']:.2f})")
                return result
        
        return result
    
    def _classify_rule_based(self, question: str) -> Dict:
        """
        Phân loại bằng rule-based patterns (nhanh, đơn giản)
        """
        question_lower = question.lower().strip()
        
        # Check statistical patterns
        statistical_score = 0
        matched_patterns = []
        
        for category, patterns in self.STATISTICAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, question_lower, re.IGNORECASE):
                    statistical_score += 1
                    matched_patterns.append(f"{category}:{pattern}")
        
        # Check semantic patterns
        semantic_score = 0
        semantic_matches = []
        for pattern in self.SEMANTIC_PATTERNS:
            if re.search(pattern, question_lower, re.IGNORECASE):
                semantic_score += 1
                semantic_matches.append(pattern)
        
        # Determine type
        if statistical_score > 0 and semantic_score == 0:
            # Pure statistical
            confidence = min(0.9, 0.5 + statistical_score * 0.1)
            return {
                "type": "statistical",
                "confidence": confidence,
                "reason": f"Matched {statistical_score} statistical patterns: {matched_patterns[:2]}",
                "method": "rule-based"
            }
        elif statistical_score == 0 and semantic_score > 0:
            # Pure semantic
            confidence = min(0.9, 0.5 + semantic_score * 0.1)
            return {
                "type": "semantic",
                "confidence": confidence,
                "reason": f"Matched {semantic_score} semantic patterns",
                "method": "rule-based"
            }
        elif statistical_score > 0 and semantic_score > 0:
            # Hybrid: có thể cần cả 2
            # Ví dụ: "Có bao nhiêu khách sạn 5 sao có hồ bơi?" 
            # → Cần SQL để đếm, nhưng cũng cần RAG để hiểu "hồ bơi"
            return {
                "type": "hybrid",
                "confidence": 0.7,
                "reason": f"Matched both: {statistical_score} statistical, {semantic_score} semantic",
                "method": "rule-based"
            }
        else:
            # Default to semantic (RAG)
            return {
                "type": "semantic",
                "confidence": 0.5,
                "reason": "No patterns matched, defaulting to semantic",
                "method": "rule-based"
            }
    
    def _classify_with_llm(self, question: str) -> Dict:
        """
        Phân loại bằng LLM (thông minh, linh hoạt hơn)
        """
        try:
            classification_prompt = """Bạn là hệ thống phân loại câu hỏi về khách sạn.

Phân loại câu hỏi sau thành một trong các loại:

1. "statistical": Câu hỏi cần đếm, thống kê, tính toán số lượng
   - Ví dụ: "Có bao nhiêu khách sạn trong khu vực Ngũ Hành Sơn?"
   - Ví dụ: "Giá trung bình của khách sạn 5 sao là bao nhiêu?"
   - Ví dụ: "Có khách sạn nào ở Sơn Trà không?"

2. "semantic": Câu hỏi tìm kiếm, mô tả, thông tin chi tiết
   - Ví dụ: "Khách sạn nào có view biển đẹp?"
   - Ví dụ: "Giới thiệu khách sạn 5 sao ở Đà Nẵng"
   - Ví dụ: "Khách sạn nào có spa và hồ bơi?"

3. "hybrid": Câu hỏi cần cả thống kê và tìm kiếm
   - Ví dụ: "Có bao nhiêu khách sạn 5 sao có hồ bơi?" (cần đếm + tìm kiếm)

Câu hỏi: {question}

Trả về JSON format:
{{
    "type": "statistical" | "semantic" | "hybrid",
    "confidence": 0.0-1.0,
    "reason": "Lý do phân loại"
}}

CHỈ trả về JSON, không có text khác."""

            prompt = classification_prompt.format(question=question)
            
            # Call LLM
            if hasattr(self.llm, 'invoke'):
                # LangChain ChatOpenAI
                try:
                    from langchain.schema import HumanMessage
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    response_text = response.content if hasattr(response, 'content') else str(response)
                except:
                    # Fallback for Ollama
                    response_text = self.llm.invoke(prompt)
            elif hasattr(self.llm, 'predict'):
                response_text = self.llm.predict(prompt)
            else:
                response_text = str(self.llm.invoke(prompt))
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            result = json.loads(response_text)
            
            # Validate
            if not isinstance(result, dict) or "type" not in result:
                logger.warning("LLM returned invalid format, falling back to rule-based")
                return self._classify_rule_based(question)
            
            query_type = result.get("type", "semantic")
            if query_type not in ["statistical", "semantic", "hybrid"]:
                query_type = "semantic"
            
            confidence = float(result.get("confidence", 0.7))
            # Ensure confidence is in valid range
            confidence = max(0.0, min(1.0, confidence))
            
            return {
                "type": query_type,
                "confidence": confidence,
                "reason": result.get("reason", "LLM classification"),
                "method": "llm"
            }
            
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}, falling back to rule-based")
            return self._classify_rule_based(question)

