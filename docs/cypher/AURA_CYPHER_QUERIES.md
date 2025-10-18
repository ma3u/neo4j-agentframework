# Neo4j Aura Cypher Query Guide

**Instance**: `6b870b04` (ma3u)
**Database**: Neo4j 5.27-aura (enterprise)
**Content**: 12 books, 30,006 chunks, 100% embedded

Copy and paste these queries into your Neo4j Browser at: https://console.neo4j.io

---

## 📊 STATISTICS QUERIES

### 1. Overall System Statistics

**What it shows**: Total documents, chunks, and content size metrics

```cypher
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    COUNT(DISTINCT d) as total_documents,
    COUNT(c) as total_chunks,
    AVG(SIZE(d.content)) as avg_doc_size,
    MIN(SIZE(d.content)) as min_doc_size,
    MAX(SIZE(d.content)) as max_doc_size,
    SUM(SIZE(d.content)) as total_content_size;
```

**Expected**: 12 documents, 30,006 chunks, 25.9 GB total

---

### 2. Category Distribution

**What it shows**: How documents are distributed across categories

```cypher
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    COALESCE(d.category, 'Uncategorized') as category,
    COUNT(DISTINCT d) as doc_count,
    COUNT(c) as chunk_count,
    AVG(SIZE(d.content)) as avg_size
ORDER BY doc_count DESC;
```

**Expected**: 5 categories (neo4j, general, rag, knowledge_graph, vector_db)

---

### 3. Complete PDF Inventory

**What it shows**: All 12 PDFs with detailed metrics

```cypher
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf'
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count,
     CASE WHEN d.source CONTAINS '/'
          THEN split(d.source, '/')[-1]
          ELSE d.source END as filename
RETURN
    filename as pdf_document,
    COALESCE(d.category, 'uncategorized') as category,
    chunk_count as chunks,
    ROUND(SIZE(d.content) / 1000.0, 1) as size_kb,
    substring(toString(d.created), 0, 16) as uploaded
ORDER BY chunk_count DESC;
```

**Use**: See all books with chunk counts and upload dates

---

## 🔍 SEARCH & DISCOVERY QUERIES

### 4. Search for "Neo4j" Content

**What it does**: Find all chunks mentioning Neo4j with context

```cypher
MATCH (c:Chunk)
WHERE toLower(c.text) CONTAINS 'neo4j'
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
WITH c, d,
     CASE WHEN d.source CONTAINS '/'
          THEN split(d.source, '/')[-1]
          ELSE d.source END as filename
RETURN
    filename as source_document,
    c.chunk_index as chunk_id,
    substring(c.text, 0, 200) + '...' as content_preview
ORDER BY filename, c.chunk_index
LIMIT 20;
```

**Try**: Replace 'neo4j' with 'vector', 'rag', 'cypher', 'graph neural', etc.

---

### 5. Search for "Vector Embeddings"

**What it does**: Find content about vector embeddings

```cypher
MATCH (c:Chunk)
WHERE toLower(c.text) CONTAINS 'vector'
  AND (toLower(c.text) CONTAINS 'embedding' OR toLower(c.text) CONTAINS 'search')
OPTIONAL MATCH (d:Document)-[:HAS_CHUNK]->(c)
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    c.chunk_index as chunk_id,
    substring(c.text, 0, 250) + '...' as content
ORDER BY document, chunk_id
LIMIT 10;
```

**Use**: Find specific technical topics

---

### 6. Search by Document Category

**What it does**: Find all documents in a specific category

```cypher
MATCH (d:Document {category: 'neo4j'})  // Change to: rag, general, knowledge_graph, vector_db
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    COUNT(c) as chunks,
    ROUND(SIZE(d.content) / 1024.0, 1) as size_kb
ORDER BY chunks DESC;
```

**Try different categories**: neo4j, rag, general, knowledge_graph, vector_db

---

## 🧮 EMBEDDING & VECTOR ANALYSIS

### 7. Embedding Coverage Check

**What it shows**: Percentage of chunks with vector embeddings

