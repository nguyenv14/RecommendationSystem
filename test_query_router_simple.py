#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test cho QueryRouter
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rag.core.query_router import QueryRouter
    print("✅ Import QueryRouter thành công!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def main():
    print("=" * 80)
    print("🧪 Testing QueryRouter (Rule-based only)")
    print("=" * 80)
    
    # Initialize router (không cần LLM)
    router = QueryRouter(use_llm=False, llm=None)
    
    # Test cases
    test_cases = [
        ("Có bao nhiêu khách sạn trong khu vực Ngũ Hành Sơn?", "statistical"),
        ("Khách sạn nào có view biển đẹp?", "semantic"),
        ("Có bao nhiêu khách sạn 5 sao có hồ bơi?", "hybrid"),
    ]
    
    print("\n📋 Test Results:\n")
    
    for question, expected_type in test_cases:
        result = router.classify_query(question)
        
        status = "✅" if result["type"] == expected_type else "⚠️"
        type_emoji = {
            "statistical": "📊",
            "semantic": "🔍",
            "hybrid": "🔀"
        }.get(result["type"], "❓")
        
        print(f"{status} {type_emoji} {result['type'].upper()} (expected: {expected_type})")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Q: {question}")
        print(f"   Reason: {result.get('reason', 'N/A')}")
        print()
    
    print("=" * 80)
    print("✅ Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()

