# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project Overview

**Neo4j RAG + BitNet + Azure Agent Framework** - A complete production-ready RAG (Retrieval-Augmented Generation) system combining:

1. **Neo4j Database** - High-performance graph database with 417x retrieval performance improvement
2. **BitNet.cpp Integration** - Microsoft's 1.58-bit quantized LLM (87% memory reduction)
3. **Azure Agent Framework** - Enterprise-grade conversational AI orchestration
4. **100% Local Operation** - Optional Azure integration for production deployment

### Key Performance Metrics
- **Vector Search**: <100ms (417x improvement from 46s baseline)
- **BitNet Inference**: 2-5s with 1.5GB memory footprint
- **Auto-scaling**: 0-10 instances on Azure
- **Cost Savings**: $100+/month compared to traditional RAG systems

## Project Structure

```
.
├── README.md                      # Main project documentation
├── CLAUDE.md                      # This file - Claude Code guidance
├── scripts/                       # Deployment and utility scripts
│   ├── docker-compose.optimized.yml
│   ├── azure-deploy-complete.sh
│   ├── Dockerfile.bitnet-*
│   └── *.py (helper scripts)
├── neo4j-rag-demo/               # Core RAG implementation
│   ├── src/                      # Source code
│   │   ├── neo4j_rag.py         # Main RAG system (417x optimized)
│   │   ├── docling_loader.py    # Advanced PDF processing
│   │   └── azure_agent/         # Agent Framework integration
│   ├── scripts/                  # Utility scripts
│   ├── tests/                    # Test suite
│   ├── azure_deploy/             # Azure deployment configs
│   └── requirements.txt
├── docs/                         # Comprehensive documentation
│   ├── README-QUICKSTART.md      # Getting started guide
│   ├── LOCAL-TESTING-GUIDE.md    # Local testing procedures
│   ├── DEPLOYMENT.md             # Deployment instructions
│   ├── BITNET-SUCCESS.md         # BitNet build documentation
│   └── IMPLEMENTATION-STATUS.md  # Current status
└── BitNet/                       # Native BitNet.cpp integration
```

## Quick Start Commands

### 1. Local Development Setup

```bash
# Start optimized system (Neo4j + RAG + BitNet)
docker-compose -f scripts/docker-compose.optimized.yml up -d

# Or start Neo4j only for development
docker run -d --name neo4j-rag \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_dbms_memory_heap_max__size=4G \
  neo4j:5.11

# Setup Python environment (in neo4j-rag-demo/)
cd neo4j-rag-demo
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Load Data and Test

```bash
# Load sample data (8 documents)
cd neo4j-rag-demo
python scripts/load_sample_data.py

# Upload your own PDFs
python scripts/upload_pdfs_to_neo4j.py /path/to/pdfs/

# Test the system
python tests/test_rag.py

# Interactive demo
python scripts/rag_demo.py
```

### 3. Build and Deploy BitNet

```bash
# Build real BitNet.cpp (30 min, recommended for production)
docker build -f scripts/Dockerfile.bitnet-final -t bitnet-final:latest .

# Or build mock version for testing (1 min)
docker build -f scripts/Dockerfile.bitnet-simple -t bitnet-llm:local .

# Deploy complete stack locally
docker-compose -f scripts/docker-compose.optimized.yml up -d
```

### 4. Azure Deployment

```bash
# Quick automated deployment
./scripts/azure-deploy-complete.sh

# Or manual step-by-step (see docs/README-QUICKSTART.md)
cd neo4j-rag-demo/azure_deploy
./deploy.sh
```

## Core Components

### 1. Neo4j RAG System (`neo4j-rag-demo/src/neo4j_rag.py`)

**Main Classes:**
- `Neo4jRAG` - Core RAG system with optimizations
  - Connection pooling (10 max connections)
  - FIFO query cache (100 entries, thread-safe)
  - Parallel vector + keyword search
  - Full-text indexing

- `RAGQueryEngine` - Query processing and context retrieval

**Key Features:**
- SentenceTransformer embeddings (384 dimensions)
- RecursiveCharacterTextSplitter (300 chars, 50 overlap)
- Vector search with cosine similarity
- Hybrid search (vector + keyword, alpha=0.5)
- Similarity threshold filtering

**Usage:**
```python
from src.neo4j_rag import Neo4jRAG, RAGQueryEngine

