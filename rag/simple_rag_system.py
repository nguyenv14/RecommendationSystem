#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple RAG System cho Hotel Recommendation
Sử dụng LangChain + Ollama + Qdrant
"""

import pandas as pd
import os
import json
from typing import List, Dict, Optional
import logging
from pathlib import Path

from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from qdrant_client import QdrantClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleRAGSystem:
    """Simple RAG System cho Hotel Recommendation"""
    
    def __init__(self,
                 ollama_url="http://localhost:11434",
                 qdrant_url="http://localhost:6333",
                 embedding_model="bge-m3",
                 llm_model="qwen3",
                 collection_name="hotels"):
        """
        Initialize RAG System
        
        Args:
            ollama_url: Ollama server URL
            qdrant_url: Qdrant server URL
            embedding_model: Embedding model name
            llm_model: LLM model name
            collection_name: Qdrant collection name
        """
        self.ollama_url = ollama_url
        self.qdrant_url = qdrant_url
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.collection_name = collection_name
        
        # Initialize embeddings
        logger.info(f"Initializing embeddings: {embedding_model}")
        self.embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_url
        )
        
        # Initialize LLM
        logger.info(f"Initializing LLM: {llm_model}")
        # Lower temperature for more consistent Vietnamese responses
        self.llm = Ollama(
            model=llm_model,
            base_url=ollama_url,
            temperature=0.3  # Lower temperature for more focused responses
        )
        
        # Vector store (will be initialized after indexing)
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None
    
    def index_hotels(self, normalized_data_path: str = "rag/normalized_data/normalized_hotels.csv", 
                     recreate_collection: bool = False):
        """
        Index hotels vào Qdrant từ normalized data
        
        Args:
            normalized_data_path: Path to normalized_hotels.csv
            recreate_collection: If True, recreate collection
        """
        logger.info(f"Loading normalized data from: {normalized_data_path}")
        
        # Get absolute path
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        data_path = project_root / normalized_data_path
        
        # Load normalized data
        normalized_df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(normalized_df)} hotels")
        
        # Create documents
        documents = []
        for idx, hotel in normalized_df.iterrows():
            hotel_id = int(hotel["hotel_id"])
            
            # Use semantic_text for embedding
            semantic_text = hotel.get("semantic_text", "")
            
            if pd.isna(semantic_text) or not semantic_text.strip():
                logger.warning(f"Hotel {hotel_id} has no semantic_text, skipping")
                continue
            
            # Truncate text if too long (to avoid Ollama timeout)
            # Keep first 1500 characters to preserve main semantic meaning
            max_text_length = 1500
            if len(semantic_text) > max_text_length:
                logger.debug(f"Truncating hotel {hotel_id} text from {len(semantic_text)} to {max_text_length} chars")
                semantic_text = semantic_text[:max_text_length] + "..."
            
            # Create document
            doc = Document(
                page_content=semantic_text,
                metadata={
                    "hotel_id": hotel_id,
                    "hotel_name": str(hotel.get("hotel_name", "")),
                    "hotel_rank": int(hotel.get("hotel_rank", 0)) if pd.notna(hotel.get("hotel_rank")) else None,
                    "hotel_price_average": float(hotel.get("hotel_price_average", 0)) if pd.notna(hotel.get("hotel_price_average")) else None,
                    "area_name": str(hotel.get("area_name", "")) if pd.notna(hotel.get("area_name")) else "",
                    "brand_name": str(hotel.get("brand_name", "")) if pd.notna(hotel.get("brand_name")) else "",
                    "price_category": str(hotel.get("price_category", "")) if pd.notna(hotel.get("price_category")) else "",
                    "normalized_name": str(hotel.get("normalized_name", "")) if pd.notna(hotel.get("normalized_name")) else ""
                }
            )
            documents.append(doc)
        
        logger.info(f"Created {len(documents)} documents")
        
        # Store in Qdrant with batch processing to avoid timeout
        logger.info(f"Storing {len(documents)} documents in Qdrant collection: {self.collection_name}")
        
        # Create collection first if not exists
        from qdrant_client.models import Distance, VectorParams
        client = QdrantClient(url=self.qdrant_url)
        
        try:
            # Get embedding dimension by testing with first document
            test_embedding = self.embeddings.embed_query(documents[0].page_content)
            vector_size = len(test_embedding)
            
            # Check if collection exists
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            # Delete collection if recreate is requested
            if recreate_collection and self.collection_name in collection_names:
                logger.info(f"Deleting existing collection: {self.collection_name}")
                client.delete_collection(collection_name=self.collection_name)
                # Refresh collection list after deletion
                collections = client.get_collections()
                collection_names = [col.name for col in collections.collections]
            
            # Create collection if it doesn't exist
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection '{self.collection_name}' with vector size {vector_size}")
                client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' created successfully")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
            
            # Initialize vectorstore
            self.vectorstore = Qdrant(
                client=client,
                collection_name=self.collection_name,
                embeddings=self.embeddings
            )
            
            # Add documents in small batches to avoid timeout
            batch_size = 1  # Process one hotel at a time
            import time
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1} ({len(batch)} documents)")
                
                # Retry logic for Ollama timeout
                max_retries = 3
                retry_delay = 2  # seconds
                
                for retry in range(max_retries):
                    try:
                        self.vectorstore.add_texts(
                            texts=[doc.page_content for doc in batch],
                            metadatas=[doc.metadata for doc in batch],
                            ids=[doc.metadata.get("hotel_id", i+j) for j, doc in enumerate(batch)]
                        )
                        break  # Success, exit retry loop
                    except Exception as e:
                        if retry < max_retries - 1:
                            logger.warning(f"Error processing batch {i//batch_size + 1} (attempt {retry+1}/{max_retries}): {e}")
                            logger.info(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"Error processing batch {i//batch_size + 1} after {max_retries} attempts: {e}")
                            raise
                
                # Small delay between batches to avoid overwhelming Ollama
                if i < len(documents) - batch_size:
                    time.sleep(0.5)
            
            logger.info(f"Successfully stored {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Error storing documents: {e}")
            raise
        
        # Create retriever from vectorstore
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}  # Top 5 results
        )
        
        # Create QA chain
        prompt_template = """
