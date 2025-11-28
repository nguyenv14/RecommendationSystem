#!/bin/bash
# Script to uninstall PyTorch and related packages from venv
# This helps reduce memory usage on Mac

set -e

echo "🗑️  Uninstalling PyTorch and related packages..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment if exists
if [ -d "venv_rag" ]; then
    echo "📦 Activating virtual environment..."
    source venv_rag/bin/activate
elif [ -d "../venv" ]; then
    echo "📦 Activating parent virtual environment..."
    source ../venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python..."
fi

# Uninstall PyTorch and related packages
echo "🔍 Uninstalling packages..."
pip uninstall -y torch torchvision torchaudio sentence-transformers transformers 2>/dev/null || true

echo "✅ PyTorch and related packages uninstalled!"
echo ""
echo "📝 Note: These packages are not needed because:"
echo "   - This system uses Ollama for embeddings (runs on server)"
echo "   - This system uses Ollama/LM Studio for LLM (runs on server)"
echo "   - No local PyTorch models are used"
echo ""
echo "💡 If you need to reinstall dependencies, run:"
echo "   pip install -r requirements_rag.txt"

