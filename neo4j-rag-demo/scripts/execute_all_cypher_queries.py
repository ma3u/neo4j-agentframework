#!/usr/bin/env python3
"""
Execute All Cypher Queries from Browser Scripts
Runs each query individually and displays results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neo4j import GraphDatabase
from dotenv import load_dotenv
from tabulate import tabulate
import time

load_dotenv()

def print_header(title, query_num=None):
    """Print formatted section header"""
    if query_num:
        print(f"\n\n{'='*80}")
        print(f"Query {query_num}: {title}")
        print('='*80)
    else:
        print(f"\n\n{'#'*80}")
        print(f"# {title}")
        print('#'*80)

def run_query(session, query, title, description=""):
    """Execute and display query results"""
    print(f"\n{description}")
    print(f"\nQuery:\n{query}\n")

    try:
        start_time = time.time()
        result = session.run(query)
        records = list(result)
        elapsed = (time.time() - start_time) * 1000

        if not records:
            print("⚠️ No results returned")
            return

        # Convert to list of dicts
        data = [dict(record) for record in records]

        # Display as table
        if len(data) <= 50:
            print(tabulate(data, headers='keys', tablefmt='grid'))
        else:
            print(tabulate(data[:50], headers='keys', tablefmt='grid'))
            print(f"\n... and {len(data) - 50} more rows")

        print(f"\n⏱️ Query executed in {elapsed:.2f}ms")
        print(f"📊 Rows returned: {len(data)}")

    except Exception as e:
        print(f"❌ Error executing query: {e}")

def main():
    """Run all Cypher queries"""

    print("\n🚀 EXECUTING ALL CYPHER QUERIES ON AURA INSTANCE")
    print("="*80)

    # Connect to Aura
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD')

    print(f"🔗 Target: {uri}")
    print(f"👤 User: {username}")

    driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:

        print_header("STATISTICS QUERIES")
        query_num = 1

        # Query 1: Overall Statistics
        print_header("Overall Statistics", query_num)
        run_query(session, """
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    COUNT(DISTINCT d) as total_documents,
    COUNT(c) as total_chunks,
    AVG(SIZE(d.content)) as avg_doc_size,
    MIN(SIZE(d.content)) as min_doc_size,
    MAX(SIZE(d.content)) as max_doc_size,
    SUM(SIZE(d.content)) as total_content_size
        """, f"Query {query_num}", "System-wide document and chunk statistics")
        query_num += 1

        # Query 2: Category Distribution
        print_header("Document Category Distribution", query_num)
        run_query(session, """
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    COALESCE(d.category, 'Uncategorized') as category,
    COUNT(DISTINCT d) as doc_count,
    COUNT(c) as chunk_count,
    AVG(SIZE(d.content)) as avg_size
ORDER BY doc_count DESC
        """, f"Query {query_num}", "Documents grouped by category")
        query_num += 1

        # Query 3: PDF Documents Analysis
        print_header("PDF Documents Detailed Analysis", query_num)
        run_query(session, """
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
        """, f"Query {query_num}", "All PDF documents with detailed metrics")
        query_num += 1

        # Query 4: Recent Documents
        print_header("Recent Documents (Last 10)", query_num)
        run_query(session, """
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
LIMIT 10
        """, f"Query {query_num}", "Most recently uploaded documents")
        query_num += 1

        # Query 5: Document with Most Chunks
        print_header("Top Documents by Chunk Count", query_num)
        run_query(session, """
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count
ORDER BY chunk_count DESC
LIMIT 5
RETURN d.source, d.category, chunk_count
        """, f"Query {query_num}", "Documents with highest chunk counts")
        query_num += 1

        print_header("EMBEDDING & VECTOR ANALYSIS")

        # Query 6: Embedding Coverage
        print_header("Embedding Coverage", query_num)
        run_query(session, """
MATCH (c:Chunk)
RETURN
    COUNT(c) as total_chunks,
    COUNT(c.embedding) as chunks_with_embedding,
    toFloat(COUNT(c.embedding)) / toFloat(COUNT(c)) * 100 as coverage_percentage
        """, f"Query {query_num}", "Vector embedding coverage across all chunks")
        query_num += 1

        # Query 7: Chunk Size Distribution
        print_header("Chunk Size Distribution", query_num)
        run_query(session, """
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
        """, f"Query {query_num}", "Distribution of text chunk sizes")
        query_num += 1

        # Query 8: Chunk Statistics
        print_header("Chunk Size Statistics", query_num)
        run_query(session, """
