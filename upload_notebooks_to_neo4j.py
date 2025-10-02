#!/usr/bin/env python3
"""
Upload Jupyter Notebooks to Neo4j Knowledge Graph

This script processes Jupyter notebooks and stores them in Neo4j
for analysis and search capabilities.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from neo4j_rag import Neo4jRAG
from datetime import datetime

def extract_notebook_content(notebook_path: Path) -> Dict[str, Any]:
    """
    Extract content from a Jupyter notebook file.

    Args:
        notebook_path: Path to the .ipynb file

    Returns:
        Dictionary containing notebook metadata and content
    """
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    content_parts = []
    code_cells = []
    markdown_cells = []

    # Extract content from cells
    for cell in notebook.get('cells', []):
        cell_type = cell.get('cell_type', '')
        source = cell.get('source', [])

        # Join source lines if it's a list
        if isinstance(source, list):
            source = ''.join(source)

        if cell_type == 'markdown':
            markdown_cells.append(source)
            content_parts.append(f"[MARKDOWN]\n{source}\n")
        elif cell_type == 'code':
            code_cells.append(source)
            content_parts.append(f"[CODE]\n{source}\n")

    # Combine all content
    full_content = '\n'.join(content_parts)

    # Extract notebook name and description
    notebook_name = notebook_path.stem
    description = ""

    # Try to get description from first markdown cell
    if markdown_cells and markdown_cells[0]:
        lines = markdown_cells[0].split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                description = line.strip()
                break

    return {
        'name': notebook_name,
        'description': description,
        'full_content': full_content,
        'markdown_cells': len(markdown_cells),
        'code_cells': len(code_cells),
        'total_cells': len(markdown_cells) + len(code_cells),
        'file_path': str(notebook_path)
    }


def upload_notebooks_to_neo4j(notebooks_dir: str = "notebooks"):
    """
    Upload all notebooks from a directory to Neo4j.

    Args:
        notebooks_dir: Directory containing notebook files
    """
    print("🚀 Uploading Notebooks to Neo4j Knowledge Graph")
    print("=" * 50)

    # Initialize Neo4j connection
    try:
        rag = Neo4jRAG()
        print("✅ Connected to Neo4j")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        print("\nMake sure Neo4j is running:")
        print("docker start neo4j-rag")
        return

    # Get initial stats
    initial_stats = rag.get_stats()
    print(f"\n📊 Initial database state:")
    print(f"   Documents: {initial_stats['documents']}")
    print(f"   Chunks: {initial_stats['chunks']}")

    # Find all notebook files
    notebooks_path = Path(notebooks_dir)
    if not notebooks_path.exists():
        print(f"❌ Directory not found: {notebooks_dir}")
        rag.close()
        return

    notebook_files = list(notebooks_path.glob("*.ipynb"))

    if not notebook_files:
        print(f"⚠️ No notebook files found in {notebooks_dir}")
        rag.close()
        return

    print(f"\n📓 Found {len(notebook_files)} notebooks to upload:")
    for nb_file in notebook_files:
        print(f"   - {nb_file.name}")

    # Process each notebook
    uploaded_count = 0
    total_chunks = 0

    for nb_file in notebook_files:
        print(f"\n📝 Processing: {nb_file.name}")

        try:
            # Extract notebook content
            notebook_data = extract_notebook_content(nb_file)

            print(f"   📊 Stats: {notebook_data['markdown_cells']} markdown cells, "
                  f"{notebook_data['code_cells']} code cells")

            # Prepare metadata
            metadata = {
                'source': f"notebook:{nb_file.name}",
                'category': 'tutorial',
                'topic': 'knowledge_graph_analysis',
                'author': 'Neo4j RAG System',
                'notebook_name': notebook_data['name'],
                'description': notebook_data['description'][:200] if notebook_data['description'] else '',
                'markdown_cells': notebook_data['markdown_cells'],
                'code_cells': notebook_data['code_cells'],
                'uploaded_at': datetime.now().isoformat()
            }

            # Add to Neo4j
            doc_id = rag.add_document(
                content=notebook_data['full_content'],
                metadata=metadata
            )

            # Get chunk count for this document
            with rag.driver.session() as session:
                result = session.run("""
                    MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK]->(c:Chunk)
                    RETURN COUNT(c) as chunk_count
                """, doc_id=doc_id)

                chunk_count = result.single()['chunk_count']
                total_chunks += chunk_count

            print(f"   ✅ Uploaded successfully (ID: {doc_id[:8]}...)")
            print(f"   📦 Created {chunk_count} chunks")
            uploaded_count += 1

        except Exception as e:
            print(f"   ❌ Error processing {nb_file.name}: {str(e)}")
            continue

    # Get final stats
    final_stats = rag.get_stats()

    print("\n" + "=" * 50)
    print("📊 Upload Summary:")
    print(f"   Notebooks processed: {uploaded_count}/{len(notebook_files)}")
    print(f"   Total chunks created: {total_chunks}")
    print(f"\n   Database growth:")
    print(f"   Documents: {initial_stats['documents']} → {final_stats['documents']} "
          f"(+{final_stats['documents'] - initial_stats['documents']})")
    print(f"   Chunks: {initial_stats['chunks']} → {final_stats['chunks']} "
          f"(+{final_stats['chunks'] - initial_stats['chunks']})")

    # Test search on notebook content
    print("\n🔍 Testing search on notebook content...")
    test_queries = [
        "graph analysis visualization",
        "knowledge discovery clustering",
        "query optimization performance"
    ]

    for query in test_queries:
        results = rag.vector_search(query, k=3)
        notebook_results = [r for r in results
                           if r.get('metadata', {}).get('source', '').startswith('notebook:')]

        print(f"\n   Query: '{query}'")
        print(f"   Found {len(notebook_results)} notebook-related results")

        if notebook_results:
            best_result = notebook_results[0]
            source = best_result.get('metadata', {}).get('source', 'Unknown')
            score = best_result.get('score', 0)
            text_preview = best_result['text'][:100]
            print(f"   Best match: {source} (score: {score:.3f})")
            print(f"   Preview: {text_preview}...")

    # Close connection
    rag.close()
    print("\n✅ Upload complete! Notebooks are now searchable in your Neo4j knowledge graph.")
    print("\n💡 Next steps:")
    print("   1. Use the search functions to find notebook content")
    print("   2. Query specific topics covered in the notebooks")
    print("   3. Analyze the notebook knowledge using graph queries")
    print("   4. Open Neo4j Browser at http://localhost:7474 to visualize")


def verify_notebook_upload():
    """
    Verify that notebooks were uploaded successfully and show sample queries.
    """
    print("\n🔍 Verifying Notebook Upload")
    print("=" * 50)

    rag = Neo4jRAG()

    # Query for notebook documents
    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            WHERE d.source STARTS WITH 'notebook:'
            RETURN d.source as source,
                   d.notebook_name as name,
                   d.description as description,
                   d.markdown_cells as markdown_cells,
                   d.code_cells as code_cells,
                   COUNT{(d)-[:HAS_CHUNK]->()} as chunks
            ORDER BY d.source
        """)

        notebooks = []
        for record in result:
            notebooks.append({
                'source': record['source'],
                'name': record['name'],
                'description': record.get('description', '')[:100],
                'markdown_cells': record.get('markdown_cells', 0),
                'code_cells': record.get('code_cells', 0),
                'chunks': record['chunks']
            })

    if notebooks:
        print(f"\n📚 Found {len(notebooks)} notebooks in Neo4j:")
        for nb in notebooks:
            print(f"\n   📓 {nb['name']}")
            print(f"      Source: {nb['source']}")
            print(f"      Cells: {nb['markdown_cells']} markdown, {nb['code_cells']} code")
            print(f"      Chunks: {nb['chunks']}")
            if nb['description']:
                print(f"      Description: {nb['description']}...")
    else:
        print("⚠️ No notebooks found in Neo4j")

    # Sample Cypher queries
    print("\n📝 Sample Cypher queries you can run in Neo4j Browser:")
    print("\n1. View all notebook documents:")
    print("   MATCH (d:Document) WHERE d.source STARTS WITH 'notebook:' RETURN d")

    print("\n2. Find chunks about specific topics:")
    print("   MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)")
    print("   WHERE d.source STARTS WITH 'notebook:' AND c.text CONTAINS 'optimization'")
    print("   RETURN d.notebook_name, c.text LIMIT 5")

    print("\n3. Visualize notebook knowledge graph:")
    print("   MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)")
    print("   WHERE d.source STARTS WITH 'notebook:'")
    print("   RETURN d, c LIMIT 50")

    rag.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--verify":
            verify_notebook_upload()
        else:
            upload_notebooks_to_neo4j(sys.argv[1])
    else:
        # Default: upload from notebooks directory
        upload_notebooks_to_neo4j()

        # Then verify
        verify_notebook_upload()