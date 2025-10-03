#!/usr/bin/env python3
"""
Simple PDF Upload Script - Uploads PDFs one by one to Neo4j
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from src.docling_loader import DoclingDocumentLoader
from src.neo4j_rag import Neo4jRAG
import time

def main():
    pdf_dir = Path("knowledge/pdfs")
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    print(f"📚 Found {len(pdf_files)} PDFs to process\n")

    # Connect to Neo4j
    rag = Neo4jRAG()
    loader = DoclingDocumentLoader(neo4j_rag=rag)

    # Get initial stats
    stats_before = rag.get_stats()
    print(f"📊 Initial: {stats_before['documents']} documents, {stats_before['chunks']} chunks\n")

    successful = 0
    skipped = 0
    failed = 0

    # Process each PDF
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] 📄 {pdf_path.name}")

        # Check if already exists
        with rag.driver.session() as session:
            existing = session.run(
                "MATCH (d:Document {source: $source}) RETURN COUNT(d) as count",
                source=str(pdf_path)
            ).single()['count']

            if existing > 0:
                print(f"  ⏭️ Skipping - already exists\n")
                skipped += 1
                continue

        # Get file size
        size_mb = pdf_path.stat().st_size / (1024 * 1024)

        # Skip very large files (>15MB) for now
        if size_mb > 15:
            print(f"  ⚠️ Skipping - too large ({size_mb:.1f} MB)\n")
            skipped += 1
            continue

        try:
            print(f"  📥 Uploading ({size_mb:.1f} MB)...")
            start = time.time()

            # Upload with timeout
            doc_info = loader.load_document(
                str(pdf_path),
                metadata={
                    'category': 'pdf_resource',
                    'source_type': 'pdf_download',
                    'file_size_mb': round(size_mb, 2)
                }
            )

            elapsed = time.time() - start
            chunks = doc_info.get('statistics', {}).get('chunk_count', 0)

            print(f"  ✅ Success! {chunks} chunks in {elapsed:.1f}s\n")
            successful += 1

        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            break

        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}\n")
            failed += 1

            # If too many failures, stop
            if failed > 5:
                print("❌ Too many failures, stopping")
                break

    # Get final stats
    stats_after = rag.get_stats()

    # Print summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print(f"  ✅ Successful: {successful}")
    print(f"  ⏭️ Skipped: {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"\n📈 Database changes:")
    print(f"  Documents: {stats_before['documents']} → {stats_after['documents']} (+{stats_after['documents'] - stats_before['documents']})")
    print(f"  Chunks: {stats_before['chunks']} → {stats_after['chunks']} (+{stats_after['chunks'] - stats_before['chunks']})")

    # Clean up
    loader.close()
    rag.close()

    print("\n✨ Done!")

if __name__ == "__main__":
    main()