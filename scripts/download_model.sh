#!/bin/bash
# BitNet Model Download Script
# Downloads BitNet model if not present in mounted volume
# Designed for ultra-minimal container deployment

set -e

MODEL_PATH="${MODEL_PATH:-/app/models/ggml-model-i2_s.gguf}"
MODEL_DIR="$(dirname "$MODEL_PATH")"
HF_MODEL_ID="${HF_MODEL_ID:-microsoft/BitNet-b1.58-2B-4T-gguf}"

echo "🚀 BitNet Model Download Script"
echo "================================"
echo "Model path: $MODEL_PATH"
echo "Model directory: $MODEL_DIR"
echo "HuggingFace Model ID: $HF_MODEL_ID"

# Create models directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Check if model already exists
if [ -f "$MODEL_PATH" ]; then
    MODEL_SIZE=$(stat -c%s "$MODEL_PATH" 2>/dev/null || stat -f%z "$MODEL_PATH" 2>/dev/null || echo "0")
    if [ "$MODEL_SIZE" -gt 1000000000 ]; then  # > 1GB means valid model
        echo "✅ Model already exists ($(($MODEL_SIZE / 1024 / 1024 / 1024))GB)"
        echo "✅ Skipping download"
        exit 0
    else
        echo "⚠️  Model file exists but is too small ($(($MODEL_SIZE / 1024 / 1024))MB), re-downloading..."
        rm -f "$MODEL_PATH"
    fi
fi

echo "📥 Model not found, downloading from HuggingFace..."
echo "   This may take several minutes (1.1GB download)"

# Download using HuggingFace CLI
if command -v huggingface-cli >/dev/null 2>&1; then
    echo "🔄 Using huggingface-cli to download model..."
    huggingface-cli download "$HF_MODEL_ID" \
        --local-dir "$MODEL_DIR" \
        --local-dir-use-symlinks False
    
    # Check if the download created the expected file
    if [ ! -f "$MODEL_PATH" ]; then
        # Sometimes the file has a different name, let's find it
        DOWNLOADED_FILE=$(find "$MODEL_DIR" -name "*.gguf" -type f | head -n1)
        if [ -n "$DOWNLOADED_FILE" ] && [ -f "$DOWNLOADED_FILE" ]; then
            echo "📁 Found GGUF file: $DOWNLOADED_FILE"
            if [ "$DOWNLOADED_FILE" != "$MODEL_PATH" ]; then
                echo "🔄 Renaming to expected path: $MODEL_PATH"
                mv "$DOWNLOADED_FILE" "$MODEL_PATH"
            fi
        else
            echo "❌ No GGUF file found after download!"
            exit 1
        fi
    fi
else
    echo "❌ huggingface-cli not found, trying alternative download..."
    # Fallback to direct download (if available)
    echo "⚠️  Direct download not implemented, please use volume mount approach"
    exit 1
fi

# Verify download
if [ -f "$MODEL_PATH" ]; then
    MODEL_SIZE=$(stat -c%s "$MODEL_PATH" 2>/dev/null || stat -f%z "$MODEL_PATH" 2>/dev/null || echo "0")
    MODEL_SIZE_GB=$((MODEL_SIZE / 1024 / 1024 / 1024))
    
    if [ "$MODEL_SIZE" -gt 1000000000 ]; then  # > 1GB
        echo "✅ Model downloaded successfully!"
        echo "   Size: ${MODEL_SIZE_GB}GB"
        echo "   Path: $MODEL_PATH"
    else
        echo "❌ Downloaded model is too small (${MODEL_SIZE_GB}GB), something went wrong"
        exit 1
    fi
else
    echo "❌ Model download failed - file not found"
    exit 1
fi

echo "🎉 Model ready for inference!"