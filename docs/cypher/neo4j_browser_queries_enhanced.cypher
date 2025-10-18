// ============================================
// Neo4j RAG System - Enhanced Browser Queries
// ============================================
// Save these as favorites in Neo4j Browser
// Each query is standalone and can be run independently

// ============================================
// QUICK STATS - Run this first!
// ============================================

// 📊 Database Overview
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH COUNT(DISTINCT d) as docs, COUNT(c) as chunks
MATCH (c2:Chunk) WHERE c2.embedding IS NOT NULL
RETURN
    docs as `Total Documents`,
    chunks as `Total Chunks`,
    COUNT(c2) as `Chunks with Embeddings`,
    ROUND(toFloat(COUNT(c2)) / toFloat(chunks) * 100, 1) + '%' as `Embedding Coverage`;

// ============================================
// PDF ANALYSIS
// ============================================

// 📄 List All PDF Documents with Stats
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf' OR d.category = 'pdf' OR d.category = 'test'
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count
RETURN
    CASE
        WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1]
        ELSE d.source
    END as PDF,
    d.category as Category,
    chunk_count as Chunks,
    CASE
        WHEN SIZE(d.content) > 1000000 THEN toString(ROUND(toFloat(SIZE(d.content)) / 1000000, 1)) + ' MB'
        WHEN SIZE(d.content) > 1000 THEN toString(ROUND(toFloat(SIZE(d.content)) / 1000, 1)) + ' KB'
        ELSE toString(SIZE(d.content)) + ' bytes'
    END as Size,
    substring(toString(d.created), 0, 19) as Uploaded
ORDER BY chunk_count DESC;

// ============================================
// SEARCH EXAMPLES
// ============================================

// 🔍 Semantic Search - Find chunks about "graph databases"
// Change the search term in the WHERE clause
MATCH (c:Chunk)
WHERE c.text CONTAINS 'graph' AND c.text CONTAINS 'database'
RETURN
    c.chunk_index as ChunkID,
    substring(c.text, 0, 200) + '...' as Content,
    CASE
        WHEN exists((d:Document)-[:HAS_CHUNK]->(c))
        THEN [(d:Document)-[:HAS_CHUNK]->(c) | split(d.source, '/')[-1]][0]
        ELSE 'Unknown'
    END as Source
LIMIT 10;

// 🔍 Search with Context - Get surrounding chunks
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE c.text CONTAINS 'RAG' OR c.text CONTAINS 'retrieval'
WITH d, c
ORDER BY d.source, c.chunk_index
WITH d, COLLECT({index: c.chunk_index, text: substring(c.text, 0, 100)}) as chunks
RETURN
    split(d.source, '/')[-1] as Document,
    d.category as Category,
    SIZE(chunks) as MatchingChunks,
    chunks[0..3] as FirstThreeMatches
LIMIT 5;

// ============================================
// KNOWLEDGE GRAPH EXPLORATION
// ============================================

// 📊 Category Distribution
MATCH (d:Document)
RETURN
    COALESCE(d.category, 'Uncategorized') as Category,
    COUNT(d) as Documents,
    SUM(SIZE((d)-[:HAS_CHUNK]->())) as TotalChunks
ORDER BY Documents DESC;

// 📈 Document Complexity Analysis
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunks, AVG(SIZE(c.text)) as avg_chunk_size
RETURN
    split(d.source, '/')[-1] as Document,
    chunks as Chunks,
    ROUND(avg_chunk_size) as `Avg Chunk Size`,
    CASE
        WHEN chunks > 500 THEN 'Very Complex'
        WHEN chunks > 200 THEN 'Complex'
        WHEN chunks > 50 THEN 'Moderate'
        ELSE 'Simple'
    END as Complexity
ORDER BY chunks DESC
LIMIT 20;

// ============================================
// VISUALIZATION QUERIES
// ============================================

// 🎨 Graph Visualization - Document-Chunk Relationships
// Best viewed in Graph mode
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE d.category IN ['tutorial', 'pdf', 'test', 'knowledge_graph']
WITH d, COLLECT(c)[0..5] as sample_chunks
UNWIND sample_chunks as chunk
RETURN d, chunk
LIMIT 100;

// 🎨 Category Network
// Shows how documents are distributed across categories
MATCH (d:Document)
WITH d.category as category, COLLECT(d) as docs
WHERE SIZE(docs) > 1
UNWIND docs as doc
MATCH (doc)-[:HAS_CHUNK]->(c:Chunk)
WITH category, doc, COUNT(c) as weight
RETURN category, doc, weight
LIMIT 50;

// ============================================
// DATA QUALITY CHECKS
// ============================================

// ✅ Data Integrity Check
MATCH (c:Chunk)
WHERE NOT (c)<-[:HAS_CHUNK]-()
WITH COUNT(c) as orphaned_chunks
MATCH (d:Document)
WHERE NOT (d)-[:HAS_CHUNK]->()
WITH orphaned_chunks, COUNT(d) as docs_without_chunks
MATCH (c2:Chunk)
WHERE c2.embedding IS NULL
RETURN
    orphaned_chunks as `Orphaned Chunks`,
    docs_without_chunks as `Documents without Chunks`,
    COUNT(c2) as `Chunks without Embeddings`,
    CASE
        WHEN orphaned_chunks = 0 AND docs_without_chunks = 0 AND COUNT(c2) = 0
        THEN '✅ All Good!'
        ELSE '⚠️ Issues Found'
    END as Status;