```cypher
MATCH (c:Chunk)
RETURN
    COUNT(c) as total_chunks,
    COUNT(c.embedding) as chunks_with_embedding,
    toFloat(COUNT(c.embedding)) / toFloat(COUNT(c)) * 100 as coverage_percentage,
    SIZE(COLLECT(c.embedding)[0]) as embedding_dimensions;
```

**Expected**: 100% coverage, 384 dimensions

---

### 8. Chunk Size Distribution

**What it shows**: How chunk sizes are distributed

```cypher
MATCH (c:Chunk)
WITH c, SIZE(c.text) as size
RETURN
    CASE
        WHEN size < 100 THEN '📏 Tiny (0-100)'
        WHEN size < 200 THEN '📄 Small (100-200)'
        WHEN size < 300 THEN '📋 Medium (200-300)'
        WHEN size < 400 THEN '📊 Large (300-400)'
        WHEN size < 500 THEN '📚 X-Large (400-500)'
        ELSE '📖 Huge (500+)'
    END as size_category,
    COUNT(*) as chunk_count,
    ROUND(AVG(toFloat(size)), 0) as avg_size
ORDER BY size_category;
```

**Use**: Understand your chunking strategy effectiveness

---

## 🔗 GRAPH RELATIONSHIP QUERIES

### 9. Visualize Document-Chunk Relationships

**What it shows**: Graph structure (best viewed in Graph view)

```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COLLECT(c)[0..5] as sample_chunks
UNWIND sample_chunks as chunk
RETURN d, chunk
LIMIT 50;
```

**How to use**: Click "Graph" view in Neo4j Browser to see relationships

---

### 10. Document Relationship Network

**What it shows**: How documents connect through their chunks

```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count
WHERE chunk_count > 1000
MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COLLECT(c)[0..10] as chunks
UNWIND chunks as chunk
RETURN d, chunk;
```

**Graph Database Benefit**: Visualize how knowledge is structured and connected

---

### 11. Multi-Document Topic Connections

**What it shows**: Documents that share common topics (graph traversal)

```cypher
// Find documents that both discuss "vector search"
MATCH (d1:Document)-[:HAS_CHUNK]->(c1:Chunk)
WHERE toLower(c1.text) CONTAINS 'vector'
WITH DISTINCT d1

MATCH (d2:Document)-[:HAS_CHUNK]->(c2:Chunk)
WHERE toLower(c2.text) CONTAINS 'vector' AND d2 <> d1
WITH DISTINCT d1, d2

RETURN
    CASE WHEN d1.source CONTAINS '/' THEN split(d1.source, '/')[-1] ELSE d1.source END as document1,
    CASE WHEN d2.source CONTAINS '/' THEN split(d2.source, '/')[-1] ELSE d2.source END as document2,
    'discusses vector concepts' as shared_topic
LIMIT 20;
```

**Graph Database Benefit**: Find related content across documents instantly

---

### 12. Chunk Context Window (Neighbors)

**What it shows**: Get a chunk with its surrounding context

```cypher
// Get chunk 100 from first Neo4j book with neighbors
MATCH (d:Document {category: 'neo4j'})-[:HAS_CHUNK]->(c:Chunk {chunk_index: 100})
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(prev:Chunk {chunk_index: 99})
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(next:Chunk {chunk_index: 101})
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    prev.text as previous_chunk,
    c.text as current_chunk,
    next.text as next_chunk
LIMIT 1;
```

**Graph Database Benefit**: Traverse relationships to get context instantly

---

## 🎯 ADVANCED GRAPH QUERIES

### 13. Cross-Document Knowledge Graph

**What it shows**: Build a knowledge graph from shared concepts

```cypher
// Find documents that share multiple technical concepts
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, c.text as text
WHERE toLower(text) CONTAINS 'neo4j'
   OR toLower(text) CONTAINS 'graph'
   OR toLower(text) CONTAINS 'vector'
WITH d,
    COUNT(CASE WHEN toLower(text) CONTAINS 'neo4j' THEN 1 END) as neo4j_mentions,
    COUNT(CASE WHEN toLower(text) CONTAINS 'graph' THEN 1 END) as graph_mentions,
    COUNT(CASE WHEN toLower(text) CONTAINS 'vector' THEN 1 END) as vector_mentions
WHERE neo4j_mentions > 0 OR graph_mentions > 0 OR vector_mentions > 0
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    d.category as category,
    neo4j_mentions,
    graph_mentions,
    vector_mentions
ORDER BY (neo4j_mentions + graph_mentions + vector_mentions) DESC;
```

