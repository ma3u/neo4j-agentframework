"""
Enhanced Document Loader with Docling
Supports PDF, DOCX, PPTX, HTML, Markdown, and more formats
"""

import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PipelineOptions
from .neo4j_rag import Neo4jRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DoclingDocumentLoader:
    """
    Enhanced document loader using Docling for advanced extraction
    from various document formats including PDF, DOCX, PPTX, etc.
    """

    def __init__(self, neo4j_rag: Optional[Neo4jRAG] = None):
        """Initialize Docling document loader

        Args:
            neo4j_rag: Neo4jRAG instance for storing processed documents
        """
        self.rag = neo4j_rag or Neo4jRAG()

        # Initialize document converter
        self.converter = DocumentConverter()

        # Supported file extensions (Docling auto-detects format)
        self.supported_formats = [
            '.pdf', '.docx', '.doc', '.pptx', '.ppt',
            '.html', '.htm', '.md', '.txt', '.xlsx', '.xls'
        ]

    def load_document(self, file_path: str, metadata: Optional[Dict] = None) -> Dict:
        """Load a single document using Docling

        Args:
            file_path: Path to the document
            metadata: Additional metadata to store with the document

        Returns:
            Dictionary with extraction results and statistics
        """
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check if format is supported
        extension = path.suffix.lower()
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}. Supported: {self.supported_formats}")

        logger.info(f"Loading document: {file_path}")

        try:
            # Convert document with Docling
            result = self.converter.convert(str(path))

            # Extract document information
            doc_info = self._extract_document_info(result.document, path, metadata)

            # Store in Neo4j
            if self.rag:
                self._store_in_neo4j(doc_info)

            return doc_info

        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def _extract_document_info(self, doc, path: Path,
                               custom_metadata: Optional[Dict] = None) -> Dict:
        """Extract structured information from Docling document

        Args:
            doc: Docling document object
            path: Path to the original file
            custom_metadata: Additional metadata to include

        Returns:
            Structured document information
        """
        # Extract text content
        text_content = doc.export_to_markdown() if hasattr(doc, 'export_to_markdown') else str(doc)

        # Extract metadata
        metadata = {
            "source": str(path),
            "filename": path.name,
            "format": path.suffix.lower(),
            "size_bytes": path.stat().st_size if path.exists() else 0
        }

        # Add document metadata if available
        if hasattr(doc, 'metadata'):
            doc_meta = doc.metadata
            if hasattr(doc_meta, 'title'):
                metadata['title'] = doc_meta.title
            if hasattr(doc_meta, 'author'):
                metadata['author'] = doc_meta.author
            if hasattr(doc_meta, 'created_date'):
                metadata['created_date'] = str(doc_meta.created_date)
            if hasattr(doc_meta, 'page_count'):
                metadata['page_count'] = doc_meta.page_count

        # Extract tables if present
        tables = []
        if hasattr(doc, 'tables'):
            for i, table in enumerate(doc.tables):
                table_dict = {
                    "index": i,
                    "content": self._format_table(table)
                }
                # Try to get row/col count if available
                if hasattr(table, 'num_rows'):
                    table_dict["rows"] = table.num_rows
                if hasattr(table, 'num_cols'):
                    table_dict["cols"] = table.num_cols
                tables.append(table_dict)
                metadata[f'table_{i}_summary'] = f"Table {i+1}"

        # Extract images metadata if present
        images = []
        if hasattr(doc, 'images'):
            for i, img in enumerate(doc.images):
                img_info = {
                    "index": i,
                    "caption": getattr(img, 'caption', f'Image {i}'),
                    "alt_text": getattr(img, 'alt_text', '')
                }
                images.append(img_info)
                metadata[f'image_{i}_caption'] = img_info['caption']

        # Extract sections/structure
        sections = []
        if hasattr(doc, 'sections'):
            for section in doc.sections:
                sections.append({
                    "title": getattr(section, 'title', ''),
                    "level": getattr(section, 'level', 1),
                    "content_preview": getattr(section, 'text', '')[:200]
                })

        # Add custom metadata
        if custom_metadata:
            metadata.update(custom_metadata)

        return {
            "content": text_content,
            "metadata": metadata,
            "tables": tables,
            "images": images,
            "sections": sections,
            "statistics": {
                "character_count": len(text_content),
                "table_count": len(tables),
                "image_count": len(images),
                "section_count": len(sections)
            }
        }

    def _format_table(self, table) -> str:
        """Format table data as markdown

        Args:
            table: Table object from Docling

        Returns:
            Markdown formatted table string
        """
        # Simply convert to string if table doesn't have expected structure
        return str(table)

    def _store_in_neo4j(self, doc_info: Dict) -> str:
        """Store extracted document in Neo4j

        Args:
            doc_info: Document information dictionary

        Returns:
            Document ID
        """
        # Prepare content with tables and sections
        full_content = doc_info['content']

        # Append tables to content
        if doc_info['tables']:
            full_content += "\n\n## Tables\n"
            for table in doc_info['tables']:
                full_content += f"\n### Table {table['index'] + 1}\n"
                full_content += table['content'] + "\n"

        # Store in Neo4j using batch_add_documents
        doc_data = [{
            'content': full_content,
            'metadata': doc_info['metadata']
        }]
        self.rag.batch_add_documents(doc_data, batch_size=1)

        # Generate document ID from content hash
        import hashlib
        doc_id = hashlib.sha256(full_content.encode()).hexdigest()[:16]

        logger.info(f"Stored document in Neo4j with ID: {doc_id}")
        logger.info(f"Statistics: {doc_info['statistics']}")

        return doc_id

    def load_directory(self, directory_path: str,
                       recursive: bool = True,
                       file_filter: Optional[List[str]] = None) -> List[Dict]:
        """Load all supported documents from a directory

        Args:
            directory_path: Path to directory containing documents
            recursive: Whether to search subdirectories
            file_filter: List of file extensions to process (e.g., ['.pdf', '.docx'])

        Returns:
            List of document information dictionaries
        """
        path = Path(directory_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")

        # Determine which extensions to process
        extensions_to_process = file_filter or self.supported_formats

        # Find all matching files
        files_to_process = []
        pattern = "**/*" if recursive else "*"

        for ext in extensions_to_process:
            files_to_process.extend(path.glob(f"{pattern}{ext}"))

        logger.info(f"Found {len(files_to_process)} documents to process")

        # Process each file
        results = []
        for file_path in files_to_process:
            try:
                result = self.load_document(str(file_path))
                results.append(result)
                logger.info(f"Successfully processed: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {str(e)}")
                continue

        logger.info(f"Successfully processed {len(results)} out of {len(files_to_process)} documents")

        return results

    def extract_text_only(self, file_path: str) -> str:
        """Extract only text content from a document (no storage)

        Args:
            file_path: Path to the document

        Returns:
            Extracted text content
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Convert document
        result = self.converter.convert(str(path))

        # Return markdown text
        return result.document.export_to_markdown() if hasattr(result.document, 'export_to_markdown') else str(result.document)

    def close(self):
        """Close Neo4j connection"""
        if self.rag:
            self.rag.close()


def demo_docling_loader():
    """Demonstrate Docling document loader capabilities"""

    loader = DoclingDocumentLoader()

    print("=== Docling Document Loader Demo ===\n")
    print("Supported formats:", loader.supported_formats)
    print()

    # Example: Load a PDF
    sample_files = [
        "sample.pdf",
        "document.docx",
        "presentation.pptx",
        "webpage.html",
        "notes.md"
    ]

    for file_name in sample_files:
        if Path(file_name).exists():
            print(f"Loading {file_name}...")
            try:
                info = loader.load_document(file_name)
                print(f"✅ Successfully loaded: {file_name}")
                print(f"   - Characters: {info['statistics']['character_count']}")
                print(f"   - Tables: {info['statistics']['table_count']}")
                print(f"   - Images: {info['statistics']['image_count']}")
                print(f"   - Sections: {info['statistics']['section_count']}")
                print()
            except Exception as e:
                print(f"❌ Error loading {file_name}: {str(e)}")
                print()

    # Example: Load entire directory
    if Path("documents/").exists():
        print("Loading all PDFs from documents/ directory...")
        results = loader.load_directory("documents/", file_filter=['.pdf'])
        print(f"Processed {len(results)} PDF documents")

    loader.close()


if __name__ == "__main__":
    demo_docling_loader()