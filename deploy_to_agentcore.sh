#!/bin/bash

# Deploy S3 Data Lake MCP Server to AWS AgentCore Runtime
# This script automates the deployment process for the MCP server

set -e  # Exit on any error

echo "🚀 S3 Data Lake MCP Server - AgentCore Deployment"
echo "=================================================="

# Check if required tools are installed
check_requirements() {
    echo "🔍 Checking requirements..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed"
        exit 1
    fi
    
    if ! python3 -c "import bedrock_agentcore" 2>/dev/null; then
        echo "📦 Installing bedrock-agentcore-starter-toolkit..."
        pip install bedrock-agentcore-starter-toolkit
    fi
    
    echo "✅ Requirements check passed"
}

# Validate environment
validate_environment() {
    echo "🔧 Validating environment..."
    
    if [ -z "$AWS_REGION" ]; then
        export AWS_REGION="us-east-1"
        echo "⚠️  AWS_REGION not set, using default: us-east-1"
    fi
    
    # Test AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "❌ AWS credentials not configured or invalid"
        echo "   Please run 'aws configure' or set AWS environment variables"
        exit 1
    fi
    
    echo "✅ Environment validation passed"
}

# Create project structure
setup_project() {
    echo "📁 Setting up project structure..."
    
    # Ensure all required files exist
    required_files=("s3_data_lake_mcp_server.py" "requirements.txt")
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "❌ Required file missing: $file"
            exit 1
        fi
    done
    
    # Create __init__.py if it doesn't exist
    if [ ! -f "__init__.py" ]; then
        touch __init__.py
        echo "📄 Created __init__.py"
    fi
    
    echo "✅ Project structure ready"
}

# Configure deployment
configure_deployment() {
    echo "⚙️  Configuring deployment..."
    
    # Check if already configured
    if [ -f ".agentcore/config.json" ]; then
        echo "📋 Existing configuration found"
        read -p "Do you want to reconfigure? (y/N): " reconfigure
        if [[ ! $reconfigure =~ ^[Yy]$ ]]; then
            echo "Using existing configuration"
            return
        fi
    fi
    
    echo "🔧 Running agentcore configure..."
    echo "   You will be prompted to:"
    echo "   1. Select MCP protocol"
    echo "   2. Configure OAuth settings (if needed)"
    echo "   3. Set environment variables"
    echo "   4. Configure IAM permissions"
    echo ""
    
    agentcore configure -e s3_data_lake_mcp_server.py --protocol MCP
    
    echo "✅ Configuration completed"
}

# Deploy to AgentCore
deploy_server() {
    echo "🚀 Deploying to AgentCore Runtime..."
    
    echo "📤 Starting deployment..."
    agentcore deploy
    
    echo "✅ Deployment completed!"
}

# Show post-deployment information
show_deployment_info() {
    echo ""
    echo "🎉 Deployment Successful!"
    echo "========================"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Note your Agent Runtime ARN from the deployment output above"
    echo "2. Set up your bearer token for authentication"
    echo "3. Test your deployed MCP server"
    echo ""
    echo "🧪 Testing Commands:"
    echo "export AGENT_ARN=\"your-agent-runtime-arn\""
    echo "export BEARER_TOKEN=\"your-bearer-token\""
    echo "python test_s3_mcp_client.py --remote"
    echo ""
    echo "🔗 Integration with Strands Agents:"
    echo "Use the Agent ARN and bearer token to connect your Strands agents"
    echo "to this MCP server for S3 data lake access."
    echo ""
    echo "📚 Documentation:"
    echo "See README.md for detailed usage instructions and examples."
}

# Main deployment flow
main() {
    check_requirements
    validate_environment
    setup_project
    configure_deployment
    deploy_server
    show_deployment_info
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --configure    Only run configuration step"
        echo "  --deploy       Only run deployment step (requires existing config)"
        echo ""
        echo "Environment Variables:"
        echo "  AWS_REGION     AWS region (default: us-east-1)"
        echo "  S3_BUCKET_NAME Default S3 bucket for the MCP server"
        echo ""
        echo "Prerequisites:"
        echo "  - AWS credentials configured"
        echo "  - Python 3.10+ installed"
        echo "  - Required files present (see README.md)"
        exit 0
        ;;
    --configure)
        check_requirements
        validate_environment
        setup_project
        configure_deployment
        echo "✅ Configuration completed. Run '$0 --deploy' to deploy."
        exit 0
        ;;
    --deploy)
        if [ ! -f ".agentcore/config.json" ]; then
            echo "❌ No configuration found. Run '$0 --configure' first."
            exit 1
        fi
        deploy_server
        show_deployment_info
        exit 0
        ;;
    "")
        # Run full deployment
        main
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac