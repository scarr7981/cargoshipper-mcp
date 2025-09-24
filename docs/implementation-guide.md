# CargoShipper MCP Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the CargoShipper MCP server that interfaces with Docker, DigitalOcean, and CloudFlare APIs. The server is built using Python and the FastMCP framework.

## Project Architecture

```
cargoshipper-mcp/
├── src/
│   ├── __init__.py
│   ├── server.py              # Main MCP server entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── docker.py          # Docker operation tools
│   │   ├── digitalocean.py    # DigitalOcean operation tools
│   │   └── cloudflare.py      # CloudFlare operation tools
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── docker.py          # Docker resources (container info, logs, etc.)
│   │   ├── digitalocean.py    # DO resources (droplet info, DNS records, etc.)
│   │   └── cloudflare.py      # CF resources (zone info, analytics, etc.)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication helpers
│   │   ├── validation.py      # Input validation utilities
│   │   ├── errors.py          # Custom error classes
│   │   └── formatters.py      # Response formatting utilities
│   └── config/
│       ├── __init__.py
│       └── settings.py        # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_docker.py
│   ├── test_digitalocean.py
│   ├── test_cloudflare.py
│   └── fixtures/
├── docs/
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Dependencies

### Core Dependencies
```toml
[project]
dependencies = [
    "mcp[cli]>=1.0.0",          # MCP Python SDK with CLI support
    "docker>=7.1.0",            # Docker SDK for Python
    "pydo>=0.4.0",              # Official DigitalOcean Python client
    "cloudflare>=2.19.0",       # Official CloudFlare Python SDK
    "pydantic>=2.5.0",          # Data validation and serialization
    "python-dotenv>=1.0.0",     # Environment variable management
    "httpx>=0.25.0",            # HTTP client (used by MCP SDK)
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "pre-commit>=3.5.0",
]
```

### Installation Commands
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# For development
pip install -e ".[dev]"
```

## Configuration Management

### Environment Variables

Create a `.env` file in the project root:

```env
# Docker Configuration
DOCKER_HOST=unix:///var/run/docker.sock  # Default Docker socket
# DOCKER_HOST=tcp://localhost:2375       # For remote Docker

# DigitalOcean Configuration
DIGITALOCEAN_TOKEN=your_digitalocean_token_here

# CloudFlare Configuration
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token_here
# Alternative: Use email + global API key (not recommended)
# CLOUDFLARE_EMAIL=your_email@example.com
# CLOUDFLARE_API_KEY=your_global_api_key

# MCP Server Configuration
MCP_SERVER_NAME=CargoShipper
MCP_SERVER_VERSION=1.0.0
MCP_LOG_LEVEL=INFO
MCP_TRANSPORT=stdio  # stdio, sse, http

# Optional: Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Optional: Authentication
REQUIRE_API_KEY=false
API_KEY_HEADER=X-API-Key
ALLOWED_API_KEYS=key1,key2,key3
```

### Settings Class

```python
# src/config/settings.py
import os
from typing import Optional, List
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # MCP Configuration
    mcp_server_name: str = Field(default="CargoShipper", env="MCP_SERVER_NAME")
    mcp_server_version: str = Field(default="1.0.0", env="MCP_SERVER_VERSION")
    mcp_log_level: str = Field(default="INFO", env="MCP_LOG_LEVEL")
    mcp_transport: str = Field(default="stdio", env="MCP_TRANSPORT")
    
    # Docker Configuration
    docker_host: Optional[str] = Field(default=None, env="DOCKER_HOST")
    
    # DigitalOcean Configuration
    digitalocean_token: Optional[str] = Field(default=None, env="DIGITALOCEAN_TOKEN")
    
    # CloudFlare Configuration
    cloudflare_api_token: Optional[str] = Field(default=None, env="CLOUDFLARE_API_TOKEN")
    cloudflare_email: Optional[str] = Field(default=None, env="CLOUDFLARE_EMAIL")
    cloudflare_api_key: Optional[str] = Field(default=None, env="CLOUDFLARE_API_KEY")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Authentication
    require_api_key: bool = Field(default=False, env="REQUIRE_API_KEY")
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    allowed_api_keys: List[str] = Field(default_factory=list)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse comma-separated API keys
        if os.getenv("ALLOWED_API_KEYS"):
            self.allowed_api_keys = os.getenv("ALLOWED_API_KEYS").split(",")
    
    @property
    def has_docker_config(self) -> bool:
        return True  # Docker client auto-detects configuration
    
    @property
    def has_digitalocean_config(self) -> bool:
        return bool(self.digitalocean_token)
    
    @property
    def has_cloudflare_config(self) -> bool:
        return bool(self.cloudflare_api_token or 
                   (self.cloudflare_email and self.cloudflare_api_key))

settings = Settings()
```

