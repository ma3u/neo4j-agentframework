#!/bin/bash
# Tag and Push Existing Local Images to GitHub Container Registry
# Usage: ./scripts/tag-and-push-existing.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

REGISTRY="ghcr.io/ma3u/ms-agentf-neo4j"

echo -e "${GREEN}🏷️  Tagging and Pushing Existing Images to GHCR${NC}"
echo -e "${BLUE}Registry: ${REGISTRY}${NC}"
echo ""

# Check if logged in
if ! docker info 2>/dev/null | grep -q "ghcr.io"; then
    echo -e "${RED}❌ Not logged into GitHub Container Registry${NC}"
    echo -e "${YELLOW}Please run: docker login ghcr.io -u ma3u${NC}"
    echo -e "${YELLOW}Use your GitHub personal access token as password${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Logged into GitHub Container Registry${NC}"
echo ""

# Function to tag and push
tag_and_push() {
    local local_image=$1
    local registry_name=$2
    local registry_tag="${REGISTRY}/${registry_name}:latest"
    
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^${local_image}:latest$"; then
        echo -e "${GREEN}📦 Processing: ${local_image}${NC}"
        echo -e "${YELLOW}   Tagging: ${registry_tag}${NC}"
        
        # Tag the image
        docker tag "${local_image}:latest" "${registry_tag}"
        
        # Also create date-based tag
        local date_tag=$(date +%Y%m%d)
        docker tag "${local_image}:latest" "${REGISTRY}/${registry_name}:${date_tag}"
        
        echo -e "${YELLOW}   Pushing: ${registry_tag}${NC}"
        # Push the images
        docker push "${registry_tag}"
        docker push "${REGISTRY}/${registry_name}:${date_tag}"
        
        echo -e "${GREEN}   ✅ Pushed: ${registry_tag}${NC}"
        echo ""
    else
        echo -e "${RED}   ❌ Local image not found: ${local_image}:latest${NC}"
        echo ""
    fi
}

# Tag and push existing images
echo -e "${BLUE}=== Processing BitNet Final Image ===${NC}"
tag_and_push "bitnet-final" "bitnet-final"

echo -e "${BLUE}=== Processing RAG Service Image ===${NC}"
tag_and_push "ms-agentf-neo4j-rag-service" "rag-service"

echo -e "${BLUE}=== Processing Streamlit Chat Image ===${NC}"
tag_and_push "streamlit-chat" "streamlit-chat"

# Show summary
echo -e "${GREEN}=== Push Summary ===${NC}"
echo -e "${GREEN}Images now available at:${NC}"
echo -e "  📦 ${REGISTRY}/bitnet-final:latest"
echo -e "  📦 ${REGISTRY}/rag-service:latest"  
echo -e "  📦 ${REGISTRY}/streamlit-chat:latest"
echo ""

echo -e "${GREEN}🔗 View in GitHub Container Registry:${NC}"
echo -e "  https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Fbitnet-final"
echo -e "  https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Frag-service"
echo -e "  https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Fstreamlit-chat"
echo ""

echo -e "${GREEN}🚀 Test deployment:${NC}"
echo -e "  docker-compose -f scripts/docker-compose.ghcr.yml pull"
echo -e "  docker-compose -f scripts/docker-compose.ghcr.yml up -d"
echo ""

echo -e "${GREEN}✅ All images pushed successfully!${NC}"