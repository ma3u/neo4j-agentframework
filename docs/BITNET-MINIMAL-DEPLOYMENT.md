# BitNet Ultra-Minimal Deployment Guide (200MB Container)

**Achieve 94% size reduction**: 3.2GB → 200MB container with external model storage

---

## 🎯 Overview

This guide implements the **ultra-minimal BitNet deployment** approach where the model is stored externally (volume mount or download), reducing container size from 3.2GB to ~200MB.

### Size Comparison
| Image | Size | Model Storage | Use Case |
|-------|------|---------------|----------|
| `bitnet-final` | 3.2GB | Embedded | Original build |
| `bitnet-optimized` | 1.4GB | Embedded | 56% reduction |
| **`bitnet-minimal`** | **200MB** | **External** | **94% reduction** |

---

## 🏗️ Architecture

### Minimal Container Contents
```
bitnet-minimal:latest (~200MB)
├── Python 3.11-slim base    150MB
├── Runtime packages         25MB
├── FastAPI                  20MB
├── BitNet binary            3MB
├── Shared libraries         2MB
└── Scripts & configs        <1MB
```

### External Model Storage
- **Volume Mount**: Pre-downloaded model mounted at `/app/models`
- **Runtime Download**: Model downloaded at container startup
- **Model Size**: 1.1GB (stored outside container)

---

## 🚀 Quick Start

### Option 1: Volume Mount (Recommended)

**Step 1**: Download model to host
```bash
# Create models directory
mkdir -p ./models

# Download BitNet model using HuggingFace CLI
pip install huggingface-hub
huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf \
    --local-dir ./models \
    --local-dir-use-symlinks False

# Verify download
ls -lh ./models/ggml-model-i2_s.gguf
# Expected: ~1.1GB file
```

**Step 2**: Build and run minimal container
```bash
cd scripts

# Build ultra-minimal image
docker build -f Dockerfile.bitnet-minimal -t bitnet-minimal:latest .

# Run with volume mount
docker run -d \
    --name bitnet-minimal \
    -p 8001:8001 \
    -v $(pwd)/models:/app/models:ro \
    -e MODEL_PATH=/app/models/ggml-model-i2_s.gguf \
    bitnet-minimal:latest
```

**Step 3**: Test functionality
```bash
# Check health
curl http://localhost:8001/health

# Test inference
curl -X POST http://localhost:8001/generate \
    -H 'Content-Type: application/json' \
    -d '{"prompt":"What is BitNet?","max_tokens":50}'
```

### Option 2: Runtime Download

**Run with automatic download**:
```bash
docker run -d \
    --name bitnet-minimal-download \
    -p 8001:8001 \
    -v bitnet-models:/app/models \
    -e HF_MODEL_ID=microsoft/BitNet-b1.58-2B-4T-gguf \
    bitnet-minimal:latest

# Monitor download progress
docker logs -f bitnet-minimal-download
```

---

## 📋 Docker Compose Deployment

### Volume Mount Approach
```bash
cd scripts

# Start with volume mount (fastest)
docker compose -f docker-compose-bitnet-minimal.yml \
    --profile volume-mount up -d

# Check status
docker compose -f docker-compose-bitnet-minimal.yml ps
```

### Runtime Download Approach
```bash
# Start with runtime download
docker compose -f docker-compose-bitnet-minimal.yml \
    --profile download up -d

# Monitor download progress
docker compose -f docker-compose-bitnet-minimal.yml \
    logs -f bitnet-minimal-download
```

### Full RAG Stack
```bash
# Deploy complete stack with minimal BitNet
docker compose -f docker-compose-bitnet-minimal.yml \
    --profile full-stack up -d
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `/app/models/ggml-model-i2_s.gguf` | Path to GGUF model file |
| `BITNET_BINARY` | `/app/bin/llama-cli` | BitNet binary location |
| `BITNET_THREADS` | `4` | CPU threads for inference |
| `BITNET_CTX_SIZE` | `2048` | Context window size |
| `MODEL_WAIT_TIMEOUT` | `300` | Seconds to wait for model |
| `HF_MODEL_ID` | `microsoft/BitNet-b1.58-2B-4T-gguf` | HuggingFace model ID |

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      memory: 1.5G      # Total memory (model + inference)
      cpus: '0.5'       # Half CPU core
    reservations:
      memory: 512M      # Minimum memory
```

---

## 🔧 Advanced Usage

### Custom Model Path
```bash
# Use different model file
docker run -d \
    -v $(pwd)/my-models:/app/models:ro \
    -e MODEL_PATH=/app/models/my-custom-model.gguf \
    bitnet-minimal:latest
```

### Performance Tuning
```bash
# Optimize for your hardware
docker run -d \
    -e BITNET_THREADS=8 \
    -e BITNET_CTX_SIZE=4096 \
    -e MODEL_WAIT_TIMEOUT=600 \
    bitnet-minimal:latest
```

### Network Storage Mount
```bash
# Mount network storage (NFS, SMB, etc.)
docker run -d \
    -v /mnt/network-storage/bitnet-models:/app/models:ro \
    bitnet-minimal:latest
```

---

## 🌐 Production Deployment

### Azure Container Apps

**Create resource group and container app**:
```bash
# Variables
RESOURCE_GROUP="rg-bitnet-minimal"
LOCATION="eastus"
APP_NAME="bitnet-minimal-app"
ACR_NAME="myregistry"

# Create container app with minimal resources
az containerapp create \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --image $ACR_NAME.azurecr.io/bitnet-minimal:latest \
    --cpu 0.25 \
    --memory 0.5Gi \
    --min-replicas 0 \
    --max-replicas 2 \
    --env-vars \
        MODEL_PATH=/app/models/ggml-model-i2_s.gguf \
        BITNET_THREADS=2 \
        MODEL_WAIT_TIMEOUT=600
```

