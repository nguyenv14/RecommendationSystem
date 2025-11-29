#!/bin/bash
# =============================================================================
# Setup Script - Force Python 3.9
# =============================================================================

echo "🚀 Setting up with Python 3.9"
echo "=================================================================="

# Check if python3.9 exists
if ! command -v python3.9 &> /dev/null; then
    echo "❌ python3.9 not found!"
    echo ""
    echo "Please install Python 3.9:"
    echo "  macOS: brew install python@3.9"
    echo "  Ubuntu: sudo apt install python3.9 python3.9-venv python3.9-dev"
    echo ""
    exit 1
fi

echo "✅ Found: $(python3.9 --version)"

# Remove old venv
if [ -d "venv" ]; then
    echo "🗑️  Removing old venv (Python 3.10)..."
    rm -rf venv
fi

# Clean Python cache
echo "🧹 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Create new venv with Python 3.9
echo "📦 Creating venv with Python 3.9..."
python3.9 -m venv venv

# Activate venv
source venv/bin/activate

# Verify Python version in venv
echo "✅ Virtual environment created"
python --version

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "📥 Installing all dependencies..."
pip install -r requirements-python39.txt

# Verify
echo ""
echo "=================================================================="
echo "✅ Installation Complete!"
echo ""
echo "📊 Verification:"
python << 'EOF'
import sys
print(f"Python: {sys.version}")
print("-" * 60)

try:
    import flask
    print(f"✅ Flask: {flask.__version__}")
except: print("❌ Flask failed")

try:
    import qdrant_client
    print(f"✅ Qdrant: {qdrant_client.__version__}")
except: print("❌ Qdrant failed")

try:
    import pydantic
    print(f"✅ Pydantic: {pydantic.__version__}")
except: print("❌ Pydantic failed")

try:
    import langchain
    print(f"✅ LangChain: {langchain.__version__}")
except: print("❌ LangChain failed")
EOF

echo ""
echo "=================================================================="
echo "🎯 Next Steps:"
echo ""
echo "1. Activate venv (always do this first):"
echo "   source venv/bin/activate"
echo ""
echo "2. Setup collections:"
echo "   python setup_collections.py"
echo ""
echo "3. Run application:"
echo "   python app.py"
echo ""
echo "=================================================================="

