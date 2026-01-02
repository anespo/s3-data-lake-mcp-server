#!/usr/bin/env python3
"""
Test client for S3 Data Lake MCP Server

This script demonstrates how to connect a Strands agent to the S3 Data Lake MCP server
and use it to query data from S3 buckets.

Usage:
    # For local testing
    python test_s3_mcp_client.py

    # For remote AgentCore Runtime testing
    export AGENT_ARN="arn:aws:bedrock-agentcore:us-west-2:accountId:runtime/my_s3_mcp_server-xyz123"
    export BEARER_TOKEN="your_bearer_token"
    python test_s3_mcp_client.py --remote

Environment Variables:
    AGENT_ARN: ARN of the deployed MCP server in AgentCore Runtime (for remote testing)
    BEARER_TOKEN: OAuth bearer token for authentication (for remote testing)
    S3_BUCKET_NAME: S3 bucket name to use for testing
"""

import asyncio
import os
import sys
import argparse
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient

def create_local_mcp_client():
    """Create MCP client for local testing."""
    return MCPClient(lambda: streamablehttp_client("http://localhost:8000/mcp"))

def create_remote_mcp_client(agent_arn: str, bearer_token: str):
    """Create MCP client for remote AgentCore Runtime testing."""
    # URL encode the agent ARN
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    
    # Construct the MCP URL
    mcp_url = f"https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/{encoded_arn}/invocations"
    
    # Set up headers for authentication
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    
    return MCPClient(lambda: streamablehttp_client(mcp_url, headers, timeout=120))

async def test_mcp_tools_directly(mcp_client):
    """Test MCP tools directly without agent."""
    print("🔧 Testing MCP tools directly...")
    
    try:
        # List available tools
        tools = mcp_client.list_tools_sync()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Test list_s3_buckets
        print("\n📦 Testing list_s3_buckets...")
        result = mcp_client.call_tool_sync(
            tool_use_id="test-1",
            name="list_s3_buckets",
            arguments={}
        )
        print(f"Buckets result: {result['content'][0]['text'][:500]}...")
        
        # Test get_dataset_summary (you'll need to replace with your bucket name)
        bucket_name = os.getenv('S3_BUCKET_NAME', 'your-test-bucket')
        if bucket_name != 'your-test-bucket':
            print(f"\n📊 Testing get_dataset_summary for bucket: {bucket_name}...")
            result = mcp_client.call_tool_sync(
                tool_use_id="test-2",
                name="get_dataset_summary",
                arguments={"bucket_name": bucket_name}
            )
            print(f"Dataset summary: {result['content'][0]['text'][:500]}...")
        
    except Exception as e:
        print(f"❌ Error testing MCP tools: {e}")

def test_with_strands_agent(mcp_client):
    """Test the MCP server with a Strands agent."""
    print("🤖 Testing with Strands Agent...")
    
    try:
        # Get tools from MCP server
        tools = mcp_client.list_tools_sync()
        print(f"Loaded {len(tools)} tools from MCP server")
        
        # Create agent with MCP tools
        agent = Agent(
            name="S3 Data Lake Agent",
            description="An agent that can analyze data from S3 data lakes",
            tools=tools
        )
        
        # Test queries
        test_queries = [
            "List all available S3 buckets",
            "What tools do you have available for working with S3 data?",
        ]
        
        # Add bucket-specific queries if bucket is configured
        bucket_name = os.getenv('S3_BUCKET_NAME')
        if bucket_name:
            test_queries.extend([
                f"Give me a summary of the datasets in the {bucket_name} bucket",
                f"List the objects in the {bucket_name} bucket",
            ])
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            try:
                response = agent(query)
                print(f"📝 Response: {response}")
            except Exception as e:
                print(f"❌ Error with query '{query}': {e}")
                
    except Exception as e:
        print(f"❌ Error creating or using Strands agent: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Test S3 Data Lake MCP Server")
    parser.add_argument("--remote", action="store_true", help="Test remote AgentCore Runtime deployment")
    parser.add_argument("--direct-only", action="store_true", help="Only test direct MCP calls, skip Strands agent")
    args = parser.parse_args()
    
    if args.remote:
        # Remote testing
        agent_arn = os.getenv('AGENT_ARN')
        bearer_token = os.getenv('BEARER_TOKEN')
        
        if not agent_arn or not bearer_token:
            print("❌ For remote testing, please set AGENT_ARN and BEARER_TOKEN environment variables")
            sys.exit(1)
        
        print(f"🌐 Testing remote MCP server: {agent_arn}")
        mcp_client = create_remote_mcp_client(agent_arn, bearer_token)
    else:
        # Local testing
        print("🏠 Testing local MCP server at http://localhost:8000/mcp")
        mcp_client = create_local_mcp_client()
    
    # Test with context manager
    with mcp_client:
        # Test direct MCP calls
        await test_mcp_tools_directly(mcp_client)
        
        if not args.direct_only:
            print("\n" + "="*50)
            # Test with Strands agent
            test_with_strands_agent(mcp_client)

if __name__ == "__main__":
    print("🚀 S3 Data Lake MCP Server Test Client")
    print("="*50)
    
    # Check for required environment variables
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if bucket_name:
        print(f"📦 Using S3 bucket: {bucket_name}")
    else:
        print("⚠️  S3_BUCKET_NAME not set - some tests will be skipped")
        print("   Set it with: export S3_BUCKET_NAME=your-bucket-name")
    
    print()
    
    asyncio.run(main())