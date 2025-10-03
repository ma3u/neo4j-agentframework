# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Neo4j Agent Framework - an advanced RAG (Retrieval-Augmented Generation) system that provides:
1. **Optimized implementation** (`neo4j_rag.py`) - 417x performance improvement with caching and pooling
2. **Official GraphRAG integration** (`official_graphrag_demo.py`) - Requires Neo4j 5.18+ for advanced features
3. **Advanced PDF processing** (`docling_loader.py`) - Extract tables, structure, and content from complex documents

## Essential Commands

### Environment Setup
```bash
# Activate virtual environment (required for all operations)
source venv/bin/activate

# Install dependencies for core implementation
pip install -r requirements.txt

# Install for official GraphRAG (requires Neo4j 5.18+)
pip install -r requirements_graphrag.txt
```

### Neo4j Database Management
```bash
# Start Neo4j (v5.11+ for core features)
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11

# Start Neo4j with performance optimizations
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_server_jvm_additional='-XX:+UnlockExperimentalVMOptions --add-modules jdk.incubator.vector' \
  -e NEO4J_dbms_memory_heap_max__size=4G \
  -e NEO4J_dbms_memory_pagecache_size=2G \
  neo4j:latest

# Check Neo4j status
docker ps | grep neo4j-rag
docker logs neo4j-rag
```

### Running the System
```bash
# Load sample data (8 documents about Neo4j, RAG, etc.)
python scripts/load_sample_data.py

# Upload PDFs to Neo4j
python scripts/upload_pdfs_to_neo4j.py /path/to/pdfs/

# Download sample PDFs from knowledge base
python scripts/download_pdfs.py

# Run comprehensive demo
python scripts/rag_demo.py

# Run test suite
python tests/test_rag.py
```

### Analytics and Exploration
```bash
# View RAG statistics
python scripts/rag_statistics.py

# Run search examples
python scripts/rag_search_examples.py

# Execute graph queries
python scripts/rag_graph_queries.py

# Setup Neo4j Browser with queries
python scripts/setup_browser_favorites.py
```

## Architecture Overview

### Core Implementation (`neo4j_rag.py`)
- **Neo4jRAG class**: Main RAG system with performance optimizations
  - Connection pooling (10 max connections)
  - Query caching with thread-safe FIFO cache
  - Parallel vector and keyword search
  - Full-text indexing for fast searches
- **RAGQueryEngine class**: Query processing and context retrieval
- **Embedding**: SentenceTransformer('all-MiniLM-L6-v2') - 384 dimensions
- **Chunking**: RecursiveCharacterTextSplitter (chunk_size=300, overlap=50)
- **Search Methods**:
  - `vector_search()`: Cosine similarity on embeddings
  - `hybrid_search()`: Combines vector + keyword (default alpha=0.5)
  - `similarity_threshold_search()`: Filter by minimum similarity

### Document Processing (`docling_loader.py`)
- **DoclingDocumentLoader class**: Advanced PDF processing
- Handles complex PDFs with tables, images, and structure
- Automatic chunking and embedding generation
- Metadata extraction and preservation
- Batch processing capabilities

### Graph Structure
```
Document Nodes:
- Properties: id, content, source, category, created
- Metadata: Stored as individual properties (Neo4j limitation)
- Indexes: Unique constraint on id

Chunk Nodes:
- Properties: text, embedding (384-dim array), chunk_index
- Indexes: Range index on chunk_index, fulltext on text
- Relationships: Document -[:HAS_CHUNK]-> Chunk
```

## Performance Characteristics

### Optimizations Implemented
- **Connection Pooling**: Reuses database connections
- **Query Caching**: FIFO cache with configurable size (default 100)
- **Parallel Processing**: ThreadPoolExecutor for concurrent operations
- **Optimized Chunk Size**: 300 characters for faster processing
- **Full-text Indexes**: Lightning-fast keyword searches
- **Early Result Filtering**: Database-level query optimization

