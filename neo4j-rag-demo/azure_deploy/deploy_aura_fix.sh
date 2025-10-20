#!/bin/bash
#
# Deploy Neo4j RAG Service to Azure Container Apps with Aura Connection
# Issue #4 Fix - Replaces mock data with real Aura connection
#

set -e

echo "🚀 Deploying Neo4j RAG Service to Azure Container Apps"
echo "========================================================"

# Configuration
RESOURCE_GROUP="rg-neo4j-rag-bitnet"
CONTAINER_APP_NAME="neo4j-rag-agent"
IMAGE_NAME="rag-aura-service:v2.0"
LOCATION="swedencentral"

# Neo4j Aura Credentials
NEO4J_URI="neo4j+s://6b870b04.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="YHD6ZnCOHGyiYYTmFE5td3cMiLoE-DkVK7zvwQFKFrM"

echo ""
echo "📦 Step 1: Verify Docker image exists locally"
if docker images | grep -q "rag-aura-service.*v2.0"; then
    echo "✅ Docker image found: $IMAGE_NAME"
else
    echo "❌ Docker image not found. Please build it first:"
    echo "   cd neo4j-rag-demo"
    echo "   docker build -f azure_deploy/Dockerfile -t rag-aura-service:v2.0 ."
    exit 1
fi

echo ""
echo "🔍 Step 2: Check current Container App status"
az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --output table 2>/dev/null || echo "Container App not found or error accessing"

echo ""
echo "🎯 Step 3: Update Container App with Aura credentials"
echo "   - Setting environment variables for production mode"
echo "   - Connecting to Aura: $NEO4J_URI"

# Update environment variables only (keep existing image for now)
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars \
        NEO4J_URI="$NEO4J_URI" \
        NEO4J_USERNAME="$NEO4J_USERNAME" \
        NEO4J_PASSWORD="$NEO4J_PASSWORD" \
        MODE="production" \
    --output table

echo ""
echo "⏳ Step 4: Wait for deployment to complete (30 seconds)"
sleep 30

echo ""
echo "✅ Step 5: Verify deployment"
echo "   Testing health endpoint..."

HEALTH_URL="https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/health"
echo "   URL: $HEALTH_URL"

HEALTH_RESPONSE=$(curl -s $HEALTH_URL)
echo "   Response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q '"mode":"production"'; then
    echo "✅ SUCCESS: Container App is in production mode!"
elif echo "$HEALTH_RESPONSE" | grep -q '"mode":"mock_data"'; then
    echo "⚠️  WARNING: Container App still in mock_data mode"
    echo "   The deployment may still be in progress. Wait a few more minutes and check again:"
    echo "   curl $HEALTH_URL | jq ."
else
    echo "❌ ERROR: Unexpected response from health endpoint"
    echo "   Response: $HEALTH_RESPONSE"
fi

echo ""
echo "📋 Step 6: Test all endpoints"

# Test stats endpoint
echo ""
echo "Testing /stats endpoint..."
STATS_URL="https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/stats"
STATS_RESPONSE=$(curl -s $STATS_URL)
echo "Response: $STATS_RESPONSE"

# Test query endpoint
echo ""
echo "Testing /query endpoint..."
QUERY_URL="https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/query"
QUERY_RESPONSE=$(curl -s -X POST $QUERY_URL \
    -H "Content-Type: application/json" \
    -d '{"question": "What is Neo4j?", "k": 3}')

if echo "$QUERY_RESPONSE" | grep -q '"results"'; then
    echo "✅ Query endpoint working!"
    echo "   First result snippet:"
    echo "$QUERY_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('   Text:', data['results'][0]['text'][:100] + '...')" 2>/dev/null || echo "   (Could not parse response)"
else
    echo "⚠️  Query endpoint response:"
    echo "   $QUERY_RESPONSE"
fi

echo ""
echo "========================================================"
echo "🎉 Deployment Process Complete!"
echo ""
echo "📊 Next Steps:"
echo "1. Verify all endpoints are working:"
echo "   curl $HEALTH_URL | jq ."
echo "   curl $STATS_URL | jq ."
echo ""
echo "2. Configure Azure AI Foundry:"
echo "   - Upload docs/AZURE_AI_FOUNDRY_OPENAPI_SPEC.yaml"
echo "   - Test query: 'What is Neo4j?'"
echo ""
echo "3. If still showing mock_data mode:"
echo "   - Wait a few more minutes for Container App to restart"
echo "   - Check logs: az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "📝 Full documentation: docs/ISSUE_4_IMPLEMENTATION_SUMMARY.md"
echo "========================================================"
