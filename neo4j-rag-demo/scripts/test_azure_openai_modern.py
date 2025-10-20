#!/usr/bin/env python3
"""
Modern Azure OpenAI Function Calling using Chat Completions API (New Recommended Approach)
Replaces the deprecated Assistants API with the current best practice
"""

import os
import sys
import json
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"  # Your deployed model
API_VERSION = "2024-06-01"

# Azure RAG Service URL
AZURE_RAG_URL = "https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io"

# Function definitions for Chat Completions API
FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the knowledge base for relevant information about a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The search query or question to find relevant information"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_knowledge_base_statistics",
            "description": "Get statistics about the knowledge base (document count, chunks, etc.)",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_knowledge_base_health",
            "description": "Check the health and status of the knowledge base system",
            "parameters": {
                "type": "object", 
                "properties": {}
            }
        }
    }
]

def call_azure_rag_function(function_name: str, arguments: dict) -> dict:
    """
    Execute function by calling Azure RAG service endpoint
    """
    print(f"      📡 Calling Azure RAG: {function_name}")
    
    try:
        if function_name == "search_knowledge_base":
            response = requests.post(
                f"{AZURE_RAG_URL}/search_knowledge_base",
                json={
                    "question": arguments.get("question", ""),
                    "max_results": arguments.get("max_results", 5)
                },
                timeout=30
            )
        elif function_name == "get_knowledge_base_statistics":
            response = requests.get(f"{AZURE_RAG_URL}/get_knowledge_base_statistics", timeout=10)
        elif function_name == "check_knowledge_base_health":
            response = requests.get(f"{AZURE_RAG_URL}/check_knowledge_base_health", timeout=10)
        else:
            return {"error": f"Unknown function: {function_name}"}
            
        response.raise_for_status()
        result = response.json()
        print(f"      ✅ Success: {str(result)[:100]}...")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"      ❌ HTTP Error: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return {"error": str(e)}

def get_azure_openai_key():
    """Get Azure OpenAI API key"""
    key = os.getenv("AZURE_OPENAI_API_KEY")
    if key:
        return key
        
    # Try Azure CLI fallback
    try:
        import subprocess
        result = subprocess.run(
            ["az", "cognitiveservices", "account", "keys", "list",
             "--name", "neo4j-rag-bitnet-ai",
             "--resource-group", "rg-neo4j-rag-bitnet", 
             "--query", "key1", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
        
    return None

def chat_with_functions(client: AzureOpenAI, messages: list, max_iterations: int = 5):
    """
    Modern function calling using Chat Completions API
    """
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n   🔄 Iteration {iteration}")
        
        # Make chat completion request with function definitions
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=FUNCTIONS,
                tool_choice="auto"  # Let model decide when to use functions
            )
            
            message = response.choices[0].message
            messages.append(message)
            
            # Check if function calls are needed
            if message.tool_calls:
                print(f"   🔧 Function calls required: {len(message.tool_calls)}")
                
                # Execute each function call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"      📞 {function_name}({function_args})")
                    
                    # Call the actual function
                    result = call_azure_rag_function(function_name, function_args)
                    
                    # Add function result to messages
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(result)
                    })
                
                # Continue to get final response
                continue
            else:
                # No more function calls needed
                print(f"   ✅ Final response ready")
                return message.content, messages
                
        except Exception as e:
            print(f"   ❌ Chat completion error: {e}")
            return None, messages
    
    print(f"   ⚠️  Reached max iterations ({max_iterations})")
    return "Sorry, I reached the maximum number of function calls.", messages

def main():
    """Test modern Azure OpenAI function calling"""
    
    print("=" * 80)
    print("AZURE OPENAI - MODERN FUNCTION CALLING (CHAT COMPLETIONS API)")
    print("=" * 80)
    
    # Configuration
    if not AZURE_OPENAI_ENDPOINT:
        print("❌ AZURE_AI_PROJECT_ENDPOINT not set")
        sys.exit(1)
        
    print(f"\n📋 Configuration:")
    print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"   Model: {MODEL_NAME}")
    print(f"   API Version: {API_VERSION}")
    print(f"   Azure RAG: {AZURE_RAG_URL}")
    
    # Get API key
    api_key = get_azure_openai_key()
    if not api_key:
        print("❌ Could not get API key")
        sys.exit(1)
    print("   ✅ API key retrieved")
    
    # Initialize client
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        print("   ✅ Client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    # Test queries
    test_queries = [
        "What is Neo4j?",
        "How many documents are in the knowledge base?",
        "Is the system healthy?"
    ]
    
    print(f"\n🧪 Testing {len(test_queries)} queries...")
    print("=" * 80)
    
    successful = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] 👤 Query: {query}")
        print("-" * 60)
        
        # Create conversation with system message
        messages = [
            {
                "role": "system",
                "content": """You are a Neo4j RAG Assistant with access to a comprehensive knowledge base.

When users ask questions:
1. Use search_knowledge_base() to find relevant information
2. Use get_knowledge_base_statistics() for database info
3. Use check_knowledge_base_health() for system status

Always provide helpful, accurate responses based on the function results."""
            },
            {
                "role": "user", 
                "content": query
            }
        ]
        
        try:
            # Get response with function calling
            import time
            start_time = time.time()
            
            response, final_messages = chat_with_functions(client, messages)
            
            response_time = (time.time() - start_time) * 1000
            
            if response:
                print(f"\n   🤖 Assistant: {response[:200]}...")
                if len(response) > 200:
                    print(f"      ... (total {len(response)} chars)")
                    
                print(f"\n   📊 Metadata:")
                print(f"      Response Time: {response_time:.1f}ms")
                print(f"      Total Messages: {len(final_messages)}")
                print(f"      Function Calls: {len([m for m in final_messages if m.get('role') == 'tool'])}")
                
                successful += 1
            else:
                print(f"   ❌ No response received")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("MODERN FUNCTION CALLING TEST RESULTS")
    print("=" * 80)
    print(f"Successful: {successful}/{len(test_queries)} ✅")
    print(f"Success Rate: {(successful/len(test_queries)*100):.1f}%")
    
    if successful == len(test_queries):
        print("\n🎉 All tests passed!")
        print("\n✅ Modern Azure OpenAI function calling is working:")
        print("   - Chat Completions API with function calling")
        print("   - Direct HTTP calls to Azure RAG service")
        print("   - No deprecated APIs used")
        print("\n📝 This is the recommended approach going forward.")
    else:
        print(f"\n⚠️  {len(test_queries) - successful} test(s) failed")
    
    return successful == len(test_queries)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)