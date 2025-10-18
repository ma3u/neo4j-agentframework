#!/bin/bash
# Repository Documentation Reorganization Script
# Moves files to new organized structure

set -e

echo "🗂️  Starting Documentation Reorganization..."
echo "=" * 50

# Phase 1: Move Analysis Reports
echo "📊 Moving analysis reports to docs/analysis/..."
git mv CYPHER_ANALYSIS_RESULTS_EXPLAINED.md docs/analysis/
git mv docs/AURA_DATABASE_ANALYSIS_REPORT.md docs/analysis/
git mv docs/CODE_QUALITY_REPORT.md docs/analysis/ 2>/dev/null || echo "  (CODE_QUALITY_REPORT.md not tracked)"
echo "✅ Analysis reports moved"

# Phase 2: Move Cypher Resources
echo "📊 Moving Cypher queries to docs/cypher/..."
git mv neo4j-rag-demo/AURA_CYPHER_QUERIES.md docs/cypher/
git mv neo4j-rag-demo/scripts/neo4j_browser_queries.cypher docs/cypher/
git mv neo4j-rag-demo/scripts/neo4j_content_analysis.cypher docs/cypher/
git mv neo4j-rag-demo/scripts/neo4j_browser_queries_enhanced.cypher docs/cypher/
echo "✅ Cypher queries moved"

# Phase 3: Move Getting Started Guides
echo "🚀 Moving getting started docs to docs/getting-started/..."
git mv docs/LOCAL-TESTING-GUIDE.md docs/getting-started/
git mv docs/USER_GUIDE.md docs/getting-started/
git mv docs/RAG-TESTING-GUIDE.md docs/getting-started/
git mv docs/QUICKSTART_CLOUD.md docs/getting-started/ 2>/dev/null || echo "  (QUICKSTART_CLOUD already moved)"
echo "✅ Getting started guides moved"

# Phase 4: Move Deployment Docs
echo "☁️  Moving deployment docs to docs/deployment/..."
git mv docs/AZURE_DEPLOYMENT_GUIDE.md docs/deployment/
git mv docs/AZURE_ARCHITECTURE.md docs/deployment/
git mv docs/ENTERPRISE_DEPLOYMENT_SUMMARY.md docs/deployment/
git mv docs/DEPLOYMENT_GUIDES_OVERVIEW.md docs/deployment/
echo "✅ Deployment docs moved"

# Phase 5: Move Technical Guides
echo "🔧 Moving technical docs to docs/technical/..."
git mv docs/API-REFERENCE.md docs/technical/
git mv docs/EMBEDDINGS.md docs/technical/
git mv docs/LLM_SETUP.md docs/technical/
git mv docs/BITNET_OPTIMIZATION.md docs/technical/
git mv docs/PERFORMANCE_BOTTLENECK_ANALYSIS.md docs/technical/
echo "✅ Technical docs moved"

# Phase 6: Move How-To Guides
echo "📖 Moving guides to docs/guides/..."
git mv docs/NEO4J_BROWSER_GUIDE.md docs/guides/
git mv docs/KNOWLEDGE_BASE_SETUP.md docs/guides/
git mv docs/CLOUD_TESTING_GUIDE.md docs/guides/
echo "✅ Guides moved"

# Phase 7: Move Contributing Docs
echo "🤝 Moving contributing docs to docs/contributing/..."
git mv docs/CONTRIBUTING.md docs/contributing/
git mv docs/CLAUDE.md docs/contributing/
git mv docs/PROJECT-DEFINITION.md docs/contributing/
git mv docs/ASSISTANT_CONFIGURATION.md docs/contributing/
echo "✅ Contributing docs moved"

# Phase 8: Archive Reports
echo "📦 Archiving temporary reports..."
mkdir -p docs/archive/reports
git mv docs/CONSOLIDATION-REPORT.md docs/archive/reports/ 2>/dev/null || echo "  (already moved)"
git mv docs/DOCUMENTATION-AUDIT-REPORT.md docs/archive/reports/ 2>/dev/null || echo "  (already moved)"
git mv docs/DOCUMENTATION-STATUS-REPORT.md docs/archive/reports/ 2>/dev/null || echo "  (already moved)"
echo "✅ Reports archived"

# Phase 9: Archive BitNet Variants
echo "🤖 Archiving BitNet variants..."
mkdir -p docs/archive/bitnet-variants
git mv docs/BITNET-REAL-WORKING-SUMMARY.md docs/archive/bitnet-variants/ 2>/dev/null || echo "  (already moved)"
git mv docs/BITNET-TESTING-AND-DOCUMENTATION-SUMMARY.md docs/archive/bitnet-variants/ 2>/dev/null || echo "  (already moved)"
git mv docs/BITNET-VARIANTS-FINAL.md docs/archive/bitnet-variants/ 2>/dev/null || echo "  (already moved)"
git mv docs/BITNET-MINIMAL-IMPLEMENTATION.md docs/archive/bitnet-variants/ 2>/dev/null || echo "  (already moved)"
git mv docs/LOCAL_AGENT_DISCUSSION_SUMMARY.md docs/archive/bitnet-variants/ 2>/dev/null || echo "  (already moved)"
echo "✅ BitNet variants archived"

# Phase 10: Keep Core BitNet Docs in Root
echo "📚 Keeping core BitNet docs in docs/..."
# BITNET-COMPLETE-GUIDE.md stays
# BITNET-MINIMAL-DEPLOYMENT.md stays
echo "✅ Core BitNet docs remain in docs/"

echo ""
echo "=" * 50
echo "✅ Documentation Reorganization Complete!"
echo ""
echo "New Structure:"
echo "  docs/analysis/        - Analysis reports"
echo "  docs/cypher/          - Cypher query resources"
echo "  docs/getting-started/ - Beginner guides"
echo "  docs/deployment/      - Deployment guides"
echo "  docs/technical/       - Technical references"
echo "  docs/guides/          - How-to guides"
echo "  docs/contributing/    - Contributing & project info"
echo "  docs/archive/         - Historical docs"
echo ""
echo "Next: Update README.md references"
