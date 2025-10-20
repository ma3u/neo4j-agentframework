#!/bin/bash
#
# Complete Azure Deployment - Updates Container App with new ACR image
# Run this after Docker image has been pushed to ACR
#

set -e

echo "🚀 Completing Azure Container App Deployment"
echo "=============================================="

# Configuration
RESOURCE_GROUP="rg-neo4j-rag-bitnet"
CONTAINER_APP_NAME="neo4j-rag-agent"
ACR_NAME="crneo4jrag1af4ec"
IMAGE_NAME="rag-aura-service:v2.0"
FULL_IMAGE="$ACR_NAME.azurecr.io/$IMAGE_NAME"

echo ""
echo "📦 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Container App:  $CONTAINER_APP_NAME"
echo "   ACR:           $ACR_NAME.azurecr.io"
echo "   Image:         $IMAGE_NAME"

echo ""
echo "🔍 Step 1: Verify image exists in ACR"
if az acr repository show --name $ACR_NAME --image $IMAGE_NAME &>/dev/null; then
    echo "✅ Image found in ACR: $FULL_IMAGE"
else
    echo "❌ Image not found in ACR. Push may still be in progress."
    echo "   Check with: az acr repository list --name $ACR_NAME -o table"
    exit 1
fi

echo ""
echo "🎯 Step 2: Update Container App with new image"
echo "   This will:"
echo "   - Deploy new image from ACR"
echo "   - Keep existing environment variables (Aura credentials)"
echo "   - Restart the Container App"

az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $FULL_IMAGE \
    --output table

echo ""
echo "⏳ Step 3: Wait for Container App to restart (45 seconds)"
sleep 45

echo ""
echo "✅ Step 4: Verify deployment"
echo ""

# Test health endpoint
HEALTH_URL="https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/health"
echo "Testing health endpoint..."
echo "URL: $HEALTH_URL"
echo ""

HEALTH_RESPONSE=$(curl -s $HEALTH_URL)
echo "Response:"
echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"

echo ""
if echo "$HEALTH_RESPONSE" | grep -q '"mode":"production"'; then
    echo "✅ SUCCESS! Container App is now in PRODUCTION mode!"
    echo ""
    echo "   Connected to: Neo4j Aura (6b870b04)"

    # Extract stats if available
    if echo "$HEALTH_RESPONSE" | grep -q '"documents"'; then
        DOCS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['stats']['documents'])" 2>/dev/null || echo "?")
        CHUNKS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['stats']['chunks'])" 2>/dev/null || echo "?")
        echo "   Documents: $DOCS"
        echo "   Chunks: $CHUNKS"
    fi
elif echo "$HEALTH_RESPONSE" | grep -q '"mode":"mock_data"'; then
    echo "⚠️  WARNING: Still showing mock_data mode"
    echo "   The Container App may need more time to restart."
    echo "   Wait a few minutes and check again:"
    echo "   curl $HEALTH_URL | jq ."
elif echo "$HEALTH_RESPONSE" | grep -q "status.*healthy"; then
    echo "⚠️  Container is healthy but response format unexpected"
    echo "   Check the response above for details"
else
    echo "❌ Unexpected response from health endpoint"
    echo "   Check Container App logs:"
    echo "   az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
fi

echo ""
echo "📋 Step 5: Test additional endpoints"

# Test stats endpoint
echo ""
echo "Testing /stats endpoint..."
STATS_URL="https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/stats"
STATS_RESPONSE=$(curl -s $STATS_URL)

if echo "$STATS_RESPONSE" | grep -q '"documents"'; then
    echo "✅ Stats endpoint working:"
    echo "$STATS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$STATS_RESPONSE"
else
    echo "⚠️  Stats response: $STATS_RESPONSE"
fi

# Test query endpoint
echo ""
echo "Testing /query endpoint..."
QUERY_URL="https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io/query"
QUERY_RESPONSE=$(curl -s -X POST $QUERY_URL \
    -H "Content-Type: application/json" \
    -d '{"question": "What is Neo4j?", "k": 3}')

if echo "$QUERY_RESPONSE" | grep -q '"results"'; then
    echo "✅ Query endpoint working!"
    echo "   Returned $(echo "$QUERY_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['results']))" 2>/dev/null || echo "?") results"
    echo ""
    echo "   First result snippet:"
    echo "$QUERY_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('   Text:', data['results'][0]['text'][:80] + '...'); print('   Score:', data['results'][0]['score'])" 2>/dev/null || echo "   (Could not parse)"
else
    echo "⚠️  Query response: $QUERY_RESPONSE"
fi

echo ""
echo "=============================================="
echo "🎉 Deployment Complete!"
echo ""
echo "📊 Summary:"
echo "   Container App: $CONTAINER_APP_NAME"
echo "   Image: $FULL_IMAGE"
echo "   Status: Check responses above"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. If showing production mode ✅:"
echo "   → Proceed to configure Azure AI Foundry"
echo "   → Upload: docs/AZURE_AI_FOUNDRY_OPENAPI_SPEC.yaml"
echo "   → Test Assistant with: 'What is Neo4j?'"
echo ""
echo "2. If still showing mock_data ⚠️:"
echo "   → Wait 2-3 minutes for full restart"
echo "   → Check logs: az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP"
echo "   → Verify environment variables are set"
echo ""
echo "3. Monitor deployment:"
echo "   curl $HEALTH_URL | jq ."
echo ""
echo "📄 Full documentation: docs/ISSUE_4_IMPLEMENTATION_SUMMARY.md"
echo "=============================================="
