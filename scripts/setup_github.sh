#!/bin/bash

# GitHub Repository Setup Script for Neo4j RAG System
# This script helps you push your local repository to GitHub

echo "🚀 Neo4j RAG System - GitHub Setup"
echo "=================================="
echo ""
echo "This script will help you push your repository to GitHub."
echo "Make sure you have already created a repository on GitHub."
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository. Please run 'git init' first."
    exit 1
fi

# Check current remotes
REMOTE_EXISTS=$(git remote -v | grep origin)
if [ -n "$REMOTE_EXISTS" ]; then
    echo "⚠️  Warning: Remote 'origin' already exists:"
    git remote -v
    echo ""
    read -p "Do you want to remove it and add a new one? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
        echo "✅ Removed existing origin"
    else
        echo "Keeping existing remote. Exiting."
        exit 0
    fi
fi

# Get GitHub repository URL
echo ""
echo "Enter your GitHub repository URL"
echo "Format: https://github.com/username/repository-name.git"
echo "   or: git@github.com:username/repository-name.git"
echo ""
read -p "Repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ Error: Repository URL cannot be empty"
    exit 1
fi

# Add remote
echo ""
echo "Adding remote origin..."
git remote add origin "$REPO_URL"

# Verify remote was added
if git remote -v | grep -q origin; then
    echo "✅ Remote added successfully!"
    echo ""
    git remote -v
else
    echo "❌ Error: Failed to add remote"
    exit 1
fi

# Show current branch
CURRENT_BRANCH=$(git branch --show-current)
echo ""
echo "📌 Current branch: $CURRENT_BRANCH"

# Show commits that will be pushed
echo ""
echo "📝 Commits that will be pushed:"
git log --oneline -10

# Confirm push
echo ""
echo "Ready to push to GitHub!"
echo "This will push the following:"
echo "  - All commits shown above"
echo "  - 5 Jupyter notebooks for analysis"
echo "  - Complete RAG system implementation"
echo "  - Documentation and examples"
echo ""
read -p "Do you want to push now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Pushing to GitHub..."

    # Push with upstream tracking
    git push -u origin "$CURRENT_BRANCH"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Successfully pushed to GitHub!"
        echo ""
        echo "Your repository is now available at:"
        echo "$REPO_URL" | sed 's/\.git$//'
        echo ""
        echo "Next steps:"
        echo "1. Visit your GitHub repository"
        echo "2. Add a description and topics"
        echo "3. Create releases if needed"
        echo "4. Share with the community!"
    else
        echo ""
        echo "❌ Push failed. Common issues:"
        echo "  - Authentication required (set up GitHub token/SSH key)"
        echo "  - Repository doesn't exist on GitHub"
        echo "  - No push permissions"
        echo ""
        echo "To set up authentication:"
        echo "  - For HTTPS: Use a personal access token"
        echo "  - For SSH: Add your SSH key to GitHub"
    fi
else
    echo "Push cancelled. You can run this script again later or push manually with:"
    echo "  git push -u origin $CURRENT_BRANCH"
fi