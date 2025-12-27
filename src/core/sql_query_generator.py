#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Query Generator
Convert câu hỏi tiếng Việt → SQL query
"""

import re
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class SQLQueryGenerator:
    """Generate SQL queries từ câu hỏi tiếng Việt"""
    
    # Location mapping
    LOCATIONS = {
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
    
    def __init__(self, use_llm: bool = True, llm=None):
        """
        Initialize SQL Query Generator
        
        Args:
            use_llm: Nếu True, dùng LLM để generate SQL (thông minh hơn)
            llm: LLM instance (optional)
        """
        self.use_llm = use_llm and llm is not None
        self.llm = llm
    
    def generate_sql(self, question: str, extracted_info: Dict = None) -> Dict:
        """
        Generate SQL query từ câu hỏi
        
        Args:
            question: Câu hỏi tiếng Việt
            extracted_info: Thông tin đã extract (location, rank, etc.)
            
        Returns:
            Dictionary với:
            {
                "sql": "SELECT COUNT(*) ...",
                "query_type": "count" | "avg" | "max" | "min" | "exists",
                "params": {},
                "explanation": "Giải thích query"
            }
        """
        if self.use_llm:
            return self._generate_with_llm(question, extracted_info)
        else:
            return self._generate_rule_based(question, extracted_info)
    
    def _generate_rule_based(self, question: str, extracted_info: Dict = None) -> Dict:
        """
        Generate SQL bằng rule-based patterns
        """
        question_lower = question.lower().strip()
        
        # Extract location
        location = None
        if extracted_info and extracted_info.get("location"):
            location = extracted_info["location"]
        else:
            location = self._extract_location(question)
        
        # Extract rank
        rank = None
        if extracted_info and extracted_info.get("rank"):
            rank = extracted_info["rank"]
        else:
            rank = self._extract_rank(question)
        
        # Determine query type
        query_type = "count"  # Default
        
        if "trung bình" in question_lower or "giá trung bình" in question_lower:
            query_type = "avg"
        elif "cao nhất" in question_lower or "giá cao nhất" in question_lower:
            query_type = "max"
        elif "thấp nhất" in question_lower or "giá thấp nhất" in question_lower:
            query_type = "min"
        elif "có" in question_lower and ("không" in question_lower or "chưa" in question_lower):
            query_type = "exists"
        elif "bao nhiêu" in question_lower or "số lượng" in question_lower or "tổng số" in question_lower:
            query_type = "count"
        
        # Build SQL query
        sql = self._build_sql_query(query_type, location, rank)
        
        return {
            "sql": sql,
            "query_type": query_type,
            "params": {},
            "explanation": f"Đếm số lượng khách sạn" + 
                          (f" ở {location}" if location else "") +
                          (f" {rank} sao" if rank else "")
        }
    
    def _extract_location(self, question: str) -> Optional[str]:
        """Extract location từ câu hỏi"""
        question_lower = question.lower()
        for key, value in self.LOCATIONS.items():
            if key in question_lower:
                return value
        return None
    
    def _extract_rank(self, question: str) -> Optional[int]:
        """Extract rank (sao) từ câu hỏi"""
        question_lower = question.lower()
        rank_patterns = {
            5: ["5 sao", "năm sao", "5 stars"],
            4: ["4 sao", "bốn sao", "4 stars"],
            3: ["3 sao", "ba sao", "3 stars"],
            2: ["2 sao", "hai sao", "2 stars"],
            1: ["1 sao", "một sao", "1 stars"]
        }
        for rank, patterns in rank_patterns.items():
            if any(pattern in question_lower for pattern in patterns):
                return rank
        return None
    
    def _build_sql_query(self, query_type: str, location: Optional[str] = None, 
                        rank: Optional[int] = None) -> str:
        """
        Build SQL query dựa trên query type và filters
        """
        # Base query
        if query_type == "count":
            select_clause = "SELECT COUNT(*) as count"
        elif query_type == "avg":
            select_clause = "SELECT AVG(h.hotel_price_average) as avg_price"
        elif query_type == "max":
            select_clause = "SELECT MAX(h.hotel_price_average) as max_price"
        elif query_type == "min":
            select_clause = "SELECT MIN(h.hotel_price_average) as min_price"
        elif query_type == "exists":
            select_clause = "SELECT COUNT(*) > 0 as exists"
        else:
            select_clause = "SELECT COUNT(*) as count"
        
        # FROM clause
        from_clause = """
        FROM tbl_hotel h
        LEFT JOIN tbl_area a ON h.area_id = a.area_id
        """
        
        # WHERE clause
        where_conditions = ["h.hotel_status = 1"]  # Chỉ lấy hotels active
        
        if location:
            where_conditions.append(f"a.area_name = '{location}'")
        
        if rank:
            where_conditions.append(f"h.hotel_rank = {rank}")
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Combine
        sql = f"{select_clause}\n{from_clause}\n{where_clause}"
        
        return sql
    
    def _generate_with_llm(self, question: str, extracted_info: Dict = None) -> Dict:
        """
        Generate SQL bằng LLM (thông minh hơn, handle complex queries)
        """
        try:
            sql_prompt = """Bạn là hệ thống chuyển đổi câu hỏi tiếng Việt thành SQL query.

Database schema:
- tbl_hotel: hotel_id, hotel_name, hotel_rank, hotel_price_average, area_id, hotel_status
- tbl_area: area_id, area_name
- tbl_brand: brand_id, brand_name

Quy tắc:
1. Chỉ query hotels có hotel_status = 1 (active)
2. JOIN với tbl_area để lấy area_name
3. Sử dụng LEFT JOIN
4. Trả về JSON với format:
{{
    "sql": "SELECT COUNT(*) as count FROM tbl_hotel h LEFT JOIN tbl_area a ON h.area_id = a.area_id WHERE h.hotel_status = 1 AND a.area_name = 'Ngũ Hành Sơn'",
    "query_type": "count",
    "explanation": "Đếm số lượng khách sạn ở Ngũ Hành Sơn"
}}

Câu hỏi: {question}

CHỈ trả về JSON, không có text khác."""

            prompt = sql_prompt.format(question=question)
            
            # Call LLM
            if hasattr(self.llm, 'invoke'):
                try:
                    from langchain.schema import HumanMessage
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    response_text = response.content if hasattr(response, 'content') else str(response)
                except:
                    response_text = self.llm.invoke(prompt)
            elif hasattr(self.llm, 'predict'):
                response_text = self.llm.predict(prompt)
            else:
                response_text = str(self.llm.invoke(prompt))
            
            # Parse JSON
            import json
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            result = json.loads(response_text)
            
            # Validate
            if not isinstance(result, dict) or "sql" not in result:
                logger.warning("LLM returned invalid format, falling back to rule-based")
                return self._generate_rule_based(question, extracted_info)
            
            return {
                "sql": result["sql"],
                "query_type": result.get("query_type", "count"),
                "params": {},
                "explanation": result.get("explanation", "SQL query generated by LLM")
            }
            
        except Exception as e:
            logger.warning(f"LLM SQL generation failed: {e}, falling back to rule-based")
            return self._generate_rule_based(question, extracted_info)

