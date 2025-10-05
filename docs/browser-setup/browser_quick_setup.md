# 🚀 Quick Neo4j Browser Setup

## Step 1: Access Neo4j Browser
**URL**: http://localhost:7474/browser/
**Login**: neo4j / password

## Step 2: Essential Queries to Add as Favorites

### 📊 1. DASHBOARD OVERVIEW (Add First!)
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

### 📄 2. PDF INVENTORY
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

### 🏷️ 3. TOPIC ANALYSIS
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

### 🔍 4. CONTENT SEARCH
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

### 🎨 5. GRAPH VISUALIZATION
```cypher
// 🎨 Document-Category Network (Best in Graph View)
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf'
WITH d.category as category, COUNT(d) as doc_count, COLLECT(d) as docs
WHERE doc_count > 0
UNWIND docs as doc
MATCH (doc)-[:HAS_CHUNK]->(c:Chunk)
WITH category, doc, COUNT(c) as chunks
WHERE chunks > 100
RETURN category, doc, chunks
LIMIT 50;
```

## Step 3: How to Add Favorites

1. **Click the Star (⭐) icon** in left sidebar → "Favorites"
2. **Click "+ Add empty favorite"**
3. **Copy and paste** one of the queries above
4. **Name your favorite** (e.g., "📊 Dashboard Overview")
5. **Click the star** to save
6. **Repeat** for each query

## Step 4: Run Your First Analysis

1. **Start with Dashboard Overview** - gives you system statistics
2. **Run PDF Inventory** - see all your uploaded documents
3. **Try Topic Analysis** - understand your content themes
4. **Use Content Search** - find specific information
5. **View Graph Visualization** - see relationships in graph mode

## 💡 Pro Tips

- **Switch to Graph View**: Click the graph icon after running visualization queries
- **Export Results**: Click download icon to save as CSV
- **Use Parameters**: Set `:param searchTerm => 'your term'` for flexible searches
- **Save Often**: Add useful queries as favorites for quick access

## 🎯 Expected Results

Based on your current database:
- **24+ Documents** (mix of PDFs and tutorials)
- **10,000+ Chunks** with full embedding coverage
- **Rich content** about Neo4j, RAG, graph databases, and vector systems
- **Multiple publishers**: O'Reilly, Manning, arXiv, Neo4j official docs

Start with the Dashboard Overview to see your current statistics!