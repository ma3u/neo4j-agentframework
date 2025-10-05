# Azure AI Assistant Configuration Guide

**Step-by-step configuration for Assistant ID: `asst_LHQBXYvRhnbFo7KQ7IRbVXRR`**

---

## 🎯 Your Current Assistant

**From your screenshot:**
- ✅ **Assistant ID**: `asst_LHQBXYvRhnbFo7KQ7IRbVXRR`
- ✅ **Name**: `Assistant347`
- ✅ **Deployment**: `gpt-4o-mini (version:2024-07-18)`
- ✅ **Tools**: File search available, Code interpreter available
- ❌ **Status**: Not configured with Neo4j RAG yet

---

## 🚀 Quick Configuration (Automated)

**Run the configuration script:**

```bash
# Configure assistant with Neo4j RAG tools
python scripts/configure-azure-assistant.py
```

**What it does:**
- Updates instructions for Neo4j RAG usage
- Adds 4 custom tools for knowledge base access
- Sets metadata (version, performance metrics)
- Configures optimal settings

**Time**: 30 seconds

---

## 📝 Manual Configuration (Step-by-Step)

### Step 1: Update Instructions

**In Azure AI Foundry Playground → Instructions field**, paste this:

```
You are an intelligent AI assistant with access to a high-performance Neo4j knowledge base.

CAPABILITIES:
- Search knowledge base with 417x faster retrieval
- Access technical documentation and domain knowledge
- Provide answers with source citations and confidence scores
- Add new knowledge when provided by users

KNOWLEDGE BASE SPECS:
- Technology: Neo4j graph database + vector search
- Embeddings: 384-dimensional (all-MiniLM-L6-v2)
- Performance: Sub-100ms queries (417x improvement)
- Search: Hybrid (vector similarity + keyword matching)

HOW TO RESPOND:

When answering questions:
1. ALWAYS search the knowledge base first using search_knowledge_base
2. Cite sources with similarity scores (e.g., "According to source with 85% match...")
3. If no relevant information found (similarity <0.5), state clearly:
   "I couldn't find this information in the knowledge base"
4. Use check_knowledge_base_health if system seems slow or unresponsive

When providing answers:
- Synthesize information from top results
- Show confidence based on similarity scores:
  * >0.8 = High confidence
  * 0.5-0.8 = Moderate confidence
  * <0.5 = Low confidence (don't use)
- Include source count (e.g., "Based on 3 sources...")

When adding knowledge:
- Use add_document_to_knowledge_base when user provides new information
- Confirm successful addition
- Suggest related searches to verify

PERFORMANCE NOTES:
- Typical query time: <100ms
- Cache hit rate: 30-50%
- Expect 3-5 relevant sources per query

Be helpful, accurate, and always ground your answers in the knowledge base. Never make up information - if it's not in the knowledge base, say so!
```

### Step 2: Add Model Settings

**In "Model settings" section:**

- **Temperature**: `0.7` (balanced between creativity and accuracy)
- **Top P**: `0.9` (good for most cases)

Keep these settings for optimal Neo4j RAG usage.

### Step 3: Enable Tools

**Currently available in playground:**

- [x] **File search** - Toggle ON for quick testing
- [x] **Code interpreter** - Toggle OFF (not needed for RAG)

**Custom functions** (requires API):
- These need to be added via Azure AI Agent Service API
- Not available in playground UI yet
- See "Step 4" below for API configuration

### Step 4: Add Custom Functions (via API)

**Option A: Use the configuration script** (Recommended)

```bash
# Install dependencies
cd neo4j-rag-demo
pip install openai azure-identity

# Run configuration
python ../scripts/configure-azure-assistant.py
```

**Option B: Manual API call**

```python
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Initialize client
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint="https://swedencentral.api.cognitive.microsoft.com/",
    azure_ad_token_provider=token_provider,
    api_version="2024-07-18"
)

# Update assistant
client.beta.assistants.update(
    assistant_id="asst_LHQBXYvRhnbFo7KQ7IRbVXRR",
    name="Neo4j RAG Assistant",
    instructions="""<paste instructions from Step 1>""",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "Search Neo4j knowledge base (417x faster)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "max_results": {"type": "integer", "default": 5}
                    },
                    "required": ["question"]
                }
            }
        }
        # Add other tools...
    ]
)
```

---

## 🧪 Testing Your Configuration

### Test 1: Basic Search

**In the playground chat, type:**

```
Search the knowledge base for: What is Neo4j?
```

**Expected behavior:**
1. Assistant should call `search_knowledge_base` function
2. You'll see function call in the chat (if JSON response is ON)
3. Assistant returns answer with sources
4. Should mention similarity scores

**Example response:**
```
Based on my search of the knowledge base, I found 3 relevant sources:

Neo4j is a high-performance graph database management system (similarity: 87%).
According to the documentation, it stores data as nodes and relationships
(similarity: 82%), making it ideal for connected data and complex queries.

Sources:
1. Document: neo4j-overview.pdf (score: 0.87)
2. Document: graph-databases.pdf (score: 0.82)
3. Document: neo4j-architecture.pdf (score: 0.75)

Query completed in 45ms.
```

### Test 2: Health Check

**Ask:**
```
Check the knowledge base health
```

**Expected:**
```
✅ Knowledge base is healthy:
- Status: Operational
- Neo4j: Connected
- Average response time: 123ms
- Cache hit rate: 33%
- System is performing optimally with 417x improvement maintained
```

