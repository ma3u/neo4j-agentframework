#!/usr/bin/env python3
"""
Graph Visualization and Cypher Queries for Neo4j RAG System
Provides queries for visualizing and exploring the knowledge graph structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_rag import Neo4jRAG
import json
from tabulate import tabulate

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print('='*60)

def get_graph_structure(rag):
    """Get the basic graph structure and node/relationship types"""

    print_section("Graph Structure Overview")

    with rag.driver.session() as session:
        # Node labels and counts
        print("\n🔹 Node Labels and Counts:")
        result = session.run("""
            CALL db.labels() YIELD label
            CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN COUNT(n) as count', {})
            YIELD value
            RETURN label, value.count as count
            ORDER BY count DESC
        """)

        labels = []
        for record in result:
            labels.append({
                'Label': record['label'],
                'Count': record['count']
            })

        if labels:
            print(tabulate(labels, headers='keys', tablefmt='grid'))

        # Relationship types
        print("\n🔹 Relationship Types:")
        result = session.run("""
            CALL db.relationshipTypes() YIELD relationshipType
            CALL apoc.cypher.run('MATCH ()-[r:' + relationshipType + ']->() RETURN COUNT(r) as count', {})
            YIELD value
            RETURN relationshipType, value.count as count
        """)

        relationships = []
        for record in result:
            relationships.append({
                'Type': record['relationshipType'],
                'Count': record['count']
            })

        if relationships:
            print(tabulate(relationships, headers='keys', tablefmt='grid'))

def visualize_document_connections(rag):
    """Visualize how documents connect to chunks"""

    print_section("Document-Chunk Connections")

    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
            WITH d, COUNT(c) as chunk_count, COLLECT(c.chunk_index) as indices
            RETURN
                d.source as source,
                d.category as category,
                chunk_count,
                indices[0..5] as sample_indices
            ORDER BY chunk_count DESC
            LIMIT 10
        """)

        connections = []
        for record in result:
            connections.append({
                'Document': record['source'][:30] + '...' if len(record['source']) > 30 else record['source'],
                'Category': record.get('category', 'N/A'),
                'Chunks': record['chunk_count'],
                'Sample Indices': str(record['sample_indices'])
            })

        if connections:
            print("\n📈 Document-Chunk Mapping (Top 10):")
            print(tabulate(connections, headers='keys', tablefmt='grid'))

def find_semantic_clusters(rag):
    """Find semantically similar chunks (potential topics)"""

    print_section("Semantic Similarity Clusters")

    # Sample a few chunks and find similar ones
    sample_queries = [
        "graph database",
        "machine learning",
        "document processing",
        "vector embeddings"
    ]

    print("\n🔍 Finding semantic clusters around key topics:\n")

    for query in sample_queries:
        results = rag.vector_search(query, k=3)

        if results:
            print(f"📌 Topic: '{query}'")
            print(f"   Top related chunks:")

            for i, result in enumerate(results[:3], 1):
                score = result['score']
                text = result['text'][:80].replace('\n', ' ')
                print(f"   {i}. Score {score:.3f}: {text}...")
            print()

def analyze_graph_connectivity(rag):
    """Analyze the connectivity of the graph"""

    print_section("Graph Connectivity Analysis")

    with rag.driver.session() as session:
        # Connected components
        print("\n🔗 Connected Components:")
        result = session.run("""
            MATCH (d:Document)
            RETURN COUNT(DISTINCT d) as total_documents
        """)
        total_docs = result.single()['total_documents']
        print(f"  Total Documents: {total_docs}")

        # Documents without chunks (isolated nodes)
        result = session.run("""
            MATCH (d:Document)
            WHERE NOT (d)-[:HAS_CHUNK]->()
            RETURN COUNT(d) as isolated_documents
        """)
        isolated = result.single()['isolated_documents']
        print(f"  Isolated Documents: {isolated}")
        print(f"  Connected Documents: {total_docs - isolated}")

        # Average degree (chunks per document)
        result = session.run("""
            MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
            WITH d, COUNT(c) as degree
            RETURN AVG(degree) as avg_degree,
                   MIN(degree) as min_degree,
                   MAX(degree) as max_degree
        """)

        stats = result.single()
        print(f"\n📊 Chunk Distribution:")
        print(f"  Average chunks per document: {stats['avg_degree']:.1f}")
        print(f"  Min chunks: {stats['min_degree']}")
        print(f"  Max chunks: {stats['max_degree']}")