# Initialize
rag = Neo4jRAG()
engine = RAGQueryEngine(rag)

# Add documents
rag.add_document("content", metadata={"source": "file.pdf"})

# Search
results = rag.vector_search("query", k=5)

# Query
response = engine.query("What is Neo4j?")

# Always close
rag.close()
```

### 2. PDF Processing (`neo4j-rag-demo/src/docling_loader.py`)

**DoclingDocumentLoader Class:**
- Complex PDF handling (tables, images, structure)
- Automatic chunking and embedding generation
- Metadata extraction and preservation
- Batch processing capabilities

**Usage:**
```python
from src.docling_loader import DoclingDocumentLoader
from src.neo4j_rag import Neo4jRAG

rag = Neo4jRAG()
loader = DoclingDocumentLoader(neo4j_rag=rag)

# Process files
loader.load_document("document.pdf")
loader.load_directory("/path/to/pdfs/")

# Cleanup
loader.close()
rag.close()
```

### 3. BitNet.cpp Integration

**Files:**
- `scripts/Dockerfile.bitnet-final` - Production build (real inference)
- `scripts/Dockerfile.bitnet-real` - Alternative build approach
- `scripts/bitnet_server_real.py` - FastAPI server
- `scripts/bitnet_server_simple.py` - Mock server for testing

**Key Features:**
- 1.58-bit ternary quantization (-1, 0, +1)
- 87% memory reduction (1.5GB vs 8-16GB)
- ARM TL1 optimized kernels
- Real-time inference (2-5s response)

**Health Check:**
```bash
curl http://localhost:8001/health
```

### 4. Azure Agent Framework (`neo4j-rag-demo/src/azure_agent/`)

**Components:**
- `neo4j_rag_tools.py` - RAG tools wrapper with @tool decorators
- `neo4j-rag-demo/azure_deploy/app.py` - FastAPI application
- `neo4j-rag-demo/azure_deploy/agent_service.py` - Agent orchestration

**Deployment:**
- Container Apps for auto-scaling
- Managed Identity for security
- Azure AI Foundry (GPT-4o-mini) integration

## Essential Development Workflows

### Testing Pipeline

```bash
# 1. Health checks
curl http://localhost:7474          # Neo4j Browser
curl http://localhost:8000/health   # RAG Service
curl http://localhost:8001/health   # BitNet LLM

# 2. Component tests
cd neo4j-rag-demo
python tests/test_rag.py           # RAG system
python tests/interactive_test.py    # Interactive testing

# 3. Performance testing
python scripts/rag_statistics.py    # Database stats
python scripts/rag_search_examples.py  # Search quality
```

### Performance Monitoring

```bash
# Docker container stats
docker stats --no-stream

# Neo4j memory usage
docker logs neo4j-rag | grep -i memory

# RAG service metrics
curl http://localhost:8000/stats | python3 -m json.tool

# BitNet memory check
docker stats bitnet-llm --no-stream | grep MEM
```

### Debugging Common Issues

**Connection Issues:**
```bash
# Check Neo4j
docker ps | grep neo4j
docker logs neo4j-rag --tail 50

# Test connection
cd neo4j-rag-demo
python -c "from src.neo4j_rag import Neo4jRAG; rag = Neo4jRAG(); print(rag.get_stats()); rag.close()"
```

**Performance Issues:**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor query times
from src.neo4j_rag import Neo4jRAG
import time

rag = Neo4jRAG()
start = time.time()
results = rag.vector_search("test", k=5)
print(f"Query: {(time.time() - start)*1000:.2f}ms")
rag.close()
```