## Main Server Implementation

### Core Server Structure

```python
# src/server.py
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from mcp.server import NotificationOptions
from mcp.types import Resource, Tool, TextContent, LoggingLevel

from .config.settings import settings
from .tools import docker_tools, digitalocean_tools, cloudflare_tools
from .resources import docker_resources, digitalocean_resources, cloudflare_resources
from .utils.auth import validate_request
from .utils.errors import CargoShipperError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.mcp_log_level))
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name=settings.mcp_server_name,
    version=settings.mcp_server_version
)

# Global client instances (initialized on first use)
_docker_client = None
_digitalocean_client = None
_cloudflare_client = None

def get_docker_client():
    """Get or create Docker client"""
    global _docker_client
    if _docker_client is None:
        try:
            import docker
            _docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise CargoShipperError(f"Docker not available: {e}")
    return _docker_client

def get_digitalocean_client():
    """Get or create DigitalOcean client"""
    global _digitalocean_client
    if _digitalocean_client is None:
        if not settings.has_digitalocean_config:
            raise CargoShipperError("DigitalOcean token not configured")
        try:
            from pydo import Client
            _digitalocean_client = Client(token=settings.digitalocean_token)
            logger.info("DigitalOcean client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DigitalOcean client: {e}")
            raise CargoShipperError(f"DigitalOcean client error: {e}")
    return _digitalocean_client

def get_cloudflare_client():
    """Get or create CloudFlare client"""
    global _cloudflare_client
    if _cloudflare_client is None:
        if not settings.has_cloudflare_config:
            raise CargoShipperError("CloudFlare credentials not configured")
        try:
            import cloudflare
            if settings.cloudflare_api_token:
                _cloudflare_client = cloudflare.Cloudflare(api_token=settings.cloudflare_api_token)
            else:
                _cloudflare_client = cloudflare.Cloudflare(
                    api_email=settings.cloudflare_email,
                    api_key=settings.cloudflare_api_key
                )
            logger.info("CloudFlare client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize CloudFlare client: {e}")
            raise CargoShipperError(f"CloudFlare client error: {e}")
    return _cloudflare_client

# Register tools and resources
def register_components():
    """Register all tools and resources"""
    
    # Register Docker components if available
    if settings.has_docker_config:
        docker_tools.register_tools(mcp, get_docker_client)
        docker_resources.register_resources(mcp, get_docker_client)
        logger.info("Docker tools and resources registered")
    
    # Register DigitalOcean components if configured
    if settings.has_digitalocean_config:
        digitalocean_tools.register_tools(mcp, get_digitalocean_client)
        digitalocean_resources.register_resources(mcp, get_digitalocean_client)
        logger.info("DigitalOcean tools and resources registered")
    
    # Register CloudFlare components if configured
    if settings.has_cloudflare_config:
        cloudflare_tools.register_tools(mcp, get_cloudflare_client)
        cloudflare_resources.register_resources(mcp, get_cloudflare_client)
        logger.info("CloudFlare tools and resources registered")

# Initialize server
def main():
    """Main entry point"""
    try:
        register_components()
        
        # Start server based on transport
        if settings.mcp_transport == "stdio":
            mcp.run()
        elif settings.mcp_transport == "http":
            mcp.run_server(host="localhost", port=8000)
        else:
            raise ValueError(f"Unsupported transport: {settings.mcp_transport}")
            
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise

if __name__ == "__main__":
    main()
```