**Mount Azure File Share**:
```bash
# Create file share for model storage
az storage share create \
    --name bitnet-models \
    --account-name mystorageaccount

# Upload model to file share
az storage file upload \
    --share-name bitnet-models \
    --source ./models/ggml-model-i2_s.gguf \
    --path ggml-model-i2_s.gguf

# Mount in container app
az containerapp update \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --mount-path /app/models \
    --azure-file-share-name bitnet-models \
    --azure-file-account-name mystorageaccount \
    --azure-file-account-key $ACCOUNT_KEY
```

### Kubernetes Deployment

**Persistent Volume**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: bitnet-models
spec:
  accessModes:
    - ReadOnlyMany
  resources:
    requests:
      storage: 2Gi
```

**Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bitnet-minimal
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bitnet-minimal
  template:
    metadata:
      labels:
        app: bitnet-minimal
    spec:
      containers:
      - name: bitnet
        image: bitnet-minimal:latest
        ports:
        - containerPort: 8001
        env:
        - name: MODEL_PATH
          value: /app/models/ggml-model-i2_s.gguf
        - name: BITNET_THREADS
          value: "2"
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        resources:
          limits:
            memory: "1.5Gi"
            cpu: "500m"
          requests:
            memory: "512Mi"
            cpu: "250m"
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: bitnet-models
```

---

## 🧪 Testing & Validation

### Size Verification
```bash
# Check image size
docker images bitnet-minimal:latest

# Expected output:
# REPOSITORY        TAG      SIZE
# bitnet-minimal   latest   ~200MB
```

### Functionality Tests
```bash
# Health check
curl http://localhost:8001/health
# Expected: {"status": "healthy", "deployment_type": "external_model"}

# Model info
curl http://localhost:8001/model-info
# Expected: {"deployment_mode": "Ultra-minimal container (200MB)"}

# Test inference
curl -X POST http://localhost:8001/generate \
    -H 'Content-Type: application/json' \
    -d '{"prompt":"The capital of France is","max_tokens":5}'
# Expected: Actual BitNet.cpp inference output

# Performance test
time curl -X POST http://localhost:8001/generate \
    -H 'Content-Type: application/json' \
    -d '{"prompt":"Explain quantum computing","max_tokens":100}'
```

### Load Testing
```bash
# Simple load test
for i in {1..10}; do
    curl -X POST http://localhost:8001/generate \
        -H 'Content-Type: application/json' \
        -d '{"prompt":"Test '$i'","max_tokens":20}' &
done
wait
```

---

## 🎯 Benefits & Trade-offs

### ✅ Benefits
- **94% size reduction**: 3.2GB → 200MB container
- **Flexible model management**: Update models without rebuilding images
- **Faster deployments**: Small container uploads quickly
- **Storage efficiency**: Share model across multiple containers
- **Cost optimization**: Minimal container resources

### ⚠️ Trade-offs
- **Startup complexity**: Model mounting/downloading required
- **Network dependency**: Initial model download needs internet
- **Storage management**: External model storage responsibility
- **Cold start time**: Model loading adds startup latency

### 💡 When to Use
- **✅ Production deployments** with shared model storage
- **✅ CI/CD pipelines** requiring fast container builds
- **✅ Multi-container environments** sharing same model
- **✅ Storage-constrained environments**
- **❌ Single-use containers** (use embedded model instead)

---

## 🔍 Troubleshooting

### Common Issues

**Model not found**:
```bash
# Check volume mount
docker exec bitnet-minimal ls -la /app/models/
# Should show ggml-model-i2_s.gguf (~1.1GB)

# Check health endpoint
curl http://localhost:8001/health
# Status should be "healthy", not "waiting_for_model"
```

**Download timeout**:
```bash
# Increase timeout
docker run -e MODEL_WAIT_TIMEOUT=1200 bitnet-minimal:latest

# Check download progress
docker logs -f bitnet-minimal-download
```

**Memory issues**:
```bash
# Increase container memory
docker run --memory=2g bitnet-minimal:latest

# Monitor memory usage
docker stats bitnet-minimal
```

**Performance issues**:
```bash
# Tune threading
docker run -e BITNET_THREADS=8 bitnet-minimal:latest

# Check CPU usage
docker stats bitnet-minimal
```

---

## 📚 Related Documentation

- [**BitNet Complete Guide**](BITNET-COMPLETE-GUIDE.md) - Full BitNet journey
- [**BitNet Deployment Guide**](BITNET_DEPLOYMENT_GUIDE.md) - Azure deployment
- [**BitNet Optimization**](BITNET_OPTIMIZATION.md) - Size optimization techniques
- [**Local Testing Guide**](LOCAL-TESTING-GUIDE.md) - Testing procedures

---

## 🎉 Conclusion

The **ultra-minimal BitNet deployment** achieves:

- **200MB container** (94% reduction from 3.2GB)
- **Full BitNet.cpp functionality** with external model storage
- **Production-ready** with volume mounting and auto-download
- **Flexible deployment options** for local, cloud, and Kubernetes

Perfect for production environments requiring **maximum storage efficiency** while maintaining **full BitNet inference capabilities**!

---

*Generated: October 2024 | Container Size: ~200MB | Deployment: Production Ready*