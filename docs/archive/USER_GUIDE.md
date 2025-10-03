# Neo4j RAG System - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Installation Guide](#installation-guide)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Query Examples](#query-examples)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)

## Introduction

The Neo4j RAG (Retrieval-Augmented Generation) System is a powerful tool that combines Neo4j's graph database capabilities with modern vector search and natural language processing. This system allows you to:

- Store and retrieve documents with semantic search
- Ask natural language questions about your knowledge base
- Combine vector similarity with keyword search for optimal results
- Scale to thousands of documents with optimized performance

### Key Features

- 🚀 **Dual Implementation**: Choose between custom implementation or official Neo4j GraphRAG
- 🔍 **Hybrid Search**: Combines vector and keyword search for better accuracy
- 📊 **Scalable**: Optimized version handles 8,500+ document chunks efficiently
- 🎯 **Production Ready**: Includes best practices and performance optimizations
- 📚 **Comprehensive Knowledge Base**: Pre-loaded with Neo4j documentation

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/neo4j-rag-demo.git
cd neo4j-rag-demo
```

### 2. Start Neo4j with Docker

```bash
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11
```

### 3. Install Dependencies

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Load Sample Data

```bash
python load_sample_data.py
```

### 5. Test the System

```bash
python test_rag.py
```

## Installation Guide

### Prerequisites

- Python 3.12 or higher
- Docker Desktop
- 4GB+ RAM available
- 2GB+ disk space

### Detailed Installation Steps

#### Step 1: System Requirements

Verify your system meets the requirements:

```bash
# Check Python version
python3 --version  # Should be 3.12+

# Check Docker
docker --version

# Check available memory
docker system info | grep Memory
```

#### Step 2: Neo4j Setup

Choose the appropriate Neo4j version for your needs:

**For Custom Implementation (Recommended for beginners):**
```bash
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11
```

**For Official GraphRAG (Requires Neo4j 5.18+):**
```bash
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:latest
```

#### Step 3: Python Environment

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Verify Installation

```bash
# Test Neo4j connection
curl http://localhost:7474

# Test Python imports
python -c "import neo4j; print('Neo4j driver:', neo4j.__version__)"
python -c "from sentence_transformers import SentenceTransformer; print('Embeddings: OK')"
```

## Basic Usage

### Loading Documents

```python
from neo4j_rag import Neo4jRAG

# Initialize the system
rag = Neo4jRAG()

# Add a single document
rag.add_document(
    content="Neo4j is a graph database management system...",
    metadata={"source": "manual", "category": "database"},
    doc_id="doc_001"
)

# Load multiple documents
documents = [
    {"content": "Document 1 text...", "metadata": {"source": "doc1"}},
    {"content": "Document 2 text...", "metadata": {"source": "doc2"}}
]

for doc in documents:
    rag.add_document(doc["content"], doc["metadata"])

rag.close()
```

### Searching Documents

```python
from neo4j_rag import Neo4jRAG

rag = Neo4jRAG()

# Vector similarity search
results = rag.vector_search("What is Neo4j?", k=5)
for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Text: {result['text'][:200]}...\n")

# Hybrid search (vector + keyword)
results = rag.hybrid_search("graph database", k=5)

rag.close()
```

### Question Answering

```python
from neo4j_rag import Neo4jRAG, RAGQueryEngine

# Initialize
rag = Neo4jRAG()
engine = RAGQueryEngine(rag)

# Ask questions
response = engine.query("How do I configure Neo4j for production?", k=3)

print("Question:", response['question'])
print("\nSources found:", len(response['sources']))
print("\nAnswer:", response['answer'])

rag.close()
```

## Advanced Features

### Using the Optimized Version for Large Datasets

When working with thousands of documents, use the optimized implementation:

```python
from neo4j_rag_optimized import Neo4jRAGOptimized, RAGQueryEngineOptimized

# Initialize optimized version
rag = Neo4jRAGOptimized()
engine = RAGQueryEngineOptimized(rag)

# Get stats
stats = rag.get_stats()
print(f"Managing {stats['documents']} documents with {stats['chunks']} chunks")

# Performs sampling-based search for better performance
results = rag.vector_search_optimized("your query", k=5, batch_size=100)

rag.close()
```

### Customizing Embeddings

```python
from sentence_transformers import SentenceTransformer

class CustomNeo4jRAG(Neo4jRAG):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use a different embedding model
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
        # Adjust chunk size
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
```

### Batch Processing

```python
def load_documents_batch(file_paths, rag):
    """Load multiple documents efficiently"""
    for path in file_paths:
        with open(path, 'r') as f:
            content = f.read()
            metadata = {
                "source": path,
                "type": "document",
                "loaded_at": datetime.now().isoformat()
            }
            rag.add_document(content, metadata)
    print(f"Loaded {len(file_paths)} documents")
```

### Monitoring Performance

```python
import time

def benchmark_search(rag, queries, k=5):
    """Benchmark search performance"""
    results = []

    for query in queries:
        start = time.time()
        hits = rag.vector_search(query, k=k)
        elapsed = time.time() - start

        results.append({
            "query": query,
            "time": elapsed,
            "hits": len(hits),
            "top_score": hits[0]['score'] if hits else 0
        })

    avg_time = sum(r['time'] for r in results) / len(results)
    print(f"Average search time: {avg_time:.3f}s")
    print(f"Queries per second: {1/avg_time:.1f}")

    return results
```

## Query Examples

### Production & Operations

```python
# Memory configuration
response = engine.query("How do I configure Neo4j memory settings for production?")

