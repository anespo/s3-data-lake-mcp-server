"""S3 Data Lake MCP Server for AWS AgentCore."""

__version__ = "1.0.0"
__author__ = "AWS AgentCore Team"
__description__ = "MCP server for reading and querying data from S3 bucket data lakes"

from .s3_data_lake_mcp_server import main

__all__ = ["main"]