"""
Neo4j RAG (Retrieval-Augmented Generation) Implementation
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


class Neo4jRAG:
    """
    Neo4j-based RAG system for document storage and retrieval
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

    def add_document(self, content: str, metadata: Optional[Dict] = None, doc_id: Optional[str] = None):
        """
        Add a document to the RAG system

        Args:
            content: Document text content
            metadata: Optional metadata dictionary
            doc_id: Optional document ID
        """
        # Split document into chunks
        chunks = self.text_splitter.split_text(content)

        # Generate embeddings for each chunk
        embeddings = self.embedding_model.encode(chunks)

        with self.driver.session() as session:
            # Create document node
            if doc_id is None:
                import uuid
                doc_id = str(uuid.uuid4())

            # Store document with metadata as individual properties
            cypher_query = """
                MERGE (d:Document {id: $doc_id})
                SET d.content = $content,
                    d.created = datetime()
            """

            # Add metadata as individual properties
            params = {'doc_id': doc_id, 'content': content}
            if metadata:
                for key, value in metadata.items():
                    cypher_query += f", d.{key} = ${key}"
                    params[key] = value

            session.run(cypher_query, **params)

            # Store chunks with embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                session.run("""
                    MATCH (d:Document {id: $doc_id})
                    CREATE (c:Chunk {
                        text: $text,
                        embedding: $embedding,
                        chunk_index: $index
                    })
                    CREATE (d)-[:HAS_CHUNK]->(c)
                """, doc_id=doc_id, text=chunk, embedding=embedding.tolist(), index=i)

            logger.info(f"Added document {doc_id} with {len(chunks)} chunks")

    def vector_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Perform vector similarity search

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        with self.driver.session() as session:
            # Get all chunks and calculate similarity
            result = session.run("""
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                RETURN c.text as text,
                       c.embedding as embedding,
                       d as doc
            """)

            chunks_with_scores = []
            for record in result:
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

            # Sort by similarity score and return top k
            chunks_with_scores.sort(key=lambda x: x['score'], reverse=True)
            return chunks_with_scores[:k]

    def hybrid_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Perform hybrid search combining vector and keyword search

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar chunks with metadata
        """
        # Vector search results
        vector_results = self.vector_search(query, k=k*2)

        # Keyword search using full-text index
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
        results = self.hybrid_search(query, k=k)
        context_parts = []

        for i, result in enumerate(results, 1):
            context_parts.append(f"[Context {i}]: {result['text']}")

        return "\n\n".join(context_parts)

    def clear_database(self):
        """Clear all documents and chunks from the database"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared")

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


class RAGQueryEngine:
    """
    Query engine that combines retrieval with LLM generation
    """

    def __init__(self, neo4j_rag: Neo4jRAG):
        """
        Initialize RAG Query Engine

        Args:
            neo4j_rag: Neo4jRAG instance
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
        results = self.rag.hybrid_search(question, k=k)

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
    rag = Neo4jRAG()

    # Add sample document
    rag.add_document(
        "Neo4j is a graph database management system. It is designed to handle "
        "connected data and relationships efficiently. Neo4j uses Cypher query language "
        "for querying the graph database.",
        metadata={'source': 'documentation', 'type': 'intro'}
    )

    # Search
    results = rag.vector_search("What is Neo4j?", k=2)
    for result in results:
        print(f"Score: {result['score']:.3f}, Text: {result['text'][:100]}...")

    rag.close()