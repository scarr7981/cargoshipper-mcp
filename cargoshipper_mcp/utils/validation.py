"""Input validation utilities for CargoShipper MCP server"""

import re
from typing import Any, Dict, List

from .errors import ValidationError, CargoShipperError


def validate_container_name(name: str) -> bool:
    """Validate Docker container name"""
    if not name or not isinstance(name, str):
        raise ValidationError("Container name must be a non-empty string")
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
    if not zone or not isinstance(zone, str):
        raise ValidationError("Zone name must be a non-empty string")
    if not re.match(r'^[a-zA-Z0-9.-]+$', zone):
        raise ValidationError("Zone name contains invalid characters")
    return True


def validate_dns_record_type(record_type: str) -> bool:
    """Validate DNS record type"""
    if not record_type or not isinstance(record_type, str):
        raise ValidationError("DNS record type must be a non-empty string")
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


def validate_port(port: Any) -> bool:
    """Validate port number"""
    try:
        port_num = int(port)
        if not 1 <= port_num <= 65535:
            raise ValidationError("Port must be between 1 and 65535")
        return True
    except (ValueError, TypeError):
        raise ValidationError("Port must be a valid integer")


def validate_ip_address(ip: str) -> bool:
    """Basic IP address validation"""
    if not ip or not isinstance(ip, str):
        raise ValidationError("IP address must be a non-empty string")
    # Simple IPv4 validation
    parts = ip.split('.')
    if len(parts) == 4:
        try:
            for part in parts:
                num = int(part)
                if not 0 <= num <= 255:
                    raise ValidationError("Invalid IPv4 address")
            return True
        except ValueError:
            pass
    # Could add IPv6 validation here
    raise ValidationError("Invalid IP address format")


def validate_token_permissions(service: str, operation: str, constraints: Dict[str, Any]) -> None:
    """Validate if token has permissions for the requested operation"""
    if service not in constraints:
        # No constraints detected - assume allowed
        return
        
    constraint = constraints[service]
    
    # Check if token is read-only and operation is write
    write_operations = ['create', 'delete', 'update', 'modify', 'start', 'stop', 'restart']
    if constraint.get('read_only', False) and any(op in operation.lower() for op in write_operations):
        raise CargoShipperError(
            f"❌ READ-ONLY TOKEN: Cannot perform '{operation}' on {service}. "
            f"This token only allows read operations."
        )
    
    # Check specific operation restrictions
    restrictions = constraint.get('restrictions', [])
    operation_lower = operation.lower()
    
    for restriction in restrictions:
        if operation_lower in restriction.lower():
            raise CargoShipperError(
                f"❌ PERMISSION DENIED: Token cannot perform '{operation}' on {service}. "
                f"Restriction: {restriction}"
            )
    
    # Check if operation is in allowed permissions
    permissions = constraint.get('permissions', [])
    if permissions:  # If we have explicit permissions, check them
        operation_allowed = any(
            operation_lower in perm.lower() or 
            operation.replace('_', '.').lower() in perm.lower()
            for perm in permissions
        )
        if not operation_allowed:
            raise CargoShipperError(
                f"❌ INSUFFICIENT PERMISSIONS: Token cannot perform '{operation}' on {service}. "
                f"Available permissions: {', '.join(permissions)}"
            )


def get_permission_guidance(service: str, constraints: Dict[str, Any]) -> str:
    """Get helpful guidance about what the token can do"""
    if service not in constraints:
        return f"✅ {service} appears to be fully accessible"
        
    constraint = constraints[service]
    guidance = []
    
    if constraint.get('read_only'):
        guidance.append("⚠️  This token is READ-ONLY - you can view but not modify resources")
    
    if constraint.get('permissions'):
        guidance.append(f"✅ Available operations: {', '.join(constraint['permissions'])}")
    
    if constraint.get('restrictions'):
        guidance.append(f"❌ Blocked operations: {', '.join(constraint['restrictions'])}")
        
    if constraint.get('allowed_resources'):
        resources = constraint['allowed_resources']
        if len(resources) <= 5:
            guidance.append(f"🎯 Allowed resources: {', '.join(resources)}")
        else:
            guidance.append(f"🎯 Allowed resources: {', '.join(resources[:3])} (and {len(resources)-3} more)")
    
    return '\n'.join(guidance) if guidance else f"✅ {service} appears to be fully accessible"