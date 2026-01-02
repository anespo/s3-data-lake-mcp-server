#!/usr/bin/env python3
"""
S3 Data Lake MCP Server for AWS AgentCore

This MCP server provides tools to read and query data from S3 bucket data lakes,
making the data available to Strands agents for analysis and processing.

Features:
- List S3 buckets and objects
- Read CSV, JSON, and Parquet files from S3
- Query data with basic filtering
- Get metadata about datasets
- Support for different file formats commonly used in data lakes

Usage:
    python s3_data_lake_mcp_server.py

Environment Variables:
    AWS_REGION: AWS region (default: us-east-1)
    AWS_ACCESS_KEY_ID: AWS access key (optional if using IAM roles)
    AWS_SECRET_ACCESS_KEY: AWS secret key (optional if using IAM roles)
    S3_BUCKET_NAME: Default S3 bucket name for data lake operations
"""

import asyncio
import json
import os
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import io

import boto3
import pandas as pd
from botocore.exceptions import ClientError, NoCredentialsError
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool
from starlette.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server for AgentCore Runtime
mcp = FastMCP(
    name="S3 Data Lake MCP Server",
    host="0.0.0.0",
    port=8000,
    stateless_http=True
)

# Global S3 client
s3_client = None
default_bucket = os.getenv('S3_BUCKET_NAME', '')

