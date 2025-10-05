# Azure Resource Naming and Tagging Guide

**Clear naming conventions and tags to prevent confusion**

---

## ⚠️ Common Naming Confusion

### Issue: Misleading Resource Name

**Resource**: `neo4j-rag-bitnet-ai`
**Actual Content**: Azure OpenAI with GPT-4o-mini
**Confusing Because**: Name includes "bitnet" but it's NOT BitNet!

**Clarification**:
- ❌ **NOT BitNet.cpp** (1.58-bit quantized LLM)
- ✅ **IS Azure OpenAI** (GPT-4o-mini deployment)
- **Purpose**: Fallback/alternative LLM to BitNet
- **Role**: Azure AI Assistant backend

---

## 🏷️ Resource Tags (Applied)

Tags have been added to clarify the resource:

| Tag | Value | Purpose |
|-----|-------|---------|
| `component` | Azure OpenAI | What it actually is |
| `model` | GPT-4o-mini | Which model is deployed |
| `purpose` | Assistant LLM (NOT BitNet) | Clear purpose statement |
| `deployment` | gpt-4o-mini-2024-07-18 | Specific deployment version |
| `role` | Fallback/Alternative to BitNet | How it relates to BitNet |
| `note` | BitNet runs in separate container | Where BitNet actually is |

**View tags in Azure Portal**:
- Go to resource `neo4j-rag-bitnet-ai`
- Click "Tags" in left menu
- See all clarifying tags

---

## 📋 Complete Resource Inventory

### Current Resources in `rg-neo4j-rag-bitnet`

| Resource Name | Type | What It Is | Purpose | Tags |
|---------------|------|------------|---------|------|
| **neo4j-rag-bitnet-ai** | Azure OpenAI | GPT-4o-mini | Assistant LLM (fallback) | ✅ Tagged |
| **neo4j-database** | Container App | Neo4j 5.15 | Graph database | Need tags |
| **neo4j-rag-agent** | Container App | Agent Framework | Agent orchestration | Need tags |
| **crneo4jrag*** (×4) | Container Registry | Docker images | Image storage | ⚠️ Duplicates! |
| **neo4j-rag-env** | Container Apps Env | Environment | Container hosting | Need tags |
| **workspace-*** | Log Analytics | Logs & metrics | Monitoring | Need tags |

---

## 🎯 Correct Architecture

### Where Each Component Actually Runs

```
┌─────────────────────────────────────────────────┐
│  Azure OpenAI Resource                          │
│  Name: neo4j-rag-bitnet-ai                      │
│  Type: Cognitive Services / OpenAI              │
│  Model: GPT-4o-mini (NOT BitNet!)               │
│  Purpose: Azure AI Assistant backend            │
│  Role: Fallback/Alternative to BitNet           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  BitNet Container App (To Be Deployed)          │
│  Name: bitnet-llm                               │
│  Type: Container App                            │
│  Image: bitnet-llm:v1.0                         │
│  Model: BitNet.cpp 1.58-bit                     │
│  Purpose: Efficient local LLM inference         │
│  Role: Primary LLM (87% memory reduction)       │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  RAG Service Container App (To Be Deployed)     │
│  Name: rag-service                              │
│  Type: Container App                            │
│  Features: Neo4j RAG, Docling, Embeddings       │
│  Purpose: 417x faster retrieval                 │
│  Role: Primary knowledge base backend           │
└─────────────────────────────────────────────────┘
```

---

## ✅ Recommended Tagging Strategy

### Apply Tags to All Resources

**For neo4j-database:**
```bash
az containerapp update \
  --name neo4j-database \
  --resource-group rg-neo4j-rag-bitnet \
  --tags \
    "component=Neo4j Database" \
    "version=5.15" \
    "purpose=Graph database + Vector search" \
    "performance=417x improvement" \
    "role=Primary data store"
```

**For neo4j-rag-agent:**
```bash
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group rg-neo4j-rag-bitnet \
  --tags \
    "component=Agent Framework" \
    "framework=Microsoft Agent Framework" \
    "purpose=Multi-agent orchestration" \
    "role=Frontend agent service"
```

**For Container Registries** (keep only active one):
```bash
# Tag the one you're keeping
az acr update \
  --name crneo4jrag2ffa25d2 \
  --resource-group rg-neo4j-rag-bitnet \
  --tags \
    "component=Container Registry" \
    "purpose=Docker image storage" \
    "images=neo4j-rag,bitnet-llm,agent" \
    "status=active"
```

