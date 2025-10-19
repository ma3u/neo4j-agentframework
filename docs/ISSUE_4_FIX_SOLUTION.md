# Issue #4: Azure AI Foundry Connection - Fix Solution

**Date**: 2025-10-18
**Status**: Root cause identified, fix plan created
**Container App**: `neo4j-rag-agent` (yellowtree-8fdce811.swedencentral.azurecontainerapps.io)

---

## 🔍 Investigation Results

### Current State

**Container App Status**:
- ✅ **Running**: neo4j-rag-agent is active
- ✅ **Healthy**: Health endpoint responds
- ❌ **Mock Mode**: Still using `mode: mock_data`
- ❌ **No Real Data**: Not connected to Aura `6b870b04`

**Endpoints Found**:
- Health: `https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/health` ✅
- Stats: `/stats` ❌ (404 Not Found)
- Chat: `/chat` ❌ (Not working)

### Root Cause

The deployed Container App is using an **old/mock image** that doesn't:
1. Connect to real Neo4j Aura
2. Use the Agent Framework code from `azure_deploy/app.py`
3. Implement the real RAG endpoints

**Why environment variable update didn't work**:
- The deployed image has hardcoded mock mode
- Needs to be rebuilt with latest code
- Needs to use the FastAPI app from `azure_deploy/app.py`

---

## ✅ Complete Fix Solution

### Step 1: Build Updated RAG Service Image

**Create Dockerfile** for the real service:

```dockerfile
# File: neo4j-rag-demo/azure_deploy/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ../src ./src
COPY azure_deploy/app.py .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Build and Push Image

```bash
# Build image
cd neo4j-rag-demo
docker build -f azure_deploy/Dockerfile -t ghcr.io/ma3u/ms-agentf-neo4j/rag-agent:v2.0-aura .

# Push to GitHub Container Registry
docker push ghcr.io/ma3u/ms-agentf-neo4j/rag-agent:v2.0-aura
```

### Step 3: Update Container App with New Image

```bash
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group rg-neo4j-rag-bitnet \
  --image ghcr.io/ma3u/ms-agentf-neo4j/rag-agent:v2.0-aura \
  --set-env-vars \
    "NEO4J_URI=neo4j+s://6b870b04.databases.neo4j.io" \
    "NEO4J_USERNAME=neo4j" \
    "NEO4J_PASSWORD=<from-keyvault>" \
    "MODE=production"
```

**Security Note**: Use Key Vault secrets instead of direct env vars for production!

### Step 4: Configure Azure AI Foundry Functions

Once the service is deployed with real data, configure your Azure AI Foundry Assistant functions to call these endpoints:

**Function 1: search_knowledge_base**
```
POST https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/chat
Body: {"message": "{query}"}
Returns: {response, sources, performance}
```

**Function 2: get_statistics**
```
GET https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/stats
Returns: {neo4j_stats, performance}
```

**Function 3: add_document**
```
POST https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/documents
Body: {"content": "...", "metadata": {...}}
```

---

## 🚀 Quick Fix (For NODES 2025)

If time is short before your presentation, here's the fastest path:

### Option A: Deploy Simple RAG API (Recommended)

Use the existing `neo4j-rag-demo/app_local.py` as base:

```bash
# 1. Create simple FastAPI wrapper
cat > neo4j-rag-demo/simple_api.py << 'EOF'
from fastapi import FastAPI
from pydantic import BaseModel
from src.neo4j_rag import Neo4jRAG
import os