### Performance Metrics
- Vector Search: ~110ms per query (from 46s originally)
- Hybrid Search: ~24ms per query
- Cached Queries: <1ms
- Document Processing: ~2-3s per PDF page
- Memory Usage: ~100MB base + ~50MB per 1000 chunks

## Common Patterns

### Basic Usage
```python
from src.neo4j_rag import Neo4jRAG, RAGQueryEngine

# Initialize
rag = Neo4jRAG()
engine = RAGQueryEngine(rag)

# Add documents
rag.add_document("content", metadata={"source": "file.pdf"})

# Search
results = rag.vector_search("query", k=5)

# Ask questions
response = engine.query("What is Neo4j?")

# Always close
rag.close()
```

### PDF Processing
```python
from src.docling_loader import DoclingDocumentLoader
from src.neo4j_rag import Neo4jRAG

rag = Neo4jRAG()
loader = DoclingDocumentLoader(neo4j_rag=rag)

# Process single PDF
loader.load_document("document.pdf")

# Process directory
loader.load_directory("/path/to/pdfs/")

# Always close
loader.close()
rag.close()
```

## Important Notes

### Version Requirements
- Neo4j 5.11+ for core features
- Neo4j 5.18.1+ for official GraphRAG
- Python 3.12+ for all features
- 4GB+ RAM recommended

### Known Issues
1. **Nested Metadata**: Neo4j doesn't support nested maps - metadata is flattened
2. **Parameter Names**: Use unique names to avoid Cypher conflicts (e.g., `search_query` not `query`)
3. **Connection Leaks**: Always close drivers with `rag.close()`
4. **Docling Timeouts**: Large PDFs may timeout - use smaller batches

### Best Practices
1. **Always close connections**: Use try/finally or context managers
2. **Batch operations**: Process multiple documents in one session
3. **Monitor memory**: Check heap usage for large datasets
4. **Use caching**: Enable query cache for repeated searches
5. **Optimize chunks**: Adjust chunk_size based on content type

## Testing

### Run Tests
```bash
# Main test suite
python tests/test_rag.py

# Interactive testing
python tests/interactive_test.py

# PDF processing tests
python tests/test_docling_pdf.py
```

### Expected Results
- 8 documents and 12 chunks after `load_sample_data.py`
- Vector search accuracy >0.8 for relevant queries
- Hybrid search improves recall by ~20%
- Cache hits reduce response time by 99.9%

## Troubleshooting

### Connection Issues
```bash
# Check Neo4j is running
docker ps | grep neo4j

# View logs
docker logs neo4j-rag

# Test connection
python -c "from src.neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); print(rag.get_stats()); rag.close()"
```

### Performance Issues
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor query times
from src.neo4j_rag import Neo4jRAG
rag = Neo4jRAG()
import time
start = time.time()
results = rag.vector_search("test", k=5)
print(f"Query took {time.time() - start:.2f}s")
```

### Memory Issues
```bash
# Increase Docker memory
docker run -e NEO4J_dbms_memory_heap_max__size=8G ...

# Monitor memory usage
docker stats neo4j-rag
```

## Project Status

### Completed Features
- ✅ 417x performance improvement
- ✅ Connection pooling and caching
- ✅ Hybrid search implementation
- ✅ PDF processing with Docling
- ✅ Neo4j Browser integration
- ✅ Comprehensive test suite
- ✅ 50+ analytical queries

### Code Quality
- **Removed**: Redundant implementations (neo4j_rag_original.py, neo4j_rag_optimized.py)
- **Removed**: Duplicate scripts (simple_pdf_upload.py, quick_browser_test.py)
- **Consolidated**: All functionality in main neo4j_rag.py
- **Optimized**: Single source of truth for RAG implementation
- **Documented**: Clear API and usage patterns

### Future Improvements
- [ ] Add streaming response support
- [ ] Implement multi-modal embeddings
- [ ] Add LangChain integration examples
- [ ] Create Docker Compose setup
- [ ] Add API server with FastAPI