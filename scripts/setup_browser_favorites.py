#!/usr/bin/env python3
"""
Neo4j Browser Favorites Setup Script
Helps set up essential Cypher queries as favorites in Neo4j Browser
"""

import json
from pathlib import Path
from neo4j import GraphDatabase
import sys
import os

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from neo4j_rag import Neo4jRAG
except ImportError:
    print("❌ Could not import Neo4jRAG. Make sure you're in the project directory.")
    sys.exit(1)

def test_database_connection():
    """Test connection and get basic stats"""
    print("🔍 Testing database connection...")

    try:
        rag = Neo4jRAG()
        with rag.driver.session() as session:
            # Test basic connectivity
            result = session.run("""
                MATCH (d:Document)
                OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                WITH COUNT(DISTINCT d) as docs, COUNT(c) as chunks
                MATCH (c2:Chunk) WHERE c2.embedding IS NOT NULL
                RETURN
                    docs as total_documents,
                    chunks as total_chunks,
                    COUNT(c2) as chunks_with_embeddings,
                    ROUND(toFloat(COUNT(c2)) / toFloat(chunks) * 100, 1) as coverage_percent
            """)

            record = result.single()
            if record:
                print(f"✅ Connected successfully!")
                print(f"   📚 Documents: {record['total_documents']}")
                print(f"   📝 Chunks: {record['total_chunks']}")
                print(f"   🧮 With Embeddings: {record['chunks_with_embeddings']}")
                print(f"   ✅ Coverage: {record['coverage_percent']}%")
                return True, rag
            else:
                print("❌ No data found in database")
                return False, None

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False, None

def test_key_queries(rag):
    """Test a few key queries to ensure they work"""
    print("\n🧪 Testing key queries...")

    queries = {
        "PDF Documents": """
            MATCH (d:Document)
            WHERE d.source CONTAINS '.pdf' OR d.category = 'pdf'
            RETURN COUNT(d) as pdf_count
        """,
        "Topic Distribution": """
            MATCH (c:Chunk)
            WITH c.text as text
            RETURN
                CASE
                    WHEN text CONTAINS 'Neo4j' OR text CONTAINS 'neo4j' THEN 'Neo4j Database'
                    WHEN text CONTAINS 'RAG' OR text CONTAINS 'retrieval' THEN 'RAG Systems'
                    WHEN text CONTAINS 'vector' OR text CONTAINS 'embedding' THEN 'Vector/Embeddings'
                    WHEN text CONTAINS 'graph database' OR text CONTAINS 'Graph' THEN 'Graph Databases'
                    ELSE 'Other Topics'
                END as topic,
                COUNT(*) as chunk_count
            ORDER BY chunk_count DESC
            LIMIT 5
        """,
        "Publisher Analysis": """
            MATCH (d:Document)
            WHERE d.source CONTAINS '.pdf'
            WITH d.source as source, d
            WITH
                CASE
                    WHEN source CONTAINS 'oreilly' OR source CONTAINS 'OReilly' THEN 'O\\'Reilly Media'
                    WHEN source CONTAINS 'manning' OR source CONTAINS 'Manning' THEN 'Manning Publications'
                    WHEN source CONTAINS 'arxiv' THEN 'arXiv Papers'
                    WHEN source CONTAINS 'neo4j' OR source CONTAINS 'Neo4j' THEN 'Neo4j Official'
                    ELSE 'Other Publishers'
                END as publisher, d
            RETURN publisher, COUNT(DISTINCT d) as document_count
            ORDER BY document_count DESC
        """
    }

    try:
        with rag.driver.session() as session:
            for query_name, query in queries.items():
                print(f"   Testing {query_name}...")
                result = session.run(query)
                records = list(result)
                if records:
                    print(f"   ✅ {query_name}: {len(records)} results")
                    if query_name == "PDF Documents":
                        print(f"      📄 PDF Documents: {records[0]['pdf_count']}")
                    elif query_name == "Topic Distribution":
                        for record in records[:3]:
                            print(f"      🏷️ {record['topic']}: {record['chunk_count']} chunks")
                    elif query_name == "Publisher Analysis":
                        for record in records:
                            print(f"      📚 {record['publisher']}: {record['document_count']} docs")
                else:
                    print(f"   ⚠️ {query_name}: No results")

    except Exception as e:
        print(f"❌ Query testing failed: {e}")
        return False

    return True

