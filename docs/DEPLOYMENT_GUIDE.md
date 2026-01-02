# S3 Data Lake MCP Server - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- UV package manager
- AWS CLI configured with appropriate permissions
- AWS Bedrock AgentCore access

### 1. Install Dependencies
```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Local Development
```bash
# Run the MCP server locally
uv run python run_local.py

# Run tests
uv run pytest tests/
```

### 3. Deploy to AWS AgentCore Runtime
```bash
# Deploy using UV
uv run python deploy_uv.py

# Or use the shell script
chmod +x deploy_to_agentcore.sh
./deploy_to_agentcore.sh
```

### 4. Generate Demo Data
```bash
# Create demo datasets in S3
uv run python generate_mock_data.py
```

## 🛠️ Configuration

### Environment Variables
- `AWS_REGION`: AWS region (default: eu-west-1)
- `AWS_PROFILE`: AWS profile to use (default: default)

### AgentCore Configuration
The deployment creates a `.bedrock_agentcore.yaml` file with your runtime configuration.

## 📊 Available Tools

1. **list_s3_buckets** - List all accessible S3 buckets
2. **list_s3_objects** - Browse bucket contents with filtering
3. **read_csv_from_s3** - Read and parse CSV files
4. **read_json_from_s3** - Read JSON files (objects and arrays)
5. **read_parquet_from_s3** - Read Parquet files with metadata
6. **query_csv_data** - Filter and query CSV data
7. **get_dataset_summary** - Comprehensive dataset analysis
8. **get_file_metadata** - Detailed file information

## 🔍 Testing

### Test Deployed MCP Server
```bash
# Test the deployed server
uv run python test_deployed_mcp.py
```

### Integration Testing
```bash
# Run comprehensive tests
uv run pytest tests/ -v
```

## 📚 Documentation

- [Integration Guide](../kiro_integration_guide.md) - Complete integration instructions
- [Architecture Diagram](../generated-diagrams/) - System architecture visualization
- [LinkedIn Post](../linkedin_viral_post.md) - Project announcement

## 🛡️ Security

- Uses AWS SigV4 authentication
- IAM role-based access control
- S3ReadOnlyAccess policy attached
- No hardcoded credentials

## 📈 Monitoring

- CloudWatch logs: `/aws/bedrock-agentcore/runtimes/{agent-name}`
- GenAI Observability dashboard
- Built-in error tracking and performance metrics

## 🚨 Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure your AWS credentials have AgentCore permissions
2. **Deployment Fails**: Check AWS region and AgentCore availability
3. **Tool Not Found**: Verify MCP server registration and tool names
4. **S3 Access Issues**: Confirm S3 bucket permissions and IAM role

### Debug Commands
```bash
# Check AgentCore status
uv run agentcore status

# View logs
aws logs tail /aws/bedrock-agentcore/runtimes/{agent-name} --follow

# Test local MCP server
uv run python -m pytest tests/test_s3_mcp_server.py -v
```

## 🔄 Updates

To update the deployed MCP server:
1. Make your changes
2. Run tests: `uv run pytest`
3. Redeploy: `uv run python deploy_uv.py`

## 📞 Support

For issues and questions:
- Check the troubleshooting section above
- Review CloudWatch logs
- Test locally first with `run_local.py`
- Ensure all prerequisites are met