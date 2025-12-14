#!/bin/bash
# Script to run hybrid indexing inside Docker container

echo "🔧 Running Hybrid Search Indexing in Docker container..."
echo "=================================================="

# Check if container is running
if ! docker ps | grep -q unified_api; then
    echo "❌ Error: unified_api container is not running"
    echo "   Please start it first: docker-compose up -d"
    exit 1
fi

echo ""
echo "📊 This will:"
echo "   1. Create dense embeddings (semantic) from Ollama"
echo "   2. Create sparse embeddings (BM25) from fastembed"
echo "   3. Upload to Qdrant with hybrid vectors"
echo ""
echo "⚠️  This may take 5-10 minutes depending on data size"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🚀 Running index_with_hybrid.py in container..."
echo ""

# Run index script in container
docker-compose exec unified_api python index_with_hybrid.py

echo ""
echo "✅ Done!"
echo ""
echo "💡 To check collections status:"
echo "   docker-compose exec unified_api python -c \"from src.core import VectorStoreService; from src.config import get_settings; vs = VectorStoreService(url=get_settings().QDRANT_URL); [print(f'{c.name}: {vs.client.get_collection(c.name).points_count} points') for c in vs.client.get_collections().collections]\""


