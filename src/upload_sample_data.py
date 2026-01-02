#!/usr/bin/env python3
"""
Upload sample data to S3 for testing the MCP server.

This script uploads sample CSV and JSON files to an S3 bucket for testing
the S3 Data Lake MCP server functionality.

Usage:
    export S3_BUCKET_NAME=your-test-bucket
    python upload_sample_data.py
"""

import boto3
import os
import sys
from botocore.exceptions import ClientError, NoCredentialsError

def upload_sample_data():
    """Upload sample data files to S3 bucket."""
    
    # Get bucket name from environment
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        print("❌ Please set S3_BUCKET_NAME environment variable")
        print("   Example: export S3_BUCKET_NAME=your-test-bucket")
        sys.exit(1)
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' exists and is accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{bucket_name}' does not exist")
                sys.exit(1)
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{bucket_name}'")
                sys.exit(1)
            else:
                raise
        
        # Files to upload
        files_to_upload = [
            {
                'local_file': 'sample_data.csv',
                's3_key': 'test-data/employees.csv',
                'content_type': 'text/csv'
            },
            {
                'local_file': 'sample_data.json',
                's3_key': 'test-data/employees.json',
                'content_type': 'application/json'
            }
        ]
        
        print(f"📤 Uploading sample data to bucket: {bucket_name}")
        
        for file_info in files_to_upload:
            local_file = file_info['local_file']
            s3_key = file_info['s3_key']
            content_type = file_info['content_type']
            
            if not os.path.exists(local_file):
                print(f"⚠️  File {local_file} not found, skipping...")
                continue
            
            try:
                # Upload file
                s3_client.upload_file(
                    local_file,
                    bucket_name,
                    s3_key,
                    ExtraArgs={'ContentType': content_type}
                )
                print(f"✅ Uploaded {local_file} → s3://{bucket_name}/{s3_key}")
                
            except Exception as e:
                print(f"❌ Failed to upload {local_file}: {e}")
        
        print(f"\n🎉 Sample data upload completed!")
        print(f"📍 You can now test the MCP server with:")
        print(f"   - s3://{bucket_name}/test-data/employees.csv")
        print(f"   - s3://{bucket_name}/test-data/employees.json")
        
        # Test queries you can try
        print(f"\n💡 Example test queries:")
        print(f"   export S3_BUCKET_NAME={bucket_name}")
        print(f"   python test_s3_mcp_client.py")
        
        print(f"\n🔍 Example agent queries:")
        print(f"   - 'List objects in the test-data folder'")
        print(f"   - 'Read the employees.csv file and show me the data'")
        print(f"   - 'Find all employees in the Engineering department'")
        print(f"   - 'What's in the employees.json file?'")
        
    except NoCredentialsError:
        print("❌ AWS credentials not found. Please configure AWS credentials:")
        print("   - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        print("   - Or run 'aws configure'")
        print("   - Or use IAM roles")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error uploading sample data: {e}")
        sys.exit(1)

def main():
    """Main entry point for the sample data uploader."""
    print("🚀 S3 Sample Data Uploader")
    print("=" * 40)
    upload_sample_data()

if __name__ == "__main__":
    main()