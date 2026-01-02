#!/usr/bin/env python3
"""
Test the deployed MCP server on AgentCore Runtime with AWS SigV4 authentication.
"""

import asyncio
import os
import sys
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

class SigV4HTTPXAuth(httpx.Auth):
    """Custom HTTPX auth class for AWS SigV4 signing."""
    
    def __init__(self, service_name='bedrock-agentcore', region='eu-west-1'):
        self.service_name = service_name
        self.region = region
        # Get AWS credentials
        session = boto3.Session()
        credentials = session.get_credentials()
        self.credentials = credentials
    
    def auth_flow(self, request):
        """Sign the request with SigV4."""
        # Convert HTTPX request to AWS request
        aws_request = AWSRequest(
            method=request.method,
            url=str(request.url),
            data=request.content,
            headers=dict(request.headers)
        )
        
        # Sign the request
        SigV4Auth(self.credentials, self.service_name, self.region).add_auth(aws_request)
        
        # Update the original request with signed headers
        request.headers.update(aws_request.headers)
        
        yield request

async def test_deployed_mcp_server():
    """Test the deployed MCP server with proper AWS authentication."""
    
    # Agent ARN from deployment
    agent_arn = "arn:aws:bedrock-agentcore:eu-west-1:1234567890:runtime/s3_data_lake_mcp_server-wyeGrTEgwU"
    
    print(f"🧪 Testing deployed MCP server: {agent_arn}")
    
    # URL encode the agent ARN
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    
    # Construct the MCP URL for AgentCore Runtime
    mcp_url = f"https://bedrock-agentcore.eu-west-1.amazonaws.com/runtimes/{encoded_arn}/invocations"
    
    print(f"🔗 MCP URL: {mcp_url}")
    
    # Create SigV4 auth
    auth = SigV4HTTPXAuth()
    
    # Headers for MCP
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print("🔌 Connecting to MCP server with AWS SigV4 authentication...")
        
        # Create custom HTTP client with SigV4 auth
        async with httpx.AsyncClient(auth=auth, timeout=120.0) as http_client:
            async with streamablehttp_client(
                mcp_url, 
                headers, 
                timeout=120, 
                terminate_on_close=False,
                httpx_client=http_client
            ) as (read_stream, write_stream, _):
                async with ClientSession(read_stream, write_stream) as session:
                    print("🤝 Initializing MCP session...")
                    await session.initialize()
                    
                    print("📋 Listing available tools...")
                    tool_result = await session.list_tools()
                    
                    if hasattr(tool_result, 'tools') and tool_result.tools:
                        print(f"✅ Found {len(tool_result.tools)} tools:")
                        for i, tool in enumerate(tool_result.tools, 1):
                            print(f"  {i}. {tool.name}")
                            if tool.description:
                                print(f"     Description: {tool.description}")
                        
                        # Test the list_s3_buckets tool
                        print("\n🪣 Testing list_s3_buckets tool...")
                        bucket_result = await session.call_tool("list_s3_buckets", {})
                        
                        if hasattr(bucket_result, 'content') and bucket_result.content:
                            print("✅ S3 buckets result:")
                            for content in bucket_result.content:
                                if content.type == "text":
                                    print(content.text[:500] + "..." if len(content.text) > 500 else content.text)
                        else:
                            print(f"📄 Raw result: {bucket_result}")
                            
                    else:
                        print("❌ No tools found")
                        
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Testing Deployed S3 Data Lake MCP Server")
    print("=" * 50)
    asyncio.run(test_deployed_mcp_server())
