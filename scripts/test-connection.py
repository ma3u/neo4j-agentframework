#!/usr/bin/env python3
"""
Test Azure OpenAI connection and permissions
"""

import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Configuration
AZURE_OPENAI_ENDPOINT = "https://neo4j-rag-bitnet-ai.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2025-04-01-preview"

def test_connection():
    """Test the connection and permissions"""
    
    print(f"🔧 Testing Azure OpenAI Connection")
    print("=" * 50)
    print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"API Version: {AZURE_OPENAI_API_VERSION}")
    print("")
    
    try:
        # Initialize client
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        
        client = AzureOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            azure_ad_token_provider=token_provider,
            api_version=AZURE_OPENAI_API_VERSION
        )
        
        print("✅ Client initialized successfully")
        
        # Test 1: Try to list models
        print("\n🔍 Testing: List models...")
        try:
            models = client.models.list()
            print(f"✅ SUCCESS - Found {len(models.data)} models:")
            for model in models.data[:5]:  # Show first 5
                print(f"   - {model.id}")
        except Exception as e:
            print(f"❌ FAILED: {e}")
        
        # Test 2: Try to list assistants
        print("\n🔍 Testing: List assistants...")
        try:
            assistants = client.beta.assistants.list(limit=5)
            print(f"✅ SUCCESS - Found {len(assistants.data)} assistants:")
            for assistant in assistants.data:
                print(f"   - {assistant.id}: {assistant.name}")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            
        # Test 3: Try to create a simple chat completion
        print("\n🔍 Testing: Chat completion...")
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": "Say hello!"}],
                max_tokens=10
            )
            print(f"✅ SUCCESS: {response.choices[0].message.content}")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_connection()