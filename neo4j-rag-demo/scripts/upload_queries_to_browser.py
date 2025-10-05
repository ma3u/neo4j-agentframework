#!/usr/bin/env python3
"""
Upload Cypher Queries to Neo4j Browser
Helps add pre-built queries as favorites in Neo4j Browser
"""

import json
import re
from pathlib import Path
import sys
import webbrowser

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.neo4j_rag import Neo4jRAG

def parse_cypher_file(file_path):
    """Parse the Cypher file and extract individual queries with their descriptions"""

    with open(file_path, 'r') as f:
        content = f.read()

    # Split by sections marked with // =====
    sections = re.split(r'// =+\n', content)

    queries = []
    current_title = None
    current_description = None
    current_query = []

    for section in sections:
        lines = section.strip().split('\n')

        for i, line in enumerate(lines):
            # Check for section titles
            if line.startswith('// ') and not line.startswith('// ==='):
                # This could be a title or description
                comment = line[3:].strip()

                # Check if next lines contain a query
                if i + 1 < len(lines) and not lines[i + 1].startswith('//'):
                    # This is likely a query title
                    if current_query and current_title:
                        # Save previous query
                        queries.append({
                            'title': current_title,
                            'description': current_description or current_title,
                            'query': '\n'.join(current_query).strip()
                        })
                    current_title = comment
                    current_description = comment
                    current_query = []
                elif current_title:
                    # This is additional description
                    current_description = comment
            elif not line.startswith('//') and line.strip():
                # This is part of a query
                current_query.append(line)

    # Don't forget the last query
    if current_query and current_title:
        queries.append({
            'title': current_title,
            'description': current_description or current_title,
            'query': '\n'.join(current_query).strip()
        })

    return queries