def generate_cypher_examples(rag):
    """Generate useful Cypher query examples"""

    print_section("Useful Cypher Queries for RAG Analysis")

    queries = [
        {
            'name': 'Find Documents by Category',
            'query': """MATCH (d:Document {category: 'tutorial'})
RETURN d.source, d.created
LIMIT 5""",
            'description': 'Retrieve documents from a specific category'
        },
        {
            'name': 'Search Chunks by Keyword',
            'query': """MATCH (c:Chunk)
WHERE c.text CONTAINS 'vector'
RETURN c.text, c.chunk_index
LIMIT 5""",
            'description': 'Find chunks containing specific keywords'
        },
        {
            'name': 'Document with Most Chunks',
            'query': """MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunk_count
ORDER BY chunk_count DESC
LIMIT 1
RETURN d.source, chunk_count""",
            'description': 'Identify the most fragmented document'
        },
        {
            'name': 'Recent Documents',
            'query': """MATCH (d:Document)
WHERE d.created IS NOT NULL
RETURN d.source, d.created, d.category
ORDER BY d.created DESC
LIMIT 5""",
            'description': 'Find recently added documents'
        },
        {
            'name': 'Chunk Context Window',
            'query': """MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk {chunk_index: 0})
OPTIONAL MATCH (d)-[:HAS_CHUNK]->(next:Chunk {chunk_index: 1})
RETURN c.text as current, next.text as next_chunk""",
            'description': 'Get chunk with its context'
        }
    ]

    print("\n💡 Example Queries You Can Run:\n")

    for i, q in enumerate(queries, 1):
        print(f"{i}. {q['name']}")
        print(f"   Purpose: {q['description']}")
        print(f"   Query:")
        for line in q['query'].split('\n'):
            print(f"   {line}")
        print()

def visualize_embedding_space(rag):
    """Analyze the embedding space distribution"""

    print_section("Embedding Space Analysis")

    with rag.driver.session() as session:
        # Sample embeddings for analysis
        result = session.run("""
            MATCH (c:Chunk)
            WHERE c.embedding IS NOT NULL
            WITH c.embedding as embedding
            LIMIT 100
            RETURN
                AVG(SIZE(embedding)) as avg_dimensions,
                COUNT(embedding) as sample_size
        """)

        embed_stats = result.single()

        print(f"\n🧮 Embedding Statistics:")
        print(f"  Dimensions: {embed_stats['avg_dimensions']:.0f}")
        print(f"  Sample size: {embed_stats['sample_size']} chunks")

        # Find most similar chunk pairs
        print("\n🔍 Finding Most Similar Chunk Pairs:")

        result = session.run("""
            MATCH (c1:Chunk), (c2:Chunk)
            WHERE id(c1) < id(c2)
            WITH c1, c2,
                 gds.similarity.cosine(c1.embedding, c2.embedding) as similarity
            WHERE similarity > 0.8
            RETURN
                LEFT(c1.text, 50) as chunk1,
                LEFT(c2.text, 50) as chunk2,
                similarity
            ORDER BY similarity DESC
            LIMIT 5
        """)

        similar_pairs = []
        for record in result:
            similar_pairs.append({
                'Chunk 1': record['chunk1'] + '...',
                'Chunk 2': record['chunk2'] + '...',
                'Similarity': f"{record['similarity']:.3f}"
            })

        if similar_pairs:
            print(tabulate(similar_pairs, headers='keys', tablefmt='grid'))
        else:
            print("  No highly similar pairs found (threshold: 0.8)")

