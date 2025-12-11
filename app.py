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
from src.shared import get_logger, setup_logging, ApiResponse
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
    """
    Health check
    Compatible với frontend chat.js (expects rag_initialized & qdrant_connected)
    """
    # RAG service initialized (based on service + collection having data)
    rag_initialized = rag_service is not None

    # Qdrant connection & collection status
    qdrant_connected = False
    try:
        if vectorstore_service is not None:
            # Thử gọi get_collections() để kiểm tra kết nối
            collections = vectorstore_service.client.get_collections()  # type: ignore[attr-defined]
            _ = len(collections.collections)
            qdrant_connected = True
    except Exception:
        qdrant_connected = False

    # Nếu RAG service và Qdrant đều OK, cố gắng kiểm tra collection points
    if rag_initialized and qdrant_connected:
        try:
            info = vectorstore_service.get_collection_info(settings.RAG_COLLECTION_HOTELS)  # type: ignore[arg-type]
            if info and getattr(info, "points_count", 0) == 0:
                # Collection tồn tại nhưng chưa có dữ liệu
                rag_initialized = False
        except Exception:
            # Nếu check fail thì giữ nguyên rag_initialized
            pass

    status = 'ok' if rag_initialized and qdrant_connected else 'error'
    status_code = 200 if status == 'ok' else 503

    return ApiResponse.success(
        data={
            'status': status,
            'version': '3.0',
            'rag_initialized': rag_initialized,
            'qdrant_connected': qdrant_connected,
            'services': {
                'rag': rag_service is not None,
                'recommendation': recommender_service is not None,
                'embedding': embedding_service is not None,
                'vectorstore': vectorstore_service is not None
            }
        },
        message='Service health check',
        code=status_code
    )


@app.route('/api/status')
def status():
    """Detailed status"""
    try:
        rag_stats = rag_service.get_stats() if rag_service else {}
        
        return ApiResponse.success(
            data={
                'version': '3.0',
                'rag': rag_stats,
                'collections': {
                    'rag_hotels': settings.RAG_COLLECTION_HOTELS,
                    'rag_coupons': settings.RAG_COLLECTION_HOTELS,
                    'rec_hotels': settings.REC_COLLECTION_HOTELS
                }
            },
            message='Service status retrieved successfully'
        )
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return ApiResponse.error(
            message=f'Error getting status: {str(e)}',
            code=500
        )


# ==================== RAG Endpoints ====================

@app.route('/api/chat', methods=['POST'])
@app.route('/api/rag/chat', methods=['POST'])
def chat():
    """RAG chat endpoint"""
    if not rag_service:
        return ApiResponse.error(
            message='RAG service not initialized',
            code=500
        )
    
    try:
        data = request.json
        question = data.get('question', '').strip()
        
        if not question:
            return ApiResponse.error(
                message='Question is required',
                code=400
            )
        
        logger.info(f"💬 Chat: {question[:50]}...")
        
        # Get answer
        result = rag_service.ask(
            question=question,
            top_k=data.get('top_k', settings.RAG_TOP_K),
            filters=data.get('filters')
        )
        
        return ApiResponse.success(
            data=result,
            message='Chat response generated successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return ApiResponse.error(
            message=f'Error processing chat: {str(e)}',
            code=500
        )


@app.route('/api/search', methods=['POST'])
@app.route('/api/rag/search', methods=['POST'])
def search():
    """RAG search endpoint (retrieval only)"""
    if not rag_service:
        return ApiResponse.error(
            message='RAG service not initialized',
            code=500
        )
    
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return ApiResponse.error(
                message='Query is required',
                code=400
            )
        
        logger.info(f"🔍 Search: {query[:50]}...")
        
        # Search
        results = rag_service.search(
            query=query,
            top_k=data.get('top_k', settings.RAG_TOP_K),
            filters=data.get('filters')
        )
        
        return ApiResponse.success(
            data={
                'query': query,
                'results': results,
                'count': len(results)
            },
            message='Search completed successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return ApiResponse.error(
            message=f'Error processing search: {str(e)}',
            code=500
        )


# ==================== Recommendation Endpoints ====================