## Tool Implementation Pattern

### Base Tool Structure

```python
# src/tools/base.py
from typing import Any, Dict, Optional, Callable
from mcp.server.fastmcp import FastMCP
from ..utils.errors import CargoShipperError, ValidationError
from ..utils.validation import validate_input
from ..utils.formatters import format_success_response, format_error_response

class BaseTool:
    """Base class for all tools"""
    
    def __init__(self, mcp: FastMCP, get_client: Callable):
        self.mcp = mcp
        self.get_client = get_client
    
    def register(self):
        """Register tool with MCP server"""
        raise NotImplementedError
    
    def handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        """Standardized error handling"""
        if isinstance(error, CargoShipperError):
            return format_error_response(str(error), operation)
        elif isinstance(error, ValidationError):
            return format_error_response(f"Validation error: {error}", operation)
        else:
            return format_error_response(f"Unexpected error: {error}", operation)
```

### Docker Tool Example

```python
# src/tools/docker.py
from typing import Dict, Any, List, Optional
import docker
from docker.errors import DockerException, NotFound, APIError

from .base import BaseTool
from ..utils.validation import validate_container_name, validate_image_name
from ..utils.formatters import format_success_response, format_error_response

class DockerTools(BaseTool):
    """Docker operation tools"""
    
    def register(self):
        """Register all Docker tools"""
        
        @self.mcp.tool()
        def docker_run_container(
            image: str,
            name: Optional[str] = None,
            command: Optional[str] = None,
            ports: Optional[Dict[str, int]] = None,
            environment: Optional[Dict[str, str]] = None,
            volumes: Optional[Dict[str, str]] = None,
            detach: bool = True,
            remove: bool = False
        ) -> Dict[str, Any]:
            """Run a Docker container with specified configuration"""
            try:
                client = self.get_client()
                
                # Validate inputs
                validate_image_name(image)
                if name:
                    validate_container_name(name)
                
                # Prepare run arguments
                run_kwargs = {
                    "image": image,
                    "detach": detach,
                    "remove": remove
                }
                
                if name:
                    run_kwargs["name"] = name
                if command:
                    run_kwargs["command"] = command
                if ports:
                    run_kwargs["ports"] = ports
                if environment:
                    run_kwargs["environment"] = environment
                if volumes:
                    # Convert simple dict to volume mount format
                    volume_mounts = {}
                    for host_path, container_path in volumes.items():
                        volume_mounts[host_path] = {"bind": container_path, "mode": "rw"}
                    run_kwargs["volumes"] = volume_mounts
                
                # Run container
                container = client.containers.run(**run_kwargs)
                
                return format_success_response({
                    "container_id": container.id,
                    "container_name": container.name,
                    "status": container.status,
                    "image": image
                }, "run_container")
                
            except DockerException as e:
                return self.handle_error(e, "run_container")
            except Exception as e:
                return self.handle_error(e, "run_container")
        
        @self.mcp.tool()
        def docker_list_containers(
            all_containers: bool = True,
            filters: Optional[Dict[str, str]] = None
        ) -> Dict[str, Any]:
            """List Docker containers"""
            try:
                client = self.get_client()
                
                containers = client.containers.list(all=all_containers, filters=filters or {})
                
                container_list = []
                for container in containers:
                    container_info = {
                        "id": container.id[:12],  # Short ID
                        "name": container.name,
                        "image": container.image.tags[0] if container.image.tags else container.image.id[:12],
                        "status": container.status,
                        "created": container.attrs["Created"],
                        "ports": container.attrs["NetworkSettings"]["Ports"]
                    }
                    container_list.append(container_info)
                
                return format_success_response({
                    "containers": container_list,
                    "total": len(container_list)
                }, "list_containers")
                
            except DockerException as e:
                return self.handle_error(e, "list_containers")
            except Exception as e:
                return self.handle_error(e, "list_containers")
        
        @self.mcp.tool()
        def docker_stop_container(
            container_id: str,
            timeout: int = 10
        ) -> Dict[str, Any]:
            """Stop a Docker container"""
            try:
                client = self.get_client()
                
                container = client.containers.get(container_id)
                container.stop(timeout=timeout)
                
                return format_success_response({
                    "container_id": container.id[:12],
                    "name": container.name,
                    "status": "stopped"
                }, "stop_container")
                
            except NotFound:
                return format_error_response(f"Container {container_id} not found", "stop_container")
            except DockerException as e:
                return self.handle_error(e, "stop_container")
            except Exception as e:
                return self.handle_error(e, "stop_container")
        
        @self.mcp.tool()
        def docker_get_logs(
            container_id: str,
            tail: int = 100,
            follow: bool = False,
            timestamps: bool = True
        ) -> Dict[str, Any]:
            """Get logs from a Docker container"""
            try:
                client = self.get_client()
                
                container = client.containers.get(container_id)
                logs = container.logs(
                    tail=tail,
                    follow=follow,
                    timestamps=timestamps
                )
                
                log_output = logs.decode('utf-8') if isinstance(logs, bytes) else str(logs)
                
                return format_success_response({
                    "container_id": container.id[:12],
                    "name": container.name,
                    "logs": log_output,
                    "lines": len(log_output.splitlines())
                }, "get_logs")
                
            except NotFound:
                return format_error_response(f"Container {container_id} not found", "get_logs")
            except DockerException as e:
                return self.handle_error(e, "get_logs")
            except Exception as e:
                return self.handle_error(e, "get_logs")

def register_tools(mcp: FastMCP, get_client):
    """Register Docker tools with MCP server"""
    docker_tools = DockerTools(mcp, get_client)
    docker_tools.register()
```