def create_browser_instructions():
    """Create detailed instructions for setting up Neo4j Browser"""

    instructions = """
# 🚀 Neo4j Browser Setup Instructions

## Step 1: Access Neo4j Browser
1. Open your web browser
2. Go to: http://localhost:7474/browser/
3. Login with:
   - Username: neo4j
   - Password: password

## Step 2: Add Essential Queries as Favorites

### Method 1: Copy-Paste Individual Queries

1. **Click the star (⭐) icon** in the left sidebar
2. **Click "Add empty favorite"** (+ button)
3. **Copy a query** from `scripts/neo4j_content_analysis.cypher`
4. **Paste into the editor**
5. **Give it a name** (e.g., "📊 Dashboard Overview")
6. **Click the star** to save
7. **Repeat** for each query you want

### Method 3: Quick Setup Queries

Copy these essential queries to get started:

#### 1. Dashboard Overview (Run First!)
```cypher
// 📊 Complete System Statistics
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
    ROUND(toFloat(COUNT(c2)) / chunks * 100, 1) + '%' as `✅ Coverage`;
```

#### 2. PDF Document List
```cypher
// 📄 All PDF Documents with Key Metrics
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
    ROUND(SIZE(d.content) / 1000.0, 1) + ' KB' as `💾 Size`,
    substring(toString(d.created), 0, 16) as `📅 Uploaded`
ORDER BY chunk_count DESC;
```

#### 3. Topic Analysis
```cypher
// 🏷️ Knowledge Topics Distribution
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
        WHEN text CONTAINS 'performance' OR text CONTAINS 'optimization' THEN 'Performance'
        WHEN text CONTAINS 'neural' OR text CONTAINS 'GNN' THEN 'Neural Networks'
        ELSE 'Other Topics'
    END as `🧠 Knowledge Area`,
    COUNT(*) as `📊 Chunk Count`
ORDER BY `📊 Chunk Count` DESC;
```

#### 4. Search Example
```cypher
// 🔍 Sample Content Search - Change the search term
MATCH (c:Chunk)
WHERE c.text CONTAINS 'Neo4j'  // <-- Change this term
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
WITH c, d,
     CASE WHEN d.source CONTAINS '/'
          THEN split(d.source, '/')[-1]
          ELSE d.source END as filename
RETURN
    filename as `📖 Source Document`,
    c.chunk_index as `#️⃣ Chunk ID`,
    substring(c.text, 0, 200) + '...' as `📝 Content Preview`
ORDER BY filename, c.chunk_index
LIMIT 20;
```

## Step 3: Run Your Analysis

1. **Start with Dashboard Overview** - Get system statistics
2. **Check PDF Document List** - See all uploaded documents
3. **Explore Topic Analysis** - Understand content themes
4. **Try Content Search** - Find specific information

## Tips for Success

- **Use Graph View**: Click the graph icon for visualizations
- **Save Parameters**: Use `:param searchTerm => 'your term'`
- **Export Results**: Click download icon for CSV export
- **Switch Views**: Table view for data, Graph view for relationships

## Getting Help

- Type `:help` in Neo4j Browser for built-in help
- All queries are in `scripts/neo4j_content_analysis.cypher`
- Setup guide is in `scripts/browser_quick_setup.md`

Happy exploring! 🚀
"""

    return instructions

def main():
    """Main execution function"""
    print("🚀 Neo4j Browser Favorites Setup")
    print("=" * 50)

    # Test database connection
    connected, rag = test_database_connection()
    if not connected:
        print("\n❌ Cannot proceed without database connection.")
        print("   Make sure Neo4j is running: docker ps | grep neo4j")
        return

    # Test key queries
    if test_key_queries(rag):
        print("\n✅ All queries working correctly!")
    else:
        print("\n⚠️ Some queries had issues, but proceeding...")

    # Create instruction file
    instructions_file = Path(__file__).parent / "browser_setup_instructions.md"
    with open(instructions_file, 'w') as f:
        f.write(create_browser_instructions())

    print(f"\n📝 Created setup instructions: {instructions_file}")

    # Final instructions
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. Open Neo4j Browser: http://localhost:7474/browser/")
    print("2. Login: neo4j / password")
    print("3. Follow instructions in browser_setup_instructions.md")
    print("4. Copy queries from scripts/neo4j_content_analysis.cypher")
    print("5. Add them as favorites in Neo4j Browser")

    print("\n🚀 Ready to explore your knowledge graph!")

    # Close connection
    if rag:
        rag.close()

if __name__ == "__main__":
    main()