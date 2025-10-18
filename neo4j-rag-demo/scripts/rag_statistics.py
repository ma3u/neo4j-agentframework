#!/usr/bin/env python3
"""
RAG Statistics and Analysis Script
Provides comprehensive statistics about your PDF documents in Neo4j
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_rag import Neo4jRAG
import pandas as pd
from datetime import datetime
from tabulate import tabulate

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print('='*60)

def get_document_statistics(rag):
    """Get detailed statistics about documents in the database"""

    print_section("Document Statistics")

    with rag.driver.session() as session:
        # Overall statistics
        result = session.run("""
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                COUNT(DISTINCT d) as total_documents,
                COUNT(c) as total_chunks,
                AVG(SIZE(d.content)) as avg_doc_size,
                MIN(SIZE(d.content)) as min_doc_size,
                MAX(SIZE(d.content)) as max_doc_size,
                SUM(SIZE(d.content)) as total_content_size
        """)

        stats = result.single()
        print(f"\n📈 Overall Statistics:")
        print(f"  Total Documents: {stats['total_documents']}")
        print(f"  Total Chunks: {stats['total_chunks']}")
        print(f"  Average Chunks per Document: {stats['total_chunks']/max(stats['total_documents'], 1):.1f}")
        print(f"  Total Content Size: {stats['total_content_size']:,} characters")
        print(f"  Average Document Size: {stats['avg_doc_size']:.0f} characters")
        print(f"  Min Document Size: {stats['min_doc_size']} characters")
        print(f"  Max Document Size: {stats['max_doc_size']} characters")

def get_pdf_statistics(rag):
    """Get statistics specifically about PDF documents"""

    print_section("PDF Document Analysis")

    with rag.driver.session() as session:
        # PDF-specific statistics
        result = session.run("""
            MATCH (d:Document)
            WHERE d.source CONTAINS '.pdf' OR d.category = 'pdf'
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                d.source as source,
                d.category as category,
                COUNT(c) as chunk_count,
                SIZE(d.content) as doc_size,
                d.created as created
            ORDER BY chunk_count DESC
        """)

        pdf_docs = []
        for record in result:
            pdf_docs.append({
                'Source': record['source'][:40] + '...' if len(record['source']) > 40 else record['source'],
                'Category': record.get('category', 'N/A'),
                'Chunks': record['chunk_count'],
                'Size (chars)': f"{record['doc_size']:,}",
                'Created': record.get('created', 'N/A')
            })

        if pdf_docs:
            print(f"\n📄 Found {len(pdf_docs)} PDF documents:")
            df = pd.DataFrame(pdf_docs)
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        else:
            print("\n⚠️ No PDF documents found in the database")

def get_category_distribution(rag):
    """Analyze document distribution by category"""

    print_section("Category Distribution")

    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                COALESCE(d.category, 'Uncategorized') as category,
                COUNT(DISTINCT d) as doc_count,
                COUNT(c) as chunk_count,
                AVG(SIZE(d.content)) as avg_size
            ORDER BY doc_count DESC
        """)

        categories = []
        for record in result:
            categories.append({
                'Category': record['category'],
                'Documents': record['doc_count'],
                'Chunks': record['chunk_count'],
                'Avg Size': f"{record['avg_size']:.0f}"
            })

        if categories:
            df = pd.DataFrame(categories)
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def get_embedding_statistics(rag):
    """Analyze embedding coverage and quality"""

    print_section("Embedding Analysis")

    with rag.driver.session() as session:
        # Embedding coverage
        result = session.run("""
            MATCH (c:Chunk)
            RETURN
                COUNT(c) as total_chunks,
                COUNT(c.embedding) as chunks_with_embedding,
                AVG(SIZE(c.embedding)) as avg_embedding_size
        """)

        embed_stats = result.single()
        coverage = (embed_stats['chunks_with_embedding'] / max(embed_stats['total_chunks'], 1)) * 100

        print(f"\n🧮 Embedding Coverage:")
        print(f"  Total Chunks: {embed_stats['total_chunks']}")
        print(f"  Chunks with Embeddings: {embed_stats['chunks_with_embedding']}")
        print(f"  Coverage: {coverage:.1f}%")
        print(f"  Embedding Dimensions: {embed_stats['avg_embedding_size']:.0f}")

        # Quality check
        if coverage < 100:
            print(f"\n⚠️ Warning: {embed_stats['total_chunks'] - embed_stats['chunks_with_embedding']} chunks are missing embeddings")

