"""
Microsoft Agent Framework integration for Neo4j RAG
"""

import logging
from typing import Dict, List, Optional, Any
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import Agent, AgentThread, ThreadMessage
import asyncio
import json

from src.neo4j_rag import Neo4jRAG, RAGQueryEngine
from azure.config import config

logger = logging.getLogger(__name__)


class Neo4jRAGAgent:
    """Microsoft Agent Framework wrapper for Neo4j RAG"""

    def __init__(self):
        """Initialize the agent with Azure AI services"""
        self.credential = DefaultAzureCredential()

        # Initialize AI Project Client
        self.ai_client = AIProjectClient(
            endpoint=config.ai_services_endpoint,
            credential=self.credential
        )

        # Initialize Neo4j RAG
        self.neo4j_rag = Neo4jRAG(
            uri=config.neo4j_uri,
            username=config.neo4j_user,
            password=config.neo4j_password
        )
        self.query_engine = RAGQueryEngine(self.neo4j_rag, use_llm=True)

        # Create the agent
        self.agent = self._create_agent()

        logger.info("Neo4j RAG Agent initialized successfully")

    def _create_agent(self) -> Agent:
        """Create and configure the Microsoft Agent"""

        agent_config = {
            "name": "Neo4j RAG Assistant",
            "instructions": """You are an intelligent assistant that helps users query and understand
            graph databases, particularly Neo4j. You have access to a comprehensive knowledge base
            about graph databases, Neo4j, and related technologies.

            Your capabilities include:
            1. Answering questions about graph database concepts
            2. Providing information about Neo4j features and best practices
            3. Explaining graph algorithms and their applications
            4. Helping with Cypher query syntax and optimization
            5. Discussing RAG (Retrieval-Augmented Generation) systems

            Always base your answers on the knowledge base and be accurate and helpful.""",

            "model": config.openai_deployment_name,

            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_knowledge_base",
                        "description": "Search the Neo4j knowledge base for relevant information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query"
                                },
                                "k": {
                                    "type": "integer",
                                    "description": "Number of results to retrieve",
                                    "default": 5
                                }
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_database_stats",
                        "description": "Get statistics about the knowledge base",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
            ]
        }

        try:
            agent = self.ai_client.agents.create(**agent_config)
            logger.info(f"Agent created with ID: {agent.id}")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise

    async def search_knowledge_base(self, query: str, k: int = 5) -> Dict:
        """Search the Neo4j knowledge base"""
        try:
            response = self.query_engine.query(query, k=k)

            # Format response for the agent
            formatted_response = {
                "answer": response.get("answer", ""),
                "sources": [
                    {
                        "text": source["text"],
                        "score": source["score"]
                    }
                    for source in response.get("sources", [])[:3]
                ],
                "query_time": response.get("query_time", 0),
                "results_found": response.get("results_found", 0)
            }

            return formatted_response
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"error": str(e)}

    async def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = self.neo4j_rag.get_stats()
            return {
                "documents": stats.get("documents", 0),
                "chunks": stats.get("chunks", 0),
                "embeddings": stats.get("embeddings", 0),
                "status": "connected"
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e), "status": "error"}

    async def process_message(self, message: str, thread_id: Optional[str] = None) -> Dict:
        """Process a message through the agent"""

        try:
            # Create or get thread
            if thread_id:
                thread = self.ai_client.agents.threads.get(thread_id)
            else:
                thread = self.ai_client.agents.threads.create()
                thread_id = thread.id

            # Add message to thread
            message = self.ai_client.agents.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # Run the agent
            run = self.ai_client.agents.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.agent.id
            )

            # Wait for completion
            while run.status in ["queued", "in_progress"]:
                await asyncio.sleep(1)
                run = self.ai_client.agents.threads.runs.get(
                    thread_id=thread_id,
                    run_id=run.id
                )

            # Handle tool calls
            if run.status == "requires_action":
                tool_outputs = []

                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.function.name == "search_knowledge_base":
                        args = json.loads(tool_call.function.arguments)
                        result = await self.search_knowledge_base(**args)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })
                    elif tool_call.function.name == "get_database_stats":
                        result = await self.get_database_stats()
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })

                # Submit tool outputs
                run = self.ai_client.agents.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

                # Wait for final completion
                while run.status in ["queued", "in_progress"]:
                    await asyncio.sleep(1)
                    run = self.ai_client.agents.threads.runs.get(
                        thread_id=thread_id,
                        run_id=run.id
                    )

            # Get the response
            messages = self.ai_client.agents.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1
            )

            if messages.data:
                response_content = messages.data[0].content

                # Extract text from content
                if isinstance(response_content, list):
                    text_content = " ".join([
                        item.text.value for item in response_content
                        if hasattr(item, 'text')
                    ])
                else:
                    text_content = str(response_content)

                return {
                    "success": True,
                    "response": text_content,
                    "thread_id": thread_id,
                    "run_id": run.id
                }
            else:
                return {
                    "success": False,
                    "error": "No response generated",
                    "thread_id": thread_id
                }

        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def close(self):
        """Clean up resources"""
        self.neo4j_rag.close()
        logger.info("Neo4j RAG Agent closed")


class AgentOrchestrator:
    """Orchestrator for managing multiple agent instances"""

    def __init__(self, num_agents: int = 3):
        """Initialize orchestrator with multiple agents for load balancing"""
        self.agents = []
        self.current_agent = 0

        for i in range(num_agents):
            agent = Neo4jRAGAgent()
            self.agents.append(agent)
            logger.info(f"Initialized agent {i+1}/{num_agents}")

        logger.info(f"Agent Orchestrator initialized with {num_agents} agents")

    async def process_message(self, message: str, thread_id: Optional[str] = None) -> Dict:
        """Process message using round-robin load balancing"""
        agent = self.agents[self.current_agent]
        self.current_agent = (self.current_agent + 1) % len(self.agents)

        return await agent.process_message(message, thread_id)

    async def get_stats(self) -> Dict:
        """Get aggregated statistics from all agents"""
        stats = await self.agents[0].get_database_stats()
        stats["agent_count"] = len(self.agents)
        stats["active_agent"] = self.current_agent
        return stats

    def close(self):
        """Close all agents"""
        for agent in self.agents:
            agent.close()


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_agent():
        """Test the agent functionality"""

        # Initialize agent
        agent = Neo4jRAGAgent()

        # Test questions
        questions = [
            "What is Neo4j?",
            "How many authors wrote about graph databases?",
            "What are the benefits of using a graph database?",
        ]

        for question in questions:
            print(f"\nQuestion: {question}")
            response = await agent.process_message(question)
            print(f"Response: {response.get('response', 'No response')[:500]}")

            if not response.get('success'):
                print(f"Error: {response.get('error')}")

        # Get stats
        stats = await agent.get_database_stats()
        print(f"\nDatabase Stats: {stats}")

        # Clean up
        agent.close()

    # Run the test
    asyncio.run(test_agent())