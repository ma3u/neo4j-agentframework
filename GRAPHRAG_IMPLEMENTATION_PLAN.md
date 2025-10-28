# Neo4j GraphRAG Integration - Implementation Plan

**Status**: Draft - Awaiting Approval  
**Created**: 2025-10-28  
**Last Updated**: 2025-10-28

---

## 🎯 Executive Summary

Neo4j announced **Neo4j Aura Agent** at NODES 2025 (November 6, 2025), entering Early Access Program (EAP) on October 2, 2025. The official **neo4j-graphrag Python package v1.10.0** (released September 4, 2025) provides production-ready GraphRAG capabilities that align perfectly with our hybrid architecture.

**Key Opportunities**:
1. ✅ **Knowledge Graph Construction** - Automated entity extraction from our 30,006 chunks
2. ✅ **VectorCypherRetriever** - Enhanced retrieval combining vector + graph traversal
3. ✅ **Hybrid Deployment Ready** - Same package works with local Neo4j Docker and Aura
4. ✅ **LLM Flexibility** - Supports Azure OpenAI, Ollama, and custom LLM backends (BitNet)
5. ✅ **Embedding Portability** - Works with SentenceTransformers (local) and Azure OpenAI

**Implementation Effort**: 2-3 weeks, non-breaking addition to existing system

---

## 📋 Research Findings

### NODES 2025 Announcements

**Neo4j Aura Agent** (October 2, 2025):
- No-code/low-code GraphRAG platform in Early Access Program
- Available for all Aura tiers (Free, Professional, Business Critical)
- Features: Text2Cypher, GraphRAG patterns, future MCP server support
- Source: https://neo4j.com/blog/genai/build-context-aware-graphrag-agent/

**GraphRAG Pattern Catalog**:
- Comprehensive patterns at https://graphrag.com/
- Licensed under CC BY 4.0 by Neo4j, Inc.
- Research-backed implementation guidance

### Official Package Details

**Package**: `neo4j-graphrag` v1.10.0 (September 4, 2025)
- **Installation**: `pip install neo4j-graphrag[openai,sentence-transformers]`
- **Python Support**: 3.9 - 3.13
- **Neo4j Support**: 5.x compatible
- **Documentation**: https://neo4j.com/docs/neo4j-graphrag-python/current/
- **Long-term Support**: Official Neo4j package

**Core Features**:
1. **Knowledge Graph Construction Pipeline**
   - Entity extraction from unstructured text
   - Relationship detection
   - SimpleKGPipeline for quick setup (requires APOC)
   - Customizable Pipeline for advanced control

2. **Retrieval Components**
   - `VectorRetriever` - Pure vector similarity search
   - `VectorCypherRetriever` - Vector + graph traversal (multi-hop)
   - `HybridRetriever` - Vector + keyword combination
   - External vector DB support (Weaviate, Pinecone, Qdrant)

3. **LLM Integration**
   - Native support: OpenAI, Anthropic, Cohere, Mistral AI, Google, Ollama
   - Custom LLM interface for BitNet integration
   - Azure OpenAI support via `openai` extra

4. **Embedding Models**
   - SentenceTransformers (local, CPU-friendly)
   - OpenAI embeddings
   - Cohere embeddings
   - Custom embedder interface

---

## 🏗️ Current System Architecture

### Existing Implementation

**File**: `neo4j-rag-demo/src/neo4j_rag.py` (200+ lines)
```python
class Neo4jRAG:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=300)
    
    def optimized_vector_search(self, query: str, k: int = 5):
        # Custom implementation with caching, pooling
        # Uses SentenceTransformers for embeddings
        # Returns chunks with similarity scores
```

**Current Capabilities**:
- ✅ Vector search (417x optimized)
- ✅ Connection pooling (10 connections)
- ✅ Query caching (100 entry FIFO)
- ✅ Hybrid local/cloud deployment
- ✅ Azure Key Vault integration
- ❌ No entity extraction
- ❌ No graph traversal retrieval
- ❌ No relationship-aware context

**Production State**:
- Neo4j Aura instance: `6b870b04` (westeurope)
- 12 books, 30,006 chunks, 100% embedded
- SentenceTransformers embeddings (384-dim)
- Azure AI Foundry Assistant integrated

### Existing GraphRAG Demo

**File**: `neo4j-rag-demo/src/official_graphrag_demo.py` (233 lines)
```python
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.embeddings import SentenceTransformerEmbeddings
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.llm import LLMInterface

class Neo4jGraphRAGDemo:
    # Basic demo implementation
    # Uses VectorRetriever (not VectorCypherRetriever)
    # Simple LLM without real backend
```

**Status**: Proof-of-concept, not integrated with main system

---

## 🎯 Proposed Implementation

### Phase 1: Enhanced Retrieval (Week 1)

**Objective**: Add VectorCypherRetriever to existing system without breaking changes

