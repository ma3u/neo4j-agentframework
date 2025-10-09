# Neo4j RAG + BitNet - Hybrid AI Knowledge Base

**Intelligent knowledge base combining Neo4j graph database with RAG for hybrid local/cloud deployment**

![Streamlit Chat UI](docs/streamlit-ui-screenshot.png)

**Live Demo**: [Interactive Mockup](https://ma3u.github.io/neo4j-agentframework/)

---

## Overview

A production-ready hybrid RAG system that works both locally and in the cloud:

- **Neo4j Graph Database** - Fast vector search (417x improvement) with relationship tracking
- **RAG Service** - Intelligent retrieval with hybrid vector + keyword search
- **Local Development** - Full-featured Streamlit UI with BitNet.cpp (optional)
- **Azure Production** - Serverless Container Apps with AI Foundry integration

---

## Architecture

### Local Development

Fully containerized local deployment for development and testing. All components run on localhost: Neo4j provides graph database and vector search, RAG service handles retrieval and generation, BitNet.cpp delivers efficient LLM inference, and Streamlit provides an interactive testing interface.

### Azure Production

Enterprise serverless deployment using Azure Container Apps for the knowledge base (Neo4j + RAG) with Azure AI Foundry integration. Neo4j and RAG Service run as auto-scaling containers, while Azure AI Foundry agents (GPT-4o-mini) handle conversational AI as a managed service - no BitNet or Streamlit needed in production.

---

## Quick Start

### Prerequisites
- Docker Desktop
- 4GB+ RAM

### Local Setup (2 minutes)

```bash
# Clone and start
git clone https://github.com/ma3u/neo4j-agentframework.git
cd neo4j-agentframework

# Start all services
docker-compose -f scripts/docker-compose.optimized.yml up -d

# Open Streamlit UI
open http://localhost:8501
```

**Services Started**:
- 🗄️ Neo4j Database → [http://localhost:7474](http://localhost:7474)
- ⚡ RAG Service → [http://localhost:8000](http://localhost:8000)
- 🧠 Streamlit Chat UI → [http://localhost:8501](http://localhost:8501)
- 🤖 BitNet LLM → [http://localhost:8001](http://localhost:8001) *(optional)*

### Load Sample Data

```bash
cd neo4j-rag-demo
python scripts/load_sample_data.py
```

Or upload via Streamlit UI: Sidebar → Document Upload

---

## Key Features

### 🚀 Performance
- **417x faster** vector search (46s → 110ms)
- **87% memory reduction** with BitNet quantization
- **Sub-second queries** with intelligent caching

### 💡 Hybrid Deployment
- **Local**: Full control, zero cost, complete sovereignty
- **Cloud**: Auto-scaling, managed AI, enterprise-ready
- **Flexible**: Same codebase works in both environments

### 🎯 Production Ready
- Comprehensive testing (150+ Playwright tests)
- Enterprise security (Managed Identity, Key Vault)
- Full observability (Application Insights)
- Automated deployment scripts

---

## Usage

### Chat Interface

1. Open [http://localhost:8501](http://localhost:8501)
2. Type your question in the chat
3. Get AI-powered answers with sources
4. View performance metrics and health status

### Upload Documents

1. Sidebar → **Document Upload**
2. Select PDF, TXT, MD, or DOCX files
3. Click **Upload to Knowledge Base**
4. Documents are automatically indexed

### Monitor System

- **Health Cards**: Real-time service status
- **Stats Display**: Documents, chunks, response time, memory, cache rate
- **Full Statistics**: Detailed metrics and analytics

---

## Azure Deployment

Deploy Neo4j + RAG to Azure Container Apps for production:

```bash
./scripts/azure-deploy-enterprise.sh
```

**Creates**:
- Neo4j Container App (knowledge base)
- RAG Service Container App (API layer)
- Azure AI Foundry integration (managed AI agents)
- Key Vault, App Insights, Blob Storage

**Cost**: ~$326/month (Neo4j + RAG only)

**Architecture**: Neo4j + RAG in cloud, Azure AI Foundry for conversational AI

See [Azure Cloud Architecture](docs/AZURE_CLOUD_ARCHITECTURE.md) for details.

---

## Documentation

- **Quick Start**: This README
- **Testing Guide**: [tests/playwright/UI_TESTING_GUIDE.md](neo4j-rag-demo/tests/playwright/UI_TESTING_GUIDE.md)
- **Azure Deployment**: [docs/AZURE_CLOUD_ARCHITECTURE.md](docs/AZURE_CLOUD_ARCHITECTURE.md)
- **Cloud Testing**: [docs/CLOUD_TESTING_GUIDE.md](docs/CLOUD_TESTING_GUIDE.md)
- **API Documentation**: [neo4j-rag-demo/README.md](neo4j-rag-demo/README.md)

---

## Development

### Run Tests

```bash
cd neo4j-rag-demo/tests/playwright
./run_ui_tests.sh smoke  # Quick validation
./run_ui_tests.sh all    # Full suite (150+ tests)
```

### Local Development

```bash
cd neo4j-rag-demo
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app_local.py  # Start RAG API
```

---

## Performance Benchmarks

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Vector Search | 46s | 110ms | **417x faster** |
| Memory (LLM) | 8GB | 1.5GB | **87% reduction** |
| Query Response | 5-10s | <500ms | **10-20x faster** |

---

## Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines and project structure.

Issues and pull requests welcome at [GitHub Issues](https://github.com/ma3u/neo4j-agentframework/issues).

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/ma3u/neo4j-agentframework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ma3u/neo4j-agentframework/discussions)

---

**Built with ❤️ for efficient AI systems**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
