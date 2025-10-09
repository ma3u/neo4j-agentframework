#!/bin/bash
# Cloud Testing Script
# Runs Playwright tests against Azure-hosted services

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "======================================"
echo "Cloud Testing - Playwright Test Suite"
echo "======================================"
echo ""

# Check for cloud configuration
if [ ! -f "../../cloud-endpoints.env" ]; then
    echo -e "${RED}ERROR: Cloud configuration not found${NC}"
    echo "Expected file: cloud-endpoints.env"
    echo ""
    echo "Please deploy to Azure first:"
    echo "  cd /Users/ma3u/projects/ms-agentf-neo4j"
    echo "  ./scripts/azure-deploy-enterprise.sh"
    exit 1
fi

# Load cloud configuration
echo "Loading cloud configuration..."
source ../../cloud-endpoints.env

echo -e "${GREEN}✓ Cloud configuration loaded${NC}"
echo ""
echo "Cloud Endpoints:"
echo "  RAG Service:  $RAG_API_URL"
echo "  Neo4j:        $NEO4J_URI"
echo "  Streamlit:    $STREAMLIT_URL (local)"
echo ""

# Verify cloud services are reachable
echo "Verifying cloud services..."

check_service() {
    local name=$1
    local url=$2

    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is reachable"
        return 0
    else
        echo -e "${RED}✗${NC} $name is NOT reachable"
        return 1
    fi
}

ALL_HEALTHY=true
check_service "RAG Service" "$RAG_HEALTH_URL" || ALL_HEALTHY=false

if [ "$ALL_HEALTHY" = false ]; then
    echo ""
    echo -e "${RED}ERROR: Cloud services not reachable${NC}"
    echo "Please check Azure deployment status:"
    echo "  az containerapp list -g $AZURE_RESOURCE_GROUP -o table"
    exit 1
fi

echo ""
echo -e "${GREEN}All cloud services reachable${NC}"
echo ""

# Check if local Streamlit is running (optional)
if curl -s -f "$STREAMLIT_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Local Streamlit UI is running"
    LOCAL_UI=true
else
    echo -e "${YELLOW}!${NC} Local Streamlit UI is NOT running (optional)"
    echo "  To test UI: cd streamlit_app && streamlit run app.py"
    LOCAL_UI=false
fi

echo ""

# Setup test environment
echo "Setting up test environment..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓ Test environment ready${NC}"
echo ""

# Run tests based on argument
TEST_MODE=${1:-"all"}

echo "======================================"
echo "Running Cloud Tests: $TEST_MODE"
echo "======================================"
echo ""

case $TEST_MODE in
    "api")
        echo "Testing cloud API only..."
        pytest test_cloud_integration.py::TestCloudRAGAPI -v --cloud
        ;;

    "ui")
        if [ "$LOCAL_UI" = false ]; then
            echo -e "${RED}ERROR: Local UI not running${NC}"
            echo "Start with: cd streamlit_app && streamlit run app.py"
            exit 1
        fi
        echo "Testing UI with cloud backend..."
        pytest test_cloud_integration.py::TestCloudStreamlitUI -v --cloud
        ;;

    "performance")
        echo "Running performance tests..."
        pytest test_cloud_integration.py::TestCloudPerformance -v --cloud
        ;;

    "resilience")
        echo "Running resilience tests..."
        pytest test_cloud_integration.py::TestCloudResilience -v --cloud
        ;;

    "smoke")
        echo "Running cloud smoke tests..."
        pytest test_cloud_integration.py::TestCloudRAGAPI::test_cloud_rag_health \
               test_cloud_integration.py::TestCloudRAGAPI::test_cloud_rag_stats \
               test_cloud_integration.py::TestCloudRAGAPI::test_cloud_rag_query \
               -v --cloud
        ;;

    "all")
        echo "Running ALL cloud tests..."
        pytest test_cloud_integration.py -v --cloud
        ;;

    *)
        echo -e "${RED}Unknown test mode: $TEST_MODE${NC}"
        echo "Usage: $0 [api|ui|performance|resilience|smoke|all]"
        exit 1
        ;;
esac

TEST_EXIT_CODE=$?

echo ""
echo "======================================"
echo "Cloud Test Results"
echo "======================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

echo ""
echo "Cloud Monitoring:"
echo "  Logs: az containerapp logs tail --name rag-service -g $AZURE_RESOURCE_GROUP"
echo "  Metrics: Open Azure Portal > Application Insights"
echo ""

exit $TEST_EXIT_CODE
