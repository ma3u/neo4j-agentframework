"""
Real BitNet.cpp Server - Actual Inference with llama-cli
Provides REST API using actual Microsoft BitNet.cpp binary
"""

import os
import subprocess
import logging
import tempfile
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BitNet LLM API (Real Inference)",
    description="Microsoft BitNet b1.58 with Real llama-cli Inference",
    version="2.0.0-real"
)

# Configuration
BITNET_BINARY = os.getenv("BITNET_BINARY", "/usr/local/bin/llama-cli")
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf")
BITNET_THREADS = int(os.getenv("BITNET_THREADS", "4"))
BITNET_CTX_SIZE = int(os.getenv("BITNET_CTX_SIZE", "2048"))


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
        else:
            logger.info(f"Model file size: {size / (1024**3):.2f} GB")

    if issues:
        for issue in issues:
            logger.error(f"❌ {issue}")
        raise RuntimeError("BitNet setup incomplete. " + "; ".join(issues))

    logger.info(f"✅ BitNet binary: {BITNET_BINARY}")
    logger.info(f"✅ Model: {MODEL_PATH}")


@app.on_event("startup")
async def startup_event():
    """Verify setup on startup"""
    logger.info("🚀 Starting Real BitNet.cpp Server")
    try:
        verify_setup()
        logger.info("✅ Real BitNet.cpp inference ready")
    except Exception as e:
        logger.error(f"❌ Startup verification failed: {e}")
        # Continue anyway for health checks


@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        model_exists = os.path.exists(MODEL_PATH)
        model_size = os.path.getsize(MODEL_PATH) if model_exists else 0
        binary_exists = os.path.exists(BITNET_BINARY)

        status = "healthy" if (model_exists and model_size > 0 and binary_exists) else "degraded"

        return {
            "status": status,
            "model": "BitNet b1.58 2B 4T",
            "model_path": MODEL_PATH,
            "model_exists": model_exists,
            "model_size_gb": round(model_size / (1024**3), 2),
            "binary_exists": binary_exists,
            "binary_path": BITNET_BINARY,
            "quantization": "i2_s (1.58-bit ternary)",
            "mode": "real_inference",
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
    return {
        "name": "BitNet-b1.58-2B-4T",
        "type": "BitNet b1.58",
        "quantization": "i2_s (ternary: -1, 0, +1)",
        "parameters": "2.4B",
        "model_path": MODEL_PATH,
        "inference_backend": "llama-cli (BitNet.cpp)",
        "optimization": "1.58-bit quantization",
        "memory_efficiency": "87% reduction vs FP16",
        "mode": "Production-ready real inference"
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate text using real BitNet.cpp inference via llama-cli
    """
    import time
    start_time = time.time()

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
        # Filter out llama.cpp log lines and keep only generated text
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
            "inference_working": result.returncode == 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 Starting Real BitNet.cpp Inference Server")
    logger.info("=" * 60)
    logger.info(f"Binary: {BITNET_BINARY}")
    logger.info(f"Model: {MODEL_PATH}")
    logger.info(f"Threads: {BITNET_THREADS}")
    logger.info(f"Context Size: {BITNET_CTX_SIZE}")
    logger.info("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
