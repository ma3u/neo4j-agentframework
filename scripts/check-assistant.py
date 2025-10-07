#!/usr/bin/env python3
"""
Check current assistant configuration
"""

import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Configuration
ASSISTANT_ID = "asst_LHQBXYvRhnbFo7KQ7IRbVXRR"
AZURE_OPENAI_ENDPOINT = "https://neo4j-rag-bitnet-ai.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2025-04-01-preview"

def check_assistant():
    """Check the current assistant configuration"""
    
    print(f"🔍 Checking Assistant Configuration")
    print("=" * 50)
    print(f"Assistant ID: {ASSISTANT_ID}")
    print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")
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
        
        # Get assistant details
        assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
        
        print("✅ Assistant Details:")
        print(f"   ID: {assistant.id}")
        print(f"   Name: {assistant.name}")
        print(f"   Model: {assistant.model}")
        print(f"   Created: {assistant.created_at}")
        print(f"   Modified: {assistant.updated_at if hasattr(assistant, 'updated_at') else 'N/A'}")
        print(f"   Tools: {len(assistant.tools)}")
        print("")
        
        print("🔧 Configured Tools:")
        for i, tool in enumerate(assistant.tools, 1):
            if tool.type == 'function':
                print(f"   {i}. {tool.function.name}")
        print("")
        
        print("📝 Instructions Preview:")
        instructions_preview = assistant.instructions[:200] + "..." if len(assistant.instructions) > 200 else assistant.instructions
        print(f"   {instructions_preview}")
        print("")
        
        print("🏷️  Metadata:")
        if assistant.metadata:
            for key, value in assistant.metadata.items():
                print(f"   {key}: {value}")
        else:
            print("   No metadata")
            
    except Exception as e:
        print(f"❌ Error checking assistant: {e}")

if __name__ == "__main__":
    check_assistant()