## Resource Implementation Pattern

### Docker Resource Example

```python
# src/resources/docker.py
from typing import Callable
from mcp.server.fastmcp import FastMCP
from docker.errors import NotFound, DockerException

def register_resources(mcp: FastMCP, get_client: Callable):
    """Register Docker resources"""
    
    @mcp.resource("docker://containers")
    def list_containers_resource() -> str:
        """Resource to list all Docker containers"""
        try:
            client = get_client()
            containers = client.containers.list(all=True)
            
            output = ["# Docker Containers\n"]
            for container in containers:
                status_emoji = "🟢" if container.status == "running" else "🔴"
                output.append(f"## {status_emoji} {container.name}")
                output.append(f"- **ID**: {container.id[:12]}")
                output.append(f"- **Image**: {container.image.tags[0] if container.image.tags else 'N/A'}")
                output.append(f"- **Status**: {container.status}")
                output.append(f"- **Created**: {container.attrs['Created']}")
                output.append("")
            
            return "\n".join(output)
            
        except DockerException as e:
            return f"Error accessing Docker: {e}"
    
    @mcp.resource("docker://container/{container_id}")
    def get_container_resource(container_id: str) -> str:
        """Resource to get detailed information about a specific container"""
        try:
            client = get_client()
            container = client.containers.get(container_id)
            
            output = [f"# Container: {container.name}\n"]
            output.append(f"**ID**: {container.id}")
            output.append(f"**Status**: {container.status}")
            output.append(f"**Image**: {container.image.tags[0] if container.image.tags else container.image.id[:12]}")
            output.append(f"**Created**: {container.attrs['Created']}")
            output.append(f"**Started**: {container.attrs['State']['StartedAt']}")
            
            # Network information
            networks = container.attrs['NetworkSettings']['Networks']
            if networks:
                output.append("\n## Networks")
                for network_name, network_info in networks.items():
                    output.append(f"- **{network_name}**: {network_info.get('IPAddress', 'N/A')}")
            
            # Port mappings
            ports = container.attrs['NetworkSettings']['Ports']
            if ports:
                output.append("\n## Port Mappings")
                for container_port, host_bindings in ports.items():
                    if host_bindings:
                        for binding in host_bindings:
                            output.append(f"- **{container_port}** → {binding['HostIp']}:{binding['HostPort']}")
                    else:
                        output.append(f"- **{container_port}** (not bound)")
            
            # Environment variables
            env_vars = container.attrs['Config']['Env']
            if env_vars:
                output.append("\n## Environment Variables")
                for env_var in env_vars:
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        # Hide sensitive values
                        if any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret']):
                            value = '***'
                        output.append(f"- **{key}**: {value}")
            
            return "\n".join(output)
            
        except NotFound:
            return f"Container {container_id} not found"
        except DockerException as e:
            return f"Error accessing container: {e}"
    
    @mcp.resource("docker://container/{container_id}/logs")
    def get_container_logs_resource(container_id: str) -> str:
        """Resource to get logs from a specific container"""
        try:
            client = get_client()
            container = client.containers.get(container_id)
            
            logs = container.logs(tail=50, timestamps=True)
            log_output = logs.decode('utf-8') if isinstance(logs, bytes) else str(logs)
            
            return f"# Logs for {container.name}\n\n```\n{log_output}\n```"
            
        except NotFound:
            return f"Container {container_id} not found"
        except DockerException as e:
            return f"Error getting logs: {e}"
```

