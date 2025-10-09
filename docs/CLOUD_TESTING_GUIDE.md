# Cloud Testing Guide

**Testing Local Playwright Against Azure-Hosted Neo4j + RAG Services**

## Overview

This guide explains how to run Playwright tests locally against Azure-hosted knowledge base services (Neo4j + RAG), enabling enterprise cloud deployment with local testing capabilities.

## Architecture

```
┌─────────────────────────────────────────┐
│         Azure Cloud (Production)        │
│                                          │
│  ┌────────────┐      ┌────────────┐    │
│  │   Neo4j    │◄─────┤  RAG       │    │
│  │  Database  │      │  Service   │    │
│  └────────────┘      └──────┬─────┘    │
│                              │          │
└──────────────────────────────┼──────────┘
                               │ HTTPS
                               │
┌──────────────────────────────▼──────────┐
│      Local Development Machine          │
│                                          │
│  ┌────────────────────────────────┐    │
│  │   Playwright Test Suite         │    │
│  │   (Running Locally)             │    │
│  └────────────────────────────────┘    │
│                                          │
│  Optional:                               │
│  ┌────────────┐      ┌────────────┐    │
│  │ Streamlit  │◄─────┤  BitNet    │    │
│  │    UI      │      │    LLM     │    │
│  └────────────┘      └────────────┘    │
└──────────────────────────────────────────┘
```

## Prerequisites

### 1. Azure Cloud Deployment

Deploy Neo4j + RAG to Azure:

```bash
cd /Users/ma3u/projects/ms-agentf-neo4j
./scripts/azure-deploy-enterprise.sh
```

This creates:
- Neo4j Database (Azure Container Apps)
- RAG Service (Azure Container Apps)
- Key Vault (credentials storage)
- Application Insights (monitoring)
- Configuration file: `cloud-endpoints.env`

### 2. Local Environment Setup

```bash
cd neo4j-rag-demo/tests/playwright

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### 3. Optional: Local Streamlit UI

```bash
# Terminal 1: Load cloud config
cd /Users/ma3u/projects/ms-agentf-neo4j
source cloud-endpoints.env

# Start Streamlit with cloud backend
cd neo4j-rag-demo/streamlit_app
streamlit run app.py

# Terminal 2: Keep BitNet running locally (optional)
docker run -p 8001:8001 bitnet-llm:local
```

## Test Configuration

### Environment Variables

The `cloud-endpoints.env` file contains:

```bash
# Cloud Services
export RAG_API_URL=https://rag-service-xxx.azurecontainerapps.io
export NEO4J_URI=neo4j+s://neo4j-rag-xxx.azurecontainerapps.io:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=<secure-password>

# Local Services (optional)
export STREAMLIT_URL=http://localhost:8501
export BITNET_URL=http://localhost:8001

# Test Mode
export TEST_MODE=cloud
```

### Load Configuration

```bash
# Load cloud endpoints
source ../../cloud-endpoints.env

# Verify configuration
echo $RAG_API_URL
echo $NEO4J_URI
```

## Running Cloud Tests

### Quick Start

```bash
cd neo4j-rag-demo/tests/playwright

# Load cloud config
source ../../cloud-endpoints.env

# Run cloud smoke tests
./test-cloud.sh smoke
```

### Test Categories

#### 1. API Tests (Direct Cloud Testing)
```bash
# Test cloud RAG API directly
./test-cloud.sh api

# Tests:
# - Health check
# - Statistics endpoint
# - Query execution
# - Document upload
```

**Output:**
```
✓ RAG Service healthy
  Response time: 106ms
  Memory: 494MB
✓ RAG Service stats retrieved
  Documents: 42
  Chunks: 1,247
✓ Query executed
  Sources found: 5
  Query time: 112ms
```

#### 2. UI Tests (Local Streamlit + Cloud Backend)
```bash
# Requires local Streamlit running
./test-cloud.sh ui

# Tests:
# - UI loads with cloud backend
# - Health cards show cloud status
# - End-to-end query through cloud
# - File upload to cloud storage
```

**Prerequisite:**
```bash
# Terminal 1: Start Streamlit
source ../../cloud-endpoints.env
cd streamlit_app && streamlit run app.py

# Terminal 2: Run tests
cd tests/playwright && ./test-cloud.sh ui
```

#### 3. Performance Tests
```bash
# Measure cloud performance
./test-cloud.sh performance

