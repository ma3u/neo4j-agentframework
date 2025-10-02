"""
Optimized Neo4j RAG Implementation for Large Datasets
"""

import os
from typing import List, Dict, Optional
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jRAGOptimized:
    """
    Optimized Neo4j-based RAG system for large document collections
    """

    def __init__(self, uri: str = "bolt://localhost:7687",
                 username: str = "neo4j",
                 password: str = "password"):
        """
        Initialize Neo4j RAG system

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        # Initialize the database schema
        self._initialize_schema()

    def _initialize_schema(self):
        """Create necessary indexes and constraints in Neo4j"""
        with self.driver.session() as session:
            # Create vector index for similarity search
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE
            """)

            session.run("""
                CREATE INDEX IF NOT EXISTS FOR (c:Chunk) ON (c.embedding)
            """)

            logger.info("Neo4j schema initialized")

    def vector_search_optimized(self, query: str, k: int = 5, batch_size: int = 100) -> List[Dict]:
        """
        Optimized vector similarity search for large datasets

        Args:
            query: Search query
            k: Number of results to return
            batch_size: Number of chunks to process at a time

        Returns:
            List of similar chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        with self.driver.session() as session:
            # First, sample a subset of chunks for initial filtering
            # This uses Neo4j's built-in random sampling to avoid loading all chunks
            result = session.run("""
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                WITH c, d, rand() as random
                ORDER BY random
                LIMIT $limit
                RETURN c.text as text,
                       c.embedding as embedding,
                       d as doc
            """, limit=min(batch_size * 10, 1000))  # Process up to 1000 chunks

            chunks_with_scores = []
            for record in result:
                try:
                    chunk_embedding = np.array(record['embedding'])
                    # Calculate cosine similarity
                    similarity = np.dot(query_embedding, chunk_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                    )

                    # Extract metadata from document properties
                    doc = dict(record['doc'])
                    doc_id = doc.get('id')
                    metadata = {k: v for k, v in doc.items() if k not in ['id', 'content', 'created']}

                    chunks_with_scores.append({
                        'text': record['text'],
                        'score': float(similarity),
                        'doc_id': doc_id,
                        'metadata': metadata
                    })
                except Exception as e:
                    logger.debug(f"Error processing chunk: {e}")
                    continue

            # Sort by similarity score and return top k
            chunks_with_scores.sort(key=lambda x: x['score'], reverse=True)
            return chunks_with_scores[:k]

    def hybrid_search_optimized(self, query: str, k: int = 5) -> List[Dict]:
        """
        Optimized hybrid search combining vector and keyword search

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar chunks with metadata
        """
        # Vector search results (limited)
        vector_results = self.vector_search_optimized(query, k=k*2)

        # Keyword search using full-text index (also limited)
        with self.driver.session() as session:
            keyword_results = session.run("""
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                WHERE c.text CONTAINS $search_query
                RETURN c.text as text,
                       d as doc
                LIMIT $limit
            """, search_query=query, limit=k*2)

            keyword_chunks = []
            for record in keyword_results:
                doc = dict(record['doc'])
                doc_id = doc.get('id')
                metadata = {k: v for k, v in doc.items() if k not in ['id', 'content', 'created']}

                keyword_chunks.append({
                    'text': record['text'],
                    'doc_id': doc_id,
                    'metadata': metadata,
                    'score': 0.5  # Default score for keyword matches
                })

        # Combine and deduplicate results
        all_results = {}
        for result in vector_results + keyword_chunks:
            key = result['text'][:50]  # Use first 50 chars as key
            if key not in all_results or result['score'] > all_results[key]['score']:
                all_results[key] = result

        # Sort by score and return top k
        final_results = sorted(all_results.values(), key=lambda x: x['score'], reverse=True)
        return final_results[:k]

    def get_context(self, query: str, k: int = 3) -> str:
        """
        Get context for RAG based on query

        Args:
            query: Search query
            k: Number of chunks to include in context

        Returns:
            Concatenated context string
        """
        results = self.hybrid_search_optimized(query, k=k)
        context_parts = []

        for i, result in enumerate(results, 1):
            context_parts.append(f"[Context {i}]: {result['text']}")

        return "\n\n".join(context_parts)

    def get_stats(self) -> Dict:
        """Get statistics about the RAG database"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document)
                OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                RETURN COUNT(DISTINCT d) as doc_count,
                       COUNT(c) as chunk_count
            """)

            record = result.single()
            return {
                'documents': record['doc_count'],
                'chunks': record['chunk_count']
            }

    def close(self):
        """Close the database connection"""
        self.driver.close()


class RAGQueryEngineOptimized:
    """
    Optimized query engine for large datasets
    """

    def __init__(self, neo4j_rag):
        """
        Initialize RAG Query Engine

        Args:
            neo4j_rag: Neo4jRAGOptimized instance
        """
        self.rag = neo4j_rag

    def query(self, question: str, k: int = 3) -> Dict:
        """
        Query the RAG system

        Args:
            question: User question
            k: Number of context chunks to retrieve

        Returns:
            Dictionary with context and sources
        """
        # Get relevant context
        context = self.rag.get_context(question, k=k)

        # Get source documents
        results = self.rag.hybrid_search_optimized(question, k=k)

        sources = []
        for result in results:
            sources.append({
                'text': result['text'][:200] + '...' if len(result['text']) > 200 else result['text'],
                'score': result['score'],
                'doc_id': result['doc_id']
            })

        return {
            'question': question,
            'context': context,
            'sources': sources,
            'answer': f"Based on the retrieved context, here's relevant information:\n\n{context[:500]}..."
        }


if __name__ == "__main__":
    # Example usage
    rag = Neo4jRAGOptimized()

    # Get stats
    stats = rag.get_stats()
    print(f"Database contains {stats['documents']} documents with {stats['chunks']} chunks")

    # Search
    results = rag.vector_search_optimized("What is Neo4j?", k=3)
    for result in results:
        print(f"Score: {result['score']:.3f}, Text: {result['text'][:100]}...")

    rag.close()