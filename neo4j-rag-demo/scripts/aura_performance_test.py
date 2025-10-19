#!/usr/bin/env python3
"""
Neo4j Aura Performance Testing Suite
Tests vector search, hybrid search, and query performance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_rag import Neo4jRAG
from dotenv import load_dotenv
import time
from tabulate import tabulate
import statistics

load_dotenv()

def performance_test_vector_search(rag, iterations=10):
    """Test vector search performance"""
    print("\n⚡ Vector Search Performance Test")
    print("="*60)

    queries = [
        "How does Neo4j handle graph relationships?",
        "What is retrieval augmented generation?",
        "Explain vector embeddings in machine learning",
        "Neo4j performance optimization techniques",
        "Knowledge graph construction methods"
    ]

    times = []

    for i, query in enumerate(queries, 1):
        query_times = []

        for _ in range(iterations):
            start = time.time()
            results = rag.vector_search(query, k=5)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            query_times.append(elapsed)

        avg_time = statistics.mean(query_times)
        min_time = min(query_times)
        max_time = max(query_times)
        times.append(avg_time)

        print(f"\nQuery {i}: {query[:50]}...")
        print(f"  Avg: {avg_time:.2f}ms | Min: {min_time:.2f}ms | Max: {max_time:.2f}ms")
        print(f"  Results: {len(results)} chunks")

    overall_avg = statistics.mean(times)
    print(f"\n📊 Overall Vector Search Performance:")
    print(f"  Average: {overall_avg:.2f}ms")
    print(f"  Min: {min(times):.2f}ms")
    print(f"  Max: {max(times):.2f}ms")

    return overall_avg

def performance_test_hybrid_search(rag, iterations=5):
    """Test hybrid search performance"""
    print("\n⚡ Hybrid Search Performance Test")
    print("="*60)

    queries = [
        "graph database performance",
        "vector search optimization",
        "Neo4j Cypher queries"
    ]

    times = []

    for query in queries:
        query_times = []

        for _ in range(iterations):
            start = time.time()
            results = rag.hybrid_search(query, k=5, alpha=0.5)
            elapsed = (time.time() - start) * 1000
            query_times.append(elapsed)

        avg_time = statistics.mean(query_times)
        times.append(avg_time)

        print(f"\nQuery: {query}")
        print(f"  Avg: {avg_time:.2f}ms | Results: {len(results)} chunks")

    overall_avg = statistics.mean(times)
    print(f"\n📊 Overall Hybrid Search Performance:")
    print(f"  Average: {overall_avg:.2f}ms")

    return overall_avg

def performance_test_cache(rag):
    """Test cache performance"""
    print("\n⚡ Cache Performance Test")
    print("="*60)

    query = "What is Neo4j used for?"

    # First query (cache miss)
    start = time.time()
    results1 = rag.vector_search(query, k=5)
    time_miss = (time.time() - start) * 1000

    # Second query (cache hit)
    start = time.time()
    results2 = rag.vector_search(query, k=5)
    time_hit = (time.time() - start) * 1000

    improvement = ((time_miss - time_hit) / time_miss) * 100

    print(f"\nCache Miss: {time_miss:.2f}ms")
    print(f"Cache Hit: {time_hit:.2f}ms")
    print(f"Speed Improvement: {improvement:.1f}%")

    return time_miss, time_hit

def performance_test_embedding_generation(rag):
    """Test embedding generation performance"""
    print("\n⚡ Embedding Generation Performance Test")
    print("="*60)

    texts = [
        "Short text for testing",
        "A medium-length text that contains some technical information about Neo4j and graph databases.",
        "A longer text that discusses multiple concepts including vector embeddings, semantic search, knowledge graphs, and retrieval augmented generation systems with detailed explanations and examples."
    ]

    for text in texts:
        start = time.time()
        embedding = rag.model.encode([text])[0]
        elapsed = (time.time() - start) * 1000

        print(f"\nText length: {len(text)} chars")
        print(f"  Embedding time: {elapsed:.2f}ms")
        print(f"  Dimensions: {len(embedding)}")

def main():
    """Run all performance tests"""

    print("\n🚀 NEO4J AURA PERFORMANCE TEST SUITE")
    print("="*60)

    # Connect to Aura
    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_username = os.getenv('NEO4J_USERNAME', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD')

    print(f"🔗 Target: {neo4j_uri}")

    try:
        rag = Neo4jRAG(uri=neo4j_uri, username=neo4j_username, password=neo4j_password)
        print("✅ Connected to Neo4j Aura")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return 1

    try:
        # Run tests
        vector_avg = performance_test_vector_search(rag, iterations=10)
        hybrid_avg = performance_test_hybrid_search(rag, iterations=5)
        cache_miss, cache_hit = performance_test_cache(rag)
        performance_test_embedding_generation(rag)

        # Summary
        print("\n" + "="*60)
        print("📊 PERFORMANCE SUMMARY")
        print("="*60)

        summary = [
            ['Metric', 'Performance', 'Status'],
            ['Vector Search (avg)', f'{vector_avg:.2f}ms', '✅ Excellent' if vector_avg < 200 else '⚠️ Acceptable'],
            ['Hybrid Search (avg)', f'{hybrid_avg:.2f}ms', '✅ Excellent' if hybrid_avg < 100 else '⚠️ Acceptable'],
            ['Cache Miss', f'{cache_miss:.2f}ms', ''],
            ['Cache Hit', f'{cache_hit:.2f}ms', '✅ Fast'],
            ['Cache Improvement', f'{((cache_miss-cache_hit)/cache_miss*100):.1f}%', '']
        ]

        print(tabulate(summary, headers='firstrow', tablefmt='grid'))

        # Get database stats
        stats = rag.get_stats()
        print(f"\n📊 Database State:")
        print(f"  Documents: {stats['documents']}")
        print(f"  Chunks: {stats['chunks']}")

        print(f"\n✅ Performance testing complete!")

    finally:
        rag.close()

if __name__ == "__main__":
    main()
