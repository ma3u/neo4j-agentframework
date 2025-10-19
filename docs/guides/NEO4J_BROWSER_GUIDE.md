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

Start with the Dashboard Overview to see your current statistics!# 🚀 Neo4j Browser Query Import Guide

## Quick Start

Run this command to import pre-built queries into your Neo4j Browser:

```bash
python scripts/upload_queries_to_browser.py
```

This will:
1. ✅ Test all queries with your database
2. 📝 Create an HTML import helper file
3. 🌐 Open it in your browser automatically

## Step-by-Step Instructions

### Step 1: Run the Import Helper
```bash
cd neo4j-rag-demo
source venv/bin/activate
python scripts/upload_queries_to_browser.py
```

### Step 2: Use the HTML Import Page
The script creates `neo4j_browser_import.html` and opens it automatically.

You'll see a page with:
- 📋 Clear instructions at the top
- 📊 10 essential queries with descriptions
- 🔘 Copy buttons for each query

### Step 3: Add Queries to Neo4j Browser

1. **Open Neo4j Browser**: http://localhost:7474/browser/
2. **Login**: neo4j / password
3. **Click the star icon (⭐)** in the left sidebar to open Favorites
4. **For each query you want to add:**
   - Click "Copy" button in the HTML page
   - In Neo4j Browser, click "+ Add empty favorite"
   - Paste the query (Ctrl/Cmd + V)
   - Give it a name (use the title from the HTML page)
   - Click the star to save

## 📊 Available Queries

The import helper includes these 10 essential queries:

### 1. 📊 Dashboard Overview
Complete system statistics showing documents, chunks, embeddings, and coverage.

### 2. 📄 PDF Document List
All PDF documents with chunk counts, sizes, and upload dates.

### 3. 🏷️ Topic Analysis
Distribution of knowledge topics across your content.

### 4. 🔍 Content Search
Search for specific terms in your knowledge base.

### 5. 👥 Publisher Analysis
Breakdown of content sources and publishers.

### 6. 🎨 Graph Visualization
Document-chunk relationships for graph view.

### 7. ✅ Data Quality Check
Verify data integrity and identify issues.

### 8. 📏 Chunk Size Distribution
Analyze the distribution of chunk sizes.

### 9. 🔗 Cross-Document Knowledge
Find shared concepts between documents.

### 10. 📊 Quick Stats
Simple count of documents and chunks.

## Tips

### Using the Queries

**To run a query:**
1. Click on the query name in your favorites
2. The query will load in the editor
3. Click the play button (▶️) or press Ctrl/Cmd + Enter

**To modify search terms:**
- Look for comments like `// Change 'Neo4j' to your search term`
- Replace the term with what you want to search for
- Run the query again

**To view as graph:**
- Run a visualization query (like #6)
- Click the graph icon in the results panel
- Drag nodes to arrange the visualization

### Customization

You can modify queries after adding them:
1. Click the query in favorites to load it
2. Edit the query in the editor
3. Click the star to update the saved version

### Adding More Queries

The full collection of 50+ queries is in `scripts/neo4j_content_analysis.cypher`.
You can manually add any of these using the same process.

## Troubleshooting

**Queries return no results:**
- Check if you have data loaded: `python scripts/quick_test.py`
- Verify Neo4j is running: `docker ps | grep neo4j`

**Can't connect to Neo4j:**
- Ensure Docker is running
- Check Neo4j logs: `docker logs neo4j-rag`
- Verify credentials: neo4j / password

**Browser doesn't open automatically:**
- Manually open: `scripts/neo4j_browser_import.html`
- Or copy queries from the terminal output

## 🎉 Success!

Once you've imported the queries, you can:
- 📊 Monitor your knowledge base with Dashboard Overview
- 🔍 Search your content with Content Search
- 📈 Analyze topics and publishers
- 🎨 Visualize relationships in graph view
- ✅ Check data quality regularly

Happy exploring! 🚀