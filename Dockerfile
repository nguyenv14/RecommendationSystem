# Dockerfile for Unified API Service (RAG + Recommendation)
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements-python39.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY src/ ./src/
COPY rag/ ./rag/
COPY recommendation/ ./recommendation/
COPY scripts/ ./scripts/
COPY setup_collections.py .
COPY index_with_hybrid.py .

# Create directories for datasets and processed data
# These will be mounted as volumes in docker-compose, but create for standalone use
RUN mkdir -p ./datasets_extracted ./processed

# Create necessary directories
RUN mkdir -p /app/.embedding_cache /app/logs && \
    chmod -R 755 /app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the unified API service
CMD ["python", "app.py"]

