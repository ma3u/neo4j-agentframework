#!/usr/bin/env python3
"""
Comprehensive RAG System Demo
Complete demonstration of Neo4j RAG capabilities with PDF documents
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_rag import Neo4jRAG, RAGQueryEngine
from src.docling_loader import DoclingDocumentLoader
from pathlib import Path
import time
from tabulate import tabulate
import json

def print_header():
    """Print demo header"""
    print("\n" + "="*70)
    print("🚀 NEO4J RAG SYSTEM - COMPREHENSIVE DEMONSTRATION")
    print("="*70)
    print("\nThis demo showcases:")
    print("  ✓ PDF document loading with Docling")
    print("  ✓ Vector and hybrid search")
    print("  ✓ Question answering with RAG")
    print("  ✓ Performance analysis")
    print("  ✓ Graph visualization")
    print("="*70)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔹 {title}")
    print('='*60)

def check_prerequisites():
    """Check if all prerequisites are met"""
    print_section("Prerequisites Check")

    checks = []

    # Check Neo4j connection
    try:
        rag = Neo4jRAG()
        checks.append(("Neo4j Connection", "✅ Connected"))
        rag.close()
    except Exception as e:
        checks.append(("Neo4j Connection", f"❌ Failed: {e}"))

    # Check for sample PDFs
    sample_dir = Path("../samples")
    pdf_files = list(sample_dir.glob("*.pdf")) if sample_dir.exists() else []
    if pdf_files:
        checks.append(("Sample PDFs", f"✅ Found {len(pdf_files)} PDFs"))
    else:
        checks.append(("Sample PDFs", "⚠️ No PDFs found in samples/"))

    # Check Docling
    try:
        from docling.document_converter import DocumentConverter
        checks.append(("Docling", "✅ Installed"))
    except ImportError:
        checks.append(("Docling", "❌ Not installed (pip install docling)"))

    # Display results
    for check, status in checks:
        print(f"  {check}: {status}")

    # Return success status
    return all("✅" in status for _, status in checks[:2])  # Neo4j and at least basic setup

def load_demo_documents(rag):
    """Load demonstration documents"""
    print_section("Loading Demo Documents")

    # First, load basic sample data
    print("\n📄 Loading basic sample documents...")
    from scripts.load_sample_data import create_sample_documents

    docs_before = rag.get_stats()['documents']
    documents = create_sample_documents()

    for doc in documents[:3]:  # Load first 3 sample docs
        doc_id = rag.add_document(
            content=doc['content'],
            metadata=doc['metadata']
        )
        print(f"  ✅ Loaded: {doc['metadata']['source']}")

    # Check if we have PDFs to load
    sample_pdf = Path("samples/arxiv_rag_paper.pdf")
    if sample_pdf.exists():
        print(f"\n📄 Loading PDF: {sample_pdf.name}")
        try:
            loader = DoclingDocumentLoader(neo4j_rag=rag)
            doc_info = loader.load_document(
                str(sample_pdf),
                metadata={"category": "research", "source": "arxiv"}
            )
            print(f"  ✅ PDF loaded: {doc_info['statistics']['character_count']:,} characters")
            print(f"     Tables: {doc_info['statistics']['table_count']}")
            print(f"     Sections: {doc_info['statistics']['section_count']}")
            loader.close()
        except Exception as e:
            print(f"  ⚠️ Could not load PDF: {e}")

    docs_after = rag.get_stats()['documents']
    print(f"\n📊 Documents loaded: {docs_after - docs_before}")

def demo_search_capabilities(rag):
    """Demonstrate various search capabilities"""
    print_section("Search Capabilities Demo")

    test_queries = [
        ("What is Neo4j?", "Basic question about Neo4j"),
        ("How do vector embeddings work?", "Technical concept query"),
        ("graph database performance", "Keyword-based search"),
        ("ACID transactions", "Specific feature search")
    ]

    results_summary = []

    for query, description in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print(f"   Type: {description}")
        print("-" * 50)

        # Vector search
        start = time.time()
        vector_results = rag.vector_search(query, k=3)
        vector_time = time.time() - start

        # Hybrid search
        start = time.time()
        hybrid_results = rag.hybrid_search(query, k=3)
        hybrid_time = time.time() - start

        # Display comparison
        print(f"\n  Vector Search ({vector_time*1000:.1f}ms):")
        if vector_results:
            top_result = vector_results[0]
            print(f"    Top Score: {top_result['score']:.3f}")
            print(f"    Text: {top_result['text'][:100]}...")

        print(f"\n  Hybrid Search ({hybrid_time*1000:.1f}ms):")
        if hybrid_results:
            top_result = hybrid_results[0]
            print(f"    Top Score: {top_result['score']:.3f}")
            print(f"    Text: {top_result['text'][:100]}...")

        results_summary.append({
            'Query': query[:30],
            'Vector Results': len(vector_results),
            'Vector Time (ms)': f"{vector_time*1000:.1f}",
            'Hybrid Results': len(hybrid_results),
            'Hybrid Time (ms)': f"{hybrid_time*1000:.1f}"
        })

    # Display summary table
    print("\n\n📊 Search Performance Summary:")
    print(tabulate(results_summary, headers='keys', tablefmt='grid'))

def demo_rag_qa(rag):
    """Demonstrate RAG question answering"""
    print_section("RAG Question Answering Demo")

    engine = RAGQueryEngine(rag)

    questions = [
        "What are the main features of Neo4j?",
        "How does RAG improve question answering?",
        "What is the difference between vector and hybrid search?",
        "How can I optimize Neo4j performance?",
        "What are the benefits of using graph databases?"
    ]

    print("\n💬 Asking questions and generating answers:\n")

    for i, question in enumerate(questions, 1):
        print(f"{i}. Question: {question}")
        print("   " + "-" * 50)

        start = time.time()
        response = engine.query(question, k=3)
        elapsed = time.time() - start

        print(f"   Answer: {response['answer'][:200]}...")
        print(f"   Sources: {len(response['sources'])} chunks used")
        print(f"   Time: {elapsed*1000:.1f}ms")

        if response.get('relevance_scores'):
            avg_relevance = sum(response['relevance_scores']) / len(response['relevance_scores'])
            print(f"   Relevance: {avg_relevance:.3f}")
        print()

def demo_advanced_features(rag):
    """Demonstrate advanced RAG features"""
    print_section("Advanced Features Demo")

    # 1. Category-specific search
    print("\n📂 Category-Specific Search:")
    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            RETURN DISTINCT d.category as category, COUNT(d) as count
            ORDER BY count DESC
        """)

        categories = [(r['category'], r['count']) for r in result]
        for cat, count in categories:
            print(f"  • {cat}: {count} documents")

        if categories:
            # Search within a specific category
            top_category = categories[0][0]
            print(f"\n  Searching in '{top_category}' category:")

            results = rag.vector_search(
                "important concepts",
                k=2,
                metadata_filter={'category': top_category}
            )

            for i, result in enumerate(results, 1):
                print(f"    {i}. {result['text'][:80]}...")

    # 2. Similarity threshold search
    print("\n🎯 High-Confidence Search (>0.7 similarity):")
    query = "Neo4j graph database"
    all_results = rag.vector_search(query, k=20)
    high_conf = [r for r in all_results if r['score'] > 0.7]

    print(f"  Query: '{query}'")
    print(f"  Total results: {len(all_results)}")
    print(f"  High confidence: {len(high_conf)}")

    if high_conf:
        print(f"  Top match (score: {high_conf[0]['score']:.3f}):")
        print(f"    {high_conf[0]['text'][:100]}...")

    # 3. Multi-query fusion
    print("\n🔀 Multi-Query Fusion:")
    queries = [
        "database performance",
        "optimize database",
        "speed up queries"
    ]

    print(f"  Related queries: {queries}")

    fusion_results = {}
    for q in queries:
        results = rag.vector_search(q, k=5)
        for r in results:
            key = r['text'][:50]
            if key not in fusion_results:
                fusion_results[key] = {'text': r['text'], 'score': r['score'], 'count': 1}
            else:
                fusion_results[key]['score'] = max(fusion_results[key]['score'], r['score'])
                fusion_results[key]['count'] += 1

    # Sort by frequency and score
    top_fusion = sorted(
        fusion_results.values(),
        key=lambda x: (x['count'], x['score']),
        reverse=True
    )[:3]

    print(f"  Top fusion results:")
    for i, result in enumerate(top_fusion, 1):
        print(f"    {i}. Found in {result['count']} queries (score: {result['score']:.3f})")
        print(f"       {result['text'][:80]}...")

