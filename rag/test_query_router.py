#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho QueryRouter
"""

import sys
from pathlib import Path

# Add paths
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(current_dir))

# Try different import paths
try:
    from rag.core.query_router import QueryRouter
except ImportError:
    try:
        from core.query_router import QueryRouter
    except ImportError:
        # Direct import if running from rag directory
        from query_router import QueryRouter

def test_query_router():
    """Test QueryRouter với các câu hỏi mẫu"""
    
    print("=" * 80)
    print("🧪 Testing QueryRouter")
    print("=" * 80)
    
    # Initialize router (không cần LLM cho test rule-based)
    router = QueryRouter(use_llm=False, llm=None)
    
    # Test cases
    test_questions = [
        # Statistical queries
        "Có bao nhiêu khách sạn trong khu vực Ngũ Hành Sơn?",
        "Tổng số khách sạn 5 sao là bao nhiêu?",
        "Giá trung bình của khách sạn là bao nhiêu?",
        "Có khách sạn nào ở Sơn Trà không?",
        
        # Semantic queries
        "Khách sạn nào có view biển đẹp?",
        "Tìm khách sạn 5 sao có spa",
        "Giới thiệu khách sạn ở Đà Nẵng",
        "Khách sạn nào có hồ bơi?",
        
        # Hybrid queries
        "Có bao nhiêu khách sạn 5 sao có hồ bơi?",
        "Tổng số khách sạn có view biển là bao nhiêu?",
        
        # Ambiguous queries
        "Khách sạn",
        "Đà Nẵng",
    ]
    
    print("\n📋 Test Results:\n")
    
    for i, question in enumerate(test_questions, 1):
        result = router.classify_query(question)
        
        type_emoji = {
            "statistical": "📊",
            "semantic": "🔍",
            "hybrid": "🔀"
        }.get(result["type"], "❓")
        
        method_emoji = "🤖" if result.get("method") == "llm" else "⚙️"
        
        print(f"{i}. {type_emoji} {result['type'].upper()} (confidence: {result['confidence']:.2f}) {method_emoji}")
        print(f"   Q: {question}")
        print(f"   Reason: {result.get('reason', 'N/A')}")
        print()
    
    print("=" * 80)
    print("✅ Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    test_query_router()