def get_content_type_analysis(rag):
    """Analyze different types of content (PDFs, notebooks, text)"""

    print_section("Content Type Analysis")

    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            WITH d,
                CASE
                    WHEN d.source STARTS WITH 'notebook:' THEN 'Notebook'
                    WHEN d.source CONTAINS '.pdf' THEN 'PDF'
                    WHEN d.source CONTAINS '.md' THEN 'Markdown'
                    WHEN d.source CONTAINS '.txt' THEN 'Text'
                    WHEN d.source CONTAINS '.docx' THEN 'Word'
                    ELSE 'Other'
                END as doc_type
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                doc_type,
                COUNT(DISTINCT d) as count,
                COUNT(c) as chunks,
                AVG(SIZE(d.content)) as avg_size
            ORDER BY count DESC
        """)

        content_types = []
        for record in result:
            content_types.append({
                'Type': record['doc_type'],
                'Documents': record['count'],
                'Chunks': record['chunks'],
                'Avg Size': f"{record['avg_size']:.0f}"
            })

        if content_types:
            df = pd.DataFrame(content_types)
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def get_recent_documents(rag, limit=5):
    """Get the most recently added documents"""

    print_section(f"Recent Documents (Last {limit})")

    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            WHERE d.created IS NOT NULL
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                d.source as source,
                d.created as created,
                d.category as category,
                COUNT(c) as chunks,
                SIZE(d.content) as size
            ORDER BY d.created DESC
            LIMIT $limit
        """, limit=limit)

        recent = []
        for record in result:
            recent.append({
                'Source': record['source'][:40] + '...' if len(record['source']) > 40 else record['source'],
                'Created': record.get('created', 'N/A'),
                'Category': record.get('category', 'N/A'),
                'Chunks': record['chunks'],
                'Size': f"{record['size']:,}"
            })

        if recent:
            df = pd.DataFrame(recent)
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
        else:
            print("\n⚠️ No documents with creation dates found")

def get_chunk_distribution(rag):
    """Analyze chunk size and distribution"""

    print_section("Chunk Distribution Analysis")

    with rag.driver.session() as session:
        result = session.run("""
            MATCH (c:Chunk)
            RETURN
                MIN(SIZE(c.text)) as min_size,
                MAX(SIZE(c.text)) as max_size,
                AVG(SIZE(c.text)) as avg_size,
                percentileCont(SIZE(c.text), 0.5) as median_size,
                COUNT(c) as total_chunks
        """)

        chunk_stats = result.single()

        print(f"\n📏 Chunk Size Statistics:")
        print(f"  Total Chunks: {chunk_stats['total_chunks']}")
        print(f"  Min Size: {chunk_stats['min_size']} characters")
        print(f"  Max Size: {chunk_stats['max_size']} characters")
        print(f"  Average Size: {chunk_stats['avg_size']:.0f} characters")
        print(f"  Median Size: {chunk_stats['median_size']:.0f} characters")

        # Distribution by size buckets
        result = session.run("""
            MATCH (c:Chunk)
            WITH c, SIZE(c.text) as size
            RETURN
                CASE
                    WHEN size < 100 THEN '0-100'
                    WHEN size < 200 THEN '100-200'
                    WHEN size < 300 THEN '200-300'
                    WHEN size < 400 THEN '300-400'
                    WHEN size < 500 THEN '400-500'
                    ELSE '500+'
                END as size_range,
                COUNT(c) as count
            ORDER BY size_range
        """)

        print("\n📊 Chunk Size Distribution:")
        for record in result:
            bar_length = int(record['count'] / 10) if record['count'] > 0 else 0
            bar = '█' * min(bar_length, 40)
            print(f"  {record['size_range']:8} chars: {bar} ({record['count']})")

def get_orphaned_data_check(rag):
    """Check for data integrity issues"""

    print_section("Data Integrity Check")

    with rag.driver.session() as session:
        # Check for orphaned chunks
        result = session.run("""
            MATCH (c:Chunk)
            WHERE NOT (c)<-[:HAS_CHUNK]-()
            RETURN COUNT(c) as orphaned_chunks
        """)
        orphaned = result.single()['orphaned_chunks']

        # Check for documents without chunks
        result = session.run("""
            MATCH (d:Document)
            WHERE NOT (d)-[:HAS_CHUNK]->()
            RETURN COUNT(d) as docs_without_chunks
        """)
        no_chunks = result.single()['docs_without_chunks']

        # Check for duplicate documents
        result = session.run("""
            MATCH (d:Document)
            WITH d.content as content, COLLECT(d) as docs
            WHERE SIZE(docs) > 1
            RETURN COUNT(docs) as duplicate_groups
        """)
        duplicates = result.single()['duplicate_groups']

        print(f"\n🔍 Integrity Status:")

        if orphaned > 0:
            print(f"  ⚠️ Found {orphaned} orphaned chunks")
        else:
            print(f"  ✅ No orphaned chunks")

        if no_chunks > 0:
            print(f"  ⚠️ Found {no_chunks} documents without chunks")
        else:
            print(f"  ✅ All documents have chunks")

        if duplicates and duplicates > 0:
            print(f"  ⚠️ Found {duplicates} groups of duplicate documents")
        else:
            print(f"  ✅ No duplicate documents")

def main():
    """Run all statistics analyses"""

    print("\n🚀 NEO4J RAG STATISTICS ANALYSIS")
    print("="*60)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_username = os.getenv('NEO4J_USERNAME', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')

    print(f"🔗 Target: {neo4j_uri}")

    # Connect to Neo4j
    try:
        rag = Neo4jRAG(uri=neo4j_uri, username=neo4j_username, password=neo4j_password)
        print("✅ Connected to Neo4j Aura")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        print("\nMake sure Neo4j is running:")
        print("  docker start neo4j-rag")
        return

    try:
        # Run all analyses
        get_document_statistics(rag)
        get_pdf_statistics(rag)
        get_category_distribution(rag)
        get_content_type_analysis(rag)
        get_embedding_statistics(rag)
        get_chunk_distribution(rag)
        get_recent_documents(rag)
        get_orphaned_data_check(rag)

        print("\n" + "="*60)
        print("✅ Analysis complete!")
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    finally:
        rag.close()

if __name__ == "__main__":
    main()