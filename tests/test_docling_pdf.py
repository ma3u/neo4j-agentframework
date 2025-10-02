import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#!/usr/bin/env python3
"""
Test Docling PDF Extraction
Downloads sample PDFs and demonstrates extraction capabilities
"""

import os
import requests
from pathlib import Path
from src.docling_loader import DoclingDocumentLoader
from src.neo4j_rag import Neo4jRAG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_sample_pdfs():
    """Download sample PDF documents for testing"""

    # Create samples directory
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)

    # Sample PDFs to download (publicly available)
    sample_pdfs = [
        {
            "name": "neo4j_datasheet.pdf",
            "url": "https://dist.neo4j.com/wp-content/uploads/2024/01/Neo4j-Aura-Datasheet.pdf",
            "description": "Neo4j Aura datasheet"
        },
        {
            "name": "arxiv_rag_paper.pdf",
            "url": "https://arxiv.org/pdf/2005.11401.pdf",
            "description": "RAG research paper from ArXiv"
        }
    ]

    downloaded = []

    for pdf in sample_pdfs:
        file_path = samples_dir / pdf["name"]

        # Skip if already downloaded
        if file_path.exists():
            logger.info(f"✅ Already exists: {pdf['name']}")
            downloaded.append(str(file_path))
            continue

        try:
            logger.info(f"📥 Downloading: {pdf['name']} - {pdf['description']}")
            response = requests.get(pdf["url"], timeout=30)
            response.raise_for_status()

            # Save PDF
            with open(file_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"✅ Downloaded: {pdf['name']} ({len(response.content):,} bytes)")
            downloaded.append(str(file_path))

        except Exception as e:
            logger.error(f"❌ Failed to download {pdf['name']}: {str(e)}")
            # Create a simple test PDF as fallback
            create_test_pdf(file_path)
            downloaded.append(str(file_path))

    return downloaded


def create_test_pdf(file_path: Path):
    """Create a simple test PDF if downloads fail"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table

        logger.info(f"Creating test PDF: {file_path}")

        # Create PDF
        pdf = SimpleDocTemplate(str(file_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Add content
        story.append(Paragraph("Neo4j RAG System Test Document", styles['Title']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Introduction to Graph Databases", styles['Heading1']))
        story.append(Paragraph(
            "Neo4j is a powerful graph database that excels at managing highly connected data. "
            "It uses nodes, relationships, and properties to represent and store data in a natural, "
            "intuitive way that mirrors how we think about information.",
            styles['BodyText']
        ))
        story.append(Spacer(1, 12))

        story.append(Paragraph("RAG Architecture", styles['Heading1']))
        story.append(Paragraph(
            "Retrieval-Augmented Generation (RAG) combines the power of large language models "
            "with external knowledge retrieval. This approach enables more accurate and contextual "
            "responses by grounding the model's outputs in specific, relevant information.",
            styles['BodyText']
        ))
        story.append(Spacer(1, 12))

        # Add a simple table
        data = [
            ['Component', 'Description', 'Purpose'],
            ['Vector Store', 'Stores embeddings', 'Similarity search'],
            ['LLM', 'Language model', 'Generate responses'],
            ['Retriever', 'Fetch documents', 'Find relevant context']
        ]
        table = Table(data)
        story.append(table)

        # Build PDF
        pdf.build(story)
        logger.info(f"✅ Created test PDF: {file_path}")

    except ImportError:
        # If reportlab not available, create a text file instead
        logger.warning("reportlab not installed, creating text file instead")
        with open(file_path.with_suffix('.txt'), 'w') as f:
            f.write("Neo4j RAG System Test Document\n\n")
            f.write("This is a placeholder text file since PDF generation is not available.\n")
            f.write("Install reportlab to generate actual PDFs: pip install reportlab\n")


def test_pdf_extraction():
    """Test PDF extraction with Docling"""

    print("\n" + "=" * 60)
    print("🧪 Testing Docling PDF Extraction")
    print("=" * 60 + "\n")

    # Download sample PDFs
    print("📥 Downloading sample PDFs...\n")
    pdf_files = download_sample_pdfs()

    if not pdf_files:
        print("⚠️ No PDFs available for testing")
        return

    # Initialize loader with Neo4j
    print("\n🔧 Initializing Docling loader with Neo4j...\n")
    rag = Neo4jRAG()
    loader = DoclingDocumentLoader(neo4j_rag=rag)

    # Process each PDF
    results = []
    for pdf_path in pdf_files:
        print(f"\n📄 Processing: {Path(pdf_path).name}")
        print("-" * 40)

        try:
            # Load PDF with Docling
            doc_info = loader.load_document(
                pdf_path,
                metadata={
                    "category": "test",
                    "extraction_method": "docling"
                }
            )

            # Display extraction results
            print(f"✅ Successfully extracted!")
            print(f"   📊 Statistics:")
            print(f"      - Characters: {doc_info['statistics']['character_count']:,}")
            print(f"      - Tables: {doc_info['statistics']['table_count']}")
            print(f"      - Images: {doc_info['statistics']['image_count']}")
            print(f"      - Sections: {doc_info['statistics']['section_count']}")

            # Show metadata
            print(f"\n   📋 Metadata:")
            for key, value in doc_info['metadata'].items():
                if not key.startswith('table_') and not key.startswith('image_'):
                    print(f"      - {key}: {value}")

            # Show first 500 characters of content
            print(f"\n   📝 Content Preview:")
            content_preview = doc_info['content'][:500].replace('\n', ' ')
            print(f"      {content_preview}...")

            # Show tables if present
            if doc_info['tables']:
                print(f"\n   📊 Tables Found:")
                for table in doc_info['tables'][:2]:  # Show first 2 tables
                    rows = table.get('rows', 'unknown')
                    cols = table.get('cols', 'unknown')
                    print(f"      Table {table['index'] + 1}: {rows}x{cols}")

            results.append({
                "file": Path(pdf_path).name,
                "success": True,
                "chars": doc_info['statistics']['character_count'],
                "tables": doc_info['statistics']['table_count']
            })

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                "file": Path(pdf_path).name,
                "success": False,
                "error": str(e)
            })

    # Test Neo4j retrieval
    print("\n" + "=" * 60)
    print("🔍 Testing Retrieval from Neo4j")
    print("=" * 60 + "\n")

    # Get stats
    stats = rag.get_stats()
    print(f"📊 Database Statistics:")
    print(f"   - Documents: {stats['documents']}")
    print(f"   - Chunks: {stats['chunks']}")

    # Test search
    test_queries = [
        "What is Neo4j?",
        "RAG architecture",
        "graph database benefits"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = rag.hybrid_search(query, k=2)

        if results:
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                preview = result['text'][:100].replace('\n', ' ')
                print(f"   {i}. (Score: {result['score']:.3f}) {preview}...")
        else:
            print("   No results found")

    # Summary
    print("\n" + "=" * 60)
    print("📊 Extraction Summary")
    print("=" * 60 + "\n")

    successful = sum(1 for r in results if r.get('success', False))
    print(f"✅ Successfully processed: {successful}/{len(results)} PDFs")

    for result in results:
        if result.get('success'):
            print(f"   - {result['file']}: {result['chars']:,} characters, {result.get('tables', 0)} tables")
        else:
            print(f"   - {result.get('file', 'Unknown')}: Failed - {result.get('error', 'Unknown error')}")

    # Cleanup
    loader.close()
    rag.close()

    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_pdf_extraction()