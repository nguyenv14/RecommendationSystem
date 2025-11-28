#!/bin/bash
# =============================================================================
# Install Script for Hotel Recommendation & RAG System
# Python 3.9+ Compatible
# =============================================================================

set -e  # Exit on error

echo "🚀 Installing dependencies for Hotel Recommendation & RAG System"
echo "=================================================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $PYTHON_VERSION"

# Check if Python 3.9+
if ! python3 -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
    echo "❌ Error: Python 3.9 or higher is required"
    echo "   Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📥 Installing dependencies from requirements-python39.txt..."
pip install -r requirements-python39.txt

# Verify installations
echo ""
echo "🔍 Verifying key installations..."
echo "--------------------------------"

# Check Flask
python3 -c "import flask; print(f'✅ Flask: {flask.__version__}')" || echo "❌ Flask not installed"

# Check Pandas
python3 -c "import pandas; print(f'✅ Pandas: {pandas.__version__}')" || echo "❌ Pandas not installed"

# Check SQLAlchemy
python3 -c "import sqlalchemy; print(f'✅ SQLAlchemy: {sqlalchemy.__version__}')" || echo "❌ SQLAlchemy not installed"

# Check LangChain
python3 -c "import langchain; print(f'✅ LangChain: {langchain.__version__}')" || echo "❌ LangChain not installed"

# Check Qdrant
python3 -c "import qdrant_client; print(f'✅ Qdrant Client: {qdrant_client.__version__}')" || echo "❌ Qdrant not installed"

# Check Pydantic
python3 -c "import pydantic; print(f'✅ Pydantic: {pydantic.__version__}')" || echo "❌ Pydantic not installed"

# Check OpenAI
python3 -c "import openai; print(f'✅ OpenAI: {openai.__version__}')" || echo "❌ OpenAI not installed"

echo ""
echo "=================================================================="
echo "✅ Installation completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Configure environment: cp env.example .env"
echo "   3. Setup collections: python setup_collections.py"
echo "   4. Run application: python app.py"
echo ""
echo "📚 For more information, see:"
echo "   - README.md"
echo "   - SETUP_GUIDE.md"
echo "   - QUICK_START.md"
echo "=================================================================="

