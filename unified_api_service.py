#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified API Service - RAG + Recommendation System
Flask API service gộp cả RAG chatbot và Recommendation System
Version 2.0 - With proper configuration and structure
"""

import os
import sys
import socket
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import pandas as pd
from typing import Dict, Optional

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'rag'))
sys.path.insert(0, str(Path(__file__).parent / 'recommendation'))

# Import configuration
try:
    from src.config import get_settings, Collections
    from src.shared import get_logger, setup_logging
    USE_NEW_CONFIG = True
except ImportError:
    USE_NEW_CONFIG = False
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

# Import RAG system
from rag.simple_rag_system import SimpleRAGSystem

# Import Recommendation system
from recommendation.semantic_recommendation_system import SemanticRecommendationSystem

# Setup logging
if USE_NEW_CONFIG:
    setup_logging(level=logging.INFO)
    logger = get_logger(__name__)
else:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Flask app setup
BASE_DIR = Path(__file__).parent / 'rag'
app = Flask(__name__, 
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'))
app.secret_key = os.environ.get('SECRET_KEY', 'unified-service-secret-key-change-in-production')
CORS(app)

# Global system instances
rag_system: Optional[SimpleRAGSystem] = None
recommendation_system: Optional[SemanticRecommendationSystem] = None


def check_coupons_indexed(rag_sys: SimpleRAGSystem) -> bool:
    """Check if coupons are already indexed in the collection"""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        client = QdrantClient(url=rag_sys.qdrant_url)
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if rag_sys.collection_name not in collection_names:
            return False
        
        filter_condition = Filter(
            must=[
                FieldCondition(
                    key="document_type",
                    match=MatchValue(value="coupon")
                )
            ]
        )
        
        results = client.scroll(
            collection_name=rag_sys.collection_name,
            scroll_filter=filter_condition,
            limit=1
        )
        
        return len(results[0]) > 0
    except Exception as e:
        logger.warning(f"Could not check if coupons are indexed: {e}")
        return False


def initialize_rag_system():
    """Initialize RAG system"""
    global rag_system
    
    if rag_system is not None:
        return rag_system
    
    logger.info("🔄 Initializing RAG system...")
    
    # Use new config if available
    if USE_NEW_CONFIG:
        settings = get_settings()
        ollama_url = settings.OLLAMA_URL
        qdrant_url = settings.QDRANT_URL
        embedding_model = settings.EMBEDDING_MODEL
        llm_model = settings.LLM_MODEL
        collection_name = settings.RAG_COLLECTION_HOTELS  # Use dedicated RAG collection
        llm_provider = settings.LLM_PROVIDER
        lm_studio_url = settings.LM_STUDIO_URL
        auto_index_coupons = settings.AUTO_INDEX_COUPONS
        
        logger.info(f"📝 Using new config: RAG collection = {collection_name}")
    else:
        # Fallback to environment variables
        ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        qdrant_url = os.environ.get('QDRANT_URL', 'http://localhost:6333')
        embedding_model = os.environ.get('EMBEDDING_MODEL', 'bge-m3')
        llm_model = os.environ.get('LLM_MODEL', 'qwen3')
        collection_name = os.environ.get('RAG_COLLECTION_HOTELS', os.environ.get('COLLECTION_NAME', 'hotels_rag'))
        llm_provider = os.environ.get('LLM_PROVIDER', 'ollama')
        lm_studio_url = os.environ.get('LM_STUDIO_URL', None)
        auto_index_coupons = os.environ.get('AUTO_INDEX_COUPONS', 'true').lower() == 'true'
        
        logger.info(f"⚠️  Using legacy config: RAG collection = {collection_name}")
    
    rag_system = SimpleRAGSystem(
        ollama_url=ollama_url,
        qdrant_url=qdrant_url,
        embedding_model=embedding_model,
        llm_model=llm_model,
        collection_name=collection_name,
        llm_provider=llm_provider,
        lm_studio_url=lm_studio_url
    )
    
    try:
        rag_system.load_vectorstore()
        logger.info("✅ RAG system loaded existing vectorstore")
        
        if auto_index_coupons:
            try:
                coupons_indexed = check_coupons_indexed(rag_system)
                if not coupons_indexed:
                    logger.info("🔄 Auto-indexing coupons...")
                    rag_system.index_coupons_from_database(
                        use_chunking=True,
                        incremental=False,
                        recreate_collection=False,
                        valid_only=True
                    )
                    logger.info("✅ Coupons auto-indexed successfully")
                else:
                    logger.info("✅ Coupons already indexed")
            except Exception as e:
                logger.warning(f"⚠️  Could not auto-index coupons: {e}")
                
    except Exception as e:
        logger.error(f"❌ Error loading RAG vectorstore: {e}")
        logger.info("Please run index_hotels() first or set up the collection")
        rag_system = None
    
    return rag_system


def initialize_recommendation_system():
    """Initialize Recommendation system"""
    global recommendation_system
    
    if recommendation_system is not None:
        return recommendation_system
    
    logger.info("🔄 Initializing Recommendation system...")
    
    try:
        # Use new config if available
        if USE_NEW_CONFIG:
            settings = get_settings()
            use_ollama = settings.REC_USE_OLLAMA
            ollama_url = settings.OLLAMA_URL
            qdrant_url = settings.QDRANT_URL
            
            logger.info(f"📝 Using new config: Recommendation collection = {Collections.RECOMMENDATION_HOTELS}")
        else:
            # Fallback to environment variables
            use_ollama = os.getenv('REC_USE_OLLAMA', 'true').lower() == 'true'
            ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
            qdrant_url = os.getenv('QDRANT_URL', 'http://localhost:6333')
            
            logger.info("⚠️  Using legacy config for Recommendation system")
        
        recommendation_system = SemanticRecommendationSystem(
            use_ollama=use_ollama,
            ollama_url=ollama_url,
            qdrant_url=qdrant_url
        )
        
        # Override collection name if using new config
        if USE_NEW_CONFIG:
            recommendation_system.collection_name = Collections.RECOMMENDATION_HOTELS
            logger.info(f"✅ Recommendation system collection: {recommendation_system.collection_name}")
        
        logger.info("✅ Recommendation system initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing Recommendation system: {e}")
        recommendation_system = None
    
    return recommendation_system


# ==================== HEALTH & STATUS ENDPOINTS ====================

@app.route('/')
def index():
    """Render chat interface"""
    return render_template('chat.html')


@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Unified health check endpoint"""
    global rag_system, recommendation_system
    
    rag_initialized = rag_system is not None
    rec_initialized = recommendation_system is not None
    
    qdrant_connected = False
    if rag_initialized:
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(url=rag_system.qdrant_url)
            client.get_collections()
            qdrant_connected = True
        except Exception as e:
            logger.error(f"Qdrant connection error: {e}")
    
    return jsonify({
        'status': 'ok' if (rag_initialized or rec_initialized) else 'error',
        'services': {
            'rag': {
                'initialized': rag_initialized,
                'qdrant_connected': qdrant_connected
            },
            'recommendation': {
                'initialized': rec_initialized
            }
        },
        'message': 'Unified Service (RAG + Recommendation) is running'
    })


