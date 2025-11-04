#!/bin/bash
# Setup script for RAG project

set -e

echo "🚀 Setting up RAG Project Environment..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv_rag" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv_rag
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate venv
echo "🔧 Activating virtual environment..."
source venv_rag/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements_rag.txt" ]; then
    pip install -r requirements_rag.txt
else
    echo "⚠️  requirements_rag.txt not found, installing basic packages..."
    pip install langchain langchain-community langchain-core qdrant-client pandas numpy requests
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 To activate virtual environment:"
echo "   source venv_rag/bin/activate"
echo ""
echo "📝 To deactivate:"
echo "   deactivate"
echo ""

