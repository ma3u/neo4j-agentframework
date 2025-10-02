#!/usr/bin/env python3
"""
Advanced Usage Examples for Neo4j RAG System

This file contains more advanced examples including:
- Hybrid search
- Custom embeddings
- Performance optimization
- Cypher queries
"""

from neo4j_rag import Neo4jRAG
from neo4j_rag_optimized import Neo4jRAGOptimized
from sentence_transformers import SentenceTransformer
import time

# ============================================
# Example 1: Hybrid Search
# ============================================

def hybrid_search_example():
    """
    Hybrid search combines vector similarity with keyword matching.
    This gives you the best of both worlds.
    """
    rag = Neo4jRAG()

    # Query with specific keywords AND semantic meaning
    query = "Neo4j ACID compliance transactions"

    print(f"🔍 Hybrid Search: '{query}'\n")

    # Hybrid search
    results = rag.hybrid_search(
        query=query,
        k=5,
        vector_weight=0.7,    # 70% semantic similarity
        keyword_weight=0.3    # 30% keyword matching
    )

    print("Results (combined scoring):")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   {result['text'][:100]}...")

    rag.close()


# ============================================
# Example 2: Performance Benchmarking
# ============================================

def benchmark_search_methods():
    """
    Compare performance of different search methods.
    Helps you choose the right approach for your use case.
    """
    rag = Neo4jRAG()
    query = "graph database performance"

    print("⚡ Performance Benchmark\n")

    # Vector Search
    start = time.time()
    vector_results = rag.vector_search(query, k=10)
    vector_time = time.time() - start

    # Hybrid Search
    start = time.time()
    hybrid_results = rag.hybrid_search(query, k=10)
    hybrid_time = time.time() - start

    print(f"Vector Search: {vector_time:.3f}s ({len(vector_results)} results)")
    print(f"Hybrid Search: {hybrid_time:.3f}s ({len(hybrid_results)} results)")

    if vector_time < hybrid_time:
        print(f"\n✅ Vector search is {hybrid_time/vector_time:.1f}x faster")
    else:
        print(f"\n✅ Hybrid search is {vector_time/hybrid_time:.1f}x faster")

    rag.close()


# ============================================
# Example 3: Using Optimized Version
# ============================================

def optimized_for_large_datasets():
    """
    Use the optimized version for large datasets (>1000 documents).
    This version uses sampling and batching for better performance.
    """
    # Use optimized version
    rag = Neo4jRAGOptimized()

    print("🚀 Using Optimized RAG for large datasets\n")

    # Stats
    stats = rag.get_stats()
    print(f"Managing {stats['documents']} documents with {stats['chunks']} chunks")

    # Optimized search
    results = rag.vector_search_optimized(
        query="machine learning",
        k=5,
        batch_size=100  # Process in batches of 100
    )

    print(f"\nFound {len(results)} results using optimized search")

    rag.close()


# ============================================
# Example 4: Custom Cypher Queries
# ============================================

def custom_cypher_queries():
    """
    Run custom Cypher queries for advanced analysis.
    Cypher is Neo4j's query language for graphs.
    """
    rag = Neo4jRAG()

    print("🔧 Custom Cypher Queries\n")

    with rag.driver.session() as session:
        # Query 1: Document statistics by category
        print("1. Documents by category:")
        result = session.run("""
            MATCH (d:Document)
            RETURN d.category as category,
                   COUNT(d) as count,
                   AVG(SIZE(d.content)) as avg_size
            ORDER BY count DESC
        """)

        for record in result:
            cat = record.get('category', 'Unknown')
            count = record.get('count', 0)
            avg_size = record.get('avg_size', 0)
            print(f"   {cat}: {count} docs (avg {avg_size:.0f} chars)")

        # Query 2: Find documents with most chunks
        print("\n2. Documents with most chunks:")
        result = session.run("""
            MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
            RETURN d.source as source, COUNT(c) as chunk_count
            ORDER BY chunk_count DESC
            LIMIT 5
        """)

        for record in result:
            source = record.get('source', 'Unknown')
            chunks = record.get('chunk_count', 0)
            print(f"   {source}: {chunks} chunks")

    rag.close()


# ============================================
# Example 5: Similarity Threshold Search
# ============================================

def similarity_threshold_search():
    """
    Only return results above a certain similarity threshold.
    Useful when you need high-confidence matches only.
    """
    rag = Neo4jRAG()

    query = "specific technical term"
    min_score = 0.7  # Only results with 70%+ similarity

    print(f"🎯 High-Confidence Search (min score: {min_score})\n")

    # Get all results first
    all_results = rag.vector_search(query, k=20)

    # Filter by threshold
    filtered = [r for r in all_results if r['score'] >= min_score]

    print(f"Total results: {len(all_results)}")
    print(f"Above threshold: {len(filtered)}")

    if filtered:
        print("\nHigh-confidence matches:")
        for result in filtered[:3]:
            print(f"  Score {result['score']:.3f}: {result['text'][:80]}...")
    else:
        print("\nNo results met the threshold. Try lowering min_score.")

    rag.close()


# ============================================
# Example 6: Metadata Filtering
# ============================================

def search_with_metadata_filter():
    """
    Filter search results by metadata (category, date, author, etc.).
    Useful for targeted searches within specific document sets.
    """
    rag = Neo4jRAG()

    print("🏷️ Metadata-Filtered Search\n")

    # Search only in specific categories
    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
            WHERE d.category IN ['tutorial', 'guide']
              AND c.text CONTAINS 'database'
            RETURN c.text as text, d.category as category, d.source as source
            LIMIT 5
        """)

        print("Results from tutorials and guides only:")
        for record in result:
            cat = record.get('category')
            source = record.get('source')
            text = record.get('text', '')[:100]
            print(f"\n[{cat}] {source}")
            print(f"  {text}...")

    rag.close()


# ============================================
# Example 7: Export Results
# ============================================

def export_search_results():
    """
    Export search results to different formats.
    Useful for analysis or reporting.
    """
    import json
    import csv

    rag = Neo4jRAG()
    results = rag.vector_search("Neo4j features", k=5)

    # Export to JSON
    with open('search_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("✅ Exported to search_results.json")

    # Export to CSV
    with open('search_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Score', 'Text Preview', 'Source'])
        for r in results:
            writer.writerow([
                r['score'],
                r['text'][:100],
                r.get('metadata', {}).get('source', 'Unknown')
            ])
    print("✅ Exported to search_results.csv")

    rag.close()


# ============================================
# Main - Run Examples
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Neo4j RAG System - Advanced Examples")
    print("=" * 60)

    # Choose which example to run:

    # hybrid_search_example()
    # benchmark_search_methods()
    # optimized_for_large_datasets()
    custom_cypher_queries()
    # similarity_threshold_search()
    # search_with_metadata_filter()
    # export_search_results()

    print("\n✅ Advanced examples completed!")