## Utility Functions

### Authentication Helper

```python
# src/utils/auth.py
from typing import Optional
from ..config.settings import settings
from .errors import AuthenticationError

def validate_api_key(api_key: Optional[str]) -> bool:
    """Validate API key if authentication is required"""
    if not settings.require_api_key:
        return True
    
    if not api_key:
        raise AuthenticationError("API key required but not provided")
    
    if api_key not in settings.allowed_api_keys:
        raise AuthenticationError("Invalid API key")
    
    return True

def validate_request(headers: dict) -> bool:
    """Validate incoming request"""
    api_key = headers.get(settings.api_key_header)
    return validate_api_key(api_key)
```

### Validation Utilities

```python
# src/utils/validation.py
import re
from typing import Any, Dict, List, Optional
from .errors import ValidationError

def validate_container_name(name: str) -> bool:
    """Validate Docker container name"""
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*$', name):
        raise ValidationError("Container name must match pattern: [a-zA-Z0-9][a-zA-Z0-9_.-]*")
    return True

def validate_image_name(image: str) -> bool:
    """Validate Docker image name"""
    if not image or not isinstance(image, str):
        raise ValidationError("Image name must be a non-empty string")
    return True

def validate_zone_name(zone: str) -> bool:
    """Validate DNS zone name"""
    if not re.match(r'^[a-zA-Z0-9.-]+$', zone):
        raise ValidationError("Zone name contains invalid characters")
    return True

def validate_dns_record_type(record_type: str) -> bool:
    """Validate DNS record type"""
    valid_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV', 'NS', 'PTR']
    if record_type.upper() not in valid_types:
        raise ValidationError(f"Invalid DNS record type. Must be one of: {', '.join(valid_types)}")
    return True

def validate_required_fields(data: Dict[str, Any], required: List[str]) -> bool:
    """Validate required fields are present"""
    missing = [field for field in required if field not in data or data[field] is None]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(missing)}")
    return True
```

### Error Classes

```python
# src/utils/errors.py
class CargoShipperError(Exception):
    """Base exception for CargoShipper MCP server"""
    pass

class ValidationError(CargoShipperError):
    """Validation error"""
    pass

class AuthenticationError(CargoShipperError):
    """Authentication error"""
    pass

class ConfigurationError(CargoShipperError):
    """Configuration error"""
    pass

class ServiceUnavailableError(CargoShipperError):
    """Service unavailable error"""
    pass
```