**Graph Database Benefit**: Analyze concept distribution across your knowledge base

---

### 14. Document Similarity by Content Overlap

**What it shows**: Documents that discuss similar topics

```cypher
// Find documents about graph databases
MATCH (d1:Document)-[:HAS_CHUNK]->(c1:Chunk)
WHERE toLower(c1.text) CONTAINS 'graph database'
WITH DISTINCT d1, COUNT(c1) as mentions1

MATCH (d2:Document)-[:HAS_CHUNK]->(c2:Chunk)
WHERE toLower(c2.text) CONTAINS 'graph database'
  AND d2 <> d1
WITH d1, mentions1, d2, COUNT(c2) as mentions2

RETURN
    CASE WHEN d1.source CONTAINS '/' THEN split(d1.source, '/')[-1] ELSE d1.source END as document1,
    CASE WHEN d2.source CONTAINS '/' THEN split(d2.source, '/')[-1] ELSE d2.source END as document2,
    mentions1 as doc1_mentions,
    mentions2 as doc2_mentions,
    'graph database' as shared_topic
ORDER BY (mentions1 + mentions2) DESC
LIMIT 10;
```

**Graph Database Benefit**: Discover relationships between documents that traditional DB would miss

---

### 15. Topic Co-occurrence Network

**What it shows**: Which topics appear together in documents

```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, c.text as text,
    CASE WHEN toLower(text) CONTAINS 'neo4j' THEN 'Neo4j' END as topic1,
    CASE WHEN toLower(text) CONTAINS 'vector' THEN 'Vector' END as topic2,
    CASE WHEN toLower(text) CONTAINS 'rag' THEN 'RAG' END as topic3,
    CASE WHEN toLower(text) CONTAINS 'graph' THEN 'Graph' END as topic4
WHERE topic1 IS NOT NULL OR topic2 IS NOT NULL OR topic3 IS NOT NULL OR topic4 IS NOT NULL
WITH d,
    COLLECT(DISTINCT topic1) + COLLECT(DISTINCT topic2) +
    COLLECT(DISTINCT topic3) + COLLECT(DISTINCT topic4) as topics
WHERE SIZE([t IN topics WHERE t IS NOT NULL]) >= 2
WITH d, [t IN topics WHERE t IS NOT NULL] as valid_topics
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    d.category as category,
    valid_topics as topics_discussed,
    SIZE(valid_topics) as topic_count
ORDER BY topic_count DESC
LIMIT 15;
```

**Graph Database Benefit**: Multi-dimensional topic analysis in single query

---

### 16. Chunk Traversal Path (Sequential Reading)

**What it shows**: Follow chunk sequence like reading a book

```cypher
// Read first 10 chunks of a document sequentially
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE d.category = 'neo4j'
WITH d, c
ORDER BY c.chunk_index ASC
LIMIT 10
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    c.chunk_index as position,
    substring(c.text, 0, 150) + '...' as content;
```

**Graph Database Benefit**: Preserve reading order through relationships

---

### 17. Find Related Content by Proximity

**What it shows**: Get chunks near a specific topic mention

```cypher
// Find "RAG" mentions and get surrounding chunks
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE c.text CONTAINS 'RAG'
WITH d, c, c.chunk_index as target_idx
LIMIT 3

// Get 2 chunks before and after
MATCH (d)-[:HAS_CHUNK]->(neighbor:Chunk)
WHERE neighbor.chunk_index >= target_idx - 2
  AND neighbor.chunk_index <= target_idx + 2
WITH d, target_idx, COLLECT(neighbor) as context_window
ORDER BY target_idx

RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    target_idx as rag_mention_at_chunk,
    SIZE(context_window) as context_chunks_retrieved,
    [c IN context_window | c.chunk_index] as chunk_indices;
```

**Graph Database Benefit**: Relationship traversal provides instant context windows

---

## 📖 CONTENT DISCOVERY QUERIES

### 18. Topic Distribution Analysis

