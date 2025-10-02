# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Neo4j RAG (Retrieval-Augmented Generation) system demo that provides two implementations:
1. **Custom implementation** (`neo4j_rag.py`) - Works with Neo4j 5.11+
2. **Official GraphRAG** (`official_graphrag_demo.py`) - Requires Neo4j 5.18+

## Essential Commands

### Environment Setup
```bash
# Activate virtual environment (required for all operations)
source venv/bin/activate

# Install dependencies for custom implementation
pip install -r requirements.txt

# Install for official GraphRAG (requires Neo4j 5.18+)
pip install neo4j-graphrag[openai,langchain]
```

### Neo4j Database Management
```bash
# Start Neo4j (custom implementation, v5.11)
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.11

# Start Neo4j with Vector API optimization (better performance)
docker run -d --name neo4j-rag \
  -p7474:7474 -p7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_server_jvm_additional='-XX:+UnlockExperimentalVMOptions --add-modules jdk.incubator.vector' \
  neo4j:latest

# Check Neo4j status
docker ps | grep neo4j-rag
docker logs neo4j-rag
```

### Running the System
```bash
# Load sample data (8 documents about Neo4j, RAG, etc.)
python load_sample_data.py

# Run comprehensive test suite
python test_rag.py

# Interactive testing (if available)
python interactive_test.py

# Load knowledge base (if available)
python load_knowledge_base.py
```

### Testing Specific Components
```bash
# Test vector search only
python -c "from neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); results = rag.vector_search('What is Neo4j?', k=3); print([r['score'] for r in results]); rag.close()"

# Test performance benchmark
python -c "from test_rag import test_performance; from neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); test_performance(rag); rag.close()"

# Check database statistics
python -c "from neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); stats = rag.get_stats(); print(f'Documents: {stats[\"documents\"]}, Chunks: {stats[\"chunks\"]}'); rag.close()"
```

## Architecture Overview

### Two-Implementation Pattern
The codebase provides both a custom implementation and official library integration to demonstrate flexibility and compatibility with different Neo4j versions.

### Custom Implementation (`neo4j_rag.py`)
- **Neo4jRAG class**: Core RAG system with document/chunk management
- **RAGQueryEngine class**: Query processing and context retrieval
- **Embedding Strategy**: Uses SentenceTransformer('all-MiniLM-L6-v2') for local embeddings (384 dimensions)
- **Chunking Strategy**: RecursiveCharacterTextSplitter with chunk_size=500, overlap=50
- **Search Methods**:
  - `vector_search()`: Cosine similarity on embeddings
  - `hybrid_search()`: Combines vector + keyword search
- **Graph Structure**:
  - Document nodes store full content + metadata as properties
  - Chunk nodes store text fragments + embeddings
  - HAS_CHUNK relationships connect documents to chunks

### Official GraphRAG Implementation (`official_graphrag_demo.py`)
- **Neo4jGraphRAGDemo class**: Wrapper around official library
- **SimpleLLM class**: Mock LLM for demos without API keys
- **Retriever Types**: VectorRetriever, VectorCypherRetriever
- **Multiple embedding providers supported** (OpenAI, SentenceTransformers, etc.)

### Key Design Decisions

1. **Metadata Storage**: Neo4j doesn't support nested maps, so metadata is flattened to individual properties on Document nodes

2. **Parameter Naming**: Cypher parameters avoid conflicts (e.g., `search_query` instead of `query`)

3. **Connection Management**: Always close Neo4j driver after operations to prevent connection leaks

4. **Error Handling**: Version compatibility checks for official GraphRAG (requires Neo4j 5.18.1+)

## Working with Neo4j Data

### Essential Cypher Queries
```cypher
-- Count documents and chunks
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN COUNT(DISTINCT d) as documents, COUNT(c) as chunks

-- Clear all data
MATCH (n) DETACH DELETE n

-- View document structure
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
RETURN d, c LIMIT 20
```

### Expected Database State
After running `load_sample_data.py`:
- 8 Document nodes with properties: id, content, source, category, topic, created
- 12 Chunk nodes with properties: text, embedding (384-dim array), chunk_index
- 12 HAS_CHUNK relationships

## Performance Targets
- Vector Search: ~60ms per query (16.6 queries/second)
- Hybrid Search: ~24ms per query (41.4 queries/second)
- Full RAG Query: ~300ms per query

## Common Issues

1. **Neo4j Connection**: Default credentials are neo4j/password on bolt://localhost:7687
2. **Version Incompatibility**: Official GraphRAG requires Neo4j 5.18.1+ (use custom implementation for older versions)
3. **Embedding Dimensions**: Always 384 for all-MiniLM-L6-v2 model
4. **LLM Compatibility**: SimpleLLM in official_graphrag_demo.py may need `**kwargs` in invoke() method