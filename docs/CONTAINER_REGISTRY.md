# GitHub Container Registry - Pre-built Docker Images

**Zero build time deployment** - Use pre-built Docker images for instant BitNet.cpp deployment!

---

## 🐳 Available Images

All images are automatically built and published to GitHub Container Registry:

| Image | Size | Description | Use Case |
|-------|------|-------------|----------|
| [`ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest`](https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Fbitnet-final) | 3.2GB | Full BitNet.cpp with real 1.58-bit quantized inference | Production deployment |
| [`ghcr.io/ma3u/ms-agentf-neo4j/bitnet-optimized:latest`](https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Fbitnet-optimized) | 1.4GB | Size-optimized BitNet.cpp container | Resource-constrained environments |
| [`ghcr.io/ma3u/ms-agentf-neo4j/rag-service:latest`](https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Frag-service) | ~800MB | Ultra-high-performance RAG service with 417x speedup | Core RAG functionality |
| [`ghcr.io/ma3u/ms-agentf-neo4j/streamlit-chat:latest`](https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Fstreamlit-chat) | ~500MB | Interactive Streamlit chat UI | Development and testing |

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/ma3u/neo4j-agentframework.git
cd neo4j-agentframework

# Pull and start all services
docker-compose -f scripts/docker-compose.ghcr.yml up -d

# Access services:
# - Streamlit Chat: http://localhost:8501
# - Neo4j Browser: http://localhost:7474 (neo4j/password)
# - RAG API: http://localhost:8000/docs
# - BitNet API: http://localhost:8001/health
```

### Option 2: Individual Images

```bash
# Pull specific images
docker pull ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest
docker pull ghcr.io/ma3u/ms-agentf-neo4j/rag-service:latest
docker pull ghcr.io/ma3u/ms-agentf-neo4j/streamlit-chat:latest

# Run BitNet standalone
docker run -d -p 8001:8001 ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest

# Run RAG service
docker run -d -p 8000:8000 \
  -e NEO4J_URI=bolt://host.docker.internal:7687 \
  -e NEO4J_PASSWORD=password \
  ghcr.io/ma3u/ms-agentf-neo4j/rag-service:latest
```

---

## 🔄 Image Variants

### BitNet Images

#### `bitnet-final:latest` (3.2GB)
- **Contains**: Real Microsoft BitNet.cpp with 1.58-bit quantized inference
- **Model**: BitNet-b1.58-2B-4T (1.11GB GGUF file)
- **Binary**: Compiled `llama-cli` with ARM TL1 kernels
- **Performance**: 2-5 seconds inference, 1.5GB memory usage
- **Use Case**: Production deployment with real AI reasoning

#### `bitnet-optimized:latest` (1.4GB)
- **Contains**: Same as `bitnet-final` but size-optimized
- **Optimization**: Removes build artifacts, only runtime files
- **Savings**: 52% size reduction (3.2GB → 1.4GB)
- **Performance**: Identical to `bitnet-final`
- **Use Case**: Resource-constrained environments

### Service Images

#### `rag-service:latest` (~800MB)
- **Contains**: FastAPI RAG service with SentenceTransformers
- **Features**: Neo4j vector search, 417x performance optimization
- **Embeddings**: Local all-MiniLM-L6-v2 (no external API calls)
- **Use Case**: Core RAG functionality

#### `streamlit-chat:latest` (~500MB)
- **Contains**: Interactive chat UI with document upload
- **Features**: Real-time RAG queries, health monitoring
- **Use Case**: Development interface and demos

---

## 📈 Benefits

### vs Building from Source

| Aspect | Build from Source | Pre-built Images |
|--------|-------------------|------------------|
| **Build Time** | 30+ minutes | 0 minutes |
| **Disk Usage** | 10GB+ during build | Image size only |
| **Dependencies** | Build tools, compilers | None |
| **Consistency** | Varies by system | Identical everywhere |
| **Updates** | Manual rebuild | `docker pull` |

### Cross-Platform Support

- ✅ **Linux x64** - Native Docker support
- ✅ **Linux ARM64** - ARM-optimized BitNet kernels
- ✅ **macOS** - Docker Desktop (tested on M1/M2)
- ✅ **Windows** - Docker Desktop with WSL2
- ✅ **Cloud** - AWS, Azure, GCP container services

---

## 🔧 Advanced Usage

### Custom Configuration

```bash
# Use different BitNet variant
docker-compose -f scripts/docker-compose.ghcr.yml up -d
# Edit the compose file to use bitnet-optimized:latest instead

# Run with custom environment
docker run -d -p 8001:8001 \
  -e BITNET_THREADS=8 \
  -e BITNET_CTX_SIZE=4096 \
  ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest
```

### Production Deployment

```bash
# Azure Container Apps
az containerapp create \
  --name bitnet-rag \
  --resource-group myResourceGroup \
  --environment myEnvironment \
  --image ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest \
  --cpu 2 --memory 4Gi

# Kubernetes
kubectl create deployment bitnet-rag \
  --image=ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest
```

### Health Checks

```bash
# Check BitNet service
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "mode": "real_inference",
  "model_size_gb": 1.11,
  "binary_exists": true,
  "quantization": "i2_s (1.58-bit ternary)"
}
```

---

## 🤖 Automated Builds

Images are automatically built and updated via GitHub Actions:

- **Trigger**: Push to `main` branch or Dockerfile changes
- **Platforms**: `linux/amd64`, `linux/arm64`
- **Registry**: GitHub Container Registry (ghcr.io)
- **Tags**: `latest`, `YYYYMMDD` (date-based)

### Build Process

1. **BitNet Images**: 
   - Clone Microsoft BitNet.cpp
   - Generate ARM TL1 kernels with `codegen_tl1.py`
   - Compile with clang-18
   - Download BitNet-b1.58-2B-4T model
   - Package runtime

2. **Service Images**:
   - Build optimized RAG service
   - Build Streamlit chat UI
   - Multi-platform builds

### Manual Build

To build images yourself:

```bash
# Build and push all images
./scripts/build-and-push-images.sh --push

# Build locally (no push)
./scripts/build-and-push-images.sh
```

---

## 🔗 Links

- **GitHub Repository**: https://github.com/ma3u/ms-agentf-neo4j
- **Container Registry**: https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Fbitnet-final
- **BitNet Success Story**: [BITNET-SUCCESS.md](BITNET-SUCCESS.md)
- **Build Script**: [build-and-push-images.sh](../scripts/build-and-push-images.sh)
- **Docker Compose**: [docker-compose.ghcr.yml](../scripts/docker-compose.ghcr.yml)

---

## 📝 Notes

- Images are **public** and don't require authentication to pull
- **Size optimization** is ongoing - images may get smaller over time
- **Security scanning** is performed on all published images
- **License**: Same as repository (MIT)

**Ready to deploy?** Start with: `docker-compose -f scripts/docker-compose.ghcr.yml up -d`