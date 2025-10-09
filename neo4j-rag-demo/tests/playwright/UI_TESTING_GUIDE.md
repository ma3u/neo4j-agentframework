# Local UI Testing with Playwright MCP Server

**Comprehensive Guide to Interactive UI Testing for Streamlit Application**

## Overview

This guide covers local UI testing using Playwright with MCP (Model Context Protocol) server capabilities for interactive, visual, and component-level testing of the Streamlit Chat UI.

## Architecture

```
┌─────────────────────────────────────────┐
│     Local Development Machine           │
│                                          │
│  ┌────────────────────────────────┐    │
│  │   Streamlit UI                  │    │
│  │   http://localhost:8501         │    │
│  └──────────┬─────────────────────┘    │
│             │                            │
│  ┌──────────▼─────────────────────┐    │
│  │   Playwright MCP Server         │    │
│  │   - Browser Automation          │    │
│  │   - Interactive Testing         │    │
│  │   - Visual Regression           │    │
│  │   - Component Testing           │    │
│  └────────────────────────────────┘    │
│                                          │
│  Optional Cloud Backend:                 │
│  ├─ RAG Service (Azure)                 │
│  └─ Neo4j DB (Azure)                    │
└──────────────────────────────────────────┘
```

## Test Suite Components

### 1. Component Tests (`test_ui_components.py`)

Comprehensive UI component testing covering:

**Header Components** (3 tests)
- Application title display
- Developer mode indicator
- Header navigation elements

**Health Cards** (4 tests)
- Layout verification
- Status indicators (green/red/yellow)
- Response time display
- Port number display (7687, 8000, 8001)

**Chat Interface** (6 tests)
- Input placeholder text
- Input enabled state
- Message container
- Send message interaction
- Message styling (user vs assistant)

**Sidebar Controls** (8 tests)
- Sidebar visibility
- Section structure
- Max results slider
- Similarity threshold slider
- BitNet toggle
- Temperature slider
- Display toggles (sources, performance, timestamps)

**File Uploader** (4 tests)
- Component existence
- Label and help text
- Upload button interaction

**Statistics Display** (3 tests)
- Compact stats visibility
- Full statistics button
- Metric formatting

**Responsive Design** (4 tests)
- Desktop layout (1920x1080)
- Laptop layout (1366x768)
- Tablet layout (768px)
- Mobile layout (375px)

**Accessibility** (3 tests)
- Keyboard navigation
- Enter key submit
- Heading structure

**Error Handling** (2 tests)
- Empty message rejection
- Service offline handling

**Total: 40+ UI component tests**

### 2. Interactive UI Explorer (`interactive_ui_test.py`)

Interactive testing tool for manual exploration:

```bash
# Run automated exploration
python interactive_ui_test.py

# Interactive mode (keep browser open)
python interactive_ui_test.py --interactive

# Take screenshot only
python interactive_ui_test.py --screenshot my_screenshot.png

# Use custom URL
python interactive_ui_test.py --url http://localhost:8502
```

**Features:**
- ✅ UI structure analysis
- ✅ Health card inspection
- ✅ Chat interaction testing
- ✅ File upload UI verification
- ✅ Responsive design testing
- ✅ Screenshot capture
- ✅ Interactive browser mode

**Output Example:**
```
🔍 UI STRUCTURE ANALYSIS
📋 TITLE: Neo4j RAG + BitNet Chat
📁 SIDEBAR: ✓ Sidebar present
💬 CHAT INPUT: ✓ Chat input found
🏥 HEALTH CARDS:
   ✓ Neo4j card found
   ✓ RAG card found
   ✓ BitNet card found
🎚️  CONTROLS:
   Sliders: 3
   Checkboxes: 4
   File uploader: ✓
```

### 3. Visual Regression Testing (`visual_regression_test.py`)

Automated visual diff detection:

```bash
# Capture baseline screenshots
python visual_regression_test.py --baseline

# Compare current state to baseline
python visual_regression_test.py --compare
```

**Captured Views:**
- Full page screenshot
- Header only
- Health cards section
- Chat interface
- Sidebar
- Mobile view (375x667)

**Diff Detection:**
- Pixel-by-pixel comparison
- Difference percentage calculation
- Red highlighting of changes
- Saved diff images

**Output:**
```
🔍 COMPARING SCREENSHOTS
   Comparing 01_full_page.png...
      ✅ MATCH
   Comparing 02_header.png...
      ⚠️  MINOR DIFF (0.23% difference)
   Comparing 03_health_cards.png...
      ❌ DIFFERENT (2.45% difference)

📊 SUMMARY
   ✅ MATCH          01_full_page.png      (0.00%)
   ⚠️  MINOR DIFF     02_header.png        (0.23%)
   ❌ DIFFERENT      03_health_cards.png   (2.45%)
```

## Running Tests

### Prerequisites

