"""
Official Neo4j GraphRAG Implementation Demo
Based on Neo4j's official GraphRAG Python library
"""

from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import VectorRetriever, VectorCypherRetriever
from neo4j_graphrag.embeddings import SentenceTransformerEmbeddings
from neo4j_graphrag.generation import GraphRAG
from neo4j_graphrag.llm import LLMInterface, LLMResponse
import logging
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleLLM(LLMInterface):
    """Simple LLM implementation for demonstration without API keys"""

    def __init__(self):
        """Initialize with model name"""
        super().__init__(model_name="demo-llm")

    def invoke(self, input: str, model_params: Optional[dict[str, Any]] = None, **kwargs) -> LLMResponse:
        """Simple response generation"""
        # In production, this would call OpenAI, Anthropic, etc.
        # For demo, we'll return the context with a simple response
        response = f"Based on the provided context:\n\n{input[:500]}...\n\nThis information answers your query."
        return LLMResponse(content=response)

    async def ainvoke(self, input: str, model_params: Optional[dict[str, Any]] = None) -> LLMResponse:
        """Async version of invoke"""
        return self.invoke(input, model_params)


class Neo4jGraphRAGDemo:
    """
    Official Neo4j GraphRAG implementation demonstration
    """

    def __init__(self, uri: str = "bolt://localhost:7687",
                 username: str = "neo4j",
                 password: str = "password"):
        """Initialize GraphRAG components"""

        # Initialize Neo4j driver
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

        # Initialize embeddings (using Sentence Transformers for local execution)
        self.embedder = SentenceTransformerEmbeddings(
            model="all-MiniLM-L6-v2"
        )

        # Initialize LLM (simple implementation for demo)
        self.llm = SimpleLLM()

        # Create vector index
        self._create_vector_index()

        logger.info("Neo4j GraphRAG initialized successfully")

    def _create_vector_index(self):
        """Create vector index in Neo4j"""
        with self.driver.session() as session:
            # Create vector index for embeddings
            try:
                session.run("""
                    CREATE VECTOR INDEX `document_embeddings` IF NOT EXISTS
                    FOR (n:Document)
                    ON (n.embedding)
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: 384,
                        `vector.similarity_function`: 'cosine'
                    }}
                """)
                logger.info("Vector index created/verified")
            except Exception as e:
                # Index might already exist or syntax might vary by Neo4j version
                logger.info(f"Index creation note: {e}")

    def add_documents(self, documents: list[dict]):
        """
        Add documents to Neo4j with embeddings

        Args:
            documents: List of dicts with 'content' and 'metadata' keys
        """
        with self.driver.session() as session:
            for doc in documents:
                # Generate embedding
                embedding = self.embedder.embed_query(doc['content'])

                # Store document with embedding
                session.run("""
                    CREATE (d:Document {
                        content: $content,
                        embedding: $embedding,
                        source: $source,
                        category: $category
                    })
                """,
                    content=doc['content'],
                    embedding=embedding,
                    source=doc.get('metadata', {}).get('source', 'unknown'),
                    category=doc.get('metadata', {}).get('category', 'general')
                )

                logger.info(f"Added document: {doc.get('metadata', {}).get('source', 'unknown')}")

    def create_vector_retriever(self, top_k: int = 3):
        """
        Create a VectorRetriever for semantic search

        Args:
            top_k: Number of results to retrieve

        Returns:
            VectorRetriever instance
        """
        return VectorRetriever(
            driver=self.driver,
            index_name="document_embeddings",
            embedder=self.embedder,
            return_properties=["content", "source", "category"],
            result_formatter=None,
            neo4j_database=None
        )

    def create_graphrag_pipeline(self, retriever):
        """
        Create a GraphRAG pipeline

        Args:
            retriever: Retriever instance

        Returns:
            GraphRAG instance
        """
        return GraphRAG(
            retriever=retriever,
            llm=self.llm
        )

    def query(self, question: str, top_k: int = 3):
        """
        Query the GraphRAG system

        Args:
            question: User question
            top_k: Number of documents to retrieve

        Returns:
            Generated response
        """
        # Create retriever
        retriever = self.create_vector_retriever(top_k=top_k)

        # Create GraphRAG pipeline
        rag = self.create_graphrag_pipeline(retriever)

        # Execute query
        response = rag.search(query_text=question, retriever_config={"top_k": top_k})

        return response

    def close(self):
        """Close database connection"""
        self.driver.close()


def demo_graphrag():
    """Demonstrate the official Neo4j GraphRAG implementation"""

    # Sample documents
    documents = [
        {
            "content": "Neo4j is a graph database that excels at handling connected data. "
                      "It uses nodes, relationships, and properties to represent and store data.",
            "metadata": {"source": "neo4j_intro", "category": "database"}
        },
        {
            "content": "GraphRAG combines the power of knowledge graphs with retrieval-augmented generation. "
                      "It provides better context and relationships for AI applications.",
            "metadata": {"source": "graphrag_overview", "category": "ai"}
        },
        {
            "content": "Cypher is Neo4j's query language, designed for working with graph patterns. "
                      "It uses ASCII-art syntax to represent nodes and relationships visually.",
            "metadata": {"source": "cypher_guide", "category": "query"}
        }
    ]

    # Initialize GraphRAG
    graphrag = Neo4jGraphRAGDemo()

    try:
        # Clear existing data
        with graphrag.driver.session() as session:
            session.run("MATCH (n:Document) DELETE n")
            logger.info("Cleared existing documents")

        # Add documents
        logger.info("Adding sample documents...")
        graphrag.add_documents(documents)

        # Test queries
        test_queries = [
            "What is Neo4j?",
            "How does GraphRAG work?",
            "Tell me about Cypher query language"
        ]

        print("\n" + "="*60)
        print("NEO4J GRAPHRAG DEMO - OFFICIAL IMPLEMENTATION")
        print("="*60 + "\n")

        for query in test_queries:
            print(f"Query: {query}")
            print("-" * 40)

            response = graphrag.query(query, top_k=2)
            print(f"Response: {response}")
            print("\n")

    finally:
        graphrag.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    demo_graphrag()