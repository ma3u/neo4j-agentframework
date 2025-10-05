# Local Testing Guide - 100% Local RAG (No Azure Required!)

This guide shows how to run the RAG system **completely locally** using SentenceTransformer embeddings without any Azure credentials.

## 🎯 Two Deployment Options

### Option 1: 100% Local (This Guide)
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2) - runs locally
- **LLM**: Not included (RAG retrieval only)
- **Requirements**: NO Azure credentials needed!
- **Container Size**: ~2.5GB (includes PyTorch, transformers, models)
- **Memory**: ~2-4GB RAM
- **Use Case**: Local development, testing, offline use

### Option 2: Azure-Optimized (`docker-compose.yml`)
- **Embeddings**: Azure OpenAI API (cloud-based)
- **LLM**: BitNet on Azure AI Foundry (cloud-based)
- **Requirements**: Azure OpenAI credentials required
- **Container Size**: ~500MB (no local models)
- **Memory**: ~256-512MB RAM
- **Use Case**: Production deployment with cost optimization

---

## 🚀 Quick Start - Local Testing

### 1. Start Local Services

```bash
# Build and start 100% local RAG system
docker-compose -f docker-compose-local.yml up -d --build

# Check status
docker-compose -f docker-compose-local.yml ps

# View logs
docker-compose -f docker-compose-local.yml logs -f local-rag
```

### 2. Wait for Startup (~60 seconds)

The local RAG app needs time to:
1. Download SentenceTransformer model (first run only)
2. Load model into memory (~384MB)
3. Connect to Neo4j database

### 3. Test the System

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "model": "SentenceTransformer (all-MiniLM-L6-v2)",
  "deployment": "100% local - no Azure required",
  "neo4j_stats": { ... }
}

# Get statistics
curl http://localhost:8000/stats
```

### 4. Add a Test Document

```bash
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Neo4j is a graph database that stores data as nodes and relationships.",
    "metadata": {"source": "test", "category": "graph-db"}
  }'
```

### 5. Query the RAG System

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Neo4j?",
    "k": 3
  }'
```

### 6. Search for Similar Content

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "question": "graph database",
    "k": 5
  }'
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│   Local RAG Application (No Azure!)         │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │  FastAPI API (app_local.py)       │    │
│  └────────────────────────────────────┘    │
│               │                              │
│  ┌────────────────────────────────────┐    │
│  │  Neo4jRAG (src/neo4j_rag.py)      │    │
│  │  - SentenceTransformer embeddings  │    │
│  │  - Vector search                    │    │
│  │  - Hybrid search                    │    │
│  └────────────────────────────────────┘    │
│               │                              │
└───────────────┼──────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│  Neo4j Graph Database (neo4j:latest)        │
│  - Document nodes                            │
│  - Chunk nodes with embeddings              │
│  - Vector indexes                           │
└─────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` (optional - has defaults):

```bash
# Neo4j Configuration
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### Resource Requirements

**Minimum**:
- RAM: 4GB (2GB for app + 2GB for Neo4j)
- CPU: 2 cores
- Disk: 10GB

**Recommended**:
- RAM: 8GB (4GB for app + 4GB for Neo4j)
- CPU: 4 cores
- Disk: 20GB

---

## 📝 API Endpoints

### Health & Stats
- `GET /health` - Health check with model info
- `GET /stats` - System statistics

### Document Management
- `POST /documents` - Add document to knowledge base
  ```json
  {
    "content": "Your document text here",
    "metadata": {"source": "file.pdf", "page": 1}
  }
  ```

### Query & Search
- `POST /query` - RAG query with answer generation
  ```json
  {
    "question": "What is Neo4j?",
    "k": 5
  }
  ```

- `POST /search` - Vector similarity search
  ```json
  {
    "question": "graph database",
    "k": 10
  }
  ```

---

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose -f docker-compose-local.yml down

# Stop and remove volumes (deletes all data!)
docker-compose -f docker-compose-local.yml down -v
```

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose -f docker-compose-local.yml logs local-rag

# Common issues:
# - Neo4j not ready: Wait 30 seconds for Neo4j startup
# - Out of memory: Increase Docker memory limit to 8GB
# - Model download failed: Check internet connection (first run only)
```

### Health check fails
```bash
# Test manually
curl http://localhost:8000/health

# If "initializing": Wait for model to load (~60 seconds first run)
# If connection refused: Check container is running
docker-compose -f docker-compose-local.yml ps
```

### Neo4j Browser access
- URL: http://localhost:7474
- Username: `neo4j`
- Password: `password`
- Connection: `bolt://localhost:7687`

---

## 📚 Next Steps

1. **Load Sample Data**: Use `scripts/load_sample_data.py`
2. **Upload PDFs**: Use `scripts/upload_pdfs_to_neo4j.py`
3. **Explore Queries**: Check `scripts/rag_search_examples.py`
4. **View Statistics**: Run `scripts/rag_statistics.py`

---

## ⚖️ Local vs Azure Comparison

| Feature | Local (This Setup) | Azure (docker-compose.yml) |
|---------|-------------------|----------------------------|
| **Azure Credentials** | ❌ Not required | ✅ Required |
| **Internet Required** | ❌ No (after first run) | ✅ Yes (API calls) |
| **Cost** | 💰 Free (compute only) | 💰 Pay per API call |
| **Container Size** | 📦 ~2.5GB | 📦 ~500MB |
| **Memory Usage** | 🐏 2-4GB | 🐏 256-512MB |
| **Startup Time** | ⏱️ ~60s (model loading) | ⏱️ ~10s |
| **Embeddings** | 🏠 Local (SentenceTransformer) | ☁️ Azure OpenAI API |
| **LLM Inference** | ❌ Not included | ☁️ Azure BitNet |
| **Data Privacy** | 🔒 100% local | ☁️ Sent to Azure |

**When to use Local**: Development, testing, offline use, data privacy requirements
**When to use Azure**: Production, cost optimization, managed infrastructure

---

## 🎓 Technical Details

### Embedding Model
- **Model**: `all-MiniLM-L6-v2` (SentenceTransformer)
- **Dimensions**: 384
- **Size**: ~90MB
- **Speed**: ~100-500ms per query (CPU)
- **Quality**: Optimized for semantic similarity

### Performance Characteristics
- **Vector Search**: ~50-200ms per query
- **Hybrid Search**: ~100-300ms per query
- **Document Indexing**: ~1-5s per document (depending on size)
- **Concurrent Requests**: Supports multiple simultaneous queries

---

## 🔗 Related Files

- `app_local.py` - Local FastAPI application
- `Dockerfile.local` - Local container build
- `docker-compose-local.yml` - Local orchestration
- `src/neo4j_rag.py` - Core RAG implementation (local)
- `src/bitnet_azure_rag.py` - Azure RAG implementation (different file!)

---

**Created**: 2025-10-04
**For Questions**: Check README.md or CLAUDE.md
