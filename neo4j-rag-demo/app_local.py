"""
Local FastAPI App - Uses 100% Local Models (No Azure Required)
Uses SentenceTransformer for embeddings (all-MiniLM-L6-v2)
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from src.neo4j_rag import Neo4jRAG, RAGQueryEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG instance
rag_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global rag_engine

    try:
        # Get Neo4j connection details
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

        logger.info(f"Connecting to Neo4j: {neo4j_uri}")

        # Initialize Local RAG (100% local, no Azure required)
        rag = Neo4jRAG(
            uri=neo4j_uri,
            username=neo4j_user,
            password=neo4j_password,
            max_pool_size=10
        )

        rag_engine = RAGQueryEngine(rag)

        logger.info("✅ Local RAG initialized successfully")
        logger.info("📦 Using SentenceTransformer (all-MiniLM-L6-v2) - 100% local embeddings")
        logger.info("🚀 No Azure credentials required!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Local RAG: {str(e)}", exc_info=True)
        raise

    yield

    # Cleanup
    if rag_engine:
        logger.info("Cleaning up RAG resources...")
        rag_engine.rag.close()


# Create FastAPI app
app = FastAPI(
    title="Local Neo4j RAG API",
    description="Truly local RAG system using SentenceTransformer embeddings",
    version="1.0.0",
    lifespan=lifespan
)


# Request/Response models
class Document(BaseModel):
    content: str
    metadata: Optional[dict] = None


class Query(BaseModel):
    question: str
    k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    processing_time: float


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if rag_engine and rag_engine.rag:
            stats = rag_engine.rag.get_stats()
            return {
                "status": "healthy",
                "model": "SentenceTransformer (all-MiniLM-L6-v2)",
                "deployment": "100% local - no Azure required",
                "neo4j_stats": stats
            }
        return {"status": "initializing"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# Get statistics
@app.get("/stats")
async def get_stats():
    """Get RAG system statistics"""
    try:
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")

        # Get Neo4j stats
        neo4j_stats = rag_engine.rag.get_stats()

        # Get profiler stats
        profiler_stats = rag_engine.rag.profiler.get_summary()

        # Get cache stats
        cache_stats = {
            "size": len(rag_engine.rag._query_cache),
            "max_size": 10000,
            "hits": profiler_stats.get("cache", {}).get("hits", 0),
            "misses": profiler_stats.get("cache", {}).get("misses", 0)
        }

        # Calculate cache hit rate
        total_cache_ops = cache_stats["hits"] + cache_stats["misses"]
        cache_hit_rate = (cache_stats["hits"] / total_cache_ops * 100) if total_cache_ops > 0 else 0

        # Get memory usage
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024

        return {
            "status": "healthy",
            "neo4j_connected": True,
            "document_count": neo4j_stats.get("documents", 0),
            "chunk_count": neo4j_stats.get("chunks", 0),
            "avg_response_time_ms": profiler_stats.get("total_query", {}).get("avg_ms", 0),
            "cache_hit_rate": round(cache_hit_rate, 1),
            "memory_mb": round(memory_mb, 1),
            "performance_optimized": True,
            "query_stats": profiler_stats,
            "cache_stats": cache_stats,
            "profiler_stats": profiler_stats,
            "system_stats": {
                "cpu_count": psutil.cpu_count(),
                "memory_usage_mb": round(memory_mb, 1),
                "bitnet_available": False  # Update if BitNet is running
            }
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Add document
@app.post("/documents")
async def add_document(doc: Document):
    """Add a document to the knowledge base"""
    try:
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")

        # Use batch_add_documents with a single document
        doc_data = {
            "content": doc.content,
            "metadata": doc.metadata or {}
        }
        rag_engine.rag.batch_add_documents([doc_data], batch_size=1)

        # Generate a simple document ID
        import hashlib
        doc_id = hashlib.sha256(doc.content.encode()).hexdigest()[:16]

        return {
            "status": "success",
            "document_id": doc_id,
            "message": "Document added successfully"
        }
    except Exception as e:
        logger.error(f"Failed to add document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Query RAG
@app.post("/query", response_model=QueryResponse)
async def query_rag(query: Query):
    """Query the RAG system"""
    try:
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")

        import time
        start_time = time.time()

        # Get response from RAG engine
        response = rag_engine.query(query.question, k=query.k)

        processing_time = time.time() - start_time

        return QueryResponse(
            answer=response['answer'],
            sources=response['sources'],
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Search similar chunks
@app.post("/search")
async def search_chunks(query: Query):
    """Search for similar chunks using vector similarity"""
    try:
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG engine not initialized")

        results = rag_engine.rag.optimized_vector_search(query.question, k=query.k)

        return {
            "query": query.question,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
