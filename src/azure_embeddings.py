"""
Azure OpenAI Embeddings Integration for Cost-Optimized POC
Replaces local SentenceTransformer with Azure OpenAI API calls
"""

import os
import asyncio
import logging
from typing import List, Dict, Optional
import numpy as np
from azure.identity import DefaultAzureCredential, AzureCliCredential
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class AzureOpenAIEmbeddings:
    """
    Azure OpenAI embeddings client for cost-optimized POC deployments
    
    Cost Benefits:
    - No local compute for embeddings (saves CPU/memory)
    - Pay-per-use pricing (~$0.10 per 1M tokens)
    - Faster and higher quality embeddings
    - Scales to zero cost when not in use
    """
    
    def __init__(self, 
                 endpoint: Optional[str] = None,
                 deployment_name: str = "text-embedding-ada-002",
                 api_version: str = "2024-02-01"):
        """
        Initialize Azure OpenAI embeddings client
        
        Args:
            endpoint: Azure OpenAI endpoint (from environment if not provided)
            deployment_name: Embedding model deployment name
            api_version: Azure OpenAI API version
        """
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = deployment_name
        self.api_version = api_version
        
        if not self.endpoint:
            raise ValueError("Azure OpenAI endpoint must be provided via parameter or AZURE_OPENAI_ENDPOINT environment variable")
        
        # Initialize client with Managed Identity (production) or CLI (development)
        try:
            credential = DefaultAzureCredential()
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                azure_ad_token_provider=credential.get_token("https://cognitiveservices.azure.com/.default"),
                api_version=self.api_version
            )
            logger.info("Initialized Azure OpenAI client with Managed Identity")
        except Exception as e:
            logger.warning(f"Managed Identity failed, trying Azure CLI: {e}")
            # Fallback to Azure CLI credential for local development
            credential = AzureCliCredential()
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                azure_ad_token_provider=credential.get_token("https://cognitiveservices.azure.com/.default"),
                api_version=self.api_version
            )
            logger.info("Initialized Azure OpenAI client with Azure CLI")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        try:
            # Azure OpenAI embeddings API call
            response = self.client.embeddings.create(
                model=self.deployment_name,
                input=texts
            )
            
            # Extract embeddings from response
            embeddings = []
            for item in response.data:
                embeddings.append(item.embedding)
            
            # Convert to numpy array for compatibility
            embeddings_array = np.array(embeddings)
            
            # Log cost information (approximate)
            total_tokens = response.usage.total_tokens
            estimated_cost = (total_tokens / 1000000) * 0.10  # $0.10 per 1M tokens
            
            logger.info(f"Generated {len(embeddings)} embeddings using {total_tokens} tokens (≈${estimated_cost:.4f})")
            
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def encode_async(self, texts: List[str]) -> np.ndarray:
        """
        Async version of encode method
        """
        # Run the sync method in a thread to avoid blocking
        return await asyncio.to_thread(self.encode, texts)


class CostOptimizedNeo4jRAG:
    """
    Cost-optimized Neo4j RAG system using Azure OpenAI embeddings
    Perfect for POC deployments with low query volumes
    """
    
    def __init__(self, 
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password",
                 azure_openai_endpoint: Optional[str] = None,
                 embedding_deployment: str = "text-embedding-ada-002",
                 max_pool_size: int = 2):  # Reduced for POC
        """
        Initialize cost-optimized RAG system
        """
        # Neo4j connection with minimal pool size
        from neo4j import GraphDatabase
        self.driver = GraphDatabase.driver(
            neo4j_uri, 
            auth=(neo4j_user, neo4j_password),
            max_connection_pool_size=max_pool_size,
            connection_timeout=15.0
        )
        
        # Azure OpenAI embeddings (replaces SentenceTransformer)
        self.embedding_model = AzureOpenAIEmbeddings(
            endpoint=azure_openai_endpoint,
            deployment_name=embedding_deployment
        )
        
        # Simple text splitter
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,  # Smaller chunks for POC = lower costs
            chunk_overlap=20
        )
        
        # Minimal caching for POC
        self._query_cache = {}
        
        logger.info("Initialized cost-optimized Neo4j RAG with Azure OpenAI embeddings")
    
    def add_document(self, content: str, metadata: Optional[Dict] = None, doc_id: Optional[str] = None):
        """Add document with Azure OpenAI embeddings"""
        # Split into smaller chunks (cost optimization)
        chunks = self.text_splitter.split_text(content)
        
        # Generate embeddings using Azure OpenAI
        embeddings = self.embedding_model.encode(chunks)
        
        with self.driver.session() as session:
            if doc_id is None:
                import uuid
                doc_id = str(uuid.uuid4())
            
            # Create document
            session.run("""
                MERGE (d:Document {id: $doc_id})
                SET d.content = $content, d.created = datetime()
            """, doc_id=doc_id, content=content)
            
            # Add chunks with embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                session.run("""
                    MATCH (d:Document {id: $doc_id})
                    CREATE (c:Chunk {
                        text: $text,
                        embedding: $embedding,
                        chunk_index: $index
                    })
                    CREATE (d)-[:HAS_CHUNK]->(c)
                """, doc_id=doc_id, text=chunk, embedding=embedding.tolist(), index=i)
        
        logger.info(f"Added document {doc_id} with {len(chunks)} chunks using Azure OpenAI embeddings")
    
    def vector_search(self, query: str, k: int = 3) -> List[Dict]:
        """Perform vector search using Azure OpenAI query embedding"""
        # Check cache first (POC optimization)
        cache_key = f"{query}_{k}"
        if cache_key in self._query_cache:
            logger.info("Using cached result")
            return self._query_cache[cache_key]
        
        # Generate query embedding using Azure OpenAI
        query_embedding = self.embedding_model.encode([query])[0]
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document)-[:HAS_CHUNK]->(c:Chunk)
                RETURN c.text as text, c.embedding as embedding, d.id as doc_id
                LIMIT $limit
            """, limit=k*3)  # Minimal data retrieval for POC
            
            chunks_with_scores = []
            for record in result:
                chunk_embedding = np.array(record['embedding'])
                similarity = np.dot(query_embedding, chunk_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                )
                
                chunks_with_scores.append({
                    'text': record['text'],
                    'score': float(similarity),
                    'doc_id': record['doc_id']
                })
            
            # Sort and get top k
            chunks_with_scores.sort(key=lambda x: x['score'], reverse=True)
            results = chunks_with_scores[:k]
            
            # Cache for POC (simple caching)
            self._query_cache[cache_key] = results
            
            return results
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document)
                OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                RETURN COUNT(DISTINCT d) as doc_count, COUNT(c) as chunk_count
            """)
            record = result.single()
            return {
                'documents': record['doc_count'],
                'chunks': record['chunk_count'],
                'cache_entries': len(self._query_cache),
                'embedding_provider': 'Azure OpenAI',
                'cost_optimized': True
            }
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()


# Example usage for POC
if __name__ == "__main__":
    # Initialize cost-optimized RAG
    rag = CostOptimizedNeo4jRAG(
        azure_openai_endpoint="https://your-openai.openai.azure.com/"
    )
    
    # Add sample document
    rag.add_document(
        "Neo4j is a graph database that excels at handling connected data and relationships.",
        metadata={'source': 'documentation', 'type': 'intro'}
    )
    
    # Search (uses Azure OpenAI for query embedding)
    results = rag.vector_search("What is Neo4j?", k=2)
    for result in results:
        print(f"Score: {result['score']:.3f}, Text: {result['text']}")
    
    # Show stats
    stats = rag.get_stats()
    print(f"Database stats: {stats}")
    
    rag.close()