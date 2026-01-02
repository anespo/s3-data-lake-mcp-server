#!/usr/bin/env python3
"""
UV-based deployment script for S3 Data Lake MCP Server to AWS AgentCore Runtime.

This script uses UV for dependency management and automates the deployment process.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any

def run_command(cmd: list[str], cwd: Path = None, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a command with proper error handling."""
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            capture_output=capture_output, 
            text=True, 
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr if e.stderr else e.stdout}")
        sys.exit(1)

def check_uv_installed():
    """Check if UV is installed."""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ UV is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ UV is not installed. Please install UV first:")
    print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
    print("   or visit: https://docs.astral.sh/uv/getting-started/installation/")
    return False

def setup_uv_environment():
    """Set up UV environment and install dependencies."""
    print("🔧 Setting up UV environment...")
    
    # Initialize UV project if not already done
    if not Path("uv.lock").exists():
        print("📦 Initializing UV project...")
        run_command(["uv", "sync"])
    else:
        print("📦 Syncing UV dependencies...")
        run_command(["uv", "sync"])
    
    print("✅ UV environment ready")

def check_aws_credentials():
    """Check AWS credentials and configuration."""
    print("🔍 Checking AWS credentials...")
    
    # Check if AWS CLI is available
    try:
        result = run_command(["aws", "sts", "get-caller-identity"], capture_output=True)
        caller_info = json.loads(result.stdout)
        print(f"✅ AWS credentials valid for account: {caller_info.get('Account')}")
        print(f"   User/Role: {caller_info.get('Arn')}")
        return True
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        print("❌ AWS credentials not configured or AWS CLI not available")
        print("   Please ensure AWS credentials are configured in ~/.aws/credentials")
        return False

def validate_region():
    """Validate and set AWS region."""
    region = os.getenv('AWS_REGION', 'eu-west-1')
    print(f"🌍 Using AWS region: {region}")
    
    # Set region environment variable
    os.environ['AWS_REGION'] = region
    return region

def create_agentcore_requirements():
    """Create requirements.txt for AgentCore deployment."""
    print("📝 Creating requirements.txt for AgentCore...")
    
    # Export UV dependencies to requirements.txt
    result = run_command(["uv", "export", "--format", "requirements-txt"], capture_output=True)
    
    with open("requirements.txt", "w") as f:
        f.write(result.stdout)
    
    print("✅ requirements.txt created")

def prepare_deployment_files():
    """Prepare files for AgentCore deployment."""
    print("📁 Preparing deployment files...")
    
    # Copy main server file to root for AgentCore
    import shutil
    shutil.copy("src/s3_data_lake_mcp_server.py", "s3_data_lake_mcp_server.py")
    
    # Create __init__.py in root
    with open("__init__.py", "w") as f:
        f.write("# AgentCore deployment package\n")
    
    print("✅ Deployment files prepared")

def configure_agentcore():
    """Configure AgentCore deployment."""
    print("⚙️ Configuring AgentCore deployment...")
    
    # Check if already configured
    if Path(".agentcore/config.json").exists():
        print("📋 Existing AgentCore configuration found")
        response = input("Do you want to reconfigure? (y/N): ")
        if response.lower() != 'y':
            print("Using existing configuration")
            return
    
    print("🔧 Running agentcore configure...")
    print("   You will be prompted to:")
    print("   1. Select MCP protocol")
    print("   2. Configure OAuth settings")
    print("   3. Set environment variables")
    print("   4. Configure IAM permissions")
    print("")
    
    # Run agentcore configure with UV
    run_command([
        "uv", "run", "agentcore", "configure", 
        "-e", "s3_data_lake_mcp_server.py", 
        "--protocol", "MCP"
    ])
    
    print("✅ AgentCore configuration completed")

def deploy_to_agentcore():
    """Deploy to AgentCore Runtime."""
    print("🚀 Deploying to AgentCore Runtime...")
    
    # Run deployment with UV
    run_command(["uv", "run", "agentcore", "deploy"])
    
    print("✅ Deployment completed!")

def show_post_deployment_info():
    """Show post-deployment information."""
    print("\n🎉 Deployment Successful!")
    print("=" * 50)
    print("\n📋 Next Steps:")
    print("1. Note your Agent Runtime ARN from the deployment output above")
    print("2. Set up your bearer token for authentication")
    print("3. Test your deployed MCP server")
    print("\n🧪 Testing Commands:")
    print("export AGENT_ARN=\"your-agent-runtime-arn\"")
    print("export BEARER_TOKEN=\"your-bearer-token\"")
    print("uv run python src/test_s3_mcp_client.py --remote")
    print("\n🔗 Integration with Strands Agents:")
    print("Use the Agent ARN and bearer token to connect your Strands agents")
    print("to this MCP server for S3 data lake access.")

def main():
    """Main deployment function."""
    print("🚀 S3 Data Lake MCP Server - UV Deployment")
    print("=" * 50)
    
    # Step 1: Check UV installation
    if not check_uv_installed():
        sys.exit(1)
    
    # Step 2: Set up UV environment
    setup_uv_environment()
    
    # Step 3: Check AWS credentials
    if not check_aws_credentials():
        sys.exit(1)
    
    # Step 4: Validate region
    validate_region()
    
    # Step 5: Prepare deployment files
    create_agentcore_requirements()
    prepare_deployment_files()
    
    # Step 6: Configure AgentCore
    configure_agentcore()
    
    # Step 7: Deploy
    deploy_to_agentcore()
    
    # Step 8: Show info
    show_post_deployment_info()

if __name__ == "__main__":
    main()