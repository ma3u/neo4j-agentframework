# Cost-Optimized Azure Deployment

## 💰 Current vs Optimized Costs

### Original Estimate (Over-provisioned)
- **Agent Container**: 2 CPU, 4GB RAM, auto-scaling 0-10 instances = **$100-500/month**
- **Neo4j Container**: 4 CPU, 8GB RAM = **$200/month**
- **Total Infrastructure**: **$300-700/month**

### Cost-Optimized Configuration
- **Agent Container**: 0.5 CPU, 1GB RAM, auto-scaling 0-3 instances = **$25-75/month**
- **Neo4j Container**: 1 CPU, 2GB RAM = **$50/month**  
- **Total Infrastructure**: **$75-125/month** (**75% cost reduction**)

## 🔧 Optimized Resource Configuration

### Why the Original Was Expensive
1. **Over-provisioned CPU/Memory**: Configured for enterprise workloads
2. **High scaling limits**: 0-10 instances for demo use case
3. **Production-grade Neo4j**: 8GB RAM for large datasets

### Cost-Optimized Settings
```bash
# Optimized Agent Container (75% cost reduction)
az containerapp create \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --environment "${PROJECT_NAME}-env" \
  --image "${ACR_LOGIN_SERVER}/neo4j-rag-agent:v1.0" \
  --target-port 8000 \
  --ingress external \
  --cpu 0.5 \              # Reduced from 2.0
  --memory 1Gi \            # Reduced from 4Gi  
  --min-replicas 0 \        # Scale to zero when not used
  --max-replicas 3 \        # Reduced from 10
  --env-vars \
    NEO4J_URI=bolt://neo4j-database:7687 \
    AZURE_AI_PROJECT_ENDPOINT="$AZURE_AI_ENDPOINT" \
    AZURE_AI_MODEL_DEPLOYMENT_NAME=text-embedding-ada-002

# Optimized Neo4j Container (75% cost reduction)  
az containerapp create \
  --name neo4j-database \
  --resource-group $RESOURCE_GROUP \
  --environment "${PROJECT_NAME}-env" \
  --image neo4j:5.11 \
  --target-port 7687 \
  --ingress internal \
  --cpu 1.0 \               # Reduced from 4.0
  --memory 2Gi \            # Reduced from 8Gi
  --min-replicas 1 \
  --max-replicas 1 \
  --env-vars \
    NEO4J_AUTH=neo4j/password \
    NEO4J_dbms_memory_heap_initial__size=512m \    # Optimized for small datasets
    NEO4J_dbms_memory_heap_max__size=1G \
    NEO4J_dbms_memory_pagecache_size=512m
```

## 📊 Performance Impact Assessment

### Agent Container Optimization
- **CPU**: 0.5 vCPU is sufficient for:
  - Processing 1-2 concurrent requests
  - Vector embedding generation  
  - Agent Framework operations
- **Memory**: 1GB handles:
  - FastAPI application (~200MB)
  - Neo4j driver (~50MB)
  - Agent Framework (~300MB)
  - Query caching (~200MB)
  - Buffer for spikes (~250MB)

### Neo4j Container Optimization  
- **CPU**: 1 vCPU sufficient for:
  - Small to medium datasets (<100k chunks)
  - Development and testing workloads
- **Memory**: 2GB allocation:
  - Heap: 1GB (adequate for <50k chunks)
  - Page cache: 512MB (good for frequent queries)
  - System overhead: 512MB

## 🔄 Right-Sizing Strategy

### Start Small, Scale Up
```bash
# Start with minimal resources
INITIAL_AGENT_CPU="0.25"      # $12-25/month
INITIAL_AGENT_MEMORY="0.5Gi"  
INITIAL_NEO4J_CPU="0.5"       # $25/month
INITIAL_NEO4J_MEMORY="1Gi"

# Scale based on actual usage
# Monitor for 1-2 weeks, then adjust
```

### Monitoring Thresholds
```bash
# Set up alerts to know when to scale up
az monitor metrics alert create \
  --name "Agent CPU High" \
  --condition "avg Percentage CPU > 70" \
  --description "Scale up agent container" \
  --evaluation-frequency 5m
```

## 💡 Additional Cost Optimizations

### 1. Use Azure OpenAI Embeddings (Instead of Local Model)
**Current**: SentenceTransformer runs locally (uses CPU/memory)
**Optimized**: Azure OpenAI text-embedding-ada-002 (external API)
- **Cost**: ~$0.10 per 1M tokens (very cheap)
- **Benefits**: No local compute needed, faster, better quality

### 2. Consumption-Based Scaling  
```bash
# Scale to zero when not in use
--min-replicas 0

# Conservative scaling rules
--scale-rule-name cpu-utilization \
--scale-rule-type cpu \
--scale-rule-metadata targetAverageUtilization=60
```

### 3. Development vs Production Profiles

#### Development Profile ($30-50/month)
```yaml
agent:
  cpu: 0.25
  memory: 0.5Gi
  replicas: 0-1

neo4j:
  cpu: 0.5  
  memory: 1Gi
```

#### Production Profile ($75-150/month)
```yaml
agent:
  cpu: 0.5
  memory: 1Gi  
  replicas: 0-5

neo4j:
  cpu: 1.0
  memory: 2Gi
```

## 🎯 Recommended Deployment Strategy

### Phase 1: Minimal Deployment (Test costs)
```bash
export DEPLOYMENT_SIZE="minimal"
export AGENT_CPU="0.25"
export AGENT_MEMORY="0.5Gi"
export NEO4J_CPU="0.5" 
export NEO4J_MEMORY="1Gi"
```

### Phase 2: Monitor and Scale
- Deploy minimal configuration
- Load test with your expected usage
- Monitor CPU/memory utilization
- Scale up only if needed

### Phase 3: Cost Optimization
- Implement Azure OpenAI embeddings
- Use consumption-based scaling
- Regular cost reviews

## 📈 Expected Results

### Cost Comparison (Monthly)
| Component | Original | Optimized | Savings |
|-----------|----------|-----------|---------|
| Agent Container | $100-500 | **$25-75** | **75-85%** |
| Neo4j Container | $200 | **$50** | **75%** |
| **Total** | **$300-700** | **$75-125** | **75-80%** |

### Performance Expectations
- **Response Time**: 200-500ms (vs 110ms optimized local)
- **Throughput**: 10-20 requests/minute
- **Availability**: 99.9% with auto-scaling
- **417x Optimization**: Maintained for vector operations

This configuration is perfect for:
- Development and testing
- Small to medium production workloads
- Cost-conscious deployments
- Proof of concept demonstrations