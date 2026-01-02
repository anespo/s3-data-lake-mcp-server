# S3 Data Lake MCP Server - Architecture

## 🏗️ System Architecture

![S3 Data Lake MCP Server Architecture](../generated-diagrams/s3_data_lake_mcp_architecture.png)

## 📋 Architecture Overview

The S3 Data Lake MCP Server is built on AWS Bedrock AgentCore Runtime, providing a serverless, scalable solution for AI agents to interact with S3 data lakes through the Model Context Protocol (MCP).

### Core Components

#### 1. **Client Layer**
- **Kiro IDE**: Development environment with MCP client integration
- **Strands Agents**: AI agents that consume MCP tools
- **MCP Client**: Handles protocol communication and tool invocation

#### 2. **AWS AgentCore Runtime**
- **Serverless Execution**: Automatic scaling and resource management
- **MCP Protocol Handler**: Processes tool calls and responses
- **Authentication**: AWS SigV4 signature validation
- **Load Balancing**: Distributes requests across instances

#### 3. **MCP Server Implementation**
- **FastMCP Framework**: Modern Python MCP server framework
- **8 Specialized Tools**: Comprehensive S3 data lake operations
- **Error Handling**: Robust error management and logging
- **Type Safety**: Full type hints and validation

#### 4. **Security Layer**
- **IAM Role**: `AmazonBedrockAgentCoreSDKRuntime-{region}-{hash}`
- **S3 Permissions**: Read-only access to S3 buckets
- **SigV4 Authentication**: Secure API authentication
- **Network Security**: VPC and security group controls

#### 5. **Data Layer**
- **S3 Data Lake**: Scalable object storage for datasets
- **Multiple Formats**: CSV, JSON, Parquet support
- **Demo Environment**: Safe testing environment with mock data

#### 6. **Observability**
- **CloudWatch Logs**: Centralized logging and monitoring
- **GenAI Observability**: Specialized AI/ML monitoring dashboard
- **Performance Metrics**: Request latency and throughput tracking
- **Error Tracking**: Comprehensive error logging and alerting

## 🔄 Data Flow

### 1. **Request Flow**
```
User Query → Kiro IDE → Strands Agent → MCP Client → AgentCore Runtime → MCP Server
```

### 2. **Authentication Flow**
```
AWS Credentials → SigV4 Signature → AgentCore Validation → IAM Role Assumption
```

### 3. **Data Access Flow**
```
MCP Tool → IAM Role → S3 API → Data Processing → Structured Response
```

### 4. **Response Flow**
```
MCP Server → AgentCore Runtime → MCP Client → Strands Agent → Kiro IDE → User
```

## 🛠️ Technical Stack

### **Backend**
- **Runtime**: AWS Bedrock AgentCore Runtime
- **Language**: Python 3.12+
- **Framework**: FastMCP
- **Package Manager**: UV (ultra-fast Python package installer)

### **Dependencies**
- **boto3**: AWS SDK for Python
- **pandas**: Data manipulation and analysis
- **pyarrow**: Parquet file processing
- **fastmcp**: MCP server framework
- **pydantic**: Data validation and settings management

### **Infrastructure**
- **Compute**: AWS Lambda (via AgentCore Runtime)
- **Storage**: Amazon S3
- **Authentication**: AWS IAM
- **Monitoring**: Amazon CloudWatch
- **Networking**: AWS VPC (configurable)

## 🔧 MCP Tools Architecture

### **Tool Categories**

#### **Discovery Tools**
- `list_s3_buckets`: Bucket enumeration and access validation
- `list_s3_objects`: Object discovery with filtering capabilities

#### **Data Reading Tools**
- `read_csv_from_s3`: CSV parsing with type inference
- `read_json_from_s3`: JSON processing for objects and arrays
- `read_parquet_from_s3`: Columnar data access with metadata

#### **Analysis Tools**
- `query_csv_data`: SQL-like filtering and querying
- `get_dataset_summary`: Statistical analysis and profiling
- `get_file_metadata`: Comprehensive file information

### **Tool Design Principles**

1. **Stateless**: Each tool call is independent
2. **Type Safe**: Full type hints and validation
3. **Error Resilient**: Comprehensive error handling
4. **Performance Optimized**: Streaming and chunking support
5. **Secure**: Least privilege access patterns

## 📊 Scalability Considerations

### **Horizontal Scaling**
- AgentCore Runtime automatically scales based on demand
- Stateless design enables unlimited concurrent requests
- S3 provides virtually unlimited storage capacity

### **Performance Optimization**
- Streaming responses for large datasets
- Configurable row limits and pagination
- Efficient memory usage with pandas optimization
- Parquet format for fast columnar access

### **Cost Optimization**
- Pay-per-request pricing model
- Efficient data formats (Parquet compression)
- S3 Intelligent Tiering for storage optimization
- CloudWatch log retention policies

## 🛡️ Security Architecture

### **Authentication & Authorization**
- AWS SigV4 request signing
- IAM role-based access control
- Least privilege principle
- No hardcoded credentials

### **Data Protection**
- Encryption in transit (HTTPS/TLS)
- S3 server-side encryption at rest
- VPC network isolation (optional)
- CloudTrail audit logging

### **Access Control**
- S3 bucket policies
- IAM resource-based permissions
- Cross-account access controls
- Time-based access tokens

## 🔍 Monitoring & Observability

### **Logging Strategy**
- Structured JSON logging
- Request/response correlation IDs
- Performance timing metrics
- Error stack traces and context

### **Metrics Collection**
- Request latency percentiles
- Error rates by tool and bucket
- Data processing throughput
- Memory and CPU utilization

### **Alerting**
- High error rate alerts
- Performance degradation warnings
- Security anomaly detection
- Resource utilization thresholds

## 🚀 Deployment Architecture

### **CI/CD Pipeline**
- UV-based dependency management
- Automated testing with pytest
- AgentCore CLI deployment
- Environment-specific configurations

### **Environment Management**
- Development: Local MCP server
- Testing: Isolated AgentCore runtime
- Production: Multi-region deployment
- Demo: Safe environment with mock data

### **Configuration Management**
- Environment variables for settings
- YAML-based AgentCore configuration
- Secrets management via AWS Systems Manager
- Feature flags for tool enablement

## 🔄 Future Architecture Enhancements

### **Planned Improvements**
- Multi-region deployment support
- Advanced caching layer (Redis/ElastiCache)
- Real-time streaming data support
- Enhanced security with AWS KMS
- GraphQL-style query capabilities
- Machine learning model integration

### **Extensibility Points**
- Plugin architecture for custom tools
- Configurable data processing pipelines
- Custom authentication providers
- Third-party data source connectors
- Advanced analytics and visualization tools