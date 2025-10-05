# 🚀 Neo4j Browser Query Import Guide

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