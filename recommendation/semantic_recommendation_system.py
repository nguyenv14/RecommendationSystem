#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Recommendation System using Embeddings and Qdrant Vector DB
"""

import pandas as pd
import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import json
import os
from typing import List, Dict, Tuple
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticRecommendationSystem:
    def __init__(self, model_name='paraphrase-multilingual-MiniLM-L12-v2', 
                 device=None, qdrant_url='http://localhost:6333',
                 use_ollama=False, ollama_url='http://localhost:11434'):
        """
        Initialize the Semantic Recommendation System
        
        Args:
            model_name: SentenceTransformer model (default: multilingual)
            device: 'cuda' for GPU, 'cpu' for CPU. Auto-detect if None
            qdrant_url: Qdrant server URL
            use_ollama: Use Ollama for embeddings (default: False)
            ollama_url: Ollama server URL
        """
        self.use_ollama = use_ollama
        self.ollama_url = ollama_url
        
        # Auto-detect device
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.device = device
        self.model_name = model_name
        
        logger.info(f"Loading model: {model_name}")
        logger.info(f"Using device: {device}")
        logger.info(f"Using Ollama: {use_ollama}")
        
        # Load embedding model
        if not use_ollama:
            logger.info("Initializing SentenceTransformer model...")
            self.model = SentenceTransformer(model_name, device=device)
            self.is_bge = True
            self.tokenizer = None
            self.transformer_model = None
        else:
            self.model = None
            
        # Qdrant client
        self.qdrant_url = qdrant_url
        self.client = QdrantClient(url=qdrant_url)
        
        # Collection name
        self.collection_name = "hotel_recommendations"
        
        # Cache for embeddings
        self.embedding_cache = {}
    
    def preprocess_description(self, description: str, chunk_size: int = 512) -> List[str]:
        """
        Chunk long descriptions into smaller pieces
        
        Args:
            description: Hotel description text
            chunk_size: Maximum number of characters per chunk
            
        Returns:
            List of description chunks
        """
        if pd.isna(description) or description == '':
            return ['']
        
        # If description is short, return as is
        if len(description) <= chunk_size:
            return [description]
        
        # Split into chunks by sentences or fixed size
        chunks = []
        words = description.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks if chunks else [description]
    
    def _create_embeddings_ollama(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings using Ollama API with caching
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        embeddings = []
        
        for text in texts:
            # Check cache first
            text_key = text[:100]  # Use first 100 chars as key
            if text_key in self.embedding_cache:
                embeddings.append(self.embedding_cache[text_key])
                continue
                
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": "bge-m3",
                        "prompt": text
                    },
                    timeout=60
                )
                response.raise_for_status()
                result = response.json()
                embedding = np.array(result['embedding'])
                embeddings.append(embedding)
                
                # Cache the embedding
                self.embedding_cache[text_key] = embedding
                
            except Exception as e:
                logger.error(f"Error creating embedding: {e}")
                # Return zero vector as fallback
                fallback_emb = np.array([0.0] * 1024)
                embeddings.append(fallback_emb)
                self.embedding_cache[text_key] = fallback_emb
        
        embeddings = np.array(embeddings)
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms = np.where(norms > 0, norms, 1.0)
        embeddings = embeddings / norms
        
        return embeddings
    
    def create_embeddings(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        """
        Create embeddings for text
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing (smaller for BGE-M3)
            
        Returns:
            Numpy array of embeddings
        """
        logger.info(f"Creating embeddings for {len(texts)} texts...")
        
        if self.use_ollama:
            logger.info("Using Ollama for embeddings...")
            return self._create_embeddings_ollama(texts)
        else:
            # BGE-M3 specific settings
            embeddings = self.model.encode(
                texts, 
                batch_size=batch_size, 
                show_progress_bar=True,
                normalize_embeddings=True,  # Normalize embeddings for better cosine similarity
                convert_to_numpy=True
            )
            logger.info(f"Created embeddings shape: {embeddings.shape}")
            return embeddings
    
    def create_qdrant_collection(self, vector_size: int = 1024, recreate: bool = False):
        """
        Create Qdrant collection if it doesn't exist
        
        Args:
            vector_size: Dimension of embedding vectors
            recreate: If True, delete existing collection and create new one
        """
        collections = self.client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        # Delete existing collection if recreate is True
        if recreate and self.collection_name in collection_names:
            logger.info(f"Deleting existing collection: {self.collection_name}")
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Collection '{self.collection_name}' deleted")
        
        if recreate or self.collection_name not in collection_names:
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection '{self.collection_name}' created")
        else:
            logger.info(f"Collection '{self.collection_name}' already exists")
    
    def index_hotels(self, hotels_df: pd.DataFrame, recreate_collection: bool = True):
        """
        Index all hotels to Qdrant with single vector per hotel
        
        Args:
            hotels_df: DataFrame containing hotel information
            recreate_collection: If True, delete existing collection and create new one
        """
        logger.info("Starting hotel indexing process...")
        
        # Create single vector per hotel
        hotel_texts = []
        hotel_metadata = []
        
        for idx, hotel in hotels_df.iterrows():
            hotel_id = hotel['hotel_id']
            
            # Combine multiple fields into description
            description_parts = []
            
            if pd.notna(hotel.get('hotel_name')):
                description_parts.append(f"Tên khách sạn: {hotel['hotel_name']}")
            
            if pd.notna(hotel.get('hotel_desc')):
                description_parts.append(str(hotel['hotel_desc']))
            
            if pd.notna(hotel.get('hotel_placedetails')):
                description_parts.append(f"Địa chỉ: {hotel['hotel_placedetails']}")
            
            if pd.notna(hotel.get('hotel_tag_keyword')):
                description_parts.append(f"Từ khóa: {hotel['hotel_tag_keyword']}")
            
            full_description = ' '.join(description_parts)
            
            # Fallback: nếu không có mô tả, dùng tên hoặc ID
            if not full_description or full_description.strip() == '':
                full_description = f"Khách sạn ID {hotel_id}"
                if pd.notna(hotel.get('hotel_name')):
                    full_description = str(hotel['hotel_name'])
                logger.warning(f"Hotel {hotel_id} has no description, using: {full_description}")
            
            # Use full description as single text (limit to model max length)
            if len(full_description) > 512:
                full_description = full_description[:512]
            
            hotel_texts.append(full_description)
            hotel_metadata.append({
                'hotel_id': hotel_id,
                'hotel_name': hotel.get('hotel_name', f'Hotel {hotel_id}'),
                'hotel_rank': hotel.get('hotel_rank', 0),
                'hotel_price_average': hotel.get('hotel_price_average', 0)
            })
        
        # Create embeddings
        embeddings = self.create_embeddings(hotel_texts)
        vector_size = embeddings.shape[1]
        
        # Create collection
        self.create_qdrant_collection(vector_size=vector_size, recreate=recreate_collection)
        
        # Prepare points for Qdrant - one point per hotel
        points = []
        for idx, (embedding, metadata) in enumerate(zip(embeddings, hotel_metadata)):
            # Validate embedding
            if embedding is None or len(embedding) == 0:
                logger.error(f"Hotel {metadata['hotel_id']} has invalid embedding, skipping")
                continue
            
            # Ensure embedding is numeric
            try:
                embedding_list = embedding.tolist()
                # Check for any NaN or inf values
                if not all(np.isfinite(embedding_list)):
                    logger.error(f"Hotel {metadata['hotel_id']} has NaN or inf values in embedding")
                    continue
            except Exception as e:
                logger.error(f"Error processing embedding for hotel {metadata['hotel_id']}: {e}")
                continue
            
            points.append(
                PointStruct(
                    id=metadata['hotel_id'],  # Use hotel_id as point id
                    vector=embedding_list,
                    payload=metadata
                )
            )
        
        # Upload to Qdrant
        logger.info(f"Uploading {len(points)} points to Qdrant...")
        
        if len(points) == 0:
            logger.error("No valid points to upload")
            return
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        # Verify upload
        info = self.client.get_collection(self.collection_name)
        logger.info(f"Uploaded {info.points_count} points successfully")
        logger.info("Hotel indexing completed successfully!")
    
    def add_new_hotels(self, new_hotels_df: pd.DataFrame):
        """
        Add new hotels to existing collection without recreating (incremental update)
        
        Args:
            new_hotels_df: DataFrame containing new hotel information
        """
        logger.info(f"Adding {len(new_hotels_df)} new hotels to existing collection...")
        
        # Check which hotels are actually new
        all_ids = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000
        )[0]
        
        existing_ids = {point.payload['hotel_id'] for point in all_ids}
        new_hotels = new_hotels_df[~new_hotels_df['hotel_id'].isin(existing_ids)]
        
        if len(new_hotels) == 0:
            logger.info("No new hotels to add")
            return
        
        logger.info(f"Found {len(new_hotels)} new hotels to add")
        
        # Create texts for new hotels only
        hotel_texts = []
        hotel_metadata = []
        
        for idx, hotel in new_hotels.iterrows():
            hotel_id = hotel['hotel_id']
            
            description_parts = []
            if pd.notna(hotel.get('hotel_name')):
                description_parts.append(f"Tên khách sạn: {hotel['hotel_name']}")
            if pd.notna(hotel.get('hotel_desc')):
                description_parts.append(str(hotel['hotel_desc']))
            if pd.notna(hotel.get('hotel_placedetails')):
                description_parts.append(f"Địa chỉ: {hotel['hotel_placedetails']}")
            if pd.notna(hotel.get('hotel_tag_keyword')):
                description_parts.append(f"Từ khóa: {hotel['hotel_tag_keyword']}")
            
            full_description = ' '.join(description_parts) if description_parts else f"Khách sạn ID {hotel_id}"
            if len(full_description) > 512:
                full_description = full_description[:512]
            
            hotel_texts.append(full_description)
            hotel_metadata.append({
                'hotel_id': hotel_id,
                'hotel_name': hotel.get('hotel_name', f'Hotel {hotel_id}'),
                'hotel_rank': hotel.get('hotel_rank', 0),
                'hotel_price_average': hotel.get('hotel_price_average', 0)
            })
        
        # Create embeddings for new hotels
        logger.info(f"Creating embeddings for {len(hotel_texts)} new hotels...")
        embeddings = self.create_embeddings(hotel_texts)
        
        # Prepare points
        points = []
        for embedding, metadata in zip(embeddings, hotel_metadata):
            try:
                embedding_list = embedding.tolist()
                if not all(np.isfinite(embedding_list)):
                    logger.error(f"Hotel {metadata['hotel_id']} has NaN or inf values")
                    continue
                points.append(
                    PointStruct(
                        id=metadata['hotel_id'],
                        vector=embedding_list,
                        payload=metadata
                    )
                )
            except Exception as e:
                logger.error(f"Error processing hotel {metadata['hotel_id']}: {e}")
                continue
        
        # Upload only new hotels
        if points:
            logger.info(f"Uploading {len(points)} new hotels to Qdrant...")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully added {len(points)} new hotels!")
        else:
            logger.warning("No new hotels were added")
    
    def calculate_hotel_distances(self, top_n: int = 10) -> pd.DataFrame:
        """
        Calculate cosine distances between all hotels
        
        Args:
            top_n: Number of top similar hotels to show for each hotel
            
        Returns:
            DataFrame with hotel-to-hotel distances
        """
        logger.info("Calculating cosine distances between all hotels...")
        
        # Get all hotel vectors from Qdrant
        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=10000,  # Get all hotels
            with_vectors=True
        )
        
        if not results:
            logger.warning("No hotels found in database")
            return pd.DataFrame()
        
        # Store vectors and metadata
        hotel_vectors = {}
        hotel_info = {}
        
        for result in results:
            hotel_id = result.payload['hotel_id']
            # Check if vector exists
            if result.vector is not None:
                hotel_vectors[hotel_id] = np.array(result.vector)
                hotel_info[hotel_id] = result.payload
            else:
                logger.warning(f"Hotel {hotel_id} has no vector, skipping")
        
        logger.info(f"Retrieved {len(hotel_vectors)} hotel vectors")
        
        if len(hotel_vectors) == 0:
            logger.warning("No valid hotel vectors found")
            return pd.DataFrame()
        
        # Calculate pairwise cosine distances
        hotel_ids = list(hotel_vectors.keys())
        n_hotels = len(hotel_ids)
        distance_data = []
        
        for i, hotel1_id in enumerate(hotel_ids):
            if i % 10 == 0:
                logger.info(f"Processing hotel {i+1}/{n_hotels}")
            
            hotel1_vec = hotel_vectors[hotel1_id]
            
            # Check if vector is valid
            if hotel1_vec is None or len(hotel1_vec) == 0:
                logger.warning(f"Hotel {hotel1_id} has invalid vector, skipping")
                continue
            
            distances = []
            
            for hotel2_id in hotel_ids:
                hotel2_vec = hotel_vectors[hotel2_id]
                
                # Check if second vector is valid
                if hotel2_vec is None or len(hotel2_vec) == 0:
                    continue
                
                if hotel1_id == hotel2_id:
                    cosine_distance = 0.0
                    cosine_similarity = 1.0
                else:
                    # Calculate cosine similarity
                    dot_product = np.dot(hotel1_vec, hotel2_vec)
                    norm1 = np.linalg.norm(hotel1_vec)
                    norm2 = np.linalg.norm(hotel2_vec)
                    
                    # Check for zero norms
                    if norm1 == 0 or norm2 == 0:
                        cosine_similarity = 0.0
                    else:
                        cosine_similarity = dot_product / (norm1 * norm2)
                    
                    # Cosine distance = 1 - similarity
                    cosine_distance = 1 - cosine_similarity
                
                distances.append({
                    'hotel1_id': hotel1_id,
                    'hotel2_id': hotel2_id,
                    'distance': cosine_distance,
                    'similarity': cosine_similarity,
                    'hotel1_name': hotel_info[hotel1_id].get('hotel_name', ''),
                    'hotel2_name': hotel_info[hotel2_id].get('hotel_name', '')
                })
            
            # Sort by similarity (descending) and get top N
            distances.sort(key=lambda x: x['similarity'], reverse=True)
            distance_data.extend(distances[1:top_n+1])  # Exclude self (index 0) and take top N
        
        distance_df = pd.DataFrame(distance_data)
        logger.info(f"Calculated distances for {len(distance_df)} hotel pairs")
        
        return distance_df
    
    def search_similar_hotels(self, query_text: str, top_k: int = 10) -> List[Dict]:
        """
        Search for similar hotels based on query
        
        Args:
            query_text: User query or hotel description
            top_k: Number of results to return
            
        Returns:
            List of similar hotels with similarity scores
        """
        # Create embedding for query
        if self.use_ollama:
            query_embedding = self._create_embeddings_ollama([query_text])[0]
        else:
            query_embedding = self.model.encode([query_text])[0]
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k
        )
        
        # Process results
        similar_hotels = []
        seen_hotels = set()
        
        for result in results:
            payload = result.payload
            hotel_id = payload['hotel_id']
            
            # Only add each hotel once (in case of chunks)
            if hotel_id not in seen_hotels:
                similar_hotels.append({
                    'hotel_id': hotel_id,
                    'hotel_name': payload.get('hotel_name', ''),
                    'similarity_score': result.score,
                    'hotel_rank': payload.get('hotel_rank', 0),
                    'hotel_price_average': payload.get('hotel_price_average', 0)
                })
                seen_hotels.add(hotel_id)
        
        return similar_hotels
    
    def recommend_for_hotel(self, hotel_id: int, top_k: int = 10) -> List[Dict]:
        """
        Recommend similar hotels for a given hotel using cosine distance
        
        Args:
            hotel_id: ID of the hotel
            top_k: Number of recommendations to return
            
        Returns:
            List of recommended hotels
        """
        # Get hotel vector directly by ID
        try:
            # Use scroll with filter to get hotel with vector
            result, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="hotel_id",
                            match=MatchValue(value=hotel_id)
                        )
                    ]
                ),
                limit=1,
                with_vectors=True
            )
            
            if not result or len(result) == 0:
                logger.warning(f"Hotel {hotel_id} not found in database")
                return []
            
            hotel_point = result[0]
            
            # Check if vector exists
            if not hasattr(hotel_point, 'vector') or hotel_point.vector is None:
                logger.error(f"Hotel {hotel_id} has no vector")
                return []
            
            hotel_vector = np.array(hotel_point.vector)
            
            # Validate vector
            if len(hotel_vector) == 0 or not np.all(np.isfinite(hotel_vector)):
                logger.error(f"Hotel {hotel_id} has invalid vector")
                return []
            
            # Search for similar hotels using cosine similarity
            # Using the deprecated search method but it works more reliably
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=hotel_vector.tolist(),
                limit=top_k + 1,  # +1 to exclude the hotel itself
                with_payload=True
            )
            
            # Process results and filter out the hotel itself
            recommendations = []
            for res in search_results:
                # Skip the hotel itself
                if res.payload.get('hotel_id') == hotel_id:
                    continue
                    
                recommendations.append({
                    'hotel_id': res.payload['hotel_id'],
                    'hotel_name': res.payload.get('hotel_name', ''),
                    'similarity_score': res.score,
                    'cosine_similarity': res.score,
                    'cosine_distance': 1 - res.score,
                    'hotel_rank': res.payload.get('hotel_rank', 0),
                    'hotel_price_average': res.payload.get('hotel_price_average', 0)
                })
            
            return recommendations[:top_k]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

def main():
    """Main execution function"""
    
    # Load data
    logger.info("Loading hotel data...")
    hotels_df = pd.read_csv('datasets_extracted/tbl_hotel.csv')
    logger.info(f"Loaded {len(hotels_df)} hotels")
    
    # Initialize system with BGE-M3 via Ollama
    logger.info("Initializing Semantic Recommendation System with BGE-M3 via Ollama...")
    system = SemanticRecommendationSystem(
        use_ollama=True,
        ollama_url='http://localhost:11434'
    )
    
    # Index hotels (recreate collection for first time)
    system.index_hotels(hotels_df, recreate_collection=True)
    
    # Calculate cosine distances between all hotels
    logger.info("\n=== Calculating hotel distances ===")
    distance_df = system.calculate_hotel_distances(top_n=5)
    
    # Save distance matrix to CSV
    if not distance_df.empty:
        output_file = 'hotel_distances.csv'
        distance_df.to_csv(output_file, index=False)
        logger.info(f"Saved hotel distances to {output_file}")
    
    # Example: Recommend hotels similar to a specific hotel
    example_hotel_id = 2
    logger.info(f"\n=== Finding recommendations for hotel ID: {example_hotel_id} ===")
    recommendations = system.recommend_for_hotel(example_hotel_id, top_k=5)
    
    print("\n=== Recommendations ===")
    for idx, rec in enumerate(recommendations, 1):
        print(f"\n{idx}. Hotel ID: {rec['hotel_id']}")
        print(f"   Name: {rec['hotel_name']}")
        print(f"   Similarity: {rec['cosine_similarity']:.4f}")
        print(f"   Distance: {rec['cosine_distance']:.4f}")
        print(f"   Rank: {rec['hotel_rank']} stars")
        print(f"   Price: {rec['hotel_price_average']:,.0f} VND")

if __name__ == '__main__':
    main()

