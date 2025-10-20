#!/usr/bin/env python3
"""
Test Azure OpenAI Assistant with Function Calling Handler
Handles function execution and submits results back to Azure OpenAI
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

# RAG Service URL (local or Azure)
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io")

def call_rag_function(function_name: str, arguments: dict) -> dict:
    """
    Call the actual RAG service to execute the function

    Args:
        function_name: Name of the function to call
        arguments: Function arguments as dict

    Returns:
        Function result as dict
    """
    print(f"      📡 Calling RAG service: {function_name}")

    try:
        if function_name == "search_knowledge_base":
            # Call /query endpoint
            response = requests.post(
                f"{RAG_SERVICE_URL}/query",
                json={
                    "question": arguments.get("question", ""),
                    "k": arguments.get("max_results", 5)
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        elif function_name == "get_knowledge_base_statistics":
            # Call /stats endpoint
            response = requests.get(f"{RAG_SERVICE_URL}/stats", timeout=10)
            response.raise_for_status()
            return response.json()

        elif function_name == "check_knowledge_base_health":
            # Call /health endpoint
            response = requests.get(f"{RAG_SERVICE_URL}/health", timeout=10)
            response.raise_for_status()
            return response.json()

        elif function_name == "add_document_to_knowledge_base":
            # This would call a document upload endpoint (not implemented in simple API)
            return {"status": "not_implemented", "message": "Document upload via API not available in current simple API"}

        else:
            return {"error": f"Unknown function: {function_name}"}

    except requests.exceptions.RequestException as e:
        print(f"      ❌ RAG service error: {e}")
        return {"error": str(e), "service_url": RAG_SERVICE_URL}
    except Exception as e:
        print(f"      ❌ Function execution error: {e}")
        return {"error": str(e)}

def main():
    """Test Azure OpenAI Assistant with function execution"""

    print("="*80)
    print("AZURE OPENAI + NEO4J RAG - INTEGRATION TEST WITH FUNCTION EXECUTION")
    print("="*80)

    # Validate configuration
    if not AZURE_OPENAI_ENDPOINT:
        print("❌ AZURE_AI_PROJECT_ENDPOINT not set in .env")
        sys.exit(1)

    if not AZURE_OPENAI_API_KEY:
        print("❌ AZURE_OPENAI_API_KEY not set in .env")
        sys.exit(1)

    print(f"\n📋 Configuration:")
    print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"   Assistant ID: {ASSISTANT_ID}")
    print(f"   RAG Service: {RAG_SERVICE_URL}")

    # Verify RAG service is accessible
    print(f"\n🔍 Verifying RAG service...")
    try:
        health = requests.get(f"{RAG_SERVICE_URL}/health", timeout=5)
        health_data = health.json()
        print(f"   ✅ RAG service is healthy")
        print(f"      Mode: {health_data.get('mode')}")
        print(f"      Documents: {health_data.get('stats', {}).get('documents')}")
        print(f"      Chunks: {health_data.get('stats', {}).get('chunks')}")
    except Exception as e:
        print(f"   ❌ RAG service not accessible: {e}")
        print(f"   Start it with:")
        print(f"   docker run -d -p 8000:8000 ... rag-aura-service:v2.0")
        sys.exit(1)

    # Initialize Azure OpenAI client
    print(f"\n🔗 Connecting to Azure OpenAI...")
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
    print("   ✅ Client initialized")

    # Get assistant
    print(f"\n🤖 Fetching assistant...")
    assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
    print(f"   ✅ Assistant: {assistant.name}")
    print(f"      Model: {assistant.model}")
    print(f"      Functions: {len(assistant.tools)}")

    # Test queries
    test_messages = [
        "What is Neo4j?",
        "How many documents are in the knowledge base?",
        "Is the system healthy?"
    ]

    print(f"\n🧪 Running {len(test_messages)} test queries with function execution...")
    print("="*80)

    successful = 0

    for i, message in enumerate(test_messages, 1):
        print(f"\n[{i}/{len(test_messages)}] 👤 User: {message}")
        print("-" * 80)

        try:
            # Create new thread for each query (to avoid active run conflicts)
            thread = client.beta.threads.create()

            # Add message
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message
            )

            # Run assistant
            print("   🤔 Processing...")
            start_time = time.time()

            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID
            )

            # Poll for completion and handle function calls
            timeout = 60
            run_start = time.time()
            tool_calls_made = []

            while run.status in ["queued", "in_progress", "requires_action"]:
                if (time.time() - run_start) > timeout:
                    print(f"   ⏱️  Timeout after {timeout}s")
                    break

                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

                # Handle function calls
                if run.status == "requires_action":
                    print(f"   🔧 Function call required...")

                    tool_outputs = []

                    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        print(f"   🔧 Executing: {function_name}")
                        print(f"      Arguments: {function_args}")

                        # Call the actual RAG service
                        result = call_rag_function(function_name, function_args)

                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)
                        })

                        tool_calls_made.append(function_name)
                        print(f"      ✅ Result: {str(result)[:100]}...")

                    # Submit tool outputs
                    print(f"   📤 Submitting function results...")
                    run = client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    print(f"   ✅ Results submitted, waiting for response...\n")
                    # Immediately retrieve the run object to get its latest status after submission
                    run = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )

            response_time = (time.time() - start_time) * 1000

            # Get response
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id, limit=1)
                latest_message = messages.data[0]

                answer = ""
                for content in latest_message.content:
                    if hasattr(content, 'text'):
                        answer += content.text.value

                print(f"   🤖 Assistant: {answer[:300]}...")
                if len(answer) > 300:
                    print(f"      ... (total {len(answer)} chars)")

                print(f"\n   📊 Metadata:")
                print(f"      Response Time: {response_time:.1f}ms ({response_time/1000:.1f}s)")
                print(f"      Functions Used: {', '.join(tool_calls_made)}")
                print(f"      Status: ✅ {run.status}")

                successful += 1
            else:
                print(f"   ❌ Final Status: {run.status}")
                if hasattr(run, 'last_error') and run.last_error:
                    print(f"   Error: {run.last_error}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Summary
    print("\n" + "="*80)
    print("INTEGRATION TEST SUMMARY")
    print("="*80)
    print(f"Total Queries: {len(test_messages)}")
    print(f"Successful: {successful} ✅")
    print(f"Failed: {len(test_messages) - successful} ❌")
    print(f"Success Rate: {(successful/len(test_messages)*100):.1f}%")
    print("="*80)

    if successful == len(test_messages):
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Azure OpenAI Assistant successfully:")
        print("   - Connected to Azure OpenAI endpoint")
        print("   - Called Neo4j RAG functions")
        print("   - Retrieved data from local RAG service")
        print("   - Generated intelligent responses with function results")
        print("\n📊 Integration Status: FULLY OPERATIONAL")
    else:
        print(f"\n⚠️  {len(test_messages) - successful} test(s) failed")
        print("\n💡 Next steps:")
        print("   1. Verify RAG service is running: curl http://localhost:8000/health")
        print("   2. Check function configuration in Azure OpenAI Studio")
        print("   3. Configure functions as HTTP endpoints (OpenAPI spec)")

    return successful == len(test_messages)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
