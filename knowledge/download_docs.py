#!/usr/bin/env python3
"""
Neo4j Documentation Downloader
Downloads official Neo4j manuals and documentation
"""

import requests
import os
from urllib.parse import urlparse

def download_file(url, filename, description=""):
    """Download a file from URL"""
    try:
        print(f"Downloading {description or filename}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Check if it's actually a PDF
        with open(filename, 'rb') as f:
            header = f.read(4)
            if header.startswith(b'%PDF'):
                print(f"✅ Successfully downloaded {filename} ({len(response.content):,} bytes)")
                return True
            else:
                print(f"❌ {filename} is not a valid PDF, removing...")
                os.remove(filename)
                return False
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False

def main():
    """Download Neo4j documentation"""
    
    # Documentation URLs to try
    docs_to_download = [
        {
            "url": "https://neo4j.com/docs/pdf/operations-manual-5.pdf",
            "filename": "neo4j-operations-manual.pdf",
            "description": "Neo4j Operations Manual"
        },
        {
            "url": "https://neo4j.com/docs/pdf/cypher-manual-5.pdf", 
            "filename": "neo4j-cypher-manual.pdf",
            "description": "Neo4j Cypher Manual"
        },
        {
            "url": "https://neo4j.com/docs/pdf/getting-started-5.pdf",
            "filename": "neo4j-getting-started.pdf", 
            "description": "Neo4j Getting Started Guide"
        },
        {
            "url": "https://neo4j.com/docs/pdf/python-driver-manual-5.pdf",
            "filename": "neo4j-python-driver-manual.pdf",
            "description": "Neo4j Python Driver Manual"
        }
    ]
    
    successful_downloads = 0
    
    for doc in docs_to_download:
        if download_file(doc["url"], doc["filename"], doc["description"]):
            successful_downloads += 1
    
    print(f"\n📊 Downloaded {successful_downloads}/{len(docs_to_download)} documents successfully")
    
    # List all files in the knowledge directory
    print("\n📚 Current knowledge base contents:")
    for filename in sorted(os.listdir('.')):
        if filename.endswith('.pdf'):
            size = os.path.getsize(filename)
            print(f"  📄 {filename} ({size:,} bytes)")

if __name__ == "__main__":
    main()