// 📏 Chunk Size Analysis
MATCH (c:Chunk)
WITH SIZE(c.text) as size
RETURN
    CASE
        WHEN size < 100 THEN '0-100'
        WHEN size < 200 THEN '100-200'
        WHEN size < 300 THEN '200-300'
        WHEN size < 400 THEN '300-400'
        WHEN size < 500 THEN '400-500'
        ELSE '500+'
    END as `Size Range`,
    COUNT(*) as Count
ORDER BY `Size Range`;

// ============================================
// RECENT ACTIVITY
// ============================================

// 📅 Recently Added Documents
MATCH (d:Document)
WHERE d.created IS NOT NULL
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunks
RETURN
    split(d.source, '/')[-1] as Document,
    d.category as Category,
    chunks as Chunks,
    substring(toString(d.created), 0, 19) as Created
ORDER BY d.created DESC
LIMIT 10;

// ============================================
// PERFORMANCE ANALYSIS
// ============================================

// ⚡ Large Documents Analysis
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count
WHERE chunk_count > 100
RETURN
    split(d.source, '/')[-1] as Document,
    chunk_count as Chunks,
    ROUND(toFloat(SIZE(d.content)) / 1000) as `Size (KB)`,
    ROUND(toFloat(chunk_count) * 384 * 4 / 1000) as `Est. Embedding Storage (KB)`
ORDER BY chunk_count DESC;

// ============================================
// ADVANCED SEARCH QUERIES
// ============================================

// 🔍 Find Similar Documents (by shared vocabulary)
MATCH (d1:Document)-[:HAS_CHUNK]->(c1:Chunk)
WHERE d1.source CONTAINS 'kg-tour'  // Change this to your document
WITH d1, COLLECT(DISTINCT c1.text) as texts1
MATCH (d2:Document)-[:HAS_CHUNK]->(c2:Chunk)
WHERE d2 <> d1
WITH d1, texts1, d2, COLLECT(DISTINCT c2.text) as texts2
WITH d1, d2,
     [text IN texts1 WHERE text IN texts2] as common_texts
WHERE SIZE(common_texts) > 0
RETURN
    split(d1.source, '/')[-1] as Document1,
    split(d2.source, '/')[-1] as Document2,
    SIZE(common_texts) as `Shared Chunks`
ORDER BY `Shared Chunks` DESC
LIMIT 10;

// 🔍 Knowledge Coverage Analysis
MATCH (c:Chunk)
WITH COLLECT(DISTINCT
    CASE
        WHEN c.text CONTAINS 'Neo4j' THEN 'Neo4j'
        WHEN c.text CONTAINS 'graph' THEN 'Graph Theory'
        WHEN c.text CONTAINS 'RAG' OR c.text CONTAINS 'retrieval' THEN 'RAG/Retrieval'
        WHEN c.text CONTAINS 'vector' OR c.text CONTAINS 'embedding' THEN 'Vector/Embeddings'
        WHEN c.text CONTAINS 'machine learning' OR c.text CONTAINS 'ML' THEN 'Machine Learning'
        WHEN c.text CONTAINS 'knowledge graph' THEN 'Knowledge Graphs'
        ELSE NULL
    END
) as topics
UNWIND topics as topic
WITH topic
WHERE topic IS NOT NULL
MATCH (c2:Chunk)
WHERE (topic = 'Neo4j' AND c2.text CONTAINS 'Neo4j') OR
      (topic = 'Graph Theory' AND c2.text CONTAINS 'graph') OR
      (topic = 'RAG/Retrieval' AND (c2.text CONTAINS 'RAG' OR c2.text CONTAINS 'retrieval')) OR
      (topic = 'Vector/Embeddings' AND (c2.text CONTAINS 'vector' OR c2.text CONTAINS 'embedding')) OR
      (topic = 'Machine Learning' AND (c2.text CONTAINS 'machine learning' OR c2.text CONTAINS 'ML')) OR
      (topic = 'Knowledge Graphs' AND c2.text CONTAINS 'knowledge graph')
RETURN
    topic as Topic,
    COUNT(DISTINCT c2) as `Chunk Count`,
    COUNT(DISTINCT [(d:Document)-[:HAS_CHUNK]->(c2) | d]) as `Document Count`
ORDER BY `Chunk Count` DESC;

// ============================================
// USEFUL UTILITIES
// ============================================

// 🗑️ Clear Test Data (BE CAREFUL!)
// Uncomment to run
// MATCH (d:Document {category: 'test'})
// DETACH DELETE d;

// 📊 Export Document List
MATCH (d:Document)
RETURN
    d.id as ID,
    split(d.source, '/')[-1] as Filename,
    d.category as Category,
    SIZE((d)-[:HAS_CHUNK]->()) as Chunks,
    substring(toString(d.created), 0, 10) as Date
ORDER BY d.created DESC;

// 🔧 Check Index Status
SHOW INDEXES
YIELD name, type, state, labelsOrTypes, properties
RETURN name, type, state, labelsOrTypes, properties;

// ============================================
// SAMPLE DATA EXPLORATION
// ============================================

// 📖 Read Sample Content
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE d.category = 'tutorial' OR d.source CONTAINS '.pdf'
WITH d, c
ORDER BY d.source, c.chunk_index
LIMIT 5
RETURN
    split(d.source, '/')[-1] as Document,
    c.chunk_index as Index,
    substring(c.text, 0, 300) as Content;

// 🔗 Find Cross-References
// Find chunks that mention multiple key concepts
MATCH (c:Chunk)
WHERE c.text CONTAINS 'Neo4j' AND
      c.text CONTAINS 'RAG' AND
      c.text CONTAINS 'vector'
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
RETURN
    split(d.source, '/')[-1] as Document,
    c.chunk_index as Chunk,
    substring(c.text, 0, 200) + '...' as Content
LIMIT 10;