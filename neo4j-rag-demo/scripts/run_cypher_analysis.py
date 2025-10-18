#!/usr/bin/env python3
"""
Execute Cypher Analysis Scripts Against Aura Instance
Runs all analysis queries and generates comprehensive report
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from dotenv import load_dotenv
from tabulate import tabulate
from pathlib import Path

load_dotenv()

def run_query(session, query_name, query, description=""):
    """Execute a Cypher query and format results"""
    print(f"\n{'='*70}")
    print(f"📊 {query_name}")
    if description:
        print(f"   {description}")
    print('='*70)

    try:
        result = session.run(query)
        records = list(result)

        if not records:
            print("   No results returned")
            return []

        # Convert to list of dicts
        data = []
        for record in records:
            data.append(dict(record))

        # Display as table
        if data:
            print(tabulate(data, headers='keys', tablefmt='grid'))

        return data

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def main():
    """Run all Cypher analysis queries"""

    print("\n🚀 NEO4J AURA CYPHER ANALYSIS")
    print("="*70)

    # Connect to Aura
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD')

    print(f"🔗 Connecting to: {uri}")

    driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:

        # 1. Overall Statistics
        run_query(session, "Overall System Statistics", """
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                COUNT(DISTINCT d) as total_documents,
                COUNT(c) as total_chunks,
                AVG(SIZE(d.content)) as avg_doc_size,
                MIN(SIZE(d.content)) as min_doc_size,
                MAX(SIZE(d.content)) as max_doc_size,
                SUM(SIZE(d.content)) as total_content_size
        """, "Document and chunk counts with size metrics")

        # 2. Category Distribution
        run_query(session, "Category Distribution", """
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                COALESCE(d.category, 'Uncategorized') as category,
                COUNT(DISTINCT d) as doc_count,
                COUNT(c) as chunk_count,
                AVG(SIZE(d.content)) as avg_size
            ORDER BY doc_count DESC
        """, "Documents grouped by category")

        # 3. PDF Document Inventory
        run_query(session, "PDF Document Inventory", """
            MATCH (d:Document)
            WHERE d.source CONTAINS '.pdf'
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            WITH d, COUNT(c) as chunk_count,
                 CASE WHEN d.source CONTAINS '/'
                      THEN split(d.source, '/')[-1]
                      ELSE d.source END as filename
            RETURN
                filename as pdf_document,
                COALESCE(d.category, 'uncategorized') as category,
                chunk_count as chunks,
                ROUND(SIZE(d.content) / 1000.0, 1) as size_kb,
                substring(toString(d.created), 0, 10) as uploaded
            ORDER BY chunk_count DESC
        """, "All PDF documents with metrics")

        # 4. Content Topic Analysis
        run_query(session, "Knowledge Topics Distribution", """
            MATCH (c:Chunk)
            WITH c.text as text
            RETURN
                CASE
                    WHEN text CONTAINS 'Neo4j' OR text CONTAINS 'neo4j' THEN 'Neo4j Database'
                    WHEN text CONTAINS 'RAG' OR text CONTAINS 'retrieval' THEN 'RAG Systems'
                    WHEN text CONTAINS 'vector' OR text CONTAINS 'embedding' THEN 'Vector/Embeddings'
                    WHEN text CONTAINS 'graph database' OR text CONTAINS 'Graph' THEN 'Graph Databases'
                    WHEN text CONTAINS 'machine learning' OR text CONTAINS 'ML' THEN 'Machine Learning'
                    WHEN text CONTAINS 'knowledge graph' THEN 'Knowledge Graphs'
                    WHEN text CONTAINS 'Cypher' OR text CONTAINS 'cypher' THEN 'Cypher Language'
                    WHEN text CONTAINS 'algorithm' OR text CONTAINS 'Algorithm' THEN 'Algorithms'
                    WHEN text CONTAINS 'neural' OR text CONTAINS 'GNN' THEN 'Neural Networks'
                    ELSE 'Other Topics'
                END as knowledge_area,
                COUNT(*) as chunk_count
            ORDER BY chunk_count DESC
        """, "Content topics identified across all chunks")

        # 5. Publisher/Source Analysis
        run_query(session, "Publishers & Sources", """
            MATCH (d:Document)
            WHERE d.source CONTAINS '.pdf'
            WITH d.source as source, d
            WITH
                CASE
                    WHEN source CONTAINS 'oreilly' OR source CONTAINS 'OReilly' THEN 'O\\'Reilly Media'
                    WHEN source CONTAINS 'arxiv' OR source CONTAINS '2312.' OR source CONTAINS '2309.' THEN 'arXiv Papers'
                    WHEN source CONTAINS 'neo4j' OR source CONTAINS 'Neo4j' THEN 'Neo4j Official'
                    WHEN source CONTAINS 'Beginning' THEN 'Apress'
                    WHEN source CONTAINS 'Deep-Learning' OR source CONTAINS 'Graph-Representation' THEN 'Academic Books'
                    ELSE 'Other'
                END as publisher, d
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                publisher,
                COUNT(DISTINCT d) as documents,
                COUNT(c) as total_chunks,
                ROUND(AVG(toFloat(SIZE(d.content))) / 1000, 1) as avg_doc_size_kb
            ORDER BY documents DESC
        """, "Content sources and publishers")

        # 6. Embedding Coverage
        run_query(session, "Embedding Coverage Analysis", """
            MATCH (c:Chunk)
            RETURN
                COUNT(c) as total_chunks,
                COUNT(c.embedding) as chunks_with_embedding,
                toFloat(COUNT(c.embedding)) / toFloat(COUNT(c)) * 100 as coverage_percentage
        """, "Vector embedding coverage")

        # 7. Chunk Size Distribution
        run_query(session, "Chunk Size Distribution", """
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
        """, "Distribution of chunk sizes")

        # 8. Data Integrity Checks
        print(f"\n{'='*70}")
        print("🔍 Data Integrity Checks")
        print('='*70)

        # Orphaned chunks
        result = session.run("""
            MATCH (c:Chunk)
            WHERE NOT (c)<-[:HAS_CHUNK]-()
            RETURN COUNT(c) as orphaned_chunks
        """)
        orphaned = result.single()['orphaned_chunks']

        # Documents without chunks
        result = session.run("""
            MATCH (d:Document)
            WHERE NOT (d)-[:HAS_CHUNK]->()
            RETURN COUNT(d) as docs_without_chunks
        """)
        no_chunks = result.single()['docs_without_chunks']

        # Duplicate documents
        result = session.run("""
            MATCH (d:Document)
            WITH d.source as source, COLLECT(d) as docs
            WHERE SIZE(docs) > 1
            RETURN source, SIZE(docs) as duplicate_count
        """)
        duplicates = list(result)

        print(f"\n✅ Orphaned Chunks: {orphaned}")
        print(f"✅ Documents Without Chunks: {no_chunks}")
        print(f"⚠️ Duplicate Documents: {len(duplicates)}")

        if duplicates:
            print("\nDuplicate Documents Found:")
            for dup in duplicates:
                filename = dup['source'].split('/')[-1] if '/' in dup['source'] else dup['source']
                print(f"  • {filename}: {dup['duplicate_count']} copies")

        # 9. Graph Structure
        run_query(session, "Graph Structure Overview", """
            MATCH (n)
            WITH COUNT(n) as node_count
            MATCH ()-[r]->()
            WITH node_count, COUNT(r) as relationship_count
            RETURN node_count, relationship_count
        """, "Total nodes and relationships")

        # 10. Document Processing Timeline
        run_query(session, "Upload Timeline", """
            MATCH (d:Document)
            WHERE d.created IS NOT NULL AND d.source CONTAINS '.pdf'
            WITH d, date(d.created) as upload_date
            WITH upload_date, COUNT(d) as docs_uploaded,
                 COLLECT(CASE WHEN d.source CONTAINS '/'
                              THEN split(d.source, '/')[-1]
                              ELSE d.source END)[0..3] as sample_files
            RETURN
                toString(upload_date) as upload_date,
                docs_uploaded,
                sample_files
            ORDER BY upload_date DESC
            LIMIT 5
        """, "Recent upload activity")

    driver.close()

    print(f"\n{'='*70}")
    print("✅ Cypher Analysis Complete!")
    print(f"   Instance: 6b870b04 (ma3u)")
    print(f"   Database: Neo4j 5.27-aura (enterprise)")
    print('='*70)

if __name__ == "__main__":
    main()