def initialize_s3_client():
    """Initialize S3 client with proper error handling."""
    global s3_client
    try:
        # Use default credentials chain (IAM roles, environment variables, etc.)
        s3_client = boto3.client(
            's3',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        # Test connection
        s3_client.list_buckets()
        logger.info("S3 client initialized successfully")
    except NoCredentialsError:
        logger.error("AWS credentials not found. Please configure AWS credentials.")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        raise

@mcp.tool()
def list_s3_buckets() -> str:
    """
    List all S3 buckets accessible to the current AWS credentials.
    
    Returns:
        JSON string containing list of bucket names and creation dates
    """
    try:
        if not s3_client:
            initialize_s3_client()
            
        response = s3_client.list_buckets()
        buckets = []
        
        for bucket in response['Buckets']:
            buckets.append({
                'name': bucket['Name'],
                'creation_date': bucket['CreationDate'].isoformat()
            })
        
        return json.dumps({
            'status': 'success',
            'buckets': buckets,
            'count': len(buckets)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing S3 buckets: {e}")
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def list_s3_objects(bucket_name: str, prefix: str = "", max_keys: int = 100) -> str:
    """
    List objects in an S3 bucket with optional prefix filtering.
    
    Args:
        bucket_name: Name of the S3 bucket
        prefix: Optional prefix to filter objects (e.g., "data/2024/")
        max_keys: Maximum number of objects to return (default: 100)
    
    Returns:
        JSON string containing list of objects with metadata
    """
    try:
        if not s3_client:
            initialize_s3_client()
            
        kwargs = {
            'Bucket': bucket_name,
            'MaxKeys': max_keys
        }
        
        if prefix:
            kwargs['Prefix'] = prefix
            
        response = s3_client.list_objects_v2(**kwargs)
        
        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'storage_class': obj.get('StorageClass', 'STANDARD'),
                    'etag': obj['ETag'].strip('"')
                })
        
        return json.dumps({
            'status': 'success',
            'bucket': bucket_name,
            'prefix': prefix,
            'objects': objects,
            'count': len(objects),
            'is_truncated': response.get('IsTruncated', False)
        }, indent=2)
        
    except ClientError as e:
        logger.error(f"AWS error listing objects in bucket {bucket_name}: {e}")
        return json.dumps({
            'status': 'error',
            'message': f"AWS error: {e.response['Error']['Message']}"
        })
    except Exception as e:
        logger.error(f"Error listing objects in bucket {bucket_name}: {e}")
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def read_csv_from_s3(bucket_name: str, object_key: str, max_rows: int = 1000) -> str:
    """
    Read a CSV file from S3 and return its contents as JSON.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key (path) of the CSV file in S3
        max_rows: Maximum number of rows to return (default: 1000)
    
    Returns:
        JSON string containing CSV data and metadata
    """
    try:
        if not s3_client:
            initialize_s3_client()
            
        # Get object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        
        # Read CSV data
        csv_data = response['Body'].read()
        df = pd.read_csv(io.BytesIO(csv_data))
        
        # Limit rows if specified
        if max_rows and len(df) > max_rows:
            df_limited = df.head(max_rows)
            truncated = True
        else:
            df_limited = df
            truncated = False
        
        # Convert to JSON-serializable format
        data = df_limited.to_dict('records')
        
        # Get basic statistics
        stats = {
            'total_rows': len(df),
            'returned_rows': len(df_limited),
            'columns': list(df.columns),
            'column_count': len(df.columns),
            'truncated': truncated
        }
        
        return json.dumps({
            'status': 'success',
            'bucket': bucket_name,
            'object_key': object_key,
            'file_type': 'csv',
            'metadata': stats,
            'data': data
        }, indent=2, default=str)
        
    except ClientError as e:
        logger.error(f"AWS error reading CSV from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': f"AWS error: {e.response['Error']['Message']}"
        })
    except Exception as e:
        logger.error(f"Error reading CSV from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def read_json_from_s3(bucket_name: str, object_key: str, max_records: int = 1000) -> str:
    """
    Read a JSON file from S3 and return its contents.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key (path) of the JSON file in S3
        max_records: Maximum number of records to return for JSON arrays (default: 1000)
    
    Returns:
        JSON string containing the file data and metadata
    """
    try:
        if not s3_client:
            initialize_s3_client()
            
        # Get object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        
        # Read JSON data
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)
        
        # Handle different JSON structures
        if isinstance(data, list):
            total_records = len(data)
            if max_records and total_records > max_records:
                data = data[:max_records]
                truncated = True
            else:
                truncated = False
            
            metadata = {
                'type': 'array',
                'total_records': total_records,
                'returned_records': len(data),
                'truncated': truncated
            }
        elif isinstance(data, dict):
            metadata = {
                'type': 'object',
                'keys': list(data.keys()),
                'key_count': len(data.keys())
            }
        else:
            metadata = {
                'type': type(data).__name__
            }
        
        return json.dumps({
            'status': 'success',
            'bucket': bucket_name,
            'object_key': object_key,
            'file_type': 'json',
            'metadata': metadata,
            'data': data
        }, indent=2, default=str)
        
    except ClientError as e:
        logger.error(f"AWS error reading JSON from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': f"AWS error: {e.response['Error']['Message']}"
        })
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error reading from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': f"Invalid JSON format: {str(e)}"
        })
    except Exception as e:
        logger.error(f"Error reading JSON from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def read_parquet_from_s3(bucket_name: str, object_key: str, max_rows: int = 1000) -> str:
    """
    Read a Parquet file from S3 and return its contents as JSON.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key (path) of the Parquet file in S3
        max_rows: Maximum number of rows to return (default: 1000)
    
    Returns:
        JSON string containing Parquet data and metadata
    """
    try:
        if not s3_client:
            initialize_s3_client()
            
        # Get object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        
        # Read Parquet data
        parquet_data = response['Body'].read()
        df = pd.read_parquet(io.BytesIO(parquet_data))
        
        # Limit rows if specified
        if max_rows and len(df) > max_rows:
            df_limited = df.head(max_rows)
            truncated = True
        else:
            df_limited = df
            truncated = False
        
        # Convert to JSON-serializable format
        data = df_limited.to_dict('records')
        
        # Get basic statistics
        stats = {
            'total_rows': len(df),
            'returned_rows': len(df_limited),
            'columns': list(df.columns),
            'column_count': len(df.columns),
            'truncated': truncated,
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return json.dumps({
            'status': 'success',
            'bucket': bucket_name,
            'object_key': object_key,
            'file_type': 'parquet',
            'metadata': stats,
            'data': data
        }, indent=2, default=str)
        
    except ClientError as e:
        logger.error(f"AWS error reading Parquet from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': f"AWS error: {e.response['Error']['Message']}"
        })
    except Exception as e:
        logger.error(f"Error reading Parquet from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def query_csv_data(bucket_name: str, object_key: str, filter_column: str = "", 
                   filter_value: str = "", max_rows: int = 1000) -> str:
    """
    Query CSV data from S3 with basic filtering capabilities.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key (path) of the CSV file in S3
        filter_column: Column name to filter on (optional)
        filter_value: Value to filter for (optional)
        max_rows: Maximum number of rows to return (default: 1000)
    
    Returns:
        JSON string containing filtered data and metadata
    """
    try:
        if not s3_client:
            initialize_s3_client()
            
        # Get object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        
        # Read CSV data
        csv_data = response['Body'].read()
        df = pd.read_csv(io.BytesIO(csv_data))
        
        original_rows = len(df)
        
        # Apply filtering if specified
        if filter_column and filter_value:
            if filter_column in df.columns:
                # Handle different data types for filtering
                if df[filter_column].dtype == 'object':
                    # String filtering (case-insensitive contains)
                    df = df[df[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]
                else:
                    # Numeric filtering (exact match or convert filter_value to appropriate type)
                    try:
                        if df[filter_column].dtype in ['int64', 'int32', 'float64', 'float32']:
                            filter_val_numeric = pd.to_numeric(filter_value)
                            df = df[df[filter_column] == filter_val_numeric]
                        else:
                            df = df[df[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]
                    except (ValueError, TypeError):
                        df = df[df[filter_column].astype(str).str.contains(filter_value, case=False, na=False)]
            else:
                return json.dumps({
                    'status': 'error',
                    'message': f"Column '{filter_column}' not found in CSV. Available columns: {list(df.columns)}"
                })
        
        filtered_rows = len(df)
        
        # Limit rows if specified
        if max_rows and len(df) > max_rows:
            df_limited = df.head(max_rows)
            truncated = True
        else:
            df_limited = df
            truncated = False
        
        # Convert to JSON-serializable format
        data = df_limited.to_dict('records')
        
        # Get statistics
        stats = {
            'original_rows': original_rows,
            'filtered_rows': filtered_rows,
            'returned_rows': len(df_limited),
            'columns': list(df.columns),
            'column_count': len(df.columns),
            'filter_applied': bool(filter_column and filter_value),
            'filter_column': filter_column,
            'filter_value': filter_value,
            'truncated': truncated
        }
        
        return json.dumps({
            'status': 'success',
            'bucket': bucket_name,
            'object_key': object_key,
            'file_type': 'csv',
            'metadata': stats,
            'data': data
        }, indent=2, default=str)
        
    except ClientError as e:
        logger.error(f"AWS error querying CSV from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': f"AWS error: {e.response['Error']['Message']}"
        })
    except Exception as e:
        logger.error(f"Error querying CSV from {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def get_dataset_summary(bucket_name: str, prefix: str = "") -> str:
    """
    Get a summary of datasets in an S3 bucket or prefix, including file types and sizes.
    
    Args:
        bucket_name: Name of the S3 bucket
        prefix: Optional prefix to filter objects (e.g., "data/2024/")
    
    Returns:
        JSON string containing dataset summary and statistics
    """
    try:
        if not s3_client:
            initialize_s3_client()
            
        kwargs = {
            'Bucket': bucket_name,
            'MaxKeys': 1000  # Get more objects for better summary
        }
        
        if prefix:
            kwargs['Prefix'] = prefix
            
        response = s3_client.list_objects_v2(**kwargs)
        
        if 'Contents' not in response:
            return json.dumps({
                'status': 'success',
                'bucket': bucket_name,
                'prefix': prefix,
                'message': 'No objects found',
                'summary': {}
            })
        
        # Analyze objects
        file_types = {}
        total_size = 0
        total_files = 0
        
        for obj in response['Contents']:
            key = obj['Key']
            size = obj['Size']
            total_size += size
            total_files += 1
            
            # Determine file type from extension
            if '.' in key:
                ext = key.split('.')[-1].lower()
            else:
                ext = 'no_extension'
            
            if ext not in file_types:
                file_types[ext] = {
                    'count': 0,
                    'total_size': 0,
                    'files': []
                }
            
            file_types[ext]['count'] += 1
            file_types[ext]['total_size'] += size
            file_types[ext]['files'].append({
                'key': key,
                'size': size,
                'last_modified': obj['LastModified'].isoformat()
            })
        
        # Format sizes in human-readable format
        def format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.1f} PB"
        
        # Create summary
        summary = {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_formatted': format_size(total_size),
            'file_types': {}
        }
        
        for ext, info in file_types.items():
            summary['file_types'][ext] = {
                'count': info['count'],
                'total_size': info['total_size'],
                'total_size_formatted': format_size(info['total_size']),
                'average_size': info['total_size'] / info['count'],
                'average_size_formatted': format_size(info['total_size'] / info['count']),
                'sample_files': info['files'][:5]  # Show first 5 files as samples
            }
        
        return json.dumps({
            'status': 'success',
            'bucket': bucket_name,
            'prefix': prefix,
            'summary': summary,
            'is_truncated': response.get('IsTruncated', False)
        }, indent=2, default=str)
        
    except ClientError as e:
        logger.error(f"AWS error getting dataset summary for {bucket_name}: {e}")
        return json.dumps({
            'status': 'error',
            'message': f"AWS error: {e.response['Error']['Message']}"
        })
    except Exception as e:
        logger.error(f"Error getting dataset summary for {bucket_name}: {e}")
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

@mcp.tool()
def get_file_metadata(bucket_name: str, object_key: str) -> str:
    """
    Get detailed metadata for a specific file in S3.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key (path) of the file in S3
    
    Returns:
        JSON string containing detailed file metadata
    """
    try:
        if not s3_client:
            initialize_s3_client()
            
        # Get object metadata
        response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
        
        metadata = {
            'bucket': bucket_name,
            'key': object_key,
            'size': response['ContentLength'],
            'size_formatted': format_size(response['ContentLength']),
            'last_modified': response['LastModified'].isoformat(),
            'etag': response['ETag'].strip('"'),
            'content_type': response.get('ContentType', 'unknown'),
            'storage_class': response.get('StorageClass', 'STANDARD'),
            'server_side_encryption': response.get('ServerSideEncryption'),
            'metadata': response.get('Metadata', {}),
            'cache_control': response.get('CacheControl'),
            'content_disposition': response.get('ContentDisposition'),
            'content_encoding': response.get('ContentEncoding'),
            'content_language': response.get('ContentLanguage')
        }
        
        # Determine file type and add specific info
        if '.' in object_key:
            ext = object_key.split('.')[-1].lower()
            metadata['file_extension'] = ext
            
            # Add file type specific information
            if ext in ['csv', 'json', 'parquet', 'txt']:
                metadata['data_file'] = True
                metadata['readable_formats'] = ['csv', 'json', 'parquet']
            else:
                metadata['data_file'] = False
        
        return json.dumps({
            'status': 'success',
            'metadata': metadata
        }, indent=2, default=str)
        
    except ClientError as e:
        logger.error(f"AWS error getting metadata for {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': f"AWS error: {e.response['Error']['Message']}"
        })
    except Exception as e:
        logger.error(f"Error getting metadata for {bucket_name}/{object_key}: {e}")
        return json.dumps({
            'status': 'error',
            'message': str(e)
        })

def format_size(size_bytes):
    """Helper function to format file sizes in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def main():
    """Main entry point for the S3 Data Lake MCP Server."""
    logger.info("Starting S3 Data Lake MCP Server...")
    
    # Initialize S3 client on startup
    try:
        initialize_s3_client()
        logger.info("S3 client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
        logger.error("Server will start but S3 operations will fail until credentials are configured")
    
    # Run the MCP server with streamable-HTTP transport for AgentCore Runtime
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()