"""
Test script for the optimized RAG system that can handle large datasets
"""

from neo4j_rag_optimized import Neo4jRAGOptimized, RAGQueryEngineOptimized
import time

def test_optimized_rag():
    """Test the optimized RAG system"""

    print("🚀 TESTING OPTIMIZED NEO4J RAG SYSTEM 🚀\n")
    print("=" * 60)

    # Initialize optimized RAG system
    print("Initializing optimized RAG system...")
    rag = Neo4jRAGOptimized()
    engine = RAGQueryEngineOptimized(rag)

    # Get database stats
    stats = rag.get_stats()
    print(f"\n📊 Database Statistics:")
    print(f"  • Documents: {stats['documents']}")
    print(f"  • Chunks: {stats['chunks']}")
    if stats['documents'] > 0:
        print(f"  • Avg chunks per doc: {stats['chunks'] / stats['documents']:.1f}")

    # Test queries covering different knowledge areas
    test_queries = [
        # Production & Operations
        "How do I configure Neo4j memory settings for production?",
        "What are Neo4j clustering and high availability options?",

        # RAG Implementation
        "What are best practices for vector search in Neo4j?",
        "How to use the Neo4j GraphRAG Python library?",

        # Development & Cypher
        "How to write efficient Cypher queries?",
        "What are Neo4j indexing strategies?",

        # Original sample queries
        "What is Neo4j?",
        "Tell me about graph databases"
    ]

    print("\n" + "=" * 60)
    print("TESTING OPTIMIZED VECTOR SEARCH")
    print("=" * 60)

    for i, query in enumerate(test_queries[:4], 1):  # Test first 4 queries
        print(f"\n❓ Query {i}: {query[:60]}...")
        print("-" * 40)

        start_time = time.time()

        try:
            # Perform optimized vector search
            results = rag.vector_search_optimized(query, k=3)
            search_time = time.time() - start_time

            if results:
                print(f"✅ Found {len(results)} results in {search_time:.3f}s")

                # Show top result
                if results:
                    top_result = results[0]
                    print(f"\n📚 Top Result (Score: {top_result['score']:.3f}):")
                    print(f"  Doc ID: {top_result.get('doc_id', 'unknown')}")
                    source = top_result.get('metadata', {}).get('source', 'unknown')
                    print(f"  Source: {source}")
                    text_preview = top_result['text'][:150] if len(top_result['text']) > 150 else top_result['text']
                    print(f"  Text: {text_preview}...")
            else:
                print(f"⚠️ No results found")

        except Exception as e:
            print(f"❌ Error during search: {str(e)[:100]}")

    # Test hybrid search
    print("\n" + "=" * 60)
    print("TESTING OPTIMIZED HYBRID SEARCH")
    print("=" * 60)

    test_query = "Neo4j production configuration memory settings"
    print(f"\n❓ Hybrid Query: {test_query}")
    print("-" * 40)

    start_time = time.time()
    try:
        results = rag.hybrid_search_optimized(test_query, k=3)
        search_time = time.time() - start_time

        if results:
            print(f"✅ Found {len(results)} results in {search_time:.3f}s")
            for i, result in enumerate(results, 1):
                print(f"\n  Result {i} (Score: {result['score']:.3f}):")
                print(f"    Text: {result['text'][:100]}...")
        else:
            print(f"⚠️ No results found")

    except Exception as e:
        print(f"❌ Error during hybrid search: {str(e)[:100]}")

    # Test RAG query engine
    print("\n" + "=" * 60)
    print("TESTING OPTIMIZED RAG QUERY ENGINE")
    print("=" * 60)

    sample_question = "How to configure Neo4j for production with optimal memory settings?"
    print(f"\n❓ Question: {sample_question}")
    print("-" * 40)

    try:
        response = engine.query(sample_question, k=3)

        print(f"\n📚 Retrieved {len(response['sources'])} sources:")
        for i, source in enumerate(response['sources'], 1):
            print(f"  {i}. [{source['score']:.3f}] {source.get('doc_id', 'unknown')[:30]}...")

        print(f"\n💡 Context Preview:")
        context_preview = response['context'][:300] if len(response['context']) > 300 else response['context']
        print(f"  {context_preview}...")

    except Exception as e:
        print(f"❌ Error during RAG query: {str(e)[:100]}")

    print("\n" + "=" * 60)
    print("✅ OPTIMIZED RAG SYSTEM TEST COMPLETED")
    print("=" * 60)

    rag.close()

if __name__ == "__main__":
    test_optimized_rag()