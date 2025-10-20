# BitNet LLM Integration for Neo4j RAG Demo

This directory contains the BitNet LLM integration for the Neo4j RAG Demo project.

## 📁 Directory Structure

```
bitnet-llm/
├── dockerfiles/
│   └── Dockerfile.bitnet-minimal     # BitNet container definition (334MB)
├── scripts/
│   ├── bitnet_server_minimal.py     # FastAPI server for BitNet inference
│   └── download_model.sh            # Model download utility
├── models/
│   ├── ggml-model-i2_s.gguf         # BitNet 1.58B 2B 4T model (1.1GB)
│   └── README.md                    # Model information
├── docker-compose-bitnet-minimal.yml # Standalone BitNet deployment
└── README.md                        # This file
```

## 🚀 Quick Start

### Option 1: Integrated with Neo4j RAG Demo (Recommended)

Start the complete stack including Neo4j, RAG API, Streamlit UI, and BitNet LLM:

```bash
# From neo4j-rag-demo root directory
docker compose up -d

# Check all services
docker compose ps

# Test BitNet LLM
curl http://localhost:8001/health
```

### Option 2: Standalone BitNet LLM

Start only the BitNet LLM service:

```bash
cd bitnet-llm
docker compose -f docker-compose-bitnet-minimal.yml --profile volume-mount up -d

# Test standalone
curl http://localhost:8001/health
curl -X POST http://localhost:8001/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"What is Neo4j?","max_tokens":50}'
```

## 📊 Service Details

### BitNet LLM Service
- **Container**: `neo4j-rag-demo-bitnet`
- **Image**: `neo4j-rag-demo/bitnet-minimal:latest` (334MB)
- **Model**: BitNet b1.58 2B 4T (1.1GB)
- **Port**: `8001`
- **Health Check**: `http://localhost:8001/health`

### API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | Service health check |
| `/model-info` | GET | Model information |
| `/generate` | POST | Text generation |

### Example API Usage

```bash
# Health check
curl http://localhost:8001/health

# Text generation
curl -X POST http://localhost:8001/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explain graph databases:",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `/app/models/ggml-model-i2_s.gguf` | Path to GGUF model |
| `BITNET_BINARY` | `/app/bin/llama-cli` | BitNet.cpp binary path |
| `BITNET_THREADS` | `4` | CPU threads for inference |
| `BITNET_CTX_SIZE` | `2048` | Context window size |
| `MODEL_WAIT_TIMEOUT` | `60` | Model loading timeout (seconds) |

### Resource Usage

- **Memory**: ~1.5GB (model + inference)
- **CPU**: 4 threads (configurable)
- **Disk**: 334MB (container) + 1.1GB (model)
- **Network**: Internal Docker network + port 8001

## 🌐 Integration with RAG API

The BitNet LLM is automatically integrated with the RAG API service:

- **Connection**: `http://bitnet-llm:8001` (internal Docker network)
- **Environment**: `BITNET_LLM_URL=http://bitnet-llm:8001`
- **Dependencies**: RAG API waits for BitNet LLM to be healthy

## 🧪 Testing & Validation

### Basic Functionality Test
```bash
# Test health
curl http://localhost:8001/health

# Expected response:
# {
#   "status": "healthy",
#   "model": "BitNet b1.58 2B 4T",
#   "model_size_gb": 1.11,
#   "deployment_type": "external_model"
# }
```

### Inference Test
```bash
# Test generation
curl -X POST http://localhost:8001/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"The capital of France is","max_tokens":5}'

# Expected response:
# {
#   "generated_text": "Answer: Paris.",
#   "execution_time_seconds": 1.4,
#   "model": "BitNet b1.58 2B 4T"
# }
```

### Performance Test
```bash
# Measure response time
time curl -X POST http://localhost:8001/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Explain quantum computing","max_tokens":50}' \
  -s > /dev/null

# Expected: ~1-3 seconds for 50 tokens
```

## 🔍 Troubleshooting

### Common Issues

**Container won't start**:
```bash
# Check logs
docker logs neo4j-rag-demo-bitnet

# Check model file
docker exec neo4j-rag-demo-bitnet ls -lh /app/models/
```

**Model not found**:
```bash
# Verify model mount
ls -lh bitnet-llm/models/ggml-model-i2_s.gguf

# Should show ~1.1GB file
```

**Inference timeout**:
```bash
# Increase timeout
docker compose down
# Edit docker-compose.yml: MODEL_WAIT_TIMEOUT=120
docker compose up -d bitnet-llm
```

### Health Check Commands

```bash
# Container status
docker compose ps bitnet-llm

# Service health
curl http://localhost:8001/health

# Detailed logs
docker logs neo4j-rag-demo-bitnet --tail 50
```

## 📈 Performance Metrics

### Benchmarks (MacOS M1/M2)
- **Startup time**: ~30 seconds
- **Memory usage**: 1.5GB peak
- **Inference speed**: ~30 tokens/second
- **Response time**: 1-3 seconds (50 tokens)

### Size Optimization
- **Original**: 3.2GB (embedded model)
- **Optimized**: 334MB (external model)
- **Reduction**: 90% smaller container

## 🛠️ Development

### Rebuild Container
```bash
cd bitnet-llm
docker compose -f docker-compose-bitnet-minimal.yml build --no-cache
```

### Update Model
```bash
# Replace model file
cp new-model.gguf bitnet-llm/models/ggml-model-i2_s.gguf

# Restart service
docker compose restart bitnet-llm
```

### Modify Configuration
```bash
# Edit docker-compose.yml
vim docker-compose.yml

# Apply changes
docker compose up -d bitnet-llm
```

## 📚 Related Documentation

- [Neo4j RAG Demo README](../README.md)
- [BitNet.cpp GitHub](https://github.com/microsoft/BitNet)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Status**: ✅ Production Ready | **Container Size**: 334MB | **Model**: BitNet 1.58B 2B 4T