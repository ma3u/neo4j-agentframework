# Playwright Test Suite for Issue #12

Comprehensive test suite for Streamlit Chat UI covering issues #7, #8, and #9.

## Test Coverage

### Chat Interface (TC-7.* - 20 tests)
- ✅ Chat functionality (TC-7.1 - TC-7.10)
- ✅ Settings configuration (TC-7.11 - TC-7.20)

### Document Upload (TC-8.* - 20 tests)
- ✅ Upload functionality (TC-8.1 - TC-8.10)
- ✅ Upload integration (TC-8.11 - TC-8.20)

### Monitoring Dashboard (TC-9.* - 30 tests)
- ✅ Service health monitoring (TC-9.1 - TC-9.10)
- ✅ Performance metrics (TC-9.11 - TC-9.20)
- ✅ Full statistics modal (TC-9.21 - TC-9.30)

### Integration & Error Handling (TC-INT.* & TC-ERR.* - 20 tests)
- ✅ Service integration (TC-INT.1 - TC-INT.10)
- ✅ Error handling (TC-ERR.1 - TC-ERR.10)

**Total: 90+ test cases**

## Prerequisites

1. **Services Running:**
   ```bash
   # Start all services
   docker-compose -f scripts/docker-compose.optimized.yml up -d

   # Verify services
   curl http://localhost:8501  # Streamlit
   curl http://localhost:8000/health  # RAG Service
   curl http://localhost:8001/health  # BitNet LLM
   curl http://localhost:7474  # Neo4j Browser
   ```

2. **Python Environment:**
   ```bash
   cd neo4j-rag-demo/tests/playwright
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Playwright Browsers:**
   ```bash
   playwright install chromium
   # Optional: playwright install firefox webkit
   ```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Chat interface tests only
pytest -m chat test_chat_interface.py

# Upload tests only
pytest -m upload test_document_upload.py

# Monitoring tests only
pytest -m monitoring test_monitoring_dashboard.py

# Integration tests
pytest -m integration test_integration.py

# Error handling tests
pytest -m error test_integration.py
```

### Run Individual Test Files
```bash
pytest test_chat_interface.py
pytest test_document_upload.py
pytest test_monitoring_dashboard.py
pytest test_integration.py
```

### Run Specific Test Classes
```bash
pytest test_chat_interface.py::TestChatFunctionality
pytest test_chat_interface.py::TestSettingsConfiguration
pytest test_document_upload.py::TestUploadFunctionality
pytest test_monitoring_dashboard.py::TestServiceHealthMonitoring
```

### Run Individual Tests
```bash
pytest test_chat_interface.py::TestChatFunctionality::test_tc_7_1_send_message
pytest test_document_upload.py::TestUploadFunctionality::test_tc_8_1_accepts_pdf
```

### Advanced Options
```bash
# Run with video recording
pytest --video=on

# Run with screenshots on failure
pytest --screenshot=only-on-failure

# Run with detailed output
pytest -vv

# Run in headed mode (see browser)
pytest --headed

# Run with specific browser
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# Run in slow motion (for debugging)
pytest --slowmo 1000

# Run with parallel execution
pytest -n auto
```

## Test Results

Results are saved to `test-results/`:
- `report.html` - HTML test report
- `junit.xml` - JUnit XML for CI/CD integration
- Videos and screenshots (if enabled)

### View HTML Report
```bash
open test-results/report.html  # macOS
xdg-open test-results/report.html  # Linux
start test-results/report.html  # Windows
```

## Test Data

Test files are created in `../test_files/`:
- PDFs (various sizes: 100KB, 1MB, 5MB, 10MB)
- TXT files
- MD files
- DOCX files

These are automatically cleaned up between test runs.

## Environment Variables

Configure via environment variables:
```bash
export STREAMLIT_URL=http://localhost:8501
export RAG_API_URL=http://localhost:8000
export TIMEOUT=30000  # milliseconds
```

Or create `.env` file:
```
STREAMLIT_URL=http://localhost:8501
RAG_API_URL=http://localhost:8000
TIMEOUT=30000
```

## Debugging Tests

### Interactive Mode
```bash
# Open Playwright Inspector
PWDEBUG=1 pytest test_chat_interface.py::test_tc_7_1_send_message
```

### Trace Viewer
```bash
# Generate trace
pytest --tracing=on

# View trace
playwright show-trace trace.zip
```

### Screenshots and Videos
```bash
# Enable for all tests
pytest --screenshot=on --video=on

# Results in test-results/
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium

      - name: Start services
        run: docker-compose -f scripts/docker-compose.optimized.yml up -d

      - name: Wait for services
        run: sleep 30

      - name: Run tests
        run: pytest

      - name: Upload results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: test-results/
```

## Test Maintenance

### Adding New Tests
1. Create test function following naming convention: `test_tc_X_Y_description`
2. Add appropriate marker decorator
3. Use fixtures for common setup
4. Follow existing patterns

### Updating Tests
1. Update test when UI changes
2. Keep test data in fixtures
3. Use descriptive assertions
4. Document test purpose

### Skipping Tests
```python
@pytest.mark.skip(reason="Service not available")
def test_tc_example():
    pass

@pytest.mark.skipif(condition, reason="Conditional skip")
def test_tc_example2():
    pass
```

## Known Issues

1. **Streamlit Rerun Timing**: Some tests may need longer waits for Streamlit reruns
2. **File Upload Timing**: Large file uploads may timeout on slow systems
3. **Service Health Checks**: Flaky if services are under load
4. **Modal Detection**: Streamlit modals may use different selectors in different versions

## Performance Notes

- Average test execution: 2-5 seconds per test
- Full suite: ~10-15 minutes
- Upload tests: Slower due to file I/O
- Integration tests: Slower due to service communication

## Support

For issues or questions:
- GitHub Issue: https://github.com/ma3u/neo4j-agentframework/issues/12
- Documentation: See main README.md
- Mockup Reference: https://ma3u.github.io/neo4j-agentframework/

---

**Generated with Claude Code** (https://claude.com/claude-code)
