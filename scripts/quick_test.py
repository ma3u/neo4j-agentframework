"""
Quick test script for the enhanced RAG system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_rag import Neo4jRAG, RAGQueryEngine
import time

def test_enhanced_rag():
    """Test the enhanced RAG system with comprehensive Neo4j knowledge"""

    print("🚀 TESTING ENHANCED NEO4J RAG SYSTEM 🚀\n")
    print("=" * 60)

    # Initialize RAG system
    print("Initializing RAG system...")
    rag = Neo4jRAG()
    engine = RAGQueryEngine(rag)

    # Get database stats
    stats = rag.get_stats()
    print(f"\n📊 Database Statistics:")
    print(f"  • Documents: {stats['documents']}")
    print(f"  • Chunks: {stats['chunks']}")
    print(f"  • Avg chunks per doc: {stats['chunks'] / max(stats['documents'], 1):.1f}")

    # Test queries covering different knowledge areas
    test_queries = [
        # Production & Operations
        "How do I configure Neo4j memory settings for production?",
        "What are Neo4j backup best practices?",

        # RAG Implementation
        "What are best practices for vector search in Neo4j?",
        "How to optimize chunk size for RAG applications?",

        # Development & Cypher
        "How to write efficient Cypher queries?",
        "What are Neo4j indexing strategies?"
    ]

    print("\n" + "=" * 60)
    print("TESTING ENHANCED QUERY CAPABILITIES")
    print("=" * 60)

    for i, query in enumerate(test_queries, 1):
        print(f"\n❓ Query {i}: {query}")
        print("-" * 40)

        start_time = time.time()

        # Perform vector search
        results = rag.vector_search(query, k=3)
        search_time = time.time() - start_time

        if results:
            print(f"✅ Found {len(results)} relevant results in {search_time:.3f}s")

            # Show top result
            top_result = results[0]
            print(f"\n📚 Top Result (Score: {top_result['score']:.3f}):")
            print(f"  Source: {top_result.get('metadata', {}).get('source', 'unknown')}")
            print(f"  Text: {top_result['text'][:150]}...")
        else:
            print(f"❌ No results found")

    # Test RAG query engine
    print("\n" + "=" * 60)
    print("TESTING RAG QUERY ENGINE")
    print("=" * 60)

    sample_question = "How to configure Neo4j for high availability and clustering?"
    print(f"\n❓ Question: {sample_question}")
    print("-" * 40)

    response = engine.query(sample_question, k=3)

    print(f"\n📚 Retrieved {len(response['sources'])} sources:")
    for i, source in enumerate(response['sources'], 1):
        print(f"  {i}. [{source['score']:.3f}] {source['doc_id']}: {source['text'][:80]}...")

    print(f"\n💡 Context Preview:")
    print(f"  {response['context'][:300]}...")

    print("\n" + "=" * 60)
    print("✅ ENHANCED RAG SYSTEM TEST COMPLETED")
    print("=" * 60)

    rag.close()

if __name__ == "__main__":
    test_enhanced_rag()