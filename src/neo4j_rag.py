"""
Optimized Neo4j RAG (Retrieval-Augmented Generation) Implementation
Addresses performance bottlenecks identified in the original implementation
"""

import os
from typing import List, Dict, Optional
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging
import time
from concurrent.futures import ThreadPoolExecutor
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Neo4jRAG:
    """
    Optimized Neo4j-based RAG system with performance improvements
    """

    def __init__(self, uri: str = "bolt://localhost:7687",
                 username: str = "neo4j",
                 password: str = "password",
                 max_pool_size: int = 10):
        """
        Initialize optimized Neo4j RAG system

        Args:
            uri: Neo4j connection URI
            username: Neo4j username
            password: Neo4j password
            max_pool_size: Maximum connection pool size
        """
        # Use connection pooling for better performance
        self.driver = GraphDatabase.driver(
            uri, 
            auth=(username, password),
            max_connection_pool_size=max_pool_size,
            connection_timeout=30.0,
            max_transaction_retry_time=15.0
        )
        
        # Initialize embedding model once (thread-safe)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._embedding_lock = threading.Lock()
        
        # Query cache for frequently asked questions
        self._query_cache = {}
        self._cache_lock = threading.Lock()
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,  # Smaller chunks for faster processing
            chunk_overlap=30
        )

        # Initialize the database schema with optimized indexes
        self._initialize_optimized_schema()

    def _initialize_optimized_schema(self):
        """Create optimized indexes and constraints in Neo4j"""
        with self.driver.session() as session:
            # Create constraints
            session.run("""
                CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE
            """)
            
            # Create optimized indexes
            try:
                # Range index for faster numeric operations
                session.run("""
                    CREATE INDEX IF NOT EXISTS FOR (c:Chunk) ON (c.chunk_index)
                """)
                
                # Text index for keyword search optimization
                try:
                    session.run("""
                        CREATE FULLTEXT INDEX chunk_text_index IF NOT EXISTS
                        FOR (c:Chunk) ON EACH [c.text]
                    """)
                except Exception as fulltext_error:
                    logger.warning(f"Fulltext index creation failed: {fulltext_error}")
                    # Try without IF NOT EXISTS for compatibility
                    try:
                        session.run("""
                            CREATE FULLTEXT INDEX chunk_text_index
                            FOR (c:Chunk) ON EACH [c.text]
                        """)
                    except Exception:
                        logger.warning("Fulltext index already exists or creation failed")
                
            except Exception as e:
                logger.warning(f"Some indexes might already exist: {e}")

            logger.info("Neo4j schema initialized")

    def _get_cached_query_result(self, query_key: str) -> Optional[List[Dict]]:
        """Get cached query result if available"""
        with self._cache_lock:
            return self._query_cache.get(query_key)
    
    def _cache_query_result(self, query_key: str, result: List[Dict]):
        """Cache query result for future use"""
        with self._cache_lock:
            # Simple cache with max size limit
            if len(self._query_cache) > 100:
                # Remove oldest entries (simple FIFO)
                oldest_key = next(iter(self._query_cache))
                del self._query_cache[oldest_key]
            self._query_cache[query_key] = result

    def optimized_vector_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Optimized vector similarity search with caching and batch processing
        """
        # Check cache first
        query_key = f"vector_{hash(query)}_{k}"
        cached_result = self._get_cached_query_result(query_key)
        if cached_result:
            logger.info("Using cached result for vector search")
            return cached_result

        # Generate query embedding (thread-safe)
        with self._embedding_lock:
            query_embedding = self.embedding_model.encode([query])[0]

        with self.driver.session() as session:
            # Optimized query: Use LIMIT in Cypher to reduce data transfer
            result = session.run("""
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                RETURN c.text as text,
                       c.embedding as embedding,
                       c.chunk_index as chunk_index,
                       d.id as doc_id,
                       d as doc_properties
                LIMIT $limit
            """, limit=k*5)  # Get more initially to ensure good results after filtering

            chunks_with_scores = []
            for record in result:
                chunk_embedding = np.array(record['embedding'])
                
                # Optimized similarity calculation
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )

                # Extract metadata efficiently
                doc_props = dict(record['doc_properties'])
                metadata = {k: v for k, v in doc_props.items() 
                          if k not in ['id', 'content', 'created']}

                chunks_with_scores.append({
                    'text': record['text'],
                    'score': float(similarity),
                    'doc_id': record['doc_id'],
                    'chunk_index': record['chunk_index'],
                    'metadata': metadata
                })

            # Sort and filter top k results
            chunks_with_scores.sort(key=lambda x: x['score'], reverse=True)
            final_results = chunks_with_scores[:k]
            
            # Cache the result
            self._cache_query_result(query_key, final_results)
            
            return final_results

    def optimized_keyword_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Optimized keyword search using full-text indexes
        """
        query_key = f"keyword_{hash(query)}_{k}"
        cached_result = self._get_cached_query_result(query_key)
        if cached_result:
            return cached_result

        with self.driver.session() as session:
            try:
                # Use full-text index for better performance
                keyword_results = session.run("""
                    CALL db.index.fulltext.queryNodes('chunk_text_index', $search_query)
                    YIELD node, score
                    MATCH (d:Document)-[:HAS_CHUNK]->(node)
                    RETURN node.text as text,
                           d.id as doc_id,
                           d as doc_properties,
                           score
                    LIMIT $limit
                """, search_query=query, limit=k)
            except Exception:
                # Fallback to CONTAINS if full-text index is not available
                keyword_results = session.run("""
                    MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                    WHERE c.text CONTAINS $search_query
                    RETURN c.text as text,
                           d.id as doc_id,
                           d as doc_properties,
                           0.5 as score
                    LIMIT $limit
                """, search_query=query, limit=k)

            keyword_chunks = []
            for record in keyword_results:
                doc_props = dict(record['doc_properties'])
                metadata = {k: v for k, v in doc_props.items() 
                          if k not in ['id', 'content', 'created']}

                keyword_chunks.append({
                    'text': record['text'],
                    'doc_id': record['doc_id'],
                    'metadata': metadata,
                    'score': float(record.get('score', 0.5))
                })

            self._cache_query_result(query_key, keyword_chunks)
            return keyword_chunks

    def optimized_hybrid_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Optimized hybrid search with parallel processing
        """
        query_key = f"hybrid_{hash(query)}_{k}"
        cached_result = self._get_cached_query_result(query_key)
        if cached_result:
            return cached_result

        # Use ThreadPoolExecutor for parallel search
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both searches simultaneously
            vector_future = executor.submit(self.optimized_vector_search, query, k*2)
            keyword_future = executor.submit(self.optimized_keyword_search, query, k*2)
            
            # Get results
            vector_results = vector_future.result()
            keyword_results = keyword_future.result()

        # Combine and deduplicate results efficiently
        all_results = {}
        
        # Process vector results
        for result in vector_results:
            text_key = result['text'][:100]  # Use first 100 chars as key
            all_results[text_key] = result

        # Process keyword results (only add if better score or new)
        for result in keyword_results:
            text_key = result['text'][:100]
            if text_key not in all_results or result['score'] > all_results[text_key]['score']:
                all_results[text_key] = result

        # Sort by score and return top k
        final_results = sorted(all_results.values(), key=lambda x: x['score'], reverse=True)
        final_results = final_results[:k]
        
        self._cache_query_result(query_key, final_results)
        return final_results

    def batch_add_documents(self, documents: List[Dict], batch_size: int = 10):
        """
        Optimized batch document insertion
        
        Args:
            documents: List of dicts with 'content', 'metadata', and optional 'doc_id'
            batch_size: Number of documents to process in each batch
        """
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    for doc in batch:
                        self._add_single_document_tx(
                            tx, 
                            doc['content'], 
                            doc.get('metadata'), 
                            doc.get('doc_id')
                        )
                    tx.commit()
            
            logger.info(f"Processed batch {i//batch_size + 1}, documents {i+1}-{min(i+batch_size, len(documents))}")

    def _add_single_document_tx(self, tx, content: str, metadata: Optional[Dict] = None, doc_id: Optional[str] = None):
        """Add a single document within a transaction"""
        # Split document into smaller chunks for better performance
        chunks = self.text_splitter.split_text(content)
        
        # Generate embeddings in batch for better performance
        embeddings = self.embedding_model.encode(chunks)

        # Create document node
        if doc_id is None:
            import uuid
            doc_id = str(uuid.uuid4())

        # Store document with metadata
        doc_params = {'doc_id': doc_id, 'content': content}
        cypher_query = """
            MERGE (d:Document {id: $doc_id})
            SET d.content = $content,
                d.created = datetime(),
                d.chunk_count = $chunk_count
        """
        doc_params['chunk_count'] = len(chunks)
        
        if metadata:
            for key, value in metadata.items():
                cypher_query += f", d.{key} = ${key}"
                doc_params[key] = value

        tx.run(cypher_query, **doc_params)

        # Batch insert chunks
        chunk_data = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_data.append({
                'doc_id': doc_id,
                'text': chunk,
                'embedding': embedding.tolist(),
                'index': i
            })

        # Insert all chunks in a single query
        tx.run("""
            UNWIND $chunk_data as chunk
            MATCH (d:Document {id: chunk.doc_id})
            CREATE (c:Chunk {
                text: chunk.text,
                embedding: chunk.embedding,
                chunk_index: chunk.index
            })
            CREATE (d)-[:HAS_CHUNK]->(c)
        """, chunk_data=chunk_data)

    def get_stats(self) -> Dict:
        """Get optimized statistics about the RAG database"""
        with self.driver.session() as session:
            # Single query to get all stats efficiently
            result = session.run("""
                MATCH (d:Document)
                OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                RETURN COUNT(DISTINCT d) as doc_count,
                       COUNT(c) as chunk_count,
                       AVG(d.chunk_count) as avg_chunks_per_doc
            """)

            record = result.single()
            return {
                'documents': record['doc_count'],
                'chunks': record['chunk_count'],
                'avg_chunks_per_doc': round(record['avg_chunks_per_doc'] or 0, 1),
                'cache_size': len(self._query_cache)
            }

    def clear_cache(self):
        """Clear the query cache"""
        with self._cache_lock:
            self._query_cache.clear()
        logger.info("Query cache cleared")

    def close(self):
        """Close the database connection"""
        self.driver.close()


class RAGQueryEngine:
    """
    Optimized query engine with better performance characteristics
    """

    def __init__(self, neo4j_rag: Neo4jRAG):
        self.rag = neo4j_rag

    def query(self, question: str, k: int = 3) -> Dict:
        """
        Optimized query processing
        """
        start_time = time.time()
        
        # Use optimized hybrid search
        results = self.rag.optimized_hybrid_search(question, k=k)
        
        # Build context more efficiently
        context_parts = [f"[Context {i+1}]: {result['text']}" 
                        for i, result in enumerate(results)]
        context = "\n\n".join(context_parts)

        # Prepare sources
        sources = []
        for result in results:
            sources.append({
                'text': result['text'][:200] + '...' if len(result['text']) > 200 else result['text'],
                'score': result['score'],
                'doc_id': result['doc_id']
            })

        query_time = time.time() - start_time
        
        return {
            'question': question,
            'context': context,
            'sources': sources,
            'answer': f"Based on the retrieved context, here's relevant information:\n\n{context[:500]}...",
            'query_time': query_time,
            'results_found': len(results)
        }


if __name__ == "__main__":
    # Example usage with optimizations
    rag = Neo4jRAG()
    
    # Example of batch document addition
    sample_docs = [
        {
            'content': "Neo4j is a highly scalable graph database that provides ACID transactions.",
            'metadata': {'source': 'docs', 'category': 'database'}
        },
        {
            'content': "Vector search in Neo4j enables semantic similarity queries using embeddings.",
            'metadata': {'source': 'docs', 'category': 'search'}
        }
    ]
    
    # Add documents in batch
    rag.batch_add_documents(sample_docs)
    
    # Test optimized search
    engine = RAGQueryEngine(rag)
    response = engine.query("What is Neo4j?", k=2)
    
    print(f"Query completed in {response['query_time']:.3f}s")
    print(f"Found {response['results_found']} results")
    
    rag.close()