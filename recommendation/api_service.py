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
from typing import Any, Tuple

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