def demo_graph_insights(rag):
    """Show graph database insights"""
    print_section("Graph Database Insights")

    with rag.driver.session() as session:
        # Document statistics
        result = session.run("""
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            WITH d, COUNT(c) as chunks
            RETURN
                COUNT(d) as total_docs,
                AVG(chunks) as avg_chunks,
                MAX(chunks) as max_chunks,
                MIN(chunks) as min_chunks
        """)

        stats = result.single()
        print("\n📊 Document Statistics:")
        print(f"  Total Documents: {stats['total_docs']}")
        print(f"  Avg Chunks/Doc: {stats['avg_chunks']:.1f}")
        print(f"  Max Chunks: {stats['max_chunks']}")
        print(f"  Min Chunks: {stats['min_chunks']}")

        # Embedding coverage
        result = session.run("""
            MATCH (c:Chunk)
            RETURN
                COUNT(c) as total_chunks,
                COUNT(c.embedding) as chunks_with_embedding
        """)

        embed_stats = result.single()
        coverage = (embed_stats['chunks_with_embedding'] / max(embed_stats['total_chunks'], 1)) * 100

        print("\n🧮 Embedding Coverage:")
        print(f"  Total Chunks: {embed_stats['total_chunks']}")
        print(f"  With Embeddings: {embed_stats['chunks_with_embedding']}")
        print(f"  Coverage: {coverage:.1f}%")

        # Top sources
        result = session.run("""
            MATCH (d:Document)
            RETURN d.source as source, d.category as category
            LIMIT 5
        """)

        print("\n📚 Sample Documents:")
        for record in result:
            source = record['source'][:40] + '...' if len(record['source']) > 40 else record['source']
            category = record.get('category', 'N/A')
            print(f"  • [{category}] {source}")

