#!/bin/bash
# Script to pull required Ollama models
# Note: Only pulls embedding model (bge-m3)
# LLM (qwen3) uses LM Studio, not Ollama

echo "📥 Pulling Ollama Embedding Model..."
echo "====================================="

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Error: Ollama is not running"
    echo "   Please start Ollama first"
    exit 1
fi

echo ""
echo "ℹ️  Note: This script only pulls embedding model (bge-m3)"
echo "   LLM model (qwen3) uses LM Studio, not Ollama"
echo ""

# Pull embedding model (bge-m3)
echo "📥 Pulling bge-m3 (embedding model)..."
ollama pull bge-m3

echo ""
echo "✅ Done!"
echo ""
echo "📊 Installed Ollama models:"
ollama list
echo ""
echo "💡 For LLM (qwen3), make sure LM Studio is running with qwen3 model loaded"
echo "   LM Studio URL: http://localhost:1234"

