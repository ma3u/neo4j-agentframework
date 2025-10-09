#!/bin/bash
# Playwright Test Runner for Issue #12

set -e

echo "=== Playwright Test Suite for Issue #12 ==="
echo "Testing Streamlit Chat UI (Issues #7, #8, #9)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check services
echo "1. Checking service health..."

check_service() {
    local name=$1
    local url=$2

    if curl -s -f "$url" > /dev/null; then
        echo -e "${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $name is NOT running"
        return 1
    fi
}

SERVICES_OK=true
check_service "Streamlit" "http://localhost:8501" || SERVICES_OK=false
check_service "RAG Service" "http://localhost:8000/health" || SERVICES_OK=false
check_service "BitNet LLM" "http://localhost:8001/health" || SERVICES_OK=false
check_service "Neo4j" "http://localhost:7474" || SERVICES_OK=false

if [ "$SERVICES_OK" = false ]; then
    echo ""
    echo -e "${RED}ERROR: Some services are not running${NC}"
    echo "Please start services first:"
    echo "  docker-compose -f scripts/docker-compose.optimized.yml up -d"
    exit 1
fi

echo ""
echo "2. Setting up test environment..."

# Activate venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create test files directory
mkdir -p ../test_files

# Create test results directory
mkdir -p test-results

echo ""
echo "3. Running tests..."
echo ""

# Run tests with different modes
if [ "$1" = "quick" ]; then
    echo "Running quick test (chat interface only)..."
    pytest test_chat_interface.py::TestChatFunctionality -v
elif [ "$1" = "chat" ]; then
    echo "Running chat interface tests..."
    pytest test_chat_interface.py -v
elif [ "$1" = "upload" ]; then
    echo "Running upload tests..."
    pytest test_document_upload.py -v
elif [ "$1" = "monitoring" ]; then
    echo "Running monitoring dashboard tests..."
    pytest test_monitoring_dashboard.py -v
elif [ "$1" = "integration" ]; then
    echo "Running integration tests..."
    pytest test_integration.py -v
elif [ "$1" = "all" ] || [ -z "$1" ]; then
    echo "Running ALL tests..."
    pytest -v --html=test-results/report.html --self-contained-html
else
    echo "Unknown test mode: $1"
    echo "Usage: $0 [quick|chat|upload|monitoring|integration|all]"
    exit 1
fi

TEST_EXIT_CODE=$?

echo ""
echo "=== Test Results ==="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Tests passed!${NC}"
else
    echo -e "${RED}✗ Tests failed!${NC}"
fi

echo ""
echo "Test report: test-results/report.html"
echo ""

# Open report if all tests run
if [ "$1" = "all" ] || [ -z "$1" ]; then
    echo "Opening test report..."
    if command -v open &> /dev/null; then
        open test-results/report.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open test-results/report.html
    fi
fi

exit $TEST_EXIT_CODE
