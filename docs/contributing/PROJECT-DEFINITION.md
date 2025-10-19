# Project Definition - Hybrid RAG System

## Core Purpose
**Neo4j + RAG + Local LLM**: A hybrid RAG (Retrieval-Augmented Generation) system that combines Neo4j's graph database with local and cloud deployment options for intelligent document search and generation.

## What It Does
1. **Stores documents** in Neo4j graph database with vector embeddings
2. **Searches documents** using hybrid vector + keyword search
3. **Generates responses** using local BitNet LLM or cloud Azure OpenAI
4. **Scales efficiently** from local development to cloud production

## Key Features
- **Hybrid deployment**: 100% local OR Azure cloud-based
- **Graph + Vector search**: Neo4j provides both capabilities 
- **Efficient LLM**: BitNet.cpp with 1.58-bit quantization
- **No vendor lock-in**: Knowledge Base works without cloud dependencies

## Target Users
- **Developers** building RAG applications
- **Organizations** needing document search with AI
- **Enterprises** requiring data sovereignty + cloud scalability

## Architecture Options
```
LOCAL: Neo4j + SentenceTransformer + BitNet.cpp (100% local)
CLOUD: Neo4j Aura + Azure OpenAI + Container Apps + Azure AI Foundary Agents
```

## Main Use Cases
1. **Knowledge base search** with intelligent answers
2. **Document Q&A** with context-aware responses  
3. **Enterprise RAG** with graph relationships
4. **Cost-efficient AI** with local deployment options
