#!/usr/bin/env python3
"""
Enhanced Neo4j RAG Assistant Integration Test

This script demonstrates the complete integration between:
1. Azure OpenAI Assistant (GPT-4o-mini)
2. Container Apps RAG API
3. Function calling workflow

It simulates exactly what happens in Azure AI Foundry when using the assistant.
"""

import os
import json
import time
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
CONTAINER_APP_URL = "https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io"

def initialize_client():
    """Initialize Azure OpenAI client"""
    print("🔧 Initializing Azure OpenAI client...")
    
    if not all([AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, ASSISTANT_ID]):
        print("❌ Missing required environment variables:")
        print(f"   AZURE_OPENAI_ENDPOINT: {'✅' if AZURE_OPENAI_ENDPOINT else '❌'}")
        print(f"   AZURE_OPENAI_API_KEY: {'✅' if AZURE_OPENAI_API_KEY else '❌'}")
        print(f"   ASSISTANT_ID: {'✅' if ASSISTANT_ID else '❌'}")
        return None
    
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-05-01-preview"
    )
    
    print("✅ Azure OpenAI client initialized")
    return client

def test_container_app_health():
    """Test Container Apps API health"""
    print("🏥 Testing Container Apps health...")
    
    try:
        response = requests.get(f"{CONTAINER_APP_URL}/health", timeout=10)
        response.raise_for_status()
        health_data = response.json()
        
        print(f"✅ Container Apps Status: {health_data['status']}")
        print(f"   Service: {health_data['service']} v{health_data['version']}")
        print(f"   Mode: {health_data['mode']}")
        return True
        
    except Exception as e:
        print(f"❌ Container Apps health check failed: {e}")
        return False

def call_container_function(function_name, arguments):
    """Call Container Apps function and return result"""
    print(f"🔧 Calling Container Apps function: {function_name}")
    print(f"   Arguments: {json.dumps(arguments, indent=2)}")
    
    try:
        if function_name == "search_knowledge_base":
            url = f"{CONTAINER_APP_URL}/search_knowledge_base"
            response = requests.post(url, json=arguments, timeout=30)
            
        elif function_name == "get_knowledge_base_statistics":
            url = f"{CONTAINER_APP_URL}/get_knowledge_base_statistics"
            response = requests.get(url, timeout=10)
            
        else:
            return {"error": f"Unknown function: {function_name}"}
        
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Function call successful")
        print(f"   Response size: {len(str(result))} characters")
        
        return result
        
    except Exception as e:
        error_result = {"error": f"Function call failed: {str(e)}"}
        print(f"❌ Function call failed: {e}")
        return error_result

def run_assistant_conversation(client, question):
    """Run a complete assistant conversation with function calling"""
    print(f"\n🤖 Starting assistant conversation")
    print(f"   Question: '{question}'")
    print("=" * 60)
    
    try:
        # Create a thread
        thread = client.beta.threads.create()
        print(f"📝 Created thread: {thread.id}")
        
        # Add user message
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )
        print(f"💬 Added user message")
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )
        print(f"🏃 Started assistant run: {run.id}")
        
        # Wait for completion and handle function calls
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # Check run status
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            print(f"📊 Run status: {run.status}")
            
            if run.status == "requires_action":
                # Handle function calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                print(f"🔧 Processing {len(tool_calls)} function call(s)")
                
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    print(f"\n🔍 Function Call Details:")
                    print(f"   ID: {tool_call.id}")
                    print(f"   Function: {function_name}")
                    print(f"   Arguments: {json.dumps(arguments, indent=4)}")
                    
                    # Call our Container Apps function
                    result = call_container_function(function_name, arguments)
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": json.dumps(result)
                    })
                    
                    print(f"📤 Function result:")
                    print(f"   {json.dumps(result, indent=4)}")
                
                # Submit function outputs
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                print(f"✅ Submitted {len(tool_outputs)} function output(s)")
                
            elif run.status == "completed":
                print("🎉 Assistant run completed!")
                break
                
            elif run.status in ["failed", "cancelled", "expired"]:
                print(f"❌ Assistant run {run.status}")
                if run.last_error:
                    print(f"   Error: {run.last_error}")
                return None
                
            else:
                print(f"⏳ Waiting for assistant... (status: {run.status})")
                time.sleep(2)
        
        # Get the final response
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="desc",
            limit=1
        )
        
        if messages.data:
            assistant_message = messages.data[0]
            if assistant_message.role == "assistant":
                response_text = ""
                for content in assistant_message.content:
                    if content.type == "text":
                        response_text += content.text.value
                
                print(f"\n🎯 Final Assistant Response:")
                print("=" * 60)
                print(response_text)
                print("=" * 60)
                
                return response_text
        
        print("❌ No assistant response found")
        return None
        
    except Exception as e:
        print(f"❌ Assistant conversation failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Neo4j RAG Assistant Integration Test")
    print("=" * 60)
    
    # Test Container Apps health
    if not test_container_app_health():
        print("❌ Container Apps not available, exiting")
        return
    
    # Initialize OpenAI client
    client = initialize_client()
    if not client:
        print("❌ OpenAI client initialization failed, exiting")
        return
    
    # Test questions
    test_questions = [
        "What is Neo4j and how does it work?",
        "Get knowledge base statistics",
        "Tell me about graph databases and their advantages",
        "How many documents are in the knowledge base?"
    ]
    
    print(f"\n📋 Running {len(test_questions)} test conversations...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n" + "=" * 80)
        print(f"TEST {i}/{len(test_questions)}")
        print("=" * 80)
        
        response = run_assistant_conversation(client, question)
        
        if response:
            print(f"✅ Test {i} completed successfully")
        else:
            print(f"❌ Test {i} failed")
        
        # Wait between tests
        if i < len(test_questions):
            print("\n⏳ Waiting 3 seconds before next test...")
            time.sleep(3)
    
    print("\n" + "=" * 80)
    print("🏁 All tests completed!")
    print("=" * 80)

if __name__ == "__main__":
    main()