**New File**: `neo4j-rag-demo/src/neo4j_graphrag_retriever.py`
```python
from neo4j_graphrag.retrievers import VectorCypherRetriever
from neo4j_graphrag.embeddings import SentenceTransformerEmbeddings
from neo4j_graphrag.generation import GraphRAG
from .neo4j_rag import Neo4jRAG

class Neo4jGraphRAGRetriever:
    """
    Enhanced retrieval using official GraphRAG package
    Works alongside existing Neo4jRAG for backward compatibility
    """
    
    def __init__(self, neo4j_rag: Neo4jRAG):
        # Reuse existing driver and embedder
        self.driver = neo4j_rag.driver
        self.embedder = SentenceTransformerEmbeddings(
            model="all-MiniLM-L6-v2"
        )
        
        # Create VectorCypherRetriever with custom query
        self.retriever = VectorCypherRetriever(
            driver=self.driver,
            index_name="text_embeddings",  # Existing index
            embedder=self.embedder,
            retrieval_query=self._get_retrieval_query()
        )
    
    def _get_retrieval_query(self) -> str:
        """Custom Cypher for document-chunk traversal"""
        return """
        // Start with vector similarity
        WITH node AS chunk, score
        
        // Traverse to parent document
        MATCH (doc:Document)-[:HAS_CHUNK]->(chunk)
        
        // Find related chunks (same document)
        MATCH (doc)-[:HAS_CHUNK]->(related:Chunk)
        WHERE related.chunk_index IN [chunk.chunk_index - 1, chunk.chunk_index + 1]
        
        // Return enriched context
        RETURN chunk.text + '\\n\\nContext: ' + 
               collect(related.text)[0..1] AS text,
               score,
               {source: doc.source, chunk_index: chunk.chunk_index} AS metadata
        """
    
    def search(self, query: str, top_k: int = 5):
        """Search with graph-enhanced context"""
        return self.retriever.search(query_text=query, top_k=top_k)
```

**Integration Point**: `neo4j-rag-demo/src/neo4j_rag.py` (add method)
```python
def create_graphrag_retriever(self):
    """Factory method for GraphRAG retriever"""
    from .neo4j_graphrag_retriever import Neo4jGraphRAGRetriever
    return Neo4jGraphRAGRetriever(self)
```

**Benefits**:
- Non-breaking: Existing code continues working
- Gradual adoption: Use `.create_graphrag_retriever()` when needed
- Hybrid approach: Compare performance against current implementation

### Phase 2: Knowledge Graph Construction (Week 2)

**Objective**: Extract entities from existing 30,006 chunks

**New File**: `neo4j-rag-demo/scripts/extract_entities_graphrag.py`
```python
from neo4j_graphrag.experimental.pipeline import SimpleKGPipeline
from neo4j import GraphDatabase
import os

# Connect to Aura or local
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

# Configure entity extraction
pipeline = SimpleKGPipeline(
    llm=azure_openai_llm,  # Use existing Azure AI Foundry
    driver=driver,
    entities=["Technology", "Concept", "Framework", "Author", "Organization"],
    relations=["USES", "IMPLEMENTS", "RELATED_TO", "AUTHORED_BY"],
    from_pdf=False  # We already have chunks in Neo4j
)

# Process existing chunks
with driver.session() as session:
    chunks = session.run("MATCH (c:Chunk) RETURN c.text AS text, ID(c) AS id")
    
    for chunk in chunks:
        # Extract entities and relationships
        pipeline.run(text=chunk["text"])
```

**Expected Graph Structure**:
```
Before:
(Document)-[:HAS_CHUNK]->(Chunk {text, embedding})

After:
(Document)-[:HAS_CHUNK]->(Chunk {text, embedding})
(Chunk)-[:MENTIONS]->(Entity {name, type})
(Entity)-[:RELATED_TO]->(Entity)
(Entity)-[:USES]->(Technology)
```

**Considerations**:
- Cost: ~$5-10 for 30K chunks using gpt-4o-mini
- Time: ~2-3 hours for full processing
- One-time operation: Entities reused for all queries
- Incremental: Process new documents only

### Phase 3: LLM Integration (Week 2-3)

**Objective**: Integrate Azure AI Foundry and BitNet as LLM backends

**Azure OpenAI LLM** (Production):
```python
from neo4j_graphrag.llm import AzureOpenAILLM

llm = AzureOpenAILLM(
    model="gpt-4o-mini",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-08-01-preview"
)
```

**BitNet Custom LLM** (Local):
```python
from neo4j_graphrag.llm import LLMInterface, LLMResponse
import requests

class BitNetLLM(LLMInterface):
    def __init__(self, endpoint: str = "http://localhost:8001"):
        super().__init__(model_name="bitnet-b1.58-2b4t")
        self.endpoint = endpoint
    
    def invoke(self, input: str, **kwargs) -> LLMResponse:
        response = requests.post(
            f"{self.endpoint}/generate",
            json={"prompt": input, "max_tokens": 512}
        )
        return LLMResponse(content=response.json()["text"])
```

**Environment-Aware Factory**:
```python
def get_llm():
    if os.getenv("DEPLOYMENT_ENV") == "production":
        return AzureOpenAILLM(...)
    else:
        return BitNetLLM(...)
```

### Phase 4: Testing & Documentation (Week 3)

