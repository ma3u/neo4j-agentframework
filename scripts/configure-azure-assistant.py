#!/usr/bin/env python3
"""
Configure Azure AI Assistant with Neo4j RAG Integration

This script configures your Assistant347 (asst_LHQBXYvRhnbFo7KQ7IRbVXRR)
to use the Neo4j RAG system with 417x performance.

Usage:
    python scripts/configure-azure-assistant.py
"""

import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Configuration
ASSISTANT_ID = "asst_LHQBXYvRhnbFo7KQ7IRbVXRR"
AZURE_OPENAI_ENDPOINT = os.getenv(
    'AZURE_OPENAI_ENDPOINT',
    'https://neo4j-rag-bitnet-ai.openai.azure.com/'
)
AZURE_OPENAI_API_VERSION = "2024-10-01-preview"

# Instructions for the assistant
ASSISTANT_INSTRUCTIONS = """You are an intelligent AI assistant with access to a high-performance Neo4j knowledge base.

## Your Capabilities

You have access to a **Neo4j RAG system** with exceptional performance:
- ⚡ **417x faster retrieval** than traditional vector databases
- 🧠 **87% memory reduction** with BitNet.cpp LLM
- 📄 **Advanced PDF processing** with Docling (tables, images, structure)
- 🔍 **Hybrid search** combining vector similarity and keyword matching

## Your Tools

1. **search_knowledge_base** - Search the Neo4j knowledge base
   - Uses 384-dimensional embeddings (all-MiniLM-L6-v2)
   - Hybrid search: vector similarity + keyword matching
   - Returns top-K results with similarity scores
   - Sub-100ms query performance

2. **add_document_to_knowledge_base** - Add new knowledge
   - Processes documents with Docling
   - Extracts tables, images, and structure
   - Automatically chunks and indexes
   - Generates embeddings for vector search

3. **get_knowledge_base_statistics** - Get performance metrics
   - Total queries and documents
   - Cache hit rate and performance
   - Memory usage and system health

4. **check_knowledge_base_health** - Check system status
   - Neo4j connection status
   - Average response times
   - Cache efficiency
   - System availability

## How to Respond

**When answering questions**:
1. **ALWAYS search the knowledge base first** using `search_knowledge_base`
2. **Cite your sources** from the search results
3. **Show similarity scores** to indicate confidence
4. **Acknowledge limitations** if information isn't in the knowledge base
5. **Be accurate** - only use information from search results

**When information is found**:
- Synthesize information from top results
- Include source citations with scores
- Mention which documents the information came from

**When information is NOT found**:
- Clearly state "I couldn't find this in the knowledge base"
- Don't make up information
- Suggest related topics that ARE in the knowledge base
- Offer to add the information if the user provides it

**Performance expectations**:
- Queries typically return in <100ms
- Cache hit rate usually 30-50%
- High-quality results with semantic understanding

## Knowledge Base Contents

The knowledge base contains:
- Neo4j documentation and best practices
- Graph database concepts and patterns
- RAG system architecture and implementation
- BitNet.cpp and efficient AI deployment
- Azure integration guides
- Performance optimization techniques

## Your Personality

- **Helpful**: Provide clear, actionable information
- **Accurate**: Only use information from the knowledge base
- **Transparent**: Always cite sources and show confidence scores
- **Educational**: Explain concepts clearly when needed
- **Efficient**: Leverage the 417x performance to provide fast responses

Remember: You have access to an exceptionally fast knowledge base. Use it!
"""

# Tool definitions for Neo4j RAG
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the Neo4j knowledge base using vector + keyword hybrid search. Provides 417x faster retrieval with high accuracy. Returns relevant documents with similarity scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question or query to search for in the knowledge base"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-20). Default is 5.",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "use_llm": {
                        "type": "boolean",
                        "description": "Whether to use BitNet LLM for answer generation. Default is false (returns retrieved context only).",
                        "default": False
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_document_to_knowledge_base",
            "description": "Add a new document to the Neo4j knowledge base. The document will be processed with Docling (extracts tables, images, structure), chunked into 300-character segments with 50-char overlap, embedded with 384-dim vectors, and indexed for fast retrieval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The document content to add to the knowledge base"
                    },
                    "source": {
                        "type": "string",
                        "description": "Source identifier for the document (e.g., 'user_upload', 'web_scrape', 'documentation')",
                        "default": "user_upload"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional metadata (category, author, date, tags, etc.)",
                        "properties": {},
                        "additionalProperties": True
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_knowledge_base_statistics",
            "description": "Get comprehensive statistics about the Neo4j knowledge base including total queries, documents, chunks, cache hit rate, average response times, and memory usage. Useful for understanding system performance and health.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_knowledge_base_health",
            "description": "Check the health status and connectivity of the Neo4j RAG system. Returns status (healthy/unhealthy), Neo4j connection status, average response time, cache hit rate, and system availability. Use this to troubleshoot or verify the knowledge base is operational.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def configure_assistant():
    """Configure the Azure AI Assistant with Neo4j RAG tools"""

    print("🤖 Configuring Azure AI Assistant with Neo4j RAG")
    print("=" * 60)
    print(f"Assistant ID: {ASSISTANT_ID}")
    print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print("")

    try:
        # Initialize Azure OpenAI client
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )

        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=AZURE_OPENAI_API_VERSION
        )

        print("✅ Connected to Azure OpenAI")
        print("")

        # Update assistant configuration
        print("📝 Updating assistant configuration...")

        assistant = client.beta.assistants.update(
            assistant_id=ASSISTANT_ID,
            name="Neo4j RAG Assistant",
            instructions=ASSISTANT_INSTRUCTIONS,
            tools=TOOLS,
            model="gpt-4o-mini",
            metadata={
                "version": "1.0",
                "rag_system": "neo4j",
                "performance": "417x improvement",
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimensions": "384"
            }
        )

        print("✅ Assistant updated successfully!")
        print("")
        print("📊 Configuration Summary:")
        print(f"   Name: {assistant.name}")
        print(f"   Model: {assistant.model}")
        print(f"   Tools: {len(assistant.tools)} functions")
        print("")
        print("🔧 Tools Configured:")
        for i, tool in enumerate(assistant.tools, 1):
            if tool.type == 'function':
                print(f"   {i}. {tool.function.name}")
                print(f"      {tool.function.description[:60]}...")
        print("")
        print("=" * 60)
        print("✅ Configuration complete!")
        print("")
        print("🚀 Next Steps:")
        print("   1. Test the assistant in Azure AI Foundry playground")
        print("   2. Ask: 'What is Neo4j?'")
        print("   3. Verify it calls search_knowledge_base tool")
        print("   4. Check sources and similarity scores in response")
        print("")
        print("📚 Note: For tools to work, you need to:")
        print("   - Deploy the agent service as Container App")
        print("   - Or implement tool call handling in your application")
        print("   See: docs/AZURE_ASSISTANT_SETUP.md")

    except Exception as e:
        print(f"❌ Error configuring assistant: {e}")
        print("")
        print("Troubleshooting:")
        print("   - Ensure you're logged in: az login")
        print("   - Check AZURE_OPENAI_ENDPOINT is correct")
        print("   - Verify you have 'Cognitive Services OpenAI User' role")
        return False

    return True


if __name__ == "__main__":
    success = configure_assistant()
    exit(0 if success else 1)
