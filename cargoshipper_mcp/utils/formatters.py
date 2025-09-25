"""Response formatting utilities for CargoShipper MCP server"""

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


def format_container_info(container) -> Dict[str, Any]:
    """Format Docker container information for consistent output"""
    # Handle missing or None image gracefully
    image_name = "<missing>"
    if container.image:
        if container.image.tags:
            image_name = container.image.tags[0]
        else:
            image_name = container.image.id[:12]
    
    return {
        "id": container.id[:12],
        "name": container.name,
        "image": image_name,
        "status": container.status,
        "created": container.attrs["Created"],
        "ports": container.attrs["NetworkSettings"]["Ports"]
    }


def format_droplet_info(droplet) -> Dict[str, Any]:
    """Format DigitalOcean droplet information for consistent output"""
    return {
        "id": droplet.get("id"),
        "name": droplet.get("name"),
        "status": droplet.get("status"),
        "region": droplet.get("region", {}).get("name"),
        "size": droplet.get("size", {}).get("slug"),
        "image": droplet.get("image", {}).get("name"),
        "ip_address": droplet.get("networks", {}).get("v4", [{}])[0].get("ip_address"),
        "created_at": droplet.get("created_at")
    }


def format_zone_info(zone) -> Dict[str, Any]:
    """Format CloudFlare zone information for consistent output"""
    return {
        "id": zone.get("id"),
        "name": zone.get("name"),
        "status": zone.get("status"),
        "name_servers": zone.get("name_servers", []),
        "created_on": zone.get("created_on"),
        "modified_on": zone.get("modified_on")
    }