# Tests:
# - Query response time (<2s target)
# - Health check latency (<1s target)
# - Concurrent query handling
```

**Metrics:**
```
✓ Cloud query performance:
  Total time: 245ms
  API time: 112ms
✓ Cloud health check performance: 187ms
✓ Concurrent queries completed:
  Total time: 876ms
  Average per query: 175ms
```

#### 4. Resilience Tests
```bash
# Test error handling
./test-cloud.sh resilience

# Tests:
# - Invalid query handling
# - Large query handling
# - Sustained load (20 queries)
```

#### 5. All Tests
```bash
# Run complete cloud test suite
./test-cloud.sh all

# Runs all test categories (~5-10 minutes)
```

### Individual Tests

```bash
# Run specific test
pytest test_cloud_integration.py::TestCloudRAGAPI::test_cloud_rag_health -v --cloud

# Run test class
pytest test_cloud_integration.py::TestCloudPerformance -v --cloud

# Run with detailed output
pytest test_cloud_integration.py -vv --cloud
```

## Test Suite Structure

### Files

```
playwright/
├── conftest-cloud.py           # Cloud test configuration
├── test_cloud_integration.py   # Cloud-specific tests
├── test-cloud.sh              # Cloud test runner
├── test_smoke.py               # Smoke tests (local + cloud)
└── cloud-endpoints.env         # Generated by deployment
```

### Test Classes

#### TestCloudRAGAPI
Direct API testing against cloud RAG service:
- Health checks
- Statistics retrieval
- Query execution
- Document upload

#### TestCloudStreamlitUI
UI testing with cloud backend:
- UI loading with cloud services
- Health card status display
- End-to-end query workflows
- File upload to cloud

#### TestCloudPerformance
Performance benchmarking:
- Query response times
- Health check latency
- Concurrent request handling
- Sustained load testing

#### TestCloudResilience
Error handling and resilience:
- Invalid request handling
- Large query processing
- Sustained load management
- Error recovery

## Configuration Options

### Pytest Configuration

Use cloud-specific conftest:
```bash
# Symlink cloud config
ln -sf conftest-cloud.py conftest.py

# Or specify explicitly
pytest -c pytest-cloud.ini
```

### Test Markers

Tests use `@pytest.mark.cloud` decorator:

```python
@pytest.mark.cloud
def test_cloud_feature():
    # This test only runs in cloud mode
    pass
```

**Run only cloud tests:**
```bash
pytest -m cloud -v
```

**Skip cloud tests (local mode):**
```bash
pytest -m "not cloud" -v
```

### Timeouts

Cloud tests use longer timeouts:
- Local: 30 seconds
- Cloud: 60 seconds

```python
# Automatic timeout adjustment in conftest-cloud.py
TIMEOUT = 60000 if CLOUD_MODE else 30000
```

## Monitoring Cloud Tests

### Real-Time Logs

```bash
# RAG Service logs
az containerapp logs tail \
  --name rag-service \
  --resource-group rg-neo4j-rag-enterprise \
  --follow

# Neo4j logs
az containerapp logs tail \
  --name neo4j-rag \
  --resource-group rg-neo4j-rag-enterprise \
  --follow
```

### Application Insights

```bash
# Query recent requests
az monitor app-insights query \
  --app neo4j-rag-insights \
  --resource-group rg-neo4j-rag-enterprise \
  --analytics-query "requests | where timestamp > ago(1h) | summarize count() by name"

# Check errors
az monitor app-insights query \
  --app neo4j-rag-insights \
  --resource-group rg-neo4j-rag-enterprise \
  --analytics-query "exceptions | where timestamp > ago(1h) | take 10"
```

### Metrics Dashboard

Access metrics in Azure Portal:
1. Navigate to Application Insights: `neo4j-rag-insights`
2. View dashboards:
   - **Performance**: Response times, throughput
   - **Failures**: Error rates, exceptions
   - **Usage**: Request volumes, users
   - **Availability**: Uptime, health checks

## Troubleshooting

### Cloud Services Not Reachable

```bash
# Check deployment status
az containerapp list \
  --resource-group rg-neo4j-rag-enterprise \
  --output table

# Check specific app
az containerapp show \
  --name rag-service \
  --resource-group rg-neo4j-rag-enterprise \
  --query "properties.{Status:provisioningState,FQDN:configuration.ingress.fqdn}"

# Restart if needed
az containerapp revision restart \
  --name rag-service \
  --resource-group rg-neo4j-rag-enterprise
