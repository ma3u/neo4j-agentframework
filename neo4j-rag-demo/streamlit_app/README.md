# Streamlit Chat UI for Neo4j RAG + BitNet

Interactive chat interface implementing features from issues #7, #8, and #9.

## Features

### Issue #7: Streamlit Chat UI for Local Testing
- ✅ Real-time chat with RAG-powered responses
- ✅ Message history with user/assistant differentiation
- ✅ Source document tracking and exploration
- ✅ Performance metrics display
- ✅ Configurable RAG and LLM settings

### Issue #8: Document Upload Interface
- ✅ Multi-file upload support (PDF, TXT, MD, DOCX)
- ✅ File type and size validation (up to 10MB)
- ✅ Upload progress tracking
- ✅ Recent uploads history
- ✅ Direct integration with RAG service

### Issue #9: Real-time System Monitoring Dashboard
- ✅ Individual service health indicators (Neo4j, RAG, BitNet)
- ✅ Performance metrics (response time, cache hit rate, memory)
- ✅ System statistics (documents, chunks, queries)
- ✅ Full statistics view with detailed metrics
- ✅ Query analytics and history

## Quick Start

### Docker Compose (Recommended)

```bash
# Start all services including Streamlit
docker-compose -f scripts/docker-compose.optimized.yml up -d streamlit-chat

# View logs
docker-compose -f scripts/docker-compose.optimized.yml logs -f streamlit-chat

# Access the app
open http://localhost:8501
```

### Local Development

```bash
# Install dependencies
cd neo4j-rag-demo/streamlit_app
pip install -r requirements.txt

# Run Streamlit
streamlit run app.py

# Access the app
# Opens automatically at http://localhost:8501
```

## Architecture

```
┌─────────────────┐
│ Streamlit UI    │ :8501
│ (User Interface)│
└────────┬────────┘
         │
         ├──────> Neo4j DB :7687
         │        (Direct connection for stats)
         │
         └──────> RAG Service :8000
                  ├─> Query endpoint
                  ├─> Upload endpoint
                  ├─> Health endpoint
                  └─> Stats endpoint
                       │
                       └──> BitNet LLM :8001
```

## Configuration

### Environment Variables

```bash
RAG_API_URL=http://bitnet-optimized-rag:8000  # RAG service endpoint
NEO4J_URI=bolt://neo4j-rag-optimized:7687     # Neo4j connection
STREAMLIT_SERVER_PORT=8501                     # Streamlit port
```

### Streamlit Settings

Edit `.streamlit/config.toml` for theme and server configuration.

## API Integration

### RAG Service Endpoints

**Query:**
```python
POST /query
{
  "question": "What is BitNet?",
  "max_results": 5,
  "similarity_threshold": 0.7,
  "use_llm": true
}
```

**Upload:**
```python
POST /upload
Content-Type: multipart/form-data
file: <binary>
```

**Health:**
```python
GET /health
```

**Statistics:**
```python
GET /stats
```

## Development

### Project Structure

```
streamlit_app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── .streamlit/
│   ├── config.toml       # Streamlit theme and server config
│   └── secrets.toml      # API secrets (not committed)
└── README.md            # This file
```

### Adding New Features

1. **Update app.py** with new functionality
2. **Update requirements.txt** if new dependencies needed
3. **Rebuild container**: `docker-compose build streamlit-chat`
4. **Restart service**: `docker-compose up -d streamlit-chat`

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs streamlit-chat

# Verify RAG service is running
curl http://localhost:8000/health

# Rebuild container
docker-compose build --no-cache streamlit-chat
docker-compose up -d streamlit-chat
```

### Cannot Connect to RAG Service

```bash
# Check network
docker network inspect optimized-rag-network

# Test connectivity
docker exec streamlit-chat curl http://bitnet-optimized-rag:8000/health
```

### Upload Fails

- Check file size (max 10MB)
- Verify file type (PDF, TXT, MD, DOCX)
- Check RAG service logs
- Ensure Neo4j is accessible

## Testing

```bash
# Health check
curl http://localhost:8501/_stcore/health

# Test RAG integration
# Use the UI to send a test query

# Test upload
# Use the UI to upload a test document
```

## Production Deployment

For production deployment to Azure, see the main project documentation.

## Resources

- **Live Demo Mockup**: https://ma3u.github.io/neo4j-agentframework/
- **Issue #7**: Streamlit Chat UI
- **Issue #8**: Document Upload Interface
- **Issue #9**: System Monitoring Dashboard
- **Streamlit Docs**: https://docs.streamlit.io/

---

**Made with ❤️ for efficient AI systems**
**Generated with Claude Code** (https://claude.com/claude-code)
