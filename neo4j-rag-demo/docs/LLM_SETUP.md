# LLM Setup Guide for Neo4j RAG

## Overview

The Neo4j RAG system now supports proper LLM-based answer generation instead of simple pattern matching. This provides more intelligent, context-aware answers to your questions.

## Supported LLM Backends

### 1. Ollama (Recommended for Local Development)

**Ollama** runs LLMs locally on your machine without requiring API keys.

#### Installation
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

#### Setup
```bash
# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull llama2       # 7B model, good for most uses
ollama pull mistral      # Alternative, faster model
ollama pull phi          # Smaller, faster model

# Test it works
ollama run llama2 "Hello, world!"
```

#### Configuration
```python
# In your code
from src.neo4j_rag import Neo4jRAG, RAGQueryEngine

rag = Neo4jRAG()
engine = RAGQueryEngine(rag, use_llm=True)  # Will auto-detect Ollama
```

### 2. OpenAI API

For production use with OpenAI's GPT models.

#### Setup
```bash
# Set your API key
export OPENAI_API_KEY="sk-..."

# Or add to .env file
echo "OPENAI_API_KEY=sk-..." >> .env
```

#### Install Dependencies
```bash
pip install openai
```

### 3. Fallback Mode

If no LLM is available, the system falls back to intelligent pattern extraction.

## Using the LLM Handler

### Basic Usage

```python
from src.neo4j_rag import Neo4jRAG, RAGQueryEngine

# Initialize with LLM support
rag = Neo4jRAG()
engine = RAGQueryEngine(rag, use_llm=True)

# Ask a question
response = engine.query("How many authors wrote about graph databases?")
print(response['answer'])  # LLM-generated answer based on context
```

### Direct LLM Handler Usage

```python
from src.llm_handler import LLMHandler

# Initialize handler
handler = LLMHandler(preferred_backend="auto")  # or "ollama", "openai", "fallback"

# Generate answer
context = "Neo4j was created by Emil Eifrem, Johan Svensson, and Peter Neubauer."
question = "Who created Neo4j?"

answer = handler.generate_answer(question, context)
print(answer)
```

## Configuration Options

### Environment Variables

Create a `.env` file:

```env
# LLM Backend Selection
LLM_BACKEND=ollama  # Options: ollama, openai, auto, fallback

# Ollama Configuration
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI Configuration (if using)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### Programmatic Configuration

```python
# Force specific backend
engine = RAGQueryEngine(rag, use_llm=True)

# Disable LLM (use pattern extraction only)
engine = RAGQueryEngine(rag, use_llm=False)
```

## Performance Considerations

### Response Times
- **Ollama (local)**: 2-10 seconds depending on model and hardware
- **OpenAI**: 1-3 seconds (requires internet)
- **Fallback**: <100ms (pattern extraction only)

### Model Recommendations

#### For Development
- **Ollama + llama2**: Good balance of quality and speed
- **Ollama + mistral**: Faster responses, slightly less accurate
- **Ollama + phi**: Fastest, good for testing

#### For Production
- **OpenAI GPT-3.5-turbo**: Fast, cost-effective
- **OpenAI GPT-4**: Highest quality, more expensive
- **Ollama + llama2-70b**: High quality, requires powerful hardware

## Troubleshooting

### Ollama Not Detected

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Check available models
ollama list
```

### OpenAI Errors

```python
# Check API key
import os
print(os.getenv("OPENAI_API_KEY"))

# Test directly
import openai
openai.api_key = "your_key"
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Fallback to Pattern Extraction

If LLMs aren't working, the system automatically falls back to pattern extraction:

```python
# Check what's being used
if engine.use_llm and engine.llm_handler:
    print("Using LLM for answer generation")
else:
    print("Using pattern extraction (fallback)")
```

## Example Questions That Work Well

With proper LLM support, these questions now get intelligent answers:

```python
questions = [
    "How many authors do you know about?",
    "What are the main benefits of graph databases?",
    "Explain the difference between SQL and graph databases",
    "Who are the key contributors to Neo4j?",
    "Summarize the performance characteristics of Neo4j",
    "List the graph algorithms mentioned in the documents"
]

for q in questions:
    response = engine.query(q, k=5)
    print(f"Q: {q}")
    print(f"A: {response['answer']}\n")
```

## Integration with Neo4j GraphRAG

For advanced users, you can use Neo4j's official GraphRAG library:

```python
from src.official_graphrag_demo import Neo4jGraphRAGDemo

# Initialize GraphRAG
graphrag = Neo4jGraphRAGDemo()

# Use with retrieval chain
retriever = graphrag.get_retriever()
chain = graphrag.get_rag_chain()

response = chain.invoke({"question": "What is Neo4j?"})
print(response)
```

## Best Practices

1. **Always provide sufficient context**: Use k=5 or k=10 for better answers
2. **Use specific questions**: "Who created Neo4j?" vs "Tell me about Neo4j"
3. **Monitor token usage**: Larger contexts use more tokens/processing
4. **Cache responses**: For frequently asked questions
5. **Test fallback**: Ensure system works even without LLM

## Next Steps

1. Install Ollama for local LLM support
2. Test with sample questions
3. Fine-tune retrieval parameters (k value)
4. Consider implementing response caching
5. Monitor and optimize performance