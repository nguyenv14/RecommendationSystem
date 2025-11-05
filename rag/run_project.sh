#!/bin/bash
# Quick start script for RAG project

set -e

echo "🚀 Starting RAG Project..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Setup venv
echo ""
echo "📦 Step 1: Setup Virtual Environment"
echo "============================================================"

if [ ! -d "venv_rag" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv_rag
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate venv
echo "Activating virtual environment..."
source venv_rag/bin/activate

# Step 2: Install dependencies
echo ""
echo "📦 Step 2: Install Dependencies"
echo "============================================================"

# Upgrade pip
pip install --upgrade pip --quiet

# Install dependencies
if [ -f "requirements_rag.txt" ]; then
    echo "Installing from requirements_rag.txt..."
    pip install -r requirements_rag.txt --quiet
else
    echo "Installing basic packages..."
    pip install langchain langchain-community langchain-core qdrant-client pandas numpy requests --quiet
fi

echo "✅ Dependencies installed"

# Step 3: Start services
echo ""
echo "🐳 Step 3: Start Docker Services"
echo "============================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start services
echo "Starting Qdrant and Redis..."
docker-compose up -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 5

# Check Qdrant
echo "Checking Qdrant..."
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "✅ Qdrant is healthy"
else
    echo "⚠️  Qdrant health check failed (may need more time)"
fi

# Check Redis
echo "Checking Redis..."
if docker exec redis_rag redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "⚠️  Redis health check failed (optional service)"
fi

# Step 4: Check Ollama
echo ""
echo "🤖 Step 4: Check Ollama"
echo "============================================================"

if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Warning: Ollama is not running on port 11434"
    echo "   Make sure Ollama is running: http://localhost:11434"
fi

# Step 5: Normalize data (if needed)
echo ""
echo "📊 Step 5: Normalize Data"
echo "============================================================"

if [ ! -f "normalized_data/normalized_hotels.csv" ]; then
    echo "Normalized data not found. Running normalization..."
    python3 hotel_data_normalization.py
    echo "✅ Data normalized"
else
    echo "✅ Normalized data already exists"
fi

# Step 6: Test RAG system
echo ""
echo "🧪 Step 6: Test RAG System"
echo "============================================================"

echo "Running RAG system test..."
python3 test_rag.py

echo ""
echo "✅ Project setup complete!"
echo ""
echo "📝 Next steps:"
echo "   - Activate venv: source venv_rag/bin/activate"
echo "   - Run RAG: python3 simple_rag_system.py"
echo "   - Test: python3 test_rag.py"
echo ""

