# UI Testing Quick Start

**5-Minute Guide to Local UI Testing with Playwright MCP Server**

## Setup (One-Time)

```bash
# Terminal 1: Start Streamlit
cd streamlit_app
streamlit run app.py

# Terminal 2: Setup tests
cd tests/playwright
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Run Tests (30 seconds)

```bash
# Quick smoke test (4 tests, ~15s)
./run_ui_tests.sh smoke

# All component tests (40+ tests, ~2 min)
./run_ui_tests.sh component

# Interactive UI explorer
./run_ui_tests.sh interactive
```

## Test Output

```
✓ Streamlit is running on port 8501

Running Smoke Tests...
test_ui_components.py::TestHeaderComponents::test_app_title_display PASSED
test_ui_components.py::TestHealthCards::test_health_cards_layout PASSED
test_ui_components.py::TestChatInterface::test_chat_input_placeholder PASSED
test_ui_components.py::TestSidebarControls::test_sidebar_visibility PASSED

========================
4 passed in 13.65s
========================

✅ Tests PASSED!
```

## Common Commands

```bash
# Smoke tests (fastest)
./run_ui_tests.sh smoke

# Specific components
./run_ui_tests.sh chat
./run_ui_tests.sh sidebar
./run_ui_tests.sh health

# Interactive mode (browser visible)
./run_ui_tests.sh interactive-headed

# Visual regression
./run_ui_tests.sh baseline    # First time
./run_ui_tests.sh visual      # Check for changes

# Everything
./run_ui_tests.sh all
```

## Interactive Scripts

```bash
# Automated UI analysis
python interactive_ui_test.py

# Keep browser open for manual testing
python interactive_ui_test.py --interactive

# Take screenshot
python interactive_ui_test.py --screenshot ui.png
```

## Test Coverage

- ✅ 40+ Component Tests
- ✅ Interactive UI Explorer
- ✅ Visual Regression Testing
- ✅ Responsive Design (4 viewports)
- ✅ Accessibility Testing
- ✅ Error Handling

## File Structure

```
tests/playwright/
├── run_ui_tests.sh              # Test runner ⭐
├── test_ui_components.py        # 40+ tests
├── interactive_ui_test.py       # UI explorer
├── visual_regression_test.py    # Visual tests
└── UI_TESTING_GUIDE.md         # Full docs
```

## Troubleshooting

**Streamlit not running?**
```bash
cd streamlit_app && streamlit run app.py
```

**Element not found?**
```bash
# Run in headed mode to see what's happening
pytest test_ui_components.py --headed
```

**Need verbose output?**
```bash
./run_ui_tests.sh component -vv
```

## Documentation

- **Quick Start**: This file
- **Full Guide**: `UI_TESTING_GUIDE.md`
- **Summary**: `LOCAL_UI_TESTING_SUMMARY.md`
- **Issue #12**: Original test requirements

---

**Status**: ✅ Ready
**Tests**: 40+ UI component tests
**Time**: ~2 minutes (full suite)
**MCP Server**: Playwright integration
