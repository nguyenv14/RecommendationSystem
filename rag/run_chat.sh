#!/bin/bash
# Script to run RAG Chat API

set -e

echo "🚀 Starting RAG Chat API..."

# Activate virtual environment if exists
if [ -d "venv_rag" ]; then
    echo "📦 Activating virtual environment..."
    source venv_rag/bin/activate
fi

# Check if Ollama is running
echo "🔍 Checking Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama is not running on http://localhost:11434"
    echo "   Please start Ollama first:"
    echo "   - macOS: brew services start ollama"
    echo "   - Or run: ollama serve"
fi

# Check if Qdrant is running
echo "🔍 Checking Qdrant..."
if ! curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Qdrant is not running on http://localhost:6333"
    echo "   Please start Qdrant first:"
    echo "   - Docker: docker-compose up -d qdrant"
    echo "   - Or: docker run -p 6333:6333 qdrant/qdrant"
fi

# Set environment variables (optional)
export OLLAMA_URL=${OLLAMA_URL:-"http://localhost:11434"}
export QDRANT_URL=${QDRANT_URL:-"http://localhost:6333"}
export EMBEDDING_MODEL=${EMBEDDING_MODEL:-"bge-m3"}
export LLM_MODEL=${LLM_MODEL:-"qwen3"}
export COLLECTION_NAME=${COLLECTION_NAME:-"hotels"}
export PORT=${PORT:-5001}
export DEBUG=${DEBUG:-"False"}

echo ""
echo "📋 Configuration:"
echo "   Ollama URL: $OLLAMA_URL"
echo "   Qdrant URL: $QDRANT_URL"
echo "   Embedding Model: $EMBEDDING_MODEL"
echo "   LLM Model: $LLM_MODEL"
echo "   Collection: $COLLECTION_NAME"
echo "   Port: $PORT"
echo ""

# Run Flask app
echo "🌐 Starting Flask API server..."
python rag_chat_api.py

