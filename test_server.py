#!/usr/bin/env python3
"""Simple test script to validate CargoShipper MCP server functionality"""

import sys
import os
import logging

# Ensure we're using the virtual environment
def check_virtual_env():
    """Check if we're running in a virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        venv_path = sys.prefix
        print(f"✅ Running in virtual environment: {venv_path}")
        return True
    else:
        print("❌ Not running in virtual environment!")
        print("Please run:")
        print("  source .venv/bin/activate  # Linux/Mac")
        print("  .venv\\Scripts\\activate.bat  # Windows")
        print("  python test_server.py")
        return False

# Add cargoshipper_mcp to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cargoshipper_mcp'))

from cargoshipper_mcp.config.settings import settings
from cargoshipper_mcp.utils.errors import CargoShipperError

def test_configuration():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    print(f"  Server Name: {settings.mcp_server_name}")
    print(f"  Version: {settings.mcp_server_version}")
    print(f"  Transport: {settings.mcp_transport}")
    print(f"  Log Level: {settings.mcp_log_level}")
    print(f"  Docker Available: {settings.has_docker_config}")
    print(f"  DigitalOcean Available: {settings.has_digitalocean_config}")
    print(f"  CloudFlare Available: {settings.has_cloudflare_config}")
    print("  ✅ Configuration loaded successfully\n")

def test_docker_connection():
    """Test Docker connection"""
    print("🐳 Testing Docker Connection...")
    try:
        from cargoshipper_mcp.server import get_docker_client
        client = get_docker_client()
        info = client.info()
        print(f"  Docker Version: {info.get('ServerVersion', 'Unknown')}")
        print(f"  Containers: {info.get('Containers', 0)}")
        print(f"  Images: {info.get('Images', 0)}")
        print("  ✅ Docker connection successful\n")
        return True
    except Exception as e:
        print(f"  ❌ Docker connection failed: {e}\n")
        return False

def test_imports():
    """Test that all modules can be imported"""
    print("📦 Testing Module Imports...")
    try:
        from cargoshipper_mcp.utils import errors, validation, formatters, auth
        print("  ✅ Utils modules imported")
        
        from cargoshipper_mcp.config.settings import settings
        print("  ✅ Settings imported")
        
        from cargoshipper_mcp.tools import docker as docker_tools
        print("  ✅ Docker tools imported")
        
        from cargoshipper_mcp.resources import docker as docker_resources
        print("  ✅ Docker resources imported")
        
        from cargoshipper_mcp import server
        print("  ✅ Server module imported")
        
        print("  ✅ All imports successful\n")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}\n")
        return False

def test_validation():
    """Test validation functions"""
    print("✅ Testing Validation Functions...")
    try:
        from cargoshipper_mcp.utils.validation import validate_container_name, validate_image_name
        
        # Test valid inputs
        validate_container_name("test-container")
        validate_image_name("nginx:latest")
        print("  ✅ Valid inputs passed")
        
        # Test invalid inputs
        try:
            validate_container_name("")
            print("  ❌ Empty container name should fail")
        except Exception:
            print("  ✅ Empty container name correctly rejected")
        
        print("  ✅ Validation functions working\n")
        return True
    except Exception as e:
        print(f"  ❌ Validation test failed: {e}\n")
        return False

def main():
    """Run all tests"""
    print("🚀 CargoShipper MCP Server Tests\n")
    
    # First check if we're in a virtual environment
    if not check_virtual_env():
        return 1
    print()
    
    tests = [
        test_configuration,
        test_imports, 
        test_validation,
        test_docker_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test {test.__name__} crashed: {e}\n")
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CargoShipper MCP server is ready.")
        print("🔗 The server is configured to run from .venv/bin/python in .mcp.json")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())