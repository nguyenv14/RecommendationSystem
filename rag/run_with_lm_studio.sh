#!/bin/bash
# Script to run RAG Chat API với LM Studio

set -e

# Get script directory and cd to it
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 Starting RAG Chat API với LM Studio..."

# Activate virtual environment if exists
if [ -d "venv_rag" ]; then
    echo "📦 Activating virtual environment..."
    source venv_rag/bin/activate
fi

# LM Studio configuration
export LLM_PROVIDER="lm_studio"
export LM_STUDIO_URL="http://127.0.0.1:1234"
export LLM_MODEL="qwen/qwen3-4b-2507"

# Other configuration (vẫn dùng Ollama cho embeddings)
export OLLAMA_URL=${OLLAMA_URL:-"http://localhost:11434"}
export QDRANT_URL=${QDRANT_URL:-"http://localhost:6333"}
export EMBEDDING_MODEL=${EMBEDDING_MODEL:-"bge-m3"}
export COLLECTION_NAME=${COLLECTION_NAME:-"hotels"}
export PORT=${PORT:-5001}
export DEBUG=${DEBUG:-"False"}

# Check LM Studio
echo "🔍 Checking LM Studio..."
if curl -s "$LM_STUDIO_URL/v1/models" > /dev/null 2>&1; then
    echo "✅ LM Studio is running on $LM_STUDIO_URL"
    # List available models
    echo "📋 Available models:"
    curl -s "$LM_STUDIO_URL/v1/models" | python3 -c "import sys, json; models = json.load(sys.stdin); [print(f'   - {m[\"id\"]}') for m in models.get('data', [])]" 2>/dev/null || echo "   (Could not list models)"
else
    echo "❌ Error: LM Studio is not running on $LM_STUDIO_URL"
    echo "   Please start LM Studio:"
    echo "   1. Open LM Studio"
    echo "   2. Go to 'Developer' tab"
    echo "   3. Click 'Start Server'"
    echo "   4. Set address to $LM_STUDIO_URL"
    exit 1
fi

# Check Ollama (for embeddings)
echo "🔍 Checking Ollama (for embeddings)..."
if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama is running on $OLLAMA_URL"
else
    echo "⚠️  Warning: Ollama is not running on $OLLAMA_URL"
    echo "   Embeddings require Ollama. Please start Ollama:"
    echo "   - macOS: brew services start ollama"
    echo "   - Or run: ollama serve"
fi

# Check Qdrant
echo "🔍 Checking Qdrant..."
if curl -s "$QDRANT_URL/health" > /dev/null 2>&1; then
    echo "✅ Qdrant is running on $QDRANT_URL"
else
    echo "❌ Error: Qdrant is not running on $QDRANT_URL"
    echo "   Please start Qdrant first:"
    echo "   - Docker: docker-compose up -d qdrant"
    echo "   - Or: docker run -p 6333:6333 qdrant/qdrant"
    exit 1
fi

echo ""
echo "📋 Configuration:"
echo "   LLM Provider: $LLM_PROVIDER"
echo "   LM Studio URL: $LM_STUDIO_URL"
echo "   LLM Model: $LLM_MODEL"
echo "   Ollama URL (for embeddings): $OLLAMA_URL"
echo "   Embedding Model: $EMBEDDING_MODEL"
echo "   Qdrant URL: $QDRANT_URL"
echo "   Collection: $COLLECTION_NAME"
echo "   Port: $PORT"
echo ""

# Test LM Studio connection
echo "🧪 Testing LM Studio connection..."
if curl -s -X POST "$LM_STUDIO_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "{\"model\": \"$LLM_MODEL\", \"messages\": [{\"role\": \"user\", \"content\": \"test\"}], \"max_tokens\": 5}" \
    > /dev/null 2>&1; then
    echo "✅ LM Studio connection test successful"
else
    echo "⚠️  Warning: LM Studio connection test failed"
    echo "   Model may need to be loaded in LM Studio"
fi

echo ""
echo "🌐 Starting Flask API server..."
echo "   API will be available at: http://localhost:$PORT"
echo ""

python api/chat_api.py

