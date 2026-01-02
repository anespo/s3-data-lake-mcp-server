#!/bin/bash

# GitHub Repository Setup Commands
# Run these commands after creating the repository on GitHub

echo "🚀 Setting up GitHub repository for S3 Data Lake MCP Server..."

# Set the main branch
git branch -M main

# Add the GitHub remote (replace YOUR_GITHUB_USERNAME with your actual username)
echo "📡 Adding GitHub remote..."
read -p "Enter your GitHub username: " GITHUB_USERNAME
git remote add origin https://github.com/$GITHUB_USERNAME/s3-data-lake-mcp-server.git

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo "✅ Repository successfully pushed to GitHub!"
echo ""
echo "🎯 Next steps:"
echo "1. Go to your GitHub repository"
echo "2. Add repository topics: mcp, aws, bedrock, agentcore, s3, data-lake, ai, agents, python"
echo "3. Enable Discussions and Issues"
echo "4. Create your first release (v1.0.0)"
echo "5. Share the LinkedIn post from docs/linkedin_viral_post.md"
echo ""
echo "🌟 Your repository is ready to go viral!"