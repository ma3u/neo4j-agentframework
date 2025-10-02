"""
Test script for Neo4j RAG system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_rag import Neo4jRAG, RAGQueryEngine
import time
import logging
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def print_separator():
    """Print a visual separator"""
    print("\n" + "="*80 + "\n")


def test_vector_search(rag: Neo4jRAG):
    """Test vector similarity search"""
    print_separator()
    print("TEST 1: VECTOR SIMILARITY SEARCH")
    print_separator()

    test_queries = [
        "What is Neo4j?",
        "How does Cypher work?",
        "Tell me about RAG systems",
        "What are vector embeddings?",
        "How to implement RAG with Python?"
    ]

    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)

        start_time = time.time()
        results = rag.vector_search(query, k=3)
        search_time = time.time() - start_time

        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"  Score: {result['score']:.4f}")
            print(f"  Source: {result['metadata'].get('source', 'unknown')}")
            print(f"  Text: {result['text'][:150]}...")

        print(f"\n  ⏱️  Search time: {search_time:.3f}s")


def test_hybrid_search(rag: Neo4jRAG):
    """Test hybrid search (vector + keyword)"""
    print_separator()
    print("TEST 2: HYBRID SEARCH (VECTOR + KEYWORD)")
    print_separator()

    test_queries = [
        "graph database relationships",
        "Cypher MATCH CREATE",
        "retrieval augmented generation RAG"
    ]

    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)

        start_time = time.time()
        results = rag.hybrid_search(query, k=3)
        search_time = time.time() - start_time

        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"  Score: {result['score']:.4f}")
            print(f"  Source: {result['metadata'].get('source', 'unknown')}")
            print(f"  Category: {result['metadata'].get('category', 'unknown')}")
            print(f"  Text: {result['text'][:150]}...")

        print(f"\n  ⏱️  Search time: {search_time:.3f}s")


def test_query_engine(rag: Neo4jRAG):
    """Test the RAG query engine"""
    print_separator()
    print("TEST 3: RAG QUERY ENGINE")
    print_separator()

    engine = RAGQueryEngine(rag)

    test_questions = [
        "What are the main differences between graph databases and relational databases?",
        "How can I use Neo4j for implementing a RAG system?",
        "What are the best practices for RAG implementation?",
        "Explain how vector embeddings work in RAG"
    ]

    for question in test_questions:
        print(f"\n❓ Question: '{question}'")
        print("-" * 40)

        start_time = time.time()
        response = engine.query(question, k=3)
        query_time = time.time() - start_time

        print(f"\n📚 Retrieved Context Sources:")
        for i, source in enumerate(response['sources'], 1):
            print(f"  {i}. [{source['score']:.3f}] Doc: {source['doc_id']} - {source['text'][:100]}...")

        print(f"\n💡 Context Summary:")
        print(f"  {response['context'][:300]}...")

        print(f"\n  ⏱️  Query time: {query_time:.3f}s")


def test_database_stats(rag: Neo4jRAG):
    """Display database statistics"""
    print_separator()
    print("TEST 4: DATABASE STATISTICS")
    print_separator()

    stats = rag.get_stats()
    print(f"📊 Database Statistics:")
    print(f"  • Total Documents: {stats['documents']}")
    print(f"  • Total Chunks: {stats['chunks']}")
    print(f"  • Average Chunks per Document: {stats['chunks'] / stats['documents']:.1f}")


def test_performance(rag: Neo4jRAG):
    """Test search performance with multiple queries"""
    print_separator()
    print("TEST 5: PERFORMANCE BENCHMARK")
    print_separator()

    queries = [
        "Neo4j database",
        "Cypher query",
        "graph relationships",
        "RAG implementation",
        "vector embeddings"
    ] * 2  # Run each query twice

    print(f"Running {len(queries)} queries...")

    # Vector search benchmark
    start_time = time.time()
    for query in queries:
        rag.vector_search(query, k=3)
    vector_time = time.time() - start_time

    print(f"\n⚡ Vector Search Performance:")
    print(f"  • Total time: {vector_time:.3f}s")
    print(f"  • Average per query: {vector_time/len(queries):.3f}s")
    print(f"  • Queries per second: {len(queries)/vector_time:.1f}")

    # Hybrid search benchmark
    start_time = time.time()
    for query in queries:
        rag.hybrid_search(query, k=3)
    hybrid_time = time.time() - start_time

    print(f"\n⚡ Hybrid Search Performance:")
    print(f"  • Total time: {hybrid_time:.3f}s")
    print(f"  • Average per query: {hybrid_time/len(queries):.3f}s")
    print(f"  • Queries per second: {len(queries)/hybrid_time:.1f}")


def main():
    """Main test function"""
    print("\n" + "🚀 NEO4J RAG SYSTEM TEST SUITE 🚀".center(80))

    # Initialize RAG system
    logger.info("Connecting to Neo4j...")
    rag = Neo4jRAG(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password"
    )

    try:
        # Check if data is loaded
        stats = rag.get_stats()
        if stats['documents'] == 0:
            print("\n⚠️  No data found in database. Please run 'python load_sample_data.py' first.")
            return

        # Run all tests
        test_vector_search(rag)
        test_hybrid_search(rag)
        test_query_engine(rag)
        test_database_stats(rag)
        test_performance(rag)

        print_separator()
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print_separator()

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        rag.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    main()