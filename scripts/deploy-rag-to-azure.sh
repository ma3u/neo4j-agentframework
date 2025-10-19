#!/bin/bash
# Deploy Simple RAG API to Azure Container Apps
# Connects to Neo4j Aura instance 6b870b04

set -e

echo "🚀 Deploying Neo4j RAG Service to Azure Container Apps"
echo "="*70

# Configuration
RESOURCE_GROUP="rg-neo4j-rag-bitnet"
CONTAINER_APP_NAME="neo4j-rag-agent"
IMAGE_NAME="ghcr.io/ma3u/ms-agentf-neo4j/rag-service-simple:v2.0-aura"
AURA_INSTANCE="6b870b04"

# Aura connection (from environment or Key Vault)
NEO4J_URI="neo4j+s://${AURA_INSTANCE}.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
# Password should come from Key Vault or environment

echo "📦 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Container App: $CONTAINER_APP_NAME"
echo "  Image: $IMAGE_NAME"
echo "  Aura Instance: $AURA_INSTANCE"
echo "  Neo4j URI: $NEO4J_URI"
echo ""

# Check if we're building or using existing image
read -p "Build new image? (y/n): " BUILD_IMAGE

if [ "$BUILD_IMAGE" = "y" ]; then
    echo "🔨 Building Docker image..."
    cd neo4j-rag-demo

    docker build \
        -f azure_deploy/Dockerfile.simple \
        -t $IMAGE_NAME \
        .

    echo "📤 Pushing to GitHub Container Registry..."
    docker push $IMAGE_NAME

    echo "✅ Image built and pushed"
    cd ..
else
    echo "⏭️  Skipping build, using existing image"
fi

# Update Container App
echo "🔄 Updating Container App..."

# Get password from user or Key Vault
if [ -z "$NEO4J_PASSWORD" ]; then
    echo "🔑 Neo4j Aura password needed"
    read -s -p "Password: " NEO4J_PASSWORD
    echo ""
fi

az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $IMAGE_NAME \
    --set-env-vars \
        "NEO4J_URI=$NEO4J_URI" \
        "NEO4J_USERNAME=$NEO4J_USERNAME" \
        "NEO4J_PASSWORD=$NEO4J_PASSWORD" \
        "MODE=production" \
    --output none

echo "✅ Container App updated"

# Wait for deployment
echo "⏳ Waiting for Container App to restart..."
sleep 30

# Get FQDN
FQDN=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    -o tsv)

echo "🌐 Service URL: https://$FQDN"

# Test health
echo "🏥 Testing health endpoint..."
curl -s "https://$FQDN/health" | python3 -m json.tool

echo ""
echo "📊 Testing stats endpoint..."
curl -s "https://$FQDN/stats" | python3 -m json.tool

echo ""
echo "="*70
echo "✅ Deployment Complete!"
echo ""
echo "Service Endpoints:"
echo "  Health:  https://$FQDN/health"
echo "  Stats:   https://$FQDN/stats"
echo "  Query:   https://$FQDN/query"
echo "  Docs:    https://$FQDN/docs"
echo ""
echo "Test Query:"
echo "  curl -X POST https://$FQDN/query \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"question\":\"What is Neo4j?\",\"k\":5}'"
echo ""
echo "Next: Configure Azure AI Foundry functions to use this endpoint"
