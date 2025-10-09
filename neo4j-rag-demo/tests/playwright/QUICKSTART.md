# Playwright Test Suite - Quick Start Guide

## 🚀 5-Minute Quick Start

### 1. Start Services (30 seconds)
```bash
cd /Users/ma3u/projects/ms-agentf-neo4j
docker-compose -f scripts/docker-compose.optimized.yml up -d
```

Wait 30 seconds for services to start.

### 2. Verify Services (10 seconds)
```bash
curl http://localhost:8501  # Streamlit ✓
curl http://localhost:8000/health  # RAG Service ✓
curl http://localhost:8001/health  # BitNet LLM ✓
curl http://localhost:7474  # Neo4j ✓
```

### 3. Run Tests (3 minutes)
```bash
cd neo4j-rag-demo/tests/playwright

# Already set up? Just run:
source venv/bin/activate && pytest test_smoke.py -v

# First time? Run setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Then run smoke tests:
pytest test_smoke.py -v
```

### Expected Output
```
====== test session starts ======
...
test_smoke.py::... PASSED [  7%]
...
===== 13 passed in 32.77s =====
```

## 📊 Test Coverage

- **Smoke Tests**: 13 tests (quick validation)
- **Chat Interface**: 20 tests (TC-7.*)
- **Document Upload**: 20 tests (TC-8.*)
- **Monitoring**: 30 tests (TC-9.*)
- **Integration**: 20 tests (TC-INT.*, TC-ERR.*)

**Total: 90+ tests**

## 🎯 Quick Commands

```bash
# Smoke tests only (30s)
pytest test_smoke.py -v

# All tests (~10-15 min)
pytest -v

# Specific category
pytest test_chat_interface.py -v
pytest test_document_upload.py -v

# With screenshots
pytest --screenshot=on

# Headed mode (see browser)
pytest --headed test_smoke.py
```

## ✅ Success Criteria

All 13 smoke tests should pass:
- ✅ Streamlit loads
- ✅ Chat input works
- ✅ Health cards visible
- ✅ Services reachable
- ✅ UI responsive

## 📁 Test Files

```
playwright/
├── conftest.py              # Fixtures & config
├── test_smoke.py            # 13 smoke tests ✅
├── test_chat_interface.py   # 20 chat tests
├── test_document_upload.py  # 20 upload tests
├── test_monitoring_dashboard.py  # 30 monitoring tests
├── test_integration.py      # 20 integration tests
├── pytest.ini               # Pytest config
├── requirements.txt         # Dependencies
├── run_tests.sh            # Test runner
└── README.md               # Full documentation
```

## 🐛 Troubleshooting

**Services not running?**
```bash
docker-compose -f scripts/docker-compose.optimized.yml ps
docker-compose -f scripts/docker-compose.optimized.yml up -d
```

**Tests fail to find elements?**
```bash
# Run in headed mode to see what's happening
pytest --headed --slowmo 1000 test_smoke.py
```

**Browser not installed?**
```bash
playwright install chromium
```

## 📖 Full Documentation

- See `README.md` for complete documentation
- See `TEST_REPORT.md` for execution results
- See issue #12 for original requirements

---

**Quick Links:**
- Issue #12: https://github.com/ma3u/neo4j-agentframework/issues/12
- Mockup: https://ma3u.github.io/neo4j-agentframework/

**Status**: ✅ Operational (13/13 smoke tests passing)
