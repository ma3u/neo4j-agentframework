#!/bin/bash
# Complete Azure Deployment Script
# Deploys Neo4j RAG + BitNet + Microsoft Agent Framework to Azure
# Uses Azure CLI to create all resources

set -e  # Exit on error

echo "🚀 Azure Deployment: Neo4j RAG + BitNet + Agent Framework"
echo "=========================================================="

# Configuration
export RESOURCE_GROUP="${RESOURCE_GROUP:-rg-neo4j-rag-bitnet}"
export LOCATION="${LOCATION:-eastus}"
export APP_NAME="${APP_NAME:-neo4j-rag-bitnet}"
export REGISTRY_NAME="${REGISTRY_NAME:-crneo4jrag$(openssl rand -hex 4)}"

echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  App Name: $APP_NAME"
echo "  Registry: $REGISTRY_NAME"
echo ""

# Step 1: Create Resource Group
echo "1️⃣  Creating Resource Group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

echo "✅ Resource Group created"
echo ""

# Step 2: Create Azure Container Registry
echo "2️⃣  Creating Azure Container Registry..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic \
  --admin-enabled true \
  --location $LOCATION

REGISTRY_URL=$(az acr show --name $REGISTRY_NAME --query loginServer -o tsv)
echo "✅ ACR created: $REGISTRY_URL"
echo ""

# Step 3: Create Azure AI Foundry (OpenAI Service)
echo "3️⃣  Creating Azure AI Foundry (OpenAI Service)..."
az cognitiveservices account create \
  --name "${APP_NAME}-ai" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --kind OpenAI \
  --sku S0 \
  --yes

echo "✅ Azure AI Services created"
echo ""

# Step 4: Deploy GPT-4o-mini model
echo "4️⃣  Deploying GPT-4o-mini model..."
az cognitiveservices account deployment create \
  --name "${APP_NAME}-ai" \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4o-mini \
  --model-name gpt-4o-mini \
  --model-version "2024-07-18" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard

AZURE_AI_ENDPOINT=$(az cognitiveservices account show \
  --name "${APP_NAME}-ai" \
  --resource-group $RESOURCE_GROUP \
  --query "properties.endpoint" \
  --output tsv)

echo "✅ Model deployed"
echo "   Endpoint: $AZURE_AI_ENDPOINT"
echo ""

# Step 5: Build and Push Docker Images to ACR
echo "5️⃣  Building and pushing Docker images to ACR..."

# Login to ACR
az acr login --name $REGISTRY_NAME

# Build Neo4j RAG image
echo "   Building RAG service..."
az acr build \
  --registry $REGISTRY_NAME \
  --image neo4j-rag:v1.0 \
  --file neo4j-rag-demo/Dockerfile.local \
  neo4j-rag-demo

# Build BitNet image (using real BitNet)
echo "   Building BitNet service..."
az acr build \
  --registry $REGISTRY_NAME \
  --image bitnet-llm:v1.0 \
  --file Dockerfile.bitnet-final \
  .

# Build Agent Framework image
echo "   Building Agent Framework service..."
az acr build \
  --registry $REGISTRY_NAME \
  --image neo4j-agent:v1.0 \
  --file neo4j-rag-demo/azure_deploy/Dockerfile.agent \
  neo4j-rag-demo

echo "✅ All images built and pushed to ACR"
echo ""

# Step 6: Create Container Apps Environment
echo "6️⃣  Creating Container Apps Environment..."
az containerapp env create \
  --name "${APP_NAME}-env" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

echo "✅ Container Apps Environment created"
echo ""

# Step 7: Deploy Neo4j Database
echo "7️⃣  Deploying Neo4j Database..."
az containerapp create \
  --name neo4j-database \
  --resource-group $RESOURCE_GROUP \
  --environment "${APP_NAME}-env" \
  --image neo4j:5.15-community \
  --target-port 7687 \
  --ingress internal \
  --env-vars \
    NEO4J_AUTH=neo4j/SecurePassword123! \
    NEO4J_dbms_memory_heap_max__size=4G \
    NEO4J_dbms_memory_pagecache_size=2G \
  --cpu 2.0 \
  --memory 4Gi \
  --min-replicas 1 \
  --max-replicas 1

echo "✅ Neo4j deployed"
echo ""

