# BitNet File Management & Git Best Practices

**Managing large AI model files and compilation artifacts in Git repositories**

---

## 📋 Overview

BitNet.cpp involves large model files (1GB+), compiled binaries, and build artifacts that should **NOT** be stored in Git. This guide explains what to commit, what to ignore, and best practices for handling large AI files.

---

## 🎯 File Classification

### ✅ **COMMIT to Git** (Source Code & Configuration)

| File Type | Examples | Size | Why Include |
|-----------|----------|------|-------------|
| **Source Code** | `*.py`, `*.cpp`, `*.h`, `*.c` | < 1MB | Essential for building |
| **Build Scripts** | `CMakeLists.txt`, `Makefile` | < 100KB | Build configuration |
| **Documentation** | `README.md`, `docs/` | < 10MB | User guidance |
| **Requirements** | `requirements.txt`, `setup.py` | < 10KB | Dependencies |
| **Utilities** | `utils/`, `scripts/` | < 1MB | Development tools |
| **Preset Configs** | `preset_kernels/` | < 500KB | Pre-generated configs |
| **Git Config** | `.gitignore`, `.gitmodules` | < 10KB | Repository management |

### ❌ **DO NOT COMMIT** (Large Files & Build Artifacts)

| File Type | Examples | Size | Alternative Solution |
|-----------|----------|------|---------------------|
| **Model Files** | `*.gguf`, `*.bin`, `*.model` | 100MB - 10GB | Container Registry |
| **Compiled Binaries** | `*.exe`, `*.so`, `*.dll` | 1MB - 100MB | Build from source |
| **Build Artifacts** | `build/`, `CMakeFiles/` | 10MB - 1GB | Regenerate on build |
| **Downloaded Models** | `models/`, `checkpoints/` | 1GB+ | Download during build |
| **Generated Kernels** | `bitnet-lut-kernels.h` | 10KB - 1MB | Generate during build |
| **Temporary Files** | `*.tmp`, `*.log`, `*.cache` | Various | Ephemeral |

---

## 🔧 Implementation

### Current `.gitignore` Configuration

Our `.gitignore` now includes comprehensive BitNet patterns:

```bash
# Large model files (should use Git LFS or container registry)
*.gguf
*.gguf.json
*.bin
*.model
*.vocab
*.tokenizer
*.safetensors

# BitNet build artifacts  
BitNet/build/
BitNet/*/build/

# BitNet compiled binaries
BitNet/**/*.exe
BitNet/**/*.so
BitNet/**/*.dylib
BitNet/**/*.dll
BitNet/**/*.a

# BitNet model downloads and cache
BitNet/models/
BitNet/*/models/
BitNet/3rdparty/llama.cpp/models/*.gguf
BitNet/checkpoints/
BitNet/gpu/checkpoints/

# BitNet generated kernels (except preset ones)
BitNet/include/bitnet-lut-kernels.h
```

### Verification Commands

```bash
# Check what files are tracked
git ls-files BitNet/ | head -10

# Check what files are ignored  
git status --ignored BitNet/

# Find large files that might need attention
find BitNet -type f -size +10M | head -10

# Check total size of tracked BitNet files
git ls-files BitNet/ | xargs du -ch | tail -1
```

---

## 🌍 Alternative Solutions for Large Files

### Option 1: Container Registry (Recommended) ✅

**What we implemented**: Store compiled BitNet + models in Docker containers

```bash
# Pre-built containers with everything included
docker pull ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest        # 3.2GB
docker pull ghcr.io/ma3u/ms-agentf-neo4j/bitnet-optimized:latest    # 2.5GB

# Benefits:
# - No Git repository bloat
# - Cross-platform compatibility  
# - Version control for binary artifacts
# - Easy deployment
```

### Option 2: Git LFS (Large File Storage)

For files you need to version control but are too large for Git:

```bash
# Install Git LFS
git lfs install

# Track large file types
git lfs track "*.gguf"
git lfs track "*.bin"
git lfs track "BitNet/models/*"

# Add .gitattributes to repository
git add .gitattributes
git commit -m "Add Git LFS tracking for model files"
```

### Option 3: External Storage + Download Scripts

Store models externally and download during build:

```bash
# In Dockerfile or build script
RUN wget https://huggingface.co/microsoft/BitNet-b1.58-2B-4T-gguf/resolve/main/ggml-model-i2_s.gguf \
    -O models/ggml-model-i2_s.gguf
```

### Option 4: Submodule for Models

Separate repository for large files:

```bash
# Add model repository as submodule
git submodule add https://github.com/user/bitnet-models.git BitNet/models
git submodule update --init --recursive
```

---

## 📊 Repository Size Analysis

### Before Cleanup (Hypothetical)
```
Repository Size: 5.2GB
├── Source Code: 50MB
├── BitNet Models: 4.8GB  ❌ Too large for Git
├── Build Artifacts: 300MB ❌ Should be generated
└── Documentation: 50MB
```

### After Cleanup (Recommended)
```
Repository Size: 100MB
├── Source Code: 50MB      ✅ Essential
├── Documentation: 30MB    ✅ Helpful  
├── Configuration: 10MB    ✅ Required
└── Scripts/Utils: 10MB    ✅ Useful

Models stored in: Container Registry (ghcr.io) ✅
```

