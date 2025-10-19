#!/bin/bash
# Remove large binary files from Git tracking
# Usage: ./scripts/cleanup-large-files.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧹 Cleaning up large files from Git repository...${NC}"
echo ""

# Show what we're about to remove
echo -e "${YELLOW}Files to be removed from Git tracking:${NC}"
git ls-files BitNet/ | grep -E "\.gguf$|\.bin$|\.so$" | sed 's/^/  /'
echo ""

read -p "Remove these files from Git tracking? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Removing large files from Git index...${NC}"
    echo ""
    
    # Remove GGUF files from Git (but keep in working directory)
    echo "Removing *.gguf files..."
    git ls-files BitNet/ | grep "\.gguf$" | xargs -I {} git rm --cached "{}" || true
    
    # Remove binary files from Git (but keep in working directory)
    echo "Removing *.bin files..."
    git ls-files BitNet/ | grep "\.bin$" | xargs -I {} git rm --cached "{}" || true
    
    # Remove shared libraries from Git (but keep in working directory)
    echo "Removing *.so files..."
    git ls-files BitNet/ | grep "\.so$" | xargs -I {} git rm --cached "{}" || true
    
    echo ""
    echo -e "${GREEN}✅ Files removed from Git tracking (but preserved in working directory)${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Commit the changes:"
    echo "   git commit -m 'Remove large binary files from Git tracking'"
    echo ""
    echo "2. Verify .gitignore is working:"
    echo "   git status BitNet/"
    echo ""
    echo "3. Files are still available locally and in containers:"
    echo "   docker pull ghcr.io/ma3u/ms-agentf-neo4j/bitnet-final:latest"
    echo ""
    
    # Show repository size improvement
    echo -e "${GREEN}Repository size check:${NC}"
    du -sh .git/ | sed 's/^/  Git database: /'
    
else
    echo -e "${YELLOW}Operation cancelled.${NC}"
    exit 0
fi