@app.route('/api/recommend/query', methods=['POST'])
@app.route('/api/hotels/search', methods=['POST'])
def recommend_by_query():
    """Recommend hotels by query"""
    if not recommender_service:
        return ApiResponse.error(
            message='Recommender service not initialized',
            code=500
        )
    
    try:
        data = request.json
        query = data.get('query', '').strip()
        
        if not query:
            return ApiResponse.error(
                message='Query is required',
                code=400
            )
        
        logger.info(f"🎯 Recommend by query: {query[:50]}...")
        
        recommendations = recommender_service.recommend_by_query(
            query=query,
            collection_name=settings.REC_COLLECTION_HOTELS,
            top_k=data.get('top_k', settings.REC_TOP_K),
            filters=data.get('filters')
        )
        
        return ApiResponse.success(
            data={
                'query': query,
                'recommendations': recommendations,
                'count': len(recommendations)
            },
            message='Recommendations generated successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in recommend by query: {e}")
        return ApiResponse.error(
            message=f'Error generating recommendations: {str(e)}',
            code=500
        )


def apply_filters(results: list, filters: dict) -> list:
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


def rerank_by_intent(results: list, processed_query: dict, top_k: int) -> list:
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
    if not recommender_service:
        return ApiResponse.error(
            message='Recommender service not initialized',
            code=500
        )
    
    try:
        data = request.json
        if not data or 'query' not in data:
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
        
        # Step 2: Semantic search (get more results for filtering)
        # Use retriever directly to get raw results with scores
        results = recommender_service.retriever.retrieve(
            query=query,
            collection_name=settings.REC_COLLECTION_HOTELS,
            top_k=top_k * 3,  # Get more results for filtering
            filters=None  # Don't use Qdrant filters, we'll filter manually
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


@app.route('/api/recommend/similar/<item_id>', methods=['GET'])
@app.route('/api/hotels/<item_id>/similar', methods=['GET'])
def recommend_similar(item_id):
    """Recommend similar hotels"""
    if not recommender_service:
        return ApiResponse.error(
            message='Recommender service not initialized',
            code=500
        )
    
    try:
        top_k = request.args.get('top_k', settings.REC_TOP_K, type=int)
        
        logger.info(f"🎯 Recommend similar for item_id={item_id}")
        
        recommendations = recommender_service.recommend_similar(
            item_id=item_id,
            collection_name=settings.REC_COLLECTION_HOTELS,
            top_k=top_k
        )
        
        return ApiResponse.success(
            data={
                'item_id': item_id,
                'recommendations': recommendations,
                'count': len(recommendations)
            },
            message='Similar recommendations generated successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in recommend similar: {e}")
        return ApiResponse.error(
            message=f'Error generating similar recommendations: {str(e)}',
            code=500
        )


@app.route('/api/recommend/popular', methods=['GET'])
@app.route('/api/hotels/popular', methods=['GET'])
def recommend_popular():
    """Recommend popular hotels"""
    if not recommender_service:
        return ApiResponse.error(
            message='Recommender service not initialized',
            code=500
        )
    
    try:
        top_k = request.args.get('top_k', settings.REC_TOP_K, type=int)
        
        logger.info(f"🎯 Recommend popular hotels")
        
        recommendations = recommender_service.recommend_popular(
            collection_name=settings.REC_COLLECTION_HOTELS,
            top_k=top_k
        )
        
        return ApiResponse.success(
            data={
                'recommendations': recommendations,
                'count': len(recommendations)
            },
            message='Popular recommendations generated successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in recommend popular: {e}")
        return ApiResponse.error(
            message=f'Error generating popular recommendations: {str(e)}',
            code=500
        )


@app.route('/api/recommend/hybrid', methods=['POST'])
def recommend_hybrid():
    """Hybrid recommendation"""
    if not recommender_service:
        return ApiResponse.error(
            message='Recommender service not initialized',
            code=500
        )
    
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
        
        return ApiResponse.success(
            data={
                'recommendations': recommendations,
                'count': len(recommendations)
            },
            message='Hybrid recommendations generated successfully'
        )
        
    except Exception as e:
        logger.error(f"Error in hybrid recommendation: {e}")
        return ApiResponse.error(
            message=f'Error generating hybrid recommendations: {str(e)}',
            code=500
        )


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
    logger.info(f"   Semantic Search: POST   http://localhost:{port}/api/hotels/semantic-search")
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

