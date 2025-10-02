# Neo4j RAG (Retrieval-Augmented Generation) System

A comprehensive implementation of RAG using Neo4j as the vector database, featuring both a custom implementation and integration with the official Neo4j GraphRAG library.

## 📚 Official Documentation

- **[Neo4j RAG Tutorial](https://neo4j.com/blog/developer/rag-tutorial/)** - Official Neo4j blog tutorial on RAG implementation
- **[Neo4j GraphRAG Python Documentation](https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html)** - Official Python library documentation
- **[Neo4j GraphRAG GitHub](https://github.com/neo4j/neo4j-graphrag-python)** - Source code and examples

## 🎯 Overview

This repository provides two complete RAG implementations:

1. **Custom Implementation** (`neo4j_rag.py`) - Fully functional with Neo4j 5.11+, using basic Neo4j driver and sentence transformers
2. **Official Neo4j GraphRAG** (`official_graphrag_demo.py`) - Using Neo4j's official GraphRAG Python library (requires Neo4j 5.18+)

## ✨ Features

- **Vector Similarity Search**: Semantic search using sentence embeddings
- **Hybrid Search**: Combines vector similarity with keyword matching
- **Document Management**: Store and retrieve documents with metadata
- **Chunk Management**: Automatic text splitting and embedding generation
- **Query Engine**: Complete RAG pipeline with context retrieval
- **Multiple Embedding Providers**: Support for OpenAI, Sentence Transformers, and more
- **Production-Ready**: Includes performance benchmarks and best practices

## 🚀 Quick Start

### Prerequisites

- Docker installed
- Python 3.12
- Neo4j database

### Step 1: Set Up Neo4j Database

#### Option A: Neo4j Community Edition (For Custom Implementation)

```bash
# Run Neo4j 5.11 (compatible with custom implementation)
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11

# Verify it's running
docker ps | grep neo4j-rag

# Access Neo4j Browser at http://localhost:7474
# Login: neo4j / password
```

#### Option B: Neo4j 5.18+ (For Official GraphRAG)

```bash
# Stop old version if running
docker stop neo4j-rag && docker rm neo4j-rag

# Run latest Neo4j (required for official GraphRAG)
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:latest

# Verify version (should be 5.18.1+)
docker exec neo4j-rag neo4j --version
```

### Step 2: Install Python Environment

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# For custom implementation
pip install -r requirements.txt

# For official GraphRAG (requires Neo4j 5.18+)
pip install neo4j-graphrag[openai,langchain]
# Or with specific providers:
# pip install neo4j-graphrag[openai]     # OpenAI only
# pip install neo4j-graphrag[langchain]  # LangChain integration
# pip install neo4j-graphrag[all]        # All providers
```

### Step 3: Run the Implementation

#### Custom Implementation (Works with Neo4j 5.11+)

```bash
# 1. Load sample data
python load_sample_data.py

# 2. Run comprehensive tests
python test_rag.py
```

This loads 8 sample documents covering:
- Neo4j and graph databases
- Cypher query language
- RAG concepts and implementation
- Vector embeddings
- Best practices

#### Official GraphRAG (Requires Neo4j 5.18+)

```bash
# Run the official GraphRAG demo
python official_graphrag_demo.py
```

## 💻 Code Examples

### Custom Implementation

```python
from neo4j_rag import Neo4jRAG, RAGQueryEngine

# Initialize RAG system
rag = Neo4jRAG(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password"
)

# Add a document
rag.add_document(
    content="Your document text here",
    metadata={"source": "my_doc", "category": "example"}
)

# Vector search
results = rag.vector_search("What is Neo4j?", k=3)
for result in results:
    print(f"Score: {result['score']:.3f}, Text: {result['text'][:100]}...")

# Hybrid search (combines vector and keyword)
results = rag.hybrid_search("graph database", k=3)

# Use the RAG Query Engine
engine = RAGQueryEngine(rag)
response = engine.query("How do graph databases work?", k=3)
print(response['context'])

# Close connection
rag.close()
```

### Official GraphRAG Implementation

```python
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.embeddings import OpenAIEmbeddings

# Setup
driver = GraphDatabase.driver(uri, auth=auth)
embedder = OpenAIEmbeddings(model="text-embedding-3-large")
retriever = VectorRetriever(driver, index_name, embedder)
llm = OpenAILLM(model_name="gpt-4")

# Create RAG pipeline
rag = GraphRAG(retriever=retriever, llm=llm)

# Query
response = rag.search(
    query_text="What is Neo4j?",
    retriever_config={"top_k": 5}
)
```

## 📦 API Reference

### Custom Implementation

#### Neo4jRAG Class

- `add_document(content, metadata, doc_id)`: Add document to the database
- `vector_search(query, k)`: Perform vector similarity search
- `hybrid_search(query, k)`: Perform hybrid search (vector + keyword)
- `get_context(query, k)`: Get context for RAG
- `get_stats()`: Get database statistics
- `clear_database()`: Clear all data
- `close()`: Close database connection

#### RAGQueryEngine Class

- `query(question, k)`: Query the RAG system and get context + sources

### Official GraphRAG Components

#### Retrievers
- **VectorRetriever**: Semantic similarity search in Neo4j vector index
- **VectorCypherRetriever**: Combines vector search with graph traversal
- **HybridRetriever**: Search across vector and full-text indexes
- **Text2CypherRetriever**: Natural language to Cypher conversion

#### Supported Embedding Providers
- OpenAI (`pip install neo4j-graphrag[openai]`)
- Sentence Transformers (local, no API key required)
- Azure OpenAI (`pip install neo4j-graphrag[azure]`)
- Google VertexAI (`pip install neo4j-graphrag[vertexai]`)
- Cohere (`pip install neo4j-graphrag[cohere]`)
- MistralAI (`pip install neo4j-graphrag[mistralai]`)
- Ollama (`pip install neo4j-graphrag[ollama]`)

## 📊 Performance

Based on test results with 8 documents and 12 chunks:

- **Vector Search**: ~60ms per query (16.6 queries/second)
- **Hybrid Search**: ~24ms per query (41.4 queries/second)
- **Full RAG Query**: ~300ms per query

## 🏗️ Architecture

### Custom Implementation Architecture

```
Documents → Text Splitter → Chunks → Embeddings → Neo4j
                                                      ↓
User Query → Embedding → Vector/Keyword Search → Context → Response
```

### Official Neo4j GraphRAG Architecture

```
Documents
    ↓
Neo4j GraphRAG Pipeline
    ├── Embedders (multiple providers)
    ├── Retrievers
    │   ├── VectorRetriever
    │   ├── VectorCypherRetriever
    │   ├── HybridRetriever
    │   └── Text2CypherRetriever
    ├── LLMs (multiple providers)
    └── GraphRAG orchestration
    ↓
Enhanced Response with Graph Context
```

## 🗄️ Neo4j Graph Structure

### Nodes

```cypher
// Document Node
(:Document {
  id: "doc_1",
  content: "Full document text",
  source: "document_source",
  category: "category_name",
  created: datetime
})

// Chunk Node
(:Chunk {
  text: "Chunk text",
  embedding: [384-dimensional vector],
  chunk_index: 0
})
```

### Relationships

```cypher
(document:Document)-[:HAS_CHUNK]->(chunk:Chunk)
```

### Useful Cypher Queries

```cypher
// Count documents and chunks
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN COUNT(DISTINCT d) as documents, COUNT(c) as chunks

// Find similar chunks (manual)
MATCH (c:Chunk)
WITH c, gds.similarity.cosine(c.embedding, $query_embedding) as similarity
WHERE similarity > 0.7
RETURN c.text, similarity
ORDER BY similarity DESC
LIMIT 5

// Clear all data
MATCH (n) DETACH DELETE n
```

## ⚙️ Customization

### Change Embedding Model

For custom implementation, edit `neo4j_rag.py`:
```python
self.embedding_model = SentenceTransformer('your-model-name')
```

For official GraphRAG:
```python
from neo4j_graphrag.embeddings import SentenceTransformerEmbeddings
embedder = SentenceTransformerEmbeddings(model="all-MiniLM-L6-v2")
```

### Adjust Chunk Size

Edit `neo4j_rag.py`:
```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Change size
    chunk_overlap=100  # Change overlap
)
```

## 🔧 Troubleshooting

### Neo4j Connection Issues

```bash
# Check if Neo4j is running
docker ps | grep neo4j-rag

# Restart Neo4j
docker restart neo4j-rag

# Check logs
docker logs neo4j-rag

# Test connection
curl http://localhost:7474
```

### Version Incompatibility

The official `neo4j-graphrag` requires Neo4j 5.18.1+. If you see:
```
Neo4jVersionError: This package only supports Neo4j version 5.18.1 or greater
```

**Solution**: Either upgrade Neo4j to latest version or use the custom implementation which works with Neo4j 5.11+.

### Missing API Keys

For OpenAI embeddings:
```bash
export OPENAI_API_KEY="your-api-key"
```

For local embeddings without API keys, use Sentence Transformers:
```python
from neo4j_graphrag.embeddings import SentenceTransformerEmbeddings
embedder = SentenceTransformerEmbeddings(model="all-MiniLM-L6-v2")
```

## 📈 Best Practices

1. **Chunk Size**: Use 200-500 tokens for optimal balance between context and precision
2. **Overlap**: Implement 10-20% chunk overlap to maintain context continuity
3. **Embeddings**: Choose models based on your domain (general vs specialized)
4. **Indexing**: Always create vector indexes for performance
5. **Hybrid Search**: Combine vector and keyword search for better results
6. **Caching**: Cache embeddings for frequently accessed content
7. **Monitoring**: Track retrieval quality metrics and response times
8. **Batch Processing**: Process documents in batches for better performance

## 🧪 Testing

### Prerequisites for Testing

Before testing, ensure Neo4j is running with Java Vector API optimization for best performance:

```bash
# Start Neo4j with Vector API optimization
docker run -d \
  --name neo4j-rag \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -e NEO4J_server_jvm_additional='-XX:+UnlockExperimentalVMOptions --add-modules jdk.incubator.vector' \
  neo4j:latest
```

### Step-by-Step Testing Guide

#### Step 1: Load Sample Data

First, load the sample documents into Neo4j:

```bash
python load_sample_data.py
```

**Expected Output:**
```
INFO:__main__:Loading 8 documents...
INFO:neo4j_rag:Added document doc_1 with 2 chunks
INFO:neo4j_rag:Added document doc_2 with 1 chunks
...
INFO:__main__:Database statistics: {'documents': 8, 'chunks': 12}
INFO:__main__:Sample data loaded successfully!
```

#### Step 2: Run Comprehensive Test Suite

Execute the full test suite to validate all functionality:

```bash
python test_rag.py
```

**Test Coverage:**
- ✅ Vector similarity search with 5 different queries
- ✅ Hybrid search (vector + keyword) with 3 query types
- ✅ RAG query engine with 4 complex questions
- ✅ Database statistics and health checks
- ✅ Performance benchmarks (10 queries each for vector and hybrid search)

**Expected Performance Metrics:**
```
⚡ Vector Search Performance:
  • Total time: 0.180s
  • Average per query: 0.018s
  • Queries per second: 55.5

⚡ Hybrid Search Performance:
  • Total time: 0.223s
  • Average per query: 0.022s
  • Queries per second: 44.9
```

#### Step 3: Interactive Testing

Test with your own questions using the interactive interface:

```bash
python interactive_test.py
```

**Sample Session:**
```
🤖 NEO4J RAG INTERACTIVE SESSION 🤖
Ask any question about Neo4j, RAG, or related topics!

❓ Your question: What is Neo4j?
📚 Found 3 relevant sources:
   1. [0.704] doc_1: Neo4j is a highly scalable native graph database...
   2. [0.604] doc_2: Cypher is Neo4j's declarative graph query language...
   3. [0.522] doc_6: Neo4j can be effectively used as a vector database...

💡 Answer: Based on the retrieved context...
```

**Recommended Test Queries:**
- "What is Neo4j?"
- "How do vector embeddings work?"
- "What are RAG best practices?"
- "How to implement Cypher queries?"
- "What's the difference between graph and relational databases?"

#### Step 4: Verify Vector API Optimization

Check that the Java Vector API is working correctly:

```bash
# Check Neo4j logs - should show "Using incubator modules: jdk.incubator.vector"
docker logs neo4j-rag | grep "incubator"
```

**Expected Output:**
```
WARNING: Using incubator modules: jdk.incubator.vector
```

### Testing Different Implementations

#### Custom Implementation (Recommended)

```bash
# Run all tests for custom implementation
python test_rag.py

# Test individual components
python -c "from neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); results = rag.vector_search('What is Neo4j?', k=3); print([r['score'] for r in results]); rag.close()"
```

#### Official GraphRAG (Optional)

```bash
# Test official Neo4j GraphRAG (may have LLM compatibility issues)
python official_graphrag_demo.py
```

### Performance Benchmarking

For detailed performance analysis:

```bash
# Performance benchmark only
python -c "from test_rag import test_performance; from neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); test_performance(rag); rag.close()"

# Database statistics
python -c "from neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); stats = rag.get_stats(); print(f'Documents: {stats[\"documents\"]}, Chunks: {stats[\"chunks\"]}'); rag.close()"
```

### Success Criteria

Your RAG system is working correctly if:

1. ✅ **Data Loading**: 8 documents loaded, 12 chunks created
2. ✅ **Vector Search**: Returns relevant results with similarity scores > 0.5
3. ✅ **Performance**: Achieves >50 queries/second for vector search
4. ✅ **Interactive**: Responds appropriately to natural language questions
5. ✅ **No Errors**: All tests complete without connection or embedding errors

### Troubleshooting Test Issues

#### "No data found in database"
```bash
# Reload sample data
python load_sample_data.py
```

#### Poor search results or low similarity scores
```bash
# Check if embeddings are generated correctly
python -c "from neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); results = rag.vector_search('Neo4j database', k=1); print(f'Top result score: {results[0][\"score\"] if results else \"No results\"}'); rag.close()"
```

#### Slow performance
```bash
# Verify Java Vector API is enabled
docker logs neo4j-rag 2>&1 | grep -i vector
```

## 🌐 Exploring RAG Data in Neo4j Browser

Once your data is loaded, you can explore it visually using the Neo4j Browser at http://localhost:7474.

### Essential Cypher Queries for RAG Data Exploration

#### 1. View Documents by Category
```cypher
MATCH (d:Document) 
RETURN d.category, COUNT(d) as document_count, COLLECT(d.source) as sources
ORDER BY document_count DESC
```

**Expected Results:**
| d.category | document_count | sources |
|------------|----------------|----------|
| "database" | 1 | ["neo4j_overview"] |
| "query_language" | 1 | ["cypher_guide"] |
| "comparison" | 1 | ["graph_vs_relational"] |
| "ai" | 1 | ["rag_concepts"] |
| "integration" | 1 | ["neo4j_rag"] |
| "programming" | 1 | ["python_rag"] |
| "best_practices" | 1 | ["rag_best_practices"] |

![Document Categories](images/neo4j-document-categories.png)
*Documents organized by category in Neo4j Browser*

#### 2. Comprehensive Overview (Most Useful)
```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
RETURN d.source, 
       d.category, 
       d.topic,
       COUNT(c) as chunk_count,
       substring(d.content, 0, 100) + '...' as content_preview
ORDER BY d.source
```

**Expected Results:**
| d.source | d.category | d.topic | chunk_count | content_preview |
|----------|------------|---------|-------------|------------------|
| "neo4j_overview" | "database" | "graph_database" | 2 | "Neo4j is a highly scalable native graph database management system..." |
| "cypher_guide" | "query_language" | "cypher" | 1 | "Cypher is Neo4j's declarative graph query language..." |
| "rag_concepts" | "ai" | "rag" | 2 | "Retrieval-Augmented Generation (RAG) is an AI framework..." |

#### 3. Visualize Graph Structure
```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
RETURN d, c
LIMIT 20
```

**What You'll See:**
- 🟢 **Green circles**: Document nodes (8 total)
- 🔵 **Blue circles**: Chunk nodes (12 total) 
- **Arrows**: HAS_CHUNK relationships connecting documents to their chunks
- **Node Statistics**: "Displaying 9 nodes, 0 relationships" in the overview panel

![Neo4j Graph Visualization](images/neo4j-graph-visualization.png)
*Neo4j Browser showing the RAG system's document-chunk relationships*

#### 4. Get Database Statistics
```cypher
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN COUNT(DISTINCT d) as total_documents, 
       COUNT(c) as total_chunks
```

**Expected Results:**
| total_documents | total_chunks |
|-----------------|-------------|
| 8 | 12 |

#### 5. Sample Embedding Data
```cypher
MATCH (c:Chunk)
RETURN substring(c.text, 0, 50) + '...' AS text_preview,
       size(c.embedding) AS embedding_dimensions,
       c.embedding[0..3] AS first_4_embedding_values
LIMIT 3
```

**Expected Results:**
| text_preview | embedding_dimensions | first_4_embedding_values |
|--------------|---------------------|-------------------------|
| "Neo4j is a highly scalable native graph databa..." | 384 | [0.123, -0.456, 0.789, -0.321] |
| "Cypher is Neo4j's declarative graph query lang..." | 384 | [-0.234, 0.567, -0.890, 0.432] |
| "Graph databases differ from traditional relat..." | 384 | [0.345, -0.678, 0.901, -0.543] |

### Visual Graph Exploration Tips

1. **Switch to Graph View**: Click the graph icon when viewing results
2. **Expand Relationships**: Double-click on nodes to see their connections
3. **Filter by Labels**: Use the node labels panel (Document, Chunk) to show/hide node types
4. **Zoom and Pan**: Use mouse wheel to zoom, drag to pan around the graph
5. **Node Properties**: Click on any node to see its properties in the details panel

### Graph Structure Overview

Your RAG system creates this structure:
```
📄 Document ("neo4j_overview")
├── 📝 Chunk 0: "Neo4j is a highly scalable..."
└── 📝 Chunk 1: "Each node represents an entity..."

📄 Document ("cypher_guide")
└── 📝 Chunk 0: "Cypher is Neo4j's declarative..."

📄 Document ("rag_concepts")
├── 📝 Chunk 0: "Retrieval-Augmented Generation..."
└── 📝 Chunk 1: "The RAG pipeline typically..."
```

**Node Labels Visible:**
- 🔖 **Document (8)**: Each source document with metadata
- 🔖 **Chunk (12)**: Text chunks with 384-dimensional embeddings

**Relationship Types:**
- ➡️ **HAS_CHUNK (12)**: Links documents to their text chunks

## 🔍 What You Can Query

Your RAG system now has comprehensive Neo4j knowledge! You can ask questions like:

### Production & Operations
- "How do I configure Neo4j for production workloads?"
- "What are the memory requirements for large Neo4j databases?"
- "How to set up Neo4j clustering and high availability?"
- "What are Neo4j backup and recovery best practices?"
- "How to monitor Neo4j performance metrics?"

### RAG Implementation
- "How to implement advanced RAG patterns with Neo4j?"
- "What are the best practices for Neo4j vector search?"
- "How to optimize Neo4j for RAG applications?"
- "How to use the Neo4j GraphRAG Python library?"
- "What are the optimal chunk sizes for different use cases?"

### Development & Cypher
- "How to write efficient Cypher queries?"
- "What are Neo4j indexing strategies?"
- "How to use Neo4j Python driver effectively?"
- "What are Cypher query optimization techniques?"
- "How to model graph schemas for different domains?"

### Getting Started Examples
```python
from neo4j_rag import Neo4jRAG, RAGQueryEngine

# Initialize the system
rag = Neo4jRAG()
engine = RAGQueryEngine(rag)

# Ask production questions
response = engine.query("How do I configure Neo4j memory settings for production?")
print(response['answer'])

# Ask about RAG implementation
response = engine.query("What are best practices for vector search in Neo4j?")
print(response['answer'])

# Ask about Cypher
response = engine.query("How to optimize Cypher queries for large datasets?")
print(response['answer'])

rag.close()
```

## ⚠️ Production Considerations

1. **Security**:
   - Never hardcode credentials
   - Use environment variables or secret management systems
   - Implement proper authentication and authorization

2. **Scaling**:
   - Consider Neo4j Aura for managed cloud deployment
   - Implement connection pooling
   - Use read replicas for search operations

3. **Cost Management**:
   - Monitor API usage for embedding and LLM providers
   - Implement rate limiting
   - Cache frequently accessed embeddings

4. **Performance**:
   - Create appropriate indexes
   - Optimize chunk sizes based on your use case
   - Implement async operations where possible

5. **Monitoring**:
   - Add comprehensive logging
   - Track query performance metrics
   - Monitor embedding quality and drift

## 🔗 Additional Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [GraphRAG Concepts](https://neo4j.com/blog/graphrag-concepts/)
- [LangChain Neo4j Integration](https://python.langchain.com/docs/integrations/graphs/neo4j_cypher)
- [Vector Search in Neo4j](https://neo4j.com/docs/cypher-manual/current/syntax/functions/vector-similarity-functions/)
- [Neo4j Community Forum](https://community.neo4j.com/)

## 📝 License

This is a demonstration project for educational purposes. Refer to Neo4j's licensing for production use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

---

*Built with Neo4j - The Graph Database Platform for Connected Data*