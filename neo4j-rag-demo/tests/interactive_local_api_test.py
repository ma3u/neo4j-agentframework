#!/usr/bin/env python3
"""
Interactive RAG Session - Tests the LOCAL Docker API (port 8000)
Uses SentenceTransformer embeddings - 100% local, no Azure required
"""

import requests
import json
import sys
from typing import Dict, Optional

BASE_URL = "http://localhost:8000"

class Colors:
    """Terminal colors for better UX"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print session header"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"🧊 NEO4J RAG INTERACTIVE SESSION 🧊")
    print(f"{'='*70}{Colors.END}")
    print("Ask any question about Neo4j, RAG, or related topics!")
    print("Type 'quit' or 'exit' to end the session.\n")

def get_health() -> Optional[Dict]:
    """Check API health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to connect to API: {e}{Colors.END}")
        return None

def get_stats() -> Optional[Dict]:
    """Get database statistics"""
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to get stats: {e}{Colors.END}")
        return None

def print_database_status(stats: Dict):
    """Print formatted database status"""
    print(f"{Colors.BOLD}📊 Database Status:{Colors.END}")

    neo4j_stats = stats.get('neo4j_stats', {})
    print(f"  • Documents: {neo4j_stats.get('documents', 0)}")
    print(f"  • Chunks: {neo4j_stats.get('chunks', 0)}")
    print(f"  • Estimated Size: ~{neo4j_stats.get('documents', 0) * 0.1:.1f} MB")
    print()

def query_rag(question: str, k: int = 3) -> Optional[Dict]:
    """Query the RAG system"""
    try:
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": question, "k": k},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"{Colors.RED}❌ Query failed: {e}{Colors.END}")
        return None

def print_answer(result: Dict):
    """Print formatted RAG answer"""
    print(f"\n{Colors.GREEN}💡 Answer:{Colors.END}")
    print(f"  {result['answer']}\n")

    print(f"{Colors.CYAN}📚 Sources ({len(result['sources'])}):{Colors.END}")
    for i, source in enumerate(result['sources'], 1):
        score = source['score']
        text = source['text'][:100] + "..." if len(source['text']) > 100 else source['text']
        print(f"  {i}. [{score:.3f}] {text}")

    print(f"\n{Colors.YELLOW}⏱️  Processing time: {result['processing_time']:.3f}s{Colors.END}\n")

def interactive_session():
    """Main interactive session"""
    print_header()

    # Check API health
    print(f"{Colors.YELLOW}Connecting to local API...{Colors.END}")
    health = get_health()

    if not health:
        print(f"{Colors.RED}Cannot connect to API at {BASE_URL}{Colors.END}")
        print("\nMake sure the local containers are running:")
        print("  docker-compose -f docker-compose-local.yml up -d")
        sys.exit(1)

    # Verify it's the local deployment
    if health.get('deployment') != "100% local - no Azure required":
        print(f"{Colors.YELLOW}⚠️  Warning: Not using local deployment!{Colors.END}")

    print(f"{Colors.GREEN}✅ Connected to: {health.get('model', 'Unknown')}{Colors.END}")
    print(f"{Colors.GREEN}✅ Deployment: {health.get('deployment', 'Unknown')}{Colors.END}\n")

    # Get initial stats
    stats = get_stats()
    if stats:
        print_database_status(stats)

    # Print available LLM info
    print(f"{Colors.CYAN}ℹ️  LLM Backend Info:{Colors.END}")
    print(f"  The local API uses SentenceTransformer for embeddings.")
    print(f"  Answer generation uses built-in context extraction.")
    print(f"  For better answers, you can run Ollama locally (optional).\n")

    # Main interaction loop
    while True:
        try:
            # Get user question
            question = input(f"{Colors.BOLD}{Colors.BLUE}❓ Your question: {Colors.END}").strip()

            # Check for exit commands
            if question.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}\n")
                break

            # Skip empty questions
            if not question:
                continue

            # Query the RAG system
            result = query_rag(question)

            if result:
                print_answer(result)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}👋 Session interrupted. Goodbye!{Colors.END}\n")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.END}\n")

if __name__ == "__main__":
    interactive_session()
