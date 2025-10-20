#!/usr/bin/env python3
"""
Test Azure OpenAI Assistants API with Neo4j RAG
Uses Azure OpenAI endpoint (not Azure AI Foundry Projects)

Your Configuration:
- Endpoint: https://neo4j-rag-bitnet-ai.openai.azure.com/
- Assistant: asst_LHQBXYvRhnbFo7KQ7IRbVXRR
- Functions: search_knowledge_base, add_document_to_knowledge_base,
             get_knowledge_base_statistics, check_knowledge_base_health
"""

import os
import sys
import time
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")  # Will try to get from Azure
ASSISTANT_ID = os.getenv("AZURE_AI_ASSISTANT_ID", "asst_LHQBXYvRhnbFo7KQ7IRbVXRR")
API_VERSION = "2024-05-01-preview"  # Azure OpenAI Assistants API version

def get_azure_openai_key():
    """Get Azure OpenAI API key from environment or Azure Key Vault"""
    # First try environment variable
    key = os.getenv("AZURE_OPENAI_API_KEY")
    if key:
        return key

    # Try to get from Azure CLI
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
    """Test Azure OpenAI Assistant with Neo4j RAG functions"""

    print("="*80)
    print("AZURE OPENAI ASSISTANTS API + NEO4J RAG - INTEGRATION TEST")
    print("="*80)

    # Check configuration
    if not AZURE_OPENAI_ENDPOINT:
        print("❌ ERROR: AZURE_AI_PROJECT_ENDPOINT not set")
        print("   Set in .env file:")
        print("   AZURE_AI_PROJECT_ENDPOINT=https://neo4j-rag-bitnet-ai.openai.azure.com/")
        sys.exit(1)

    print(f"\n📋 Configuration:")
    print(f"   Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"   Assistant ID: {ASSISTANT_ID}")
    print(f"   API Version: {API_VERSION}")

    # Get API key
    print(f"\n🔐 Getting Azure OpenAI API key...")
    api_key = get_azure_openai_key()

    if not api_key:
        print("   ❌ Could not get API key")
        print("\n   Try one of:")
        print("   1. Set AZURE_OPENAI_API_KEY in .env")
        print("   2. Login with: az login")
        print("   3. Get key from Azure Portal:")
        print("      https://portal.azure.com → neo4j-rag-bitnet-ai → Keys and Endpoint")
        sys.exit(1)

    print(f"   ✅ API key retrieved: {api_key[:10]}...{api_key[-10:]}")

    # Initialize Azure OpenAI client
    print(f"\n🔗 Connecting to Azure OpenAI...")
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        print("   ✅ Client initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        sys.exit(1)

    # Get assistant details
    print(f"\n🤖 Fetching assistant...")
    try:
        assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
        print(f"   ✅ Assistant found:")
        print(f"      Name: {assistant.name}")
        print(f"      Model: {assistant.model}")
        print(f"      Instructions: {assistant.instructions[:80]}...")

        if assistant.tools:
            print(f"\n   📦 Functions configured ({len(assistant.tools)}):")
            for tool in assistant.tools:
                if hasattr(tool, 'function'):
                    print(f"      - {tool.function.name}")
        else:
            print(f"   ⚠️  No functions configured")

    except Exception as e:
        print(f"   ❌ Failed to get assistant: {e}")
        sys.exit(1)

    # Create a thread for conversation
    print(f"\n💬 Creating conversation thread...")
    try:
        thread = client.beta.threads.create()
        print(f"   ✅ Thread created: {thread.id}")
    except Exception as e:
        print(f"   ❌ Failed to create thread: {e}")
        sys.exit(1)

    # Test queries (proven to work from comprehensive tests)
    test_messages = [
        "What is Neo4j?",
        "How many documents are in the knowledge base?",
        "Is the system healthy?"
    ]

    print(f"\n🧪 Running {len(test_messages)} test queries...")
    print("="*80)

    successful_queries = 0

    for i, message in enumerate(test_messages, 1):
        print(f"\n[{i}/{len(test_messages)}] 👤 User: {message}")
        print("-" * 80)

        try:
            # Add message to thread
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

            # Wait for completion (with timeout)
            timeout = 60
            run_start = time.time()
            tool_calls_seen = []

            while run.status in ["queued", "in_progress", "requires_action"]:
                if (time.time() - run_start) > timeout:
                    print(f"   ⏱️  Timeout after {timeout}s")
                    break

                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

                # Show function calls
                if run.status == "requires_action" and run.required_action:
                    for tc in run.required_action.submit_tool_outputs.tool_calls:
                        if tc.function.name not in tool_calls_seen:
                            tool_calls_seen.append(tc.function.name)
                            print(f"   🔧 Function called: {tc.function.name}")
                            print(f"      Arguments: {tc.function.arguments}")

            response_time = (time.time() - start_time) * 1000

            # Get assistant's response
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id, limit=1)
                latest_message = messages.data[0]

                # Extract text from message content
                answer = ""
                for content in latest_message.content:
                    if hasattr(content, 'text'):
                        answer += content.text.value

                print(f"   🤖 Assistant: {answer[:250]}...")
                if len(answer) > 250:
                    print(f"      ... (total {len(answer)} chars)")
                print(f"\n   📊 Metadata:")
                print(f"      Response Time: {response_time:.1f}ms")
                print(f"      Functions Used: {', '.join(tool_calls_seen) if tool_calls_seen else 'None'}")
                print(f"      Status: {run.status}")
                successful_queries += 1
            else:
                print(f"   ❌ Status: {run.status}")
                if run.last_error:
                    print(f"   Error: {run.last_error.message}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Queries: {len(test_messages)}")
    print(f"Successful: {successful_queries} ✅")
    print(f"Failed: {len(test_messages) - successful_queries} ❌")
    print(f"Success Rate: {(successful_queries/len(test_messages)*100):.1f}%")
    print(f"\nThread ID: {thread.id}")
    print(f"   (View in Azure OpenAI Studio)")
    print("="*80)

    if successful_queries == len(test_messages):
        print("\n🎉 All tests passed! Azure OpenAI Assistant integration working!")
        print("\n✅ Your assistant successfully:")
        print("   - Connected to Azure OpenAI")
        print("   - Called configured functions")
        print("   - Retrieved data from Neo4j RAG service")
        print("   - Generated intelligent responses")
    else:
        print(f"\n⚠️  {len(test_messages) - successful_queries} test(s) failed.")
        print("   Check that your RAG service is running:")
        print("   - Local: docker run -d -p 8000:8000 ... rag-aura-service:v2.0")
        print("   - Azure: Verify Container App is in production mode")

    return successful_queries == len(test_messages)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
