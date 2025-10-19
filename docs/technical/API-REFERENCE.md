# API Reference

Complete API documentation for the Neo4j Hybrid RAG System.

## 🔗 Quick Navigation
- [← Back to Main README](../README.md) | [Architecture](ARCHITECTURE.md) | [Deployment](DEPLOYMENT.md)

---

## 🚀 Base URLs

| Environment | URL | Description |
|-------------|-----|-------------|
| **Local** | `http://localhost:8000` | Default local deployment |
| **Azure** | `https://your-app.azurecontainerapps.io` | Azure Container Apps |

## 📝 Core Endpoints

### Document Management

#### Add Document
```http
POST /documents
Content-Type: application/json

{
  "content": "Neo4j is a graph database management system.",
  "metadata": {
    "source": "documentation",
    "category": "databases",
    "author": "technical-team"
  }
}
```

**Response:**
```json
{
  "id": "doc_123456",
  "status": "processed",
  "chunks": 3,
  "embeddings_created": true
}
```

#### Get Document
```http
GET /documents/{document_id}
```

#### List Documents
```http
GET /documents?limit=10&offset=0&category=databases
```

### Query & RAG

#### Intelligent Query
```http
POST /query
Content-Type: application/json

{
  "question": "How does Neo4j handle graph traversals?",
  "k": 5,
  "use_llm": true,
  "llm_provider": "bitnet"
}
```

**Response:**
```json
{
  "answer": "Neo4j handles graph traversals through its Cypher query language...",
  "sources": [
    {
      "document_id": "doc_123456",
      "chunk": "Neo4j uses efficient graph algorithms...",
      "similarity": 0.92,
      "metadata": {"source": "documentation"}
    }
  ],
  "query_time": 1.2,
  "llm_time": 2.1
}
```

#### Search Only (No LLM)
```http
POST /search
Content-Type: application/json

{
  "query": "graph traversal algorithms",
  "k": 10,
  "search_type": "hybrid"
}
```

### System Status

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "neo4j": "connected",
  "bitnet_llm": "available",
  "version": "1.5.0",
  "uptime": "2h 15m"
}
```

#### System Metrics
```http
GET /metrics
```

**Response:**
```json
{
  "documents_count": 1250,
  "embeddings_count": 15600,
  "queries_today": 342,
  "avg_response_time": "1.8s",
  "cache_hit_rate": "73%"
}
```

## 🔧 Configuration

### Request Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | `application/json` |
| `Authorization` | No | `Bearer {token}` (if auth enabled) |

### Query Parameters

#### Search Configuration
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `k` | integer | 5 | Number of results to return |
| `search_type` | string | "hybrid" | "vector", "keyword", or "hybrid" |
| `min_similarity` | float | 0.0 | Minimum similarity threshold |

#### LLM Configuration  
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `use_llm` | boolean | true | Enable LLM response generation |
| `llm_provider` | string | "bitnet" | "bitnet" or "azure" |
| `max_tokens` | integer | 512 | Maximum response length |
| `temperature` | float | 0.1 | Response creativity (0.0-1.0) |

## 🧠 LLM Integration

### BitNet (Local)

**Endpoint:** `POST /query` with `llm_provider: "bitnet"`

**Characteristics:**
- 1.58-bit quantized inference
- ~2 second response time
- Works completely offline
- 1.1GB model memory usage

### Azure OpenAI (Cloud)

**Endpoint:** `POST /query` with `llm_provider: "azure"`

**Environment Variables Required:**
```bash
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_MODEL=gpt-4o-mini
```

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "metadata": {
    "query_time": 0.15,
    "timestamp": "2024-10-15T07:30:00Z"
  }
}
```

### Error Response  
```json
{
  "success": false,
  "error": {
    "code": "INVALID_QUERY",
    "message": "Query text cannot be empty",
    "details": {}
  },
  "timestamp": "2024-10-15T07:30:00Z"
}
```

## 🔍 Advanced Usage

### Batch Document Upload
```http
POST /documents/batch
Content-Type: application/json

{
  "documents": [
    {"content": "Document 1 content", "metadata": {"source": "batch1"}},
    {"content": "Document 2 content", "metadata": {"source": "batch2"}}
  ]
}
```

### Graph Relationship Queries
```http  
POST /graph/query
Content-Type: application/json

{
  "cypher": "MATCH (d:Document)-[:RELATES_TO]->(r) RETURN d, r LIMIT 10"
}
```

### Vector Similarity Search
```http
POST /embeddings/similarity
Content-Type: application/json

{
  "text": "machine learning algorithms",
  "top_k": 20,
  "threshold": 0.8
}
```

## 🛠️ Development Examples

### Python Client
```python
import requests

class RAGClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def add_document(self, content, metadata=None):
        response = requests.post(
            f"{self.base_url}/documents",
            json={"content": content, "metadata": metadata or {}}
        )
        return response.json()
    
    def query(self, question, k=5):
        response = requests.post(
            f"{self.base_url}/query",
            json={"question": question, "k": k}
        )
        return response.json()

# Usage
client = RAGClient()
result = client.query("What is Neo4j?")
print(result["answer"])
```

### cURL Examples
```bash
# Add document
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{"content":"Neo4j is a graph database","metadata":{"source":"docs"}}'

# Query with specific LLM
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Neo4j?","llm_provider":"bitnet","k":3}'

# Health check
curl http://localhost:8000/health
```

## ⚡ Performance Tips

1. **Batch Operations**: Use `/documents/batch` for multiple documents
2. **Cache Results**: Enable query caching for repeated questions
3. **Optimal K Values**: Use k=3-7 for best balance of speed vs relevance
4. **Search Types**: Use "vector" for semantic, "keyword" for exact matches

## 🚨 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_QUERY` | 400 | Query text missing or invalid |
| `DOCUMENT_NOT_FOUND` | 404 | Document ID does not exist |
| `LLM_UNAVAILABLE` | 503 | LLM service is down |
| `NEO4J_CONNECTION` | 503 | Database connection failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

---

## 📚 Related Documentation

- **[Architecture Overview](ARCHITECTURE.md)** - System design and components
- **[Deployment Guide](DEPLOYMENT.md)** - Setup and configuration  
- **[BitNet Integration](BITNET-COMPLETE-GUIDE.md)** - Local LLM setup
- **[Performance Optimization](BITNET_OPTIMIZATION.md)** - Tuning and scaling

**Need help?** Check the [troubleshooting section](../README.md#-support) or open an [issue](https://github.com/ma3u/neo4j-agentframework/issues).