Bạn là trợ lý tư vấn khách sạn chuyên nghiệp tại Đà Nẵng. QUAN TRỌNG: Bạn PHẢI trả lời HOÀN TOÀN bằng tiếng Việt, KHÔNG được sử dụng tiếng Anh trong câu trả lời.

Dựa trên thông tin sau về các khách sạn, hãy trả lời câu hỏi của người dùng một cách tự nhiên và hữu ích BẰNG TIẾNG VIỆT.

Context:
{context}

Câu hỏi: {question}

YÊU CẦU TRẢ LỜI (QUAN TRỌNG):
1. TRẢ LỜI HOÀN TOÀN BẰNG TIẾNG VIỆT - KHÔNG SỬ DỤNG TIẾNG ANH
2. Trả lời tự nhiên, dễ hiểu, chuyên nghiệp
3. Nêu tên khách sạn, địa chỉ, giá nếu có trong context
4. Nếu không có thông tin phù hợp, hãy nói rõ "Tôi không tìm thấy khách sạn phù hợp với yêu cầu của bạn."
5. Nếu có nhiều khách sạn, hãy liệt kê top 3-5 khách sạn phù hợp nhất với thông tin chi tiết

LƯU Ý: Chỉ trả lời bằng tiếng Việt, không dịch ra tiếng Anh, không sử dụng từ tiếng Anh.

