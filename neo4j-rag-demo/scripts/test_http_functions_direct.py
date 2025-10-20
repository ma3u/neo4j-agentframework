#!/usr/bin/env python3
"""
Test Azure OpenAI Assistant HTTP Functions by manually calling Azure RAG endpoints
This tests the HTTP function approach by simulating what the assistant should do
"""

import os
import sys
import time
import json
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("AZURE_AI_ASSISTANT_ID", "asst_LHQBXYvRhnbFo7KQ7IRbVXRR")
API_VERSION = "2024-05-01-preview"

# Azure RAG Service URL
AZURE_RAG_URL = "https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io"

def call_azure_rag_endpoint(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """
    Call Azure RAG service endpoint directly
    """
    url = f"{AZURE_RAG_URL}/{endpoint}"
    print(f"   📡 Calling: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        result = response.json()
        print(f"   ✅ Success: {str(result)[:100]}...")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ HTTP Error: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"error": str(e)}

def get_azure_openai_key():
    """Get Azure OpenAI API key from environment or Azure Key Vault"""
    key = os.getenv("AZURE_OPENAI_API_KEY")
    if key:
        return key

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
    except Exception as e:
        print(f"   ⚠️  Could not get API key from Azure CLI: {e}")

    return None

def main():
    """Test HTTP functions by calling Azure RAG endpoints directly"""
    
    print("=" * 80)
    print("AZURE RAG SERVICE - DIRECT HTTP ENDPOINT TEST")
    print("=" * 80)

    print(f"\n📋 Configuration:")
    print(f"   Azure RAG URL: {AZURE_RAG_URL}")
    print(f"   Assistant ID: {ASSISTANT_ID}")

    # Test 1: Direct HTTP endpoint calls
    print(f"\n🧪 Testing Direct HTTP Endpoints...")
    print("-" * 80)

    test_cases = [
        {
            "name": "Health Check",
            "endpoint": "check_knowledge_base_health",
            "method": "GET",
            "data": None
        },
        {
            "name": "Knowledge Base Statistics", 
            "endpoint": "get_knowledge_base_statistics",
            "method": "GET",
            "data": None
        },
        {
            "name": "Search Knowledge Base",
            "endpoint": "search_knowledge_base", 
            "method": "POST",
            "data": {"question": "What is Neo4j?", "max_results": 3}
        }
    ]

    successful_direct = 0
    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/3] 🔍 {test['name']}:")
        result = call_azure_rag_endpoint(test['endpoint'], test['method'], test['data'])
        if "error" not in result:
            successful_direct += 1

    # Test 2: Azure OpenAI Assistant with simulated HTTP function handling
    print(f"\n🤖 Testing Azure OpenAI Assistant (with manual HTTP handling)...")
    print("-" * 80)

    # Get API key
    api_key = get_azure_openai_key()
    if not api_key:
        print("❌ Could not get Azure OpenAI API key")
        return False

    # Initialize client
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    except Exception as e:
        print(f"❌ Failed to initialize Azure OpenAI client: {e}")
        return False

    # Get assistant
    try:
        assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
        print(f"   ✅ Assistant: {assistant.name}")
        print(f"      Functions: {len(assistant.tools)}")
    except Exception as e:
        print(f"❌ Failed to get assistant: {e}")
        return False

    # Test with a simple query to see function call behavior
    test_query = "How many documents are in the knowledge base?"
    print(f"\n🔍 Testing Query: '{test_query}'")

    try:
        # Create new thread
        thread = client.beta.threads.create()
        print(f"   ✅ Thread created: {thread.id}")

        # Add message
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=test_query
        )

        # Run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        
        print(f"   🤔 Processing... (Run ID: {run.id})")
        
        # Monitor for function calls
        timeout = 30
        start_time = time.time()
        function_calls_detected = []
        
        while run.status in ["queued", "in_progress", "requires_action"] and (time.time() - start_time) < timeout:
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            
            if run.status == "requires_action":
                print(f"   🔧 Function calls required!")
                
                # Handle function calls manually (simulating what should happen automatically)
                if run.required_action and run.required_action.submit_tool_outputs:
                    tool_outputs = []
                    
                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        func_name = tool_call.function.name
                        func_args = json.loads(tool_call.function.arguments)
                        
                        print(f"      📞 Function: {func_name}")
                        print(f"         Args: {func_args}")
                        
                        function_calls_detected.append(func_name)
                        
                        # Manually call the corresponding HTTP endpoint
                        if func_name == "search_knowledge_base":
                            result = call_azure_rag_endpoint("search_knowledge_base", "POST", func_args)
                        elif func_name == "get_knowledge_base_statistics":
                            result = call_azure_rag_endpoint("get_knowledge_base_statistics", "GET")
                        elif func_name == "check_knowledge_base_health":
                            result = call_azure_rag_endpoint("check_knowledge_base_health", "GET")
                        else:
                            result = {"error": f"Unknown function: {func_name}"}
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })
                    
                    # Submit results
                    print(f"   📤 Submitting {len(tool_outputs)} function results...")
                    run = client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    
        # Get final response
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread.id, limit=1)
            response = messages.data[0].content[0].text.value
            
            print(f"   🤖 Assistant Response:")
            print(f"      {response[:200]}...")
            print(f"\n   📊 Functions Called: {', '.join(function_calls_detected)}")
            print(f"   ⏱️  Status: {run.status}")
            
            assistant_success = True
        else:
            print(f"   ❌ Final Status: {run.status}")
            if run.last_error:
                print(f"   Error: {run.last_error}")
            assistant_success = False
            
    except Exception as e:
        print(f"   ❌ Assistant test failed: {e}")
        assistant_success = False

    # Summary
    print("\n" + "=" * 80)
    print("HTTP FUNCTION TEST RESULTS")
    print("=" * 80)
    print(f"Direct HTTP Calls: {successful_direct}/3 ✅")
    print(f"Assistant Integration: {'✅' if assistant_success else '❌'}")
    
    if successful_direct == 3 and assistant_success:
        print("\n🎉 All tests passed!")
        print("\n✅ Your setup is working:")
        print("   - Azure RAG service endpoints are accessible")
        print("   - Azure OpenAI Assistant can be configured with functions")  
        print("   - Function calls can be handled manually")
        print(f"\n📝 Note: Azure OpenAI may not automatically handle HTTP functions.")
        print("   Consider using the local execution approach with HTTP client calls.")
        
        return True
    else:
        print(f"\n⚠️  Issues detected:")
        if successful_direct < 3:
            print("   - Some Azure RAG endpoints are not responding correctly")
        if not assistant_success:
            print("   - Assistant function integration needs troubleshooting")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)