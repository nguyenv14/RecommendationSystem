# RAG System Documentation

## 📚 Documentation Index

- **[README.md](./README.md)** - Main documentation
- **[RAG_ARCHITECTURE.md](./RAG_ARCHITECTURE.md)** - System architecture
- **[RAG_FLOW_EXPLANATION.md](./RAG_FLOW_EXPLANATION.md)** - Query flow explanation
- **[QUERY_EXTRACTION.md](./QUERY_EXTRACTION.md)** - Keyword extraction guide
- **[LM_STUDIO_SETUP.md](./LM_STUDIO_SETUP.md)** - LM Studio setup guide
- **[REFACTOR_GUIDE.md](./REFACTOR_GUIDE.md)** - Refactoring guide

## 🏗️ Project Structure

See [../PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) for complete folder structure.

## 🚀 Quick Start

1. **Setup environment**:
   ```bash
   ./setup_venv.sh
   source venv_rag/bin/activate
   pip install -r requirements_rag.txt
   ```

2. **Start services**:
   ```bash
   docker-compose up -d  # Start Qdrant, MySQL, etc.
   ```

3. **Index hotels**:
   ```python
   from simple_rag_system import SimpleRAGSystem
   
   rag = SimpleRAGSystem()
   rag.index_hotels_from_database()
   ```

4. **Run API**:
   ```bash
   ./run_chat.sh
   # or with LM Studio
   ./run_with_lm_studio.sh
   ```

## 📦 Packages

### `core/` - Core RAG Components
- Embeddings, query extraction, retrieval, RAG chain

### `data/` - Data Processing
- Normalizer, connector, chunker

### `api/` - API Server
- Flask chat API

## 🔧 Architecture

**Layer 1: Ingestion** (Offline)
- Data → Normalize → Chunk → Embed → Qdrant

**Layer 2: Retrieval** (Online)
- Query → Extract keywords → Search → Documents

**Layer 3: Generation** (Online)
- Documents → Prompt → LLM → Answer

See [RAG_ARCHITECTURE.md](./RAG_ARCHITECTURE.md) for details.