**Memory Issues:**
```bash
# Increase Neo4j memory
docker run -e NEO4J_dbms_memory_heap_max__size=8G ...

# Monitor usage
docker stats neo4j-rag
```

## Version Requirements

- **Neo4j**: 5.11+ (core features), 5.18.1+ (official GraphRAG)
- **Python**: 3.11+ (3.12+ recommended)
- **Docker**: Latest version with 4GB+ RAM
- **Azure CLI**: Latest (for Azure deployment)
- **Node.js**: Not required

## Performance Characteristics

### Optimizations Implemented
- Connection pooling (reuses DB connections)
- Query caching (FIFO, 100 entries)
- Parallel processing (ThreadPoolExecutor)
- Optimized chunk size (300 chars)
- Full-text indexes (fast keyword search)
- Database-level filtering

### Benchmarks
- **Vector Search**: ~110ms (from 46s baseline = 417x improvement)
- **Hybrid Search**: ~24ms
- **Cached Queries**: <1ms (99.9% improvement)
- **PDF Processing**: ~2-3s per page
- **Memory Usage**: ~100MB base + ~50MB per 1000 chunks

## Known Issues and Limitations

1. **Nested Metadata**: Neo4j doesn't support nested maps - metadata is flattened
2. **Parameter Names**: Use unique names to avoid Cypher conflicts (e.g., `search_query` not `query`)
3. **Connection Leaks**: Always close drivers with `rag.close()`
4. **Docling Timeouts**: Large PDFs may timeout - use smaller batches
5. **BitNet Build Time**: Real BitNet.cpp takes 30 minutes to build

## Best Practices

### Code Quality
1. **Always close connections**: Use try/finally or context managers
2. **Batch operations**: Process multiple documents in one session
3. **Monitor memory**: Check heap usage for large datasets
4. **Use caching**: Enable query cache for repeated searches
5. **Optimize chunks**: Adjust chunk_size based on content type

### Deployment
1. **Start with local**: Test locally before Azure deployment
2. **Use real BitNet**: Build production BitNet.cpp for actual inference
3. **Monitor costs**: Track Azure resource usage
4. **Setup alerts**: Configure monitoring and alerting
5. **Secure secrets**: Use Azure Key Vault for credentials

### Testing
1. **Component tests first**: Test Neo4j, RAG, BitNet independently
2. **Integration tests**: Test complete pipeline
3. **Performance tests**: Verify 417x improvement is maintained
4. **Load tests**: Test concurrent query handling

## Documentation Map

**Getting Started:**
- [README.md](README.md) - Project overview and quick start
- [docs/README-QUICKSTART.md](docs/README-QUICKSTART.md) - Complete developer journey

**Local Development:**
- [docs/LOCAL-TESTING-GUIDE.md](docs/LOCAL-TESTING-GUIDE.md) - Comprehensive testing guide
- [neo4j-rag-demo/LOCAL_TESTING.md](neo4j-rag-demo/LOCAL_TESTING.md) - RAG-specific tests

**Deployment:**
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Basic deployment guide
- [neo4j-rag-demo/docs/AZURE_DEPLOYMENT_GUIDE.md](neo4j-rag-demo/docs/AZURE_DEPLOYMENT_GUIDE.md) - Detailed Azure guide
- [neo4j-rag-demo/docs/AZURE_ARCHITECTURE.md](neo4j-rag-demo/docs/AZURE_ARCHITECTURE.md) - Architecture documentation

**BitNet Integration:**
- [docs/BITNET-SUCCESS.md](docs/BITNET-SUCCESS.md) - BitNet build success story
- [neo4j-rag-demo/azure_deploy/BITNET_DEPLOYMENT_GUIDE.md](neo4j-rag-demo/azure_deploy/BITNET_DEPLOYMENT_GUIDE.md) - BitNet deployment

