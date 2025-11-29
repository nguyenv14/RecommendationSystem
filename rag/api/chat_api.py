#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Chat API Service
Flask API cho chat interface với RAG system
"""

# CRITICAL: Set environment variables BEFORE any imports to prevent PyTorch loading
import os
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TORCH_DISABLE_IMPORT'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import socket
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import logging
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from simple_rag_system import SimpleRAGSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set template and static folders to parent directory (where templates/ and static/ are)
BASE_DIR = Path(__file__).parent.parent
app = Flask(__name__, 
            template_folder=str(BASE_DIR / 'templates'),
            static_folder=str(BASE_DIR / 'static'))
app.secret_key = os.environ.get('SECRET_KEY', 'rag-chat-secret-key-change-in-production')
CORS(app)

# Global RAG system instance
rag_system: Optional[SimpleRAGSystem] = None


def check_coupons_indexed(rag_system: SimpleRAGSystem) -> bool:
    """Check if coupons are already indexed in the collection"""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        client = QdrantClient(url=rag_system.qdrant_url)
        
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if rag_system.collection_name not in collection_names:
            return False
        
        # Search for documents with document_type="coupon"
        # In Qdrant, metadata is stored directly, not nested under "metadata"
        filter_condition = Filter(
            must=[
                FieldCondition(
                    key="document_type",
                    match=MatchValue(value="coupon")
                )
            ]
        )
        
        # Try to get at least one coupon document
        results = client.scroll(
            collection_name=rag_system.collection_name,
            scroll_filter=filter_condition,
            limit=1
        )
        
        return len(results[0]) > 0
    except Exception as e:
        logger.warning(f"Could not check if coupons are indexed: {e}")
        # If check fails, assume not indexed to be safe (will try to index)
        return False


def initialize_rag_system():
    """Initialize RAG system"""
    global rag_system
    
    if rag_system is not None:
        return rag_system
    
    logger.info("Initializing RAG system...")
    
    # Get configuration from environment or use defaults
    ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
    qdrant_url = os.environ.get('QDRANT_URL', 'http://localhost:6333')
    embedding_model = os.environ.get('EMBEDDING_MODEL', 'bge-m3')
    llm_model = os.environ.get('LLM_MODEL', 'qwen3')
    collection_name = os.environ.get('COLLECTION_NAME', 'hotels')
    llm_provider = os.environ.get('LLM_PROVIDER', 'ollama')  # 'ollama' or 'lm_studio'
    lm_studio_url = os.environ.get('LM_STUDIO_URL', None)  # e.g., 'http://192.168.10.42:1234'
    
    # Auto-index coupons on startup (can be disabled via env var)
    auto_index_coupons = os.environ.get('AUTO_INDEX_COUPONS', 'true').lower() == 'true'
    
    rag_system = SimpleRAGSystem(
        ollama_url=ollama_url,
        qdrant_url=qdrant_url,
        embedding_model=embedding_model,
        llm_model=llm_model,
        collection_name=collection_name,
        llm_provider=llm_provider,
        lm_studio_url=lm_studio_url
    )
    
    # Try to load existing vectorstore
    try:
        rag_system.load_vectorstore()
        logger.info("✅ Loaded existing vectorstore")
        
        # Auto-index coupons if enabled and not already indexed
        if auto_index_coupons:
            try:
                coupons_indexed = check_coupons_indexed(rag_system)
                if not coupons_indexed:
                    logger.info("🔄 Coupons not found in collection, auto-indexing coupons...")
                    rag_system.index_coupons_from_database(
                        use_chunking=True,
                        incremental=False,  # Don't recreate, just add
                        recreate_collection=False,
                        valid_only=True  # Only index valid coupons
                    )
                    logger.info("✅ Coupons auto-indexed successfully")
                else:
                    logger.info("✅ Coupons already indexed in collection")
            except Exception as e:
                logger.warning(f"⚠️  Could not auto-index coupons: {e}")
                logger.info("You can manually index coupons later using index_coupons_from_database()")
        else:
            logger.info("ℹ️  Auto-index coupons is disabled (set AUTO_INDEX_COUPONS=true to enable)")
            
    except Exception as e:
        logger.error(f"❌ Error loading vectorstore: {e}")
        logger.info("Please run index_hotels() first or set up the collection")
        rag_system = None
    
    return rag_system


@app.route('/')
def index():
    """Render chat interface"""
    return render_template('chat.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    global rag_system
    
    rag_initialized = rag_system is not None
    
    if rag_initialized:
        try:
            # Try to check Qdrant connection
            from qdrant_client import QdrantClient
            client = QdrantClient(url=rag_system.qdrant_url)
            collections = client.get_collections()
            qdrant_connected = True
        except Exception as e:
            logger.error(f"Qdrant connection error: {e}")
            qdrant_connected = False
    else:
        qdrant_connected = False
    
    return jsonify({
        'status': 'ok' if rag_initialized and qdrant_connected else 'error',
        'rag_initialized': rag_initialized,
        'qdrant_connected': qdrant_connected
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint - Ask question to RAG system"""
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
            return jsonify({
                'error': 'Question is required'
            }), 400
        
        logger.info(f"Received question: {question}")
        
        # Get answer from RAG system
        response = rag_system.ask(question)
        
        # Format response for frontend
        return jsonify({
            'success': True,
            'question': response['question'],
            'answer': response['answer'],
            'sources': response['sources']
        })
        
    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        return jsonify({
            'error': f'Error processing question: {str(e)}'
        }), 500


@app.route('/api/search', methods=['POST'])
def search():
    """Search endpoint - Semantic search only (no LLM)"""
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
            return jsonify({
                'error': 'Query is required'
            }), 400
        
        logger.info(f"Received search query: {query}")
        
        # Get search results - use optimized search if available
        # Use search_hotels_optimized for better performance
        try:
            # Try optimized search first (faster)
            results = rag_system.search_hotels_optimized(query, top_k=top_k, ef=50)
        except Exception:
            # Fallback to regular search
            results = rag_system.search_hotels(query, top_k=top_k)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error processing search: {e}", exc_info=True)
        return jsonify({
            'error': f'Error processing search: {str(e)}'
        }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Get RAG system status"""
    global rag_system
    
    if rag_system is None:
        return jsonify({
            'initialized': False,
            'message': 'RAG system not initialized'
        })
    
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=rag_system.qdrant_url)
        collection = client.get_collection(rag_system.collection_name)
        
        return jsonify({
            'initialized': True,
            'collection_name': rag_system.collection_name,
            'points_count': collection.points_count,
            'vector_size': collection.config.params.vectors.size,
            'embedding_model': rag_system.embedding_model,
            'llm_model': rag_system.llm_model
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'initialized': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Initialize RAG system on startup
    initialize_rag_system()
    
    # Get port from environment or use default
    default_port = int(os.environ.get('PORT', 5001))  # Changed default to 5001
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Find available port
    def find_free_port(start_port):
        port = start_port
        while port < start_port + 100:  # Try up to 100 ports
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
    
    logger.info(f"Starting RAG Chat API on port {port}")
    logger.info(f"🌐 Open http://localhost:{port} in your browser")
    app.run(host='0.0.0.0', port=port, debug=debug)

