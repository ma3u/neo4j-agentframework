#!/usr/bin/env python3
"""
Simple RAG API for Azure AI Foundry - Connects to Aura
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from src.neo4j_rag import Neo4jRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Neo4j RAG API", version="2.0")

# Connect to Aura
uri = os.getenv("NEO4J_URI", "neo4j+s://6b870b04.databases.neo4j.io")
username = os.getenv("NEO4J_USERNAME", "neo4j")
password = os.getenv("NEO4J_PASSWORD")

logger.info(f"Connecting to: {uri}")
rag = Neo4jRAG(uri=uri, username=username, password=password)

class QueryRequest(BaseModel):
    question: str
    k: int = 5

@app.post("/query")
async def query(req: QueryRequest):
    results = rag.optimized_vector_search(req.question, k=req.k)
    return {"results": results}

@app.get("/health")
async def health():
    stats = rag.get_stats()
    return {"status": "healthy", "mode": "production", "stats": stats}

@app.get("/stats")
async def stats():
    return rag.get_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