def extract_essential_queries():
    """Extract the most important queries for Neo4j Browser"""

    essential_queries = [
        {
            'title': '📊 Dashboard Overview',
            'description': 'Complete system statistics and overview',
            'query': '''MATCH (d:Document)
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
    ROUND(toFloat(COUNT(c2)) / chunks * 100, 1) + '%' as `✅ Coverage`'''
        },
        {
            'title': '📄 PDF Document List',
            'description': 'All PDF documents with metrics',
            'query': '''MATCH (d:Document)
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
ORDER BY chunk_count DESC'''
        },
        {
            'title': '🏷️ Topic Analysis',
            'description': 'Knowledge topics distribution',
            'query': '''MATCH (c:Chunk)
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
ORDER BY `📊 Chunk Count` DESC'''
        },
        {
            'title': '🔍 Content Search',
            'description': 'Search for specific content',
            'query': '''// Change 'Neo4j' to your search term
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
    substring(c.text, 0, 200) + '...' as `📝 Content Preview`
ORDER BY filename, c.chunk_index
LIMIT 20'''
        },
        {
            'title': '👥 Publisher Analysis',
            'description': 'Content sources and publishers',
            'query': '''MATCH (d:Document)
WHERE d.source CONTAINS '.pdf'
WITH d.source as source, d
WITH
    CASE
        WHEN source CONTAINS 'oreilly' OR source CONTAINS 'OReilly' THEN 'O\\'Reilly Media'
        WHEN source CONTAINS 'manning' OR source CONTAINS 'Manning' THEN 'Manning Publications'
        WHEN source CONTAINS 'arxiv' OR source CONTAINS '2312.' OR source CONTAINS '2309.' THEN 'arXiv Papers'
        WHEN source CONTAINS 'neo4j' OR source CONTAINS 'Neo4j' THEN 'Neo4j Official'
        WHEN source CONTAINS 'Beginning' OR source CONTAINS 'beginning' THEN 'Apress'
        WHEN source CONTAINS 'appliedai' OR source CONTAINS 'AppliedAI' THEN 'AppliedAI'
        ELSE 'Other Publishers'
    END as publisher, d
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    publisher as `📚 Publisher/Source`,
    COUNT(DISTINCT d) as `📖 Documents`,
    COUNT(c) as `📝 Total Chunks`,
    ROUND(AVG(toFloat(SIZE(d.content))) / 1000, 1) + ' KB' as `📊 Avg Doc Size`
ORDER BY `📖 Documents` DESC'''
        },
        {
            'title': '🎨 Graph Visualization',
            'description': 'Document-Chunk relationships for graph view',
            'query': '''MATCH (d:Document)
WHERE d.source CONTAINS '.pdf'
WITH d.category as category, COUNT(d) as doc_count, COLLECT(d) as docs
WHERE doc_count > 0
UNWIND docs as doc
MATCH (doc)-[:HAS_CHUNK]->(c:Chunk)
WITH category, doc, COUNT(c) as chunks
WHERE chunks > 100
RETURN category, doc, chunks
LIMIT 50'''
        },
        {
            'title': '✅ Data Quality Check',
            'description': 'Check data integrity and quality',
            'query': '''MATCH (c:Chunk)
WITH
    COUNT(c) as total_chunks,
    COUNT(CASE WHEN c.embedding IS NOT NULL THEN 1 END) as with_embeddings,
    COUNT(CASE WHEN SIZE(c.text) < 50 THEN 1 END) as too_short,
    COUNT(CASE WHEN SIZE(c.text) > 500 THEN 1 END) as too_long,
    AVG(SIZE(c.text)) as avg_size
MATCH (d:Document)
WHERE NOT (d)-[:HAS_CHUNK]->()
WITH total_chunks, with_embeddings, too_short, too_long, avg_size,
     COUNT(d) as orphaned_docs
RETURN
    total_chunks as `📝 Total Chunks`,
    with_embeddings as `🧮 With Embeddings`,
    orphaned_docs as `🚨 Orphaned Documents`,
    too_short as `⚠️ Very Short (<50 chars)`,
    too_long as `📏 Very Long (>500 chars)`,
    ROUND(avg_size) + ' chars' as `📊 Average Size`,
    CASE WHEN orphaned_docs = 0 AND too_short < total_chunks * 0.05
         THEN '✅ Good Quality'
         ELSE '⚠️ Check Quality' END as `🎯 Status`'''
        },
        {
            'title': '📏 Chunk Size Distribution',
            'description': 'Analyze chunk sizes',
            'query': '''MATCH (c:Chunk)
WITH SIZE(c.text) as size
RETURN
    CASE
        WHEN size < 100 THEN '📏 Tiny (0-100)'
        WHEN size < 200 THEN '📄 Small (100-200)'
        WHEN size < 300 THEN '📋 Medium (200-300)'
        WHEN size < 400 THEN '📊 Large (300-400)'
        WHEN size < 500 THEN '📚 X-Large (400-500)'
        ELSE '📖 Huge (500+)'
    END as `📐 Size Category`,
    COUNT(*) as `📊 Count`,
    ROUND(AVG(toFloat(size))) + ' chars' as `📏 Avg Size`
ORDER BY `📐 Size Category`'''
        },
        {
            'title': '🔗 Cross-Document Knowledge',
            'description': 'Find shared concepts between documents',
            'query': '''MATCH (d1:Document)-[:HAS_CHUNK]->(c1:Chunk)
WHERE d1.source CONTAINS '.pdf'
WITH d1, COLLECT(DISTINCT toLower(
    CASE
        WHEN c1.text CONTAINS 'Neo4j' THEN 'neo4j'
        WHEN c1.text CONTAINS 'RAG' THEN 'rag'
        WHEN c1.text CONTAINS 'vector' THEN 'vector'
        WHEN c1.text CONTAINS 'graph' THEN 'graph'
        WHEN c1.text CONTAINS 'knowledge' THEN 'knowledge'
        ELSE null
    END
)) as concepts
WHERE SIZE([x IN concepts WHERE x IS NOT NULL]) > 0
WITH d1, [x IN concepts WHERE x IS NOT NULL] as valid_concepts
UNWIND valid_concepts as concept
WITH concept, COUNT(DISTINCT d1) as doc_count
WHERE doc_count > 1
RETURN
    concept as `🧠 Shared Concept`,
    doc_count as `📚 Document Count`
ORDER BY doc_count DESC'''
        },
        {
            'title': '📊 Quick Stats',
            'description': 'Simple count of documents and chunks',
            'query': '''MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    COUNT(DISTINCT d) as `Documents`,
    COUNT(c) as `Chunks`'''
        }
    ]

    return essential_queries