# Backup strategies
response = engine.query("What are the best practices for Neo4j backup and recovery?")

# Clustering
response = engine.query("How to set up Neo4j clustering for high availability?")

# Performance tuning
response = engine.query("How to optimize Neo4j for large-scale graph queries?")
```

### Development Queries

```python
# Cypher optimization
response = engine.query("How to write efficient Cypher queries for pattern matching?")

# Index strategies
response = engine.query("What indexing strategies should I use in Neo4j?")

# Data modeling
response = engine.query("Best practices for modeling hierarchical data in Neo4j?")

# Transactions
response = engine.query("How to handle transactions in Neo4j Python driver?")
```

### RAG Implementation

```python
# Vector search
response = engine.query("How to implement vector similarity search in Neo4j?")

# GraphRAG patterns
response = engine.query("What are advanced RAG patterns with Neo4j?")

# Embedding strategies
response = engine.query("Optimal chunk sizes for different RAG use cases?")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Neo4j Connection Failed

**Error:** `ServiceUnavailable: Failed to establish connection`

**Solution:**
```bash
# Check if Neo4j is running
docker ps | grep neo4j-rag

# Restart Neo4j
docker restart neo4j-rag

# Check logs
docker logs neo4j-rag --tail 50
```

#### 2. Out of Memory Errors

**Error:** `OutOfMemoryError` during vector search

**Solution:**
```python
# Use the optimized version
from neo4j_rag_optimized import Neo4jRAGOptimized

rag = Neo4jRAGOptimized()
# This uses sampling to avoid loading all chunks

# Or increase Docker memory
# Docker Desktop > Settings > Resources > Memory: 6GB+
```

#### 3. Slow Search Performance

**Problem:** Searches taking >5 seconds

**Solution:**
```bash
# Enable Java Vector API for better performance
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_server_jvm_additional='-XX:+UnlockExperimentalVMOptions --add-modules jdk.incubator.vector' \
  neo4j:latest
```

#### 4. Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# For official GraphRAG
pip install neo4j-graphrag[openai,langchain]
```

### Performance Tuning

#### Neo4j Configuration

Add to Neo4j configuration for better performance:

```conf
# Memory settings
dbms.memory.heap.initial_size=2g
dbms.memory.heap.max_size=4g
dbms.memory.pagecache.size=2g

# Query cache
dbms.query_cache_size=100

# Connection pool
dbms.connector.bolt.thread_pool_max_size=400
```

#### Python Optimizations

```python
# Use connection pooling
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password"),
    max_connection_lifetime=3600,
    max_connection_pool_size=50,
    connection_acquisition_timeout=60
)

# Batch operations
def batch_add_documents(documents, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        # Process batch
```

## API Reference

### Neo4jRAG Class

#### Constructor
```python
Neo4jRAG(uri="bolt://localhost:7687", username="neo4j", password="password")
```

#### Methods

**add_document(content, metadata=None, doc_id=None)**
- Adds a document to the database
- Returns: None
- Parameters:
  - `content` (str): Document text
  - `metadata` (dict): Optional metadata
  - `doc_id` (str): Optional document ID

**vector_search(query, k=5)**
- Performs vector similarity search
- Returns: List[Dict] with scores and text
- Parameters:
  - `query` (str): Search query
  - `k` (int): Number of results

**hybrid_search(query, k=5)**
- Combines vector and keyword search
- Returns: List[Dict] with scores and text
- Parameters:
  - `query` (str): Search query
  - `k` (int): Number of results

**get_context(query, k=3)**
- Gets context for RAG
- Returns: str (concatenated context)
- Parameters:
  - `query` (str): Search query
  - `k` (int): Number of chunks

**get_stats()**
- Returns database statistics
- Returns: Dict with 'documents' and 'chunks' counts

**clear_database()**
- Removes all data from database
- Returns: None

**close()**
- Closes database connection
- Returns: None

### RAGQueryEngine Class

#### Constructor
```python
RAGQueryEngine(neo4j_rag)
```

#### Methods

**query(question, k=3)**
- Queries the RAG system
- Returns: Dict with 'question', 'context', 'sources', 'answer'
- Parameters:
  - `question` (str): User question
  - `k` (int): Number of context chunks

### Neo4jRAGOptimized Class

Same interface as Neo4jRAG with additional parameters:

**vector_search_optimized(query, k=5, batch_size=100)**
- Optimized search for large datasets
- Additional parameter:
  - `batch_size` (int): Chunks to process at once

## Best Practices

1. **Document Chunking**
   - Use 200-500 tokens for balanced retrieval
   - Implement 10-20% overlap between chunks
   - Consider document structure when splitting

2. **Embedding Strategy**
   - Choose model based on your domain
   - Cache embeddings for frequently accessed content
   - Consider multilingual models if needed

3. **Search Optimization**
   - Start with hybrid search for best results
   - Adjust k parameter based on use case
   - Implement result caching for common queries

4. **Production Deployment**
   - Use environment variables for credentials
   - Implement proper logging and monitoring
   - Set up regular backups
   - Use connection pooling

5. **Scaling Considerations**
   - Use optimized version for >1000 documents
   - Consider Neo4j Aura for managed deployment
   - Implement rate limiting for API endpoints
   - Monitor memory usage and query performance

## Support and Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Neo4j GraphRAG Python](https://neo4j.com/docs/neo4j-graphrag-python/)
- [Project Issues](https://github.com/yourusername/neo4j-rag-demo/issues)
- [Neo4j Community](https://community.neo4j.com/)

---

*For more examples and advanced usage, check the `/examples` directory in the repository.*