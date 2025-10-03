#!/usr/bin/env python3
"""
Batch PDF Upload to Neo4j RAG System
Processes and uploads all PDFs from a directory to Neo4j using Docling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from src.docling_loader import DoclingDocumentLoader
from src.neo4j_rag import Neo4jRAG
import time
import argparse
from tqdm import tqdm
from tabulate import tabulate
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Suppress verbose Docling logs
logging.getLogger('docling').setLevel(logging.WARNING)
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)


def get_pdf_files(directory: Path, pattern: str = "*.pdf") -> list:
    """Get all PDF files from directory."""
    pdf_files = sorted(directory.glob(pattern))
    return [f for f in pdf_files if f.is_file()]


def categorize_pdf(filename: str) -> str:
    """Categorize PDF based on filename."""
    filename_lower = filename.lower()

    # Define category mappings
    categories = {
        'neo4j': ['neo4j', 'graph_database', 'cypher'],
        'rag': ['rag', 'retrieval', 'augmented'],
        'knowledge_graph': ['knowledge', 'kg', 'ontology'],
        'graph_neural': ['gnn', 'neural', 'deep_learning'],
        'vector_db': ['vector', 'embedding', 'vdbms'],
        'algorithm': ['algorithm', 'spark'],
        'semantic': ['semantic', 'sparql', 'rdf', 'linked'],
        'tutorial': ['beginner', 'dummy', 'introduction'],
        'research': ['arxiv', 'paper', 'survey'],
        'book': ['book', 'oreilly', 'manning', 'apress']
    }

    for category, keywords in categories.items():
        if any(kw in filename_lower for kw in keywords):
            return category

    return 'general'


def extract_pdf_metadata(pdf_path: Path) -> dict:
    """Extract basic metadata from PDF file."""
    stat = pdf_path.stat()

    return {
        'filename': pdf_path.name,
        'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
        'category': categorize_pdf(pdf_path.name),
        'source_type': 'pdf_download',
        'extraction_method': 'docling'
    }


def upload_pdf_to_neo4j(
    pdf_path: Path,
    loader: DoclingDocumentLoader,
    skip_existing: bool = True
) -> dict:
    """Upload a single PDF to Neo4j."""

    result = {
        'filename': pdf_path.name,
        'status': 'pending',
        'chunks': 0,
        'tables': 0,
        'characters': 0,
        'error': None,
        'time_seconds': 0
    }

    try:
        start_time = time.time()

        # Check if document already exists
        if skip_existing and loader.rag:
            with loader.rag.driver.session() as session:
                existing = session.run(
                    "MATCH (d:Document {source: $source}) RETURN COUNT(d) as count",
                    source=str(pdf_path)
                ).single()['count']

                if existing > 0:
                    result['status'] = 'skipped'
                    result['error'] = 'Already exists'
                    return result

        # Extract metadata
        metadata = extract_pdf_metadata(pdf_path)

        # Load document with Docling
        doc_info = loader.load_document(
            str(pdf_path),
            metadata=metadata
        )

        # Update result
        result['status'] = 'success'
        result['chunks'] = doc_info['statistics'].get('chunk_count', 0)
        result['tables'] = doc_info['statistics'].get('table_count', 0)
        result['characters'] = doc_info['statistics'].get('character_count', 0)
        result['time_seconds'] = round(time.time() - start_time, 2)

    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)[:100]
        result['time_seconds'] = round(time.time() - start_time, 2)
        logger.error(f"  ❌ Error: {str(e)[:200]}")

    return result


def main():
    """Main function to upload PDFs to Neo4j."""

    parser = argparse.ArgumentParser(description='Upload PDFs to Neo4j RAG System')
    parser.add_argument(
        '--input',
        default='knowledge/pdfs',
        help='Input directory containing PDFs (default: knowledge/pdfs)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of uploads (for testing)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        default=True,
        help='Skip PDFs already in database (default: True)'
    )
    parser.add_argument(
        '--pattern',
        default='*.pdf',
        help='File pattern to match (default: *.pdf)'
    )
    parser.add_argument(
        '--category',
        help='Only process PDFs matching this category'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be uploaded without processing'
    )

    args = parser.parse_args()

    # Set up paths
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    input_dir = project_root / args.input

    # Check if input directory exists
    if not input_dir.exists():
        logger.error(f"❌ Input directory not found: {input_dir}")
        return 1

    print(f"\n📚 Neo4j RAG PDF Batch Uploader")
    print(f"{'='*60}")
    print(f"📁 Input directory: {input_dir}")

    # Get PDF files
    pdf_files = get_pdf_files(input_dir, args.pattern)

    if not pdf_files:
        logger.error(f"❌ No PDF files found in {input_dir}")
        return 1

    print(f"📄 Found {len(pdf_files)} PDF files")

    # Filter by category if specified
    if args.category:
        pdf_files = [f for f in pdf_files if categorize_pdf(f.name) == args.category]
        print(f"🏷️ Filtered to {len(pdf_files)} files in category: {args.category}")

    # Apply limit if specified
    if args.limit:
        pdf_files = pdf_files[:args.limit]
        print(f"🎯 Limited to {len(pdf_files)} files")

    # Dry run mode
    if args.dry_run:
        print(f"\n🔍 DRY RUN MODE - No files will be processed")
        print(f"{'='*60}\n")

        categories = {}
        total_size = 0

        for pdf in pdf_files:
            metadata = extract_pdf_metadata(pdf)
            cat = metadata['category']
            categories[cat] = categories.get(cat, 0) + 1
            total_size += metadata['file_size_mb']
            print(f"  • {pdf.name[:50]:<50} [{cat:^15}] {metadata['file_size_mb']:>6.1f} MB")

        print(f"\n📊 Summary:")
        print(f"  Total files: {len(pdf_files)}")
        print(f"  Total size: {total_size:.1f} MB")
        print(f"  Categories: {', '.join(f'{k}({v})' for k, v in categories.items())}")
        return 0

    # Connect to Neo4j
    print(f"\n🔗 Connecting to Neo4j...")
    try:
        rag = Neo4jRAG()
        loader = DoclingDocumentLoader(neo4j_rag=rag)
        print("✅ Connected to Neo4j")

        # Get initial stats
        stats_before = rag.get_stats()
        print(f"📊 Current database: {stats_before['documents']} documents, {stats_before['chunks']} chunks")

    except Exception as e:
        logger.error(f"❌ Failed to connect to Neo4j: {e}")
        return 1

    # Process PDFs
    print(f"\n🚀 Starting upload process...")
    print(f"{'='*60}\n")

    results = []
    successful = 0
    failed = 0
    skipped = 0
    total_chunks = 0
    total_tables = 0

    # Process each PDF with progress bar
    with tqdm(pdf_files, desc="Processing PDFs", unit="file") as pbar:
        for pdf_path in pbar:
            # Update progress bar description
            pbar.set_description(f"Processing {pdf_path.name[:30]}...")

            # Process PDF
            result = upload_pdf_to_neo4j(pdf_path, loader, args.skip_existing)
            results.append(result)

            # Update counters
            if result['status'] == 'success':
                successful += 1
                total_chunks += result['chunks']
                total_tables += result['tables']
                logger.info(f"  ✅ {pdf_path.name}: {result['chunks']} chunks, {result['tables']} tables")
            elif result['status'] == 'skipped':
                skipped += 1
                logger.info(f"  ⏭️ {pdf_path.name}: Already exists")
            else:
                failed += 1
                logger.error(f"  ❌ {pdf_path.name}: {result['error']}")

            # Update progress bar postfix
            pbar.set_postfix({
                'Success': successful,
                'Skip': skipped,
                'Fail': failed
            })

    # Get final stats
    stats_after = rag.get_stats()

    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 Upload Summary:\n")

    summary_table = [
        ['Status', 'Count'],
        ['✅ Successful', successful],
        ['⏭️ Skipped', skipped],
        ['❌ Failed', failed],
        ['📄 Total Processed', len(results)]
    ]
    print(tabulate(summary_table, headers='firstrow', tablefmt='grid'))

    if successful > 0:
        print(f"\n📈 Database Changes:")
        print(f"  Documents: {stats_before['documents']} → {stats_after['documents']} (+{stats_after['documents'] - stats_before['documents']})")
        print(f"  Chunks: {stats_before['chunks']} → {stats_after['chunks']} (+{stats_after['chunks'] - stats_before['chunks']})")
        print(f"  Tables extracted: {total_tables}")

        # Show top uploaded files
        print(f"\n📚 Successfully Uploaded:")
        success_results = [r for r in results if r['status'] == 'success']
        success_results.sort(key=lambda x: x['chunks'], reverse=True)

        for result in success_results[:10]:
            print(f"  • {result['filename'][:40]:<40} | {result['chunks']:>4} chunks | {result['time_seconds']:>5.1f}s")

        if len(success_results) > 10:
            print(f"  ... and {len(success_results) - 10} more files")

    if failed > 0:
        print(f"\n⚠️ Failed Uploads:")
        failed_results = [r for r in results if r['status'] == 'failed']
        for result in failed_results[:5]:
            print(f"  • {result['filename']}: {result['error']}")

    # Clean up
    loader.close()
    rag.close()

    print(f"\n✨ Upload complete!")
    print(f"📊 View statistics: python scripts/rag_statistics.py")
    print(f"🔍 Test search: python scripts/rag_search_examples.py")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())