#!/usr/bin/env python3
"""
Basic Usage Examples for Neo4j RAG System

This file contains simple examples to get you started.
Each example is self-contained and explains what it does.
"""

from neo4j_rag import Neo4jRAG, RAGQueryEngine
from docling_loader import DoclingDocumentLoader

# ============================================
# Example 1: Add a Simple Document
# ============================================

def add_simple_document():
    """
    Shows how to add a basic text document to the system.
    This is the simplest way to get started.
    """
    # Connect to Neo4j
    rag = Neo4jRAG()

    # Your document content
    content = """
    Neo4j is a graph database management system.
    It stores data as nodes and relationships, making it perfect
    for connected data. Unlike traditional databases that use tables,
    Neo4j uses a graph structure which is more intuitive for
    many real-world scenarios.
    """

    # Add the document with some metadata
    doc_id = rag.add_document(
        content=content,
        metadata={
            "source": "example",
            "topic": "database",
            "author": "Tutorial"
        }
    )

    print(f"✅ Document added with ID: {doc_id}")

    # Always close the connection
    rag.close()


# ============================================
# Example 2: Search for Information
# ============================================

def search_documents():
    """
    Shows how to search for information in your documents.
    Vector search finds semantically similar content.
    """
    rag = Neo4jRAG()

    # What you're looking for
    query = "How does Neo4j store data?"

    # Search (k=3 means return top 3 results)
    results = rag.vector_search(query, k=3)

    print(f"🔍 Searching for: '{query}'\n")
    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Score: {result['score']:.3f} (higher is better)")
        print(f"  Text: {result['text'][:150]}...")
        print()

    rag.close()


# ============================================
# Example 3: Ask Questions (Q&A)
# ============================================

def ask_questions():
    """
    Shows how to get answers to questions based on your documents.
    The system finds relevant information and formulates an answer.
    """
    rag = Neo4jRAG()
    engine = RAGQueryEngine(rag)

    questions = [
        "What is Neo4j?",
        "How is data stored in Neo4j?",
        "What are the advantages of graph databases?"
    ]

    for question in questions:
        print(f"❓ Question: {question}")

        # Get answer
        response = engine.query(question, k=3)

        print(f"💡 Answer: {response['answer']}")
        print(f"📚 Based on {len(response['sources'])} sources")
        print("-" * 50)
        print()

    rag.close()


# ============================================
# Example 4: Load a PDF Document
# ============================================

def load_pdf_document():
    """
    Shows how to load a PDF file with advanced extraction.
    Docling handles tables, images, and document structure.
    """
    loader = DoclingDocumentLoader()

    # Path to your PDF
    pdf_path = "sample.pdf"  # Change to your PDF path

    try:
        print(f"📄 Loading PDF: {pdf_path}")

        # Load and extract
        doc_info = loader.load_document(
            pdf_path,
            metadata={"category": "report", "year": "2024"}
        )

        # Show what was extracted
        stats = doc_info['statistics']
        print(f"✅ Successfully extracted:")
        print(f"   - {stats['character_count']:,} characters")
        print(f"   - {stats['table_count']} tables")
        print(f"   - {stats['image_count']} images")
        print(f"   - {stats['section_count']} sections")

    except FileNotFoundError:
        print(f"❌ File not found: {pdf_path}")
        print("   Please provide a valid PDF path")

    finally:
        loader.close()


# ============================================
# Example 5: Process Multiple Documents
# ============================================

def batch_processing():
    """
    Shows how to process multiple documents at once.
    Useful for loading your entire document collection.
    """
    loader = DoclingDocumentLoader()

    # Directory containing your documents
    docs_directory = "./documents"  # Change to your directory

    print(f"📁 Processing all documents in: {docs_directory}")

    try:
        # Load all PDFs and Word docs in the directory
        results = loader.load_directory(
            docs_directory,
            recursive=True,  # Include subdirectories
            file_filter=['.pdf', '.docx', '.pptx']
        )

        print(f"✅ Processed {len(results)} documents")

        # Show summary
        for result in results:
            name = result['metadata'].get('filename', 'Unknown')
            chars = result['statistics']['character_count']
            print(f"   - {name}: {chars:,} characters")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        loader.close()


# ============================================
# Example 6: Check What's in Your Database
# ============================================

def check_database_stats():
    """
    Shows how to check what documents and chunks are in your database.
    Useful for verifying your data loaded correctly.
    """
    rag = Neo4jRAG()

    # Get statistics
    stats = rag.get_stats()

    print("📊 Database Statistics:")
    print(f"   - Documents: {stats['documents']}")
    print(f"   - Chunks: {stats['chunks']}")

    # Get a sample of document sources
    with rag.driver.session() as session:
        result = session.run("""
            MATCH (d:Document)
            RETURN d.source as source, d.category as category
            LIMIT 5
        """)

        print("\n📄 Sample Documents:")
        for record in result:
            source = record.get('source', 'Unknown')
            category = record.get('category', 'Uncategorized')
            print(f"   - {source} ({category})")

    rag.close()


# ============================================
# Main - Run Examples
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Neo4j RAG System - Basic Examples")
    print("=" * 60)

    # Uncomment the examples you want to run:

    # add_simple_document()
    # search_documents()
    # ask_questions()
    # load_pdf_document()
    # batch_processing()
    check_database_stats()

    print("\n✅ Examples completed!")
    print("💡 Tip: Uncomment different examples in the main section to try them")