**Test Script**: `neo4j-rag-demo/tests/test_graphrag_integration.py`
- Compare retrieval quality: current vs GraphRAG
- Measure latency impact
- Validate hybrid deployment (local + Aura)
- Test entity extraction accuracy

**Documentation Updates**:
- Update README.md with GraphRAG features
- Add `docs/GRAPHRAG_GUIDE.md`
- Update Cypher queries to include entity traversal
- Add to NODES2025 presentation (Slide 10: "What's Next")

---

## 📊 Impact Analysis

### Performance Impact

**Expected Improvements**:
- ✅ Better context: Adjacent chunks + entity relationships
- ✅ Multi-hop reasoning: "How do GNNs relate to Neo4j?"
- ✅ Cross-document connections: Concepts across 12 books

**Potential Concerns**:
- ⚠️ Query latency: Additional graph traversal (10-50ms overhead)
- ⚠️ Complexity: More moving parts to maintain
- ⚠️ Storage: Entity nodes (estimated +10% database size)

**Mitigation**:
- Keep existing optimized retriever as fallback
- A/B test: Current vs GraphRAG on same queries
- Measure: `time_current` vs `time_graphrag` for 100 queries

### Cost Impact

**One-Time** (Entity Extraction):
- 30,006 chunks × $0.15/1M tokens ≈ $4.50 (gpt-4o-mini)
- Local option: Use Ollama (free, slower)

**Ongoing** (Zero):
- GraphRAG uses existing infrastructure
- No new databases or services
- Entity graph stored in same Aura instance

### Deployment Impact

**Development Environment**:
```bash
# Add to requirements.txt
neo4j-graphrag[openai,sentence-transformers]==1.10.0

# Test locally
docker-compose -f scripts/docker-compose.ghcr.yml up -d
python neo4j-rag-demo/scripts/extract_entities_graphrag.py --target local
```

**Production Environment** (Azure Container Apps):
- Same container image
- No infrastructure changes
- Environment variable for LLM backend

---

## 🚀 Rollout Strategy

### Option A: Gradual Migration (Recommended)

**Week 1**: Add GraphRAG retriever alongside existing
**Week 2**: Extract entities for 1-2 books (test quality)
**Week 3**: Compare performance, document findings
**Week 4+**: Full rollout if beneficial

### Option B: Parallel Systems

Keep both systems running:
- **Current**: Fast, optimized, proven (default)
- **GraphRAG**: Enhanced context, experimental (opt-in)

API flag: `?use_graphrag=true` for testing

---

## ✅ Decision Points

**Before starting implementation, confirm**:

1. ☐ **Value Proposition**: Do we need entity extraction for our use case?
   - Current system: 417x fast, works well
   - GraphRAG adds: Entity relationships, multi-hop reasoning
   - Question: Will users benefit from entity-aware search?

2. ☐ **Hybrid Compatibility**: Verify GraphRAG works in both environments
   - Local: Neo4j Docker + SentenceTransformers + BitNet
   - Cloud: Neo4j Aura + Azure OpenAI + gpt-4o-mini
   - Test: Install package, run demo, validate

3. ☐ **Cost Justification**: Is $5-10 entity extraction worth it?
   - Benefit: Better cross-document understanding
   - Alternative: Use current system, add later if needed

4. ☐ **Maintenance Burden**: Can we maintain two retrieval paths?
   - Existing: Custom, optimized, proven
   - New: Official package, but adds complexity

---

## 📝 Next Steps (Upon Approval)

1. **Install and Test** (1 day)
   ```bash
   pip install neo4j-graphrag[openai,sentence-transformers]==1.10.0
   python neo4j-rag-demo/src/official_graphrag_demo.py
   ```

2. **Create Hybrid Demo** (2 days)
   - Test VectorCypherRetriever with existing Aura data
   - Compare query results: current vs GraphRAG
   - Measure latency difference

3. **Entity Extraction Proof-of-Concept** (2 days)
   - Process 1 book (~2,500 chunks)
   - Review extracted entities manually
   - Assess quality and usefulness

4. **Document Findings** (1 day)
   - Update this plan with results
   - Recommendation: Proceed or defer

5. **Full Implementation** (If approved after PoC)
   - Follow Phase 1-4 timeline
   - Gradual rollout to production

---

## 🔗 References

- **Neo4j Aura Agent Blog**: https://neo4j.com/blog/genai/build-context-aware-graphrag-agent/
- **GraphRAG Pattern Catalog**: https://graphrag.com/
- **Official Documentation**: https://neo4j.com/docs/neo4j-graphrag-python/current/
- **GitHub Repository**: https://github.com/neo4j/neo4j-graphrag-python
- **PyPI Package**: https://pypi.org/project/neo4j-graphrag/
- **NODES 2025 Session**: https://neo4j.com/nodes-2025/agenda/sovereign-neo4j-rag-achieving-cloud-grade-performance-using-bitnet-llm/
- **Discussion Created**: https://github.com/ma3u/neo4j-agentframework/discussions/17

---

**Status**: 🟡 **Awaiting Approval** - Do not implement until reviewed and approved
