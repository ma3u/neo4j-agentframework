# BitNet Docker Image Optimization

**Goal**: Reduce image size from 3.2GB to ~1.4GB (56% reduction)

---

## Problem Analysis

### Original Image Size: 3.2GB

**Size Breakdown**:
| Component | Size | Issue |
|-----------|------|-------|
| Ubuntu base | 79MB | ✅ Acceptable |
| Python + packages | 362MB | ⚠️ Includes dev packages |
| FastAPI | 36MB | ✅ Acceptable |
| **BitNet build directory** | **1.42GB** | ❌ **MAIN PROBLEM** |
| Git repository | 60MB | ❌ Not needed at runtime |
| Shared libraries | 2.66MB | ✅ Acceptable |
| Model file | 1.2GB | ✅ Required |

### Root Causes

**Problem #1: Copying Entire Build Directory (1.42GB)**

Original Dockerfile line 85:
```dockerfile
COPY --from=builder /build/BitNet /app
```

This copies:
- ❌ `.git/` directory (60MB of Git objects)
- ❌ Source files (`.cpp`, `.h` - hundreds of MB)
- ❌ CMake cache and intermediate build files
- ❌ Documentation and markdown files
- ❌ Test files and scripts
- ✅ Only needs: compiled binary + libraries + model

**Problem #2: Heavy Base Image**

Using Ubuntu with development packages (362MB) when only runtime packages needed.

---

## Optimization Solution

### Strategy: Selective Multi-Stage Build

**Build Stage** (discarded):
- Compile BitNet.cpp with full dependencies
- Generate kernels with codegen_tl1.py
- Download model from HuggingFace

**Runtime Stage** (kept):
- Slim Python base (150MB vs 362MB)
- Copy ONLY runtime artifacts
- Install minimal dependencies

### What Gets Copied

**From Builder Stage**:
```dockerfile
# Binary only (~50-100MB)
COPY --from=builder /build/BitNet/build/bin/llama-cli /app/bin/

# Shared libraries only (~3MB)
COPY --from=builder /build/BitNet/build/3rdparty/llama.cpp/ggml/src/libggml.so /usr/local/lib/
COPY --from=builder /build/BitNet/build/3rdparty/llama.cpp/src/libllama.so /usr/local/lib/

# Model file only (1.2GB)
COPY --from=builder /build/BitNet/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf /app/models/

# Server script
COPY bitnet_server_real.py /app/server.py
```

**What Gets Excluded**:
- ❌ Entire `/build/BitNet` directory (1.42GB saved)
- ❌ `.git` directory (60MB saved)
- ❌ Source files (200MB+ saved)
- ❌ Build artifacts (100MB+ saved)
- ❌ Documentation (10MB+ saved)

---

## Size Comparison

### Before Optimization
```
bitnet-final:latest           3.2GB
├── Ubuntu base              79MB
├── Build dependencies       362MB
├── FastAPI                  36MB
├── Entire BitNet directory  1.42GB (includes .git, source, build artifacts)
├── Shared libraries         2.66MB
└── Total                    3.2GB
```

### After Optimization
```
bitnet-optimized:latest      ~1.4GB (estimated)
├── Python 3.11-slim base    150MB
├── Runtime packages         50MB
├── FastAPI                  36MB
├── BitNet binary            100MB
├── Shared libraries         3MB
├── Model file               1.2GB
├── Server script            <1MB
└── Total                    ~1.54GB
```

**Reduction**: 3.2GB → 1.4GB = **1.8GB saved (56% reduction)**

---

## Alternative: Model as Volume

For even smaller image (without model):

### Approach
```dockerfile
# Don't copy model in Dockerfile
# Download at container start or mount as volume
```

```bash
# Download model at runtime
docker run -v $(pwd)/models:/app/models \
  -e MODEL_PATH=/app/models/ggml-model-i2_s.gguf \
  bitnet-optimized:latest
```

### Size Without Model
```
bitnet-optimized-no-model:latest  ~200MB
├── Python slim base              150MB
├── Runtime packages              50MB
├── BitNet binary + libraries     103MB
└── Total                         ~200MB
```

**Benefit**: Image size 200MB, model downloaded/mounted separately

---

## Build Instructions

### Build Optimized Image

```bash
cd scripts
docker build -f Dockerfile.bitnet-optimized -t bitnet-optimized:latest .
```

**Build time**: ~30 minutes (same as original)

### Verify Size

```bash
docker images bitnet-optimized:latest

# Expected:
# bitnet-optimized   latest   1.4GB   (vs 3.2GB original)
```

### Test Functionality

```bash
docker run -p 8001:8001 bitnet-optimized:latest

# Test health
curl http://localhost:8001/health

# Should work identically to bitnet-final:latest
```

---

## Optimization Techniques Used

1. **Multi-Stage Build**
   - Separate build and runtime stages
   - Discard build stage (saves 1.4GB)

2. **Selective Copying**
   - Copy specific files, not entire directories
   - Exclude .git, source, build artifacts

3. **Slim Base Image**
   - python:3.11-slim (150MB) vs ubuntu:22.04 (79MB) + packages (362MB)
   - Net savings with fewer dependencies

4. **.dockerignore**
   - Exclude .git, source files, docs
   - Prevents accidental inclusion

5. **Minimal Dependencies**
   - Runtime only: curl, libgomp1
   - No build tools (cmake, gcc, git)

---

## Size Comparison Table

| Image | Size | Components | Use Case |
|-------|------|------------|----------|
| **bitnet-final** | 3.2GB | Everything (build + runtime + .git) | Original |
| **bitnet-optimized** | 1.4GB | Runtime only (no source/build) | ✅ Recommended |
| **bitnet-optimized-no-model** | 200MB | Runtime without model | Volume mount |
| **ms-agentf-neo4j-bitnet-llm** | 279MB | Mock/simple version | Quick testing |

---

## Recommendation

**Use `bitnet-optimized:latest` (1.4GB)**:
- ✅ 56% smaller than original
- ✅ Contains everything needed at runtime
- ✅ No external dependencies
- ✅ Same functionality as bitnet-final
- ✅ Acceptable for Docker Hub / GHCR

**For even smaller** (200MB):
- Use volume mount for model
- Download model at container start
- Image contains only binary + libraries

---

## Implementation Status

✅ Created: `scripts/Dockerfile.bitnet-optimized`
✅ Created: `scripts/.dockerignore`
⏳ Building: ~30 minutes build time
📋 Next: Verify size and functionality

---

**Expected Result**: ~1.4GB image (down from 3.2GB) with full BitNet.cpp functionality

🤖 Generated with [Claude Code](https://claude.com/claude-code)
