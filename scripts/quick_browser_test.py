#!/usr/bin/env python3
"""
Quick test to verify Neo4j Browser queries work with current data
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from neo4j_rag import Neo4jRAG

def main():
    print("🧪 Testing Neo4j Browser Queries")
    print("=" * 40)

    rag = Neo4jRAG()

    # Test the main dashboard query
    print("\n📊 DASHBOARD OVERVIEW:")
    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            WITH COUNT(DISTINCT d) as docs, COUNT(c) as chunks,
                 SUM(SIZE(d.content)) as total_chars
            MATCH (c2:Chunk) WHERE c2.embedding IS NOT NULL
            MATCH (pdf:Document) WHERE pdf.source CONTAINS '.pdf'
            RETURN
                docs as `📚 Total Documents`,
                chunks as `📝 Total Chunks`,
                COUNT(DISTINCT pdf) as `📄 PDF Documents`,
                COUNT(c2) as `🧮 With Embeddings`,
                ROUND(total_chars / 1000000.0, 1) + ' MB' as `💾 Content Size`,
                ROUND(toFloat(COUNT(c2)) / chunks * 100, 1) + '%' as `✅ Coverage`
        """)

        record = result.single()
        for key, value in record.items():
            print(f"   {key}: {value}")

    # Test PDF listing
    print("\n📄 TOP PDF DOCUMENTS:")
    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            WHERE d.source CONTAINS '.pdf' OR d.category CONTAINS 'pdf'
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            WITH d, COUNT(c) as chunk_count,
                 CASE WHEN d.source CONTAINS '/'
                      THEN split(d.source, '/')[-1]
                      ELSE d.source END as filename
            RETURN
                filename as `📖 PDF Document`,
                COALESCE(d.category, 'uncategorized') as `🏷️ Category`,
                chunk_count as `📝 Chunks`,
                ROUND(SIZE(d.content) / 1000.0, 1) + ' KB' as `💾 Size`
            ORDER BY chunk_count DESC
            LIMIT 10
        """)

        for record in result:
            doc = record['📖 PDF Document']
            chunks = record['📝 Chunks']
            size = record['💾 Size']
            print(f"   📖 {doc}: {chunks} chunks, {size}")

    # Test search functionality
    print("\n🔍 SAMPLE SEARCH (Neo4j):")
    with rag.driver.session() as session:
        result = session.run("""
            MATCH (c:Chunk)
            WHERE c.text CONTAINS 'Neo4j'
            OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
            WITH c, d,
                 CASE WHEN d.source CONTAINS '/'
                      THEN split(d.source, '/')[-1]
                      ELSE d.source END as filename
            RETURN
                filename as `📖 Source Document`,
                c.chunk_index as `#️⃣ Chunk ID`,
                substring(c.text, 0, 100) + '...' as `📝 Content Preview`
            ORDER BY filename, c.chunk_index
            LIMIT 5
        """)

        for record in result:
            source = record['📖 Source Document']
            chunk_id = record['#️⃣ Chunk ID']
            preview = record['📝 Content Preview']
            print(f"   📖 {source} #{chunk_id}:")
            print(f"      {preview}")

    print("\n✅ All queries working! Ready for Neo4j Browser setup.")
    print("\n🎯 Next: Open http://localhost:7474/browser/ and add these as favorites!")

    rag.close()

if __name__ == "__main__":
    main()