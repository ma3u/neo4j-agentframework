"""
BitNet.cpp Minimal Server - External Model Support
Optimized for ultra-minimal containers with volume-mounted models
"""

import os
import subprocess
import logging
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BitNet LLM API (Minimal Deployment)",
    description="Microsoft BitNet b1.58 with External Model Support",
    version="2.1.0-minimal"
)

# Configuration
BITNET_BINARY = os.getenv("BITNET_BINARY", "/app/bin/llama-cli")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/ggml-model-i2_s.gguf")
BITNET_THREADS = int(os.getenv("BITNET_THREADS", "4"))
BITNET_CTX_SIZE = int(os.getenv("BITNET_CTX_SIZE", "2048"))
MODEL_WAIT_TIMEOUT = int(os.getenv("MODEL_WAIT_TIMEOUT", "300"))  # 5 minutes


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Input text prompt")
    max_tokens: int = Field(default=150, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    context: Optional[str] = Field(default=None, description="Additional context from RAG")


class GenerateResponse(BaseModel):
    generated_text: str
    model: str = "BitNet-b1.58-2B-4T"
    tokens_generated: int
    inference_time_ms: float


def wait_for_model(timeout_seconds=300):
    """Wait for model file to become available (for volume mounts or downloads)"""
    logger.info(f"⏳ Waiting for model file: {MODEL_PATH}")
    logger.info(f"   Timeout: {timeout_seconds} seconds")
    
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if os.path.exists(MODEL_PATH):
            size = os.path.getsize(MODEL_PATH)
            if size > 1_000_000_000:  # Model should be > 1GB
                logger.info(f"✅ Model found! Size: {size / (1024**3):.2f}GB")
                return True
            else:
                logger.info(f"⏳ Model file exists but small ({size / (1024**2):.1f}MB), waiting for download to complete...")
        else:
            logger.info("⏳ Model file not found, waiting...")
        
        time.sleep(5)  # Check every 5 seconds
    
    logger.error(f"❌ Model not available after {timeout_seconds} seconds")
    return False


def verify_setup():
    """Verify BitNet binary and model exist"""
    issues = []

    if not os.path.exists(BITNET_BINARY):
        issues.append(f"BitNet binary not found at {BITNET_BINARY}")

    if not os.path.exists(MODEL_PATH):
        issues.append(f"Model file not found at {MODEL_PATH}")
    else:
        size = os.path.getsize(MODEL_PATH)
        if size == 0:
            issues.append(f"Model file is empty (0 bytes)")
        elif size < 1_000_000_000:  # < 1GB
            issues.append(f"Model file seems incomplete ({size / (1024**2):.1f}MB)")
        else:
            logger.info(f"✅ Model file size: {size / (1024**3):.2f}GB")

    if issues:
        for issue in issues:
            logger.error(f"❌ {issue}")
        return False

    logger.info(f"✅ BitNet binary: {BITNET_BINARY}")
    logger.info(f"✅ Model: {MODEL_PATH}")
    return True


@app.on_event("startup")
async def startup_event():
    """Wait for model and verify setup on startup"""
    logger.info("🚀 Starting BitNet.cpp Minimal Server")
    logger.info("=" * 50)
    logger.info(f"Binary: {BITNET_BINARY}")
    logger.info(f"Model: {MODEL_PATH}")
    logger.info(f"Threads: {BITNET_THREADS}")
    logger.info(f"Context Size: {BITNET_CTX_SIZE}")
    logger.info("=" * 50)
    
    # Wait for model to be available (handles volume mounts and downloads)
    if not wait_for_model(MODEL_WAIT_TIMEOUT):
        logger.warning("⚠️  Model not available, server will start but inference will fail until model is ready")
        return
    
    # Verify complete setup
    if verify_setup():
        logger.info("🎉 BitNet.cpp minimal server ready for inference!")
    else:
        logger.warning("⚠️  Setup incomplete, some features may not work")


@app.get("/health")
async def health():
    """Health check endpoint with model status"""
    try:
        model_exists = os.path.exists(MODEL_PATH)
        model_size = os.path.getsize(MODEL_PATH) if model_exists else 0
        binary_exists = os.path.exists(BITNET_BINARY)
        
        # Determine status
        if model_exists and model_size > 1_000_000_000 and binary_exists:
            status = "healthy"
        elif binary_exists and not model_exists:
            status = "waiting_for_model"
        elif binary_exists and model_exists and model_size < 1_000_000_000:
            status = "downloading_model"
        else:
            status = "degraded"

        return {
            "status": status,
            "model": "BitNet b1.58 2B 4T",
            "model_path": MODEL_PATH,
            "model_exists": model_exists,
            "model_size_gb": round(model_size / (1024**3), 2),
            "binary_exists": binary_exists,
            "binary_path": BITNET_BINARY,
            "quantization": "i2_s (1.58-bit ternary)",
            "mode": "minimal_deployment",
            "deployment_type": "external_model",
            "threads": BITNET_THREADS,
            "context_size": BITNET_CTX_SIZE
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@app.get("/model-info")
async def model_info():
    """Get detailed model information"""
    model_exists = os.path.exists(MODEL_PATH)
    model_size = os.path.getsize(MODEL_PATH) if model_exists else 0
    
    return {
        "name": "BitNet-b1.58-2B-4T",
        "type": "BitNet b1.58",
        "quantization": "i2_s (ternary: -1, 0, +1)",
        "parameters": "2.4B",
        "model_path": MODEL_PATH,
        "model_ready": model_exists and model_size > 1_000_000_000,
        "model_size_gb": round(model_size / (1024**3), 2),
        "inference_backend": "llama-cli (BitNet.cpp)",
        "optimization": "1.58-bit quantization",
        "memory_efficiency": "87% reduction vs FP16",
        "deployment_mode": "Ultra-minimal container (200MB)",
        "model_storage": "External volume or download"
    }


@app.get("/wait-for-model")
async def wait_for_model_endpoint():
    """Endpoint to manually trigger model wait"""
    if wait_for_model(60):  # 60 second timeout for API call
        return {"status": "ready", "message": "Model is now available"}
    else:
        return {"status": "timeout", "message": "Model not available within timeout"}


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate text using BitNet.cpp inference via llama-cli
    """
    import time
    start_time = time.time()

    # Check if model is available before attempting inference
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=503,
            detail="Model not available. Please wait for download/mount to complete."
        )
    
    model_size = os.path.getsize(MODEL_PATH)
    if model_size < 1_000_000_000:
        raise HTTPException(
            status_code=503,
            detail=f"Model incomplete ({model_size / (1024**2):.1f}MB). Please wait for download to complete."
        )

    try:
        # Construct prompt with context if provided
        if request.context:
            full_prompt = f"""Use the following context to answer the question.

Context:
{request.context}

Question: {request.prompt}

Answer:"""
        else:
            full_prompt = request.prompt

        logger.info(f"Running BitNet.cpp inference: {full_prompt[:80]}...")

        # Build llama-cli command
        cmd = [
            BITNET_BINARY,
            "-m", MODEL_PATH,
            "-p", full_prompt,
            "-n", str(request.max_tokens),
            "-t", str(BITNET_THREADS),
            "-c", str(BITNET_CTX_SIZE),
            "--temp", str(request.temperature),
            "-b", "1",  # batch size
            "--no-display-prompt"  # Don't echo the prompt
        ]

        # Run BitNet.cpp inference
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        if result.returncode != 0:
            logger.error(f"BitNet.cpp failed: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"BitNet inference failed: {result.stderr[:200]}"
            )

        # Extract generated text from output
        generated_text = result.stdout.strip()

        # Clean up the output (remove any llama.cpp metadata)
        lines = generated_text.split('\n')
        cleaned_lines = [
            line for line in lines
            if not line.startswith('llama') and
               not line.startswith('ggml') and
               line.strip()
        ]
        generated_text = '\n'.join(cleaned_lines).strip()

        # Calculate actual tokens (rough approximation)
        tokens_generated = len(generated_text.split())

        inference_time = (time.time() - start_time) * 1000

        logger.info(f"✅ Generated {tokens_generated} tokens in {inference_time:.2f}ms")

        return GenerateResponse(
            generated_text=generated_text,
            tokens_generated=tokens_generated,
            inference_time_ms=round(inference_time, 2)
        )

    except subprocess.TimeoutExpired:
        logger.error("BitNet inference timeout")
        raise HTTPException(status_code=504, detail="Inference timeout (>30s)")
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@app.post("/chat")
async def chat(request: GenerateRequest):
    """
    Chat endpoint with conversational formatting
    Optimized for RAG pipeline integration
    """
    # Add chat formatting to prompt
    chat_prompt = f"User: {request.prompt}\nAssistant:"

    if request.context:
        chat_prompt = f"Context: {request.context}\n\n{chat_prompt}"

    # Update request with formatted prompt
    request.prompt = chat_prompt

    return await generate(request)


@app.get("/test-inference")
async def test_inference():
    """
    Quick test endpoint to verify BitNet.cpp is working
    """
    # Check model availability first
    if not os.path.exists(MODEL_PATH):
        return {
            "status": "model_not_found",
            "message": "Model file not available",
            "model_path": MODEL_PATH
        }
    
    model_size = os.path.getsize(MODEL_PATH)
    if model_size < 1_000_000_000:
        return {
            "status": "model_incomplete",
            "message": f"Model downloading ({model_size / (1024**2):.1f}MB)",
            "model_path": MODEL_PATH
        }

    try:
        test_prompt = "The capital of France is"
        cmd = [
            BITNET_BINARY,
            "-m", MODEL_PATH,
            "-p", test_prompt,
            "-n", "5",
            "-t", "2",
            "--no-display-prompt"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        return {
            "status": "success" if result.returncode == 0 else "failed",
            "test_prompt": test_prompt,
            "output": result.stdout[:200],
            "inference_working": result.returncode == 0,
            "model_size_gb": round(model_size / (1024**3), 2)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Starting BitNet.cpp Minimal Inference Server")
    logger.info("=" * 60)
    logger.info(f"Binary: {BITNET_BINARY}")
    logger.info(f"Model: {MODEL_PATH}")
    logger.info(f"Threads: {BITNET_THREADS}")
    logger.info(f"Context Size: {BITNET_CTX_SIZE}")
    logger.info(f"Model Wait Timeout: {MODEL_WAIT_TIMEOUT}s")
    logger.info("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )