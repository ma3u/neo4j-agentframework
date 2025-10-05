"""
BitNet LLM Server - Simplified API-compatible version for RAG testing
Provides REST API for testing Neo4j RAG → BitNet integration
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BitNet LLM API",
    description="Microsoft BitNet b1.58 Mock Service for RAG Testing",
    version="1.0.0-simple"
)

# Model configuration
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "/app/bitnet/BitNet/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
)


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Input text prompt")
    max_tokens: int = Field(default=150, ge=1, le=2048, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    context: Optional[str] = Field(default=None, description="Additional context from RAG")


class GenerateResponse(BaseModel):
    generated_text: str
    model: str = "BitNet-b1.58-2B-4T"
    tokens_generated: int


@app.get("/health")
async def health():
    """Health check endpoint"""
    model_exists = os.path.exists(MODEL_PATH)
    return {
        "status": "healthy" if model_exists else "model_not_found",
        "model": "BitNet b1.58 2B 4T",
        "model_path": MODEL_PATH,
        "model_exists": model_exists,
        "quantization": "i2_s (1.58-bit)",
        "mode": "simplified_api"
    }


@app.get("/model-info")
async def model_info():
    """Get model information"""
    return {
        "name": "BitNet-b1.58-2B-4T",
        "type": "BitNet b1.58",
        "quantization": "i2_s (ternary: -1, 0, +1)",
        "parameters": "2B",
        "model_path": MODEL_PATH,
        "inference_backend": "Simplified API for testing",
        "note": "This is a mock service for RAG pipeline testing"
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    Generate text using BitNet LLM (Mock for testing)
    """
    try:
        logger.info(f"Generating response for prompt: {request.prompt[:50]}...")

        # Construct full prompt with context if provided
        full_prompt = request.prompt
        if request.context:
            full_prompt = f"Context: {request.context}\n\nQuestion: {request.prompt}\n\nAnswer:"

        # Mock generation for testing the pipeline
        # In production, this would call the actual BitNet.cpp inference
        if request.context:
            generated = f"Based on the provided context, {request.prompt.lower()} BitNet is a 1.58-bit quantized LLM that provides efficient inference with minimal computational requirements."
        else:
            generated = f"BitNet-b1.58 model response: {request.prompt} is processed using ternary quantization for optimal efficiency."

        # Limit response to max_tokens (rough approximation)
        words = generated.split()
        if len(words) > request.max_tokens // 2:  # Rough word-to-token ratio
            generated = " ".join(words[:request.max_tokens // 2])

        return GenerateResponse(
            generated_text=generated,
            tokens_generated=len(generated.split())
        )

    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")


@app.post("/chat")
async def chat(request: GenerateRequest):
    """
    Chat endpoint with RAG context integration
    Specifically designed for RAG pipeline integration
    """
    # Add chat formatting
    chat_prompt = f"Human: {request.prompt}\nAssistant:"

    if request.context:
        chat_prompt = f"Context: {request.context}\n\n{chat_prompt}"

    request.prompt = chat_prompt
    return await generate(request)


if __name__ == "__main__":
    logger.info("Starting BitNet LLM Server (Simplified API)...")
    logger.info(f"Model path: {MODEL_PATH}")
    logger.info(f"Mode: API-compatible mock for RAG pipeline testing")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
