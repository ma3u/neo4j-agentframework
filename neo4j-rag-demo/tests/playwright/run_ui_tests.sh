#!/bin/bash
# Comprehensive UI Test Runner
# Runs Playwright UI tests for Streamlit application

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "======================================"
echo "UI Testing Suite - Playwright"
echo "======================================"
echo ""

# Check if Streamlit is running
echo "1. Checking Streamlit service..."
if curl -s -f http://localhost:8501 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Streamlit is running on port 8501"
else
    echo -e "${RED}✗${NC} Streamlit is NOT running"
    echo ""
    echo "Please start Streamlit first:"
    echo "  cd streamlit_app"
    echo "  streamlit run app.py"
    exit 1
fi

echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -q -r requirements.txt > /dev/null 2>&1
    playwright install chromium > /dev/null 2>&1
    touch venv/.installed
fi

echo "2. Test environment ready"
echo ""

# Parse test mode
TEST_MODE=${1:-"all"}
VERBOSE=${2:-""}

echo "======================================"
echo "Running UI Tests: $TEST_MODE"
echo "======================================"
echo ""

case $TEST_MODE in
    "component"|"components")
        echo "Running Component Tests..."
        pytest test_ui_components.py -v $VERBOSE
        ;;

    "header")
        echo "Running Header Tests..."
        pytest test_ui_components.py::TestHeaderComponents -v $VERBOSE
        ;;

    "health")
        echo "Running Health Card Tests..."
        pytest test_ui_components.py::TestHealthCards -v $VERBOSE
        ;;

    "chat")
        echo "Running Chat Interface Tests..."
        pytest test_ui_components.py::TestChatInterface -v $VERBOSE
        ;;

    "sidebar")
        echo "Running Sidebar Control Tests..."
        pytest test_ui_components.py::TestSidebarControls -v $VERBOSE
        ;;

    "upload")
        echo "Running File Upload Tests..."
        pytest test_ui_components.py::TestFileUploader -v $VERBOSE
        ;;

    "stats")
        echo "Running Stats Display Tests..."
        pytest test_ui_components.py::TestStatsDisplay -v $VERBOSE
        ;;

    "responsive")
        echo "Running Responsive Design Tests..."
        pytest test_ui_components.py::TestResponsiveDesign -v $VERBOSE
        ;;

    "accessibility"|"a11y")
        echo "Running Accessibility Tests..."
        pytest test_ui_components.py::TestAccessibility -v $VERBOSE
        ;;

    "errors")
        echo "Running Error Handling Tests..."
        pytest test_ui_components.py::TestErrorHandling -v $VERBOSE
        ;;

    "interactive")
        echo "Running Interactive UI Explorer..."
        python interactive_ui_test.py
        ;;

    "interactive-headed")
        echo "Running Interactive UI Explorer (Browser Visible)..."
        python interactive_ui_test.py --interactive
        ;;

    "visual")
        echo "Running Visual Regression Tests..."
        if [ -d "baseline_screenshots" ] && [ "$(ls -A baseline_screenshots)" ]; then
            echo "Comparing against baseline..."
            python visual_regression_test.py --compare
        else
            echo "No baseline found. Creating baseline..."
            python visual_regression_test.py --baseline
            echo ""
            echo -e "${YELLOW}Baseline created!${NC}"
            echo "Run './run_ui_tests.sh visual' again to compare changes"
        fi
        ;;

    "baseline")
        echo "Capturing Visual Baseline..."
        python visual_regression_test.py --baseline
        echo ""
        echo -e "${GREEN}Baseline captured!${NC}"
        echo "Run './run_ui_tests.sh visual' to compare changes"
        ;;

    "screenshot")
        echo "Capturing UI Screenshot..."
        python interactive_ui_test.py --screenshot ui_current_state.png
        echo ""
        echo -e "${GREEN}Screenshot saved: ui_current_state.png${NC}"
        ;;

    "smoke")
        echo "Running Smoke Tests (Quick Validation)..."
        pytest test_ui_components.py::TestHeaderComponents::test_app_title_display \
               test_ui_components.py::TestHealthCards::test_health_cards_layout \
               test_ui_components.py::TestChatInterface::test_chat_input_placeholder \
               test_ui_components.py::TestSidebarControls::test_sidebar_visibility \
               -v $VERBOSE
        ;;

    "all")
        echo "Running ALL UI Tests..."
        echo ""
        echo "1/3: Component Tests..."
        pytest test_ui_components.py -v $VERBOSE

        echo ""
        echo "2/3: Interactive Exploration..."
        python interactive_ui_test.py --headless

        echo ""
        echo "3/3: Visual Regression..."
        if [ -d "baseline_screenshots" ] && [ "$(ls -A baseline_screenshots)" ]; then
            python visual_regression_test.py --compare
        else
            echo "Skipping visual regression (no baseline)"
            echo "Run './run_ui_tests.sh baseline' to create baseline"
        fi
        ;;

    *)
        echo -e "${RED}Unknown test mode: $TEST_MODE${NC}"
        echo ""
        echo "Usage: $0 [mode] [options]"
        echo ""
        echo "Modes:"
        echo "  component     - Run all component tests"
        echo "  header        - Header component tests"
        echo "  health        - Health card tests"
        echo "  chat          - Chat interface tests"
        echo "  sidebar       - Sidebar control tests"
        echo "  upload        - File upload tests"
        echo "  stats         - Statistics display tests"
        echo "  responsive    - Responsive design tests"
        echo "  accessibility - Accessibility tests"
        echo "  errors        - Error handling tests"
        echo ""
        echo "  interactive   - Interactive UI explorer (headless)"
        echo "  interactive-headed - Interactive explorer (browser visible)"
        echo ""
        echo "  visual        - Visual regression testing"
        echo "  baseline      - Capture visual baseline"
        echo "  screenshot    - Capture single screenshot"
        echo ""
        echo "  smoke         - Quick smoke tests"
        echo "  all           - Run complete test suite"
        echo ""
        echo "Options:"
        echo "  -v            - Verbose output"
        echo "  -vv           - Very verbose output"
        echo ""
        echo "Examples:"
        echo "  $0 smoke"
        echo "  $0 component -v"
        echo "  $0 interactive-headed"
        echo "  $0 all"
        exit 1
        ;;
esac

TEST_EXIT_CODE=$?

echo ""
echo "======================================"
echo "Test Results"
echo "======================================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Tests PASSED!${NC}"
else
    echo -e "${RED}❌ Tests FAILED!${NC}"
fi

echo ""
echo "Screenshots saved to: test-results/"
echo ""

exit $TEST_EXIT_CODE
