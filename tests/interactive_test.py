import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#!/usr/bin/env python3
"""
Interactive RAG Query Script
Run this to test your own questions against the RAG system
"""

from src.neo4j_rag import Neo4jRAG, RAGQueryEngine
import sys

def get_database_stats(rag):
    """Get database statistics including memory usage estimates"""
    try:
        stats = rag.get_stats()
        
        # Estimate memory usage (rough calculation)
        # Each chunk has ~400-500 chars + 384-dim embedding (1536 bytes)
        # Plus metadata and overhead
        estimated_memory_per_chunk = 2000  # bytes
        estimated_total_mb = (stats['chunks'] * estimated_memory_per_chunk) / (1024 * 1024)
        
        return {
            'documents': stats['documents'],
            'chunks': stats['chunks'],
            'estimated_size_mb': round(estimated_total_mb, 1)
        }
    except Exception as e:
        return {'error': str(e)}

def interactive_rag():
    """Interactive RAG query session"""
    print("\n" + "🤖 NEO4J RAG INTERACTIVE SESSION 🤖".center(60))
    print("=" * 60)
    print("Ask any question about Neo4j, RAG, or related topics!")
    print("Type 'quit' or 'exit' to end the session.\n")
    
    # Initialize RAG system
    rag = Neo4jRAG(
        uri="bolt://localhost:7687",
        username="neo4j", 
        password="password",
        max_pool_size=10  # Optimized connection pooling
    )
    
    # Show database statistics
    db_stats = get_database_stats(rag)
    if 'error' not in db_stats:
        print(f"📊 Database Status:")
        print(f"   • Documents: {db_stats['documents']:,}")
        print(f"   • Chunks: {db_stats['chunks']:,}")
        print(f"   • Estimated Size: ~{db_stats['estimated_size_mb']:.1f} MB")
        print()
    
    engine = RAGQueryEngine(rag)
    
    try:
        while True:
            # Get user input
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', '']:
                break
                
            print("-" * 60)
            
            # Query the RAG system
            try:
                response = engine.query(question, k=3)
                
                print(f"📚 Found {len(response['sources'])} relevant sources:")
                for i, source in enumerate(response['sources'], 1):
                    print(f"   {i}. [{source['score']:.3f}] {source['doc_id']}: {source['text'][:100]}...")
                
                print(f"\n💡 Answer:")
                print(f"   {response['answer']}")
                print()
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a memory error and provide details in MB
                if "OutOfMemoryError" in error_msg:
                    # Extract memory values from error message
                    import re
                    used_match = re.search(r'used: (\d+)', error_msg)
                    max_match = re.search(r'max: (\d+)', error_msg)
                    
                    if used_match and max_match:
                        used_bytes = int(used_match.group(1))
                        max_bytes = int(max_match.group(1))
                        used_mb = used_bytes / (1024 * 1024)
                        max_mb = max_bytes / (1024 * 1024)
                        available_mb = max_mb - used_mb
                        
                        print(f"❌ Memory Error:")
                        print(f"   • Used Memory: {used_mb:.1f} MB")
                        print(f"   • Max Memory: {max_mb:.1f} MB")
                        print(f"   • Available: {available_mb:.1f} MB")
                        print(f"   • Recommendation: Restart Neo4j with more memory or reduce data size")
                    else:
                        print(f"❌ Memory Error: {error_msg}")
                else:
                    print(f"❌ Error: {error_msg}")
                
    except KeyboardInterrupt:
        print("\n\n👋 Session ended by user.")
    finally:
        rag.close()
        print("🔚 Connection closed. Goodbye!")

if __name__ == "__main__":
    interactive_rag()