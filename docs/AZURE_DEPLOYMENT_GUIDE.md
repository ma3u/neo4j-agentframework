# Azure Deployment Guide: Neo4j RAG + Microsoft Agent Framework

This guide provides step-by-step instructions for deploying your optimized Neo4j RAG system to Azure using Microsoft Agent Framework.

## 🎯 Deployment Overview

**What We're Deploying:**
- High-performance Neo4j RAG system (417x faster than baseline)
- Microsoft Agent Framework integration
- Azure AI Foundry models (GPT-4o-mini)
- Azure Container Apps hosting
- Production-ready monitoring and scaling

## 📋 Prerequisites

### Required Azure Services
- ✅ Azure subscription with appropriate permissions
- ✅ Azure AI Foundry project
- ✅ Azure Container Registry
- ✅ Azure Container Apps Environment
- ✅ Azure Key Vault (for secrets)
- ✅ Azure Application Insights (for monitoring)

### Local Requirements
- ✅ Azure CLI installed and authenticated (`az login`)
- ✅ Docker Desktop running
- ✅ Python 3.11+ with your optimized Neo4j RAG codebase

### Required Permissions
- `Cognitive Services OpenAI User` or `Cognitive Services OpenAI Contributor`
- `Container Apps Contributor`
- `Key Vault Contributor`
- `Application Insights Contributor`

## 🚀 Step-by-Step Deployment

### Phase 1: Azure Infrastructure Setup

#### 1.1 Create Resource Group
```bash
# Set variables
export RESOURCE_GROUP="neo4j-rag-rg"
export LOCATION="eastus"
export PROJECT_NAME="neo4j-rag-prod"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION
```

#### 1.2 Create Azure AI Foundry Project
```bash
# Create AI Foundry workspace first
az cognitiveservices account create \
  --name "${PROJECT_NAME}-ai" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --kind "OpenAI" \
  --sku "S0"

# Deploy GPT-4o-mini model
az cognitiveservices account deployment create \
  --resource-group $RESOURCE_GROUP \
  --account-name "${PROJECT_NAME}-ai" \
  --deployment-name "gpt-4o-mini" \
  --model-name "gpt-4o-mini" \
  --model-version "2024-07-18" \
  --sku-capacity 10 \
  --sku-name "Standard"

# Get your endpoint
export AZURE_AI_ENDPOINT=$(az cognitiveservices account show \
  --name "${PROJECT_NAME}-ai" \
  --resource-group $RESOURCE_GROUP \
  --query "properties.endpoint" \
  --output tsv)

echo "Your Azure AI Endpoint: $AZURE_AI_ENDPOINT"
```

#### 1.3 Create Container Registry
```bash
# Create Azure Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name "${PROJECT_NAME}acr" \
  --sku Basic \
  --location $LOCATION

# Get login server
export ACR_LOGIN_SERVER=$(az acr show \
  --name "${PROJECT_NAME}acr" \
  --resource-group $RESOURCE_GROUP \
  --query loginServer \
  --output tsv)

echo "Your ACR Login Server: $ACR_LOGIN_SERVER"
```

#### 1.4 Create Key Vault
```bash
# Create Key Vault for secrets
az keyvault create \
  --name "${PROJECT_NAME}-kv" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store secrets
az keyvault secret set \
  --vault-name "${PROJECT_NAME}-kv" \
  --name "neo4j-password" \
  --value "your-secure-password-here"

az keyvault secret set \
  --vault-name "${PROJECT_NAME}-kv" \
  --name "azure-ai-endpoint" \
  --value "$AZURE_AI_ENDPOINT"
```

#### 1.5 Create Container Apps Environment
```bash
# Create Container Apps Environment
az containerapp env create \
  --name "${PROJECT_NAME}-env" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### Phase 2: Build and Deploy Containers

#### 2.1 Build and Push Neo4j RAG Agent Image
```bash
# Navigate to your project directory
cd /path/to/your/neo4j-rag-demo

# Log into Azure Container Registry
az acr login --name "${PROJECT_NAME}acr"

# Build and push the agent image
az acr build \
  --registry "${PROJECT_NAME}acr" \
  --image neo4j-rag-agent:v1.0 \
  --file azure/Dockerfile.agent \
  .
```

#### 2.2 Deploy Neo4j Database Container App
```bash
# Create Neo4j container app with optimized configuration
az containerapp create \
  --name neo4j-database \
  --resource-group $RESOURCE_GROUP \
  --environment "${PROJECT_NAME}-env" \
  --image neo4j:5.11 \
  --target-port 7687 \
  --ingress internal \
  --env-vars \
    NEO4J_AUTH=neo4j/your-secure-password-here \
    NEO4J_dbms_memory_heap_initial__size=4G \
    NEO4J_dbms_memory_heap_max__size=6G \
    NEO4J_dbms_memory_pagecache_size=3G \
    NEO4J_dbms_connector_bolt_thread__pool__max__size=500 \
    NEO4J_dbms_transaction_concurrent_maximum=2000 \
  --cpu 4.0 \
  --memory 8Gi \
  --min-replicas 1 \
  --max-replicas 1
