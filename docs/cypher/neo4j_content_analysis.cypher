// ============================================
// NEO4J RAG CONTENT ANALYSIS QUERIES
// Copy these into Neo4j Browser as Favorites
// ============================================

// ============================================
// 1. DASHBOARD OVERVIEW - RUN THIS FIRST!
// ============================================

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

// ============================================
// 2. PDF DOCUMENT INVENTORY
// ============================================

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

// ============================================
// 3. CONTENT TOPIC ANALYSIS
// ============================================

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

// ============================================
// 4. AUTHOR & SOURCE ANALYSIS
// ============================================

// 👥 Content Sources and Publishers
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf'
WITH d.source as source, d
WITH
    CASE
        WHEN source CONTAINS 'oreilly' OR source CONTAINS 'OReilly' THEN 'O\'Reilly Media'
        WHEN source CONTAINS 'manning' OR source CONTAINS 'Manning' THEN 'Manning Publications'
        WHEN source CONTAINS 'arxiv' OR source CONTAINS '2312.' OR source CONTAINS '2309.' THEN 'arXiv Papers'
        WHEN source CONTAINS 'neo4j' OR source CONTAINS 'Neo4j' THEN 'Neo4j Official'
        WHEN source CONTAINS 'Beginning' OR source CONTAINS 'beginning' THEN 'Apress'
        WHEN source CONTAINS 'appliedai' OR source CONTAINS 'AppliedAI' THEN 'AppliedAI'
        WHEN source CONTAINS 'graph-database-use-cases' THEN 'Oracle'
        WHEN source CONTAINS 'kg-tour' OR source CONTAINS 'ldmgmt' THEN 'Academic Papers'
        WHEN source CONTAINS 'cookbook' THEN 'Digital Financial Reporting'
        ELSE 'Other Publishers'
    END as publisher, d
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    publisher as `📚 Publisher/Source`,
    COUNT(DISTINCT d) as `📖 Documents`,
    COUNT(c) as `📝 Total Chunks`,
    ROUND(AVG(toFloat(SIZE(d.content))) / 1000, 1) + ' KB' as `📊 Avg Doc Size`
ORDER BY `📖 Documents` DESC;

// ============================================
// 5. SEARCH KEYWORD ANALYSIS
// ============================================

// 🔍 Most Common Technical Terms
MATCH (c:Chunk)
WITH c.text as text
UNWIND [
    'Neo4j', 'graph', 'database', 'vector', 'embedding', 'RAG', 'retrieval',
    'Cypher', 'node', 'relationship', 'knowledge', 'algorithm', 'performance',
    'query', 'search', 'machine learning', 'neural', 'data', 'model'
] as keyword
WITH keyword,
     COUNT(CASE WHEN apoc.text.toLowerCase(text) CONTAINS apoc.text.toLowerCase(keyword) THEN 1 END) as mentions
WHERE mentions > 0
RETURN
    keyword as `🔤 Technical Term`,
    mentions as `📊 Mentions`,
    ROUND(toFloat(mentions) / 10434 * 100, 2) + '%' as `📈 Coverage`
ORDER BY mentions DESC
LIMIT 15;

// ============================================
// 6. CONTENT VISUALIZATION NETWORK
// ============================================

// 🎨 Document-Category Network (For Graph View)
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf'
WITH d.category as category, COUNT(d) as doc_count, COLLECT(d) as docs
WHERE doc_count > 0
UNWIND docs as doc
MATCH (doc)-[:HAS_CHUNK]->(c:Chunk)
WITH category, doc, COUNT(c) as chunks
WHERE chunks > 100  // Only show substantial documents
RETURN category, doc, chunks
LIMIT 50;

// ============================================
// 7. CONTENT QUALITY METRICS
// ============================================

// ✅ Data Quality Assessment
MATCH (c:Chunk)
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
         ELSE '⚠️ Check Quality' END as `🎯 Status`;

// ============================================
// 8. SEARCH PERFORMANCE TEST
// ============================================

// 🔍 Sample Content Search - Try Different Terms
// Change the search term below
MATCH (c:Chunk)
WHERE apoc.text.toLowerCase(c.text) CONTAINS 'neo4j'  // <-- Change this term
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

// ============================================
// 9. CHUNK SIZE DISTRIBUTION
// ============================================

// 📏 Content Chunk Analysis
MATCH (c:Chunk)
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
ORDER BY `📐 Size Category`;

// ============================================
// 10. RECENT ACTIVITY TIMELINE
// ============================================

// 📅 Upload Timeline
MATCH (d:Document)
WHERE d.created IS NOT NULL AND d.source CONTAINS '.pdf'
WITH d, date(d.created) as upload_date
WITH upload_date, COUNT(d) as docs_uploaded,
     COLLECT(CASE WHEN d.source CONTAINS '/'
                  THEN split(d.source, '/')[-1]
                  ELSE d.source END)[0..3] as sample_files
RETURN
    toString(upload_date) as `📅 Upload Date`,
    docs_uploaded as `📚 Documents`,
    sample_files as `📄 Sample Files`
ORDER BY upload_date DESC;

// ============================================
// 11. ADVANCED CONTENT DISCOVERY
// ============================================

// 🕵️ Cross-Document Knowledge Connections
MATCH (d1:Document)-[:HAS_CHUNK]->(c1:Chunk)
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
WITH concept, COUNT(DISTINCT d1) as doc_count, COLLECT(DISTINCT d1.source) as sources
WHERE doc_count > 1
RETURN
    concept as `🧠 Shared Concept`,
    doc_count as `📚 Document Count`,
    [s IN sources | CASE WHEN s CONTAINS '/' THEN split(s, '/')[-1] ELSE s END][0..5] as `📖 Sample Documents`
ORDER BY doc_count DESC;

// ============================================
// 12. PERFORMANCE MONITORING
// ============================================

// ⚡ Database Performance Metrics
CALL db.stats.retrieve('GRAPH COUNTS') YIELD data
WITH data.nodes as node_count, data.relationships as rel_count
CALL dbms.queryJmx('java.lang:type=Memory') YIELD attributes
WITH node_count, rel_count, attributes.HeapMemoryUsage.used as heap_used,
     attributes.HeapMemoryUsage.max as heap_max
RETURN
    node_count as `🔵 Total Nodes`,
    rel_count as `🔗 Total Relationships`,
    ROUND(toFloat(heap_used) / 1000000) + ' MB' as `💾 Heap Used`,
    ROUND(toFloat(heap_max) / 1000000) + ' MB' as `💾 Heap Max`,
    ROUND(toFloat(heap_used) / heap_max * 100, 1) + '%' as `📊 Memory Usage`;

// ============================================
// BONUS: Quick Search Template
// ============================================

// 🔍 QUICK SEARCH TEMPLATE - Modify the search term
// Replace 'your-search-term' with what you want to find
:param searchTerm => 'graph database'

MATCH (c:Chunk)
WHERE apoc.text.toLowerCase(c.text) CONTAINS toLower($searchTerm)
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
RETURN
    CASE WHEN d.source CONTAINS '/'
         THEN split(d.source, '/')[-1]
         ELSE d.source END as Document,
    c.chunk_index as ChunkID,
    substring(c.text, 0, 300) + '...' as Content
LIMIT 10;