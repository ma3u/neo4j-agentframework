#!/bin/bash
# Open all GitHub Container Registry package URLs in browser
# Usage: ./scripts/open-packages.sh

echo "🌍 Opening all BitNet GitHub Container Registry packages..."
echo ""
echo "For each package that opens, follow these steps:"
echo "1. Click the ⚙️ 'Package settings' button"
echo "2. Scroll down to 'Danger Zone'"
echo "3. Click 'Change visibility'"
echo "4. Select 'Public'"
echo "5. Confirm the change"
echo ""

# Package URLs
PACKAGES=(
    "https://github.com/users/ma3u/packages/container/package/ms-agentf-neo4j%2Fbitnet-final"
    "https://github.com/users/ma3u/packages/container/package/ms-agentf-neo4j%2Fbitnet-optimized"
    "https://github.com/users/ma3u/packages/container/package/ms-agentf-neo4j%2Frag-service"
    "https://github.com/users/ma3u/packages/container/package/ms-agentf-neo4j%2Fstreamlit-chat"
    "https://github.com/users/ma3u/packages/container/package/ms-agentf-neo4j%2Fbitnet-minimal"
)

NAMES=(
    "BitNet Final (3.2GB)"
    "BitNet Optimized (2.5GB)"
    "RAG Service (2.76GB)"
    "Streamlit Chat (792MB)"
    "BitNet Minimal"
)

# Open each package URL
for i in "${!PACKAGES[@]}"; do
    echo "Opening: ${NAMES[$i]}"
    open "${PACKAGES[$i]}"
    echo "  URL: ${PACKAGES[$i]}"
    echo ""
    sleep 2  # Brief delay between opens
done

echo "✅ All package URLs opened in browser!"
echo ""
echo "After making them all public, test with:"
echo "  docker pull ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest"
echo "  docker pull ghcr.io/ma3u/ms-agentf-neo4j/bitnet-optimized:latest"
echo "  docker pull ghcr.io/ma3u/ms-agentf-neo4j/rag-service:latest"
echo "  docker pull ghcr.io/ma3u/ms-agentf-neo4j/streamlit-chat:latest"