#!/bin/bash
# Azure Enterprise Deployment Script
# Deploys Neo4j + RAG Service to Azure Container Apps
# Keeps BitNet and Streamlit local for cost optimization

set -e

# Configuration
RESOURCE_GROUP="rg-neo4j-rag-enterprise"
LOCATION="eastus"
ENVIRONMENT_NAME="env-neo4j-rag"
ACR_NAME="acrneo4jrag${RANDOM}"
KEY_VAULT_NAME="kv-neo4j-rag-${RANDOM}"
STORAGE_ACCOUNT="stneo4jrag${RANDOM}"

# Container Apps
NEO4J_APP_NAME="neo4j-rag"
RAG_APP_NAME="rag-service"

# Neo4j Configuration
NEO4J_USER="neo4j"
NEO4J_PASSWORD=$(openssl rand -base64 32)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "Azure Enterprise Deployment"
echo "Neo4j + RAG Service to Cloud"
echo "======================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v az &> /dev/null; then
    echo -e "${RED}ERROR: Azure CLI not installed${NC}"
    echo "Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

if ! az account show &> /dev/null; then
    echo -e "${RED}ERROR: Not logged in to Azure${NC}"
    echo "Run: az login"
    exit 1
fi

echo -e "${GREEN}✓ Azure CLI installed and logged in${NC}"
echo ""

# Get subscription info
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)

echo "Deploying to subscription:"
echo "  ID: $SUBSCRIPTION_ID"
echo "  Name: $SUBSCRIPTION_NAME"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 1
fi

# Step 1: Create Resource Group
echo ""
echo "Step 1: Creating Resource Group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output none

echo -e "${GREEN}✓ Resource Group created: $RESOURCE_GROUP${NC}"

# Step 2: Create Azure Container Registry
echo ""
echo "Step 2: Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output none

echo -e "${GREEN}✓ Container Registry created: $ACR_NAME${NC}"

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show -n $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show -n $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show -n $ACR_NAME --query passwords[0].value -o tsv)

echo "  Login Server: $ACR_LOGIN_SERVER"

# Step 3: Create Key Vault
echo ""
echo "Step 3: Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none

echo -e "${GREEN}✓ Key Vault created: $KEY_VAULT_NAME${NC}"

# Store Neo4j password in Key Vault
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name neo4j-password \
    --value "$NEO4J_PASSWORD" \
    --output none

echo "  ✓ Neo4j password stored in Key Vault"

# Step 4: Create Storage Account
echo ""
echo "Step 4: Creating Storage Account..."
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --output none

echo -e "${GREEN}✓ Storage Account created: $STORAGE_ACCOUNT${NC}"

# Create blob containers
STORAGE_KEY=$(az storage account keys list \
    --account-name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query [0].value -o tsv)

az storage container create \
    --name backups \
    --account-name $STORAGE_ACCOUNT \
    --account-key "$STORAGE_KEY" \
    --output none

az storage container create \
    --name documents \
    --account-name $STORAGE_ACCOUNT \
    --account-key "$STORAGE_KEY" \
    --output none

echo "  ✓ Blob containers created: backups, documents"

# Step 5: Create Application Insights
echo ""
echo "Step 5: Creating Application Insights..."
az monitor app-insights component create \
    --app neo4j-rag-insights \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --output none

INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app neo4j-rag-insights \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey -o tsv)

echo -e "${GREEN}✓ Application Insights created${NC}"
echo "  Instrumentation Key: ${INSTRUMENTATION_KEY:0:20}..."

# Step 6: Build and Push Container Images
echo ""
echo "Step 6: Building and Pushing Container Images..."

# Login to ACR
az acr login --name $ACR_NAME

# Build Neo4j image (custom with optimizations)
echo "  Building Neo4j image..."
cat > Dockerfile.neo4j.cloud <<EOF
FROM neo4j:5.11

# Environment variables will be set by Container Apps
# Install APOC and GDS plugins
ENV NEO4J_PLUGINS='["apoc", "graph-data-science"]'

# Optimization settings
ENV NEO4J_dbms_memory_heap_max__size=4G
ENV NEO4J_dbms_memory_pagecache_size=2G
ENV NEO4J_dbms_jvm_additional=-XX:+UseG1GC

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD cypher-shell "RETURN 1" || exit 1
EOF

docker build -f Dockerfile.neo4j.cloud -t $ACR_LOGIN_SERVER/neo4j:latest . --quiet
docker push $ACR_LOGIN_SERVER/neo4j:latest --quiet

echo -e "${GREEN}  ✓ Neo4j image pushed${NC}"

# Build RAG Service image
echo "  Building RAG Service image..."
cd neo4j-rag-demo

docker build -t $ACR_LOGIN_SERVER/rag-service:latest . --quiet
docker push $ACR_LOGIN_SERVER/rag-service:latest --quiet

echo -e "${GREEN}  ✓ RAG Service image pushed${NC}"

cd ..

# Step 7: Create Container Apps Environment
echo ""
echo "Step 7: Creating Container Apps Environment..."
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none

echo -e "${GREEN}✓ Container Apps Environment created${NC}"

# Step 8: Deploy Neo4j Container App
echo ""
echo "Step 8: Deploying Neo4j Database..."
az containerapp create \
    --name $NEO4J_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_LOGIN_SERVER/neo4j:latest \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 7474 \
    --ingress external \
    --cpu 2.0 \
    --memory 8Gi \
    --min-replicas 1 \
    --max-replicas 1 \
    --env-vars \
        "NEO4J_AUTH=neo4j/$NEO4J_PASSWORD" \
        "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY" \
    --output none

