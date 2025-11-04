#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script for RAG system
"""

from simple_rag_system import SimpleRAGSystem

def main():
    print("🚀 Testing Simple RAG System...\n")
    
    # Initialize RAG
    rag = SimpleRAGSystem(
        ollama_url="http://localhost:11434",
        qdrant_url="http://localhost:6333",
        embedding_model="bge-m3",
        llm_model="llama2"
    )
    
    # Check if already indexed
    try:
        rag.load_vectorstore()
        print("✅ Loaded existing vectorstore")
    except Exception as e:
        print(f"⚠️  Cannot load existing vectorstore: {e}")
        print("📦 Indexing hotels...")
        try:
            rag.index_hotels(
                normalized_data_path="rag/normalized_data/normalized_hotels.csv",
                recreate_collection=False
            )
        except Exception as e2:
            print(f"❌ Error indexing: {e2}")
            print("\n💡 Tip: Check if:")
            print("   - Ollama is running: curl http://localhost:11434/api/tags")
            print("   - Model bge-m3 is available: ollama list")
            print("   - If not, pull model: ollama pull bge-m3")
            raise
    
    # Test search
    print("\n" + "="*60)
    print("🔍 Test 1: Semantic Search")
    print("="*60)
    
    query = "Khách sạn 5 sao gần biển Đà Nẵng"
    print(f"\nQuery: '{query}'\n")
    
    results = rag.search_hotels(query, top_k=3)
    
    for idx, hotel in enumerate(results, 1):
        print(f"{idx}. {hotel['hotel_name']}")
        print(f"   ID: {hotel['hotel_id']} | Rank: {hotel['hotel_rank']} sao")
        print(f"   Price: {hotel['hotel_price_average']:,.0f} VND" if hotel['hotel_price_average'] else "   Price: N/A")
        print(f"   Area: {hotel['area_name']}")
        print(f"   Similarity: {hotel['similarity_score']:.3f}\n")
    
    # Test RAG
    print("\n" + "="*60)
    print("💬 Test 2: RAG (with LLM)")
    print("="*60)
    
    question = "Khách sạn nào 5 sao gần biển Đà Nẵng?"
    print(f"\nQuestion: {question}\n")
    
    response = rag.ask(question)
    
    print("Answer:")
    print(response["answer"])
    
    print(f"\nSources ({len(response['sources'])} hotels):")
    for idx, source in enumerate(response["sources"], 1):
        print(f"  {idx}. {source['hotel_name']} (ID: {source['hotel_id']})")

if __name__ == "__main__":
    main()

