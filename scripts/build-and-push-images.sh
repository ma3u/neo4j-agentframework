#!/bin/bash
# Build and Push BitNet Docker Images to GitHub Container Registry
# Usage: ./scripts/build-and-push-images.sh [--push]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="ghcr.io/ma3u/ms-agentf-neo4j"
IMAGES=(
    "bitnet-final"
    "bitnet-optimized"
    "bitnet-minimal"
    "rag-service"
    "streamlit-chat"
)

# Check if we should push
SHOULD_PUSH=false
if [[ "$1" == "--push" ]]; then
    SHOULD_PUSH=true
fi

echo -e "${GREEN}🐳 Building BitNet Docker Images${NC}"
echo -e "${BLUE}Registry: ${REGISTRY}${NC}"
echo -e "${BLUE}Push to registry: ${SHOULD_PUSH}${NC}"
echo ""

# Function to build image
build_image() {
    local image_name=$1
    local dockerfile_path=$2
    local context_path=$3
    local full_name="${REGISTRY}/${image_name}:latest"
    
    echo -e "${GREEN}Building ${image_name}...${NC}"
    echo -e "${YELLOW}Dockerfile: ${dockerfile_path}${NC}"
    echo -e "${YELLOW}Context: ${context_path}${NC}"
    
    if [[ -f "${dockerfile_path}" ]]; then
        # Build the image
        docker build \
            -f "${dockerfile_path}" \
            -t "${full_name}" \
            "${context_path}"
        
        # Also tag with current date for versioning
        local date_tag=$(date +%Y%m%d)
        docker tag "${full_name}" "${REGISTRY}/${image_name}:${date_tag}"
        
        echo -e "${GREEN}✅ Built: ${full_name}${NC}"
        
        # Push if requested
        if [[ "$SHOULD_PUSH" == "true" ]]; then
            echo -e "${GREEN}Pushing ${image_name}...${NC}"
            docker push "${full_name}"
            docker push "${REGISTRY}/${image_name}:${date_tag}"
            echo -e "${GREEN}✅ Pushed: ${full_name}${NC}"
        fi
    else
        echo -e "${RED}❌ Dockerfile not found: ${dockerfile_path}${NC}"
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    echo -e "${GREEN}Checking prerequisites...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
        exit 1
    fi
    
    if [[ "$SHOULD_PUSH" == "true" ]]; then
        # Check if logged in to GitHub Container Registry
        if ! docker info | grep -q "ghcr.io"; then
            echo -e "${YELLOW}⚠️  Not logged in to GitHub Container Registry${NC}"
            echo -e "${YELLOW}Please run: echo \$GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin${NC}"
            echo -e "${YELLOW}Or: docker login ghcr.io${NC}"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    fi
    
    echo -e "${GREEN}✅ Prerequisites satisfied${NC}"
    echo ""
}

# Main build process
main() {
    check_prerequisites
    
    # Build BitNet Final (3.2GB - full working build)
    echo -e "${BLUE}=== Building BitNet Final Image ===${NC}"
    build_image "bitnet-final" "scripts/Dockerfile.bitnet-final" "scripts"
    echo ""
    
    # Build BitNet Optimized (1.4GB - size optimized)
    echo -e "${BLUE}=== Building BitNet Optimized Image ===${NC}"
    build_image "bitnet-optimized" "scripts/Dockerfile.bitnet-optimized" "scripts"
    echo ""
    
    # Build BitNet Minimal (334MB - ultra-minimal with external model)
    echo -e "${BLUE}=== Building BitNet Minimal Image ===${NC}"
    build_image "bitnet-minimal" "scripts/Dockerfile.bitnet-minimal" "scripts"
    echo ""
    
    # Build RAG Service
    echo -e "${BLUE}=== Building RAG Service Image ===${NC}"
    build_image "rag-service" "Dockerfile.optimized" "."
    echo ""
    
    # Build Streamlit Chat UI
    echo -e "${BLUE}=== Building Streamlit Chat UI ===${NC}"
    build_image "streamlit-chat" "neo4j-rag-demo/streamlit_app/Dockerfile" "neo4j-rag-demo/streamlit_app"
    echo ""
    
    # Show summary
    echo -e "${GREEN}=== Build Summary ===${NC}"
    echo -e "${GREEN}Images built:${NC}"
    for image in "${IMAGES[@]}"; do
        if docker images | grep -q "${REGISTRY}/${image}"; then
            local size=$(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep "${REGISTRY}/${image}:latest" | awk '{print $2}')
            echo -e "  ✅ ${REGISTRY}/${image}:latest (${size:-Unknown})"
        else
            echo -e "  ❌ ${REGISTRY}/${image}:latest (Failed)"
        fi
    done
    echo ""
    
    if [[ "$SHOULD_PUSH" == "true" ]]; then
        echo -e "${GREEN}🚀 All images pushed to GitHub Container Registry!${NC}"
        echo -e "${GREEN}Available at: https://github.com/ma3u/ms-agentf-neo4j/pkgs/container/ms-agentf-neo4j%2Fbitnet-final${NC}"
    else
        echo -e "${YELLOW}💡 To push images to registry, run:${NC}"
        echo -e "${YELLOW}   ./scripts/build-and-push-images.sh --push${NC}"
    fi
    echo ""
    
    # Show usage instructions
    echo -e "${BLUE}=== Usage Instructions ===${NC}"
    echo -e "${GREEN}Pull pre-built images:${NC}"
    for image in "${IMAGES[@]}"; do
        echo -e "  docker pull ${REGISTRY}/${image}:latest"
    done
    echo ""
    echo -e "${GREEN}Use with Docker Compose:${NC}"
    echo -e "  docker-compose -f scripts/docker-compose.ghcr.yml up -d"
    echo ""
}

# Show help
show_help() {
    echo "BitNet Docker Image Build Script"
    echo ""
    echo "Usage:"
    echo "  $0 [--push]     Build images (and push to registry if --push)"
    echo "  $0 --help       Show this help"
    echo ""
    echo "Examples:"
    echo "  $0              # Build images locally"
    echo "  $0 --push       # Build and push to GitHub Container Registry"
    echo ""
    echo "Prerequisites:"
    echo "  - Docker installed and running"
    echo "  - For --push: logged in to ghcr.io"
    echo "    docker login ghcr.io"
    echo ""
}

# Handle help flag
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Run main function
main