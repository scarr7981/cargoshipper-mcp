# MCP (Model Context Protocol) Architecture Reference

## Overview

The Model Context Protocol (MCP) is an open standard that enables AI assistants like Claude to interact with external systems through a standardized interface. Think of MCP like a USB-C port for AI applications - it provides a universal way to connect AI to various services and data sources.

## Core Architecture

### Components

1. **MCP Hosts**: AI assistants (like Claude Desktop, Claude.ai/code, or Cursor) that need to access external capabilities
2. **MCP Clients**: Embedded within MCP hosts, these establish connections to MCP servers
3. **MCP Servers**: Applications that expose tools, resources, and prompts to MCP clients

### Communication Flow

```
Claude/AI Assistant (Host)
    ↓
MCP Client
    ↓ (JSON-RPC 2.0 over transport)
MCP Server (CargoShipper)
    ↓
External APIs (Docker, DigitalOcean, CloudFlare)
```

## MCP Server Components

### 1. Tools
Tools are functions that can perform actions and may have side effects. They're like POST endpoints in a REST API.

**Key characteristics:**
- Can modify state (create resources, update configurations, etc.)
- Support structured input via type annotations
- Return structured output
- Can report progress and intermediate results
- Support cancellation

**Example:**
```python
@mcp.tool()
def create_droplet(name: str, size: str, region: str) -> dict:
    """Create a new DigitalOcean droplet"""
    # Implementation
    return {"id": "12345", "status": "creating"}
```

### 2. Resources
Resources expose data and information, similar to GET endpoints. They provide read-only access to data.

**Key characteristics:**
- No side effects
- Can be parameterized via URI templates
- Return text or binary data
- Support subscriptions for updates

**Example:**
```python
@mcp.resource("docker://containers/{container_id}")
def get_container_info(container_id: str) -> str:
    """Get information about a Docker container"""
    # Return container details as text/markdown
    return f"Container {container_id} status: running"
```

### 3. Prompts
Prompts are reusable templates that help structure interactions with the LLM.

**Key characteristics:**
- Define conversation patterns
- Can include dynamic arguments
- Return structured messages for the LLM

**Example:**
```python
@mcp.prompt()
def deploy_app_prompt(app_name: str, environment: str) -> list:
    """Generate a deployment checklist prompt"""
    return [{
        "role": "user",
        "content": f"Help me deploy {app_name} to {environment} environment"
    }]
```

## Transport Mechanisms

MCP supports multiple transport mechanisms:

### 1. stdio (Standard I/O)
- Default for local servers
- Communicates via stdin/stdout
- Used by Claude Desktop and similar local clients

### 2. SSE (Server-Sent Events) - Deprecated
- For remote HTTP connections
- Being phased out in favor of Streamable HTTP

### 3. Streamable HTTP (Recommended for Remote)
- Modern HTTP transport for remote servers
- Supports bidirectional communication
- Better performance than SSE

### 4. Custom Transports
- Can implement custom transports for specific needs

## Message Protocol

All MCP communication uses JSON-RPC 2.0 format:

### Request Example:
```json
{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/call",
    "params": {
        "name": "create_droplet",
        "arguments": {
            "name": "web-server-1",
            "size": "s-1vcpu-1gb",
            "region": "nyc3"
        }
    }
}
```

### Response Example:
```json
{
    "jsonrpc": "2.0",
    "id": "1",
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Droplet created successfully"
            }
        ]
    }
}
```

## Lifecycle Management

### 1. Initialization
```
Client → Server: initialize request
Server → Client: initialize response (with capabilities)
```

### 2. Capability Negotiation
Server declares supported features:
- tools: Server provides callable tools
- resources: Server provides readable resources
- prompts: Server provides prompt templates

### 3. Discovery
Clients can discover available tools/resources:
- `tools/list` - List all available tools
- `resources/list` - List all available resources
- `prompts/list` - List all available prompts

### 4. Execution
- `tools/call` - Execute a tool with arguments
- `resources/read` - Read a resource
- `prompts/get` - Get a prompt template

## Error Handling

MCP uses standard JSON-RPC 2.0 error codes:
- `-32700`: Parse error
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

Custom error codes for specific failures:
- Application-specific errors can use codes >= -32000

## Security Considerations

### Authentication
- Environment variables for API keys
- OAuth for remote servers
- Token-based authentication

### Authorization
- Servers should validate permissions for each operation
- Implement rate limiting
- Log security-relevant events

### Data Protection
- Encrypt sensitive data in transit
- Never log credentials or sensitive information
- Implement proper session management

## Best Practices

### 1. Tool Design
- Make tools atomic and focused
- Use clear, descriptive names
- Provide comprehensive descriptions
- Include parameter validation

### 2. Resource Design
- Keep resources lightweight
- Use caching where appropriate
- Support pagination for large datasets

### 3. Error Messages
- Provide helpful, actionable error messages
- Include relevant context
- Suggest fixes when possible

### 4. Progress Reporting
- Use progress notifications for long-running operations
- Provide meaningful status updates
- Support cancellation where feasible

## Python MCP SDK (FastMCP)

The Python SDK provides a decorator-based approach:

```python
from mcp.server.fastmcp import FastMCP

# Initialize server
mcp = FastMCP("CargoShipper")

# Define tools
@mcp.tool()
def my_tool(param: str) -> dict:
    """Tool description"""
    return {"result": "success"}

# Define resources
@mcp.resource("pattern://{param}")
def my_resource(param: str) -> str:
    """Resource description"""
    return "Resource content"

# Run server
mcp.run()
```

## Integration with Claude

When Claude uses an MCP server:
1. Claude identifies the need for external capabilities
2. The MCP client connects to the appropriate server
3. Claude discovers available tools/resources
4. Claude calls tools with structured arguments
5. Results are integrated into Claude's response

This architecture ensures:
- Standardized integration patterns
- Type safety and validation
- Clear separation of concerns
- Extensibility for future capabilities