def performance_analysis(rag):
    """Analyze system performance"""
    print_section("Performance Analysis")

    # Benchmark different operations
    operations = []

    # Vector search benchmark
    queries = ["database", "Neo4j", "performance", "graph", "vector"]
    times = []
    for query in queries:
        start = time.time()
        rag.vector_search(query, k=5)
        times.append(time.time() - start)

    avg_time = sum(times) / len(times)
    operations.append({
        'Operation': 'Vector Search',
        'Avg Time (ms)': f"{avg_time*1000:.1f}",
        'Throughput': f"{1/avg_time:.1f} queries/sec"
    })

    # Hybrid search benchmark
    times = []
    for query in queries:
        start = time.time()
        rag.hybrid_search(query, k=5)
        times.append(time.time() - start)

    avg_time = sum(times) / len(times)
    operations.append({
        'Operation': 'Hybrid Search',
        'Avg Time (ms)': f"{avg_time*1000:.1f}",
        'Throughput': f"{1/avg_time:.1f} queries/sec"
    })

    # RAG query benchmark
    engine = RAGQueryEngine(rag)
    times = []
    for query in queries[:3]:  # Fewer RAG queries as they're slower
        start = time.time()
        engine.query(f"What is {query}?", k=3)
        times.append(time.time() - start)

    avg_time = sum(times) / len(times)
    operations.append({
        'Operation': 'RAG Query',
        'Avg Time (ms)': f"{avg_time*1000:.1f}",
        'Throughput': f"{1/avg_time:.1f} queries/sec"
    })

    # Display results
    print("\n⚡ Performance Benchmarks:")
    print(tabulate(operations, headers='keys', tablefmt='grid'))

    # System recommendations
    print("\n💡 Performance Recommendations:")
    print("  1. Use vector search for simple similarity queries")
    print("  2. Use hybrid search when keywords matter")
    print("  3. Cache frequently accessed embeddings")
    print("  4. Consider batch operations for multiple queries")
    print("  5. Optimize chunk size based on your use case")

def export_demo_results(rag):
    """Export demo results for analysis"""
    print_section("Exporting Demo Results")

    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'stats': rag.get_stats(),
        'sample_queries': [],
        'performance_metrics': {}
    }

    # Add sample query results
    test_query = "Neo4j features"
    vector_results = rag.vector_search(test_query, k=3)
    results['sample_queries'].append({
        'query': test_query,
        'type': 'vector',
        'results': len(vector_results),
        'top_score': vector_results[0]['score'] if vector_results else 0
    })

    # Save to file
    output_file = 'rag_demo_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n✅ Demo results exported to '{output_file}'")
    print(f"   Documents: {results['stats']['documents']}")
    print(f"   Chunks: {results['stats']['chunks']}")

def main():
    """Run the comprehensive RAG demo"""

    print_header()

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please:")
        print("  1. Start Neo4j: docker start neo4j-rag")
        print("  2. Install dependencies: pip install -r requirements.txt")
        return

    # Connect to Neo4j
    print_section("Connecting to Neo4j")
    try:
        rag = Neo4jRAG()
        print("✅ Connected successfully")

        # Get initial stats
        stats = rag.get_stats()
        print(f"📊 Initial state: {stats['documents']} documents, {stats['chunks']} chunks")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    try:
        # Run demo sections
        load_demo_documents(rag)
        demo_search_capabilities(rag)
        demo_rag_qa(rag)
        demo_advanced_features(rag)
        demo_graph_insights(rag)
        performance_analysis(rag)
        export_demo_results(rag)

        # Final summary
        print_section("Demo Complete")
        final_stats = rag.get_stats()
        print(f"\n📊 Final Statistics:")
        print(f"   Documents: {final_stats['documents']}")
        print(f"   Chunks: {final_stats['chunks']}")

        print("\n✅ All demonstrations completed successfully!")
        print("\n💡 Next Steps:")
        print("  1. Explore the graph in Neo4j Browser: http://localhost:7474")
        print("  2. Try the statistics script: python scripts/rag_statistics.py")
        print("  3. Run search examples: python scripts/rag_search_examples.py")
        print("  4. Visualize the graph: python scripts/rag_graph_queries.py")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        rag.close()
        print("\n👋 Thank you for trying the Neo4j RAG System!")

if __name__ == "__main__":
    main()