# Step 8: Deploy BitNet LLM Service
echo "8️⃣  Deploying BitNet LLM Service..."
az containerapp create \
  --name bitnet-llm \
  --resource-group $RESOURCE_GROUP \
  --environment "${APP_NAME}-env" \
  --image $REGISTRY_URL/bitnet-llm:v1.0 \
  --target-port 8001 \
  --ingress internal \
  --cpu 2.0 \
  --memory 4Gi \
  --min-replicas 1 \
  --max-replicas 3 \
  --registry-server $REGISTRY_URL

echo "✅ BitNet LLM deployed"
echo ""

# Step 9: Deploy RAG Service
echo "9️⃣  Deploying RAG Service..."
az containerapp create \
  --name rag-service \
  --resource-group $RESOURCE_GROUP \
  --environment "${APP_NAME}-env" \
  --image $REGISTRY_URL/neo4j-rag:v1.0 \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    NEO4J_URI=http://neo4j-database:7687 \
    NEO4J_USER=neo4j \
    NEO4J_PASSWORD=SecurePassword123! \
    BITNET_ENDPOINT=http://bitnet-llm:8001 \
  --cpu 1.0 \
  --memory 2Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --registry-server $REGISTRY_URL

RAG_URL=$(az containerapp show \
  --name rag-service \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "✅ RAG Service deployed"
echo "   URL: https://$RAG_URL"
echo ""

# Step 10: Create Managed Identity for Agent Framework
echo "🔟 Creating Managed Identity for Agent Framework..."
az identity create \
  --name "${APP_NAME}-identity" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

IDENTITY_ID=$(az identity show \
  --name "${APP_NAME}-identity" \
  --resource-group $RESOURCE_GROUP \
  --query id \
  --output tsv)

IDENTITY_CLIENT_ID=$(az identity show \
  --name "${APP_NAME}-identity" \
  --resource-group $RESOURCE_GROUP \
  --query clientId \
  --output tsv)

echo "✅ Managed Identity created"
echo "   Client ID: $IDENTITY_CLIENT_ID"
echo ""

# Step 11: Grant AI Service Permissions
echo "1️⃣1️⃣  Granting AI Service permissions..."
az role assignment create \
  --assignee $IDENTITY_CLIENT_ID \
  --role "Cognitive Services OpenAI User" \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/${APP_NAME}-ai"

echo "✅ Permissions granted"
echo ""

# Step 12: Deploy Agent Framework Service
echo "1️⃣2️⃣  Deploying Microsoft Agent Framework Service..."
az containerapp create \
  --name neo4j-agent \
  --resource-group $RESOURCE_GROUP \
  --environment "${APP_NAME}-env" \
  --image $REGISTRY_URL/neo4j-agent:v1.0 \
  --target-port 8000 \
  --ingress external \
  --env-vars \
    NEO4J_URI=http://neo4j-database:7687 \
    NEO4J_USER=neo4j \
    NEO4J_PASSWORD=SecurePassword123! \
    AZURE_AI_PROJECT_ENDPOINT=$AZURE_AI_ENDPOINT \
    AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini \
    AZURE_CLIENT_ID=$IDENTITY_CLIENT_ID \
  --cpu 2.0 \
  --memory 4Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --registry-server $REGISTRY_URL \
  --user-assigned $IDENTITY_ID

AGENT_URL=$(az containerapp show \
  --name neo4j-agent \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "✅ Agent Framework deployed"
echo "   URL: https://$AGENT_URL"
echo ""

# Step 13: Summary
echo "=========================================================="
echo "🎉 Deployment Complete!"
echo "=========================================================="
echo ""
echo "📊 Deployed Services:"
echo "  1. Neo4j Database      (internal)"
echo "  2. BitNet LLM          (internal)"
echo "  3. RAG Service         https://$RAG_URL"
echo "  4. Agent Service       https://$AGENT_URL"
echo "  5. Azure AI Foundry    $AZURE_AI_ENDPOINT"
echo ""
echo "🧪 Test Commands:"
echo ""
echo "  # Test RAG Service"
echo "  curl https://$RAG_URL/health"
echo ""
echo "  # Test Agent Framework"
echo "  curl -X POST https://$AGENT_URL/chat \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"message\":\"What is Neo4j?\",\"user_id\":\"test\"}'"
echo ""
echo "📝 Resource Group: $RESOURCE_GROUP"
echo "🗑️  To delete: az group delete --name $RESOURCE_GROUP --yes"
echo ""