```bash
# Ensure Streamlit is running
cd streamlit_app
streamlit run app.py

# In another terminal, setup test environment
cd tests/playwright
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Quick Start

```bash
# Run all UI component tests
pytest test_ui_components.py -v

# Run specific component class
pytest test_ui_components.py::TestHealthCards -v

# Run interactive explorer
python interactive_ui_test.py

# Capture visual baseline
python visual_regression_test.py --baseline
```

### Test Categories

#### 1. Component Tests
```bash
# Run all component tests
pytest test_ui_components.py -v

# Run by category
pytest test_ui_components.py::TestHeaderComponents -v
pytest test_ui_components.py::TestHealthCards -v
pytest test_ui_components.py::TestChatInterface -v
pytest test_ui_components.py::TestSidebarControls -v
pytest test_ui_components.py::TestFileUploader -v
pytest test_ui_components.py::TestStatsDisplay -v
pytest test_ui_components.py::TestResponsiveDesign -v
pytest test_ui_components.py::TestAccessibility -v
pytest test_ui_components.py::TestErrorHandling -v

# Run specific test
pytest test_ui_components.py::TestChatInterface::test_send_message_interaction -v
```

#### 2. Interactive Exploration
```bash
# Automated exploration
python interactive_ui_test.py

# Keep browser open for manual testing
python interactive_ui_test.py --interactive

# Headless mode (no browser window)
python interactive_ui_test.py --headless

# Custom URL
python interactive_ui_test.py --url http://localhost:8502

# Screenshot only
python interactive_ui_test.py --screenshot ui_state.png
```

#### 3. Visual Regression
```bash
# Step 1: Capture baseline (run once)
python visual_regression_test.py --baseline

# Step 2: Make UI changes, then compare
python visual_regression_test.py --compare

# Re-baseline after approved changes
python visual_regression_test.py --baseline
```

### Test Runner Script

```bash
# Run complete UI test suite
./run_ui_tests.sh

# Run only component tests
./run_ui_tests.sh component

# Run only interactive tests
./run_ui_tests.sh interactive

# Run only visual regression
./run_ui_tests.sh visual

# Run with verbose output
./run_ui_tests.sh -v
```

## Test Results

### Component Test Output

```
test_ui_components.py::TestHeaderComponents::test_app_title_display PASSED
test_ui_components.py::TestHealthCards::test_health_cards_layout PASSED
✓ Found Neo4j health card
✓ Found RAG health card
✓ Found BitNet health card

test_ui_components.py::TestChatInterface::test_send_message_interaction PASSED
✓ Message sent and displayed: UI Test Message 1696867234

test_ui_components.py::TestResponsiveDesign::test_desktop_layout PASSED
✓ Desktop layout (1920x1080) working

========================
40 passed in 125.45s
========================
```

### Interactive Test Output

```
🚀 Starting Playwright UI Explorer...
✅ Streamlit app loaded!

🔍 UI STRUCTURE ANALYSIS
   ✓ 3 headings found
   ✓ Sidebar present with 10 sections
   ✓ Chat input found
   ✓ 3 health cards found
   ✓ 3 sliders, 4 checkboxes

💬 CHAT INTERACTION TEST
   ✅ Message appeared in chat!
   Total messages: 2

📱 RESPONSIVE DESIGN TEST
   ✅ Desktop (1920x1080): Working
   ✅ Laptop (1366x768): Working
   ✅ Tablet (768x1024): Working
   ✅ Mobile (375x667): Working

✅ UI TESTING COMPLETE
```

## Advanced Features

### 1. Debugging Tests

```bash
# Run with Playwright Inspector
PWDEBUG=1 pytest test_ui_components.py::TestChatInterface::test_send_message_interaction

# Run in headed mode (see browser)
pytest test_ui_components.py --headed

# Run with video recording
pytest test_ui_components.py --video=on

# Slow down for observation
pytest test_ui_components.py --slowmo 1000
```

### 2. Screenshot Capture

```python
# In test code
def test_with_screenshot(streamlit_page: Page):
    # Take screenshot at any point
    streamlit_page.screenshot(path="debug_screenshot.png")

    # Screenshot specific element
    element = streamlit_page.locator('[data-testid="stChatMessage"]')
    element.screenshot(path="chat_messages.png")

    # Full page screenshot
    streamlit_page.screenshot(path="full_page.png", full_page=True)
```

### 3. Network Monitoring

```python
def test_with_network_monitoring(page: Page):
    # Monitor network requests
    requests = []

    def log_request(request):
        requests.append({
            "url": request.url,
            "method": request.method
        })

    page.on("request", log_request)

    # Navigate and interact
    page.goto("http://localhost:8501")

    # Check requests
    api_requests = [r for r in requests if "/query" in r["url"]]
    assert len(api_requests) > 0