```

#### 2.3 Deploy Neo4j RAG Agent Container App
```bash
# Create the RAG Agent container app
az containerapp create \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --environment "${PROJECT_NAME}-env" \
  --image "${ACR_LOGIN_SERVER}/neo4j-rag-agent:v1.0" \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    NEO4J_URI=bolt://neo4j-database:7687 \
    NEO4J_USER=neo4j \
    NEO4J_PASSWORD=your-secure-password-here \
    AZURE_AI_PROJECT_ENDPOINT="$AZURE_AI_ENDPOINT" \
    AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini \
    AZURE_CLI_AUTH=true \
  --cpu 2.0 \
  --memory 4Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --registry-server $ACR_LOGIN_SERVER
```

### Phase 3: Configure Authentication and Monitoring

#### 3.1 Configure Managed Identity
```bash
# Create user-assigned managed identity
az identity create \
  --name "${PROJECT_NAME}-identity" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Get identity details
export IDENTITY_ID=$(az identity show \
  --name "${PROJECT_NAME}-identity" \
  --resource-group $RESOURCE_GROUP \
  --query id \
  --output tsv)

export IDENTITY_CLIENT_ID=$(az identity show \
  --name "${PROJECT_NAME}-identity" \
  --resource-group $RESOURCE_GROUP \
  --query clientId \
  --output tsv)

# Assign identity to container app
az containerapp identity assign \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --user-assigned $IDENTITY_ID

# Grant permissions to AI service
az role assignment create \
  --assignee $IDENTITY_CLIENT_ID \
  --role "Cognitive Services OpenAI User" \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/${PROJECT_NAME}-ai"
```

#### 3.2 Configure Application Insights
```bash
# Create Application Insights
az monitor app-insights component create \
  --app "${PROJECT_NAME}-insights" \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --kind web

