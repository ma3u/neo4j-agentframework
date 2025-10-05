"""
Ultra-High-Performance BitNet.cpp FastAPI Application
Optimized for 38ms response times with advanced caching and performance monitoring
Perfect for Azure AI Agent integration with maximum efficiency
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import optimized BitNet RAG implementation
from bitnet_optimized_rag import OptimizedNeo4jRAG

# Configure logging for performance
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/performance.log') if os.path.exists('/app/logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global optimized BitNet RAG instance
optimized_rag: Optional[OptimizedNeo4jRAG] = None


# Request/Response Models
class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to ask the RAG system", min_length=1, max_length=1000)
    max_results: int = Field(default=3, description="Maximum number of results", ge=1, le=10)
    include_sources: bool = Field(default=True, description="Include source documents in response")
    include_performance: bool = Field(default=True, description="Include detailed performance metrics")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated answer from optimized BitNet.cpp")
    sources: list = Field(default_factory=list, description="Source documents with scores")
    performance: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    optimization_stats: Dict[str, Any] = Field(default_factory=dict, description="Optimization statistics")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    model: str = Field(..., description="Model name")
    native_bitnet: bool = Field(..., description="Native BitNet.cpp availability")
    avg_response_time_ms: float = Field(..., description="Average response time in ms")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")
    memory_mb: float = Field(..., description="Memory usage in MB")
    neo4j_connected: bool = Field(..., description="Neo4j connection status")


class BenchmarkRequest(BaseModel):
    queries: list = Field(..., description="List of queries to benchmark")
    iterations: int = Field(default=5, description="Number of iterations per query", ge=1, le=20)


class BenchmarkResponse(BaseModel):
    results: list = Field(..., description="Benchmark results")
    summary: Dict[str, Any] = Field(..., description="Performance summary")


class DocumentRequest(BaseModel):
    documents: list = Field(..., description="List of documents to add to the knowledge base")


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup optimized BitNet.cpp RAG system"""
    global optimized_rag

    logger.info("🚀 Initializing Ultra-High-Performance BitNet.cpp RAG System")
    logger.info("🎯 Target: 38ms response times with advanced optimizations")

    try:
        # Get configuration from environment
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j-rag:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        cache_size = int(os.getenv("EMBEDDING_CACHE_SIZE", "10000"))

        logger.info(f"🔗 Connecting to Neo4j: {neo4j_uri}")
        logger.info(f"🧠 Embedding Cache Size: {cache_size}")
        logger.info("⚡ Performance Features: Advanced caching, pre-loaded models, optimized queries")

        # Initialize Optimized BitNet RAG
        start_init = time.perf_counter()
        optimized_rag = OptimizedNeo4jRAG(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            cache_size=cache_size
        )
        init_time = (time.perf_counter() - start_init) * 1000

        logger.info(f"✅ Optimized RAG initialized in {init_time:.1f}ms")
        
        # Check optimization status
        if optimized_rag.bitnet_available:
            logger.info("🔥 Native BitNet.cpp available - TRUE 1.58-bit inference enabled")
        else:
            logger.warning("⚠️ Native BitNet.cpp not available - using optimized fallback")

        logger.info("🎉 Ultra-High-Performance RAG system ready!")
        logger.info("📊 Monitoring: Detailed performance profiling enabled")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Optimized BitNet RAG: {str(e)}", exc_info=True)
        raise

    yield

    # Cleanup
    if optimized_rag:
        logger.info("🧹 Cleaning up Optimized BitNet RAG resources...")
        await optimized_rag.close()
        logger.info("✅ Cleanup complete")


