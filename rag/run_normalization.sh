#!/bin/bash
# Script to run hotel data normalization

set -e

echo "🔧 Running Hotel Data Normalization..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import pandas, numpy, json" 2>/dev/null || {
    echo "❌ Missing required packages. Installing..."
    pip install pandas numpy
}

# Check if data files exist
DATA_DIR="../datasets_extracted"
if [ ! -f "$DATA_DIR/tbl_hotel.csv" ]; then
    echo "❌ Data file not found: $DATA_DIR/tbl_hotel.csv"
    echo "   Please ensure datasets_extracted folder exists in project root"
    exit 1
fi

# Create output directory
OUTPUT_DIR="normalized_data"
mkdir -p "$OUTPUT_DIR"
echo "📁 Output directory: $OUTPUT_DIR"

# Run normalization script
echo "🚀 Starting normalization..."
python3 hotel_data_normalization.py

echo ""
echo "✅ Normalization complete!"
echo "📁 Output files saved in: $OUTPUT_DIR"
echo ""

