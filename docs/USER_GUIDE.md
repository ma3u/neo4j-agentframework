# Neo4j BitNet RAG - User Guide

Complete guide for using the ultra-efficient BitNet b1.58 RAG system with Neo4j.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Azure Deployment](#azure-deployment)
- [Using the API](#using-the-api)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites
- Docker Desktop installed
- Azure CLI (for Azure deployment)
- 4GB+ RAM available

### Local Setup (5 Minutes)

```bash
# 1. Check if .env exists, create if needed
if [ ! -f .env ]; then
    cp .env.example .env
fi

# 2. Start the system
./start-bitnet-local.sh

# 3. Test the system
curl http://localhost:8000/health
```

## Local Development

### Starting the System

```bash
# Build and start all services
docker-compose build
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bitnet-rag
```

### Stopping the System

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

### Configuration

Edit `.env` file to configure:

```bash
# Neo4j Connection
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Azure OpenAI (for embeddings)
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key

# BitNet (optional - uses fallback if not set)
BITNET_ENDPOINT=https://your-bitnet.azureml.azure.com/
BITNET_API_KEY=your-bitnet-api-key
```

## Azure Deployment

### Quick Deploy

```bash
cd azure
chmod +x deploy_bitnet.sh
./deploy_bitnet.sh
```

See [Azure Deployment Guide](AZURE_DEPLOYMENT_GUIDE.md) for detailed instructions.

## Using the API

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "bitnet_mode": "enabled",
  "neo4j_connected": true,
  "memory_usage_gb": 0.4
}
```

### Query Endpoint

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is BitNet?",
    "max_results": 3,
    "include_sources": true
  }'
```

**Response:**
```json
{
  "answer": "BitNet is an ultra-efficient 1.58-bit ternary quantized language model...",
  "sources": [
    {
      "text": "BitNet b1.58 achieves 87% memory reduction...",
      "score": 0.92
    }
  ],
  "performance": {
    "response_time_ms": 29,
    "memory_usage_gb": 0.4,
    "cost_estimate": "$0.0001"
  }
}
```

### System Stats

```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "neo4j": {
    "documents": 32,
    "chunks": 29129,
    "avg_chunks_per_doc": 910
  },
  "performance": {
    "avg_response_time_ms": 29,
    "cache_hit_rate": 0.85
  }
}
```

### Model Information

```bash
curl http://localhost:8000/model-info
```

**Response:**
```json
{
  "model": "BitNet b1.58 2B4T",
  "efficiency": {
    "memory_usage_gb": 0.4,
    "memory_reduction": "87%",
    "inference_latency_ms": 29,
    "speed_improvement": "77%",
    "cost_savings": "85-90%"
  }
}
```

## Advanced Usage

### Loading Custom Documents

```python
from src.docling_loader import DoclingDocumentLoader
from src.neo4j_rag import Neo4jRAG

# Initialize
rag = Neo4jRAG()
loader = DoclingDocumentLoader(neo4j_rag=rag)

# Load PDF
loader.load_document("document.pdf", metadata={"category": "research"})

# Load directory
loader.load_directory("documents/", recursive=True)

loader.close()
rag.close()
```

### Custom Search Queries

```python
from src.bitnet_azure_rag import BitNetAzureRAG

# Initialize BitNet RAG
rag = BitNetAzureRAG(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

# Vector search
results = rag.vector_search("machine learning", k=5)

# Hybrid search
results = rag.hybrid_search("graph database", k=5, alpha=0.7)

rag.close()
```

### Monitoring

```bash
# View container logs
docker-compose logs -f bitnet-rag

# Check Neo4j Browser
open http://localhost:7474

# Monitor resource usage
docker stats
```

## Troubleshooting

### Container Won't Start

```bash
# Check Docker
docker ps -a

# View logs
docker-compose logs bitnet-rag

# Restart services
docker-compose restart
```

### Connection Errors

```bash
# Test Neo4j connection
docker exec neo4j-rag cypher-shell -u neo4j -p password "RETURN 1;"

# Test BitNet service
curl http://localhost:8000/health
```

### Memory Issues

```bash
# Check memory usage
docker stats

# Increase Docker memory (Docker Desktop > Settings > Resources)
# Recommended: 8GB+ for optimal performance
```

### API Errors

```bash
# Check API logs
docker-compose logs -f bitnet-rag

# Test with verbose output
curl -v http://localhost:8000/health
```

## Performance Optimization

### Docker Optimization

```yaml
# docker-compose.yml
services:
  bitnet-rag:
    deploy:
      resources:
        limits:
          memory: 512M   # Ultra-low footprint
          cpus: '0.5'    # Minimal CPU
```

### Neo4j Optimization

```bash
# Set Neo4j memory
docker run -e NEO4J_dbms_memory_heap_max__size=4G \
           -e NEO4J_dbms_memory_pagecache_size=2G \
           neo4j:latest
```

### Application Tuning

```python
# .env configuration
MAX_WORKERS=1          # Single worker for efficiency
CACHE_SIZE=50          # Minimal cache
MEMORY_LIMIT_GB=0.5    # BitNet's ultra-low footprint
```

## Support Resources

- [Azure Architecture](AZURE_ARCHITECTURE.md) - System architecture
- [Azure Deployment Guide](AZURE_DEPLOYMENT_GUIDE.md) - Deployment instructions
- [CLAUDE.md](../CLAUDE.md) - Developer guide
- [GitHub Issues](https://github.com/ma3u/neo4j-agentframework/issues) - Report bugs

---

**Need help?** Check the [Troubleshooting](#troubleshooting) section or open an issue on GitHub.
