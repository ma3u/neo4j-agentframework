"""
Load sample data into Neo4j RAG system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.neo4j_rag import Neo4jRAG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample documents about different topics
SAMPLE_DOCUMENTS = [
    {
        "content": """
        Neo4j is a highly scalable native graph database management system. It is designed
        specifically for storing and managing connected data. Neo4j excels at handling complex
        relationships and can traverse millions of connections per second. The database uses
        property graphs where data is stored as nodes, relationships, and properties.
        Each node represents an entity, relationships connect nodes, and properties provide
        additional information about nodes and relationships.
        """,
        "metadata": {"source": "neo4j_overview", "category": "database", "topic": "graph_database"}
    },
    {
        "content": """
        Cypher is Neo4j's declarative graph query language. It allows users to efficiently
        read, write, and delete data from the graph database. Cypher's syntax is designed to
        be intuitive and visual, using ASCII-art to represent patterns. For example,
        (a)-[:KNOWS]->(b) represents a relationship where node 'a' knows node 'b'.
        Common Cypher commands include MATCH for pattern matching, CREATE for adding data,
        and RETURN for specifying what data to retrieve.
        """,
        "metadata": {"source": "cypher_guide", "category": "query_language", "topic": "cypher"}
    },
    {
        "content": """
        Graph databases differ from traditional relational databases in how they store and
        query connected data. While relational databases use tables and foreign keys,
        graph databases use nodes and relationships as first-class citizens. This makes
        graph databases ideal for use cases like social networks, recommendation engines,
        fraud detection, and knowledge graphs. They excel at queries that would require
        multiple joins in a relational database.
        """,
        "metadata": {"source": "graph_vs_relational", "category": "comparison", "topic": "database_types"}
    },
    {
        "content": """
        Retrieval-Augmented Generation (RAG) is an AI framework that enhances large language
        models by providing them with relevant context from external knowledge sources.
        The RAG pipeline typically consists of three steps: retrieval of relevant documents
        based on a query, augmentation of the prompt with retrieved context, and generation
        of the response using the augmented prompt. This approach helps reduce hallucinations
        and provides more accurate, up-to-date responses.
        """,
        "metadata": {"source": "rag_concepts", "category": "ai", "topic": "rag"}
    },
    {
        "content": """
        Vector embeddings are numerical representations of text that capture semantic meaning.
        In a RAG system, documents are split into chunks and each chunk is converted to a
        vector embedding using models like Sentence-BERT or OpenAI's text-embedding models.
        These embeddings enable semantic similarity search, where queries are matched against
        documents based on meaning rather than exact keyword matching. Cosine similarity is
        commonly used to measure the similarity between embedding vectors.
        """,
        "metadata": {"source": "embeddings_guide", "category": "ai", "topic": "embeddings"}
    },
    {
        "content": """
        Neo4j can be effectively used as a vector database for RAG applications. By storing
        document chunks as nodes with embedding properties, Neo4j enables both vector
        similarity search and graph traversal in a single query. This hybrid approach
        allows for sophisticated retrieval strategies that combine semantic similarity
        with graph relationships, such as finding related documents through citation networks
        or organizational hierarchies.
        """,
        "metadata": {"source": "neo4j_rag", "category": "integration", "topic": "neo4j_vectors"}
    },
    {
        "content": """
        Python is the primary language for implementing RAG systems. Key libraries include
        LangChain for orchestration, Sentence-Transformers for generating embeddings,
        and Neo4j Python driver for database interactions. The typical workflow involves
        loading documents, splitting them into chunks, generating embeddings, storing them
        in Neo4j, and then querying based on semantic similarity to retrieve relevant context
        for answering questions.
        """,
        "metadata": {"source": "python_rag", "category": "programming", "topic": "python"}
    },
    {
        "content": """
        Best practices for RAG implementation include: choosing appropriate chunk sizes
        (typically 200-500 tokens), implementing chunk overlap to maintain context,
        using hybrid search combining vector and keyword search, storing metadata for
        filtering and attribution, implementing caching for frequently accessed embeddings,
        and monitoring retrieval quality through metrics like relevance scores and user feedback.
        """,
        "metadata": {"source": "rag_best_practices", "category": "best_practices", "topic": "rag_implementation"}
    }
]


def load_sample_data():
    """Load sample documents into Neo4j RAG system"""

    # Initialize RAG system
    rag = Neo4jRAG(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password"
    )

    try:
        # Clear existing data
        logger.info("Clearing existing data...")
        rag.clear_database()

        # Load each document
        logger.info(f"Loading {len(SAMPLE_DOCUMENTS)} documents...")
        for i, doc in enumerate(SAMPLE_DOCUMENTS, 1):
            rag.add_document(
                content=doc["content"],
                metadata=doc["metadata"],
                doc_id=f"doc_{i}"
            )
            logger.info(f"Loaded document {i}/{len(SAMPLE_DOCUMENTS)}: {doc['metadata']['source']}")

        # Display statistics
        stats = rag.get_stats()
        logger.info(f"Database statistics: {stats}")

        logger.info("Sample data loaded successfully!")

    finally:
        rag.close()


if __name__ == "__main__":
    load_sample_data()