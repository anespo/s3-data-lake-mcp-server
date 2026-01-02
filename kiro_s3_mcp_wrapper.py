#!/usr/bin/env python3
"""
Kiro MCP Wrapper for S3 Data Lake MCP Server

This wrapper provides a standard MCP server interface that Kiro can connect to,
which then forwards requests to the deployed AgentCore Runtime MCP server.
"""

import asyncio
import json
import os
import sys
import logging
from typing import Any, Dict
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import httpx
from mcp.server import Server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AgentCore Runtime configuration
AGENT_ARN = "arn:aws:bedrock-agentcore:eu-west-1:1234567890:runtime/s3_data_lake_mcp_server-wyeGrTEgwU"
REGION = "eu-west-1"
SERVICE_NAME = "bedrock-agentcore"

class SigV4HTTPXAuth(httpx.Auth):
    """Custom HTTPX auth class for AWS SigV4 signing."""
    
    def __init__(self, service_name=SERVICE_NAME, region=REGION):
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

class S3DataLakeMCPWrapper:
    """Wrapper for the deployed S3 Data Lake MCP Server."""
    
    def __init__(self):
        self.agent_arn = AGENT_ARN
        self.region = REGION
        self.auth = SigV4HTTPXAuth()
        self.tools_cache = None
        
        # URL encode the agent ARN
        encoded_arn = self.agent_arn.replace(':', '%3A').replace('/', '%2F')
        self.mcp_url = f"https://bedrock-agentcore.{self.region}.amazonaws.com/runtimes/{encoded_arn}/invocations"
        
        logger.info(f"Initialized S3 Data Lake MCP Wrapper for: {self.agent_arn}")
    
    async def _make_mcp_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the AgentCore Runtime MCP server."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        async with httpx.AsyncClient(auth=self.auth, timeout=120.0) as client:
            response = await client.post(
                self.mcp_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            # Parse the Server-Sent Events response
            response_text = response.text
            if "event: message\ndata: " in response_text:
                # Extract JSON from SSE format
                json_start = response_text.find("data: ") + 6
                json_end = response_text.find("\n", json_start)
                if json_end == -1:
                    json_end = len(response_text)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                return response.json()
    
    async def list_tools(self) -> ListToolsResult:
        """List available tools from the AgentCore Runtime MCP server."""
        if self.tools_cache:
            return self.tools_cache
            
        payload = {
            "jsonrpc": "2.0",
            "id": "list-tools",
            "method": "tools/list",
            "params": {}
        }
        
        try:
            response = await self._make_mcp_request(payload)
            
            if "result" in response and "tools" in response["result"]:
                tools = []
                for tool_data in response["result"]["tools"]:
                    tool = Tool(
                        name=tool_data["name"],
                        description=tool_data["description"],
                        inputSchema=tool_data["inputSchema"]
                    )
                    tools.append(tool)
                
                result = ListToolsResult(tools=tools)
                self.tools_cache = result
                return result
            else:
                logger.error(f"Unexpected response format: {response}")
                return ListToolsResult(tools=[])
                
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return ListToolsResult(tools=[])
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Call a tool on the AgentCore Runtime MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": f"call-{name}",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self._make_mcp_request(payload)
            
            if "result" in response:
                result_data = response["result"]
                
                if "content" in result_data:
                    # Extract text content
                    content = []
                    for item in result_data["content"]:
                        if item["type"] == "text":
                            content.append(TextContent(type="text", text=item["text"]))
                    
                    return CallToolResult(content=content)
                else:
                    # Fallback for different response formats
                    text_content = json.dumps(result_data, indent=2)
                    return CallToolResult(content=[TextContent(type="text", text=text_content)])
            else:
                error_msg = f"Tool call failed: {response.get('error', 'Unknown error')}"
                return CallToolResult(content=[TextContent(type="text", text=error_msg)])
                
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            error_msg = f"Error calling tool {name}: {str(e)}"
            return CallToolResult(content=[TextContent(type="text", text=error_msg)])

# Create the MCP server
server = Server("s3-data-lake-wrapper")
wrapper = S3DataLakeMCPWrapper()

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """Handle list tools request."""
    return await wrapper.list_tools()

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle call tool request."""
    return await wrapper.call_tool(request.params.name, request.params.arguments or {})

async def main():
    """Main entry point for the MCP wrapper server."""
    logger.info("Starting S3 Data Lake MCP Wrapper Server...")
    
    # Test connection to AgentCore Runtime
    try:
        tools = await wrapper.list_tools()
        logger.info(f"Successfully connected to AgentCore Runtime. Found {len(tools.tools)} tools.")
    except Exception as e:
        logger.error(f"Failed to connect to AgentCore Runtime: {e}")
        # Don't exit, let the server start anyway
    
    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as streams:
        read_stream, write_stream = streams
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
