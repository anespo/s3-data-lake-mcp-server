"""
Tests for S3 Data Lake MCP Server.
"""

import pytest
import json
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from s3_data_lake_mcp_server import (
    list_s3_buckets,
    list_s3_objects,
    get_dataset_summary,
    format_size
)

class TestS3MCPServer:
    """Test cases for S3 MCP Server functions."""
    
    def test_format_size(self):
        """Test file size formatting."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(1048576) == "1.0 MB"
        assert format_size(1073741824) == "1.0 GB"
        assert format_size(500) == "500.0 B"
    
    @patch('s3_data_lake_mcp_server.s3_client')
    def test_list_s3_buckets_success(self, mock_s3_client):
        """Test successful bucket listing."""
        from datetime import datetime
        
        # Mock S3 response
        mock_s3_client.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'test-bucket-1', 'CreationDate': datetime(2024, 1, 1)},
                {'Name': 'test-bucket-2', 'CreationDate': datetime(2024, 1, 2)}
            ]
        }
        
        result = list_s3_buckets()
        result_data = json.loads(result)
        
        assert result_data['status'] == 'success'
        assert len(result_data['buckets']) == 2
        assert result_data['buckets'][0]['name'] == 'test-bucket-1'
    
    @patch('s3_data_lake_mcp_server.s3_client')
    def test_list_s3_objects_success(self, mock_s3_client):
        """Test successful object listing."""
        from datetime import datetime
        
        # Mock S3 response
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'data/file1.csv',
                    'Size': 1024,
                    'LastModified': datetime(2024, 1, 1),
                    'StorageClass': 'STANDARD',
                    'ETag': '"abc123"'
                }
            ],
            'IsTruncated': False
        }
        
        result = list_s3_objects('test-bucket', 'data/')
        result_data = json.loads(result)
        
        assert result_data['status'] == 'success'
        assert result_data['bucket'] == 'test-bucket'
        assert result_data['prefix'] == 'data/'
        assert len(result_data['objects']) == 1
        assert result_data['objects'][0]['key'] == 'data/file1.csv'

    @patch('s3_data_lake_mcp_server.s3_client')
    def test_get_dataset_summary_success(self, mock_s3_client):
        """Test successful dataset summary."""
        from datetime import datetime
        
        # Mock S3 response
        mock_s3_client.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'data/file1.csv',
                    'Size': 1024,
                    'LastModified': datetime(2024, 1, 1)
                },
                {
                    'Key': 'data/file2.json',
                    'Size': 2048,
                    'LastModified': datetime(2024, 1, 1)
                }
            ],
            'IsTruncated': False
        }
        
        result = get_dataset_summary('test-bucket', 'data/')
        result_data = json.loads(result)
        
        assert result_data['status'] == 'success'
        assert result_data['summary']['total_files'] == 2
        assert result_data['summary']['total_size'] == 3072
        assert 'csv' in result_data['summary']['file_types']
        assert 'json' in result_data['summary']['file_types']

if __name__ == "__main__":
    pytest.main([__file__])