@app.route('/api/status', methods=['GET'])
def status():
    """Get detailed system status"""
    global rag_system, recommendation_system
    
    status_info = {
        'rag': {'initialized': False},
        'recommendation': {'initialized': False}
    }
    
    if rag_system:
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(url=rag_system.qdrant_url)
            collection = client.get_collection(rag_system.collection_name)
            
            status_info['rag'] = {
                'initialized': True,
                'collection_name': rag_system.collection_name,
                'points_count': collection.points_count,
                'vector_size': collection.config.params.vectors.size,
                'embedding_model': rag_system.embedding_model,
                'llm_model': rag_system.llm_model
            }
        except Exception as e:
            logger.error(f"Error getting RAG status: {e}")
    
    if recommendation_system:
        try:
            collection_info = recommendation_system.client.get_collection(recommendation_system.collection_name)
            status_info['recommendation'] = {
                'initialized': True,
                'collection_name': recommendation_system.collection_name,
                'points_count': collection_info.points_count
            }
        except Exception as e:
            logger.error(f"Error getting Recommendation status: {e}")
    
    return jsonify(status_info)


# ==================== RAG ENDPOINTS ====================

@app.route('/api/chat', methods=['POST'])
@app.route('/api/rag/chat', methods=['POST'])
def chat():
    """RAG Chat endpoint - Ask question to RAG system"""
    global rag_system
    
    if rag_system is None:
        rag_system = initialize_rag_system()
    
    if rag_system is None:
        return jsonify({
            'error': 'RAG system not initialized. Please ensure Qdrant collection exists.'
        }), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        logger.info(f"📝 RAG Chat question: {question}")
        
        response = rag_system.ask(question)
        
        return jsonify({
            'success': True,
            'question': response['question'],
            'answer': response['answer'],
            'sources': response['sources']
        })
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        return jsonify({'error': f'Error processing question: {str(e)}'}), 500