---

## 🛡️ Best Practices

### 1. **Repository Hygiene**

```bash
# Check repository size regularly
git count-objects -vH

# Find large files in history
git rev-list --objects --all | \
    git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
    awk '/^blob/ {print substr($0,6)}' | sort --numeric-sort --key=2 | tail -10

# Remove accidentally committed large files
git filter-branch --force --index-filter \
    'git rm --cached --ignore-unmatch BitNet/models/*.gguf' \
    --prune-empty --tag-name-filter cat -- --all
```

### 2. **Pre-commit Hooks**

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-large-files
        name: Check for large files
        entry: bash -c 'find . -type f -size +50M | head -1 | grep -q . && echo "Large files found!" && exit 1 || exit 0'
        language: system
```

### 3. **Build Process**

```dockerfile
# Dockerfile should handle large files
FROM ubuntu:22.04 AS builder

# Download models during build, not from Git
RUN huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf \
    --local-dir /app/models/

# Copy source code only
COPY BitNet/src/ /build/src/
COPY BitNet/utils/ /build/utils/
COPY BitNet/CMakeLists.txt /build/
```

### 4. **Documentation**

Always document what files are excluded and why:

```markdown
## Getting Started

1. Clone repository: `git clone https://github.com/user/repo.git`
2. Pull models: `docker pull ghcr.io/user/repo/bitnet-models:latest`
3. Build: `docker-compose up -d`

Note: Model files (*.gguf) are not stored in Git due to size (1GB+).
They are available as pre-built containers.
```

---

## 🔍 Current Status Check

### Verification Commands

```bash
# Check what files are currently tracked in BitNet/
git ls-files BitNet/ | wc -l

# Find large files that might need attention
find BitNet -type f -size +1M 2>/dev/null

# Check repository size
du -sh .git/

# Verify .gitignore is working
git status --ignored BitNet/
```

### Recommended Actions

1. **Verify no large files are tracked**:
   ```bash
   git ls-files BitNet/ | xargs ls -lh | awk '$5 > 1000000 {print $5, $9}'
   ```

2. **Clean up any accidentally tracked large files**:
   ```bash
   # Remove from index but keep in working directory
   git rm --cached BitNet/models/*.gguf
   git rm --cached BitNet/**/*.so
   ```

3. **Verify container registry is working**:
   ```bash
   docker pull ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest
   ```

---

## 📝 Summary & Recommendations

### ✅ What We've Implemented

1. **Comprehensive `.gitignore`**: Added patterns for all BitNet large files
2. **Container Registry**: Models stored in `ghcr.io/ma3u/ms-agentf-neo4j/`
3. **Documentation**: Clear guidance on what to commit vs ignore
4. **Build Process**: Dockerfiles handle model downloads

### 💯 Best Practice Strategy

```
Git Repository (Source Code):          Container Registry (Binaries):
┌─────────────────────────────┐          ┌─────────────────────────────┐
│ ✅ Source code (*.py, *.cpp)       │          │ ✅ Compiled binaries (llama-cli) │
│ ✅ Build scripts (CMakeLists.txt) │          │ ✅ Model files (*.gguf)         │
│ ✅ Documentation (README.md)     │          │ ✅ Runtime environment           │
│ ✅ Configuration files           │          │ ✅ Dependencies                  │
│ ✅ Utilities and scripts         │          │ ✅ Complete deployment package   │
│                              │          │                               │
│ Size: ~100MB                 │          │ Size: 1.4GB - 3.2GB          │
│ Clone time: 30 seconds       │          │ Pull time: 2-5 minutes       │
│ Purpose: Development         │          │ Purpose: Deployment           │
└─────────────────────────────┘          └─────────────────────────────┘
```

### 🚀 Developer Workflow

```bash
# 1. Developer clones source code (fast)
git clone https://github.com/ma3u/ms-agentf-neo4j.git
cd ms-agentf-neo4j

# 2. Uses pre-built containers (convenient)  
docker-compose -f scripts/docker-compose.ghcr.yml up -d

# 3. Makes source code changes
vim BitNet/src/some_file.cpp

# 4. Commits only source changes (small)
git add BitNet/src/
git commit -m "Improve BitNet inference speed"

# 5. CI/CD rebuilds containers automatically
# New images published to ghcr.io with latest changes
```

### 📖 Documentation Links

- **Main Documentation**: [BITNET-COMPLETE-GUIDE.md](BITNET-COMPLETE-GUIDE.md)
- **Container Registry**: [CONTAINER_REGISTRY.md](CONTAINER_REGISTRY.md) 
- **Build Success**: [BITNET-SUCCESS.md](BITNET-SUCCESS.md)
- **Repository**: https://github.com/ma3u/ms-agentf-neo4j

---

**🎉 Result: Clean repository + Powerful deployment**

*Source code in Git, binaries in containers – the best of both worlds!*

---

**Document Version**: 1.0  
**Last Updated**: October 18, 2025  
**Status**: Implementation Complete ✅
