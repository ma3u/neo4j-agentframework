# Azure Resources Guide

**Understanding and managing Azure resources for Neo4j RAG + BitNet deployment**

---

## 📑 Table of Contents

- [Expected Resources](#expected-resources)
- [Current Deployment](#current-deployment)
- [Common Issues](#common-issues)
- [Cleanup Duplicate Resources](#cleanup-duplicate-resources)
- [Cost Optimization](#cost-optimization)
- [Resource Management](#resource-management)

---

## Expected Resources

### Correct Azure Deployment (8-9 Resources)

For a complete deployment in **rg-neo4j-rag-bitnet**, you should have:

| Resource Type | Name | Quantity | Purpose | Monthly Cost |
|---------------|------|----------|---------|--------------|
| **Container Registry** | crneo4jrag* | **1** | Store Docker images | $5 |
| **Container Apps Environment** | neo4j-rag-env | 1 | Host containers | $50 |
| **Container App** | neo4j-database | 1 | Neo4j database | $200 |
| **Container App** | rag-service | 1 | RAG API service | $100-500 |
| **Container App** | bitnet-llm | 1 (optional) | BitNet LLM service | $50-150 |
| **Container App** | neo4j-rag-agent | 1 (optional) | Agent Framework | $100-500 |
| **Container App** | mcp-server | 1 (optional) | MCP Server | $25-75 |
| **Azure OpenAI** | neo4j-rag-bitnet-ai | 1 (optional) | GPT-4o-mini | $0-200 |
| **Log Analytics** | workspace-* | 1 | Monitoring & logs | $25-100 |
| **Storage Account** | (optional) | 1 | Backups & PDFs | $10-50 |

**Total**: 8-10 resources
**Cost**: $465-1,830/month (depending on optional components)

---

## Current Deployment

### ⚠️ Issue Detected: Duplicate Container Registries

**Your resource group has:**
- ❌ **4 Container Registries** (Should be 1!)
- ✅ 2 Container Apps (Correct)
- ✅ 1 Azure OpenAI (Correct)
- ✅ 1 Container Apps Environment (Correct)
- ✅ 1 Log Analytics (Correct)

### Why Multiple Registries?

**Root Cause**: Deployment script generates random registry names

```bash
# Line in scripts/azure-deploy-complete.sh
REGISTRY_NAME="crneo4jrag$(openssl rand -hex 4)"
# This creates NEW registry each time!
```

**Each deployment run created**:
1. First run: `crneo4jrag0fe20593`
2. Second run: `crneo4jrag2ffa25d2`
3. Third run: `crneo4jrag5478c2fb`
4. Fourth run: `crneo4jragec81d81b`

**Only ONE is actually used** by your Container Apps!

---

## Common Issues

### Issue 1: Multiple Container Registries

**Symptoms:**
- Multiple `crneo4jrag*` registries in resource group
- Unnecessary $5/month cost per registry
- Confusion about which registry to use

**Impact:**
- **Cost**: $15-20/month wasted (3-4 extra registries × $5)
- **Confusion**: Which registry has latest images?
- **Management**: Unnecessary resources to maintain

**Solution:**
- Keep the registry used by Container Apps
- Delete unused registries
- Fix deployment script to reuse registry

### Issue 2: Incomplete Deployments

**Symptoms:**
- Container Apps not deployed
- Registry created but no images
- Environment exists but no apps

**Cause:**
- Deployment script failed mid-execution
- Network issues during deployment
- Permission errors

**Solution:**
- Check deployment logs
- Re-run deployment script
- Use `--debug` flag for detailed output

### Issue 3: Image Not Found

**Symptoms:**
- Container App creation fails
- "Image not found" error
- Registry exists but empty

**Cause:**
- Image build/push failed
- Wrong registry name used
- ACR not authenticated

**Solution:**
```bash
# Check images in registry
az acr repository list --name crneo4jrag2ffa25d2 --output table

# Re-build and push
az acr build --registry crneo4jrag2ffa25d2 \
  --image neo4j-rag:v1.0 \
  --file neo4j-rag-demo/Dockerfile.local \
  neo4j-rag-demo
```

---

## Cleanup Duplicate Resources

### Automated Cleanup Script

**Run the cleanup script:**

```bash
./scripts/azure-cleanup-duplicate-registries.sh
```

**What it does:**
1. Lists all Container Registries in resource group
2. Identifies which registry is actively used by Container Apps
3. Shows which registries can be safely deleted
4. Asks for confirmation before deletion
5. Deletes unused registries
6. Shows cost savings

**Expected Output:**
```
🔍 Azure Resource Cleanup - Duplicate Container Registries
==========================================================

Found 4 container registries:

Name                   SKU    CreatedDate          UsageGB
crneo4jrag0fe20593     Basic  2025-10-03T10:00:00  0.5
crneo4jrag2ffa25d2     Basic  2025-10-04T14:30:00  1.2
crneo4jrag5478c2fb     Basic  2025-10-05T09:15:00  0.8
crneo4jragec81d81b     Basic  2025-10-05T16:45:00  0.3

✅ Active registry (in use): crneo4jrag2ffa25d2

🗑️  Registries that can be safely deleted:
   ❌ crneo4jrag0fe20593 (not in use)
   ❌ crneo4jrag5478c2fb (not in use)
   ❌ crneo4jragec81d81b (not in use)
   ✅ crneo4jrag2ffa25d2 (KEEP - currently in use)

Continue with deletion? (yes/no):
```

### Manual Cleanup

**1. Identify Active Registry:**
```bash
# Check which registry Container Apps use
az containerapp list --resource-group rg-neo4j-rag-bitnet \
  --query "[].{Name:name, Image:properties.template.containers[0].image}" \
  --output table
```

**2. Delete Unused Registries:**
```bash
# Delete each unused registry
az acr delete --name crneo4jrag0fe20593 --resource-group rg-neo4j-rag-bitnet --yes
az acr delete --name crneo4jrag5478c2fb --resource-group rg-neo4j-rag-bitnet --yes
az acr delete --name crneo4jragec81d81b --resource-group rg-neo4j-rag-bitnet --yes

# Keep the one in use (example: crneo4jrag2ffa25d2)
```

**3. Verify Cleanup:**
```bash
az acr list --resource-group rg-neo4j-rag-bitnet --output table
# Should show only 1 registry
```

---

## Cost Optimization

### Before Cleanup

**4 Container Registries**: $20/month
**2 Container Apps**: $300-1000/month (varies with usage)
**Azure OpenAI**: $0-200/month (usage-based)
**Environment + Logs**: $75-150/month

**Total**: $395-1,370/month

### After Cleanup

**1 Container Registry**: $5/month ✅
**2 Container Apps**: $300-1000/month
**Azure OpenAI**: $0-200/month
**Environment + Logs**: $75-150/month

**Total**: $380-1,355/month
**Savings**: $15/month (from removing 3 duplicate registries)

---

## Proper Deployment Process

### Fixed Deployment Script

Update `scripts/azure-deploy-complete.sh` to reuse existing registry:

```bash
# Check if registry exists
EXISTING_REGISTRY=$(az acr list \
  --resource-group $RESOURCE_GROUP \
  --query "[0].name" -o tsv 2>/dev/null)

if [ -n "$EXISTING_REGISTRY" ]; then
    echo "✅ Using existing registry: $EXISTING_REGISTRY"
    REGISTRY_NAME=$EXISTING_REGISTRY
else
    echo "📦 Creating new registry..."
    REGISTRY_NAME="crneo4jrag$(openssl rand -hex 4)"
fi
```

### Idempotent Deployment

**Best Practice**: Deployment should be **idempotent** (safe to run multiple times)

```bash
# Before creating resource, check if exists
az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP &>/dev/null
if [ $? -eq 0 ]; then
    echo "Registry already exists, reusing..."
else
    echo "Creating new registry..."
    az acr create --name $REGISTRY_NAME ...
fi
```

---

## Resource Management

### View All Resources

```bash
# List all resources in resource group
az resource list --resource-group rg-neo4j-rag-bitnet --output table

# Detailed view
az resource list --resource-group rg-neo4j-rag-bitnet \
  --query "[].{Name:name, Type:type, Location:location}" \
  --output table
```

### Check Resource Costs

```bash
# View cost analysis
az consumption usage list \
  --start-date 2025-10-01 \
  --end-date 2025-10-05 \
  | jq '[.[] | select(.instanceName | contains("neo4j-rag"))]'

# Or use Azure Portal:
# Cost Management + Billing → Cost Analysis
```

### Delete Entire Resource Group (Careful!)

```bash
# ⚠️  WARNING: Deletes EVERYTHING in resource group
az group delete --name rg-neo4j-rag-bitnet --yes --no-wait

# Use only for complete cleanup/restart
```

---

## Recommended Resource Structure

### Minimal Deployment (Local Development)

**Azure Resources**: 0
**Local Resources**: Docker containers only
**Cost**: $0/month

```bash
# Run locally with Docker Compose
docker-compose -f scripts/docker-compose.optimized.yml up -d
```

### Production Deployment (Azure)

**Required Resources** (3):
1. Container Registry (1)
2. Container Apps Environment (1)
3. Log Analytics Workspace (1)

**Container Apps** (2-5 depending on architecture):
- neo4j-database (required)
- rag-service (required)
- bitnet-llm (optional)
- mcp-server (optional)
- agent-service (optional)

**Optional Resources**:
- Azure OpenAI (for Agent Framework)
- Storage Account (for backups)

**Total**: 5-10 resources
**Cost**: $380-1,830/month

---

## Current State Assessment

### What You Have Now

**✅ Working Deployment:**
- neo4j-database Container App
- neo4j-rag-agent Container App
- Azure OpenAI service
- Container Apps Environment
- Log Analytics

**❌ Issues:**
- 4 Container Registries (need 1)
- Missing: bitnet-llm Container App
- Missing: rag-service Container App
- Missing: mcp-server Container App (optional)

### Recommended Actions

**1. Cleanup Duplicates** (Save $15/month):
```bash
./scripts/azure-cleanup-duplicate-registries.sh
```

**2. Complete Deployment** (Add missing services):
```bash
# Deploy BitNet LLM
az containerapp create --name bitnet-llm ...

# Deploy RAG Service
az containerapp create --name rag-service ...

# Deploy MCP Server (optional)
az containerapp create --name mcp-server ...
```

**3. Verify Deployment**:
```bash
az containerapp list --resource-group rg-neo4j-rag-bitnet --output table
# Should show all required services
```

---

## Resource Naming Conventions

### Recommended Naming

**Format**: `{service}-{component}-{environment}`

```bash
# Resource Group
rg-neo4j-rag-prod              # Production
rg-neo4j-rag-dev               # Development

# Container Registry
crneo4jragprod                 # Production (no random suffix!)
crneo4jragdev                  # Development

# Container Apps
neo4j-database-prod
rag-service-prod
bitnet-llm-prod
mcp-server-prod

# Storage
stneo4jragprod                 # Storage account
```

**Benefits:**
- Clear purpose from name
- Easy to identify environment
- No confusion between deployments
- Predictable resource names

---

## Monitoring Resources

### Resource Health

```bash
# Check all Container Apps health
az containerapp list --resource-group rg-neo4j-rag-bitnet \
  --query "[].{Name:name, Status:properties.runningStatus, Replicas:properties.runningStatus}" \
  --output table

# Check Container Registry usage
az acr show-usage --name crneo4jrag2ffa25d2 --output table
```

### View Logs

```bash
# Container App logs
az containerapp logs show \
  --name neo4j-database \
  --resource-group rg-neo4j-rag-bitnet \
  --follow

# Log Analytics query
az monitor log-analytics query \
  --workspace workspace-rgneo4jragbitnetf4Qh \
  --analytics-query "ContainerAppConsoleLogs_CL | take 100"
```

---

## Related Documentation

- [**☁️ Azure Deployment Guide**](AZURE_DEPLOYMENT_GUIDE.md) - Step-by-step deployment
- [**🏗️ Azure Architecture**](AZURE_ARCHITECTURE.md) - Architecture overview
- [**💰 Cost Optimization**](azure/cost-optimized-deployment.md) - Cost strategies
- [**📖 Documentation Index**](README.md) - All documentation

---

**Last Updated**: 2025-10-05
**Your Current Issue**: 4 duplicate Container Registries (cleanup recommended)
**Quick Fix**: Run `./scripts/azure-cleanup-duplicate-registries.sh`
