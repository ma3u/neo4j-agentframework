# Cloud Deployment & Testing - Quick Start

**5-Minute Guide to Azure Enterprise Deployment + Local Testing**

## Prerequisites

```bash
# Install Azure CLI
brew install azure-cli  # macOS

# Login to Azure
az login
```

## Step 1: Deploy to Azure (30 minutes)

```bash
cd /Users/ma3u/projects/ms-agentf-neo4j
./scripts/azure-deploy-enterprise.sh
```

Creates:
- Neo4j Database in Azure
- RAG Service in Azure
- Key Vault, Storage, Monitoring
- Configuration file: `cloud-endpoints.env`

## Step 2: Run Tests Locally (5 minutes)

```bash
# Load cloud configuration
source cloud-endpoints.env

# Setup test environment
cd neo4j-rag-demo/tests/playwright
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Run cloud smoke tests
./test-cloud.sh smoke
```

Expected: ✅ 13 tests passed

## Step 3: Optional - Local Streamlit UI

```bash
# Connect local UI to cloud backend
source cloud-endpoints.env
cd streamlit_app
streamlit run app.py

# Opens: http://localhost:8501
# Uses: Cloud Neo4j + Cloud RAG
```

## Architecture

```
Azure Cloud:
  ├── Neo4j Database (2CPU, 8GB)
  └── RAG Service (4CPU, 8GB, auto-scale)

Local Machine:
  ├── Playwright Tests ✅
  ├── Streamlit UI (optional)
  └── BitNet LLM (optional)
```

## Cost

**$326/month** (cloud services only)
- Neo4j: $150
- RAG Service: $150
- Storage & Monitoring: $26

## Test Commands

```bash
source cloud-endpoints.env
cd neo4j-rag-demo/tests/playwright

./test-cloud.sh smoke        # Quick validation (30s)
./test-cloud.sh api          # API tests only
./test-cloud.sh performance  # Performance tests
./test-cloud.sh all          # Complete suite (~10 min)
```

## Monitoring

```bash
# View logs
az containerapp logs tail --name rag-service -g rg-neo4j-rag-enterprise

# Check status
az containerapp list -g rg-neo4j-rag-enterprise -o table

# View in portal
https://portal.azure.com → Application Insights → neo4j-rag-insights
```

## Documentation

- **Architecture**: `docs/AZURE_CLOUD_ARCHITECTURE.md`
- **Testing Guide**: `docs/CLOUD_TESTING_GUIDE.md`
- **Full Summary**: `docs/ENTERPRISE_DEPLOYMENT_SUMMARY.md`

---

**Status**: ✅ Ready for Enterprise Production
**Support**: See docs/ for detailed guides