```

### Authentication Failures

```bash
# Verify Neo4j credentials from Key Vault
az keyvault secret show \
  --vault-name kv-neo4j-rag-xxxxx \
  --name neo4j-password \
  --query value -o tsv

# Test connection manually
cypher-shell -a neo4j+s://neo4j-rag-xxx.azurecontainerapps.io:7687 \
  -u neo4j -p <password> \
  "RETURN 1"
```

### Slow Performance

```bash
# Check container metrics
az containerapp show \
  --name rag-service \
  --resource-group rg-neo4j-rag-enterprise \
  --query "properties.template.{CPU:containers[0].resources.cpu,Memory:containers[0].resources.memory}"

# Scale up if needed
az containerapp update \
  --name rag-service \
  --resource-group rg-neo4j-rag-enterprise \
  --cpu 8.0 \
  --memory 16Gi
```

### Network Latency

```bash
# Test latency
time curl -s https://rag-service-xxx.azurecontainerapps.io/health

# Expected: <500ms
# If >1s, check:
# - Azure region (use closest to you)
# - Network connectivity
# - Service load
```

## Best Practices

### 1. Test Data Management

```bash
# Use unique IDs for test data
test_id = f"cloud_test_{int(time.time())}"

# Clean up after tests
@pytest.fixture(autouse=True)
def cleanup_test_data():
    yield
    # Cleanup code here
```

### 2. Network Resilience

```python
# Implement retries for network issues
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
```

### 3. Cost Optimization

```bash
# Stop services when not testing
az containerapp update \
  --name rag-service \
  --resource-group rg-neo4j-rag-enterprise \
  --min-replicas 0

# Restart for testing
az containerapp update \
  --name rag-service \
  --resource-group rg-neo4j-rag-enterprise \
  --min-replicas 1
```

### 4. Security

```bash
# Never commit credentials
echo "cloud-endpoints.env" >> .gitignore
echo "*.key" >> .gitignore
echo "*.pem" >> .gitignore

# Use environment variables
export NEO4J_PASSWORD=$(az keyvault secret show ...)
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Cloud Integration Tests

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  test-cloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Get Cloud Config
        run: |
          az keyvault secret download \
            --vault-name ${{ secrets.KEY_VAULT_NAME }} \
            --name cloud-config \
            --file cloud-endpoints.env

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: |
          cd neo4j-rag-demo/tests/playwright
          pip install -r requirements.txt
          playwright install chromium

      - name: Run Cloud Tests
        run: |
          source cloud-endpoints.env
          cd neo4j-rag-demo/tests/playwright
          ./test-cloud.sh smoke

      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: tests/playwright/test-results/
```

## Cost Monitoring

### Estimated Costs (Testing)

- **Active Testing** (8 hours/day): ~$11/day
- **Idle** (16 hours/day with min replicas=0): ~$2/day
- **Monthly** (moderate usage): ~$326/month

### Cost Optimization

```bash
# Development: Scale to zero when not in use
az containerapp update --min-replicas 0 --max-replicas 1

# Staging: Minimal scaling
az containerapp update --min-replicas 1 --max-replicas 3

# Production: Full scaling
az containerapp update --min-replicas 2 --max-replicas 10
```

## Summary

### Quick Reference

```bash
# Deploy to Azure
./scripts/azure-deploy-enterprise.sh

# Load configuration
source cloud-endpoints.env

# Run smoke tests
cd tests/playwright && ./test-cloud.sh smoke

# Run all tests
./test-cloud.sh all

# Monitor
az containerapp logs tail --name rag-service -g <resource-group> --follow
```

### Test Coverage

- ✅ **API Tests**: Direct cloud service testing
- ✅ **UI Tests**: Local Streamlit with cloud backend
- ✅ **Performance**: Query latency, concurrent load
- ✅ **Resilience**: Error handling, sustained load
- ✅ **Integration**: End-to-end workflows

### Benefits

- **Hybrid Architecture**: Cloud knowledge base + local testing
- **Cost Efficient**: Only pay for cloud storage/compute
- **Fast Iteration**: Test locally against production data
- **Production Parity**: Same services in dev and prod
- **Scalable**: Auto-scaling cloud infrastructure

---

**Architecture**: Hybrid Cloud Testing
**Local**: Playwright, Streamlit (optional), BitNet (optional)
**Cloud**: Neo4j Database, RAG Service, Monitoring
**Cost**: ~$326/month (cloud), $0/month (local testing)
