#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API Service for Semantic Hotel Recommendation
"""

from flask import Flask, request, jsonify, Response
from semantic_recommendation_system import SemanticRecommendationSystem
import pandas as pd
import logging
import os
import sys
from pathlib import Path
from typing import Any, Tuple, List, Dict

# Try to import ApiResponse from src/shared, fallback to local implementation
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.shared.response import ApiResponse
except ImportError:
    # Local implementation if src/shared not available
    class ApiResponse:
        @staticmethod
        def success(data: Any = None, message: str = "OK", code: int = 200) -> Tuple[Response, int]:
            return jsonify({
                "success": True,
                "code": code,
                "message": message,
                "data": data
            }), code
        
        @staticmethod
        def error(message: str = "Error", code: int = 400, data: Any = None) -> Tuple[Response, int]:
            return jsonify({
                "success": False,
                "code": code,
                "message": message,
                "data": data
            }), code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global system instance
system = None

def initialize_system():
    """Initialize the recommendation system"""
    global system
    if system is None:
        logger.info("Initializing Semantic Recommendation System...")
        system = SemanticRecommendationSystem(
            use_ollama=True,
            ollama_url=os.getenv('OLLAMA_URL', 'http://localhost:11434')
        )
        logger.info("System initialized successfully")
    return system

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return ApiResponse.success(
        data={
            'status': 'ok'
        },
        message='Semantic Recommendation Service is running'
    )

@app.route('/api/hotels/process', methods=['POST'])
def process_hotel():
    """
    Process a new hotel (chunk + embedding)
    
    Request body:
    {
        "hotel_id": 123,
        "hotel_name": "Hotel Name",
        "hotel_desc": "Description...",
        "hotel_placedetails": "Location...",
        "hotel_tag_keyword": "keywords...",
        "hotel_rank": 5,
        "hotel_price_average": 1000000
    }
    """
    try:
        sys = initialize_system()
        data = request.json
        
        required_fields = ['hotel_id']
        if not all(field in data for field in required_fields):
            return ApiResponse.error(
                message='Missing required fields',
                code=400,
                data={'required': required_fields}
            )
        
        # Create hotel dataframe
        hotel_df = pd.DataFrame([data])
        
        # Process and add hotel
        sys.add_new_hotels(hotel_df)
        
        return ApiResponse.success(
            data={
                'hotel_id': data['hotel_id']
            },
            message=f'Hotel {data["hotel_id"]} processed successfully'
        )
        
    except Exception as e:
        logger.error(f"Error processing hotel: {e}")
        return ApiResponse.error(
            message=f'Error processing hotel: {str(e)}',
            code=500
        )

@app.route('/api/hotels/batch', methods=['POST'])
def process_hotels_batch():
    """
    Process multiple hotels at once
    
    Request body:
    {
        "hotels": [
            {"hotel_id": 1, "hotel_name": "...", ...},
            {"hotel_id": 2, "hotel_name": "...", ...}
        ]
    }
    """
    try:
        sys = initialize_system()
        data = request.json
        
        if 'hotels' not in data or not isinstance(data['hotels'], list):
            return ApiResponse.error(
                message='Invalid request. Expected "hotels" array',
                code=400
            )
        
        hotels_df = pd.DataFrame(data['hotels'])
        sys.add_new_hotels(hotels_df)
        
        return ApiResponse.success(
            data={
                'count': len(data['hotels'])
            },
            message=f'Processed {len(data["hotels"])} hotels'
        )
        
    except Exception as e:
        logger.error(f"Error processing hotels batch: {e}")
        return ApiResponse.error(
            message=f'Error processing hotels batch: {str(e)}',
            code=500
        )

@app.route('/api/hotels/<int:hotel_id>/similar', methods=['GET'])
def get_similar_hotels(hotel_id):
    """
    Get similar hotels for a given hotel_id
    
    Query parameters:
    - top_k: Number of recommendations (default: 10)
    """
    try:
        sys = initialize_system()
        top_k = request.args.get('top_k', 10, type=int)
        
        recommendations = sys.recommend_for_hotel(hotel_id, top_k=top_k)
        
        return ApiResponse.success(
            data={
                'hotel_id': hotel_id,
                'recommendations': recommendations,
                'count': len(recommendations)
            },
            message='Similar hotels retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error getting similar hotels: {e}")
        return ApiResponse.error(
            message=f'Error getting similar hotels: {str(e)}',
            code=500,
            data={'hotel_id': hotel_id}
        )

@app.route('/api/hotels/search', methods=['POST'])
def search_hotels():
    """
    Search hotels by query text
    
    Request body:
    {
        "query": "Khách sạn gần biển Nha Trang",
        "top_k": 10
    }
    """
    try:
        sys = initialize_system()
        data = request.json
        
        if 'query' not in data:
            return ApiResponse.error(
                message='Missing required field: "query"',
                code=400
            )
        
        query = data['query']
        top_k = data.get('top_k', 10)
        
        results = sys.search_similar_hotels(query, top_k=top_k)
        
        return ApiResponse.success(
            data={
                'query': query,
                'results': results,
                'count': len(results)
            },
            message='Hotels search completed successfully'
        )
        
    except Exception as e:
        logger.error(f"Error searching hotels: {e}")
        return ApiResponse.error(
            message=f'Error searching hotels: {str(e)}',
            code=500
        )

def apply_filters(results: List[Dict], filters: Dict) -> List[Dict]:
    """Apply filters to search results"""
    filtered = results
    
    logger.debug(f"Applying filters: {filters} to {len(results)} results")
    
    # Filter by area_id (convert to int for comparison)
    if "area_id" in filters:
        area_id_filter = int(filters["area_id"])
        before_count = len(filtered)
        filtered = [
            r for r in filtered 
            if int(r.get("payload", {}).get("area_id", 0)) == area_id_filter
        ]
        logger.debug(f"Area filter: {before_count} -> {len(filtered)} results")
    
    # Filter by max_price
    if "max_price" in filters:
        max_price_filter = float(filters["max_price"])
        before_count = len(filtered)
        filtered = [
            r for r in filtered 
            if float(r.get("payload", {}).get("hotel_price_average", float('inf'))) <= max_price_filter
        ]
        logger.debug(f"Price filter: {before_count} -> {len(filtered)} results")
    
    # Filter by min_rank
    if "min_rank" in filters:
        min_rank_filter = int(filters["min_rank"])
        before_count = len(filtered)
        filtered = [
            r for r in filtered 
            if int(r.get("payload", {}).get("hotel_rank", 0)) >= min_rank_filter
        ]
        logger.debug(f"Rank filter: {before_count} -> {len(filtered)} results")
    
    return filtered

def rerank_by_intent(results: List[Dict], processed_query: Dict, top_k: int) -> List[Dict]:
    """Re-rank results based on query intent"""
    intent = processed_query.get("intent", {})
    original_query = processed_query.get("original_query", "").lower()
    
    # Boost score for price-related queries
    if intent.get("price_range") == "low":
        # Sort by price ascending, then by relevance score
        results = sorted(
            results,
            key=lambda x: (
                x.get("payload", {}).get("hotel_price_average", float('inf')),
                -x.get("score", 0)  # Higher score = better
            )
        )
    
    # Boost score for hotels with matching tags
    if "giá tốt" in original_query or "giá rẻ" in original_query:
        for result in results:
            tags = result.get("payload", {}).get("hotel_tag_keyword", "").lower()
            if "giá tốt" in tags or "khách sạn giá tốt" in tags:
                result["score"] = result.get("score", 0) * 1.2  # Boost 20%
    
    # Sort by final score
    results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    
    return results[:top_k]

@app.route('/api/hotels/semantic-search', methods=['POST'])
def semantic_search_hotels():
    """
    Semantic search với query preprocessing và filtering
    
    Request body:
    {
        "query": "Tìm kiếm khách sạn ở Ngũ Hành Sơn giá tốt",
        "top_k": 10,
        "filters": {
            "area_id": 7,  # Optional: Ngũ Hành Sơn
            "max_price": 2000000,  # Optional
            "min_rank": 3  # Optional
        }
    }
    """
    try:
        sys = initialize_system()
        data = request.json
        
        if 'query' not in data:
            return ApiResponse.error(
                message='Missing required field: "query"',
                code=400
            )
        
        query = data['query']
        top_k = data.get('top_k', 10)
        filters = data.get('filters', {})
        
        # Step 1: Query preprocessing (extract intent, entities)
        try:
            from src.core.query_preprocessor import QueryPreprocessor
            preprocessor = QueryPreprocessor()
            processed_query = preprocessor.process(query)
            
            logger.info(f"Processed query: {processed_query}")
            
            # Merge filters from query preprocessing with provided filters
            if processed_query.get("filters"):
                filters = {**processed_query["filters"], **filters}
        except Exception as e:
            logger.warning(f"Query preprocessing failed: {e}, using original query")
            processed_query = {"original_query": query, "intent": {}, "filters": filters}
        
        logger.info(f"Final filters: {filters}")
        
        # Step 2: Semantic search
        results = sys.search_similar_hotels(
            query=query,
            top_k=top_k * 3  # Get more results for filtering (increased from 2x to 3x)
        )
        
        logger.info(f"Semantic search returned {len(results)} results")
        
        # Step 3: Apply filters
        filtered_results = apply_filters(results, filters)
        
        logger.info(f"After filtering: {len(filtered_results)} results")
        
        # If no results after filtering, try without strict filters
        if len(filtered_results) == 0 and filters:
            logger.warning("No results after filtering, trying with relaxed filters")
            # Try without price filter first
            relaxed_filters = {k: v for k, v in filters.items() if k != "max_price"}
            if relaxed_filters:
                filtered_results = apply_filters(results, relaxed_filters)
            
            # If still no results, use original results without any filters
            if len(filtered_results) == 0:
                logger.warning("No results with relaxed filters, using original results")
                filtered_results = results[:top_k * 2]
        
        # Step 4: Re-rank based on query intent
        ranked_results = rerank_by_intent(
            filtered_results, 
            processed_query,
            top_k=top_k
        )
        
        logger.info(f"Final ranked results: {len(ranked_results)}")
        
        return ApiResponse.success(
            data={
                'query': query,
                'processed_query': processed_query,
                'results': ranked_results,
                'count': len(ranked_results)
            },
            message='Semantic search completed successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}", exc_info=True)
        return ApiResponse.error(
            message=f'Error in semantic search: {str(e)}',
            code=500
        )

@app.route('/api/hotels/reload', methods=['POST'])
def reload_database():
    """
    Reload hotels from CSV file and rebuild index
    
    Request body:
    {
        "csv_path": "datasets_extracted/tbl_hotel.csv",  # Optional
        "recreate_collection": true  # Optional
    }
    """
    try:
        sys = initialize_system()
        data = request.json or {}
        
        csv_path = data.get('csv_path', 'datasets_extracted/tbl_hotel.csv')
        recreate = data.get('recreate_collection', True)
        
        logger.info(f"Reloading hotels from: {csv_path}")
        
        # Load data
        hotels_df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(hotels_df)} hotels")
        
        # Index hotels
        sys.index_hotels(hotels_df, recreate_collection=recreate)
        
        return ApiResponse.success(
            data={
                'count': len(hotels_df),
                'recreated': recreate,
                'csv_path': csv_path
            },
            message=f'Reloaded {len(hotels_df)} hotels from {csv_path}'
        )
        
    except Exception as e:
        logger.error(f"Error reloading database: {e}")
        return ApiResponse.error(
            message=f'Error reloading database: {str(e)}',
            code=500
        )

@app.route('/api/hotels/calculate-distances', methods=['POST'])
def calculate_distances():
    """
    Calculate cosine distances between all hotels
    
    Request body:
    {
        "top_n": 10  # Optional
    }
    """
    try:
        sys = initialize_system()
        data = request.json or {}
        top_n = data.get('top_n', 10)
        
        logger.info("Calculating hotel distances...")
        distance_df = sys.calculate_hotel_distances(top_n=top_n)
        
        # Save to CSV
        output_file = 'hotel_distances.csv'
        distance_df.to_csv(output_file, index=False)
        
        return ApiResponse.success(
            data={
                'output_file': output_file,
                'count': len(distance_df)
            },
            message=f'Calculated distances for {len(distance_df)} hotel pairs'
        )
        
    except Exception as e:
        logger.error(f"Error calculating distances: {e}")
        return ApiResponse.error(
            message=f'Error calculating distances: {str(e)}',
            code=500
        )

@app.route('/api/hotels/info', methods=['GET'])
def get_collection_info():
    """Get information about the hotel collection"""
    try:
        sys = initialize_system()
        
        collection_info = sys.client.get_collection(sys.collection_name)
        
        return ApiResponse.success(
            data={
                'collection_name': sys.collection_name,
                'points_count': collection_info.points_count,
                'vectors_count': collection_info.config.params.vectors.size if hasattr(collection_info.config.params.vectors, 'size') else None
            },
            message='Collection info retrieved successfully'
        )
        
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        return ApiResponse.error(
            message=f'Error getting collection info: {str(e)}',
            code=500
        )

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    
    logger.info(f"Starting Semantic Recommendation API Service on {host}:{port}")
    app.run(host=host, port=port, debug=True)

