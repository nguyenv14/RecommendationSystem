#!/bin/bash
# Script to activate virtual environment and run the improved recommendation system

echo "🚀 Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated!"
echo "📦 Installed packages:"
pip list | grep -E "(numpy|pandas|tensorflow|pyarrow)"

echo ""
echo "🎯 To run the improved recommendation system:"
echo "python improved_recommendation_system.py"
echo ""
echo "💡 Or run this script directly:"
echo "./run_recommendation.sh"
