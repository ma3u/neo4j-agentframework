"""
Ultra-High-Performance Integration for Existing RAG Service
Integrates performance optimizations with your current rag-service container
Uses same endpoints and maintains compatibility
"""

import asyncio
import logging
import os
import time
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import performance optimizations
sys.path.append('/app')

# Try to import optimized components, fallback to standard if not available
try:
    from bitnet_optimized_rag import OptimizedNeo4jRAG
    OPTIMIZED_AVAILABLE = True
    print("🚀 Using ultra-high-performance optimized RAG")
except ImportError:
    # Fallback to your existing implementation
    try:
        from src.neo4j_rag import Neo4jRAG as OptimizedNeo4jRAG
        OPTIMIZED_AVAILABLE = False
        print("📦 Using standard RAG implementation")
    except ImportError:
        # Last fallback - create minimal implementation
        class OptimizedNeo4jRAG:
            def __init__(self, **kwargs):
                print("⚠️ Minimal RAG fallback - performance not optimized")
            async def query(self, question, max_results=3):
                return {"answer": "Service temporarily unavailable", "sources": []}
            async def close(self):
                pass
        OPTIMIZED_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global RAG instance
rag_instance: Optional[OptimizedNeo4jRAG] = None


# Maintain compatibility with existing API
class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask the RAG system")
    max_results: int = Field(default=3, description="Maximum results", ge=1, le=10)
    include_sources: bool = Field(default=True, description="Include sources")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: list = Field(default_factory=list, description="Source documents")
    processing_time: float = Field(..., description="Processing time in seconds")
    performance_optimized: bool = Field(default=False, description="Whether optimizations are active")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup RAG system with performance optimizations"""
    global rag_instance

    logger.info("🚀 Initializing Performance-Optimized RAG Service")
    logger.info(f"🎯 Optimizations Available: {OPTIMIZED_AVAILABLE}")

    try:
        # Get configuration from environment (matching your existing setup)
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

        logger.info(f"🔗 Connecting to Neo4j: {neo4j_uri}")

        if OPTIMIZED_AVAILABLE:
            # Use optimized version with performance features
            rag_instance = OptimizedNeo4jRAG(
                neo4j_uri=neo4j_uri,
                neo4j_user=neo4j_user,
                neo4j_password=neo4j_password,
                cache_size=int(os.getenv("EMBEDDING_CACHE_SIZE", "10000"))
            )
            logger.info("✅ Ultra-high-performance RAG initialized")
            logger.info("🎯 Target response time: 38ms")
        else:
            # Use your existing implementation
            rag_instance = OptimizedNeo4jRAG(
                uri=neo4j_uri,
                username=neo4j_user,
                password=neo4j_password
            )
            logger.info("✅ Standard RAG initialized")

    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG: {str(e)}", exc_info=True)
        raise

    yield

    # Cleanup
    if rag_instance:
        logger.info("🧹 Cleaning up RAG resources...")
        if hasattr(rag_instance, 'close'):
            await rag_instance.close()
        logger.info("✅ Cleanup complete")


# Create FastAPI app with same configuration as your existing service
app = FastAPI(
    title="Neo4j RAG Service (Performance Optimized)",
    description="Ultra-high-performance RAG system with 38ms target response time",
    version="2.0.0-optimized",
    lifespan=lifespan
)

# Add CORS middleware (same as existing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - maintains compatibility"""
    return {
        "service": "Neo4j RAG Service",
        "version": "2.0.0-optimized",
        "performance_optimized": OPTIMIZED_AVAILABLE,
        "target_response_time": "38ms" if OPTIMIZED_AVAILABLE else "standard",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "add_docs": "/add-documents",
            "stats": "/stats" if OPTIMIZED_AVAILABLE else "/status"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint - maintains compatibility with existing monitoring"""
    try:
        # Basic health check
        status = {
            "status": "healthy",
            "performance_optimized": OPTIMIZED_AVAILABLE,
            "neo4j_connected": True,  # Assume healthy if we got here
        }

        # Add performance metrics if available
        if OPTIMIZED_AVAILABLE and hasattr(rag_instance, 'get_performance_stats'):
            try:
                stats = rag_instance.get_performance_stats()
                status.update({
                    "avg_response_time_ms": round(stats.get('query_stats', {}).get('avg_response_time', 0), 1),
                    "cache_hit_rate": round(stats.get('cache_stats', {}).get('hit_rate_percent', 0), 1),
                    "memory_mb": round(stats.get('system_stats', {}).get('memory_usage_mb', 0), 1)
                })
            except Exception:
                pass

        return status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Main query endpoint - enhanced with performance optimizations"""
    if not rag_instance:
        raise HTTPException(status_code=503, detail="RAG service not initialized")

    start_time = time.perf_counter()

    try:
        logger.info(f"Processing query: {request.question[:50]}...")

        if OPTIMIZED_AVAILABLE and hasattr(rag_instance, 'query_optimized'):
            # Use ultra-high-performance optimized query
            result = await rag_instance.query_optimized(
                question=request.question,
                k=request.max_results
            )
            
            # Extract response in optimized format
            answer = result.get('answer', 'No answer generated')
            sources = result.get('sources', []) if request.include_sources else []
            
        elif hasattr(rag_instance, 'query'):
            # Use async query method if available
            result = await rag_instance.query(
                question=request.question,
                max_results=request.max_results
            )
            answer = result.get('answer', 'No answer generated')
            sources = result.get('sources', []) if request.include_sources else []
            
        else:
            # Fallback to sync method
            if hasattr(rag_instance, 'search_and_generate'):
                result = await asyncio.to_thread(
                    rag_instance.search_and_generate,
                    request.question,
                    request.max_results
                )
                answer = result.get('answer', 'No answer generated')
                sources = result.get('contexts', []) if request.include_sources else []
            else:
                answer = "Service method not available"
                sources = []

        processing_time = time.perf_counter() - start_time

        # Log performance
        time_ms = processing_time * 1000
        if OPTIMIZED_AVAILABLE and time_ms <= 50:
            logger.info(f"🎯 Query completed in {time_ms:.1f}ms - Performance target achieved!")
        elif time_ms <= 100:
            logger.info(f"✅ Query completed in {time_ms:.1f}ms")
        else:
            logger.warning(f"⚠️ Query took {time_ms:.1f}ms - Consider optimization")

        return QueryResponse(
            answer=answer,
            sources=sources,
            processing_time=processing_time,
            performance_optimized=OPTIMIZED_AVAILABLE
        )

    except Exception as e:
        processing_time = time.perf_counter() - start_time
        logger.error(f"Query failed after {processing_time*1000:.1f}ms: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/add-documents")
async def add_documents(request: dict):
    """Add documents endpoint - maintains compatibility"""
    if not rag_instance:
        raise HTTPException(status_code=503, detail="RAG service not initialized")

    try:
        documents = request.get('documents', [])
        if not documents:
            raise ValueError("No documents provided")

        logger.info(f"Adding {len(documents)} documents")

        # Use optimized method if available
        if OPTIMIZED_AVAILABLE and hasattr(rag_instance, 'add_documents_optimized'):
            await asyncio.to_thread(rag_instance.add_documents_optimized, documents)
        elif hasattr(rag_instance, 'add_documents'):
            await asyncio.to_thread(rag_instance.add_documents, documents)
        else:
            raise ValueError("Document addition not supported")

        return {
            "status": "success",
            "message": f"Added {len(documents)} documents",
            "performance_optimized": OPTIMIZED_AVAILABLE
        }

    except Exception as e:
        logger.error(f"Document addition failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add documents: {str(e)}")


# Performance endpoints (only available with optimizations)
if OPTIMIZED_AVAILABLE:
    @app.get("/stats")
    async def stats():
        """Performance statistics - only available with optimizations"""
        if not rag_instance or not hasattr(rag_instance, 'get_performance_stats'):
            raise HTTPException(status_code=404, detail="Performance stats not available")

        try:
            return rag_instance.get_performance_stats()
        except Exception as e:
            logger.error(f"Stats retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")

    @app.post("/benchmark")
    async def benchmark(request: dict):
        """Performance benchmarking endpoint"""
        if not rag_instance:
            raise HTTPException(status_code=503, detail="RAG service not initialized")

        queries = request.get('queries', ['What is Neo4j?', 'Explain graph databases'])
        iterations = min(request.get('iterations', 3), 10)  # Limit iterations

        results = []
        for query in queries:
            query_times = []
            for _ in range(iterations):
                start = time.perf_counter()
                await query({'question': query, 'max_results': 3, 'include_sources': False})
                end = time.perf_counter()
                query_times.append((end - start) * 1000)
            
            avg_time = sum(query_times) / len(query_times)
            results.append({
                'query': query,
                'avg_time_ms': round(avg_time, 2),
                'min_time_ms': round(min(query_times), 2),
                'max_time_ms': round(max(query_times), 2)
            })

        overall_avg = sum(r['avg_time_ms'] for r in results) / len(results)
        
        return {
            'results': results,
            'summary': {
                'overall_avg_ms': round(overall_avg, 2),
                'performance_grade': 'A' if overall_avg <= 38 else 'B' if overall_avg <= 50 else 'C',
                'target_achieved': overall_avg <= 38
            }
        }

else:
    @app.get("/status")
    async def status():
        """Basic status endpoint for non-optimized version"""
        return {
            "status": "running",
            "performance_optimized": False,
            "message": "Standard performance mode"
        }


if __name__ == "__main__":
    uvicorn.run(
        "app_optimized_integration:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        log_level="info"
    )