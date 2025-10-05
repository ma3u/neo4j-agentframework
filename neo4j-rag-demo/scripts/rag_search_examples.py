#!/usr/bin/env python3
"""
Advanced RAG Search Examples
Demonstrates various search techniques with PDF and document content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_rag import Neo4jRAG, RAGQueryEngine
import time
from tabulate import tabulate
import numpy as np

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def vector_search_examples(rag):
    """Demonstrate vector/semantic search capabilities"""

    print_section("Vector Search Examples")

    queries = [
        "What is Neo4j and how does it work?",
        "graph database performance optimization",
        "How to implement RAG systems?",
        "vector embeddings and similarity search",
        "PDF document processing techniques"
    ]

    for query in queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 50)

        start = time.time()
        results = rag.vector_search(query, k=3)
        elapsed = time.time() - start

        if results:
            print(f"⏱️ Search time: {elapsed*1000:.1f}ms")
            print(f"📊 Found {len(results)} results:\n")

            for i, result in enumerate(results, 1):
                score = result['score']
                text = result['text'][:150].replace('\n', ' ')
                source = result.get('metadata', {}).get('source', 'Unknown')

                print(f"  {i}. Score: {score:.3f}")
                print(f"     Source: {source}")
                print(f"     Text: {text}...")
                print()
        else:
            print("  ❌ No results found")

def hybrid_search_examples(rag):
    """Demonstrate hybrid search (vector + keyword)"""

    print_section("Hybrid Search Examples")

    hybrid_queries = [
        ("Neo4j ACID transactions", 0.7, 0.3),  # More semantic
        ("PDF table extraction", 0.5, 0.5),      # Balanced
        ("graph database Cypher", 0.3, 0.7),     # More keyword
    ]

    for query, vector_weight, keyword_weight in hybrid_queries:
        print(f"\n📝 Query: '{query}'")
        print(f"   Weights: Vector={vector_weight}, Keyword={keyword_weight}")
        print("-" * 50)

        results = rag.hybrid_search(
            query=query,
            k=3,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight
        )

        if results:
            for i, result in enumerate(results, 1):
                score = result['score']
                text = result['text'][:100].replace('\n', ' ')
                print(f"  {i}. Combined Score: {score:.3f}")
                print(f"     Text: {text}...")
        else:
            print("  ❌ No results found")

def search_by_category(rag):
    """Search within specific document categories"""

    print_section("Category-Specific Search")

    categories = ['pdf', 'tutorial', 'documentation', 'notebook']

    for category in categories:
        print(f"\n📂 Searching in category: '{category}'")

        with rag.driver.session() as session:
            result = session.run("""
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                WHERE d.category = $category
                WITH c, d
                ORDER BY c.chunk_index
                LIMIT 3
                RETURN c.text as text, d.source as source, c.chunk_index as index
            """, category=category)

            found = False
            for record in result:
                found = True
                text = record['text'][:100].replace('\n', ' ')
                print(f"  • Chunk {record['index']}: {text}...")

            if not found:
                print(f"  ⚠️ No documents in category '{category}'")

def similarity_threshold_search(rag):
    """Search with minimum similarity threshold"""

    print_section("Similarity Threshold Search")

    query = "machine learning and artificial intelligence"
    thresholds = [0.3, 0.5, 0.7]

    print(f"\n📝 Query: '{query}'")

    for threshold in thresholds:
        print(f"\n🎯 Minimum similarity: {threshold}")
        print("-" * 30)

        # Get results
        results = rag.vector_search(query, k=20)

        # Filter by threshold
        filtered = [r for r in results if r['score'] >= threshold]

        print(f"  Results above threshold: {len(filtered)}/{len(results)}")

        if filtered:
            # Show score distribution
            scores = [r['score'] for r in filtered]
            print(f"  Score range: {min(scores):.3f} - {max(scores):.3f}")
            print(f"  Average score: {np.mean(scores):.3f}")

            # Show top result
            top = filtered[0]
            print(f"\n  Top result (score: {top['score']:.3f}):")
            print(f"  {top['text'][:100]}...")

def search_pdf_specific_content(rag):
    """Search specifically within PDF documents"""

    print_section("PDF-Specific Content Search")

    with rag.driver.session() as session:
        # Search only in PDF documents
        result = session.run("""
            MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
            WHERE d.source CONTAINS '.pdf' OR d.category = 'pdf'
            WITH d, c,
                 gds.similarity.cosine(
                     c.embedding,
                     $query_embedding
                 ) as similarity
            WHERE similarity > 0.5
            RETURN d.source as source,
                   c.text as text,
                   similarity,
                   c.chunk_index as index
            ORDER BY similarity DESC
            LIMIT 5
        """, query_embedding=rag.model.encode("data analysis techniques").tolist())

        print("\n🔍 Searching for 'data analysis techniques' in PDFs:")
        print("-" * 50)

        results = list(result)
        if results:
            for i, record in enumerate(results, 1):
                print(f"\n{i}. PDF: {record['source']}")
                print(f"   Similarity: {record['similarity']:.3f}")
                print(f"   Chunk #{record['index']}")
                print(f"   Text: {record['text'][:100]}...")
        else:
            print("  ℹ️ No PDF content found matching the query")

def multi_query_fusion(rag):
    """Combine results from multiple related queries"""

    print_section("Multi-Query Fusion Search")

    base_query = "database optimization"
    related_queries = [
        "database optimization",
        "improve database performance",
        "database speed tuning",
        "optimize query execution"
    ]

    print(f"\n🎯 Base concept: '{base_query}'")
    print("📍 Searching with multiple query variations...")

    all_results = {}
    for query in related_queries:
        results = rag.vector_search(query, k=5)
        for result in results:
            text_key = result['text'][:50]  # Use first 50 chars as key
            if text_key not in all_results:
                all_results[text_key] = {
                    'text': result['text'],
                    'score': result['score'],
                    'count': 1,
                    'queries': [query]
                }
            else:
                all_results[text_key]['score'] = max(all_results[text_key]['score'], result['score'])
                all_results[text_key]['count'] += 1
                all_results[text_key]['queries'].append(query)

    # Sort by frequency and score
    fusion_results = sorted(
        all_results.values(),
        key=lambda x: (x['count'], x['score']),
        reverse=True
    )[:3]

    print(f"\n📊 Fusion Results (from {len(related_queries)} queries):\n")
    for i, result in enumerate(fusion_results, 1):
        print(f"{i}. Found in {result['count']} queries")
        print(f"   Best score: {result['score']:.3f}")
        print(f"   Matched queries: {', '.join(result['queries'])}")
        print(f"   Text: {result['text'][:100]}...")
        print()

def contextual_rag_search(rag):
    """Demonstrate RAG with contextual question answering"""

    print_section("Contextual RAG Question Answering")

    engine = RAGQueryEngine(rag)

    questions = [
        "What are the main features of Neo4j?",
        "How do vector embeddings work in RAG systems?",
        "What techniques are used for PDF processing?",
        "Explain the difference between vector and hybrid search",
        "How to optimize graph database performance?"
    ]

    for question in questions:
        print(f"\n❓ Question: {question}")
        print("-" * 50)

        response = engine.query(question, k=3)

        print(f"💡 Answer: {response['answer'][:300]}...")
        print(f"\n📚 Based on {len(response['sources'])} sources:")

        for i, source in enumerate(response['sources'][:2], 1):
            print(f"   {i}. {source[:80]}...")

        if response.get('relevance_scores'):
            avg_relevance = np.mean(response['relevance_scores'])
            print(f"\n📊 Average relevance: {avg_relevance:.3f}")

def search_performance_comparison(rag):
    """Compare performance of different search methods"""

    print_section("Search Performance Comparison")

    test_query = "graph database query optimization"

    print(f"\n📝 Test Query: '{test_query}'")
    print("-" * 50)

    results_table = []

    # 1. Vector Search
    start = time.time()
    vector_results = rag.vector_search(test_query, k=5)
    vector_time = time.time() - start
    results_table.append({
        'Method': 'Vector Search',
        'Time (ms)': f"{vector_time*1000:.1f}",
        'Results': len(vector_results),
        'Top Score': f"{vector_results[0]['score']:.3f}" if vector_results else "N/A"
    })

    # 2. Hybrid Search
    start = time.time()
    hybrid_results = rag.hybrid_search(test_query, k=5)
    hybrid_time = time.time() - start
    results_table.append({
        'Method': 'Hybrid Search',
        'Time (ms)': f"{hybrid_time*1000:.1f}",
        'Results': len(hybrid_results),
        'Top Score': f"{hybrid_results[0]['score']:.3f}" if hybrid_results else "N/A"
    })

    # 3. RAG Query
    start = time.time()
    engine = RAGQueryEngine(rag)
    rag_response = engine.query(test_query, k=5)
    rag_time = time.time() - start
    results_table.append({
        'Method': 'RAG Query',
        'Time (ms)': f"{rag_time*1000:.1f}",
        'Results': len(rag_response['sources']),
        'Top Score': 'N/A (generates answer)'
    })

    print("\n📊 Performance Comparison:")
    print(tabulate(results_table, headers='keys', tablefmt='grid'))

    # Show speedup
    if vector_time > 0:
        print(f"\n⚡ Speedup Analysis:")
        print(f"  Hybrid vs Vector: {vector_time/hybrid_time:.2f}x")
        print(f"  RAG vs Vector: {rag_time/vector_time:.2f}x (includes generation)")

def main():
    """Run all search examples"""

    print("\n🚀 NEO4J RAG ADVANCED SEARCH EXAMPLES")
    print("="*60)

    # Connect to Neo4j
    try:
        rag = Neo4jRAG()
        print("✅ Connected to Neo4j")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        return

    try:
        # Get initial stats
        stats = rag.get_stats()
        print(f"📊 Database contains {stats['documents']} documents with {stats['chunks']} chunks")

        # Run all search examples
        vector_search_examples(rag)
        hybrid_search_examples(rag)
        search_by_category(rag)
        similarity_threshold_search(rag)
        search_pdf_specific_content(rag)
        multi_query_fusion(rag)
        contextual_rag_search(rag)
        search_performance_comparison(rag)

        print("\n" + "="*60)
        print("✅ Search examples complete!")

    finally:
        rag.close()

if __name__ == "__main__":
    main()