**Project Status:**
- [docs/IMPLEMENTATION-STATUS.md](docs/IMPLEMENTATION-STATUS.md) - Current implementation status
- [docs/NEXT-STEPS.md](docs/NEXT-STEPS.md) - Future improvements and roadmap

**Additional Resources:**
- [neo4j-rag-demo/docs/USER_GUIDE.md](neo4j-rag-demo/docs/USER_GUIDE.md) - User guide
- [neo4j-rag-demo/docs/LLM_SETUP.md](neo4j-rag-demo/docs/LLM_SETUP.md) - LLM configuration
- [neo4j-rag-demo/CONTRIBUTING.md](neo4j-rag-demo/CONTRIBUTING.md) - Contribution guidelines
- [neo4j-rag-demo/SECURITY.md](neo4j-rag-demo/SECURITY.md) - Security policies

## Common Tasks Reference

### Adding New Documents
```bash
# Via script
cd neo4j-rag-demo
python scripts/upload_pdfs_to_neo4j.py /path/to/pdfs/

# Via API
curl -X POST http://localhost:8000/add-documents \
  -H 'Content-Type: application/json' \
  -d '{"documents": [{"id": "doc1", "content": "..."}]}'
```

### Querying the System
```bash
# Simple query
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question": "What is Neo4j?", "max_results": 3}'

# With LLM generation
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"question": "How does Neo4j work?", "use_llm": true}'
```

### Managing Docker Services
```bash
# Start all services
docker-compose -f scripts/docker-compose.optimized.yml up -d

# View logs
docker-compose -f scripts/docker-compose.optimized.yml logs -f

# Stop services
docker-compose -f scripts/docker-compose.optimized.yml down

# Restart specific service
docker-compose -f scripts/docker-compose.optimized.yml restart rag-service
```

### Azure Management
```bash
# View deployments
az containerapp list --resource-group rg-neo4j-rag-bitnet --output table

# View logs
az containerapp logs show --name neo4j-rag-agent \
  --resource-group rg-neo4j-rag-bitnet --follow

# Scale service
az containerapp update --name neo4j-rag-agent \
  --resource-group rg-neo4j-rag-bitnet \
  --min-replicas 2 --max-replicas 20
```

## Troubleshooting Guide

### Service Won't Start
1. Check Docker is running: `docker ps`
2. Check port conflicts: `lsof -i :7474 -i :7687 -i :8000 -i :8001`
3. View logs: `docker-compose logs <service-name>`
4. Restart: `docker-compose restart <service-name>`

### Slow Performance
1. Check cache hit rate: `curl http://localhost:8000/stats`
2. Monitor memory: `docker stats`
3. Review query patterns: Enable debug logging
4. Optimize chunk size: Adjust in `neo4j_rag.py`

### Build Failures
1. **BitNet build**: Check disk space (needs 10GB+)
2. **Docker**: Increase Docker memory to 8GB+
3. **Azure**: Check ACR permissions and quotas
4. **Dependencies**: Update requirements.txt

## Project Status

**Completed Features:**
- ✅ 417x performance improvement
- ✅ Real BitNet.cpp integration
- ✅ Azure deployment automation
- ✅ Comprehensive documentation
- ✅ Complete test suite
- ✅ Production-ready containerization

**In Progress:**
- 🟡 Enhanced monitoring and observability
- 🟡 Additional LLM model support
- 🟡 Advanced caching strategies

**Future Enhancements:**
- [ ] Multi-modal embeddings
- [ ] Streaming response support
- [ ] LangChain integration examples
- [ ] Enhanced security features
- [ ] GraphRAG advanced features

## Support and Resources

**Issues**: https://github.com/ma3u/neo4j-agentframework/issues
**Documentation**: https://github.com/ma3u/neo4j-agentframework/wiki
**Discussions**: https://github.com/ma3u/neo4j-agentframework/discussions

---

**Made with ❤️ for efficient AI systems**
**Generated with Claude Code** (https://claude.com/claude-code)
