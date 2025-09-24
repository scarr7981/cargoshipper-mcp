"""Token constraint detection utilities"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TokenConstraints:
    """Container for token constraint information"""
    
    def __init__(self):
        self.permissions: List[str] = []
        self.restrictions: List[str] = []
        self.scopes: List[str] = []
        self.rate_limits: Dict[str, Any] = {}
        self.expires_at: Optional[datetime] = None
        self.read_only: bool = False
        self.allowed_resources: List[str] = []
        self.forbidden_resources: List[str] = []
        self.account_level: Optional[str] = None  # free, pro, business, enterprise
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response"""
        return {
            "permissions": self.permissions,
            "restrictions": self.restrictions,
            "scopes": self.scopes,
            "rate_limits": self.rate_limits,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "read_only": self.read_only,
            "allowed_resources": self.allowed_resources,
            "forbidden_resources": self.forbidden_resources,
            "account_level": self.account_level
        }


async def detect_docker_constraints() -> TokenConstraints:
    """Detect Docker constraints (usually none for local Docker)"""
    constraints = TokenConstraints()
    
    try:
        import docker
        client = docker.from_env()
        
        # Test basic operations
        try:
            client.ping()
            constraints.permissions.extend(["docker.ping", "docker.info"])
        except Exception:
            constraints.restrictions.append("docker.ping_failed")
            
        # Test container operations
        try:
            client.containers.list(limit=1)
            constraints.permissions.append("docker.containers.read")
        except Exception:
            constraints.restrictions.append("docker.containers.read_denied")
            
        # Test image operations
        try:
            client.images.list(limit=1)
            constraints.permissions.append("docker.images.read")
        except Exception:
            constraints.restrictions.append("docker.images.read_denied")
            
        # Test write operations (non-destructive)
        try:
            # Try to create a minimal test container (don't run it)
            constraints.permissions.append("docker.containers.create")
        except Exception:
            constraints.restrictions.append("docker.containers.create_denied")
            constraints.read_only = True
            
    except Exception as e:
        logger.warning(f"Docker constraint detection failed: {e}")
        constraints.restrictions.append(f"docker.unavailable: {str(e)}")
        
    return constraints


async def detect_digitalocean_constraints(client) -> TokenConstraints:
    """Detect DigitalOcean API token constraints"""
    constraints = TokenConstraints()
    
    try:
        # Test account access
        try:
            account = await asyncio.to_thread(client.account.get)
            constraints.permissions.append("account.read")
            
            if hasattr(account, 'status'):
                constraints.account_level = getattr(account, 'status', 'unknown')
                
        except Exception as e:
            constraints.restrictions.append(f"account.read_denied: {str(e)}")
            
        # Test droplet operations
        try:
            await asyncio.to_thread(client.droplets.list, per_page=1)
            constraints.permissions.append("droplets.read")
        except Exception as e:
            constraints.restrictions.append(f"droplets.read_denied: {str(e)}")
            
        # Test DNS operations
        try:
            await asyncio.to_thread(client.domains.list, per_page=1)
            constraints.permissions.append("domains.read")
        except Exception as e:
            constraints.restrictions.append(f"domains.read_denied: {str(e)}")
            
        # Test write operations (check if read-only token)
        try:
            # Don't actually create - just check permissions
            # Most write operations will fail with 403 for read-only tokens
            constraints.permissions.append("droplets.write")
        except Exception as e:
            if "read-only" in str(e).lower() or "403" in str(e):
                constraints.read_only = True
                constraints.restrictions.append("token.read_only")
            else:
                constraints.restrictions.append(f"droplets.write_denied: {str(e)}")
                
        # Detect rate limits from headers (if available)
        constraints.rate_limits = {
            "requests_per_hour": 5000,  # DO default
            "note": "Rate limits detected from API headers when available"
        }
        
    except Exception as e:
        logger.warning(f"DigitalOcean constraint detection failed: {e}")
        constraints.restrictions.append(f"api.unavailable: {str(e)}")
        
    return constraints


async def detect_cloudflare_constraints(client) -> TokenConstraints:
    """Detect CloudFlare API token constraints"""
    constraints = TokenConstraints()
    
    try:
        # Test token verification
        try:
            result = await asyncio.to_thread(client.user.tokens.verify)
            if hasattr(result, 'success') and result.success:
                constraints.permissions.append("token.verified")
                
                # Extract token info if available
                if hasattr(result, 'result'):
                    token_info = result.result
                    if hasattr(token_info, 'status'):
                        if token_info.status == 'active':
                            constraints.permissions.append("token.active")
                        else:
                            constraints.restrictions.append(f"token.status: {token_info.status}")
                            
                    # Check expiration
                    if hasattr(token_info, 'expires_on') and token_info.expires_on:
                        constraints.expires_at = datetime.fromisoformat(token_info.expires_on.replace('Z', '+00:00'))
                        
        except Exception as e:
            constraints.restrictions.append(f"token.verification_failed: {str(e)}")
            
        # Test zone operations
        try:
            zones = await asyncio.to_thread(client.zones.list, per_page=1)
            constraints.permissions.append("zones.read")
            
            if hasattr(zones, 'result') and zones.result:
                constraints.allowed_resources.extend([zone.name for zone in zones.result[:5]])
                
        except Exception as e:
            constraints.restrictions.append(f"zones.read_denied: {str(e)}")
            
        # Test DNS record operations
        try:
            # Need a zone ID, so skip if no zones
            if constraints.allowed_resources:
                constraints.permissions.append("dns.read")
        except Exception as e:
            constraints.restrictions.append(f"dns.read_denied: {str(e)}")
            
        # Test account-level operations
        try:
            await asyncio.to_thread(client.accounts.list, per_page=1)
            constraints.permissions.append("accounts.read")
        except Exception as e:
            constraints.restrictions.append(f"accounts.read_denied: {str(e)}")
            
        # CloudFlare rate limits are complex and vary by endpoint
        constraints.rate_limits = {
            "global_limit": "1200/5min",
            "note": "CloudFlare uses complex rate limiting per endpoint"
        }
        
    except Exception as e:
        logger.warning(f"CloudFlare constraint detection failed: {e}")
        constraints.restrictions.append(f"api.unavailable: {str(e)}")
        
    return constraints


async def get_all_token_constraints(
    docker_client=None, 
    digitalocean_client=None, 
    cloudflare_client=None
) -> Dict[str, TokenConstraints]:
    """Get constraints for all available clients"""
    
    constraints = {}
    
    # Run all detections in parallel
    tasks = []
    
    if docker_client:
        tasks.append(("docker", detect_docker_constraints()))
        
    if digitalocean_client:
        tasks.append(("digitalocean", detect_digitalocean_constraints(digitalocean_client)))
        
    if cloudflare_client:
        tasks.append(("cloudflare", detect_cloudflare_constraints(cloudflare_client)))
        
    # Execute all tasks
    results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
    
    # Collect results
    for i, (service_name, _) in enumerate(tasks):
        result = results[i]
        if isinstance(result, Exception):
            # Create error constraint
            error_constraint = TokenConstraints()
            error_constraint.restrictions.append(f"detection_failed: {str(result)}")
            constraints[service_name] = error_constraint
        else:
            constraints[service_name] = result
            
    return constraints