```

### 4. Console Monitoring

```python
def test_with_console_monitoring(page: Page):
    # Monitor console messages
    console_messages = []

    def log_console(msg):
        console_messages.append(msg.text)

    page.on("console", log_console)

    # Run test
    page.goto("http://localhost:8501")

    # Check for errors
    errors = [m for m in console_messages if "error" in m.lower()]
    assert len(errors) == 0
```

## Test Data

### PDF Test Files

```python
def test_with_pdf(create_test_pdf):
    # Create test PDF
    pdf_file = create_test_pdf(
        "test_document.pdf",
        size_kb=500,
        content="Custom test content"
    )

    # Use in test
    file_input.set_input_files(pdf_file)
```

### TXT Test Files

```python
def test_with_txt(create_test_txt):
    # Create test TXT
    txt_file = create_test_txt(
        "test_doc.txt",
        content="Test content for upload"
    )

    # Use in test
    file_input.set_input_files(txt_file)
```

## Integration with MCP Server

The Playwright MCP server provides:

### Browser Automation
- Headless or headed browser control
- Multiple browser support (Chromium, Firefox, WebKit)
- Mobile device emulation
- Network condition simulation

### Element Interaction
- Click, type, hover, drag
- Keyboard shortcuts
- File uploads
- Form submissions

### State Inspection
- DOM querying
- Element attributes
- CSS properties
- JavaScript execution

### Screenshot & Video
- Full page screenshots
- Element screenshots
- Video recording
- Trace generation

## CI/CD Integration

### GitHub Actions Example

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  ui-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd tests/playwright
          pip install -r requirements.txt
          playwright install chromium

      - name: Start Streamlit
        run: |
          cd streamlit_app
          streamlit run app.py &
          sleep 10

      - name: Run UI tests
        run: |
          cd tests/playwright
          pytest test_ui_components.py -v

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots
          path: tests/playwright/test-results/
```

## Troubleshooting

### Common Issues

**1. Streamlit not running**
```bash
# Check if Streamlit is running
curl http://localhost:8501

# Start if needed
cd streamlit_app && streamlit run app.py
```

**2. Element not found**
```python
# Increase timeout
element.wait_for(timeout=30000)

# Check if element exists first
if element.count() > 0:
    element.click()
```

**3. Timing issues**
```python
# Wait for network to be idle
page.wait_for_load_state("networkidle")

# Wait for specific element
page.wait_for_selector('[data-testid="stChatMessage"]')

# Add explicit wait
time.sleep(2)
```

**4. Visual regression false positives**
```bash
# Re-capture baseline after approved changes
python visual_regression_test.py --baseline

# Adjust difference threshold in code
if diff_percent > 5.0:  # More tolerant
    differences_found = True
```

## Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- Add docstrings with test IDs (TC-7.1, etc.)
- Keep tests independent

### 2. Assertions
```python
# Good: Specific assertions
expect(element).to_be_visible()
expect(element).to_have_text("Expected text")

# Bad: Generic assertions
assert element.count() > 0
```

### 3. Waiting
```python
# Good: Explicit waits
page.wait_for_selector('[data-testid="stChatMessage"]')

# Bad: Sleep
time.sleep(5)  # Only when necessary
```

### 4. Screenshots
- Capture on failure for debugging
- Use descriptive filenames
- Clean up after tests

### 5. Cleanup
```python
@pytest.fixture
def test_with_cleanup():
    # Setup
    yield
    # Cleanup
    page.locator('button:has-text("Clear Chat")').click()
```

## Performance

### Test Execution Times

| Test Suite | Tests | Time |
|------------|-------|------|
| Header Components | 3 | ~8s |
| Health Cards | 4 | ~12s |
| Chat Interface | 6 | ~25s |
| Sidebar Controls | 8 | ~30s |
| File Uploader | 4 | ~15s |
| Stats Display | 3 | ~10s |
| Responsive Design | 4 | ~15s |
| Accessibility | 3 | ~10s |
| Error Handling | 2 | ~8s |
| **Total** | **40+** | **~125s** |

### Optimization Tips

```python
# Run tests in parallel
pytest test_ui_components.py -n auto

# Run only fast tests
pytest -m "not slow" test_ui_components.py

# Skip slow tests in development
pytest -m "not slow" -v
```

## Summary

### Test Coverage

✅ **40+ Component Tests**
✅ **Interactive UI Explorer**
✅ **Visual Regression Testing**
✅ **Responsive Design Testing**
✅ **Accessibility Testing**
✅ **Error Handling Testing**

### Quick Commands

```bash
# Component tests
pytest test_ui_components.py -v

# Interactive exploration
python interactive_ui_test.py --interactive

# Visual regression
python visual_regression_test.py --compare

# Complete suite
./run_ui_tests.sh
```

---

**Testing Framework**: Playwright + MCP Server
**Coverage**: 40+ UI component tests
**Execution Time**: ~2 minutes (full suite)
**Visual Regression**: Automated screenshot comparison
**Interactive Mode**: Browser-based exploration