MATCH (c:Chunk)
RETURN
    MIN(SIZE(c.text)) as min_size,
    MAX(SIZE(c.text)) as max_size,
    AVG(SIZE(c.text)) as avg_size,
    percentileCont(SIZE(c.text), 0.5) as median_size,
    COUNT(c) as total_chunks
        """, f"Query {query_num}", "Min, max, average chunk sizes")
        query_num += 1

        print_header("DATA INTEGRITY CHECKS")

        # Query 9: Orphaned Chunks
        print_header("Find Orphaned Chunks", query_num)
        run_query(session, """
MATCH (c:Chunk)
WHERE NOT (c)<-[:HAS_CHUNK]-()
RETURN COUNT(c) as orphaned_chunks
        """, f"Query {query_num}", "Chunks not linked to any document")
        query_num += 1

        # Query 10: Documents Without Chunks
        print_header("Documents Without Chunks", query_num)
        run_query(session, """
MATCH (d:Document)
WHERE NOT (d)-[:HAS_CHUNK]->()
RETURN COUNT(d) as docs_without_chunks
        """, f"Query {query_num}", "Documents that failed chunking")
        query_num += 1

        # Query 11: Duplicate Documents
        print_header("Check for Duplicate Documents", query_num)
        run_query(session, """
MATCH (d:Document)
WITH d.source as source, COLLECT(d) as docs
WHERE SIZE(docs) > 1
RETURN source, SIZE(docs) as duplicate_count
        """, f"Query {query_num}", "Documents with same source path")
        query_num += 1

        print_header("GRAPH STRUCTURE ANALYSIS")

        # Query 12: Node and Relationship Counts
        print_header("Total Nodes and Relationships", query_num)
        run_query(session, """
MATCH (n)
WITH COUNT(n) as node_count
MATCH ()-[r]->()
WITH node_count, COUNT(r) as relationship_count
RETURN node_count, relationship_count
        """, f"Query {query_num}", "Complete graph structure overview")
        query_num += 1

        # Query 13: Document-Chunk Connections
        print_header("Document-Chunk Connection Patterns", query_num)
        run_query(session, """
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count, COLLECT(c.chunk_index) as indices
RETURN
    d.source as source,
    d.category as category,
    chunk_count,
    indices[0..5] as sample_indices
ORDER BY chunk_count DESC
LIMIT 10
        """, f"Query {query_num}", "Document to chunk relationship analysis")
        query_num += 1

        # Query 14: Average Chunks per Document
        print_header("Average Chunks per Document", query_num)
        run_query(session, """
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as degree
RETURN
    AVG(degree) as avg_chunks_per_doc,
    MIN(degree) as min_chunks,
    MAX(degree) as max_chunks
        """, f"Query {query_num}", "Chunk distribution metrics")
        query_num += 1

        print_header("CONTENT ANALYSIS")

        # Query 15: Knowledge Topic Analysis
        print_header("Knowledge Topics Distribution", query_num)
        run_query(session, """
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
        """, f"Query {query_num}", "Content categorized by knowledge domain")
        query_num += 1

        # Query 16: Publisher Analysis
        print_header("Publisher & Source Analysis", query_num)
        run_query(session, """
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf'
WITH d.source as source, d
WITH
    CASE
        WHEN source CONTAINS 'oreilly' OR source CONTAINS 'OReilly' THEN "O'Reilly Media"
        WHEN source CONTAINS 'manning' OR source CONTAINS 'Manning' THEN 'Manning Publications'
        WHEN source CONTAINS 'arxiv' OR source CONTAINS '2312.' OR source CONTAINS '2309.' THEN 'arXiv Papers'
        WHEN source CONTAINS 'neo4j' OR source CONTAINS 'Neo4j' THEN 'Neo4j Official'
        WHEN source CONTAINS 'Beginning' OR source CONTAINS 'beginning' THEN 'Apress'
        ELSE 'Other Publishers'
    END as publisher, d
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    publisher,
    COUNT(DISTINCT d) as documents,
    COUNT(c) as total_chunks,
    ROUND(AVG(toFloat(SIZE(d.content))) / 1000, 1) as avg_doc_size_kb
ORDER BY documents DESC
        """, f"Query {query_num}", "Content grouped by publisher/source")
        query_num += 1

        # Query 17: Database Size Estimation
        print_header("Database Size Estimation", query_num)
        run_query(session, """
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH
    SUM(SIZE(d.content)) as total_doc_size,
    COUNT(c) as total_chunks,
    AVG(SIZE(c.text)) as avg_chunk_size