# Get instrumentation key
export APPINSIGHTS_KEY=$(az monitor app-insights component show \
  --app "${PROJECT_NAME}-insights" \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

# Update container app with monitoring
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    APPLICATIONINSIGHTS_INSTRUMENTATION_KEY=$APPINSIGHTS_KEY
```

### Phase 4: Load Data and Validate Deployment

#### 4.1 Get Container App URL
```bash
# Get the public URL of your deployed agent
export AGENT_URL=$(az containerapp show \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Your Neo4j RAG Agent URL: https://$AGENT_URL"
```

#### 4.2 Load Your Knowledge Base
```bash
# Upload your existing Neo4j data using the container app
# First, copy your data to the Neo4j container
az containerapp exec \
  --name neo4j-database \
  --resource-group $RESOURCE_GROUP \
  --command "/bin/bash"

# Or use your existing data loading scripts
# python scripts/load_sample_data.py --neo4j-uri=bolt://$AGENT_URL:7687
```

#### 4.3 Test the Deployment
```bash
# Test the health endpoint
curl https://$AGENT_URL/health

# Test the agent functionality
curl -X POST https://$AGENT_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Neo4j?", "user_id": "test-user"}'

# Get system statistics
curl https://$AGENT_URL/stats
```

## 🔧 Production Configuration

### Environment Variables Configuration
Create a `.env.azure` file for production deployment:

```bash
# Azure AI Configuration
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# Neo4j Configuration  
NEO4J_URI=bolt://neo4j-database:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=secure-production-password

# Authentication
AZURE_CLI_AUTH=true

# Performance Configuration
WORKERS=4
MAX_CONNECTIONS=100
LOG_LEVEL=INFO

# Monitoring
APPLICATIONINSIGHTS_INSTRUMENTATION_KEY=your-insights-key
```

### Scaling Configuration
```bash
# Configure auto-scaling rules
az containerapp revision set-mode \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --mode single

# Set scaling rules based on HTTP requests
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --scale-rule-name http-requests \
  --scale-rule-type http \
  --scale-rule-metadata concurrentRequests=50 \
  --min-replicas 1 \
  --max-replicas 20
```

## 📊 Monitoring and Maintenance

### Application Insights Queries
Use these KQL queries in Application Insights:

```kusto
// Performance monitoring
requests
| where timestamp > ago(1h)
| summarize 
    AvgDuration = avg(duration),
    MaxDuration = max(duration),
    RequestCount = count()
by bin(timestamp, 5m)
| render timechart

// Error tracking
exceptions
| where timestamp > ago(24h)
| summarize ErrorCount = count() by type
| order by ErrorCount desc

// Agent Framework specific metrics
customMetrics
| where name contains "neo4j" or name contains "agent"
| summarize avg(value) by name, bin(timestamp, 15m)
| render timechart
```

### Health Checks
Set up Azure Monitor alerts:

```bash
# Create alert for high response times
az monitor metrics alert create \
  --name "Neo4j RAG High Response Time" \
  --resource-group $RESOURCE_GROUP \
  --scopes "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/neo4j-rag-agent" \
  --condition "avg requests/duration > 5000" \
  --description "Alert when average response time exceeds 5 seconds" \
  --evaluation-frequency 5m \
  --window-size 15m \
  --severity 2
```

## 🔄 Migration Strategy

### From Local to Azure

#### Data Migration
1. **Export Neo4j Data:**
   ```bash
   # Create dump of your local Neo4j database
   docker exec neo4j-rag neo4j-admin dump --to=/backups/production-dump.dump
   ```

2. **Import to Azure:**
   ```bash
   # Copy dump to Azure container
   az containerapp exec \
     --name neo4j-database \
     --resource-group $RESOURCE_GROUP \
     --command "neo4j-admin load --from=/backups/production-dump.dump --force"
   ```

#### Configuration Migration
1. **Update Connection Strings:** Replace local URIs with Azure internal service names
2. **Environment Variables:** Use Azure Key Vault references
3. **Authentication:** Switch from local auth to Managed Identity

### Performance Validation
After migration, validate that the 417x performance improvement is preserved:

```bash
# Run performance tests
curl -X POST https://$AGENT_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me system statistics", "user_id": "performance-test"}' \
  | jq '.performance'
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Agent Framework Authentication Errors
**Symptom:** `Failed to initialize agent: Authentication failed`
**Solution:**
```bash
# Verify managed identity is properly configured
az containerapp identity show \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP

# Check role assignments
az role assignment list \
  --assignee $IDENTITY_CLIENT_ID \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP"
```

#### 2. Neo4j Connection Issues
**Symptom:** `Connection refused to Neo4j`
**Solution:**
```bash
# Check Neo4j container logs
az containerapp logs show \
  --name neo4j-database \
  --resource-group $RESOURCE_GROUP \
  --follow

# Verify internal networking
az containerapp show \
  --name neo4j-database \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress
```

#### 3. Performance Degradation
**Symptom:** Slower than expected response times
**Solution:**
```bash
# Check resource utilization
az containerapp revision list \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --query "[].{name:name,cpu:properties.template.containers[0].resources.cpu,memory:properties.template.containers[0].resources.memory}"

# Scale up if needed
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --cpu 4.0 \
  --memory 8Gi
```

### Debug Mode Deployment
For troubleshooting, deploy with debug configuration:

```bash
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars \
    LOG_LEVEL=DEBUG \
    PYTHONDEBUG=1
```

## 🔐 Security Best Practices

1. **Use Managed Identity** for all Azure service authentication
2. **Store secrets in Key Vault** and reference via environment variables
3. **Enable Container Apps ingress restrictions** for internal services
4. **Configure VNet integration** for production deployments
5. **Enable audit logging** for all API calls

## 💰 Cost Optimization

### Resource Sizing Recommendations
- **Agent Container:** 2 CPU, 4GB RAM (scales 0-10 instances)
- **Neo4j Container:** 4 CPU, 8GB RAM (persistent, always-on)
- **AI Model:** GPT-4o-mini for cost-effective performance

### Auto-scaling Best Practices
```bash
# Configure intelligent scaling
az containerapp update \
  --name neo4j-rag-agent \
  --resource-group $RESOURCE_GROUP \
  --scale-rule-name cpu-utilization \
  --scale-rule-type cpu \
  --scale-rule-metadata type=Utilization targetAverageUtilization=70 \
  --min-replicas 1 \
  --max-replicas 10
```

## 📝 Next Steps

1. **Setup CI/CD Pipeline:** Implement GitHub Actions for automated deployment
2. **Configure Backup Strategy:** Schedule regular Neo4j backups to Azure Storage
3. **Load Testing:** Validate performance under expected production load
4. **Security Review:** Conduct penetration testing and security audit
5. **Documentation:** Create runbooks for operations team

## 🎉 Success Validation

Your deployment is successful when you can:

✅ Access the agent at your Container App URL  
✅ Receive responses in <1 second (preserving 417x optimization)  
✅ See performance metrics in Application Insights  
✅ Auto-scale based on load  
✅ Maintain >99.9% uptime  
✅ Process concurrent requests efficiently  

**Congratulations!** You now have a production-ready, high-performance Neo4j RAG system running on Azure with Microsoft Agent Framework integration.

---

For additional support or questions about this deployment, refer to:
- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/)
- [Neo4j Production Deployment Guide](https://neo4j.com/docs/operations-manual/current/deployment/)

**Performance Optimized** • **Production Ready** • **Azure Native**