**For Container Apps Environment:**
```bash
az containerapp env update \
  --name neo4j-rag-env \
  --resource-group rg-neo4j-rag-bitnet \
  --tags \
    "component=Container Apps Environment" \
    "purpose=Host all container apps" \
    "apps=neo4j,rag,bitnet,agent,mcp"
```

---

## 📝 Resource Naming Best Practices

### What Went Wrong

**Misleading Name**: `neo4j-rag-bitnet-ai`
- Implies it's BitNet
- Actually Azure OpenAI
- Causes confusion

**Better Names**:
- `neo4j-rag-azure-openai` ✅
- `neo4j-assistant-gpt4o` ✅
- `neo4j-rag-fallback-llm` ✅

### Recommended Naming Convention

**Format**: `{project}-{component}-{descriptor}`

**Examples**:
```bash
# Azure OpenAI
neo4j-rag-azure-openai        # Clear it's Azure OpenAI
neo4j-assistant-backend       # Clear it's for Assistant

# Container Apps
neo4j-rag-database            # Neo4j database service
neo4j-rag-service             # RAG API service
neo4j-bitnet-llm              # BitNet LLM service
neo4j-agent-service           # Agent Framework service
neo4j-mcp-server              # MCP Server

# Container Registry
crneo4jragprod                # Production registry (no random suffix!)

# Storage
stneo4jragprod                # Storage for backups
```

---

## 🔧 Fixing Current Naming

### Option 1: Update Tags (Easiest)

✅ **Already done** for `neo4j-rag-bitnet-ai`

Tags now clearly state:
- `component=Azure OpenAI`
- `purpose=Assistant LLM (NOT BitNet)`
- `note=BitNet runs in separate container`

**No resource renaming needed** - tags solve the confusion!

### Option 2: Rename Resources (More Work)

**Not recommended** because:
- Resource renaming can break existing deployments
- Tags provide same clarity
- Avoids potential downtime

**If you must rename:**
```bash
# Can't rename Azure resources directly
# Must: Create new → Migrate → Delete old

# 1. Create new with better name
az cognitiveservices account create \
  --name neo4j-rag-azure-openai \
  --resource-group rg-neo4j-rag-bitnet \
  --kind OpenAI \
  --sku S0 \
  --location swedencentral

# 2. Recreate deployments
az cognitiveservices account deployment create ...

# 3. Update Container Apps to use new endpoint
# 4. Delete old resource
```

---

## 📊 Resource Hierarchy

### Logical Grouping

```
rg-neo4j-rag-bitnet (Resource Group)
├── Compute
│   ├── neo4j-rag-env (Container Apps Environment)
│   ├── neo4j-database (Container App) - Neo4j DB
│   ├── rag-service (Container App) - RAG API [TO DEPLOY]
│   ├── bitnet-llm (Container App) - BitNet LLM [TO DEPLOY]
│   ├── neo4j-rag-agent (Container App) - Agent Framework
│   └── mcp-server (Container App) - MCP [OPTIONAL]
│
├── AI Services
│   └── neo4j-rag-bitnet-ai (Azure OpenAI)
│       └── Deployment: gpt-4o-mini
│           └── Role: Assistant backend (NOT BitNet!)
│
├── Storage
│   └── crneo4jrag* (Container Registry) - Keep 1, delete 3
│
└── Monitoring
    └── workspace-* (Log Analytics)
```

---

## 🎯 Action Items

### Immediate

- [x] Tag `neo4j-rag-bitnet-ai` with clarifying labels
- [ ] Run cleanup script for duplicate registries
- [ ] Tag remaining resources (database, agent, environment)

### Short-term

- [ ] Deploy missing Container Apps (rag-service, bitnet-llm)
- [ ] Verify all resources tagged properly
- [ ] Document actual vs expected resources

### Long-term

- [ ] Consider renaming for new deployments
- [ ] Implement proper naming convention
- [ ] Add tags to deployment scripts

---

## 📚 Related Documentation

- [**💰 Azure Resources Guide**](AZURE_RESOURCES.md) - Resource management
- [**🏗️ Azure Architecture**](AZURE_ARCHITECTURE.md) - Architecture overview
- [**☁️ Deployment Guide**](AZURE_DEPLOYMENT_GUIDE.md) - Deployment steps

---

**Key Takeaway**: `neo4j-rag-bitnet-ai` = Azure OpenAI (GPT-4o-mini), NOT BitNet!

BitNet runs in separate Container App (to be deployed as `bitnet-llm`).

Tags now make this crystal clear in Azure Portal. ✅