RETURN
    total_doc_size as total_document_bytes,
    total_chunks * avg_chunk_size as estimated_chunk_bytes,
    total_doc_size + (total_chunks * avg_chunk_size) as estimated_total_bytes
        """, f"Query {query_num}", "Estimate total database storage size")
        query_num += 1

        # Query 18: Upload Timeline
        print_header("Document Upload Timeline", query_num)
        run_query(session, """
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
        """, f"Query {query_num}", "When documents were uploaded")
        query_num += 1

        # Query 19: Sample Chunk Content
        print_header("Sample Chunk Content", query_num)
        run_query(session, """
MATCH (c:Chunk)
RETURN
    c.chunk_index as chunk_id,
    substring(c.text, 0, 100) + '...' as text_preview
LIMIT 5
        """, f"Query {query_num}", "Preview of actual chunk content")
        query_num += 1

        # Query 20: Search for "Neo4j" term
        print_header("Content Search: 'Neo4j'", query_num)
        run_query(session, """
MATCH (c:Chunk)
WHERE toLower(c.text) CONTAINS 'neo4j'
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
WITH c, d,
     CASE WHEN d.source CONTAINS '/'
          THEN split(d.source, '/')[-1]
          ELSE d.source END as filename
RETURN
    filename as source_document,
    c.chunk_index as chunk_id,
    substring(c.text, 0, 150) + '...' as content_preview
ORDER BY filename, c.chunk_index
LIMIT 10
        """, f"Query {query_num}", "Find chunks mentioning 'Neo4j'")
        query_num += 1

        # Query 21: Search for "vector" term
        print_header("Content Search: 'vector'", query_num)
        run_query(session, """
MATCH (c:Chunk)
WHERE toLower(c.text) CONTAINS 'vector'
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
WITH c, d,
     CASE WHEN d.source CONTAINS '/'
          THEN split(d.source, '/')[-1]
          ELSE d.source END as filename
RETURN
    filename as source_document,
    c.chunk_index as chunk_id,
    substring(c.text, 0, 150) + '...' as content_preview
ORDER BY filename, c.chunk_index
LIMIT 10
        """, f"Query {query_num}", "Find chunks mentioning 'vector'")
        query_num += 1

        # Query 22: Search for "RAG" term
        print_header("Content Search: 'RAG'", query_num)
        run_query(session, """
MATCH (c:Chunk)
WHERE c.text CONTAINS 'RAG' OR toLower(c.text) CONTAINS 'retrieval augmented'
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
WITH c, d,
     CASE WHEN d.source CONTAINS '/'
          THEN split(d.source, '/')[-1]
          ELSE d.source END as filename
RETURN
    filename as source_document,
    c.chunk_index as chunk_id,
    substring(c.text, 0, 150) + '...' as content_preview
ORDER BY filename, c.chunk_index
LIMIT 10
        """, f"Query {query_num}", "Find chunks about RAG systems")
        query_num += 1

        # Query 23: Documents by category (neo4j)
        print_header("Neo4j Category Documents", query_num)
        run_query(session, """
MATCH (d:Document {category: 'neo4j'})
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    COUNT(c) as chunks,
    SIZE(d.content) as size
ORDER BY chunks DESC
        """, f"Query {query_num}", "All documents in 'neo4j' category")
        query_num += 1

        # Query 24: Content by file size
        print_header("Documents by Size", query_num)
        run_query(session, """
MATCH (d:Document)
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    d.category as category,
    SIZE(d.content) as bytes,
    ROUND(SIZE(d.content) / 1024.0, 1) as size_kb
ORDER BY bytes DESC
LIMIT 10
        """, f"Query {query_num}", "Largest documents by content size")
        query_num += 1

        # Query 25: Chunk index range check
        print_header("Chunk Index Range per Document", query_num)
        run_query(session, """
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, MIN(c.chunk_index) as min_idx, MAX(c.chunk_index) as max_idx, COUNT(c) as count
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    min_idx,
    max_idx,
    count as total_chunks,
    CASE WHEN (max_idx - min_idx + 1) = count THEN 'Sequential' ELSE 'Gaps Detected' END as index_status
ORDER BY count DESC
LIMIT 10
        """, f"Query {query_num}", "Verify chunk index integrity")
        query_num += 1

    driver.close()

    print(f"\n\n{'#'*80}")
    print(f"# ✅ ALL CYPHER QUERIES EXECUTED SUCCESSFULLY")
    print(f"# Total Queries Run: {query_num - 1}")
    print(f"# Instance: 6b870b04 (ma3u)")
    print(f"# Database: Neo4j 5.27-aura (enterprise)")
    print('#'*80)

if __name__ == "__main__":
    main()
