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
- [x] Create Docker Compose setup
- [x] Add API server with FastAPI

## Azure Deployment

### Overview
Production-ready deployment to Azure with Microsoft Agent Framework integration, preserving 417x performance improvements.

### Prerequisites
- Azure CLI installed and authenticated (`az login`)
- Docker Desktop running
- Active Azure subscription

### Automated Deployment
```bash
cd azure
chmod +x deploy.sh
./deploy.sh
```

### Manual Step-by-Step Deployment

**1. Set Environment Variables**
```bash
export RESOURCE_GROUP="rg-neo4j-rag-bitnet"
export LOCATION="swedencentral"  # or your preferred region
export REGISTRY_NAME="crneo4jrag$(openssl rand -hex 4)"
export APP_NAME="neo4j-rag-bitnet"
```

**2. Create Resource Group**
```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

**3. Create Container Registry**
```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic \
  --admin-enabled true \
  --location $LOCATION
```

**4. Build and Push Docker Image**
```bash
# Build in Azure (recommended - faster and more reliable)
az acr build \
  --registry $REGISTRY_NAME \
  --image neo4j-rag-agent:v1.0 \
  --file azure/Dockerfile.agent \
  .
```

**5. Create Container Apps Environment**
```bash
az containerapp env create \
  --name neo4j-rag-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

**6. Deploy Neo4j Database Container**
```bash
az containerapp create \
  --name neo4j-database \
  --resource-group $RESOURCE_GROUP \
  --environment neo4j-rag-env \
  --image neo4j:5.11 \
  --target-port 7687 \
  --ingress internal \
  --env-vars \
    NEO4J_AUTH=neo4j/YourSecurePassword123! \
    NEO4J_dbms_memory_heap_max__size=4G \
    NEO4J_dbms_memory_pagecache_size=2G \
  --cpu 4.0 \
  --memory 8Gi \
  --min-replicas 1 \
  --max-replicas 1
```

**7. Deploy RAG Agent Container**
```bash
REGISTRY_URL=$(az acr show --name $REGISTRY_NAME --query loginServer -o tsv)

az containerapp create \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --environment neo4j-rag-env \
  --image $REGISTRY_URL/neo4j-rag-agent:v1.0 \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    NEO4J_URI=bolt://neo4j-database:7687 \
    NEO4J_USER=neo4j \
    NEO4J_PASSWORD=YourSecurePassword123! \
  --cpu 2.0 \
  --memory 4Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --registry-server $REGISTRY_URL
```

**8. Get Application URL**
```bash
APP_URL=$(az containerapp show \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Application URL: https://$APP_URL"
```

### What Gets Deployed
- **Container Registry**: crneo4jrag*.azurecr.io
- **Container Apps Environment**: With Log Analytics workspace
- **Neo4j Database**: 4 CPU, 8GB RAM, always-on (1 replica)
- **RAG Agent Service**: 2 CPU, 4GB RAM, auto-scale (0-10 replicas)
- **Networking**: Internal (Neo4j) + External HTTPS (Agent)

### Deployment Files
- `azure/deploy.sh` - Automated deployment script
- `azure/Dockerfile.agent` - Production container image
- `azure/app.py` - FastAPI application
- `azure/agent_service.py` - Agent Framework integration
- `docs/AZURE_DEPLOYMENT_GUIDE.md` - Detailed guide
- `docs/AZURE_ARCHITECTURE.md` - Architecture docs

### Performance on Azure
- Query Response: ~110ms (417x faster preserved)
- Cache Hit: <1ms (99.9%+ improvement)
- Auto-scaling: 0-10 instances based on HTTP load
- Concurrent Requests: High throughput with pooling

### Cost Breakdown
- Container Apps Environment: ~$50/month
- Container Registry (Basic): ~$5/month
- Neo4j Container (4 CPU, 8GB, always-on): ~$200/month
- Agent Container (2 CPU, 4GB, auto-scale): ~$100-500/month
- **Estimated Total**: $355-755/month

### Testing Deployment
```bash
# Health check
curl https://$APP_URL/health

# Test query
curl -X POST https://$APP_URL/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Neo4j?"}'

# View stats
curl https://$APP_URL/stats
```

### Management Commands
```bash
# View all container apps
az containerapp list --resource-group $RESOURCE_GROUP --output table

# View logs (follow)
az containerapp logs show \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --follow

# Scale manually
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 20

# Restart container app
az containerapp revision restart \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP

# Delete deployment
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

### Monitoring
```bash
# View metrics
az monitor metrics list \
  --resource $(az containerapp show \
    --name neo4j-rag-agent \
    --resource-group $RESOURCE_GROUP \
    --query id -o tsv) \
  --metric-names Requests,ResponseTime

# View Log Analytics
az monitor log-analytics workspace show \
  --resource-group $RESOURCE_GROUP \
  --workspace-name workspace-rgneo4jragbitnet*
```

### Post-Deployment Tasks
1. **Load Production Data**: Use upload scripts or API
2. **Configure Backups**: Set up Neo4j backup strategy
3. **Set Up CI/CD**: GitHub Actions or Azure DevOps
4. **Configure Alerts**: Set up monitoring alerts
5. **Security Review**: Implement Key Vault for secrets

### Troubleshooting
```bash
# Check container app status
az containerapp show \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --query properties.runningStatus

# View recent logs
az containerapp logs show \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --tail 100

# Check Neo4j connectivity
az containerapp exec \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --command "/bin/sh"
```

### Complete Documentation
- 📖 [Detailed Deployment Guide](docs/AZURE_DEPLOYMENT_GUIDE.md)
- 🏗️ [Architecture Overview](docs/AZURE_ARCHITECTURE.md)
- 📊 [Integration Summary](AZURE_INTEGRATION_SUMMARY.md)