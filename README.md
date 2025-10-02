# 🚀 Neo4j RAG System - Complete Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.11+-green.svg)](https://neo4j.com/)

A powerful Retrieval-Augmented Generation (RAG) system built on Neo4j graph database, featuring semantic search, hybrid retrieval, and scalable document management.

## 📋 Table of Contents
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [User Guide](#-user-guide)
- [API Reference](#-api-reference)
- [Examples](#-examples)
- [Architecture](#-architecture)
- [Contributing](#-contributing)

## ✨ Features

- 🔍 **Dual Implementation**: Custom implementation + Official Neo4j GraphRAG support
- 🎯 **Hybrid Search**: Combines vector similarity with keyword matching
- 📊 **Scalable**: Handles 8,500+ document chunks efficiently with optimization
- 🚀 **Production Ready**: Performance benchmarks, best practices, error handling
- 📚 **Pre-loaded Knowledge**: Comprehensive Neo4j documentation included
- 🛠️ **Flexible Architecture**: Modular design for easy customization
- 🌐 **Multi-Model Support**: OpenAI, Sentence Transformers, and more
- 📄 **Advanced Document Processing**: Powered by Docling for PDF, DOCX, PPTX extraction with tables and structure preservation

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/neo4j-rag-system.git
cd neo4j-rag-system

# 2. Start Neo4j with Docker
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11

# 3. Set up Python environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Load sample data
python load_sample_data.py

# 5. Test the system
python test_rag.py
```

## 📦 Installation

### Prerequisites

- **Python**: 3.12 or higher
- **Docker**: Latest version
- **Memory**: 4GB+ RAM
- **Storage**: 2GB+ free space

### Detailed Setup

#### 1️⃣ Neo4j Database Setup

**For Custom Implementation (Recommended for beginners):**
```bash
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11
```

**For Production with Performance Optimization:**
```bash
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_server_memory_heap_initial__size=2g \
  -e NEO4J_server_memory_heap_max__size=4g \
  -e NEO4J_server_memory_pagecache_size=2g \
  neo4j:latest
```

#### 2️⃣ Python Environment

```bash
# Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# For official GraphRAG support (Neo4j 5.18+)
pip install neo4j-graphrag[openai,langchain]

# Optional: For advanced document processing with Docling
# (Already included in requirements.txt)
pip install docling pypdfium2 reportlab
```

#### 3️⃣ Verify Installation

```bash
# Check Neo4j
curl http://localhost:7474

# Test Python setup
python -c "import neo4j; print('✅ Neo4j driver ready')"
python -c "from sentence_transformers import SentenceTransformer; print('✅ Embeddings ready')"
python -c "from docling.document_converter import DocumentConverter; print('✅ Docling ready for document processing')"
```

## 📖 User Guide

### Basic Usage

#### Loading Documents

```python
from neo4j_rag import Neo4jRAG

# Initialize
rag = Neo4jRAG()

# Add documents
rag.add_document(
    content="Your document text here...",
    metadata={"source": "manual", "category": "tutorial"},
    doc_id="doc_001"
)

# Batch loading
documents = [
    {"content": "Doc 1...", "metadata": {"type": "guide"}},
    {"content": "Doc 2...", "metadata": {"type": "reference"}}
]

for doc in documents:
    rag.add_document(doc["content"], doc["metadata"])

rag.close()
```

#### Searching Documents

```python
from neo4j_rag import Neo4jRAG

rag = Neo4jRAG()

# Vector search
results = rag.vector_search("What is Neo4j?", k=5)
for result in results:
    print(f"Score: {result['score']:.3f} - {result['text'][:100]}...")

# Hybrid search (better accuracy)
results = rag.hybrid_search("graph database", k=5)

rag.close()
```

#### Question Answering

```python
from neo4j_rag import Neo4jRAG, RAGQueryEngine

rag = Neo4jRAG()
engine = RAGQueryEngine(rag)

# Ask questions
response = engine.query(
    "How do I configure Neo4j for production?",
    k=3
)

print(f"Question: {response['question']}")
print(f"Sources: {len(response['sources'])} documents found")
print(f"Answer: {response['answer']}")

rag.close()
```

### Advanced Features

#### 📄 Advanced Document Processing with Docling

**NEW**: Enhanced document extraction powered by IBM's Docling library for superior PDF, DOCX, and PPTX processing.

```python
from docling_loader import DoclingDocumentLoader
from neo4j_rag import Neo4jRAG

# Initialize with Neo4j connection
rag = Neo4jRAG()
loader = DoclingDocumentLoader(neo4j_rag=rag)

# Load a PDF with advanced extraction
doc_info = loader.load_document(
    "research_paper.pdf",
    metadata={"category": "research", "year": "2024"}
)

print(f"Extracted {doc_info['statistics']['character_count']:,} characters")
print(f"Found {doc_info['statistics']['table_count']} tables")
print(f"Found {doc_info['statistics']['image_count']} images")

# Load entire directory of documents
results = loader.load_directory(
    "documents/",
    recursive=True,
    file_filter=['.pdf', '.docx', '.pptx']
)

loader.close()
```

**Docling Features**:
- **Multi-format Support**: PDF, DOCX, PPTX, HTML, Markdown, and more
- **Table Extraction**: Preserves table structure and formatting
- **Metadata Extraction**: Titles, authors, creation dates, page counts
- **OCR Support**: Handles scanned PDFs automatically
- **Section Detection**: Identifies document structure and hierarchy
- **Batch Processing**: Efficiently process entire directories

#### 🚀 Optimized Version for Large Datasets

```python
from neo4j_rag_optimized import Neo4jRAGOptimized

# Use when dealing with 1000+ documents
rag = Neo4jRAGOptimized()

# Performs sampling-based search for better performance
results = rag.vector_search_optimized(
    query="your search query",
    k=5,
    batch_size=100  # Process in batches
)

stats = rag.get_stats()
print(f"Managing {stats['chunks']} chunks efficiently")
```

#### 🎨 Custom Embeddings

```python
from sentence_transformers import SentenceTransformer

class CustomRAG(Neo4jRAG):
    def __init__(self):
        super().__init__()
        # Use different embedding model
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')

        # Adjust chunk size
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
```

#### 📊 Performance Monitoring

```python
import time

def benchmark_search(rag, queries):
    """Benchmark search performance"""
    results = []

    for query in queries:
        start = time.time()
        hits = rag.vector_search(query, k=5)
        elapsed = time.time() - start

        results.append({
            "query": query,
            "time": elapsed,
            "hits": len(hits)
        })

    avg_time = sum(r['time'] for r in results) / len(results)
    print(f"⚡ Average: {avg_time:.3f}s ({1/avg_time:.1f} queries/sec)")

    return results
```

## 🔍 Query Examples

### Production & Operations

```python
# Memory configuration
"How do I configure Neo4j memory settings for production?"

# Clustering
"What are Neo4j clustering and high availability options?"

# Backup strategies
"Best practices for Neo4j backup and recovery?"

# Performance tuning
"How to optimize Neo4j for large-scale queries?"
```

### Development

```python
# Cypher optimization
"How to write efficient Cypher queries for pattern matching?"

# Indexing
"What indexing strategies should I use in Neo4j?"

# Data modeling
"Best practices for modeling hierarchical data in Neo4j?"
```

### RAG Implementation

```python
# Vector search
"How to implement vector similarity search in Neo4j?"

# Advanced patterns
"What are advanced RAG patterns with Neo4j?"

# Optimization
"Optimal chunk sizes for different RAG use cases?"
```

## 🏗️ Architecture

### System Design

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Documents     │────▶│  Text Splitter  │────▶│   Embeddings    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Query    │────▶│  Query Engine   │────▶│     Neo4j       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │                         │
                                ▼                         ▼
                        ┌─────────────┐          ┌──────────────┐
                        │   Context   │          │   Documents  │
                        └─────────────┘          │   & Chunks   │
                                │                 └──────────────┘
                                ▼
                        ┌─────────────┐
                        │   Response  │
                        └─────────────┘
```

### Neo4j Graph Structure

```cypher
// Document Node
(:Document {
    id: "doc_001",
    content: "Full text...",
    source: "manual",
    category: "tutorial",
    created: datetime()
})

// Chunk Node
(:Chunk {
    text: "Chunk text...",
    embedding: [384-dim vector],
    chunk_index: 0
})

// Relationship
(document:Document)-[:HAS_CHUNK]->(chunk:Chunk)
```

## 📊 Performance

### Benchmarks

| Operation | Performance | Documents | Chunks |
|-----------|------------|-----------|--------|
| Vector Search | 60ms/query | 14 | 8,547 |
| Hybrid Search | 24ms/query | 14 | 8,547 |
| Document Load | 2.5s/doc | - | - |
| RAG Query | 300ms/query | 14 | 8,547 |

### Optimization Tips

1. **For Large Datasets (>1000 docs)**:
   - Use `Neo4jRAGOptimized` class
   - Enable batch processing
   - Implement caching

2. **Memory Configuration**:
   ```bash
   # Neo4j heap memory
   NEO4J_server_memory_heap_max__size=4g

   # Page cache
   NEO4J_server_memory_pagecache_size=2g
   ```

3. **Connection Pooling**:
   ```python
   driver = GraphDatabase.driver(
       uri,
       auth=auth,
       max_connection_pool_size=50
   )
   ```

## 🛠️ API Reference

### Core Classes

#### Neo4jRAG

```python
class Neo4jRAG:
    def __init__(self, uri="bolt://localhost:7687",
                 username="neo4j", password="password")

    def add_document(self, content: str,
                    metadata: dict = None,
                    doc_id: str = None) -> None

    def vector_search(self, query: str, k: int = 5) -> List[Dict]

    def hybrid_search(self, query: str, k: int = 5) -> List[Dict]

    def get_context(self, query: str, k: int = 3) -> str

    def get_stats(self) -> Dict

    def clear_database(self) -> None

    def close(self) -> None
```

#### RAGQueryEngine

```python
class RAGQueryEngine:
    def __init__(self, neo4j_rag: Neo4jRAG)

    def query(self, question: str, k: int = 3) -> Dict
        # Returns: {
        #     'question': str,
        #     'context': str,
        #     'sources': List[Dict],
        #     'answer': str
        # }
```

#### DoclingDocumentLoader

```python
class DoclingDocumentLoader:
    def __init__(self, neo4j_rag: Optional[Neo4jRAG] = None)

    def load_document(self, file_path: str, metadata: Optional[Dict] = None) -> Dict
        # Returns document info with statistics, tables, images, sections

    def load_directory(self, directory_path: str,
                       recursive: bool = True,
                       file_filter: Optional[List[str]] = None) -> List[Dict]

    def extract_text_only(self, file_path: str) -> str
        # Extract text without storing in Neo4j

    def close(self) -> None
```

## 🧪 Testing

```bash
# Run all tests
python test_rag.py

# Test optimized version
python test_optimized.py

# Test Docling PDF extraction
python test_docling_pdf.py

# Quick validation
python quick_test.py

# Performance benchmark
python -c "from test_rag import test_performance; test_performance()"
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Check Docker: `docker ps \| grep neo4j` |
| Out of memory | Use optimized version or increase Docker memory |
| Slow search | Enable vector indexing, use batching |
| Import errors | Activate venv: `source venv/bin/activate` |

### Getting Help

1. Check the [User Guide](USER_GUIDE.md)
2. Review [Common Issues](#troubleshooting)
3. Open an [Issue](https://github.com/yourusername/neo4j-rag-system/issues)
4. Visit [Neo4j Community](https://community.neo4j.com/)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

```bash
# Fork the repository
# Create your feature branch
git checkout -b feature/amazing-feature

# Commit your changes
git commit -m 'Add amazing feature'

# Push to the branch
git push origin feature/amazing-feature

# Open a Pull Request
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Neo4j team for the amazing graph database
- Sentence Transformers for embedding models
- LangChain for RAG utilities
- All contributors to this project

## 📚 Resources

- [📖 Full User Guide](USER_GUIDE.md)
- [🔗 Neo4j Documentation](https://neo4j.com/docs/)
- [🐍 Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [🤖 Neo4j GraphRAG](https://neo4j.com/docs/neo4j-graphrag-python/)
- [💬 Community Forum](https://community.neo4j.com/)

---

<p align="center">
  Made with ❤️ by the Neo4j RAG Community
  <br>
  ⭐ Star us on GitHub!
</p>