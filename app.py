#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Hotel Recommendation & RAG System
Single application cho cả RAG chatbot và Recommendation

Version 3.0 - Clean architecture với src/
"""

import os
import sys
import socket
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

# Import from src/
from src.config import get_settings, Collections
from src.shared import get_logger, setup_logging
from src.core import (
    EmbeddingService,
    VectorStoreService,
    RetrieverService,
    GeneratorService,
    RecommenderService,
    RAGService
)

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Load settings
settings = get_settings()

# Flask app
BASE_DIR = Path(__file__).parent / 'rag'
app = Flask(__name__, 
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'))
app.secret_key = settings.SECRET_KEY
CORS(app)

# Global services
rag_service = None
recommender_service = None
embedding_service = None
vectorstore_service = None


def ensure_collections_ready():
    """
    Chỉ đảm bảo collections đã tạo (KHÔNG tự động index data)
    """
    logger.info("=" * 80)
    logger.info("🔧 Checking Collections")
    logger.info("=" * 80)
    
    from qdrant_client.models import Distance, VectorParams
    
    try:
        # Khởi tạo VectorStore để check
        temp_vectorstore = VectorStoreService(url=settings.QDRANT_URL)
        client = temp_vectorstore.client
        
        # Danh sách collections cần thiết
        required_collections = [
            (Collections.RAG_HOTELS, "RAG Hotels (Chatbot)", 1024, "🏨"),
            (Collections.RAG_COUPONS, "RAG Coupons (Chatbot)", 1024, "🎟️"),
            (Collections.RECOMMENDATION_HOTELS, "Recommendation (Similar Hotels)", 384, "🎯"),
        ]
        
        # Lấy danh sách collections hiện có
        existing_collections = client.get_collections()
        existing_names = [col.name for col in existing_collections.collections]
        
        # Tạo collections nếu chưa có
        for collection_name, description, vector_size, emoji in required_collections:
            if collection_name not in existing_names:
                logger.info(f"Creating {emoji} {description} ({collection_name})...")
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,  # RAG: 1024 (bge-m3), Recommendation: 384 (MiniLM)
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created {collection_name}")
            else:
                info = client.get_collection(collection_name)
                logger.info(f"✅ {emoji} {collection_name}: {info.points_count} points")
        
        logger.info("")
        logger.info("💡 To index data:")
        logger.info("   RAG: Use scripts in rag/ folder")
        logger.info("   Recommendation: Use scripts in recommendation/ folder")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Error checking collections: {e}")
        raise


def initialize_services():
    """Initialize all services"""
    global rag_service, recommender_service, embedding_service, vectorstore_service
    
    logger.info("🚀 Initializing services...")
    
    try:
        # Bước 1: Đảm bảo collections đã sẵn sàng
        ensure_collections_ready()
        
        # Bước 2: Initialize shared services
        embedding_service = EmbeddingService(
            provider="ollama",
            model_name=settings.EMBEDDING_MODEL,
            ollama_url=settings.OLLAMA_URL,
            cache_enabled=settings.EMBEDDING_CACHE_ENABLED
        )
        
        vectorstore_service = VectorStoreService(
            url=settings.QDRANT_URL
        )
        
        # Bước 3: Initialize RAG service
        rag_service = RAGService(
            embedding_service=embedding_service,
            vectorstore_service=vectorstore_service,
            collection_name=settings.RAG_COLLECTION_HOTELS
        )
        
        # Bước 4: Initialize Recommendation service
        retriever_service = RetrieverService(
            embedding_service=embedding_service,
            vectorstore_service=vectorstore_service,
            default_collection=settings.REC_COLLECTION_HOTELS,
            default_top_k=settings.REC_TOP_K
        )
        
        recommender_service = RecommenderService(
            retriever_service=retriever_service,
            embedding_service=embedding_service,
            vectorstore_service=vectorstore_service
        )
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        raise


# ==================== Web Interface ====================

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')


@app.route('/health')
@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'version': '3.0',
        'services': {
            'rag': rag_service is not None,
            'recommendation': recommender_service is not None,
            'embedding': embedding_service is not None,
            'vectorstore': vectorstore_service is not None
        }
    })


@app.route('/api/status')
def status():
    """Detailed status"""
    try:
        rag_stats = rag_service.get_stats() if rag_service else {}
        
        return jsonify({
            'version': '3.0',
            'rag': rag_stats,
            'collections': {
                'rag_hotels': settings.RAG_COLLECTION_HOTELS,
                'rag_coupons': settings.RAG_COLLECTION_HOTELS,
                'rec_hotels': settings.REC_COLLECTION_HOTELS
            }
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== RAG Endpoints ====================

@app.route('/api/chat', methods=['POST'])
@app.route('/api/rag/chat', methods=['POST'])
def chat():
    """RAG chat endpoint"""
    if not rag_service:
        return jsonify({'error': 'RAG service not initialized'}), 500
    
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        logger.info(f"💬 Chat: {question[:50]}...")
        
        # Get answer
        result = rag_service.ask(
            question=question,
            top_k=data.get('top_k', settings.RAG_TOP_K),
            filters=data.get('filters')
        )
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
@app.route('/api/rag/search', methods=['POST'])
def search():
    """RAG search endpoint (retrieval only)"""
    if not rag_service:
        return jsonify({'error': 'RAG service not initialized'}), 500
    
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"🔍 Search: {query[:50]}...")
        
        # Search
        results = rag_service.search(
            query=query,
            top_k=data.get('top_k', settings.RAG_TOP_K),
            filters=data.get('filters')
        )
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Recommendation Endpoints ====================

@app.route('/api/recommend/query', methods=['POST'])
@app.route('/api/hotels/search', methods=['POST'])
def recommend_by_query():
    """Recommend hotels by query"""
    if not recommender_service:
        return jsonify({'error': 'Recommender service not initialized'}), 500
    
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"🎯 Recommend by query: {query[:50]}...")
        
        recommendations = recommender_service.recommend_by_query(
            query=query,
            collection_name=settings.REC_COLLECTION_HOTELS,
            top_k=data.get('top_k', settings.REC_TOP_K),
            filters=data.get('filters')
        )
        
        return jsonify({
            'success': True,
            'query': query,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        logger.error(f"Error in recommend by query: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend/similar/<item_id>', methods=['GET'])
@app.route('/api/hotels/<item_id>/similar', methods=['GET'])
def recommend_similar(item_id):
    """Recommend similar hotels"""
    if not recommender_service:
        return jsonify({'error': 'Recommender service not initialized'}), 500
    
    try:
        top_k = request.args.get('top_k', settings.REC_TOP_K, type=int)
        
        logger.info(f"🎯 Recommend similar for item_id={item_id}")
        
        recommendations = recommender_service.recommend_similar(
            item_id=item_id,
            collection_name=settings.REC_COLLECTION_HOTELS,
            top_k=top_k
        )
        
        return jsonify({
            'success': True,
            'item_id': item_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        logger.error(f"Error in recommend similar: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend/popular', methods=['GET'])
@app.route('/api/hotels/popular', methods=['GET'])
def recommend_popular():
    """Recommend popular hotels"""
    if not recommender_service:
        return jsonify({'error': 'Recommender service not initialized'}), 500
    
    try:
        top_k = request.args.get('top_k', settings.REC_TOP_K, type=int)
        
        logger.info(f"🎯 Recommend popular hotels")
        
        recommendations = recommender_service.recommend_popular(
            collection_name=settings.REC_COLLECTION_HOTELS,
            top_k=top_k
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        logger.error(f"Error in recommend popular: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/recommend/hybrid', methods=['POST'])
def recommend_hybrid():
    """Hybrid recommendation"""
    if not recommender_service:
        return jsonify({'error': 'Recommender service not initialized'}), 500
    
    try:
        data = request.json
        
        logger.info(f"🎯 Hybrid recommendation")
        
        recommendations = recommender_service.recommend_hybrid(
            query=data.get('query'),
            item_id=data.get('item_id'),
            collection_name=settings.REC_COLLECTION_HOTELS,
            top_k=data.get('top_k', settings.REC_TOP_K),
            semantic_weight=data.get('semantic_weight', 0.7),
            popularity_weight=data.get('popularity_weight', 0.3),
            filters=data.get('filters')
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        logger.error(f"Error in hybrid recommendation: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("="*70)
    logger.info("🏨 Unified Hotel Recommendation & RAG System v3.0")
    logger.info("="*70)
    
    # Initialize services
    try:
        initialize_services()
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        sys.exit(1)
    
    # Find free port
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
    
    port = find_free_port(settings.PORT)
    
    if port is None:
        logger.error(f"Could not find free port starting from {settings.PORT}")
        sys.exit(1)
    
    if port != settings.PORT:
        logger.warning(f"Port {settings.PORT} in use, using {port}")
    
    logger.info("")
    logger.info("📡 API Endpoints:")
    logger.info(f"   RAG Chat:        POST   http://localhost:{port}/api/chat")
    logger.info(f"   RAG Search:      POST   http://localhost:{port}/api/search")
    logger.info(f"   Recommend Query: POST   http://localhost:{port}/api/recommend/query")
    logger.info(f"   Recommend Similar: GET  http://localhost:{port}/api/recommend/similar/<id>")
    logger.info(f"   Recommend Popular: GET  http://localhost:{port}/api/recommend/popular")
    logger.info(f"   Hybrid Recommend: POST  http://localhost:{port}/api/recommend/hybrid")
    logger.info("")
    logger.info(f"🌐 Open http://localhost:{port} in your browser")
    logger.info("="*70)
    
    app.run(
        host=settings.HOST,
        port=port,
        debug=settings.DEBUG
    )