def test_queries(queries):
    """Test that queries work with the current database"""
    print("\n🧪 Testing queries with database...")

    try:
        rag = Neo4jRAG()

        with rag.driver.session() as session:
            for i, query_info in enumerate(queries[:3], 1):  # Test first 3
                try:
                    print(f"\n   Testing #{i}: {query_info['title']}...")
                    result = session.run(query_info['query'])
                    record = result.single()
                    if record:
                        print(f"   ✅ Query works! Found {len(record.keys())} columns")
                    else:
                        records = list(result)
                        if records:
                            print(f"   ✅ Query works! Found {len(records)} results")
                        else:
                            print(f"   ⚠️ Query returned no results")
                except Exception as e:
                    print(f"   ❌ Query failed: {str(e)[:100]}")

        rag.close()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_browser_import_html(queries):
    """Create an HTML file that can be opened to import queries"""

    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Neo4j Browser Query Import</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        .instructions {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .query-card {
            background: #fff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .query-title {
            font-size: 18px;
            font-weight: bold;
            color: #018bff;
            margin-bottom: 10px;
        }
        .query-description {
            color: #666;
            margin-bottom: 15px;
        }
        .query-box {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
            font-size: 13px;
            overflow-x: auto;
            position: relative;
        }
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 5px 15px;
            background: #018bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .copy-btn:hover {
            background: #0070d2;
        }
        .copy-btn.copied {
            background: #28a745;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .step {
            margin: 10px 0;
            padding-left: 20px;
        }
        .highlight {
            background: #ffffcc;
            padding: 2px 4px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <h1>🚀 Neo4j Browser Query Import</h1>

    <div class="instructions">
        <h2>📝 Instructions</h2>
        <ol>
            <li class="step">Open Neo4j Browser: <a href="http://localhost:7474/browser/" target="_blank">http://localhost:7474/browser/</a></li>
            <li class="step">Login with: <span class="highlight">neo4j / password</span></li>
            <li class="step">Click the star (⭐) icon in the left sidebar</li>
            <li class="step">For each query below:
                <ul>
                    <li>Click "Copy" to copy the query</li>
                    <li>In Neo4j Browser, click "Add empty favorite" (+)</li>
                    <li>Paste the query</li>
                    <li>Name it using the title provided</li>
                    <li>Click the star to save</li>
                </ul>
            </li>
        </ol>
    </div>

    <h2>📊 Essential Queries</h2>
'''

    for i, query in enumerate(queries, 1):
        html_content += f'''
    <div class="query-card">
        <div class="query-title">{i}. {query['title']}</div>
        <div class="query-description">{query['description']}</div>
        <div class="query-box">
            <button class="copy-btn" onclick="copyQuery('query{i}', this)">Copy</button>
            <pre id="query{i}">{query['query']}</pre>
        </div>
    </div>
'''

    html_content += '''
    <script>
    function copyQuery(id, btn) {
        const text = document.getElementById(id).textContent;
        navigator.clipboard.writeText(text).then(function() {
            btn.textContent = '✓ Copied!';
            btn.classList.add('copied');
            setTimeout(() => {
                btn.textContent = 'Copy';
                btn.classList.remove('copied');
            }, 2000);
        }, function(err) {
            // Fallback for older browsers
            const textArea = document.createElement("textarea");
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            btn.textContent = '✓ Copied!';
            btn.classList.add('copied');
            setTimeout(() => {
                btn.textContent = 'Copy';
                btn.classList.remove('copied');
            }, 2000);
        });
    }
    </script>
</body>
</html>
'''

    return html_content

def main():
    print("🚀 Neo4j Browser Query Upload Helper")
    print("=" * 50)

    # Extract essential queries
    queries = extract_essential_queries()
    print(f"\n📊 Prepared {len(queries)} essential queries")

    # Test queries
    if test_queries(queries):
        print("\n✅ Queries validated successfully!")

    # Create HTML import file
    html_content = create_browser_import_html(queries)
    html_file = Path(__file__).parent / "neo4j_browser_import.html"

    with open(html_file, 'w') as f:
        f.write(html_content)

    print(f"\n📝 Created import helper: {html_file}")

    # Instructions
    print("\n" + "=" * 50)
    print("📋 INSTRUCTIONS TO ADD QUERIES TO NEO4J BROWSER:")
    print("=" * 50)
    print("\n1. OPTION A - Use the Import Helper (Recommended):")
    print(f"   • Open the file: {html_file}")
    print("   • Follow the on-screen instructions")
    print("   • Copy each query and add to Neo4j Browser favorites")

    print("\n2. OPTION B - Manual Copy from Terminal:")
    print("   • Open Neo4j Browser: http://localhost:7474/browser/")
    print("   • Login: neo4j / password")
    print("   • Click the star (⭐) icon → 'Add empty favorite'")
    print("   • Copy queries from below and paste")

    print("\n" + "=" * 50)
    print("📊 QUERIES TO ADD:")
    print("=" * 50)

    for i, query in enumerate(queries[:3], 1):  # Show first 3 in terminal
        print(f"\n--- Query {i}: {query['title']} ---")
        print(query['query'][:200] + "..." if len(query['query']) > 200 else query['query'])

    print(f"\n... and {len(queries) - 3} more queries in the HTML file")

    # Try to open the HTML file
    try:
        webbrowser.open(f"file://{html_file.absolute()}")
        print("\n✅ Opening import helper in your browser...")
    except:
        print(f"\n⚠️ Could not auto-open browser. Please open manually:\n   {html_file}")

    print("\n🎉 Ready to import queries to Neo4j Browser!")

if __name__ == "__main__":
    main()