NEO4J_FQDN=$(az containerapp show \
    --name $NEO4J_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

echo -e "${GREEN}✓ Neo4j deployed${NC}"
echo "  URL: https://$NEO4J_FQDN"
echo "  Bolt: neo4j+s://$NEO4J_FQDN:7687"

# Step 9: Deploy RAG Service Container App
echo ""
echo "Step 9: Deploying RAG Service..."
az containerapp create \
    --name $RAG_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $ACR_LOGIN_SERVER/rag-service:latest \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --target-port 8000 \
    --ingress external \
    --cpu 4.0 \
    --memory 8Gi \
    --min-replicas 1 \
    --max-replicas 10 \
    --env-vars \
        "NEO4J_URI=bolt://$NEO4J_FQDN:7687" \
        "NEO4J_USER=$NEO4J_USER" \
        "NEO4J_PASSWORD=$NEO4J_PASSWORD" \
        "APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY" \
    --output none

# Configure auto-scaling
az containerapp update \
    --name $RAG_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --scale-rule-name cpu-scale \
    --scale-rule-type cpu \
    --scale-rule-metadata type=Utilization value=70 \
    --output none

RAG_FQDN=$(az containerapp show \
    --name $RAG_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

echo -e "${GREEN}✓ RAG Service deployed${NC}"
echo "  URL: https://$RAG_FQDN"

# Step 10: Health Checks
echo ""
echo "Step 10: Running Health Checks..."
sleep 30  # Wait for services to start

echo "  Checking Neo4j..."
if curl -s -f https://$NEO4J_FQDN > /dev/null; then
    echo -e "${GREEN}  ✓ Neo4j is accessible${NC}"
else
    echo -e "${RED}  ✗ Neo4j health check failed${NC}"
fi

echo "  Checking RAG Service..."
if curl -s -f https://$RAG_FQDN/health > /dev/null; then
    echo -e "${GREEN}  ✓ RAG Service is healthy${NC}"
else
    echo -e "${RED}  ✗ RAG Service health check failed${NC}"
fi

# Step 11: Create Configuration File for Local Testing
echo ""
echo "Step 11: Creating Local Test Configuration..."
cat > cloud-endpoints.env <<EOF
# Azure Cloud Endpoints
# Generated: $(date)

# Neo4j Database
export NEO4J_URI=neo4j+s://$NEO4J_FQDN:7687
export NEO4J_USER=$NEO4J_USER
export NEO4J_PASSWORD=$NEO4J_PASSWORD
export NEO4J_BROWSER=https://$NEO4J_FQDN

# RAG Service
export RAG_API_URL=https://$RAG_FQDN
export RAG_HEALTH_URL=https://$RAG_FQDN/health
export RAG_STATS_URL=https://$RAG_FQDN/stats

# Azure Resources
export AZURE_RESOURCE_GROUP=$RESOURCE_GROUP
export AZURE_KEY_VAULT=$KEY_VAULT_NAME
export AZURE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT
export APPINSIGHTS_KEY=$INSTRUMENTATION_KEY

# Local Services (keep running locally)
export BITNET_URL=http://localhost:8001
export STREAMLIT_URL=http://localhost:8501

# Test Configuration
export TEST_MODE=cloud
EOF

echo -e "${GREEN}✓ Configuration saved to cloud-endpoints.env${NC}"

# Step 12: Display Summary
echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo ""
echo "Cloud Services:"
echo "  Neo4j Database:  https://$NEO4J_FQDN"
echo "  Neo4j Bolt:      neo4j+s://$NEO4J_FQDN:7687"
echo "  RAG Service:     https://$RAG_FQDN"
echo ""
echo "Azure Resources:"
echo "  Resource Group:  $RESOURCE_GROUP"
echo "  Location:        $LOCATION"
echo "  Key Vault:       $KEY_VAULT_NAME"
echo "  Storage Account: $STORAGE_ACCOUNT"
echo ""
echo "Local Testing:"
echo "  1. Source the configuration:"
echo "     source cloud-endpoints.env"
echo ""
echo "  2. Update local Streamlit to use cloud RAG:"
echo "     cd neo4j-rag-demo/streamlit_app"
echo "     streamlit run app.py"
echo ""
echo "  3. Run Playwright tests against cloud:"
echo "     cd tests/playwright"
echo "     pytest -v --cloud"
echo ""
echo "Credentials (SAVE THESE SECURELY):"
echo "  Neo4j User:     $NEO4J_USER"
echo "  Neo4j Password: $NEO4J_PASSWORD"
echo "  (Also stored in Key Vault: $KEY_VAULT_NAME)"
echo ""
echo "Monitoring:"
echo "  Application Insights: neo4j-rag-insights"
echo "  Logs: az containerapp logs tail --name $RAG_APP_NAME -g $RESOURCE_GROUP"
echo ""
echo "Estimated Monthly Cost: ~$326"
echo "  - Neo4j (2CPU, 8GB):  $150"
echo "  - RAG (4CPU, 8GB):    $150"
echo "  - Storage & Monitoring: $26"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Configure custom domain (optional)"
echo "  2. Setup backup automation"
echo "  3. Configure monitoring alerts"
echo "  4. Run comprehensive tests"
echo "  5. Load sample data"
echo ""