### Test 3: Statistics

**Ask:**
```
Show me knowledge base statistics
```

**Expected:**
```
📊 Knowledge Base Statistics:
- Total queries: 15
- Total documents: 10
- Total chunks: 150
- Cache size: 20 entries
- Hit rate: 40%
- Average response: 110ms
```

---

## ⚠️ Important Limitations

### Playground Limitations

**The Azure AI Foundry Playground has limitations:**

1. **Custom function calling** is limited in the UI
2. **Tool execution** may not show full details
3. **Real-time tool calls** work better via API

**For production use**, deploy the Agent Service:
- See: `docs/AZURE_ASSISTANT_SETUP.md`
- Deploy: `neo4j-rag-demo/azure_deploy/agent_service.py`

### File Search vs Custom RAG

**If you enable "File search"**:
- ✅ Quick testing capability
- ✅ Works in playground UI
- ❌ Uses Azure's vector store (not your Neo4j)
- ❌ Doesn't leverage 417x performance
- ❌ Additional costs for Azure vector storage

**Recommendation for now**:
- Enable File search for quick testing
- Upload a few test documents
- Plan to deploy agent service for full Neo4j RAG integration

---

## 🔧 Environment Variables Needed

**For the agent service (when deployed)**:

```bash
# Azure OpenAI (your Assistant)
AZURE_OPENAI_ENDPOINT=https://swedencentral.api.cognitive.microsoft.com/
AZURE_OPENAI_API_VERSION=2024-07-18
ASSISTANT_ID=asst_LHQBXYvRhnbFo7KQ7IRbVXRR

# Neo4j RAG Service
RAG_SERVICE_URL=http://rag-service:8000
# Or for local testing:
RAG_SERVICE_URL=http://localhost:8000

# Authentication (use Managed Identity in Azure)
# AZURE_OPENAI_KEY=<not-needed-with-managed-identity>
```

---

## 📋 Configuration Checklist

### In Azure AI Foundry Playground

- [ ] Update "Instructions" with Neo4j RAG instructions
- [ ] Set Temperature to 0.7
- [ ] Set Top P to 0.9
- [ ] Enable "File search" for quick testing (optional)
- [ ] Test with sample query

### Via Configuration Script

- [ ] Install dependencies: `pip install openai azure-identity`
- [ ] Run: `python scripts/configure-azure-assistant.py`
- [ ] Verify success message
- [ ] Test in playground

### For Production

- [ ] Deploy agent service to Azure Container App
- [ ] Configure environment variables
- [ ] Implement tool call handlers
- [ ] Test end-to-end integration
- [ ] Monitor performance and costs

---

## 🎯 What Each Tool Does

### 1. search_knowledge_base

**Purpose**: Search Neo4j with 417x performance

**Input:**
```json
{
  "question": "What is a graph database?",
  "max_results": 5,
  "use_llm": false
}
```

**Output:**
```json
{
  "answer": "Synthesized answer from sources...",
  "sources": [
    {
      "text": "Graph databases store data as nodes...",
      "score": 0.87,
      "doc_id": "uuid-here"
    }
  ],
  "processing_time": 0.045
}
```

### 2. add_document_to_knowledge_base

**Purpose**: Add new knowledge with Docling processing

**Input:**
```json
{
  "content": "New information about Neo4j...",
  "source": "user_upload",
  "metadata": {"category": "database", "author": "user"}
}
```

**Output:**
```json
{
  "status": "success",
  "document_id": "uuid-generated",
  "message": "Document added and indexed"
}
```

### 3. get_knowledge_base_statistics

**Purpose**: Performance and usage metrics

**Output:**
```json
{
  "query_stats": {
    "total_queries": 25,
    "avg_response_time": 110
  },
  "cache_stats": {
    "size": 30,
    "hit_rate_percent": 40
  },
  "system_stats": {
    "memory_usage_mb": 632
  }
}
```

### 4. check_knowledge_base_health

**Purpose**: System health and connectivity

**Output:**
```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "avg_response_time_ms": 123,
  "cache_hit_rate": 33.3,
  "performance_optimized": true
}
```

---

## 🔗 Related Documentation

- [**Azure Assistant Setup**](AZURE_ASSISTANT_SETUP.md) - Complete setup guide
- [**Agent Tools Reference**](../neo4j-rag-demo/src/azure_agent/neo4j_rag_agent_tools.py) - Tool implementations
- [**Azure Deployment**](AZURE_DEPLOYMENT_GUIDE.md) - Deploy agent service

---

## 🆘 Troubleshooting

### Tools Not Showing in Playground

**Issue**: Custom functions don't appear in playground UI

**Explanation**: Playground has limited custom function support

**Solution**:
- Use File search for testing
- Deploy agent service for full integration
- Use API directly for custom tools

### Function Calls Failing

**Check:**
```bash
# Verify RAG service is accessible
curl http://localhost:8000/health
# Or in Azure:
curl http://rag-service:8000/health
```

### Authentication Errors

**Ensure:**
- Logged into Azure: `az login`
- Correct permissions: Cognitive Services OpenAI User
- Managed Identity configured (for Azure deployment)

---

**Configuration script**: [`scripts/configure-azure-assistant.py`](../scripts/configure-azure-assistant.py)
**Your Assistant ID**: `asst_LHQBXYvRhnbFo7KQ7IRbVXRR`
**Status**: Ready to configure! 🚀
