#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Store Hotel Chunks in Qdrant with LangChain
"""

import pandas as pd
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import OllamaEmbeddings
from langchain.schema import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HotelChunkStorage:
    """Store hotel chunks in Qdrant using LangChain"""
    
    def __init__(self, 
                 ollama_url="http://localhost:11434",
                 qdrant_url="http://localhost:6333",
                 embedding_model="bge-m3",
                 collection_name="hotels"):
        """
        Initialize Hotel Chunk Storage
        
        Args:
            ollama_url: Ollama server URL
            qdrant_url: Qdrant server URL
            embedding_model: Embedding model name
            collection_name: Qdrant collection name
        """
        self.ollama_url = ollama_url
        self.qdrant_url = qdrant_url
        self.embedding_model = embedding_model
        self.collection_name = collection_name
        
        # Initialize embeddings
        logger.info(f"Initializing embeddings: {embedding_model}")
        self.embeddings = OllamaEmbeddings(
            model=embedding_model,
            base_url=ollama_url
        )
        
        # Initialize Qdrant client
        self.client = QdrantClient(url=qdrant_url)
        
        # Vector store (will be created after loading documents)
        self.vectorstore = None
    
    def load_data(self, data_dir="datasets_extracted"):
        """Load hotel data from CSV files"""
        logger.info("Loading data from CSV files...")
        
        # Load main tables
        hotels_df = pd.read_csv(f"{data_dir}/tbl_hotel.csv")
        areas_df = pd.read_csv(f"{data_dir}/tbl_area.csv")
        brands_df = pd.read_csv(f"{data_dir}/tbl_brand.csv")
        
        # Join tables
        hotels_df = hotels_df.merge(
            areas_df[["area_id", "area_name", "area_desc"]], 
            on="area_id", 
            how="left"
        )
        hotels_df = hotels_df.merge(
            brands_df[["brand_id", "brand_name", "brand_desc"]], 
            on="brand_id", 
            how="left"
        )
        
        logger.info(f"Loaded {len(hotels_df)} hotels")
        return hotels_df
    
    def create_documents(self, hotels_df):
        """
        Create LangChain documents from hotels dataframe
        
        Strategy: 1 hotel = 1 document (chunk)
        """
        logger.info("Creating documents from hotels...")
        
        documents = []
        
        for idx, hotel in hotels_df.iterrows():
            hotel_id = hotel["hotel_id"]
            
            # Combine text parts
            text_parts = []
            
            # Hotel name
            if pd.notna(hotel.get("hotel_name")):
                text_parts.append(f"Tên khách sạn: {hotel['hotel_name']}")
            
            # Description
            if pd.notna(hotel.get("hotel_desc")):
                desc = str(hotel["hotel_desc"]).strip()
                if desc:
                    text_parts.append(f"Mô tả: {desc}")
            
            # Address
            if pd.notna(hotel.get("hotel_placedetails")):
                text_parts.append(f"Địa chỉ: {hotel['hotel_placedetails']}")
            
            # Area
            if pd.notna(hotel.get("area_name")):
                text_parts.append(f"Khu vực: {hotel['area_name']}")
            
            # Brand
            if pd.notna(hotel.get("brand_name")):
                text_parts.append(f"Thương hiệu: {hotel['brand_name']}")
            
            # Keywords
            if pd.notna(hotel.get("hotel_tag_keyword")):
                text_parts.append(f"Từ khóa: {hotel['hotel_tag_keyword']}")
            
            # Rank
            if pd.notna(hotel.get("hotel_rank")):
                text_parts.append(f"Hạng: {hotel['hotel_rank']} sao")
            
            # Price
            if pd.notna(hotel.get("hotel_price_average")):
                price = int(hotel["hotel_price_average"])
                text_parts.append(f"Giá trung bình: {price:,} VND")
            
            # Combine all text
            text = " | ".join(text_parts)
            
            # Skip if text is empty
            if not text.strip():
                logger.warning(f"Hotel {hotel_id} has no text, skipping")
                continue
            
            # Create metadata
            metadata = {
                "hotel_id": int(hotel_id),
                "hotel_name": str(hotel.get("hotel_name", "")),
                "area_id": int(hotel["area_id"]) if pd.notna(hotel.get("area_id")) else None,
                "area_name": str(hotel.get("area_name", "")) if pd.notna(hotel.get("area_name")) else "",
                "brand_id": int(hotel["brand_id"]) if pd.notna(hotel.get("brand_id")) else None,
                "brand_name": str(hotel.get("brand_name", "")) if pd.notna(hotel.get("brand_name")) else "",
                "hotel_rank": int(hotel["hotel_rank"]) if pd.notna(hotel.get("hotel_rank")) else None,
                "hotel_price_average": float(hotel["hotel_price_average"]) if pd.notna(hotel.get("hotel_price_average")) else None,
                "chunk_type": "full_hotel",
                "chunk_index": 0,
                "source": "tbl_hotel.csv"
            }
            
            # Create document
            doc = Document(
                page_content=text,
                metadata=metadata
            )
            documents.append(doc)
            
            if (idx + 1) % 10 == 0:
                logger.info(f"Created {idx + 1}/{len(hotels_df)} documents")
        
        logger.info(f"Created {len(documents)} documents")
        return documents
    
    def store_documents(self, documents, recreate_collection=False):
        """
        Store documents in Qdrant
        
        Args:
            documents: List of LangChain documents
            recreate_collection: If True, delete existing collection first
        """
        logger.info(f"Storing {len(documents)} documents in Qdrant...")
        
        # Check if collection exists
        collections = self.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if recreate_collection and self.collection_name in collection_names:
            logger.info(f"Deleting existing collection: {self.collection_name}")
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' deleted")
        
        # Create vector store
        try:
            self.vectorstore = Qdrant.from_documents(
                documents=documents,
                embedding=self.embeddings,
                url=self.qdrant_url,
                collection_name=self.collection_name,
                prefer_grpc=True
            )
            logger.info(f"Successfully stored {len(documents)} documents in Qdrant")
            
            # Verify
            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"Collection info: {collection_info.points_count} points stored")
            
        except Exception as e:
            logger.error(f"Error storing documents: {e}")
            raise
    
    def search(self, query, top_k=10, filter_metadata=None):
        """
        Search hotels by query
        
        Args:
            query: Search query text
            top_k: Number of results
            filter_metadata: Optional metadata filter (dict)
            
        Returns:
            List of search results
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call store_documents first.")
        
        logger.info(f"Searching for: '{query}'")
        
        # Search
        if filter_metadata:
            # TODO: Implement metadata filtering
            results = self.vectorstore.similarity_search(
                query,
                k=top_k
            )
        else:
            results = self.vectorstore.similarity_search(
                query,
                k=top_k
            )
        
        return results
    
    def get_collection_info(self):
        """Get information about the collection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.config.params.vectors.size if hasattr(collection_info.config.params.vectors, 'size') else None
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None


def main():
    """Main function"""
    
    # Initialize storage
    storage = HotelChunkStorage(
        ollama_url="http://localhost:11434",
        qdrant_url="http://localhost:6333",
        embedding_model="bge-m3",
        collection_name="hotels"
    )
    
    # Load data
    hotels_df = storage.load_data(data_dir="../datasets_extracted")
    
    # Create documents
    documents = storage.create_documents(hotels_df)
    
    # Store in Qdrant
    storage.store_documents(documents, recreate_collection=True)
    
    # Get collection info
    info = storage.get_collection_info()
    print("\n=== Collection Info ===")
    print(f"Collection: {info['collection_name']}")
    print(f"Points: {info['points_count']}")
    print(f"Vector size: {info['vectors_count']}")
    
    # Test search
    print("\n=== Test Search ===")
    query = "Khách sạn 5 sao gần biển Đà Nẵng"
    results = storage.search(query, top_k=5)
    
    print(f"\nQuery: '{query}'")
    print(f"Found {len(results)} results:\n")
    
    for idx, result in enumerate(results, 1):
        print(f"{idx}. {result.metadata.get('hotel_name', 'N/A')}")
        print(f"   Hotel ID: {result.metadata.get('hotel_id', 'N/A')}")
        print(f"   Rank: {result.metadata.get('hotel_rank', 'N/A')} sao")
        print(f"   Price: {result.metadata.get('hotel_price_average', 'N/A'):,.0f} VND" if result.metadata.get('hotel_price_average') else "   Price: N/A")
        print(f"   Area: {result.metadata.get('area_name', 'N/A')}")
        print(f"   Text preview: {result.page_content[:100]}...")
        print()


if __name__ == "__main__":
    main()

