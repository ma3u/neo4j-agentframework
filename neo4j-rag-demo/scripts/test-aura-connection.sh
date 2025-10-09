#!/bin/bash
# Test Neo4j Aura Connection with Azure Key Vault Credentials
# This script verifies the complete setup is working

set -e

echo "🧪 Testing Neo4j Aura Connection with Key Vault"
echo "==============================================="
echo ""

# Check environment
if [ -z "$AZURE_KEY_VAULT_NAME" ]; then
    echo "⚠️  AZURE_KEY_VAULT_NAME not set"
    echo "Please set it: export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod"
    exit 1
fi

echo "📋 Configuration:"
echo "  Key Vault: $AZURE_KEY_VAULT_NAME"
echo ""

# Change to project directory
cd "$(dirname "$0")/.."

# Check if in correct directory
if [ ! -f "src/azure_keyvault_config.py" ]; then
    echo "❌ Error: Must run from neo4j-rag-demo directory"
    exit 1
fi

# Test 1: Key Vault credential retrieval
echo "🔐 Test 1: Key Vault Credential Retrieval"
echo "----------------------------------------"
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from azure_keyvault_config import AuraConfig

try:
    config = AuraConfig()
    creds = config.get_neo4j_credentials()
    print(f"✅ Successfully retrieved credentials")
    print(f"   URI: {creds.uri}")
    print(f"   Username: {creds.username}")
    print(f"   Password: {'*' * len(creds.password)}")
except Exception as e:
    print(f"❌ Failed to retrieve credentials: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Key Vault test failed!"
    exit 1
fi

echo ""

# Test 2: Neo4j connection
echo "🔌 Test 2: Neo4j Aura Connection"
echo "--------------------------------"
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from neo4j_rag import Neo4jRAG

try:
    print("Connecting to Neo4j Aura...")
    rag = Neo4jRAG()
    
    print("✅ Connected successfully!")
    
    # Get database stats
    stats = rag.get_stats()
    print(f"   Documents: {stats.get('total_documents', 0)}")
    print(f"   Chunks: {stats.get('total_chunks', 0)}")
    
    rag.close()
    print("✅ Connection closed cleanly")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Neo4j connection test failed!"
    exit 1
fi

echo ""

# Test 3: Vector search functionality
echo "🔍 Test 3: Vector Search Functionality"
echo "--------------------------------------"
python3 << 'EOF'
import sys
import time
sys.path.insert(0, 'src')
from neo4j_rag import Neo4jRAG

try:
    rag = Neo4jRAG()
    
    # Test vector search (even with no data, should return empty results)
    print("Testing vector search...")
    start_time = time.time()
    results = rag.vector_search("test query", k=3)
    search_time = (time.time() - start_time) * 1000
    
    print(f"✅ Vector search completed in {search_time:.2f}ms")
    print(f"   Results returned: {len(results)}")
    
    # If no results, add a test document
    if len(results) == 0:
        print("   Adding test document...")
        rag.add_document(
            "Neo4j Aura is a fully managed cloud database service.",
            metadata={"source": "test"}
        )
        print("   ✅ Test document added")
        
        # Try search again
        results = rag.vector_search("Neo4j", k=1)
        print(f"   ✅ Search after adding document: {len(results)} results")
    
    rag.close()
    
except Exception as e:
    print(f"❌ Vector search test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Vector search test failed!"
    exit 1
fi

echo ""
echo "==============================================="
echo "✅ All Tests Passed!"
echo "==============================================="
echo ""
echo "📊 Summary:"
echo "  ✓ Key Vault credential retrieval working"
echo "  ✓ Neo4j Aura connection established"
echo "  ✓ Vector search functionality confirmed"
echo ""
echo "🎉 Your Neo4j Aura integration is ready!"
echo ""
echo "📝 Next steps:"
echo "  1. Load your actual data"
echo "  2. Deploy to Azure Container Apps"
echo "  3. Monitor performance"
echo ""
