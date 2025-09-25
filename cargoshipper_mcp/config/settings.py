"""Configuration management for CargoShipper MCP server"""

import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from multiple possible locations for uvx compatibility
def load_env_files():
    """Load .env files from multiple possible locations"""
    possible_paths = [
        ".env",  # Current directory (for development)
        Path.home() / ".config" / "cargoshipper-mcp" / ".env",  # User config
        Path.home() / ".cargoshipper-mcp.env",  # User home
        os.path.expanduser("~/.config/cargoshipper-mcp/.env"),  # Expanded path
    ]
    
    for env_path in possible_paths:
        if Path(env_path).exists():
            load_dotenv(env_path)
            break

load_env_files()


class Settings(BaseSettings):
    """CargoShipper MCP server settings"""
    
    # MCP Configuration
    mcp_server_name: str = Field(default="CargoShipper", env="MCP_SERVER_NAME")
    mcp_server_version: str = Field(default="1.0.0", env="MCP_SERVER_VERSION")
    mcp_log_level: str = Field(default="INFO", env="MCP_LOG_LEVEL")
    mcp_transport: str = Field(default="stdio", env="MCP_TRANSPORT")
    
    # Docker Configuration
    docker_host: Optional[str] = Field(default=None, env="DOCKER_HOST")
    docker_registry_username: Optional[str] = Field(default=None, env="DOCKER_REGISTRY_USERNAME")
    docker_registry_password: Optional[str] = Field(default=None, env="DOCKER_REGISTRY_PASSWORD")
    docker_registry_server: Optional[str] = Field(default=None, env="DOCKER_REGISTRY_SERVER")
    docker_config_path: Optional[str] = Field(default=None, env="DOCKER_CONFIG_PATH")
    
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
            self.allowed_api_keys = [key.strip() for key in os.getenv("ALLOWED_API_KEYS").split(",")]
    
    @property
    def has_docker_config(self) -> bool:
        """Check if Docker configuration is available"""
        return True  # Docker client auto-detects configuration
    
    @property
    def has_docker_registry_auth(self) -> bool:
        """Check if Docker registry authentication is configured"""
        return bool(self.docker_registry_username and self.docker_registry_password)
    
    @property
    def has_digitalocean_config(self) -> bool:
        """Check if DigitalOcean configuration is available"""
        return bool(self.digitalocean_token)
    
    @property
    def has_cloudflare_config(self) -> bool:
        """Check if CloudFlare configuration is available"""
        return bool(self.cloudflare_api_token or 
                   (self.cloudflare_email and self.cloudflare_api_key))
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()