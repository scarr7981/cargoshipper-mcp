"""Docker authentication utilities for CargoShipper MCP server"""

import json
import base64
import os
from pathlib import Path
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


def get_docker_auth_config(
    registry: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    config_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Get Docker authentication configuration for registry operations
    
    Args:
        registry: Registry server URL (defaults to Docker Hub)
        username: Registry username (from environment variable)
        password: Registry password (from environment variable)  
        config_path: Custom Docker config path
        
    Returns:
        Auth config dict for Docker SDK, or None if no auth available
    """
    if not registry:
        registry = "https://index.docker.io/v1/"
    
    # Method 1: Use explicit credentials from environment variables
    if username and password:
        logger.info(f"Using explicit credentials for registry: {registry}")
        return {
            "username": username,
            "password": password,
            "serveraddress": registry
        }
    
    # Method 2: Try to read from Docker config file
    docker_config = get_docker_config(config_path)
    if docker_config:
        auth_config = extract_auth_from_config(docker_config, registry)
        if auth_config:
            logger.info(f"Using Docker config credentials for registry: {registry}")
            return auth_config
    
    # Method 3: Try credential helpers (basic implementation)
    cred_helper_auth = try_credential_helpers(registry)
    if cred_helper_auth:
        logger.info(f"Using credential helper for registry: {registry}")
        return cred_helper_auth
    
    logger.warning(f"No authentication configuration found for registry: {registry}")
    return None


def get_docker_config(config_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Read Docker configuration file"""
    if config_path:
        docker_config_path = Path(config_path)
    else:
        docker_config_path = Path.home() / ".docker" / "config.json"
    
    if not docker_config_path.exists():
        logger.debug(f"Docker config not found at: {docker_config_path}")
        return None
    
    try:
        with open(docker_config_path) as f:
            config = json.load(f)
        logger.debug(f"Loaded Docker config from: {docker_config_path}")
        return config
    except Exception as e:
        logger.warning(f"Failed to read Docker config: {e}")
        return None


def extract_auth_from_config(config: Dict[str, Any], registry: str) -> Optional[Dict[str, Any]]:
    """Extract authentication for a specific registry from Docker config"""
    # Check auths section
    auths = config.get("auths", {})
    
    # Try different registry URL formats
    registry_variants = [
        registry,
        registry.rstrip("/"),
        registry + "/",
        "https://index.docker.io/v1/",
        "index.docker.io",
        "docker.io",
        "registry-1.docker.io"
    ]
    
    for reg_url in registry_variants:
        if reg_url in auths:
            auth_data = auths[reg_url]
            
            # Handle base64 encoded auth
            if "auth" in auth_data:
                try:
                    decoded = base64.b64decode(auth_data["auth"]).decode()
                    username, password = decoded.split(":", 1)
                    return {
                        "username": username,
                        "password": password,
                        "serveraddress": registry
                    }
                except Exception as e:
                    logger.warning(f"Failed to decode auth for {reg_url}: {e}")
            
            # Handle separate username/password
            if "username" in auth_data and "password" in auth_data:
                return {
                    "username": auth_data["username"],
                    "password": auth_data["password"], 
                    "serveraddress": registry
                }
    
    return None


def try_credential_helpers(registry: str) -> Optional[Dict[str, Any]]:
    """Try to use Docker credential helpers (basic implementation)"""
    # This is a simplified implementation
    # In a production environment, you'd want to properly invoke credential helpers
    
    try:
        # Check if Docker Desktop credential helper is available
        if os.name == 'nt':  # Windows
            # Windows Docker Desktop stores credentials in the Windows Credential Manager
            pass
        else:  # Unix-like systems
            # Try common credential helper patterns
            pass
        
        # For now, return None - credential helpers are complex to implement properly
        return None
        
    except Exception as e:
        logger.debug(f"Credential helper failed: {e}")
        return None


def create_registry_auth_header(auth_config: Dict[str, Any]) -> Optional[str]:
    """Create X-Registry-Auth header for Docker API"""
    try:
        auth_json = json.dumps(auth_config)
        auth_header = base64.b64encode(auth_json.encode()).decode()
        return auth_header
    except Exception as e:
        logger.warning(f"Failed to create auth header: {e}")
        return None