#!/usr/bin/env python3
"""
Find an assistant across all Azure OpenAI resources
"""

import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Configuration
ASSISTANT_ID = "asst_LHQBXYvRhnbFo7KQ7IRbVXRR"
AZURE_OPENAI_API_VERSION = "2024-07-18"

# Your Azure OpenAI resources
ENDPOINTS = [
    "https://azoai-immersive-copilot.openai.azure.com/",
    "https://jasmin-openai-372bb9.openai.azure.com/",
]

def find_assistant():
    """Find the assistant across all endpoints"""
    
    print(f"🔍 Searching for Assistant ID: {ASSISTANT_ID}")
    print("=" * 60)
    
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )
    
    for endpoint in ENDPOINTS:
        print(f"\n📡 Checking: {endpoint}")
        
        try:
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                api_version=AZURE_OPENAI_API_VERSION
            )
            
            # Try to get the specific assistant
            try:
                assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
                print(f"✅ FOUND! Assistant exists here:")
                print(f"   Name: {assistant.name}")
                print(f"   Model: {assistant.model}")
                print(f"   Created: {assistant.created_at}")
                print(f"   Tools: {len(assistant.tools)}")
                return endpoint
                
            except Exception as e:
                print(f"   ❌ Not found here (404)")
                
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
    
    print(f"\n❌ Assistant {ASSISTANT_ID} not found in any resource")
    print("\n🔧 Would you like to:")
    print("1. Create a new assistant")
    print("2. List existing assistants to find the right ID")
    return None

if __name__ == "__main__":
    endpoint = find_assistant()
    if endpoint:
        print(f"\n✅ Use this endpoint: {endpoint}")