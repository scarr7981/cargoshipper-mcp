"""Main CargoShipper MCP server entry point"""

import asyncio
import logging
from typing import Optional, Callable

from mcp.server.fastmcp import FastMCP

from .config.settings import settings
from .utils.errors import CargoShipperError
from .utils.token_inspector import get_all_token_constraints

# Configure logging
logging.basicConfig(level=getattr(logging, settings.mcp_log_level.upper()))
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name=settings.mcp_server_name
)

# Global client instances (initialized on first use)
_docker_client: Optional[object] = None
_digitalocean_client: Optional[object] = None
_cloudflare_client: Optional[object] = None


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


# Add token permissions resource
@mcp.resource("cargoshipper://token-permissions")
async def get_token_permissions() -> str:
    """Get token permissions and constraints for all configured services"""
    try:
        # Get all available clients
        docker_client = get_docker_client() if settings.has_docker_config else None
        do_client = get_digitalocean_client() if settings.has_digitalocean_config else None  
        cf_client = get_cloudflare_client() if settings.has_cloudflare_config else None
        
        # Detect constraints
        constraints = await get_all_token_constraints(docker_client, do_client, cf_client)
        
        # Format for LLM consumption
        result = "# Token Permissions and Constraints\n\n"
        
        for service, constraint in constraints.items():
            result += f"## {service.title()} API\n"
            
            if constraint.permissions:
                result += f"**✅ Permissions:** {', '.join(constraint.permissions)}\n"
            
            if constraint.restrictions:
                result += f"**❌ Restrictions:** {', '.join(constraint.restrictions)}\n"
                
            if constraint.read_only:
                result += f"**⚠️  READ-ONLY TOKEN** - Cannot create, modify, or delete resources\n"
                
            if constraint.allowed_resources:
                result += f"**🎯 Allowed Resources:** {', '.join(constraint.allowed_resources[:5])}"
                if len(constraint.allowed_resources) > 5:
                    result += f" (and {len(constraint.allowed_resources) - 5} more)"
                result += "\n"
                
            if constraint.rate_limits:
                result += f"**⏱️  Rate Limits:** {constraint.rate_limits}\n"
                
            if constraint.expires_at:
                result += f"**⏰ Expires:** {constraint.expires_at}\n"
                
            result += "\n"
            
        return result
        
    except Exception as e:
        return f"❌ Token permission detection failed: {str(e)}"


def register_components() -> None:
    """Register all tools and resources"""
    
    # Register Docker components if available
    if settings.has_docker_config:
        try:
            from .tools import docker as docker_tools
            from .resources import docker as docker_resources
            
            docker_tools.register_tools(mcp, get_docker_client)
            docker_resources.register_resources(mcp, get_docker_client)
            logger.info("Docker tools and resources registered")
        except ImportError as e:
            logger.warning(f"Docker tools not available: {e}")
    else:
        logger.info("Docker configuration not found, skipping Docker tools")
    
    # Register DigitalOcean components if configured
    if settings.has_digitalocean_config:
        try:
            from .tools import digitalocean as digitalocean_tools
            from .resources import digitalocean as digitalocean_resources
            
            digitalocean_tools.register_tools(mcp, get_digitalocean_client)
            digitalocean_resources.register_resources(mcp, get_digitalocean_client)
            logger.info("DigitalOcean tools and resources registered")
        except ImportError as e:
            logger.warning(f"DigitalOcean tools not available: {e}")
    else:
        logger.info("DigitalOcean configuration not found, skipping DigitalOcean tools")
    
    # Register CloudFlare components if configured
    if settings.has_cloudflare_config:
        try:
            from .tools import cloudflare as cloudflare_tools  
            from .resources import cloudflare as cloudflare_resources
            
            cloudflare_tools.register_tools(mcp, get_cloudflare_client)
            cloudflare_resources.register_resources(mcp, get_cloudflare_client)
            logger.info("CloudFlare tools and resources registered")
        except ImportError as e:
            logger.warning(f"CloudFlare tools not available: {e}")
    else:
        logger.info("CloudFlare configuration not found, skipping CloudFlare tools")


def main() -> None:
    """Main entry point"""
    try:
        logger.info(f"Starting {settings.mcp_server_name} v{settings.mcp_server_version}")
        logger.info(f"Transport: {settings.mcp_transport}")
        logger.info(f"Log level: {settings.mcp_log_level}")
        
        register_components()
        
        # Start server based on transport
        if settings.mcp_transport == "stdio":
            logger.info("Starting with stdio transport")
            mcp.run()
        elif settings.mcp_transport == "http":
            logger.info("Starting with HTTP transport on localhost:8000")
            mcp.run_server(host="localhost", port=8000)
        else:
            raise ValueError(f"Unsupported transport: {settings.mcp_transport}")
            
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        raise


if __name__ == "__main__":
    main()