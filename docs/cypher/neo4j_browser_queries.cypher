// Neo4j RAG System - Browser Queries
// Save this file in Neo4j Browser as a local script
// Each query can be run independently

// ============================================
// 📊 STATISTICS QUERIES
// ============================================

// Overall Statistics
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    COUNT(DISTINCT d) as total_documents,
    COUNT(c) as total_chunks,
    AVG(SIZE(d.content)) as avg_doc_size,
    MIN(SIZE(d.content)) as min_doc_size,
    MAX(SIZE(d.content)) as max_doc_size,
    SUM(SIZE(d.content)) as total_content_size;

// Document Category Distribution
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    COALESCE(d.category, 'Uncategorized') as category,
    COUNT(DISTINCT d) as doc_count,
    COUNT(c) as chunk_count,
    AVG(SIZE(d.content)) as avg_size
ORDER BY doc_count DESC;

// PDF Documents Analysis
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf' OR d.category = 'pdf'
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    d.source as source,
    d.category as category,
    COUNT(c) as chunk_count,
    SIZE(d.content) as doc_size,
    d.created as created
ORDER BY chunk_count DESC;

// Recent Documents (Last 10)
MATCH (d:Document)
WHERE d.created IS NOT NULL
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    d.source as source,
    d.created as created,
    d.category as category,
    COUNT(c) as chunks,
    SIZE(d.content) as size
ORDER BY d.created DESC
LIMIT 10;

// ============================================
// 🔍 SEARCH QUERIES
// ============================================

// Find Chunks by Keyword
MATCH (c:Chunk)
WHERE c.text CONTAINS 'vector' // Change keyword here
RETURN c.text, c.chunk_index
LIMIT 10;

// Find Documents by Category
MATCH (d:Document {category: 'tutorial'}) // Change category here
RETURN d.source, d.created, SIZE(d.content) as size
LIMIT 10;

// Document with Most Chunks
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count
ORDER BY chunk_count DESC
LIMIT 5
RETURN d.source, d.category, chunk_count;

// ============================================
// 📈 GRAPH STRUCTURE QUERIES
// ============================================

// Graph Overview - Node and Relationship Counts
CALL db.labels() YIELD label
RETURN label as NodeType,
       size([(n) WHERE label IN labels(n) | n]) as Count
ORDER BY Count DESC;

// Document-Chunk Connections
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count, COLLECT(c.chunk_index) as indices
RETURN
    d.source as source,
    d.category as category,
    chunk_count,
    indices[0..5] as sample_indices
ORDER BY chunk_count DESC
LIMIT 10;

// Connected Components Analysis
MATCH (d:Document)
WITH COUNT(DISTINCT d) as total_documents
MATCH (d2:Document)
WHERE NOT (d2)-[:HAS_CHUNK]->()
WITH total_documents, COUNT(d2) as isolated_documents
RETURN
    total_documents,
    isolated_documents,
    total_documents - isolated_documents as connected_documents;

// Average Chunks per Document
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as degree
RETURN
    AVG(degree) as avg_chunks_per_doc,
    MIN(degree) as min_chunks,
    MAX(degree) as max_chunks;

// ============================================
// 🧮 EMBEDDING ANALYSIS
// ============================================

// Embedding Coverage
MATCH (c:Chunk)
RETURN
    COUNT(c) as total_chunks,
    COUNT(c.embedding) as chunks_with_embedding,
    toFloat(COUNT(c.embedding)) / toFloat(COUNT(c)) * 100 as coverage_percentage;

// Chunk Size Distribution
MATCH (c:Chunk)
WITH c, SIZE(c.text) as size
RETURN
    CASE
        WHEN size < 100 THEN '0-100'
        WHEN size < 200 THEN '100-200'
        WHEN size < 300 THEN '200-300'
        WHEN size < 400 THEN '300-400'
        WHEN size < 500 THEN '400-500'
        ELSE '500+'
    END as size_range,
    COUNT(c) as count
ORDER BY size_range;

// Chunk Statistics
MATCH (c:Chunk)
RETURN
    MIN(SIZE(c.text)) as min_size,
    MAX(SIZE(c.text)) as max_size,
    AVG(SIZE(c.text)) as avg_size,
    percentileCont(SIZE(c.text), 0.5) as median_size,
    COUNT(c) as total_chunks;

// ============================================
// 🎨 VISUALIZATION QUERIES
// ============================================

// Visualize Document-Chunk Graph (Best for Neo4j Browser)
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COLLECT(c)[0..3] as sample_chunks
UNWIND sample_chunks as chunk
RETURN d, chunk
LIMIT 50;

// Category-Based Visualization
MATCH (d:Document {category: 'tutorial'})-[:HAS_CHUNK]->(c:Chunk)
RETURN d, c
LIMIT 30;

// High-Connectivity Documents
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunks
WHERE chunks > 10
MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN d, c;

// ============================================
// 🔧 DATA INTEGRITY CHECKS
// ============================================

// Find Orphaned Chunks
MATCH (c:Chunk)
WHERE NOT (c)<-[:HAS_CHUNK]-()
RETURN COUNT(c) as orphaned_chunks;

// Find Documents Without Chunks
MATCH (d:Document)
WHERE NOT (d)-[:HAS_CHUNK]->()
RETURN COUNT(d) as docs_without_chunks;

// Check for Duplicate Documents
MATCH (d:Document)
WITH d.content as content, COLLECT(d) as docs
WHERE SIZE(docs) > 1
RETURN SIZE(docs) as duplicate_count, docs[0].source as example_source;

// ============================================
// 💡 USEFUL UTILITY QUERIES
// ============================================

// Count All Nodes and Relationships
MATCH (n)
WITH COUNT(n) as node_count
MATCH ()-[r]->()
WITH node_count, COUNT(r) as relationship_count
RETURN node_count, relationship_count;

// Database Size Estimation
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH
    SUM(SIZE(d.content)) as total_doc_size,
    COUNT(c) as total_chunks,
    AVG(SIZE(c.text)) as avg_chunk_size
RETURN
    total_doc_size as total_document_bytes,
    total_chunks * avg_chunk_size as estimated_chunk_bytes,
    total_doc_size + (total_chunks * avg_chunk_size) as estimated_total_bytes;

// Find Specific Document
MATCH (d:Document)
WHERE d.source CONTAINS 'arxiv' // Change search term
RETURN d.source, d.category, d.created
LIMIT 10;

// Get Sample Chunk Text
MATCH (c:Chunk)
RETURN c.text
LIMIT 5;

// ============================================
// 🚀 ADVANCED QUERIES
// ============================================

// Chunk Context Window (Get chunk with neighbors)
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk {chunk_index: 0})
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(prev:Chunk {chunk_index: -1})
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(next:Chunk {chunk_index: 1})
RETURN
    prev.text as previous_chunk,
    c.text as current_chunk,
    next.text as next_chunk;

// Document Processing Timeline
MATCH (d:Document)
WHERE d.created IS NOT NULL
WITH date(d.created) as day, COUNT(d) as docs_created
RETURN day, docs_created
ORDER BY day;

// Category Cross-Reference
MATCH (d:Document)
WITH d.category as category, COUNT(d) as count
WHERE category IS NOT NULL
RETURN category, count
ORDER BY count DESC;