def create_graph_visualization_query(rag):
    """Create a query for Neo4j Browser visualization"""

    print_section("Neo4j Browser Visualization Query")

    print("\n🎨 Copy this query to Neo4j Browser for visualization:\n")

    query = """// Visualize Document-Chunk relationships with categories
MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COLLECT(c)[0..3] as sample_chunks
UNWIND sample_chunks as chunk
RETURN d, chunk
LIMIT 50"""

    print(query)

    print("\n📌 Alternative Queries for Different Views:\n")

    alt_queries = [
        {
            'name': 'Category-based view',
            'query': """MATCH (d:Document {category: 'tutorial'})-[:HAS_CHUNK]->(c:Chunk)
RETURN d, c LIMIT 30"""
        },
        {
            'name': 'Recent documents view',
            'query': """MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WHERE d.created > datetime('2024-01-01')
RETURN d, c LIMIT 30"""
        },
        {
            'name': 'High-connectivity view',
            'query': """MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
WITH d, COUNT(c) as chunks
WHERE chunks > 5
MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
RETURN d, c"""
        }
    ]

    for query_info in alt_queries:
        print(f"📍 {query_info['name']}:")
        print(f"{query_info['query']}\n")

def export_graph_data(rag):
    """Export graph data for external visualization tools"""

    print_section("Export Graph Data")

    with rag.driver.session() as session:
        # Export nodes
        result = session.run("""
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
            WITH d, COUNT(c) as chunk_count
            RETURN
                id(d) as node_id,
                'Document' as node_type,
                d.source as label,
                d.category as category,
                chunk_count as size
            LIMIT 20
        """)

        nodes = []
        for record in result:
            nodes.append({
                'id': record['node_id'],
                'type': record['node_type'],
                'label': record['label'][:30] if record['label'] else 'Unknown',
                'category': record.get('category', 'Unknown'),
                'size': record['size']
            })

        # Export edges
        result = session.run("""
            MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
            RETURN
                id(d) as source,
                id(c) as target,
                'HAS_CHUNK' as relationship
            LIMIT 50
        """)

        edges = []
        for record in result:
            edges.append({
                'source': record['source'],
                'target': record['target'],
                'type': record['relationship']
            })

        # Save to JSON files
        graph_data = {
            'nodes': nodes,
            'edges': edges
        }

        output_file = 'graph_visualization_data.json'
        with open(output_file, 'w') as f:
            json.dump(graph_data, f, indent=2)

        print(f"\n✅ Exported graph data to '{output_file}'")
        print(f"   Nodes: {len(nodes)}")
        print(f"   Edges: {len(edges)}")
        print(f"\n📌 Use this data with visualization tools like:")
        print("   - D3.js")
        print("   - Cytoscape.js")
        print("   - Gephi")
        print("   - vis.js")

def main():
    """Run all graph visualization and query examples"""

    print("\n🚀 NEO4J RAG GRAPH VISUALIZATION & QUERIES")
    print("="*60)

    # Connect to Neo4j
    try:
        rag = Neo4jRAG()
        print("✅ Connected to Neo4j")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        print("\nMake sure Neo4j is running:")
        print("  docker start neo4j-rag")
        return

    try:
        # Get initial stats
        stats = rag.get_stats()
        print(f"📊 Database contains {stats['documents']} documents with {stats['chunks']} chunks")

        # Run all visualization and query functions
        get_graph_structure(rag)
        visualize_document_connections(rag)
        find_semantic_clusters(rag)
        analyze_graph_connectivity(rag)
        visualize_embedding_space(rag)
        generate_cypher_examples(rag)
        create_graph_visualization_query(rag)
        export_graph_data(rag)

        print("\n" + "="*60)
        print("✅ Graph visualization and queries complete!")
        print("\n💡 Next steps:")
        print("   1. Open Neo4j Browser at http://localhost:7474")
        print("   2. Run the visualization queries above")
        print("   3. Use exported data for external visualization tools")

    finally:
        rag.close()

if __name__ == "__main__":
    main()