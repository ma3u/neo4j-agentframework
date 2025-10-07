#!/usr/bin/env python3
"""
Test Azure OpenAI Assistant Integration with Container Apps
This script demonstrates how to properly handle function calls from the assistant
"""

import os
import json
import asyncio
import aiohttp
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Configuration
ASSISTANT_ID = "asst_LHQBXYvRhnbFo7KQ7IRbVXRR"
AZURE_OPENAI_ENDPOINT = "https://neo4j-rag-bitnet-ai.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-10-01-preview"
CONTAINER_APP_BASE_URL = "https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io"

class AssistantHandler:
    def __init__(self):
        """Initialize the assistant handler"""
        # Initialize Azure OpenAI client
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        
        self.client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=AZURE_OPENAI_API_VERSION
        )

    async def handle_function_call(self, function_name: str, arguments: dict) -> dict:
        """Route function calls to Container Apps"""
        
        print(f"🔧 Handling function call: {function_name}")
        print(f"📋 Arguments: {arguments}")
        
        async with aiohttp.ClientSession() as session:
            try:
                if function_name == "search_knowledge_base":
                    async with session.post(
                        f"{CONTAINER_APP_BASE_URL}/search_knowledge_base",
                        json={
                            "question": arguments.get("question", ""),
                            "max_results": arguments.get("max_results", 5),
                            "use_llm": arguments.get("use_llm", False)
                        }
                    ) as response:
                        result = await response.json()
                        print(f"✅ Search result: {len(result.get('sources', []))} sources found")
                        return result
                
                elif function_name == "add_document_to_knowledge_base":
                    async with session.post(
                        f"{CONTAINER_APP_BASE_URL}/add_document_to_knowledge_base",
                        json={
                            "content": arguments.get("content", ""),
                            "source": arguments.get("source", "user_upload"),
                            "metadata": arguments.get("metadata", {})
                        }
                    ) as response:
                        result = await response.json()
                        print(f"✅ Document added: {result.get('message', 'Success')}")
                        return result
                
                elif function_name == "get_knowledge_base_statistics":
                    async with session.get(
                        f"{CONTAINER_APP_BASE_URL}/get_knowledge_base_statistics"
                    ) as response:
                        result = await response.json()
                        print(f"✅ Statistics: {result.get('total_documents', 0)} docs, {result.get('total_chunks', 0)} chunks")
                        return result
                
                elif function_name == "check_knowledge_base_health":
                    async with session.get(
                        f"{CONTAINER_APP_BASE_URL}/check_knowledge_base_health"
                    ) as response:
                        result = await response.json()
                        print(f"✅ Health check: {result.get('status', 'unknown')}")
                        return result
                
                else:
                    return {"error": f"Unknown function: {function_name}"}
                    
            except Exception as e:
                error_msg = f"Error calling {function_name}: {str(e)}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}

    async def chat_with_assistant(self, message: str) -> str:
        """Send a message to the assistant and handle function calls"""
        
        print(f"\n💬 User: {message}")
        print("🤖 Assistant: Processing...")
        
        try:
            # Create a thread
            thread = self.client.beta.threads.create()
            
            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID
            )
            
            # Wait for completion and handle function calls
            while run.status in ["queued", "in_progress", "requires_action"]:
                if run.status == "requires_action":
                    print("🔧 Assistant is calling functions...")
                    
                    # Handle tool calls
                    tool_outputs = []
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        # Call our Container Apps
                        result = await self.handle_function_call(function_name, arguments)
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })
                    
                    # Submit tool outputs
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                
                # Wait a bit before checking again
                await asyncio.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            # Get the response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id,
                order="desc",
                limit=1
            )
            
            if messages.data:
                response_content = messages.data[0].content
                if isinstance(response_content, list):
                    text_content = " ".join([
                        item.text.value for item in response_content
                        if hasattr(item, 'text')
                    ])
                else:
                    text_content = str(response_content)
                
                print(f"🤖 Assistant: {text_content}")
                return text_content
            else:
                return "No response generated"
                
        except Exception as e:
            error_msg = f"Error in conversation: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

async def test_assistant():
    """Test the assistant with various queries"""
    
    print("🚀 Testing Azure OpenAI Assistant Integration")
    print("=" * 60)
    print(f"Assistant ID: {ASSISTANT_ID}")
    print(f"Container Apps: {CONTAINER_APP_BASE_URL}")
    print("")
    
    handler = AssistantHandler()
    
    # Test queries
    test_queries = [
        "What is Neo4j?",
        "Check the knowledge base health",
        "Get knowledge base statistics", 
        "How many documents are in the knowledge base?"
    ]
    
    for query in test_queries:
        print("\n" + "="*60)
        response = await handler.chat_with_assistant(query)
        print("")

if __name__ == "__main__":
    asyncio.run(test_assistant())