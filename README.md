# 🚀 Neo4j RAG System - Complete Guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.11+-green.svg)](https://neo4j.com/)
[![Docling](https://img.shields.io/badge/Docling-2.55+-blue.svg)](https://github.com/DS4SD/docling)

A powerful Retrieval-Augmented Generation (RAG) system built on Neo4j graph database, featuring semantic search, hybrid retrieval, advanced document processing, and scalable document management.

## 📋 Table of Contents

- [✨ Features](#-features)
- [⚡ Quick Installation Guide](#-quick-installation-guide)
  - [Prerequisites](#prerequisites)
  - [One-Line Install](#one-line-install)
  - [Step-by-Step Setup](#step-by-step-setup)
- [🧩 Components Overview](#-components-overview)
  - [Core Technologies](#core-technologies)
  - [System Architecture](#system-architecture)
- [📥 Extract & Load Content](#-extract--load-content)
  - [Simple Document Loading](#simple-document-loading)
  - [Advanced PDF Processing](#advanced-pdf-processing)
  - [Batch Processing](#batch-processing)
- [🔍 Search Tools & RAG Methods](#-search-tools--rag-methods)
  - [Vector Search](#vector-search)
  - [Hybrid Search](#hybrid-search)
  - [RAG Query Engine](#rag-query-engine)
- [📓 Neo4j RAG Notebooks](#-neo4j-rag-notebooks)
  - [Getting Started Notebooks](#getting-started-notebooks)
  - [Advanced Tutorials](#advanced-tutorials)
- [📖 Complete User Guide](#-complete-user-guide)
- [🏗️ Architecture Details](#️-architecture-details)
- [📊 Performance Benchmarks](#-performance-benchmarks)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📚 Resources & References](#-resources--references)

---

## ✨ Features

- 🔍 **Dual Implementation**: Custom implementation + Official Neo4j GraphRAG support
- 🎯 **Hybrid Search**: Combines vector similarity with keyword matching
- 📊 **Scalable**: Handles 8,500+ document chunks efficiently with optimization
- 🚀 **Production Ready**: Performance benchmarks, best practices, error handling
- 📚 **Pre-loaded Knowledge**: Comprehensive Neo4j documentation included
- 🛠️ **Flexible Architecture**: Modular design for easy customization
- 🌐 **Multi-Model Support**: OpenAI, Sentence Transformers, and more
- 📄 **Advanced Document Processing**: Powered by Docling for PDF, DOCX, PPTX extraction with tables and structure preservation
- 📓 **Interactive Notebooks**: Learn with Jupyter notebooks and examples

---

## ⚡ Quick Installation Guide

### Prerequisites

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/))
- **Git** ([Download](https://git-scm.com/))
- **4GB+ RAM** available
- **2GB+ disk space**

### One-Line Install

```bash
# Clone and setup everything with one command (macOS/Linux)
curl -sSL https://raw.githubusercontent.com/yourusername/neo4j-rag-system/main/install.sh | bash
```

### Step-by-Step Setup

#### 1️⃣ Clone & Navigate

```bash
git clone https://github.com/yourusername/neo4j-rag-system.git
cd neo4j-rag-system
```

#### 2️⃣ Start Neo4j Database

```bash
# Quick start (development)
docker run -d --name neo4j-rag \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11

# Or optimized for production
docker run -d --name neo4j-rag \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_server_memory_heap_max__size=4g \
  -e NEO4J_server_memory_pagecache_size=2g \
  neo4j:latest
```

#### 3️⃣ Python Environment Setup

```bash
# Create virtual environment
python3.12 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4️⃣ Verify Installation

```bash
# Check all components
python -c "
import neo4j
from sentence_transformers import SentenceTransformer
from docling.document_converter import DocumentConverter
print('✅ All components ready!')
print('📊 Neo4j at: http://localhost:7474')
print('🔐 Login: neo4j/password')
"
```

#### 5️⃣ Load Sample Data & Test

```bash
# Load sample documents
python load_sample_data.py

# Run quick test
python quick_test.py

# Expected output:
# ✅ Connected to Neo4j
# ✅ Loaded 8 documents
# ✅ Created 12 chunks
# ✅ Search working: Found results for 'Neo4j'
```

---

## 🧩 Components Overview

### Core Technologies

| Component | Version | Purpose | Documentation |
|-----------|---------|---------|---------------|
| **Neo4j** | 5.11+ | Graph database for document storage | [Docs](https://neo4j.com/docs/) |
| **Python** | 3.12+ | Primary programming language | [Docs](https://docs.python.org/) |
| **Sentence Transformers** | Latest | Generate embeddings (384-dim) | [Docs](https://sbert.net/) |
| **LangChain** | Latest | Document chunking & RAG utilities | [Docs](https://langchain.com/) |
| **Docling** | 2.55+ | Advanced document extraction | [Docs](https://github.com/DS4SD/docling) |
| **Neo4j GraphRAG** | Optional | Official RAG implementation | [Docs](https://neo4j.com/docs/neo4j-graphrag-python/) |

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Input Layer                         │
├─────────────────────────────────────────────────────────┤
│  Documents (PDF, DOCX, PPTX, MD, HTML, TXT)            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Processing Layer                        │
├─────────────────────────────────────────────────────────┤
│  Docling Extraction → Chunking → Embedding Generation   │
│  • Table preservation                                   │
│  • Metadata extraction                                  │
│  • OCR for scanned docs                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Storage Layer                          │
├─────────────────────────────────────────────────────────┤
│           Neo4j Graph Database                          │
│  ┌──────────┐      ┌─────────┐                        │
│  │ Document │─────►│  Chunk  │                        │
│  │   Node   │      │  Node   │                        │
│  └──────────┘      └─────────┘                        │
│                    • Text                              │
│                    • Embedding[384]                    │
│                    • Metadata                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Retrieval Layer                        │
├─────────────────────────────────────────────────────────┤
│  • Vector Search (Cosine Similarity)                    │
│  • Hybrid Search (Vector + Keyword)                     │
│  • Graph Traversal                                      │
└─────────────────────────────────────────────────────────┘
```

---

## 📥 Extract & Load Content

### Simple Document Loading

```python
from neo4j_rag import Neo4jRAG

# Initialize RAG system
rag = Neo4jRAG()

# Load a simple text document
rag.add_document(
    content="Your document text here...",
    metadata={
        "source": "manual",
        "category": "tutorial",
        "author": "John Doe"
    }
)

# Check what was loaded
stats = rag.get_stats()
print(f"Documents: {stats['documents']}, Chunks: {stats['chunks']}")

rag.close()
```

### Advanced PDF Processing

```python
from docling_loader import DoclingDocumentLoader
from neo4j_rag import Neo4jRAG

# Initialize with Docling for advanced extraction
rag = Neo4jRAG()
loader = DoclingDocumentLoader(neo4j_rag=rag)

# Load a complex PDF with tables and images
doc_info = loader.load_document(
    "research_paper.pdf",
    metadata={"category": "research", "year": "2024"}
)

print(f"📄 Extracted {doc_info['statistics']['character_count']:,} characters")
print(f"📊 Found {doc_info['statistics']['table_count']} tables")
print(f"🖼️ Found {doc_info['statistics']['image_count']} images")

# Tables are automatically preserved
for table in doc_info['tables']:
    print(f"Table {table['index']}: {table.get('rows', 'N/A')} rows")

loader.close()
```

### Batch Processing

```python
# Process entire directory
results = loader.load_directory(
    "documents/",
    recursive=True,                          # Include subdirectories
    file_filter=['.pdf', '.docx', '.pptx']  # Specific formats only
)

print(f"✅ Processed {len(results)} documents")

# Or load from multiple sources
sources = [
    {"path": "report.pdf", "metadata": {"type": "report"}},
    {"path": "presentation.pptx", "metadata": {"type": "slides"}},
    {"path": "data.xlsx", "metadata": {"type": "data"}}
]

for source in sources:
    loader.load_document(source["path"], source["metadata"])
```

---

## 🔍 Search Tools & RAG Methods

### Vector Search

Vector search finds documents by semantic similarity using embeddings:

```python
from neo4j_rag import Neo4jRAG

rag = Neo4jRAG()

# Semantic search - finds conceptually similar content
results = rag.vector_search(
    query="How to optimize database performance",
    k=5  # Return top 5 results
)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Text: {result['text'][:200]}...")
    print(f"Source: {result.get('metadata', {}).get('source', 'Unknown')}")
    print("---")

rag.close()
```

### Hybrid Search

Combines vector similarity with keyword matching for better accuracy:

```python
# Hybrid search - best of both worlds
results = rag.hybrid_search(
    query="Neo4j performance tuning memory settings",
    k=5,
    vector_weight=0.7,  # 70% vector, 30% keyword
    keyword_weight=0.3
)

# Results include both semantic matches and exact keyword matches
for result in results:
    print(f"Combined Score: {result['score']:.3f}")
    print(f"Content: {result['text'][:200]}...")
```

### RAG Query Engine

Complete question-answering with context retrieval:

```python
from neo4j_rag import Neo4jRAG, RAGQueryEngine

rag = Neo4jRAG()
engine = RAGQueryEngine(rag)

# Ask natural language questions
response = engine.query(
    question="What are the best practices for Neo4j memory configuration?",
    k=3,  # Use top 3 relevant chunks for context
    temperature=0.7  # Control creativity (0=deterministic, 1=creative)
)

print("Question:", response['question'])
print("\nAnswer:", response['answer'])
print(f"\nSources used: {len(response['sources'])}")
for i, source in enumerate(response['sources'], 1):
    print(f"  {i}. {source['text'][:100]}...")

rag.close()
```

### Advanced Search Patterns

```python
# 1. Filtered search with metadata
results = rag.search_with_filter(
    query="machine learning",
    metadata_filter={"category": "research", "year": "2024"},
    k=5
)

# 2. Multi-query search (find diverse results)
queries = [
    "database optimization",
    "performance tuning",
    "memory configuration"
]
all_results = rag.multi_query_search(queries, k=3)

# 3. Similarity threshold search
results = rag.vector_search(
    query="specific technical term",
    k=10,
    min_score=0.8  # Only return highly similar results
)

# 4. Graph-enhanced search (traverse relationships)
results = rag.graph_search(
    start_query="Neo4j clustering",
    max_hops=2,  # Follow relationships up to 2 hops
    relationship_types=["REFERENCES", "RELATED_TO"]
)
```

---

## 📓 Neo4j RAG Notebooks

Learn the system interactively with Jupyter notebooks that demonstrate core concepts and advanced techniques.

### Getting Started Notebooks

#### 1. Setup & First Steps (`notebooks/01_setup.ipynb`)

```python
# Install Jupyter if needed
pip install jupyter notebook

# Start Jupyter
jupyter notebook

# Navigate to notebooks/01_setup.ipynb
```

**Contents:**
- Environment setup verification
- Neo4j connection testing
- First document upload
- Basic search operations

#### 2. Understanding Embeddings (`notebooks/02_embeddings.ipynb`)

```python
# Interactive embedding visualization
from sentence_transformers import SentenceTransformer
import numpy as np
import plotly.express as px

model = SentenceTransformer('all-MiniLM-L6-v2')

# Compare semantic similarity
texts = [
    "Neo4j is a graph database",
    "Graph databases store data as nodes and relationships",
    "The weather is nice today"
]

embeddings = model.encode(texts)
similarities = np.dot(embeddings, embeddings.T)

# Visualize similarity matrix
fig = px.imshow(similarities,
                labels=dict(x="Text", y="Text", color="Similarity"),
                x=texts, y=texts)
fig.show()
```

#### 3. Document Processing (`notebooks/03_document_processing.ipynb`)

```python
# Step-by-step document processing
from docling_loader import DoclingDocumentLoader

loader = DoclingDocumentLoader()

# Extract and examine structure
doc = loader.load_document("sample.pdf")

# Explore extracted components
print("Tables found:", len(doc['tables']))
print("Sections:", [s['title'] for s in doc['sections']])

# Visualize chunking
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(doc['content'])

print(f"Document split into {len(chunks)} chunks")
print("First chunk:", chunks[0])
```

### Advanced Tutorials

#### 4. Building a RAG Pipeline (`notebooks/04_rag_pipeline.ipynb`)

Complete end-to-end RAG implementation:

```python
# Full RAG pipeline example
class CustomRAGPipeline:
    def __init__(self):
        self.rag = Neo4jRAG()
        self.loader = DoclingDocumentLoader(self.rag)
        self.engine = RAGQueryEngine(self.rag)

    def ingest_documents(self, folder_path):
        """Ingest all documents from a folder"""
        results = self.loader.load_directory(folder_path)
        return f"Loaded {len(results)} documents"

    def answer_question(self, question):
        """Answer questions using RAG"""
        response = self.engine.query(question)
        return response['answer']

    def similar_documents(self, text, k=5):
        """Find similar documents"""
        return self.rag.vector_search(text, k)

# Use the pipeline
pipeline = CustomRAGPipeline()
pipeline.ingest_documents("./documents")
answer = pipeline.answer_question("What is Neo4j?")
```

#### 5. Performance Optimization (`notebooks/05_optimization.ipynb`)

```python
# Benchmark different search methods
import time

def benchmark_search(rag, query, methods=['vector', 'hybrid']):
    results = {}

    for method in methods:
        start = time.time()

        if method == 'vector':
            res = rag.vector_search(query, k=10)
        elif method == 'hybrid':
            res = rag.hybrid_search(query, k=10)

        elapsed = time.time() - start
        results[method] = {
            'time': elapsed,
            'results': len(res),
            'top_score': res[0]['score'] if res else 0
        }

    return results

# Compare performance
benchmarks = benchmark_search(rag, "graph database performance")
print(pd.DataFrame(benchmarks).T)
```

#### 6. Graph Visualization (`notebooks/06_graph_viz.ipynb`)

```python
# Visualize document-chunk relationships
from pyvis.network import Network
import pandas as pd

# Query Neo4j for graph structure
query = """
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
RETURN d.id as doc_id, d.source as source,
       count(c) as chunk_count
LIMIT 20
"""

with rag.driver.session() as session:
    result = session.run(query)
    df = pd.DataFrame([r.dict() for r in result])

# Create interactive graph
net = Network(notebook=True, height="500px", width="100%")

for _, row in df.iterrows():
    net.add_node(row['doc_id'],
                 label=f"{row['source']}\n{row['chunk_count']} chunks",
                 size=row['chunk_count'])

net.show("document_graph.html")
```

### Creating Your Own Notebooks

Template for creating custom notebooks:

```python
# notebooks/custom_analysis.ipynb

# Cell 1: Setup
%load_ext autoreload
%autoreload 2

import sys
sys.path.append('..')

from neo4j_rag import Neo4jRAG
from docling_loader import DoclingDocumentLoader
import pandas as pd
import matplotlib.pyplot as plt

# Cell 2: Connect to Neo4j
rag = Neo4jRAG()
print(f"Connected. Stats: {rag.get_stats()}")

# Cell 3: Your Analysis
# Add your custom analysis here

# Cell 4: Cleanup
rag.close()
```

---

## 📖 Complete User Guide

### Basic Operations

#### Starting Fresh
```bash
# Clear all data and start over
python -c "from neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); rag.clear_database(); print('Database cleared')"
```

#### Loading Documents
```bash
# Load sample data
python load_sample_data.py

# Load knowledge base
python load_knowledge_base.py

# Load your own documents
python -c "
from docling_loader import DoclingDocumentLoader
loader = DoclingDocumentLoader()
loader.load_directory('./my_documents')
"
```

#### Testing the System
```bash
# Quick test
python quick_test.py

# Full test suite
python test_rag.py

# Test specific component
python test_docling_pdf.py
```

### Configuration Options

#### Neo4j Connection
```python
# Custom Neo4j connection
rag = Neo4jRAG(
    uri="bolt://your-server:7687",
    username="your-username",
    password="your-password"
)
```

#### Embedding Model Selection
```python
# Use different embedding model
from sentence_transformers import SentenceTransformer

class CustomRAG(Neo4jRAG):
    def __init__(self):
        super().__init__()
        # Use a different model (768 dimensions instead of 384)
        self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
```

#### Chunking Configuration
```python
# Customize chunking strategy
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Larger chunks
    chunk_overlap=200,    # More overlap
    separators=["\n\n", "\n", " ", ""]  # Custom separators
)
```

---

## 🏗️ Architecture Details

### Graph Schema

```cypher
// Document Node
(:Document {
    id: STRING,          // Unique identifier
    content: STRING,     // Full document text
    source: STRING,      // File path or URL
    created: DATETIME,   // Creation timestamp
    // Additional metadata as properties
    category: STRING,
    author: STRING,
    ...
})

// Chunk Node
(:Chunk {
    text: STRING,           // Chunk text
    embedding: FLOAT[384],  // Vector embedding
    chunk_index: INTEGER    // Position in document
})

// Relationships
(document:Document)-[:HAS_CHUNK]->(chunk:Chunk)
```

### Data Flow

1. **Document Input** → Docling extraction
2. **Text Processing** → Chunking with overlap
3. **Embedding Generation** → 384-dimensional vectors
4. **Neo4j Storage** → Nodes and relationships
5. **Index Creation** → Vector and text indexes
6. **Search Query** → Embedding generation
7. **Similarity Search** → Cosine similarity
8. **Result Ranking** → Score-based ordering
9. **Context Assembly** → Chunk aggregation
10. **Response Generation** → LLM or direct return

---

## 📊 Performance Benchmarks

### System Performance

| Operation | Performance | Documents | Chunks |
|-----------|------------|-----------|--------|
| Vector Search | 60ms/query | 14 docs | 8,547 chunks |
| Hybrid Search | 24ms/query | 14 docs | 8,547 chunks |
| Document Load | 2.5s/doc | - | - |
| PDF Extraction | 17s/PDF | - | ~600 chunks/PDF |
| Embedding Generation | 15ms/chunk | - | - |
| Database Write | 50ms/chunk | - | - |

### Optimization Tips

1. **For Large Datasets (>1000 docs)**:
   ```python
   # Use optimized version
   from neo4j_rag_optimized import Neo4jRAGOptimized
   rag = Neo4jRAGOptimized()
   ```

2. **Memory Configuration**:
   ```bash
   # Docker memory settings
   -e NEO4J_server_memory_heap_max__size=4g
   -e NEO4J_server_memory_pagecache_size=2g
   ```

3. **Batch Processing**:
   ```python
   # Process in batches
   rag.vector_search_optimized(
       query="search term",
       k=5,
       batch_size=100
   )
   ```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Connection Refused** | Check Docker: `docker ps \| grep neo4j` |
| **Out of Memory** | Increase Docker memory or use optimized version |
| **Slow Search** | Create indexes: `CREATE INDEX ON :Chunk(embedding)` |
| **Import Errors** | Activate venv: `source venv/bin/activate` |
| **PDF Extraction Fails** | Check Docling installation: `pip install --upgrade docling` |
| **No Search Results** | Verify data loaded: `rag.get_stats()` |

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check what's in the database
from neo4j_rag import Neo4jRAG
rag = Neo4jRAG()

# Detailed stats
print("Stats:", rag.get_stats())

# Sample documents
with rag.driver.session() as session:
    result = session.run("MATCH (d:Document) RETURN d.source LIMIT 5")
    for record in result:
        print(record['d.source'])
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/neo4j-rag-system.git
cd neo4j-rag-system

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black *.py

# Check style
flake8 *.py
```

---

## 📚 Resources & References

### Official Documentation
- 📖 [Neo4j Documentation](https://neo4j.com/docs/)
- 🐍 [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- 🤖 [Neo4j GraphRAG](https://neo4j.com/docs/neo4j-graphrag-python/)
- 📄 [Docling Documentation](https://github.com/DS4SD/docling)
- 🔗 [LangChain Docs](https://python.langchain.com/)
- 🎯 [Sentence Transformers](https://www.sbert.net/)

### Tutorials & Articles
- [Building RAG with Neo4j](https://neo4j.com/blog/developer/rag-tutorial/)
- [Vector Search in Neo4j](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/)
- [Graph RAG Patterns](https://neo4j.com/developer/graph-rag/)

### Community & Support
- 💬 [Neo4j Community Forum](https://community.neo4j.com/)
- 🐛 [Report Issues](https://github.com/yourusername/neo4j-rag-system/issues)
- ⭐ [Star on GitHub](https://github.com/yourusername/neo4j-rag-system)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by the Neo4j RAG Community
  <br>
  ⭐ Star us on GitHub!
</p>