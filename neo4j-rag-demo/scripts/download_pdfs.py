#!/usr/bin/env python3
"""
PDF Download Script for Neo4j RAG Resources
Downloads PDF resources listed in knowledge/download.md
"""

import os
import re
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import List, Tuple, Optional
import argparse
from tqdm import tqdm

def parse_markdown_links(markdown_file: str) -> List[Tuple[str, str]]:
    """
    Parse markdown file to extract PDF links and titles.

    Args:
        markdown_file: Path to the markdown file

    Returns:
        List of tuples (title, url)
    """
    links = []

    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to match markdown links: [**Title**](URL)
    pattern = r'\[?\*\*([^*]+)\*\*\]?\(([^)]+)\)'
    matches = re.findall(pattern, content)

    for title, url in matches:
        # Clean up the title
        title = title.strip()
        url = url.strip()

        # Only include URLs that look like they might be PDFs or documents
        if url.startswith('http'):
            links.append((title, url))

    return links

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')

    # Replace forward/back slashes with dashes
    filename = filename.replace('/', '-').replace('\\', '-')

    # Limit length
    if len(filename) > 200:
        filename = filename[:200]

    return filename.strip()

def get_filename_from_url(url: str, title: str) -> str:
    """
    Generate a filename from URL or use title as fallback.

    Args:
        url: The URL to download from
        title: The title of the resource

    Returns:
        Filename to use for saving
    """
    # Try to get filename from URL
    parsed = urlparse(url)
    path = unquote(parsed.path)

    if path and path != '/':
        # Get the last part of the path
        filename = os.path.basename(path)

        # If it looks like a PDF filename, use it
        if filename.endswith('.pdf'):
            return sanitize_filename(filename)

    # Otherwise, create filename from title
    filename = sanitize_filename(title) + '.pdf'
    return filename

def download_pdf(url: str, output_path: Path, timeout: int = 30) -> bool:
    """
    Download a PDF from URL to the specified path.

    Args:
        url: URL to download
        output_path: Path where to save the file
        timeout: Download timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    try:
        # Set headers to appear like a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Start download with stream=True for progress bar
        response = requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True)
        response.raise_for_status()

        # Check if it's actually a PDF or HTML (some links might be web pages)
        content_type = response.headers.get('content-type', '').lower()

        # Get total file size
        total_size = int(response.headers.get('content-length', 0))

        # Write file with progress bar
        with open(output_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_path.name) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

        # Verify file is not empty
        if output_path.stat().st_size == 0:
            output_path.unlink()
            return False

        return True

    except requests.exceptions.Timeout:
        print(f"  ⏱️ Timeout downloading from {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error downloading: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def main():
    """Main function to orchestrate PDF downloads."""

    parser = argparse.ArgumentParser(description='Download PDF resources from markdown file')
    parser.add_argument(
        '--input',
        default='knowledge/download.md',
        help='Path to markdown file with links (default: knowledge/download.md)'
    )
    parser.add_argument(
        '--output',
        default='knowledge/pdfs',
        help='Output directory for PDFs (default: knowledge/pdfs)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of downloads (for testing)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between downloads in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip files that already exist'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be downloaded without actually downloading'
    )

    args = parser.parse_args()

    # Get absolute paths
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent

    # Set up paths
    markdown_path = project_root / args.input
    output_dir = project_root / args.output

    # Check if markdown file exists
    if not markdown_path.exists():
        print(f"❌ Markdown file not found: {markdown_path}")
        return 1

    print(f"📚 Neo4j RAG PDF Downloader")
    print(f"{'='*50}")
    print(f"📄 Reading links from: {markdown_path}")
    print(f"📁 Output directory: {output_dir}")

    # Parse markdown to get links
    links = parse_markdown_links(markdown_path)

    if not links:
        print("❌ No links found in the markdown file")
        return 1

    print(f"🔗 Found {len(links)} links")

    if args.limit:
        links = links[:args.limit]
        print(f"🎯 Limiting to {args.limit} downloads")

    if args.dry_run:
        print(f"\n🔍 DRY RUN MODE - No files will be downloaded")
        print(f"{'='*50}")
        for i, (title, url) in enumerate(links, 1):
            filename = get_filename_from_url(url, title)
            print(f"{i:3}. {filename[:60]:<60} {url[:50]}...")
        return 0

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Statistics
    downloaded = 0
    skipped = 0
    failed = 0

    print(f"\n🚀 Starting downloads...")
    print(f"{'='*50}")

    for i, (title, url) in enumerate(links, 1):
        print(f"\n[{i}/{len(links)}] 📖 {title}")
        print(f"  🔗 URL: {url[:80]}{'...' if len(url) > 80 else ''}")

        # Generate filename
        filename = get_filename_from_url(url, title)
        output_path = output_dir / filename

        # Check if file exists
        if output_path.exists() and args.skip_existing:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"  ⏭️ Skipping (exists): {filename} ({size_mb:.1f} MB)")
            skipped += 1
            continue

        # Check for web pages that aren't direct PDF downloads
        if any(domain in url for domain in ['scribd.com', 'academia.edu', 'qdrant.tech/documentation']):
            print(f"  ⚠️ Skipping (requires manual download): {url}")
            skipped += 1
            continue

        # Download the file
        print(f"  📥 Downloading to: {filename}")

        success = download_pdf(url, output_path)

        if success:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ Downloaded successfully ({size_mb:.1f} MB)")
            downloaded += 1
        else:
            print(f"  ❌ Failed to download")
            failed += 1

        # Delay between downloads to be polite
        if i < len(links):
            time.sleep(args.delay)

    # Print summary
    print(f"\n{'='*50}")
    print(f"📊 Download Summary:")
    print(f"  ✅ Downloaded: {downloaded}")
    print(f"  ⏭️ Skipped: {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📁 Total files in directory: {len(list(output_dir.glob('*.pdf')))}")

    # List downloaded files
    if downloaded > 0:
        print(f"\n📚 Downloaded PDFs in {output_dir}:")
        for pdf in sorted(output_dir.glob('*.pdf'))[:10]:
            size_mb = pdf.stat().st_size / (1024 * 1024)
            print(f"  • {pdf.name[:60]:<60} ({size_mb:6.1f} MB)")

        if len(list(output_dir.glob('*.pdf'))) > 10:
            print(f"  ... and {len(list(output_dir.glob('*.pdf'))) - 10} more files")

    print(f"\n✨ Done!")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())