@app.route('/api/search', methods=['POST'])
@app.route('/api/rag/search', methods=['POST'])
def search():
    """RAG Search endpoint - Semantic search only (no LLM)"""
    global rag_system
    
    if rag_system is None:
        rag_system = initialize_rag_system()
    
    if rag_system is None:
        return jsonify({
            'error': 'RAG system not initialized. Please ensure Qdrant collection exists.'
        }), 500
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"🔍 RAG Search query: {query}")
        
        try:
            results = rag_system.search_hotels_optimized(query, top_k=top_k, ef=50)
        except Exception:
            results = rag_system.search_hotels(query, top_k=top_k)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing search: {e}", exc_info=True)
        return jsonify({'error': f'Error processing search: {str(e)}'}), 500


# ==================== RECOMMENDATION ENDPOINTS ====================

@app.route('/api/hotels/process', methods=['POST'])
@app.route('/api/recommendation/hotels/process', methods=['POST'])
def process_hotel():
    """Process a new hotel (chunk + embedding)"""
    global recommendation_system
    
    if recommendation_system is None:
        recommendation_system = initialize_recommendation_system()
    
    if recommendation_system is None:
        return jsonify({'error': 'Recommendation system not initialized'}), 500
    
    try:
        data = request.json
        
        if 'hotel_id' not in data:
            return jsonify({
                'error': 'Missing required field: hotel_id'
            }), 400
        
        hotel_df = pd.DataFrame([data])
        recommendation_system.add_new_hotels(hotel_df)
        
        logger.info(f"✅ Processed hotel {data['hotel_id']}")
        
        return jsonify({
            'success': True,
            'message': f'Hotel {data["hotel_id"]} processed successfully',
            'hotel_id': data['hotel_id']
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing hotel: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/hotels/batch', methods=['POST'])
@app.route('/api/recommendation/hotels/batch', methods=['POST'])
def process_hotels_batch():
    """Process multiple hotels at once"""
    global recommendation_system
    
    if recommendation_system is None:
        recommendation_system = initialize_recommendation_system()
    
    if recommendation_system is None:
        return jsonify({'error': 'Recommendation system not initialized'}), 500
    
    try:
        data = request.json
        
        if 'hotels' not in data or not isinstance(data['hotels'], list):
            return jsonify({
                'error': 'Invalid request. Expected "hotels" array'
            }), 400
        
        hotels_df = pd.DataFrame(data['hotels'])
        recommendation_system.add_new_hotels(hotels_df)
        
        logger.info(f"✅ Processed {len(data['hotels'])} hotels")
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(data["hotels"])} hotels',
            'count': len(data['hotels'])
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing hotels batch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/hotels/<int:hotel_id>/similar', methods=['GET'])
@app.route('/api/recommendation/hotels/<int:hotel_id>/similar', methods=['GET'])
def get_similar_hotels(hotel_id):
    """Get similar hotels for a given hotel_id"""
    global recommendation_system
    
    if recommendation_system is None:
        recommendation_system = initialize_recommendation_system()
    
    if recommendation_system is None:
        return jsonify({'error': 'Recommendation system not initialized'}), 500
    
    try:
        top_k = request.args.get('top_k', 10, type=int)
        
        recommendations = recommendation_system.recommend_for_hotel(hotel_id, top_k=top_k)
        
        logger.info(f"🎯 Found {len(recommendations)} similar hotels for hotel_id={hotel_id}")
        
        return jsonify({
            'success': True,
            'hotel_id': hotel_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting similar hotels: {e}")
        return jsonify({'error': str(e), 'hotel_id': hotel_id}), 500


@app.route('/api/hotels/search', methods=['POST'])
@app.route('/api/recommendation/hotels/search', methods=['POST'])
def search_hotels():
    """Search hotels by query text (Recommendation system)"""
    global recommendation_system
    
    if recommendation_system is None:
        recommendation_system = initialize_recommendation_system()
    
    if recommendation_system is None:
        return jsonify({'error': 'Recommendation system not initialized'}), 500
    
    try:
        data = request.json
        
        if 'query' not in data:
            return jsonify({'error': 'Missing required field: "query"'}), 400
        
        query = data['query']
        top_k = data.get('top_k', 10)
        
        results = recommendation_system.search_similar_hotels(query, top_k=top_k)
        
        logger.info(f"🔍 Hotel search: '{query}' returned {len(results)} results")
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching hotels: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/hotels/reload', methods=['POST'])
@app.route('/api/recommendation/hotels/reload', methods=['POST'])
def reload_database():
    """Reload hotels from CSV file and rebuild index"""
    global recommendation_system
    
    if recommendation_system is None:
        recommendation_system = initialize_recommendation_system()
    
    if recommendation_system is None:
        return jsonify({'error': 'Recommendation system not initialized'}), 500
    
    try:
        data = request.json or {}
        
        csv_path = data.get('csv_path', 'datasets_extracted/tbl_hotel.csv')
        recreate = data.get('recreate_collection', True)
        
        logger.info(f"🔄 Reloading hotels from: {csv_path}")
        
        hotels_df = pd.read_csv(csv_path)
        logger.info(f"📊 Loaded {len(hotels_df)} hotels")
        
        recommendation_system.index_hotels(hotels_df, recreate_collection=recreate)
        
        return jsonify({
            'success': True,
            'message': f'Reloaded {len(hotels_df)} hotels from {csv_path}',
            'count': len(hotels_df),
            'recreated': recreate
        }), 200
        
    except Exception as e:
        logger.error(f"Error reloading database: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/hotels/calculate-distances', methods=['POST'])
@app.route('/api/recommendation/hotels/calculate-distances', methods=['POST'])
def calculate_distances():
    """Calculate cosine distances between all hotels"""
    global recommendation_system
    
    if recommendation_system is None:
        recommendation_system = initialize_recommendation_system()
    
    if recommendation_system is None:
        return jsonify({'error': 'Recommendation system not initialized'}), 500
    
    try:
        data = request.json or {}
        top_n = data.get('top_n', 10)
        
        logger.info("🔄 Calculating hotel distances...")
        distance_df = recommendation_system.calculate_hotel_distances(top_n=top_n)
        
        output_file = 'hotel_distances.csv'
        distance_df.to_csv(output_file, index=False)
        
        logger.info(f"✅ Saved distances to {output_file}")
        
        return jsonify({
            'success': True,
            'message': f'Calculated distances for {len(distance_df)} hotel pairs',
            'output_file': output_file,
            'count': len(distance_df)
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating distances: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/hotels/info', methods=['GET'])
@app.route('/api/recommendation/hotels/info', methods=['GET'])
def get_collection_info():
    """Get information about the hotel collection"""
    global recommendation_system
    
    if recommendation_system is None:
        recommendation_system = initialize_recommendation_system()
    
    if recommendation_system is None:
        return jsonify({'error': 'Recommendation system not initialized'}), 500
    
    try:
        collection_info = recommendation_system.client.get_collection(recommendation_system.collection_name)
        
        return jsonify({
            'success': True,
            'collection_name': recommendation_system.collection_name,
            'points_count': collection_info.points_count,
            'vectors_count': collection_info.config.params.vectors.size if hasattr(collection_info.config.params.vectors, 'size') else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Initialize both systems on startup
    logger.info("🚀 Starting Unified API Service (RAG + Recommendation)")
    
    # Initialize RAG system
    initialize_rag_system()
    
    # Initialize Recommendation system
    initialize_recommendation_system()
    
    # Get port from environment or use default
    default_port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Find available port
    def find_free_port(start_port):
        port = start_port
        while port < start_port + 100:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('', port))
                    return port
            except OSError:
                port += 1
        return None
    
    port = find_free_port(default_port)
    
    if port is None:
        logger.error(f"Could not find free port starting from {default_port}")
        exit(1)
    
    if port != default_port:
        logger.warning(f"Port {default_port} is in use, using port {port} instead")
    
    logger.info(f"✅ Unified API Service starting on port {port}")
    logger.info(f"🌐 Open http://localhost:{port} in your browser")
    logger.info(f"📚 RAG Chat available at: /api/chat or /api/rag/chat")
    logger.info(f"🎯 Recommendation API available at: /api/hotels/* or /api/recommendation/hotels/*")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