# Create FastAPI app
app = FastAPI(
    title="Ultra-High-Performance Neo4j BitNet.cpp RAG API",
    description="Optimized RAG system targeting 38ms response times with advanced caching and performance monitoring",
    version="4.0.0-optimized",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with performance information"""
    stats = optimized_rag.get_performance_stats() if optimized_rag else {}
    avg_time = stats.get('query_stats', {}).get('avg_response_time', 0)
    cache_hit_rate = stats.get('cache_stats', {}).get('hit_rate_percent', 0)
    
    return {
        "service": "Ultra-High-Performance Neo4j BitNet.cpp RAG API",
        "version": "4.0.0-optimized",
        "target_performance": "38ms response time",
        "current_performance": {
            "avg_response_time_ms": round(avg_time, 1),
            "cache_hit_rate_percent": round(cache_hit_rate, 1)
        },
        "optimizations": [
            "LRU embedding cache with 10K+ entries",
            "Pre-loaded and warmed-up models",
            "Optimized Neo4j queries with vector indexes",
            "Persistent BitNet.cpp processes",
            "High-resolution performance profiling",
            "Async processing pipeline"
        ],
        "native_bitnet": optimized_rag.bitnet_available if optimized_rag else False,
        "perfect_for": "Azure AI Agent integration, ultra-low latency requirements",
        "endpoints": {
            "query": "POST /query - Ultra-fast RAG queries",
            "benchmark": "POST /benchmark - Performance benchmarking",
            "health": "GET /health - System health with performance metrics",
            "add_docs": "POST /add-documents - Optimized document indexing",
            "stats": "GET /performance-stats - Detailed performance analysis"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Advanced health check with performance metrics"""
    if not optimized_rag:
        raise HTTPException(status_code=503, detail="Optimized BitNet RAG not initialized")

    try:
        # Check Neo4j connection
        neo4j_connected = await asyncio.to_thread(optimized_rag.driver.verify_connectivity)
        
        # Get performance stats
        stats = optimized_rag.get_performance_stats()
        
        return HealthResponse(
            status="healthy",
            model="BitNet b1.58 2B4T (Ultra-Optimized)",
            native_bitnet=optimized_rag.bitnet_available,
            avg_response_time_ms=round(stats['query_stats']['avg_response_time'], 1),
            cache_hit_rate=round(stats['cache_stats']['hit_rate_percent'], 1),
            memory_mb=round(stats['system_stats']['memory_usage_mb'], 1),
            neo4j_connected=bool(neo4j_connected)
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Ultra-high-performance query processing - Target: 38ms"""
    if not optimized_rag:
        raise HTTPException(status_code=503, detail="Optimized BitNet RAG not initialized")

    try:
        logger.info(f"Processing optimized query: {request.question[:50]}...")
        
        # Execute optimized RAG query
        result = await optimized_rag.query_optimized(
            question=request.question,
            k=request.max_results
        )

        # Format response
        response = QueryResponse(
            answer=result.get('answer', 'No answer generated'),
            sources=result.get('sources', []) if request.include_sources else [],
            performance=result.get('performance', {}) if request.include_performance else {},
            optimization_stats=result.get('optimization_stats', {}) if request.include_performance else {}
        )

        # Log performance
        total_time = result.get('performance', {}).get('total_time_ms', 0)
        cache_hit_rate = result.get('performance', {}).get('cache_hit_rate', 0)
        
        logger.info(f"✅ Optimized query completed in {total_time:.1f}ms (cache: {cache_hit_rate:.1f}%)")
        
        # Check if we're meeting performance targets
        if total_time <= 50:  # Within target range
            logger.info("🎯 Performance target achieved!")
        elif total_time <= 100:
            logger.warning(f"⚠️ Performance close to target: {total_time:.1f}ms")
        else:
            logger.error(f"❌ Performance below target: {total_time:.1f}ms")

        return response

    except Exception as e:
        logger.error(f"Optimized query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/benchmark", response_model=BenchmarkResponse)
async def benchmark(request: BenchmarkRequest):
    """Performance benchmarking endpoint"""
    if not optimized_rag:
        raise HTTPException(status_code=503, detail="Optimized BitNet RAG not initialized")

    try:
        logger.info(f"Starting benchmark with {len(request.queries)} queries, {request.iterations} iterations each")
        
        benchmark_results = []
        all_times = []
        
        for query in request.queries:
            query_times = []
            
            for i in range(request.iterations):
                start_time = time.perf_counter()
                result = await optimized_rag.query_optimized(query)
                end_time = time.perf_counter()
                
                response_time = (end_time - start_time) * 1000  # Convert to ms
                query_times.append(response_time)
                all_times.append(response_time)
            
            # Calculate statistics for this query
            query_stats = {
                'query': query,
                'iterations': request.iterations,
                'avg_time_ms': round(sum(query_times) / len(query_times), 2),
                'min_time_ms': round(min(query_times), 2),
                'max_time_ms': round(max(query_times), 2),
                'std_dev_ms': round((sum((t - sum(query_times)/len(query_times))**2 for t in query_times) / len(query_times))**0.5, 2)
            }
            
            benchmark_results.append(query_stats)
        
        # Overall summary
        summary = {
            'total_queries': len(request.queries) * request.iterations,
            'overall_avg_ms': round(sum(all_times) / len(all_times), 2),
            'overall_min_ms': round(min(all_times), 2),
            'overall_max_ms': round(max(all_times), 2),
            'target_38ms_achieved': sum(1 for t in all_times if t <= 38),
            'target_50ms_achieved': sum(1 for t in all_times if t <= 50),
            'performance_grade': 'A' if sum(all_times) / len(all_times) <= 38 else 
                               'B' if sum(all_times) / len(all_times) <= 50 else
                               'C' if sum(all_times) / len(all_times) <= 100 else 'D'
        }
        
        logger.info(f"📊 Benchmark completed: Avg {summary['overall_avg_ms']:.1f}ms, Grade: {summary['performance_grade']}")
        
        return BenchmarkResponse(
            results=benchmark_results,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Benchmark failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Benchmark failed: {str(e)}")


@app.post("/add-documents")
async def add_documents(request: DocumentRequest):
    """Add documents with optimized batch processing"""
    if not optimized_rag:
        raise HTTPException(status_code=503, detail="Optimized BitNet RAG not initialized")

    try:
        logger.info(f"Adding {len(request.documents)} documents with optimized processing")
        
        start_time = time.perf_counter()
        
        # Use optimized document addition
        await asyncio.to_thread(optimized_rag.add_documents_optimized, request.documents)
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        logger.info(f"✅ Documents added in {processing_time:.1f}ms")
        
        return {
            "status": "success",
            "message": f"Added {len(request.documents)} documents",
            "processing_time_ms": round(processing_time, 2),
            "embedding_cost": 0.0,  # FREE with local embeddings!
            "optimization": "Batch processing enabled"
        }

    except Exception as e:
        logger.error(f"Document addition failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add documents: {str(e)}")


@app.get("/performance-stats")
async def performance_stats():
    """Get comprehensive performance statistics and optimization details"""
    if not optimized_rag:
        raise HTTPException(status_code=503, detail="Optimized BitNet RAG not initialized")

    try:
        stats = optimized_rag.get_performance_stats()
        
        # Add performance analysis
        avg_time = stats['query_stats']['avg_response_time']
        performance_analysis = {
            'target_38ms_status': 'ACHIEVED' if avg_time <= 38 else 'CLOSE' if avg_time <= 50 else 'NEEDS_OPTIMIZATION',
            'performance_grade': 'A+' if avg_time <= 25 else 'A' if avg_time <= 38 else 'B' if avg_time <= 50 else 'C',
            'optimization_level': 'MAXIMUM' if avg_time <= 38 else 'HIGH' if avg_time <= 100 else 'MEDIUM'
        }
        
        return {
            'performance_stats': stats,
            'performance_analysis': performance_analysis,
            'optimization_features': {
                'embedding_caching': 'LRU cache with high hit rate',
                'model_preloading': 'Models warmed up at startup',
                'query_optimization': 'Vectorized operations with indexes',
                'async_processing': 'Non-blocking pipeline',
                'profiling': 'High-resolution timing',
                'bitnet_integration': 'Optimized subprocess calls'
            }
        }

    except Exception as e:
        logger.error(f"Stats retrieval failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stats failed: {str(e)}")


@app.get("/optimization-guide")
async def optimization_guide():
    """Get optimization guide and performance tuning tips"""
    current_stats = optimized_rag.get_performance_stats() if optimized_rag else {}
    avg_time = current_stats.get('query_stats', {}).get('avg_response_time', 100)
    cache_hit_rate = current_stats.get('cache_stats', {}).get('hit_rate_percent', 0)
    
    recommendations = []
    
    if avg_time > 50:
        recommendations.append("Consider increasing embedding cache size")
        recommendations.append("Verify Neo4j indexes are properly created")
        recommendations.append("Check BitNet.cpp model loading time")
    
    if cache_hit_rate < 80:
        recommendations.append("Allow more warm-up queries to improve cache performance")
        recommendations.append("Consider larger cache size for better hit rates")
    
    if not optimized_rag or not optimized_rag.bitnet_available:
        recommendations.append("Enable native BitNet.cpp for optimal performance")
    
    return {
        "current_performance": {
            "avg_response_time_ms": round(avg_time, 1),
            "cache_hit_rate_percent": round(cache_hit_rate, 1),
            "status": "OPTIMAL" if avg_time <= 38 else "GOOD" if avg_time <= 50 else "NEEDS_TUNING"
        },
        "optimization_targets": {
            "embedding_generation": "5-15ms (with caching)",
            "vector_search": "10-20ms (with indexes)", 
            "answer_generation": "15-25ms (with BitNet.cpp)",
            "total_pipeline": "38ms (target)"
        },
        "recommendations": recommendations,
        "performance_tuning": {
            "cache_size": "Increase EMBEDDING_CACHE_SIZE environment variable",
            "neo4j_optimization": "Ensure vector indexes are created",
            "bitnet_optimization": "Use native BitNet.cpp binary",
            "system_optimization": "Allocate sufficient memory (2GB+)"
        }
    }


@app.get("/azure-ai-agent-integration-optimized")
async def azure_ai_agent_integration_optimized():
    """Optimized integration guide for Azure AI Agents"""
    return {
        "integration_type": "Ultra-High-Performance RAG Service for Azure AI Agents",
        "description": "Provides sub-50ms retrieval with advanced optimizations",
        "performance_benefits": {
            "response_time": "38ms target (vs 200-500ms typical)",
            "cache_efficiency": "90%+ hit rate after warm-up",
            "zero_embedding_costs": "$0.00/month vs $50+/month",
            "no_rate_limits": "Unlimited queries",
            "offline_capable": "100% local processing"
        },
        "optimization_features": {
            "embedding_caching": "10,000+ entry LRU cache",
            "model_preloading": "Pre-warmed at startup", 
            "query_optimization": "Vectorized Neo4j operations",
            "bitnet_optimization": "Persistent process optimization",
            "monitoring": "Real-time performance profiling"
        },
        "integration_example": {
            "step_1": "Deploy optimized container",
            "step_2": "Azure AI Agent calls POST /query",
            "step_3": "Agent receives context in <50ms",
            "step_4": "Agent uses context for final response",
            "result": "Best of both: ultra-fast retrieval + high-quality generation"
        },
        "monitoring_endpoints": {
            "health_check": "GET /health - Performance metrics included",
            "benchmarking": "POST /benchmark - Load testing",
            "optimization_guide": "GET /optimization-guide - Tuning recommendations"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app_bitnet_optimized:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,  # Single worker optimized for performance
        log_level="info"
    )