**What it shows**: What topics are covered in your knowledge base

```cypher
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
        WHEN text CONTAINS 'algorithm' THEN 'Algorithms'
        WHEN text CONTAINS 'neural' OR text CONTAINS 'GNN' THEN 'Neural Networks'
        ELSE 'Other Topics'
    END as knowledge_area,
    COUNT(*) as chunk_count,
    ROUND(toFloat(COUNT(*)) / 30006 * 100, 2) as percentage
ORDER BY chunk_count DESC;
```

**Use**: Understand knowledge base coverage

---

### 19. Publisher/Source Breakdown

**What it shows**: Content sources (O'Reilly, arXiv, Neo4j Official)

```cypher
MATCH (d:Document)
WHERE d.source CONTAINS '.pdf'
WITH d.source as source, d
WITH
    CASE
        WHEN source CONTAINS 'oreilly' OR source CONTAINS 'OReilly' THEN "O'Reilly Media"
        WHEN source CONTAINS 'arxiv' OR source CONTAINS '2312.' OR source CONTAINS '2309.' THEN 'arXiv Papers'
        WHEN source CONTAINS 'neo4j' OR source CONTAINS 'Neo4j' THEN 'Neo4j Official'
        WHEN source CONTAINS 'Beginning' THEN 'Apress'
        WHEN source CONTAINS 'Deep-Learning' OR source CONTAINS 'Graph-Representation' THEN 'Academic Books'
        ELSE 'Other'
    END as publisher, d
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN
    publisher,
    COUNT(DISTINCT d) as documents,
    COUNT(c) as total_chunks,
    ROUND(AVG(toFloat(SIZE(d.content))) / 1024, 1) as avg_doc_size_kb
ORDER BY documents DESC;
```

**Expected**: Neo4j Official (8 docs), arXiv (2), O'Reilly (2)

---

## 🎨 GRAPH VISUALIZATION QUERIES

### 20. Visualize Document Network

**What it shows**: Graph view of all documents and sample chunks

```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COLLECT(c)[0..3] as sample_chunks
UNWIND sample_chunks as chunk
RETURN d, chunk;
```

**How to use**: Switch to "Graph" view in Neo4j Browser
**Graph Database Benefit**: See your knowledge structure visually

---

### 21. Category Network View

**What it shows**: Documents grouped by category

```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE d.category IS NOT NULL
WITH d, COLLECT(c)[0..2] as chunks
UNWIND chunks as chunk
RETURN d.category as category, d, chunk
LIMIT 30;
```

**Use**: View in Graph mode to see category clusters

---

### 22. Largest Documents with Relationships

**What it shows**: Big books with their chunk relationships

```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunks
WHERE chunks > 3000
MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH d, c
WHERE c.chunk_index < 20
RETURN d, c;
```

**Graph Database Benefit**: Visualize document structure and organization

---

## ⚡ PERFORMANCE DEMONSTRATION QUERIES

### 23. Multi-Hop Query (Graph Advantage)

**What it shows**: Find documents → chunks → related documents (multi-hop)

```cypher
// Start from a specific topic, find related content
MATCH (d1:Document {category: 'neo4j'})-[:HAS_CHUNK]->(c1:Chunk)
WHERE toLower(c1.text) CONTAINS 'vector'
WITH DISTINCT d1, COUNT(c1) as vector_mentions

// Find other documents that also discuss vectors
MATCH (d2:Document)-[:HAS_CHUNK]->(c2:Chunk)
WHERE toLower(c2.text) CONTAINS 'vector'
  AND d2 <> d1
WITH d1, vector_mentions, d2, COUNT(c2) as d2_mentions

RETURN
    CASE WHEN d1.source CONTAINS '/' THEN split(d1.source, '/')[-1] ELSE d1.source END as source_document,
    d1.category as source_category,
    vector_mentions,
    CASE WHEN d2.source CONTAINS '/' THEN split(d2.source, '/')[-1] ELSE d2.source END as related_document,
    d2.category as related_category,
    d2_mentions as related_mentions
ORDER BY vector_mentions DESC, d2_mentions DESC
LIMIT 10;
```

**Why Graph DB Wins**: Traditional SQL would need complex self-joins and subqueries

---

### 24. Shortest Path Between Topics

**What it shows**: How topics connect through document relationships

```cypher
// Find path from Neo4j content to RAG content
MATCH path = shortestPath(
  (d1:Document {category: 'neo4j'})-[*..3]-(d2:Document {category: 'rag'})
)
RETURN
    [d IN nodes(path) |
        CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END
    ] as document_path,
    length(path) as path_length;
```

**Graph Database Benefit**: Path finding is native graph operation (impossible in SQL)

---

### 25. Aggregate Knowledge by Category

**What it shows**: Sum all knowledge in a category

```cypher
MATCH (d:Document {category: 'neo4j'})-[:HAS_CHUNK]->(c:Chunk)
WITH d, COLLECT(c.text) as all_chunks, COUNT(c) as chunk_count
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    chunk_count,
    SIZE(all_chunks) as total_chunks_collected,
    'Neo4j knowledge aggregated' as status;
```

**Graph Database Benefit**: Aggregate across relationships in single query

---

## 🔍 DATA QUALITY CHECKS

### 26. Find Orphaned Chunks

**What it shows**: Chunks not connected to any document (should be 0)

```cypher
MATCH (c:Chunk)
WHERE NOT (c)<-[:HAS_CHUNK]-()
RETURN COUNT(c) as orphaned_chunks;
```

**Expected**: 0 (perfect data integrity)

---

### 27. Documents Without Chunks

**What it shows**: Documents that failed processing (should be 0)

```cypher
MATCH (d:Document)
WHERE NOT (d)-[:HAS_CHUNK]->()
RETURN
    d.source as document,
    d.category as category,
    'Missing chunks - processing failed' as issue;
```

**Expected**: No results (all docs processed successfully)

---

### 28. Verify Chunk Index Integrity

**What it shows**: Check for gaps in chunk sequences

```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, MIN(c.chunk_index) as min_idx, MAX(c.chunk_index) as max_idx, COUNT(c) as count
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    min_idx as first_chunk,
    max_idx as last_chunk,
    count as total_chunks,
    max_idx - min_idx + 1 as expected_chunks,
    CASE
        WHEN (max_idx - min_idx + 1) = count THEN '✅ Sequential'
        ELSE '⚠️ Gaps Detected'
    END as index_status
ORDER BY count DESC;
```

**Expected**: All "✅ Sequential" (no gaps)

---

## 🚀 PERFORMANCE & GRAPH DATABASE BENEFITS

### 29. Relationship Density Analysis

**What it shows**: How connected your graph is

```cypher
MATCH (n)
WITH COUNT(n) as total_nodes
MATCH ()-[r]->()
WITH total_nodes, COUNT(r) as total_relationships
RETURN
    total_nodes,
    total_relationships,
    toFloat(total_relationships) / total_nodes as avg_relationships_per_node,
    CASE
        WHEN toFloat(total_relationships) / total_nodes > 0.9 THEN '✅ Highly Connected'
        ELSE '⚠️ Sparsely Connected'
    END as graph_density;
```

**Graph Database Benefit**: Understand your graph's connectivity

---

### 30. Pattern Matching Performance

**What it shows**: Complex pattern matching (graph database specialty)

```cypher
// Find documents with high chunk counts that discuss specific topics
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE toLower(c.text) CONTAINS 'graph'
  AND SIZE(c.text) > 200
WITH d, COUNT(c) as matching_chunks, COLLECT(c.chunk_index)[0..5] as sample_indices
WHERE matching_chunks > 50
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    d.category as category,
    matching_chunks,
    sample_indices
ORDER BY matching_chunks DESC;
```

**Why Graph DB**: Pattern matching with relationships is native operation

---

### 31. Semantic Clustering Simulation

**What it shows**: Group documents by content similarity patterns

```cypher
// Simulate clustering based on shared topics
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, c.text as text
WITH d,
    SUM(CASE WHEN toLower(text) CONTAINS 'neo4j' THEN 1 ELSE 0 END) as neo4j_score,
    SUM(CASE WHEN toLower(text) CONTAINS 'vector' THEN 1 ELSE 0 END) as vector_score,
    SUM(CASE WHEN toLower(text) CONTAINS 'rag' THEN 1 ELSE 0 END) as rag_score,
    SUM(CASE WHEN toLower(text) CONTAINS 'neural' THEN 1 ELSE 0 END) as neural_score
WITH d,
    CASE
        WHEN neo4j_score > 50 AND vector_score > 20 THEN 'Neo4j + Vectors'
        WHEN rag_score > 30 THEN 'RAG Focused'
        WHEN neural_score > 50 THEN 'Neural Networks / ML'
        WHEN neo4j_score > 20 THEN 'Neo4j Focused'
        ELSE 'General Graph Theory'
    END as content_cluster,
    neo4j_score, vector_score, rag_score, neural_score
RETURN
    content_cluster,
    COUNT(d) as documents_in_cluster,
    ROUND(AVG(toFloat(neo4j_score)), 0) as avg_neo4j_mentions,
    ROUND(AVG(toFloat(vector_score)), 0) as avg_vector_mentions
ORDER BY documents_in_cluster DESC;
```

**Graph Database Benefit**: Complex aggregations across relationships

---

## 🎯 PRACTICAL USE CASES

### 32. Find Best Documents for Specific Query

**What it shows**: Which books answer a specific question best

```cypher
// Question: "How to optimize Neo4j performance?"
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE toLower(c.text) CONTAINS 'performance'
  AND (toLower(c.text) CONTAINS 'neo4j' OR toLower(c.text) CONTAINS 'optimization')
WITH d, COUNT(c) as relevant_chunks, COLLECT(substring(c.text, 0, 100))[0..3] as samples
WHERE relevant_chunks > 5
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    d.category as category,
    relevant_chunks as matching_chunks,
    samples as content_samples
ORDER BY relevant_chunks DESC;
```

**Use**: Find best book to answer specific questions

---

### 33. Coverage Gap Analysis

**What it shows**: Topics mentioned rarely (gaps in knowledge base)

```cypher
MATCH (c:Chunk)
WITH
    SUM(CASE WHEN toLower(c.text) CONTAINS 'cypher' THEN 1 ELSE 0 END) as cypher_mentions,
    SUM(CASE WHEN toLower(c.text) CONTAINS 'apoc' THEN 1 ELSE 0 END) as apoc_mentions,
    SUM(CASE WHEN toLower(c.text) CONTAINS 'graph data science' THEN 1 ELSE 0 END) as gds_mentions,
    SUM(CASE WHEN toLower(c.text) CONTAINS 'bloom' THEN 1 ELSE 0 END) as bloom_mentions,
    SUM(CASE WHEN toLower(c.text) CONTAINS 'graphql' THEN 1 ELSE 0 END) as graphql_mentions,
    COUNT(c) as total_chunks
RETURN
    cypher_mentions,
    apoc_mentions,
    gds_mentions,
    bloom_mentions,
    graphql_mentions,
    total_chunks,
    ROUND(toFloat(cypher_mentions) / total_chunks * 100, 2) as cypher_coverage_pct;
```

**Use**: Identify topics to add more content about

---

### 34. Recent Upload Activity

**What it shows**: Timeline of document uploads

```cypher
MATCH (d:Document)
WHERE d.created IS NOT NULL
WITH date(d.created) as upload_date, COUNT(d) as docs_uploaded,
     COLLECT(CASE WHEN d.source CONTAINS '/'
                  THEN split(d.source, '/')[-1]
                  ELSE d.source END)[0..5] as sample_docs
RETURN
    toString(upload_date) as date,
    docs_uploaded as documents,
    sample_docs
ORDER BY upload_date DESC;
```

**Use**: Track when knowledge base was populated

---

### 35. Content Freshness Check

**What it shows**: Verify all content is recent

```cypher
MATCH (d:Document)
WHERE d.created IS NOT NULL
WITH d, duration.between(date(d.created), date()) as age
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    toString(date(d.created)) as uploaded_on,
    age.days as days_old,
    CASE
        WHEN age.days < 1 THEN '🟢 Fresh (today)'
        WHEN age.days < 7 THEN '🟢 Recent (this week)'
        WHEN age.days < 30 THEN '🟡 Current (this month)'
        ELSE '🟠 Older (30+ days)'
    END as freshness
ORDER BY age.days ASC;
```

**Use**: Monitor knowledge base age

---

## 💡 WHY GRAPH DATABASE FOR RAG?

### 36. Relationship Traversal Speed Demo

**What it shows**: How fast Neo4j traverses relationships

```cypher
// Multi-hop traversal - get document → chunks → back to document
PROFILE
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE c.chunk_index < 10
MATCH (c)<-[:HAS_CHUNK]-(original:Document)
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    COUNT(c) as chunks_traversed,
    COUNT(DISTINCT original) as documents_found
LIMIT 10;
```

**Why Graph**: Native relationship traversal (no joins needed)
**Check**: Look at execution time in query profile

---

### 37. Flexible Schema Advantage

**What it shows**: Documents can have different properties (schema-free)

```cypher
MATCH (d:Document)
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    keys(d) as all_properties,
    SIZE(keys(d)) as property_count
ORDER BY property_count DESC
LIMIT 10;
```

**Graph Database Benefit**: No rigid schema, properties evolve with needs

---

### 38. Bidirectional Relationship Query

**What it shows**: Query relationships in both directions easily

```cypher
// From chunks back to documents and forward to more chunks
MATCH (c:Chunk {chunk_index: 0})<-[:HAS_CHUNK]-(d:Document)-[:HAS_CHUNK]->(other:Chunk)
WHERE other.chunk_index IN [1, 2, 3]
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    c.chunk_index as starting_chunk,
    COLLECT(other.chunk_index) as connected_chunks,
    SIZE(COLLECT(other.chunk_index)) as connection_count
LIMIT 5;
```

**Graph Database Benefit**: Bidirectional traversal without complex SQL

---

## 📊 UTILITY QUERIES

### 39. Quick Stats Dashboard

**What it shows**: Single query dashboard view

```cypher
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH COUNT(DISTINCT d) as docs, COUNT(c) as chunks,
     SUM(SIZE(d.content)) as total_chars
MATCH (c2:Chunk) WHERE c2.embedding IS NOT NULL
MATCH (pdf:Document) WHERE pdf.source CONTAINS '.pdf'
RETURN
    docs as total_documents,
    chunks as total_chunks,
    COUNT(DISTINCT pdf) as pdf_documents,
    COUNT(c2) as with_embeddings,
    ROUND(total_chars / 1000000.0, 1) as content_mb,
    ROUND(toFloat(COUNT(c2)) / chunks * 100, 1) as coverage_pct;
```

**Use**: Quick health check of your knowledge base

---

### 40. Export Document List

**What it shows**: Simple list for reports/documentation

```cypher
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunks
ORDER BY chunks DESC
RETURN
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    d.category as category,
    chunks,
    ROUND(SIZE(d.content) / 1024.0, 1) as size_kb;
```

**Use**: Generate inventory reports

---

## 🎓 LEARNING QUERIES

### 41. Sample Content from Each Category

**What it shows**: Preview content from different categories

```cypher
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE d.category IS NOT NULL AND c.chunk_index = 0
RETURN
    d.category as category,
    CASE WHEN d.source CONTAINS '/' THEN split(d.source, '/')[-1] ELSE d.source END as document,
    substring(c.text, 0, 200) + '...' as first_chunk_preview
ORDER BY category;
```

**Use**: Explore what each category contains

---

### 42. Find Technical Terms

**What it shows**: Most common technical terms in your knowledge base

```cypher
MATCH (c:Chunk)
WITH c.text as text, COUNT(*) as total
RETURN
    SUM(CASE WHEN toLower(text) CONTAINS 'graph' THEN 1 ELSE 0 END) as graph_mentions,
    SUM(CASE WHEN toLower(text) CONTAINS 'node' THEN 1 ELSE 0 END) as node_mentions,
    SUM(CASE WHEN toLower(text) CONTAINS 'relationship' THEN 1 ELSE 0 END) as relationship_mentions,
    SUM(CASE WHEN toLower(text) CONTAINS 'cypher' THEN 1 ELSE 0 END) as cypher_mentions,
    SUM(CASE WHEN toLower(text) CONTAINS 'vector' THEN 1 ELSE 0 END) as vector_mentions,
    SUM(CASE WHEN toLower(text) CONTAINS 'embedding' THEN 1 ELSE 0 END) as embedding_mentions,
    SUM(CASE WHEN toLower(text) CONTAINS 'query' THEN 1 ELSE 0 END) as query_mentions,
    total as total_chunks;
```

**Use**: Understand terminology distribution

---

## 💾 EXPORT & BACKUP QUERIES

### 43. Export Document Metadata

**What it shows**: All document metadata for backup

```cypher
MATCH (d:Document)
RETURN
    d.source as source,
    d.category as category,
    d.created as created,
    SIZE(d.content) as content_size,
    keys(d) as all_properties;
```

**Use**: Backup document metadata

---

### 44. Count Everything

**What it shows**: Complete database inventory

```cypher
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) as count', {})
YIELD value
RETURN label as node_type, value.count as count
ORDER BY count DESC;
```

**Note**: Requires APOC plugin (may not be available in Aura Free)
**Alternative**: Use separate MATCH queries for each label

---

### 45. Database Health Summary

**What it shows**: Complete health check in one query

```cypher
MATCH (d:Document)
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
WITH
    COUNT(DISTINCT d) as docs,
    COUNT(c) as chunks,
    COUNT(CASE WHEN c.embedding IS NOT NULL THEN 1 END) as embedded
MATCH (orphan:Chunk) WHERE NOT (orphan)<-[:HAS_CHUNK]-()
WITH docs, chunks, embedded, COUNT(orphan) as orphans
MATCH (empty:Document) WHERE NOT (empty)-[:HAS_CHUNK]->()
WITH docs, chunks, embedded, orphans, COUNT(empty) as no_chunks
RETURN
    docs as documents,
    chunks as total_chunks,
    embedded as chunks_with_embeddings,
    ROUND(toFloat(embedded) / chunks * 100, 1) as coverage_pct,
    orphans as orphaned_chunks,
    no_chunks as empty_documents,
    CASE
        WHEN orphans = 0 AND no_chunks = 0 AND embedded = chunks THEN '✅ Perfect Health'
        WHEN orphans > 0 OR no_chunks > 0 THEN '⚠️ Issues Detected'
        ELSE '✅ Good Health'
    END as health_status;
```

**Use**: Single-query health check

---

## 🎯 GRAPH DATABASE ADVANTAGES DEMONSTRATED

### Key Benefits Shown in These Queries:

1. **Relationship Traversal** (Queries 9-12, 16-17, 23-24, 36)
   - Native graph operations (no JOIN overhead)
   - Multi-hop queries in single statement
   - Bidirectional traversal without complexity

2. **Pattern Matching** (Queries 13, 20-22, 30, 38)
   - Complex patterns expressed naturally
   - ASCII-art syntax matches mental model
   - Flexible pattern variations

3. **Flexible Schema** (Query 37)
   - Properties can vary between nodes
   - Add new properties without migrations
   - Schema evolves with application

4. **Performance** (Queries 23, 29, 36)
   - Sub-second queries on 30K chunks
   - Relationship lookups O(1) constant time
   - No expensive joins or subqueries

5. **Path Finding** (Query 24)
   - Shortest path algorithms built-in
   - Impossible in traditional RDBMS
   - Critical for knowledge graph navigation

6. **Aggregation** (Queries 15, 18-19, 25, 31)
   - Aggregate across relationships
   - Group by patterns, not just columns
   - Complex analytics in single query

---

## 🚀 Quick Reference

**Most Useful Queries:**
- **#1**: Overall stats (health check)
- **#3**: List all books
- **#7**: Embedding coverage
- **#20-22**: Search content
- **#39**: Dashboard view
- **#45**: Complete health check

**Graph Database Showcases:**
- **#23**: Multi-hop relationships
- **#24**: Path finding
- **#29**: Graph density
- **#36**: Traversal performance

**Copy these to Neo4j Browser Favorites for quick access!**

---

**Instance**: `6b870b04` (ma3u)
**Access**: https://console.neo4j.io
**Credentials**: Stored in Azure Key Vault `kv-neo4j-rag-7048` and `.env`
