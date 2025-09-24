# CargoShipper MCP Server

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![PyPI](https://img.shields.io/pypi/v/cargoshipper-mcp)](https://pypi.org/project/cargoshipper-mcp/)
[![uvx](https://img.shields.io/badge/uvx-compatible-orange.svg)](https://github.com/astral-sh/uvx)

A comprehensive MCP (Model Context Protocol) server that provides Claude with direct access to Docker, DigitalOcean, and CloudFlare APIs for infrastructure management and automation.

## ✨ Easy Setup with uvx

CargoShipper is available on PyPI and works seamlessly with `uvx` for easy installation and management, just like `mcp-server-git`.

### Quick Install from PyPI

```bash
# Run directly (recommended)
uvx cargoshipper-mcp

# Configure in your .mcp.json
{
  "mcpServers": {
    "cargoshipper": {
      "command": "uvx",
      "args": ["cargoshipper-mcp"]
    }
  }
}
```

### Development Setup

For local development and testing:

1. **Clone the repository:**
   ```bash
   cd cargoshipper-mcp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or create a virtual environment first
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Configure your APIs:**
   ```bash
   cp .env.example .env
   # Edit .env with your API tokens:
   # DIGITALOCEAN_TOKEN=your_token_here
   # CLOUDFLARE_API_TOKEN=your_token_here
   ```

4. **Use the development MCP configuration:**
   ```bash
   # Use .mcp.dev.json for local development
   cp .mcp.dev.json .mcp.json
   ```

## 🐳 Docker Integration
- **Container Management**: Full lifecycle (create, start, stop, remove, logs)
- **Image Operations**: List, pull, and manage Docker images  
- **System Information**: Docker system stats and health
- **Resource Monitoring**: Container resource usage and status

## 🌊 DigitalOcean Integration  
- **Droplet Management**: Complete droplet lifecycle management
- **DNS Management**: Full DNS record CRUD operations
- **Account Information**: Access account details and billing
- **Image Management**: Work with distributions and custom snapshots

## ☁️ CloudFlare Integration
- **Zone Management**: Create and configure CloudFlare zones
- **DNS Operations**: Advanced DNS with proxy settings
- **Cache Control**: Purge cache by URL, tags, or everything
- **Analytics**: Traffic and performance analytics
- **Security Settings**: SSL, security levels, firewall rules

## 🔧 Available Tools & Resources

**30 Tools Total:**
- **Docker (9 tools)**: `docker_run_container`, `docker_list_containers`, etc.
- **DigitalOcean (10 tools)**: `do_create_droplet`, `do_list_dns_records`, etc.  
- **CloudFlare (11 tools)**: `cf_create_zone`, `cf_purge_cache`, etc.

**17 Resources Total:**
- `docker://containers` - All containers with status
- `digitalocean://droplets` - All droplets with costs
- `cloudflare://zones` - All zones with analytics
- And many more...

## 📋 Configuration Files

### Production (.mcp.json)
```json
{
  "mcpServers": {
    "cargoshipper": {
      "command": "uvx", 
      "args": ["cargoshipper-mcp"]
    }
  }
}
```

### Development (.mcp.dev.json)
```json
{
  "mcpServers": {
    "cargoshipper": {
      "command": "python",
      "args": ["-m", "cargoshipper_mcp.server"],
      "cwd": ".",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## 🔑 API Credentials Setup

Create `.env` file or `~/.config/cargoshipper-mcp/.env`:

```env
# DigitalOcean API Token
DIGITALOCEAN_TOKEN=your_digitalocean_token_here

# CloudFlare API Token (recommended)
CLOUDFLARE_API_TOKEN=your_cloudflare_token_here

# Alternative: CloudFlare Email + Global API Key
# CLOUDFLARE_EMAIL=your@email.com
# CLOUDFLARE_API_KEY=your_global_api_key
```

**Getting API Tokens:**
- **DigitalOcean**: [API Tokens Page](https://cloud.digitalocean.com/account/api/tokens)
- **CloudFlare**: [API Tokens Page](https://dash.cloudflare.com/profile/api-tokens)

## 🚀 Usage Examples

Once configured, Claude will have access to infrastructure operations:

```
# Docker examples
"Run an nginx container on port 8080"
"List all running containers"
"Get logs from container abc123"

# DigitalOcean examples  
"Create a small droplet in NYC3"
"List all my droplets and their costs"
"Add an A record for api.example.com"

# CloudFlare examples
"Create a new zone for mysite.com"
"Purge all cache for example.com" 
"Show me analytics for the last 24 hours"
```

## 📁 Project Structure

```
cargoshipper-mcp/
├── cargoshipper_mcp/        # Main package (renamed from src/)
│   ├── server.py           # MCP server entry point  
│   ├── config/             # Configuration with multi-path .env loading
│   ├── tools/              # API operation tools
│   │   ├── docker.py       # Docker operations
│   │   ├── digitalocean.py # DigitalOcean operations
│   │   └── cloudflare.py   # CloudFlare operations
│   ├── resources/          # Read-only data access
│   └── utils/              # Shared utilities
├── .mcp.json              # Production MCP config (uvx)
├── .mcp.dev.json          # Development MCP config (local python)
├── pyproject.toml         # Python packaging (uvx compatible)
├── requirements.txt       # Dependencies
└── install.sh             # uvx installation script
```

## 🌍 Published on PyPI

CargoShipper MCP is now available on PyPI! Access it at: https://pypi.org/project/cargoshipper-mcp/

Setup is as simple as:

```bash
# Run directly (most common)
uvx cargoshipper-mcp

# Configure in .mcp.json
{
  "mcpServers": {
    "cargoshipper": {
      "command": "uvx",
      "args": ["cargoshipper-mcp"] 
    }
  }
}
```

## 🛠️ Development

### Package Structure
- Uses proper Python packaging with `pyproject.toml`
- Console entry point: `cargoshipper-mcp = "cargoshipper_mcp.server:main"`
- Multi-path environment loading for uvx compatibility
- Type hints and comprehensive error handling throughout

### Testing
```bash
python test_server.py  # Validates imports and configuration
```

This approach follows the same pattern as `mcp-server-git` and other uvx-compatible MCP servers, making it extremely easy to install and use once published!