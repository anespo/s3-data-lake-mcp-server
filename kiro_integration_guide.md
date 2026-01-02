# S3 Data Lake MCP Server - Kiro Integration Guide

## 🎉 Deployment Complete!

Your S3 Data Lake MCP Server has been successfully deployed to AWS AgentCore Runtime and is ready for integration with Kiro.

### 📋 **Deployment Details**

- **Agent ARN**: `arn:aws:bedrock-agentcore:eu-west-1:1234567890:runtime/s3_data_lake_mcp_server-wyeGrTEgwU`
- **Region**: eu-west-1
- **Status**: ✅ Operational
- **Tools**: 8 S3 data lake tools available
- **Permissions**: ✅ S3 read access configured
- **Demo Bucket**: `s3-data-lake-mcp-demo` with sample datasets

### 🛠️ **Available Tools**

1. **`list_s3_buckets`** - List all accessible S3 buckets
2. **`list_s3_objects`** - Browse bucket contents with filtering  
3. **`read_csv_from_s3`** - Read and parse CSV files
4. **`read_json_from_s3`** - Read JSON files (objects and arrays)
5. **`read_parquet_from_s3`** - Read Parquet files with metadata
6. **`query_csv_data`** - Filter and query CSV data
7. **`get_dataset_summary`** - Comprehensive dataset analysis
8. **`get_file_metadata`** - Detailed file information

### 🔗 **Integration Options for Kiro**

#### Option 1: Direct AgentCore Runtime Integration (Recommended)

Since this is a deployed AgentCore Runtime MCP server, you can integrate it directly with Strands agents using the MCP client:

```python
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient
import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import httpx

# Custom auth for AgentCore Runtime
class SigV4HTTPXAuth(httpx.Auth):
    def __init__(self, service_name='bedrock-agentcore', region='eu-west-1'):
        self.service_name = service_name
        self.region = region
        session = boto3.Session()
        credentials = session.get_credentials()
        self.credentials = credentials
    
    def auth_flow(self, request):
        aws_request = AWSRequest(
            method=request.method,
            url=str(request.url),
            data=request.content,
            headers=dict(request.headers)
        )
        SigV4Auth(self.credentials, self.service_name, self.region).add_auth(aws_request)
        request.headers.update(aws_request.headers)
        yield request

# Create MCP client for AgentCore Runtime
agent_arn = "arn:aws:bedrock-agentcore:eu-west-1:1234567890:runtime/s3_data_lake_mcp_server-wyeGrTEgwU"
encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
mcp_url = f"https://bedrock-agentcore.eu-west-1.amazonaws.com/runtimes/{encoded_arn}/invocations"

auth = SigV4HTTPXAuth()
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

# Use with Strands agent
async with httpx.AsyncClient(auth=auth, timeout=120.0) as http_client:
    mcp_client = MCPClient(lambda: streamablehttp_client(
        mcp_url, 
        headers, 
        timeout=120,
        httpx_client=http_client
    ))
    
    with mcp_client:
        tools = mcp_client.list_tools_sync()
        agent = Agent(
            name="S3 Data Lake Agent",
            description="An agent that can analyze data from S3 data lakes",
            tools=tools
        )
        
        # Now you can use the agent
        response = agent("List all my S3 buckets")
        response = agent("What datasets are available in the s3-data-lake-mcp-demo bucket?")
        response = agent("Show me the customer analytics data")
        response = agent("Analyze the sales transactions from the JSON file")
```

#### Option 2: Kiro MCP Configuration

Add this configuration to your Kiro MCP settings:

```json
{
  "mcpServers": {
    "s3-data-lake": {
      "command": "python",
      "args": ["/Users/yourdirectory/projects/mcp_server_etl/kiro_s3_mcp_wrapper.py"],
      "env": {
        "AWS_REGION": "eu-west-1",
        "AWS_PROFILE": "default"
      },
      "disabled": false,
      "autoApprove": [
        "list_s3_buckets",
        "list_s3_objects", 
        "get_dataset_summary",
        "get_file_metadata"
      ]
    }
  }
}
```

### 🧪 **Testing Commands**

You can test the deployed MCP server using AWS CLI:

```bash
# List available tools
ç

# List S3 buckets
echo '{"jsonrpc": "2.0", "id": "test-2", "method": "tools/call", "params": {"name": "list_s3_buckets", "arguments": {}}}' | base64 | \
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "arn:aws:bedrock-agentcore:eu-west-1:1234567890:runtime/s3_data_lake_mcp_server-wyeGrTEgwU" \
  --content-type "application/json" \
  --accept "application/json, text/event-stream" \
  --payload file:///dev/stdin \
  --region eu-west-1 \
  buckets.json

# Get dataset summary for demo bucket
echo '{"jsonrpc": "2.0", "id": "test-3", "method": "tools/call", "params": {"name": "get_dataset_summary", "arguments": {"bucket_name": "s3-data-lake-mcp-demo"}}}' | base64 | \
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn "arn:aws:bedrock-agentcore:eu-west-1:1234567890:runtime/s3_data_lake_mcp_server-wyeGrTEgwU" \
  --content-type "application/json" \
  --accept "application/json, text/event-stream" \
  --payload file:///dev/stdin \
  --region eu-west-1 \
  demo_summary.json
```

### 📊 **Example Queries**

Once integrated with Kiro, you can ask natural language questions like:

- **Data Discovery**:
  - "What S3 buckets do I have access to?"
  - "Show me a summary of datasets in the s3-data-lake-mcp-demo bucket"
  - "List all CSV files in the demo bucket"

- **Data Analysis**:
  - "Read the customer analytics data from the CSV file"
  - "What columns are available in the IoT sensor parquet file?"
  - "Find all customers in the Technology industry from customer_analytics.csv"
  - "Show me sales transactions over $50,000 from the JSON file"

- **Metadata Queries**:
  - "What's the size of the sales_transactions.json file?"
  - "How many files are in the datasets/ folder?"
  - "What file types are available in my demo data lake?"

### 🔧 **Monitoring & Logs**

- **CloudWatch Logs**: `/aws/bedrock-agentcore/runtimes/s3_data_lake_mcp_server-wyeGrTEgwU-DEFAULT`
- **Observability Dashboard**: [GenAI Observability](https://console.aws.amazon.com/cloudwatch/home?region=eu-west-1#gen-ai-observability/agent-core)
- **Status Check**: `uv run agentcore status`

### 🛡️ **Security & Permissions**

- **IAM Role**: `AmazonBedrockAgentCoreSDKRuntime-eu-west-1-3ab7543063`
- **S3 Permissions**: AmazonS3ReadOnlyAccess policy attached
- **Authentication**: AWS SigV4 (uses your AWS credentials)
- **Network**: Public (can be changed to private if needed)

### 🚀 **Next Steps**

1. **Test Integration**: Use the provided code examples to integrate with your Strands agents
2. **Upload Sample Data**: Use the `upload_sample_data.py` script to add test data
3. **Create Workflows**: Build agent workflows that leverage the S3 data lake tools
4. **Monitor Usage**: Check CloudWatch logs and observability dashboard
5. **Scale**: Add more tools or deploy additional MCP servers as needed

### 🏗️ **Architecture Overview**

![S3 Data Lake MCP Server Architecture](./generated-diagrams/s3_data_lake_mcp_architecture.png)

The architecture demonstrates:

- **Client Layer**: Kiro IDE with Strands agents using MCP client for tool integration
- **AgentCore Runtime**: Serverless MCP server deployment with automatic scaling
- **Security**: IAM role-based access with S3ReadOnlyAccess policy
- **Data Lake**: Demo S3 bucket with diverse datasets (CSV, JSON, Parquet)
- **Observability**: CloudWatch logs and GenAI observability dashboard
- **Authentication**: AWS SigV4 authentication for secure API access

### 📚 **Documentation**

- **Full Documentation**: See `README.md` for complete usage instructions
- **Architecture Diagram**: `./generated-diagrams/s3_data_lake_mcp_architecture.png`
- **AgentCore Docs**: [AWS Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- **MCP Protocol**: [Model Context Protocol](https://modelcontextprotocol.io)
- **Strands Agents**: [Strands Documentation](https://strandsagents.com)

---

**🎉 Your S3 Data Lake MCP Server is ready for production use with Kiro!**