### Response Formatters

```python
# src/utils/formatters.py
from typing import Any, Dict
from datetime import datetime

def format_success_response(data: Any, operation: str) -> Dict[str, Any]:
    """Format successful operation response"""
    return {
        "success": True,
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }

def format_error_response(error: str, operation: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Format error response"""
    response = {
        "success": False,
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        "error": error
    }
    if details:
        response["details"] = details
    return response

def format_resource_response(content: str, resource_type: str, resource_id: str = None) -> str:
    """Format resource response with metadata"""
    header = [f"# {resource_type.title()} Resource"]
    if resource_id:
        header.append(f"**Resource ID**: {resource_id}")
    header.append(f"**Generated**: {datetime.utcnow().isoformat()}")
    header.append("")
    
    return "\n".join(header) + content
```

## Testing Strategy

### Unit Tests

```python
# tests/test_docker.py
import pytest
from unittest.mock import Mock, patch
from src.tools.docker import DockerTools
from src.utils.errors import ValidationError

@pytest.fixture
def mock_docker_client():
    return Mock()

@pytest.fixture
def docker_tools(mock_docker_client):
    mcp_mock = Mock()
    get_client_mock = Mock(return_value=mock_docker_client)
    return DockerTools(mcp_mock, get_client_mock)

def test_docker_run_container_success(docker_tools, mock_docker_client):
    # Setup
    container_mock = Mock()
    container_mock.id = "abc123"
    container_mock.name = "test-container"
    container_mock.status = "running"
    mock_docker_client.containers.run.return_value = container_mock
    
    # Execute
    result = docker_tools.docker_run_container("ubuntu:latest", name="test-container")
    
    # Assert
    assert result["success"] is True
    assert result["data"]["container_id"] == "abc123"
    assert result["data"]["container_name"] == "test-container"

def test_docker_run_container_validation_error(docker_tools):
    # Execute & Assert
    with pytest.raises(ValidationError):
        docker_tools.docker_run_container("", name="test-container")
```

### Integration Tests

```python
# tests/test_integration.py
import pytest
from src.server import get_docker_client
from src.config.settings import settings

@pytest.mark.integration
def test_docker_client_connection():
    """Test Docker client can connect to Docker daemon"""
    if not settings.has_docker_config:
        pytest.skip("Docker not configured")
    
    client = get_docker_client()
    info = client.info()
    assert "ServerVersion" in info
```

## Deployment Options

### Local Development

```bash
# Run with stdio transport (for Claude Desktop)
python -m src.server

# Run with HTTP transport (for remote access)
MCP_TRANSPORT=http python -m src.server
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY .env .

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp
USER mcp

EXPOSE 8000

CMD ["python", "-m", "src.server"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  cargoshipper-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_TRANSPORT=http
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - .env:/app/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Production Deployment

For production deployment, consider:

1. **Security**: Use secrets management, restrict API access
2. **Monitoring**: Add health checks, logging, metrics
3. **Scaling**: Use load balancers, container orchestration
4. **Backup**: Regular configuration and state backups

## Best Practices

### Error Handling
- Always catch specific exceptions first, then general ones
- Provide meaningful error messages to users
- Log errors with appropriate detail for debugging
- Never expose sensitive information in error responses

### Performance
- Use connection pooling for HTTP clients
- Implement rate limiting to prevent API abuse
- Cache frequently requested data when appropriate
- Use async operations for I/O bound tasks

### Security
- Validate all inputs thoroughly
- Use environment variables for sensitive configuration
- Implement proper authentication and authorization
- Regular security audits and dependency updates

### Maintainability
- Follow consistent code style and structure
- Write comprehensive tests
- Document all public APIs and configuration options
- Use type hints throughout the codebase