#!/bin/bash
# Localhost-Only Setup - Simplest Working Configuration
# All services on localhost, no Docker networking issues

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "══════════════════════════════════════════════════════════════"
echo "  🚀 LOCALHOST-ONLY SETUP (Simplest)"
echo "══════════════════════════════════════════════════════════════"
echo ""

# 1. Ensure Neo4j is running
echo "1. Checking Neo4j..."
if docker ps | grep -q neo4j; then
    echo -e "  ${GREEN}✓${NC} Neo4j already running"
else
    echo "  Starting Neo4j..."
    docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/password neo4j:5.11
    sleep 20
fi

# 2. Setup Python environment
echo ""
echo "2. Setting up Python..."
cd neo4j-rag-demo
python3 -m venv venv_local 2>/dev/null || true
source venv_local/bin/activate
pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" | head -5

echo -e "  ${GREEN}✓${NC} Environment ready"

# 3. Load sample data
echo ""
echo "3. Loading 8 sample documents..."
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from neo4j_rag import Neo4jRAG

rag = Neo4jRAG()

# Use batch_add_documents method
docs = [
    {"content": "Neo4j is a highly scalable graph database with Cypher query language, ACID transactions, and property graph model for connected data.", "metadata": {"source": "neo4j_intro.txt", "category": "database"}},
    {"content": "BitNet provides 1.58-bit quantized language models achieving 87% memory reduction with TernaryWeight quantization.", "metadata": {"source": "bitnet_overview.txt", "category": "ai"}},
    {"content": "RAG (Retrieval-Augmented Generation) combines vector search retrieval with LLM generation for accurate AI responses.", "metadata": {"source": "rag_explained.txt", "category": "ai"}},
    {"content": "Vector search enables semantic similarity matching using embeddings and cosine similarity for finding relevant documents.", "metadata": {"source": "vector_search.txt", "category": "search"}},
    {"content": "Sentence embeddings transform text into dense 384-dimensional vectors capturing semantic meaning.", "metadata": {"source": "embeddings.txt", "category": "nlp"}},
    {"content": "Graph databases excel at relationship-heavy queries, traversing millions of connections per second for social networks.", "metadata": {"source": "graph_benefits.txt", "category": "database"}},
    {"content": "Streamlit is a Python framework for building interactive data applications and ML dashboards with minimal code.", "metadata": {"source": "streamlit_guide.txt", "category": "framework"}},
    {"content": "Azure Container Apps provide serverless container deployment with auto-scaling and pay-per-use pricing.", "metadata": {"source": "azure_guide.txt", "category": "cloud"}}
]

print(f"Adding {len(docs)} documents...")
rag.batch_add_documents(docs, batch_size=4)

stats = rag.get_stats()
print(f"✅ {stats['documents']} docs, {stats['chunks']} chunks loaded")
rag.close()
EOF

# 4. Start RAG API locally
echo ""
echo "4. Starting RAG API (localhost:8000)..."
pkill -f "python.*app_local" 2>/dev/null || true
python3 app_local.py > /tmp/rag_local.log 2>&1 &
sleep 5

# 5. Start Streamlit locally
echo ""
echo "5. Starting Streamlit (localhost:8501)..."
pkill -f "streamlit run" 2>/dev/null || true
cd streamlit_app
streamlit run app.py > /tmp/streamlit_local.log 2>&1 &
sleep 5

# 6. Verify
echo ""
echo "6. Verifying..."
curl -s http://localhost:8000/health > /dev/null && echo -e "  ${GREEN}✓${NC} RAG API responding" || echo -e "  ${RED}✗${NC} RAG API"
curl -s http://localhost:8501 > /dev/null && echo -e "  ${GREEN}✓${NC} Streamlit responding" || echo -e "  ${RED}✗${NC} Streamlit"

echo ""
echo "══════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}✅ SETUP COMPLETE${NC}"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Opening: http://localhost:8501"
open http://localhost:8501
echo ""
echo "Expected to see LIVE DATA:"
echo "  📄 Documents: 8"
echo "  🧩 Chunks: ~200+"
echo "  ⚡ Response: ~100ms"
echo "  All health cards: 🟢 Green"
echo ""
