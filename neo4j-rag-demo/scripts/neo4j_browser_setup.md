# Neo4j Browser Setup Guide

## 🚀 Quick Setup for Neo4j Browser

### Access Neo4j Browser
Open in your web browser: **http://localhost:7474/browser/**

### Login Credentials
- **Username**: neo4j
- **Password**: password

## 📝 Adding Queries as Local Scripts (Favorites)

### Method 1: Manual Copy-Paste

1. **Open the Favorites Panel**
   - Click the star (⭐) icon in the left sidebar
   - You'll see "Favorites" and "Sample Scripts"

2. **Add a New Favorite**
   - Click "+ Add empty favorite" or the plus (+) button
   - Copy a query from `neo4j_browser_queries_enhanced.cypher`
   - Paste it into the editor
   - Give it a descriptive name
   - Click the star to save

3. **Organize Your Favorites**
   - Create these categories as separate favorites:
     - 📊 Quick Stats
     - 📄 PDF Analysis
     - 🔍 Search Queries
     - 🎨 Visualizations
     - ✅ Data Quality
     - 📈 Performance

### Method 2: Bulk Import (Recommended)

Run this in Neo4j Browser to see instructions:

```cypher
// Show current database stats first
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    COUNT(DISTINCT d) as Documents,
    COUNT(c) as Chunks,
    COUNT(DISTINCT CASE WHEN d.source CONTAINS '.pdf' THEN d END) as PDFs;
```

## 🎯 Essential Queries to Save

### 1. **Dashboard Overview** (Run First!)
```cypher
// 📊 Complete Database Statistics
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH COUNT(DISTINCT d) as docs, COUNT(c) as chunks
MATCH (c2:Chunk) WHERE c2.embedding IS NOT NULL
RETURN
    docs as `Total Documents`,
    chunks as `Total Chunks`,
    COUNT(c2) as `Chunks with Embeddings`,
    ROUND(toFloat(COUNT(c2)) / toFloat(chunks) * 100, 1) + '%' as `Coverage`;
```

### 2. **PDF Document List**
```cypher
// 📄 All PDFs with Statistics
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf' OR d.category = 'pdf'
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunks
RETURN
    split(d.source, '/')[-1] as PDF,
    d.category as Category,
    chunks as Chunks,
    substring(toString(d.created), 0, 19) as Uploaded
ORDER BY chunks DESC;
```

### 3. **Search for Content**
```cypher
// 🔍 Find chunks about a topic
// Change 'Neo4j' to your search term
MATCH (c:Chunk)
WHERE c.text CONTAINS 'Neo4j'
RETURN
    c.chunk_index as ID,
    substring(c.text, 0, 200) + '...' as Content
LIMIT 20;
```

### 4. **Visualize Graph** (Best for Graph View)
```cypher
// 🎨 Document-Chunk Relationships
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE d.category IN ['tutorial', 'pdf', 'test']
WITH d, COLLECT(c)[0..3] as sample_chunks
UNWIND sample_chunks as chunk
RETURN d, chunk
LIMIT 50;
```

### 5. **Knowledge Coverage**
```cypher
// 📚 Topic Distribution
MATCH (c:Chunk)
RETURN
    CASE
        WHEN c.text CONTAINS 'Neo4j' THEN 'Neo4j'
        WHEN c.text CONTAINS 'RAG' THEN 'RAG/Retrieval'
        WHEN c.text CONTAINS 'vector' THEN 'Vectors'
        WHEN c.text CONTAINS 'graph' THEN 'Graphs'
        ELSE 'Other'
    END as Topic,
    COUNT(*) as Chunks
ORDER BY Chunks DESC;
```

## 🎨 Using Graph Visualization

1. **Switch to Graph View**
   - After running a query that returns nodes/relationships
   - Click the graph icon in the result panel
   - Nodes will appear as circles, relationships as lines

2. **Interact with the Graph**
   - Click and drag nodes to rearrange
   - Double-click a node to expand relationships
   - Use mouse wheel to zoom in/out
   - Click a node/relationship to see properties

3. **Customize Appearance**
   - Click the paintbrush icon
   - Set colors by category or label
   - Adjust node sizes based on properties

## 💡 Pro Tips

### Keyboard Shortcuts
- **Ctrl/Cmd + Enter**: Run query
- **Ctrl/Cmd + Up**: Previous query in history
- **Ctrl/Cmd + Down**: Next query in history
- **Esc**: Clear editor

### Query Parameters
Replace hardcoded values with parameters:
```cypher
// Use parameters for flexible queries
:param searchTerm => "Neo4j"
MATCH (c:Chunk)
WHERE c.text CONTAINS $searchTerm
RETURN c.text LIMIT 10;
```

### Multi-Statement Queries
Separate multiple queries with semicolons:
```cypher
// Run multiple queries at once
MATCH (d:Document) RETURN COUNT(d) as Documents;
MATCH (c:Chunk) RETURN COUNT(c) as Chunks;
```

### Export Results
- **Table View**: Click download icon to export as CSV
- **Graph View**: Right-click → Export as PNG/SVG
- **JSON Export**: Use `RETURN ... AS json`

## 🔧 Useful Browser Commands

Type these in the query editor:

- `:help` - Show help documentation
- `:play` - Interactive tutorials
- `:server status` - Database information
- `:schema` - Show database schema
- `:sysinfo` - System information
- `:queries` - List running queries
- `:clear` - Clear result frames
- `:style` - Edit graph styling

## 📊 Monitor Performance

```cypher
// Check query performance
PROFILE
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE c.text CONTAINS 'search term'
RETURN d.source, COUNT(c) as matches;
```

The `PROFILE` prefix shows:
- Execution plan
- DB hits
- Rows processed
- Memory usage

## 🚨 Troubleshooting

### Connection Issues
- Verify Neo4j is running: `docker ps | grep neo4j`
- Check logs: `docker logs neo4j-rag`
- Restart if needed: `docker restart neo4j-rag`

### Slow Queries
- Add indexes for frequently searched properties
- Use `LIMIT` to reduce result size
- Profile queries to find bottlenecks

### Memory Issues
- Increase heap size in Neo4j config
- Use pagination for large results
- Clear query result frames regularly

## 📚 Additional Resources

- [Neo4j Browser User Guide](https://neo4j.com/docs/browser-manual/current/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [Graph Visualization Best Practices](https://neo4j.com/developer/graph-visualization/)