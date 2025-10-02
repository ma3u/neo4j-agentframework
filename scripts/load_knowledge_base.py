import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#!/usr/bin/env python3
"""
Knowledge Base Processor using Docling
Extracts content from PDFs and Markdown files in the knowledge folder
and loads them into the Neo4j RAG system
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import ConversionStatus
from src.neo4j_rag import Neo4jRAG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeBaseProcessor:
    """Process documents from knowledge folder using Docling and load into RAG system"""
    
    def __init__(self, knowledge_dir: str = "knowledge", 
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_username: str = "neo4j", 
                 neo4j_password: str = "password"):
        """
        Initialize the knowledge base processor
        
        Args:
            knowledge_dir: Path to knowledge base folder
            neo4j_uri: Neo4j connection URI
            neo4j_username: Neo4j username
            neo4j_password: Neo4j password
        """
        self.knowledge_dir = Path(knowledge_dir)
        self.rag = Neo4jRAG(neo4j_uri, neo4j_username, neo4j_password)
        
        # Initialize document converter with default settings
        self.converter = DocumentConverter()
        
        logger.info(f"Initialized KnowledgeBaseProcessor for {self.knowledge_dir}")
        
    def get_supported_files(self) -> List[Path]:
        """Get list of supported files in knowledge directory"""
        supported_extensions = {'.pdf', '.md', '.txt', '.docx', '.pptx'}
        
        files = []
        for file_path in self.knowledge_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                files.append(file_path)
                
        logger.info(f"Found {len(files)} supported documents")
        return sorted(files)
    
    def extract_pdf_content(self, pdf_path: Path) -> str:
        """Extract content from PDF using Docling"""
        try:
            logger.info(f"Processing PDF: {pdf_path.name}")
            
            # Convert document
            result = self.converter.convert(str(pdf_path))
            
            if result.status == ConversionStatus.SUCCESS:
                # Extract text content
                content = result.document.export_to_markdown()
                
                logger.info(f"Successfully extracted {len(content)} characters from {pdf_path.name}")
                return content
            else:
                logger.warning(f"Failed to convert {pdf_path.name}: {result.status}")
                return ""
                
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
            return ""
    
    def extract_markdown_content(self, md_path: Path) -> str:
        """Extract content from Markdown file"""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Loaded {len(content)} characters from {md_path.name}")
            return content
        except Exception as e:
            logger.error(f"Error reading {md_path.name}: {e}")
            return ""
    
    def extract_text_content(self, txt_path: Path) -> str:
        """Extract content from text file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Loaded {len(content)} characters from {txt_path.name}")
            return content
        except Exception as e:
            logger.error(f"Error reading {txt_path.name}: {e}")
            return ""
    
    def extract_office_content(self, office_path: Path) -> str:
        """Extract content from Office documents (DOCX, PPTX) using Docling"""
        try:
            logger.info(f"Processing Office document: {office_path.name}")
            
            # Convert document
            result = self.converter.convert(str(office_path))
            
            if result.status == ConversionStatus.SUCCESS:
                # Extract text content
                content = result.document.export_to_markdown()
                
                logger.info(f"Successfully extracted {len(content)} characters from {office_path.name}")
                return content
            else:
                logger.warning(f"Failed to convert {office_path.name}: {result.status}")
                return ""
                
        except Exception as e:
            logger.error(f"Error processing {office_path.name}: {e}")
            return ""
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a single document and extract its content"""
        
        # Determine file type and extract content
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            content = self.extract_pdf_content(file_path)
            doc_type = 'pdf'
        elif suffix == '.md':
            content = self.extract_markdown_content(file_path)
            doc_type = 'markdown'
        elif suffix == '.txt':
            content = self.extract_text_content(file_path)
            doc_type = 'text'
        elif suffix in ['.docx', '.pptx']:
            content = self.extract_office_content(file_path)
            doc_type = 'office'
        else:
            logger.warning(f"Unsupported file type: {suffix}")
            return None
        
        if not content.strip():
            logger.warning(f"No content extracted from {file_path.name}")
            return None
        
        # Create document metadata
        file_stats = file_path.stat()
        
        metadata = {
            'source': file_path.name,
            'category': 'neo4j_knowledge',
            'type': doc_type,
            'file_size': file_stats.st_size,
            'file_extension': suffix,
            'topic': self._infer_topic(file_path.name),
            'source_folder': 'knowledge'
        }
        
        return {
            'content': content,
            'metadata': metadata,
            'doc_id': f"kb_{file_path.stem}"
        }
    
    def _infer_topic(self, filename: str) -> str:
        """Infer document topic from filename"""
        filename_lower = filename.lower()
        
        if 'operations' in filename_lower:
            return 'neo4j_operations'
        elif 'developer' in filename_lower or 'browser' in filename_lower:
            return 'neo4j_development'
        elif 'graphrag' in filename_lower or 'rag' in filename_lower:
            return 'rag_implementation'
        elif 'python' in filename_lower or 'driver' in filename_lower:
            return 'neo4j_python'
        elif 'cypher' in filename_lower:
            return 'cypher_language'
        else:
            return 'neo4j_general'
    
    def clear_existing_knowledge(self):
        """Clear existing knowledge base documents from Neo4j"""
        logger.info("Clearing existing knowledge base documents...")
        
        with self.rag.driver.session() as session:
            # Delete knowledge base documents and their chunks
            result = session.run("""
                MATCH (d:Document {category: 'neo4j_knowledge'})
                OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                DELETE d, c
                RETURN COUNT(d) as deleted_docs
            """)
            
            record = result.single()
            deleted_count = record['deleted_docs'] if record else 0
            logger.info(f"Deleted {deleted_count} existing knowledge base documents")
    
    def process_knowledge_base(self, clear_existing: bool = True) -> Dict[str, Any]:
        """Process all documents in knowledge base"""
        
        if clear_existing:
            self.clear_existing_knowledge()
        
        # Get all supported files
        files = self.get_supported_files()
        
        if not files:
            logger.warning("No supported files found in knowledge directory")
            return {'processed': 0, 'failed': 0, 'total_chunks': 0}
        
        processed_count = 0
        failed_count = 0
        total_chunks = 0
        
        logger.info(f"Processing {len(files)} documents...")
        
        for file_path in files:
            try:
                # Process document
                doc_data = self.process_document(file_path)
                
                if doc_data:
                    # Add to RAG system
                    logger.info(f"Loading {doc_data['doc_id']} into RAG system...")
                    
                    self.rag.add_document(
                        content=doc_data['content'],
                        metadata=doc_data['metadata'],
                        doc_id=doc_data['doc_id']
                    )
                    
                    processed_count += 1
                    
                    # Get chunk count for this document
                    stats = self.rag.get_stats()
                    current_chunks = stats['chunks']
                    
                    logger.info(f"✅ Successfully loaded {doc_data['doc_id']}")
                else:
                    failed_count += 1
                    logger.warning(f"❌ Failed to process {file_path.name}")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Error processing {file_path.name}: {e}")
        
        # Get final statistics
        final_stats = self.rag.get_stats()
        total_chunks = final_stats['chunks']
        
        summary = {
            'processed': processed_count,
            'failed': failed_count,
            'total_files': len(files),
            'total_documents': final_stats['documents'],
            'total_chunks': total_chunks
        }
        
        logger.info(f"""
📊 Knowledge Base Processing Complete!
   • Files processed: {processed_count}/{len(files)}
   • Failed: {failed_count}
   • Total documents in DB: {final_stats['documents']}
   • Total chunks in DB: {total_chunks}
        """)
        
        return summary
    
    def close(self):
        """Close database connection"""
        self.rag.close()

def main():
    """Main function to process knowledge base"""
    
    processor = KnowledgeBaseProcessor()
    
    try:
        # Process all documents
        results = processor.process_knowledge_base(clear_existing=True)
        
        print("\n🎉 Knowledge Base Loading Complete!")
        print(f"📄 Documents loaded: {results['processed']}")
        print(f"📝 Total chunks: {results['total_chunks']}")
        print(f"❌ Failed documents: {results['failed']}")
        
        if results['processed'] > 0:
            print("\n🔍 You can now query the knowledge base with questions like:")
            print("   • 'How do I configure Neo4j for production?'")
            print("   • 'What are Neo4j memory requirements?'")
            print("   • 'How to implement RAG with Neo4j?'")
            print("   • 'What are Neo4j best practices?'")
            
            print("\n🚀 Test with: python interactive_test.py")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
    finally:
        processor.close()

if __name__ == "__main__":
    main()