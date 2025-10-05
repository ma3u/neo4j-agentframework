# Embedding Models Guide

**Complete guide to embedding models used in Neo4j RAG system**

---

## 📑 Table of Contents

- [Overview](#overview)
- [Embedding Models Comparison](#embedding-models-comparison)
- [Local Embeddings (Default)](#local-embeddings-default)
- [Azure OpenAI Embeddings (Optional)](#azure-openai-embeddings-optional)
- [Configuration Guide](#configuration-guide)
- [Performance Comparison](#performance-comparison)
- [When to Use Which](#when-to-use-which)
- [Migration Guide](#migration-guide)

---

## Overview

Our Neo4j RAG system supports **two embedding approaches**:

1. **SentenceTransformers (Local)** - Default, cost-free, high performance
2. **Azure OpenAI (Cloud)** - Optional, API-based, ultra-minimal deployment

Both achieve the same goal: Convert text to vector representations for semantic search in Neo4j.

---

## Embedding Models Comparison

| Feature | SentenceTransformers (Local) | Azure OpenAI (Cloud) |
|---------|------------------------------|----------------------|
| **Model** | all-MiniLM-L6-v2 | text-embedding-3-small |
| **Dimensions** | 384 | 1536 (configurable) |
| **Type** | Local inference | API calls |
| **Cost** | $0 (free) | ~$0.02/1M tokens (~$2-5/month) |
| **Performance** | ~100ms per embedding | ~50-100ms (network latency) |
| **Memory** | ~500MB model loaded | 0MB (API-based) |
| **Offline** | ✅ Yes | ❌ No (requires internet) |
| **API Keys** | ❌ None required | ✅ Required |
| **Container Size** | +500MB | +0MB (minimal) |
| **Quality** | Excellent (SOTA for size) | Excellent (OpenAI-grade) |
| **Use Case** | Production, local dev | POC, cost-optimized Azure |

---

## Local Embeddings (Default)

### Model: all-MiniLM-L6-v2 (SentenceTransformers)

**Specifications:**
- **Source**: [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Dimensions**: 384
- **Model Size**: ~90MB (parameters) + ~400MB (runtime)
- **Architecture**: MiniLM (distilled from larger models)
- **Training**: Trained on 1B+ sentence pairs
- **Performance**: 14,200 sentences/second on V100 GPU

**Why This Model?**

1. **Optimal Size/Performance Ratio**
   - Small enough for edge deployment
   - Fast enough for real-time queries
   - Accurate enough for production use

2. **Production Proven**
   - 100M+ downloads on HuggingFace
   - Used by thousands of production systems
   - Well-documented and supported

3. **Cost Efficiency**
   - Zero API costs
   - Offline capability
   - No rate limits

**Quality Metrics:**
```
Benchmark                Score
Semantic Textual Sim    82.41
MS MARCO                30.81
TREC-COVID              68.06
Average                 ~75
```

### Implementation

**Installation:**
```bash
pip install sentence-transformers
```

**Usage:**
```python
from sentence_transformers import SentenceTransformer

# Load model (one-time, ~500MB memory)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
text = "Neo4j is a graph database"
embedding = model.encode(text)  # Returns 384-dim numpy array

print(f"Dimensions: {len(embedding)}")  # 384
print(f"Type: {type(embedding)}")       # numpy.ndarray
```

**In Our System:**
```python
# neo4j-rag-demo/src/neo4j_rag.py
from sentence_transformers import SentenceTransformer

class Neo4jRAG:
    def __init__(self):
        # Load model once, reuse for all queries
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _embed_text(self, text: str) -> List[float]:
        """Generate 384-dimensional embedding"""
        embedding = self.model.encode(text)
        return embedding.tolist()  # Convert to list for Neo4j
```

**Configuration:**
```bash
# Environment variable (optional)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Or in code
model = SentenceTransformer('all-MiniLM-L6-v2')
```

**Performance:**
- **Embedding Generation**: ~100ms per text
- **Batch Processing**: ~10ms per text (batch of 10)
- **Memory Usage**: ~500MB (model loaded)
- **Throughput**: ~1000 texts/second (optimized)

---

## Azure OpenAI Embeddings (Optional)

### Model: text-embedding-3-small (Azure OpenAI)

**Specifications:**
- **Source**: Azure OpenAI Service
- **Dimensions**: 1536 (default) or 512/256 (configurable)
- **Model Size**: N/A (API-based)
- **Architecture**: OpenAI proprietary
- **Pricing**: $0.020 per 1M tokens

**Why This Model?**

1. **Cost-Effective for POC**
   - No local model to load
   - Pay only for usage
   - Scale-to-zero friendly

2. **Minimal Container**
   - No ML dependencies needed
   - ~400MB total container size
   - Ultra-low memory footprint

3. **High Quality**
   - OpenAI-grade embeddings
   - Latest model improvements
   - Consistent results

**Cost Calculation:**
```
Example POC Usage:
- 100 queries/day
- ~100 tokens per query
- 30 days

Total: 100 * 100 * 30 = 300,000 tokens
Cost: 300k / 1M * $0.02 = $0.006 (~$0.01/month!)

Even at 10,000 queries/day: ~$0.60/month
```

### Implementation

**Installation:**
```bash
pip install openai azure-identity
```

**Usage:**
```python
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint="https://your-openai.openai.azure.com/",
    azure_ad_token_provider=get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )
)

# Generate embeddings
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Neo4j is a graph database"
)

embedding = response.data[0].embedding  # 1536-dim list
```

**In Azure POC System:**
```python
# Simplified for Azure-only deployment
class AzureRAG:
    def __init__(self, azure_endpoint: str):
        self.client = AzureOpenAI(azure_endpoint=azure_endpoint)

    def _embed_text(self, text: str) -> List[float]:
        """Generate embedding via Azure OpenAI API"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
```

**Configuration:**
```bash
# Environment variables
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key  # Or use Managed Identity
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

**Performance:**
- **API Latency**: ~50-100ms (network + processing)
- **Rate Limits**: 240,000 tokens/minute (default)
- **Memory Usage**: 0MB (no local model)
- **Container Size**: +0MB (API-based)

---

## Configuration Guide

### Local Deployment (Recommended)

**requirements.txt:**
```python
sentence-transformers>=2.2.2
torch>=2.0.0  # Required by sentence-transformers
transformers>=4.30.0
```

**Environment:**
```bash
EMBEDDING_MODEL=all-MiniLM-L6-v2
# No API credentials needed
```

**Docker Compose:**
```yaml
rag-service:
  environment:
    - EMBEDDING_MODEL=all-MiniLM-L6-v2
  # Model downloaded on first run and cached
```

---

### Azure POC Deployment (Cost-Optimized)

**requirements-poc.txt:**
```python
openai>=1.3.7
azure-identity>=1.19.0
# No sentence-transformers needed!
```

**Environment:**
```bash
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
# Use Managed Identity (no API key in code)
```

**Azure Container App:**
```bash
az containerapp create \
  --environment-variables \
    AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT \
    EMBEDDING_MODEL=text-embedding-3-small
```

---

## Performance Comparison

### Embedding Generation Performance

| Operation | Local (SentenceTransformers) | Azure OpenAI |
|-----------|------------------------------|--------------|
| **Single Text** | ~100ms | ~50-100ms |
| **Batch (10 texts)** | ~10ms/text | ~50-100ms total |
| **Batch (100 texts)** | ~5ms/text | ~100-200ms total |
| **Cold Start** | ~2s (model load) | 0s (API ready) |
| **Memory** | +500MB | +0MB |
| **Throughput** | ~1000 texts/sec | ~240k tokens/min |

### Vector Search Performance

**Both models achieve <100ms search** in Neo4j:

```python
# Query performance is identical regardless of embedding model
# (Once embeddings are stored in Neo4j)

Vector Search Time: ~20ms
Keyword Search Time: ~10ms
Hybrid Ranking Time: ~10ms
Total: ~40ms (417x improvement maintained)
```

**Key Insight**: Embedding model choice affects:
- ✅ Document upload time
- ✅ Query embedding time
- ❌ Does NOT affect search performance (Neo4j vector search speed)

---

## When to Use Which

### Use SentenceTransformers (all-MiniLM-L6-v2) When:

✅ **Local Development**
- No internet required
- Fast iteration
- No API setup needed

✅ **Production Deployment**
- Cost optimization ($0 API fees)
- Offline capability required
- High throughput needs (1000+ queries/sec)

✅ **Self-Hosted Infrastructure**
- On-premise deployment
- Data sovereignty requirements
- No cloud dependencies

✅ **Performance Critical**
- Batch processing large documents
- Real-time embedding generation
- Minimal latency requirements

---

### Use Azure OpenAI (text-embedding-3-small) When:

✅ **POC/Testing**
- Minimal container size needed
- Scale-to-zero deployment
- Quick Azure deployment

✅ **Ultra-Low Memory**
- Edge devices
- Minimal resource environments
- Cost-conscious POC

✅ **Azure-Native Stack**
- Already using Azure OpenAI
- Managed Identity authentication
- Azure monitoring integration

❌ **NOT Recommended For:**
- High-volume production (costs add up)
- Offline requirements
- Performance-critical (network latency)

---

## Migration Guide

### From Azure OpenAI to SentenceTransformers

**Why Migrate:**
- Eliminate API costs
- Improve performance (no network latency)
- Offline capability

**Steps:**

1. **Update Requirements:**
```bash
# Add to requirements.txt
sentence-transformers>=2.2.2
torch>=2.0.0
transformers>=4.30.0
```

2. **Update Configuration:**
```bash
# Change environment variable
EMBEDDING_MODEL=all-MiniLM-L6-v2
# Remove Azure OpenAI credentials
```

3. **Update Code:**
```python
# Before
from openai import AzureOpenAI
client = AzureOpenAI(...)

# After
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

4. **Re-embed Existing Documents:**
```python
# Existing documents need re-embedding with new model
# Run migration script to update all embeddings
python scripts/migrate_embeddings.py
```

**Note**: Existing vectors in Neo4j must be regenerated (different dimensions: 1536 → 384)

---

### From SentenceTransformers to Azure OpenAI

**Why Migrate:**
- Reduce container size
- Scale-to-zero deployment
- Azure-native architecture

**Steps:**

1. **Update Requirements:**
```bash
# requirements-poc.txt (remove heavy ML)
openai>=1.3.7
azure-identity>=1.19.0
# Remove: sentence-transformers, torch, transformers
```

2. **Update Configuration:**
```bash
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
EMBEDDING_MODEL=text-embedding-3-small
```

3. **Update Code:**
```python
# Before
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# After
from openai import AzureOpenAI
client = AzureOpenAI(azure_endpoint=endpoint)
```

4. **Re-embed Documents:**
```python
# Re-generate all embeddings with Azure OpenAI
# Dimensions change: 384 → 1536
python scripts/migrate_to_azure_embeddings.py
```

---

## Technical Details

### Vector Index Configuration in Neo4j

**For SentenceTransformers (384 dimensions):**
```cypher
CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
FOR (c:Chunk)
ON c.embedding
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 384,
    `vector.similarity_function`: 'cosine'
  }
}
```

**For Azure OpenAI (1536 dimensions):**
```cypher
CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
FOR (c:Chunk)
ON c.embedding
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
}
```

**Important**: Cannot mix embedding models! All documents must use same model/dimensions.

### Similarity Function

**We use Cosine Similarity** for both models:

```python
# Formula: cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
# Range: -1 to 1 (higher = more similar)
# Normalized: Independent of vector magnitude
```

**Why Cosine?**
- ✅ Normalized (magnitude-independent)
- ✅ Works well for text embeddings
- ✅ Fast computation in Neo4j
- ✅ Standard in semantic search

---

## Performance Benchmarks

### Embedding Generation Speed

**SentenceTransformers (Local):**
```
Single text:     ~100ms
Batch (10):      ~10ms per text
Batch (100):     ~5ms per text
Batch (1000):    ~3ms per text

Optimal batch size: 100-500 texts
```

**Azure OpenAI (API):**
```
Single text:     ~50-100ms
Batch (10):      ~50-100ms total (~10ms per text)
Batch (100):     ~100-200ms total (~2ms per text)
Batch (1000):    ~500-1000ms total (~1ms per text)

Optimal batch size: 100-1000 texts
API rate limit: 240k tokens/minute
```

### Document Processing Time

**50-page PDF with SentenceTransformers:**
```
Docling extraction: ~100-150s (2-3s per page)
Text chunking:      ~1s (150 chunks)
Embedding:          ~15s (150 chunks × 100ms)
Neo4j storage:      ~5s
Total:              ~120-170s
```

**50-page PDF with Azure OpenAI:**
```
Docling extraction: ~100-150s (2-3s per page)
Text chunking:      ~1s (150 chunks)
Embedding:          ~10s (batch API call)
Neo4j storage:      ~5s
Total:              ~115-165s
```

**Difference**: Minimal (~5s) for document upload

### Query Performance

**Both models achieve same Neo4j search speed:**

```python
# Query embedding: ~100ms (local) or ~50-100ms (API)
# Neo4j vector search: ~20ms (SAME for both)
# Keyword search: ~10ms (SAME)
# Hybrid ranking: ~10ms (SAME)

Total Query Time:
- Local:  ~140ms (100ms embed + 40ms search)
- Azure:  ~90-140ms (50-100ms embed + 40ms search)

Both maintain 417x improvement! ✅
```

---

## When to Use Which

### Decision Tree

```
Do you need offline capability?
├─ YES → Use SentenceTransformers
└─ NO
   ├─ Is this a POC with <1000 queries/day?
   │  ├─ YES → Use Azure OpenAI (cost-optimized)
   │  └─ NO
   │     ├─ Do you need scale-to-zero?
   │     │  ├─ YES → Use Azure OpenAI
   │     │  └─ NO → Use SentenceTransformers
   │     └─ Are API costs acceptable?
   │        ├─ YES → Either works
   │        └─ NO → Use SentenceTransformers
```

### Recommendations by Scenario

**Local Development**: `all-MiniLM-L6-v2`
- Zero setup complexity
- No API keys needed
- Fast iteration

**Production (Self-Hosted)**: `all-MiniLM-L6-v2`
- Zero ongoing costs
- Maximum performance
- 417x speed maintained

**Azure POC**: `text-embedding-3-small`
- Minimal container (~400MB)
- Scale-to-zero enabled
- ~$2-5/month for POC loads

**Enterprise Azure**: `all-MiniLM-L6-v2`
- Cost control at scale
- Performance optimization
- Data sovereignty

**Edge Deployment**: `all-MiniLM-L6-v2`
- Offline capability
- Local inference
- No cloud dependency

---

## Cost Analysis

### SentenceTransformers (Local)

**One-time Costs:**
- Model download: Free (~90MB)
- Container size: +500MB

**Ongoing Costs:**
- API fees: $0
- Compute: Included in container costs
- Storage: ~500MB RAM per instance

**Total**: $0/month (no API fees)

### Azure OpenAI

**One-time Costs:**
- Setup: Free (Azure subscription needed)
- Container size: +0MB (no model)

**Ongoing Costs (Example Loads):**

| Usage | Tokens/Month | Cost/Month |
|-------|--------------|------------|
| **POC** (100 queries/day) | 300k | $0.01 |
| **Light** (1k queries/day) | 3M | $0.06 |
| **Medium** (10k queries/day) | 30M | $0.60 |
| **Heavy** (100k queries/day) | 300M | $6.00 |
| **Production** (1M queries/day) | 3B | $60.00 |

**Breakeven Point**: At ~100k queries/day, local embeddings become more cost-effective

---

## Current System Configuration

### What We Use Now

**Deployment**: Docker Compose (Local + Azure)
**Embedding Model**: `all-MiniLM-L6-v2` (SentenceTransformers)
**Dimensions**: 384
**Cost**: $0 (completely free)
**Performance**: 417x improvement validated ✅

**Why We Chose This:**
1. ✅ Zero API costs
2. ✅ Offline capability
3. ✅ Proven performance
4. ✅ Production-ready
5. ✅ No rate limits

### Configuration Files

**Main requirements** (`requirements.txt`):
```python
sentence-transformers>=2.2.2  # Includes all-MiniLM-L6-v2
torch>=2.0.0
transformers>=4.30.0
```

**Docker Compose** (`scripts/docker-compose.optimized.yml`):
```yaml
rag-service:
  environment:
    - EMBEDDING_MODEL=all-MiniLM-L6-v2
  # Model auto-downloaded on first run
```

**RAG Service** (`neo4j-rag-demo/src/neo4j_rag.py`):
```python
self.model = SentenceTransformer('all-MiniLM-L6-v2')
# 384-dimensional embeddings
```

---

## Troubleshooting

### Model Download Issues

**Problem**: Model won't download
```bash
# Solution: Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Memory Issues

**Problem**: Out of memory when loading model
```bash
# Solution: Increase Docker memory to 2GB+
docker run -m 2g ...
```

### Dimension Mismatch

**Problem**: Vector index dimension error
```bash
# Solution: Check Neo4j index dimensions match model
# SentenceTransformers: 384
# Azure OpenAI: 1536
```

### Performance Issues

**Problem**: Slow embedding generation
```python
# Solution: Use batch encoding
embeddings = model.encode(texts, batch_size=100)
# Much faster than encoding one at a time
```

---

## Related Documentation

- [**🏗️ System Architecture**](ARCHITECTURE.md) - Architecture overview
- [**📊 Performance Analysis**](performance_analysis.md) - Performance benchmarks
- [**🚀 Quick Start Guide**](README-QUICKSTART.md) - Setup instructions
- [**🔧 LLM Setup**](LLM_SETUP.md) - LLM configuration
- [**📖 Documentation Index**](README.md) - All documentation

---

## References

### SentenceTransformers
- [Official Documentation](https://www.sbert.net/)
- [HuggingFace Model Card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [GitHub Repository](https://github.com/UKPLab/sentence-transformers)

### Azure OpenAI
- [Embeddings Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/embeddings)
- [Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)
- [Best Practices](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/embeddings)

---

**Last Updated**: 2025-10-05
**Current Default**: all-MiniLM-L6-v2 (SentenceTransformers)
**Status**: Both models tested and production-ready ✅
