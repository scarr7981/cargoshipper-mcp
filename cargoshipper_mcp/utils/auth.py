"""Authentication utilities for CargoShipper MCP server"""

from typing import Optional

from .errors import AuthenticationError


def validate_api_key(api_key: Optional[str], allowed_keys: list, required: bool = False) -> bool:
    """Validate API key if authentication is required"""
    if not required:
        return True
    
    if not api_key:
        raise AuthenticationError("API key required but not provided")
    
    if api_key not in allowed_keys:
        raise AuthenticationError("Invalid API key")
    
    return True


def validate_request(headers: dict, api_key_header: str, allowed_keys: list, required: bool = False) -> bool:
    """Validate incoming request"""
    api_key = headers.get(api_key_header)
    return validate_api_key(api_key, allowed_keys, required)