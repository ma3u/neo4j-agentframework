
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
