#!/usr/bin/env python3
"""
Local development runner for S3 Data Lake MCP Server using UV.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_server():
    """Run the MCP server locally using UV."""
    print("🚀 Starting S3 Data Lake MCP Server locally with UV...")
    print("Server will be available at: http://localhost:8000/mcp")
    print("Health check: http://localhost:8000/health")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the server using UV
        subprocess.run([
            "uv", "run", "python", "src/s3_data_lake_mcp_server.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

def run_tests():
    """Run tests using UV."""
    print("🧪 Running tests with UV...")
    try:
        subprocess.run([
            "uv", "run", "pytest", "tests/", "-v"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        sys.exit(1)

def run_client_test():
    """Run the test client."""
    print("🔧 Running MCP client test...")
    try:
        subprocess.run([
            "uv", "run", "python", "src/test_s3_mcp_client.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Client test failed: {e}")
        sys.exit(1)

def upload_sample_data():
    """Upload sample data to S3."""
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        print("❌ Please set S3_BUCKET_NAME environment variable")
        print("   Example: export S3_BUCKET_NAME=your-test-bucket")
        sys.exit(1)
    
    print(f"📤 Uploading sample data to bucket: {bucket_name}")
    try:
        subprocess.run([
            "uv", "run", "python", "src/upload_sample_data.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Sample data upload failed: {e}")
        sys.exit(1)

def main():
    """Main function to handle different run modes."""
    if len(sys.argv) < 2:
        print("🚀 S3 Data Lake MCP Server - UV Runner")
        print("=" * 40)
        print("Usage: python run_local.py <command>")
        print("\nCommands:")
        print("  server     - Start the MCP server locally")
        print("  test       - Run unit tests")
        print("  client     - Run client test")
        print("  upload     - Upload sample data to S3")
        print("  install    - Install dependencies with UV")
        print("\nExamples:")
        print("  python run_local.py server")
        print("  python run_local.py test")
        print("  S3_BUCKET_NAME=my-bucket python run_local.py upload")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "server":
        run_server()
    elif command == "test":
        run_tests()
    elif command == "client":
        run_client_test()
    elif command == "upload":
        upload_sample_data()
    elif command == "install":
        print("📦 Installing dependencies with UV...")
        subprocess.run(["uv", "sync"], check=True)
        print("✅ Dependencies installed")
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()