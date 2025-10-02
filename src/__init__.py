"""
Neo4j RAG System - Core Package

This package provides RAG (Retrieval-Augmented Generation) functionality
using Neo4j graph database.
"""

from .neo4j_rag import Neo4jRAG, RAGQueryEngine
from .neo4j_rag_optimized import Neo4jRAGOptimized
from .docling_loader import DoclingDocumentLoader

__all__ = [
    'Neo4jRAG',
    'RAGQueryEngine',
    'Neo4jRAGOptimized',
    'DoclingDocumentLoader'
]

__version__ = '1.0.0'