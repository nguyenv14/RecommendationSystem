#!/bin/bash
# Script to run RAG Chat API

set -e

# Get script directory and cd to it
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting RAG Chat API..."

# Activate virtual environment if exists
if [ -d "venv_rag" ]; then
    echo "📦 Activating virtual environment..."
    source venv_rag/bin/activate
fi

# Set environment variables (optional)
export OLLAMA_URL=${OLLAMA_URL:-"http://localhost:11434"}
export QDRANT_URL=${QDRANT_URL:-"http://localhost:6333"}
export EMBEDDING_MODEL=${EMBEDDING_MODEL:-"bge-m3"}
export LLM_MODEL=${LLM_MODEL:-"qwen3"}
export COLLECTION_NAME=${COLLECTION_NAME:-"hotels"}
export LLM_PROVIDER=${LLM_PROVIDER:-"ollama"}  # 'ollama' or 'lm_studio'
export LM_STUDIO_URL=${LM_STUDIO_URL:-""}  # e.g., 'http://192.168.10.42:1234'
export PORT=${PORT:-5001}
export DEBUG=${DEBUG:-"False"}

# Check services based on LLM_PROVIDER
if [ "$LLM_PROVIDER" = "lm_studio" ]; then
    echo "🔍 Checking LM Studio..."
    if [ -z "$LM_STUDIO_URL" ]; then
        echo "⚠️  Warning: LM_STUDIO_URL is not set"
        echo "   Please set LM_STUDIO_URL environment variable:"
        echo "   export LM_STUDIO_URL=http://192.168.10.42:1234"
        echo "   Or set it in this script"
    else
        if ! curl -s "$LM_STUDIO_URL/v1/models" > /dev/null 2>&1; then
            echo "⚠️  Warning: LM Studio is not running on $LM_STUDIO_URL"
            echo "   Please start LM Studio first:"
            echo "   - Open LM Studio and go to 'Developer' tab"
            echo "   - Click 'Start Server'"
            echo "   - Set address to $LM_STUDIO_URL"
        else
            echo "✅ LM Studio is running on $LM_STUDIO_URL"
        fi
    fi
else
    echo "🔍 Checking Ollama..."
    if ! curl -s $OLLAMA_URL/api/tags > /dev/null 2>&1; then
        echo "⚠️  Warning: Ollama is not running on $OLLAMA_URL"
        echo "   Please start Ollama first:"
        echo "   - macOS: brew services start ollama"
        echo "   - Or run: ollama serve"
    else
        echo "✅ Ollama is running on $OLLAMA_URL"
    fi
fi

# Check if Qdrant is running
echo "🔍 Checking Qdrant..."
if ! curl -s $QDRANT_URL/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Qdrant is not running on $QDRANT_URL"
    echo "   Please start Qdrant first:"
    echo "   - Docker: docker-compose up -d qdrant"
    echo "   - Or: docker run -p 6333:6333 qdrant/qdrant"
else
    echo "✅ Qdrant is running on $QDRANT_URL"
fi

echo ""
echo "📋 Configuration:"
echo "   LLM Provider: $LLM_PROVIDER"
if [ "$LLM_PROVIDER" = "lm_studio" ]; then
    echo "   LM Studio URL: $LM_STUDIO_URL"
else
    echo "   Ollama URL: $OLLAMA_URL"
fi
echo "   Qdrant URL: $QDRANT_URL"
echo "   Embedding Model: $EMBEDDING_MODEL"
echo "   LLM Model: $LLM_MODEL"
echo "   Collection: $COLLECTION_NAME"
echo "   Port: $PORT"
echo ""

# Run Flask app
echo "🌐 Starting Flask API server..."
python api/chat_api.py