Trả lời (bằng tiếng Việt):
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        logger.info("RAG system initialized successfully!")
    
    def search_hotels(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search hotels by query (semantic search only)
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of hotel results
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call index_hotels first.")
        
        logger.info(f"Searching for: '{query}'")
        
        # Semantic search
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=top_k
        )
        
        # Format results
        hotels = []
        for doc, score in results:
            hotels.append({
                "hotel_id": doc.metadata.get("hotel_id"),
                "hotel_name": doc.metadata.get("hotel_name", ""),
                "hotel_rank": doc.metadata.get("hotel_rank"),
                "hotel_price_average": doc.metadata.get("hotel_price_average"),
                "area_name": doc.metadata.get("area_name", ""),
                "brand_name": doc.metadata.get("brand_name", ""),
                "price_category": doc.metadata.get("price_category", ""),
                "similarity_score": float(score),
                "text_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        return hotels
    
    def ask(self, question: str) -> Dict:
        """
        Ask question với RAG (Retrieval + Generation)
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and sources
        """
        if self.qa_chain is None:
            raise ValueError("QA chain not initialized. Call index_hotels first.")
        
        logger.info(f"Question: '{question}'")
        
        # Get answer with RAG
        result = self.qa_chain({"query": question})
        
        # Format response
        response = {
            "question": question,
            "answer": result["result"],
            "sources": []
        }
        
        # Add source documents
        for doc in result.get("source_documents", []):
            response["sources"].append({
                "hotel_id": doc.metadata.get("hotel_id"),
                "hotel_name": doc.metadata.get("hotel_name", ""),
                "hotel_rank": doc.metadata.get("hotel_rank"),
                "hotel_price_average": doc.metadata.get("hotel_price_average"),
                "area_name": doc.metadata.get("area_name", ""),
                "text_preview": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            })
        
        return response
    
    def load_vectorstore(self):
        """Load existing vectorstore from Qdrant"""
        logger.info(f"Loading vectorstore from Qdrant: {self.collection_name}")
        
        # Create Qdrant client
        client = QdrantClient(url=self.qdrant_url)
        
        # Check if collection exists
        try:
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                raise ValueError(
                    f"Collection '{self.collection_name}' does not exist in Qdrant. "
                    f"Please run index_hotels() first."
                )
            
            logger.info(f"Collection '{self.collection_name}' exists")
        except Exception as e:
            logger.error(f"Error checking collection: {e}")
            raise
        
        # Load existing vectorstore
        self.vectorstore = Qdrant(
            client=client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )
        
        # Create retriever from vectorstore
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )
        
        # Create QA chain
        prompt_template = """
Bạn là trợ lý tư vấn khách sạn chuyên nghiệp tại Đà Nẵng. QUAN TRỌNG: Bạn PHẢI trả lời HOÀN TOÀN bằng tiếng Việt, KHÔNG được sử dụng tiếng Anh trong câu trả lời.

Dựa trên thông tin sau về các khách sạn, hãy trả lời câu hỏi của người dùng một cách tự nhiên và hữu ích BẰNG TIẾNG VIỆT.

Context:
{context}

Câu hỏi: {question}

YÊU CẦU TRẢ LỜI (QUAN TRỌNG):
1. TRẢ LỜI HOÀN TOÀN BẰNG TIẾNG VIỆT - KHÔNG SỬ DỤNG TIẾNG ANH
2. Trả lời tự nhiên, dễ hiểu, chuyên nghiệp
3. Nêu tên khách sạn, địa chỉ, giá nếu có trong context
4. Nếu không có thông tin phù hợp, hãy nói rõ "Tôi không tìm thấy khách sạn phù hợp với yêu cầu của bạn."
5. Nếu có nhiều khách sạn, hãy liệt kê top 3-5 khách sạn phù hợp nhất với thông tin chi tiết

LƯU Ý: Chỉ trả lời bằng tiếng Việt, không dịch ra tiếng Anh, không sử dụng từ tiếng Anh.

Trả lời (bằng tiếng Việt):
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        logger.info("Vectorstore loaded successfully!")


def main():
    """Main function - Demo RAG system"""
    
    print("🚀 Initializing Simple RAG System...")
    
    # Initialize RAG system
    rag = SimpleRAGSystem(
        ollama_url="http://localhost:11434",
        qdrant_url="http://localhost:6333",
        embedding_model="bge-m3",
        llm_model="qwen3"  # qwen3 hỗ trợ tiếng Việt rất tốt
    )
    
    # Index hotels
    print("\n📦 Indexing hotels...")
    rag.index_hotels(
        normalized_data_path="rag/normalized_data/normalized_hotels.csv",
        recreate_collection=True
    )
    
    # Test semantic search
    print("\n🔍 Testing Semantic Search:")
    print("=" * 60)
    
    test_queries = [
        "Khách sạn 5 sao gần biển Đà Nẵng",
        "Khách sạn giá rẻ ở Sơn Trà",
        "Khách sạn luxury có spa"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag.search_hotels(query, top_k=3)
        
        for idx, hotel in enumerate(results, 1):
            print(f"\n{idx}. {hotel['hotel_name']}")
            print(f"   Hotel ID: {hotel['hotel_id']}")
            print(f"   Rank: {hotel['hotel_rank']} sao")
            print(f"   Price: {hotel['hotel_price_average']:,.0f} VND" if hotel['hotel_price_average'] else "   Price: N/A")
            print(f"   Area: {hotel['area_name']}")
            print(f"   Similarity: {hotel['similarity_score']:.3f}")
    
    # Test RAG (with LLM)
    print("\n\n💬 Testing RAG (with LLM):")
    print("=" * 60)
    
    test_questions = [
        "Khách sạn nào 5 sao gần biển Đà Nẵng?",
        "Tôi muốn tìm khách sạn giá rẻ ở Sơn Trà",
        "Khách sạn nào có spa và hồ bơi?"
    ]
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        response = rag.ask(question)
        
        print(f"\n💡 Answer:")
        print(response["answer"])
        
        print(f"\n📚 Sources ({len(response['sources'])} hotels):")
        for idx, source in enumerate(response["sources"][:3], 1):
            print(f"  {idx}. {source['hotel_name']} (ID: {source['hotel_id']})")
    
    print("\n✅ RAG System Demo Complete!")


if __name__ == "__main__":
    main()

