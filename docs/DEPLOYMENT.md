# Deployment Guide

## 🔗 Quick Navigation
- [← Back to Main README](../README.md) | [Architecture](ARCHITECTURE.md) | [API Reference](API-REFERENCE.md)

Deploy the Neo4j Hybrid RAG System locally or on Azure.

## 🏠 Local Deployment

### Option 1: Pre-built Containers (Recommended)
**Best for**: Quick evaluation, development, demos

```bash
# 1. Clone repository
git clone https://github.com/ma3u/neo4j-agentframework.git
cd neo4j-agentframework

# 2. Start services (auto-downloads images)
docker compose -f scripts/docker-compose.ghcr.yml up -d

# 3. Access services
# Neo4j Browser: http://localhost:7474 (neo4j/password)
# RAG API: http://localhost:8000/docs  
# BitNet LLM: http://localhost:8001/health

# 4. Test the system
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Neo4j?","k":5}'
```

### Option 2: Minimal BitNet (334MB)
**Best for**: Resource-constrained environments, edge deployment

```bash
# 1. Pull minimal BitNet image  
docker pull ghcr.io/ma3u/ms-agentf-neo4j/bitnet-minimal:latest

# 2. Create model storage directory
mkdir models

# 3. Run with external model storage
docker run -d -p 8001:8001 --name bitnet \
  -v $(pwd)/models:/app/models \
  ghcr.io/ma3u/ms-agentf-neo4j/bitnet-minimal:latest

# 4. Monitor model download (first run)
docker logs -f bitnet
```

### Option 3: Development Setup
**Best for**: Code development, customization

```bash
# 1. Start Neo4j database
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.15-community

# 2. Setup Python environment
cd neo4j-rag-demo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Run RAG service
python app_local.py
```

## ☁️ Azure Production Deployment

### Prerequisites
- Azure subscription
- Azure CLI installed and logged in
- 30 minutes deployment time

### Automated Deployment
```bash
# 1. Set environment variables
export RESOURCE_GROUP="rg-neo4j-rag"
export LOCATION="eastus"  
export SUBSCRIPTION_ID="your-subscription-id"

# 2. Run deployment script
./scripts/azure-deploy-enterprise.sh

# 3. Configure AI Assistant (optional)
python scripts/configure-azure-assistant.py
```

### Manual Azure Setup

#### Step 1: Container Apps Environment
```bash
# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create container apps environment
az containerapp env create \
  --name neo4j-rag-env \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

#### Step 2: Neo4j Aura Database
1. Go to [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Create new AuraDB instance (2GB RAM recommended)
3. Save connection details (URI, username, password)

#### Step 3: Deploy RAG Service
```bash
az containerapp create \
  --name rag-service \
  --resource-group $RESOURCE_GROUP \
  --environment neo4j-rag-env \
  --image ghcr.io/ma3u/ms-agentf-neo4j/rag-service:latest \
  --cpu 1.0 --memory 2.0Gi \
  --min-replicas 1 --max-replicas 3 \
  --env-vars \
    NEO4J_URI="bolt://your-aura-instance" \
    NEO4J_USER="neo4j" \
    NEO4J_PASSWORD="your-password" \
  --ingress external --target-port 8000
```

#### Step 4: Azure OpenAI Integration
```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name "neo4j-rag-openai" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --kind OpenAI \
  --sku S0

# Deploy model (gpt-4o-mini recommended for cost efficiency)
az cognitiveservices account deployment create \
  --name "neo4j-rag-openai" \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18"
```

## 🔧 Configuration Options

### Environment Variables

**Local Development**:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j  
NEO4J_PASSWORD=password
BITNET_LLM_URL=http://localhost:8001
```

**Azure Production**:
```bash
NEO4J_URI=bolt://your-aura-instance.databases.neo4j.io:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
```

### Resource Requirements

| Component | Local | Azure |
|-----------|-------|-------|
| **Neo4j** | 1GB RAM | AuraDB (2-8GB) |
| **RAG Service** | 1GB RAM | Container Apps (2GB) |
| **BitNet LLM** | 1.5GB RAM | Optional (use Azure OpenAI) |
| **Total** | ~4GB RAM | $200-350/month |

## 🧪 Verification

### Health Checks
```bash  
# Check all services
curl http://localhost:8000/health  # RAG service
curl http://localhost:8001/health  # BitNet LLM  
curl http://localhost:7474/db/data/ # Neo4j (requires auth)

# Expected response
{
  "status": "healthy",
  "neo4j_connected": true,
  "model": "SentenceTransformer (all-MiniLM-L6-v2)"
}
```

### Test Document Upload and Query
```bash
# 1. Add a document
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Neo4j is a graph database management system that stores data as nodes and relationships.",
    "metadata": {"source": "test", "type": "definition"}
  }'

# 2. Query the knowledge base
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \  
  -d '{"question": "What is Neo4j?", "k": 3}'

# Expected: Intelligent response based on stored document
```

## 🐳 Container Image Options

Choose the right container for your use case:

| Use Case | Image | Command |
|----------|-------|---------|
| **Quick Demo** | Pre-built stack | `docker compose -f scripts/docker-compose.ghcr.yml up` |
| **Resource-Constrained** | BitNet Minimal | `docker run ghcr.io/ma3u/ms-agentf-neo4j/bitnet-minimal` |
| **Production** | Optimized | `docker run ghcr.io/ma3u/ms-agentf-neo4j/bitnet-optimized` |
| **Development** | Build from source | `docker compose up --build` |

## 🚨 Troubleshooting

**Common Issues**:
- **Port conflicts**: Ensure ports 7474, 7687, 8000, 8001 are available
- **Memory errors**: Allocate at least 4GB RAM to Docker
- **Model download fails**: Check internet connection and disk space (1.1GB needed)
- **Neo4j connection**: Verify credentials and wait for database startup (30-60s)

**Get Help**:
- [GitHub Issues](https://github.com/ma3u/neo4j-agentframework/issues) for bugs
- [Troubleshooting Guide](docs/reference/TROUBLESHOOT.md) for common problems

---

**Next Steps**: See [docs/API-REFERENCE.md](docs/API-REFERENCE.md) for API usage examples.