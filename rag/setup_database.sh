#!/bin/bash
# Setup database script

set -e

echo "🔧 Setting up database for RAG system..."

# Check if MySQL container is running
if ! docker ps | grep -q mysql_rag; then
    echo "❌ MySQL container is not running"
    echo "   Please start MySQL container first:"
    echo "   docker-compose up -d mysql"
    exit 1
fi

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 5

# Import SQL file
echo "📦 Importing SQL file..."
if [ -f "myhotel.sql" ]; then
    docker exec -i mysql_rag mysql -uroot -proot rag_db < myhotel.sql
    echo "✅ SQL file imported successfully"
else
    echo "⚠️  SQL file not found: myhotel.sql"
    echo "   Please ensure myhotel.sql exists in the current directory"
    exit 1
fi

# Create RAG metadata table
echo "📦 Creating RAG metadata table..."
if [ -f "create_rag_metadata_table.sql" ]; then
    docker exec -i mysql_rag mysql -uroot -proot rag_db < create_rag_metadata_table.sql
    echo "✅ RAG metadata table created successfully"
else
    echo "⚠️  SQL file not found: create_rag_metadata_table.sql"
    echo "   Table will be created automatically on first use"
fi

# Verify database
echo "🔍 Verifying database..."
docker exec -i mysql_rag mysql -uroot -proot rag_db -e "SELECT COUNT(*) as hotel_count FROM tbl_hotel;" || {
    echo "❌ Database verification failed"
    exit 1
}

echo "✅ Database setup complete!"
echo ""
echo "📊 Next steps:"
echo "   1. Run: python test_database_indexing.py"
echo "   2. Or run: python -c 'from simple_rag_system import SimpleRAGSystem; rag = SimpleRAGSystem(); rag.index_hotels_from_database(recreate_collection=True)'"
echo ""