app = FastAPI()
rag = Neo4jRAG(
    uri=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

class QueryRequest(BaseModel):
    question: str
    k: int = 5

@app.post("/query")
async def query(req: QueryRequest):
    results = rag.vector_search(req.question, k=req.k)
    return {"results": results}

@app.get("/health")
async def health():
    stats = rag.get_stats()
    return {"status": "healthy", "stats": stats}

@app.get("/stats")
async def stats():
    return rag.get_stats()
EOF

# 2. Build and deploy
docker build -t rag-simple:latest .
docker tag rag-simple:latest ghcr.io/ma3u/ms-agentf-neo4j/rag-simple:v2.0
docker push ghcr.io/ma3u/ms-agentf-neo4j/rag-simple:v2.0

# 3. Update Container App
az containerapp update \
  --name neo4j-rag-agent \
  --image ghcr.io/ma3u/ms-agentf-neo4j/rag-simple:v2.0
```

### Option B: Use Existing RAG Service Image

You already have `ghcr.io/ma3u/ms-agentf-neo4j/rag-service:latest`:

```bash
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group rg-neo4j-rag-bitnet \
  --image ghcr.io/ma3u/ms-agentf-neo4j/rag-service:latest \
  --set-env-vars \
    "NEO4J_URI=neo4j+s://6b870b04.databases.neo4j.io" \
    "NEO4J_USERNAME=neo4j" \
    "NEO4J_PASSWORD=<password>"
```

---

## 📝 Azure AI Foundry Configuration Guide

### How to Update Functions in Azure AI Foundry

**1. Go to**: https://ai.azure.com
**2. Navigate to**: Your project → Assistants → `asst_LHQBXYvRhnbFo7KQ7IRbVXRR`
**3. Edit Functions**:

**Replace current function definitions with OpenAPI spec**:

```yaml
openapi: 3.0.0
info:
  title: Neo4j RAG API
  version: 2.0.0
servers:
  - url: https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io
paths:
  /query:
    post:
      operationId: search_knowledge_base
      summary: Search the Neo4j knowledge graph
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                question:
                  type: string
                  description: The question to search for
                k:
                  type: integer
                  default: 5
                  description: Number of results
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                  query_time_ms:
                    type: number

  /stats:
    get:
      operationId: get_statistics
      summary: Get system statistics
      responses:
        '200':
          description: System statistics
```

**4. Test in Playground**:
- Ask: "What is Neo4j?"
- Should now call `search_knowledge_base` function
- Function calls Container App endpoint
- Returns results from 30K chunks

---

## ⚠️ Security Note

**Current Fix Uses Plain Text Password** - This is temporary for testing!

**Proper Production Solution**:

Use Azure Managed Identity + Key Vault:

```bash
# 1. Grant Container App access to Key Vault
az containerapp identity assign \
  --name neo4j-rag-agent \
  --resource-group rg-neo4j-rag-bitnet \
  --system-assigned

# 2. Get the identity
IDENTITY=$(az containerapp show \
  --name neo4j-rag-agent \
  --resource-group rg-neo4j-rag-bitnet \
  --query identity.principalId -o tsv)

# 3. Grant Key Vault access
az keyvault set-policy \
  --name kv-neo4j-rag-7048 \
  --object-id $IDENTITY \
  --secret-permissions get list

# 4. Update Container App to use Key Vault
az containerapp update \
  --name neo4j-rag-agent \
  --set-env-vars \
    "AZURE_KEY_VAULT_NAME=kv-neo4j-rag-7048"
```

Then the app uses `AuraConfig` class to retrieve secrets automatically.

---

## ✅ Success Criteria

After fix is applied:

- [ ] Container App shows `mode: production` (not mock_data)
- [ ] `/health` endpoint shows connection to Aura
- [ ] `/stats` returns real data (12 documents, 30,006 chunks)
- [ ] `/chat` or `/query` returns answers from knowledge base
- [ ] Azure AI Foundry Assistant successfully calls functions
- [ ] Query "What is Neo4j?" returns relevant answer with sources

---

## 📊 Next Steps (Priority Order)

### Immediate (This Weekend - Before NODES):

1. **Rebuild Service** with real RAG code
   - Use `azure_deploy/app.py` or simple FastAPI wrapper
   - Connect to Aura `6b870b04`
   - Test locally first: `uvicorn app:app --reload`

2. **Deploy Updated Image**
   - Build Docker image
   - Push to GHCR
   - Update Container App

3. **Test Endpoints**
   - Verify `/health` shows production mode
   - Test `/query` or `/chat` with "What is Neo4j?"
   - Confirm returns real data from 30K chunks

4. **Configure Azure AI Foundry**
   - Add OpenAPI spec or update function URLs
   - Test in playground
   - Verify Assistant can now answer questions

### Post-Fix (For Production):

5. **Security Hardening**
   - Implement Managed Identity
   - Use Key Vault for all secrets
   - Remove plain text passwords

6. **Documentation**
   - Update Issue #4 with solution
   - Document deployment process
   - Add troubleshooting guide

---

## 🎯 Recommendation for NODES 2025

Given timing constraints (Nov 6 is approaching):

**Plan A** - If you have 1-2 days:
- Fix the Container App deployment
- Get Azure AI Foundry working
- Demo live during presentation

**Plan B** - If time is tight:
- Keep local Docker demo (works perfectly)
- Show Aura database directly in Neo4j Browser
- Mention Azure AI Foundry as "in progress" (shows in screenshot)
- Focus on: Local deployment, Aura knowledge base, Cypher queries

Both are valid! Plan B is safer for live demo.

---

## 📚 Resources Created

1. **Investigation Document**: `docs/ISSUE_4_INVESTIGATION_CONCEPT.md`
   - Option 1 vs Option 2 comparison
   - MCP servers overview
   - Cost analysis

2. **This Fix Solution**: `docs/ISSUE_4_FIX_SOLUTION.md`
   - Root cause analysis
   - Step-by-step fix
   - Security considerations
   - Success criteria

3. **GitHub Issue Comment**: Posted findings to Issue #4

---

**Status**: Investigation complete, fix plan documented
**Next**: Choose Plan A (fix before NODES) or Plan B (demo locally)
**Time Required**: Plan A = 1-2 days, Plan B = 0 days (already works)

**Recommendation**: Given it's October 18 and NODES is November 6, you have time for Plan A!
