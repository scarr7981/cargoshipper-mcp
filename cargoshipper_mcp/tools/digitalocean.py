"""DigitalOcean API integration tools for CargoShipper MCP server"""

from typing import Dict, Any, List, Optional, Callable

from ..utils.validation import validate_required_fields, validate_ip_address, validate_dns_record_type
from ..utils.formatters import format_success_response, format_error_response, format_droplet_info
from ..utils.errors import CargoShipperError, ValidationError


def register_tools(mcp, get_client: Callable):
    """Register DigitalOcean tools with MCP server"""
    
    @mcp.tool()
    def do_list_droplets(
        per_page: int = 20,
        page: int = 1,
        tag_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """List DigitalOcean droplets
        
        Args:
            per_page: Number of droplets per page (1-200)
            page: Page number to retrieve
            tag_name: Optional tag to filter droplets
        """
        try:
            client = get_client()
            
            # Validate pagination parameters
            if per_page < 1 or per_page > 200:
                raise ValidationError("per_page must be between 1 and 200")
            if page < 1:
                raise ValidationError("page must be >= 1")
            
            # Build parameters
            params = {"per_page": per_page, "page": page}
            if tag_name:
                params["tag_name"] = tag_name
            
            droplets_resp = client.droplets.list(**params)
            droplets = droplets_resp.get('droplets', [])
            
            # Format droplets for consistent output
            droplet_list = [format_droplet_info(droplet) for droplet in droplets]
            
            return format_success_response({
                "droplets": droplet_list,
                "total": len(droplet_list),
                "page": page,
                "per_page": per_page,
                "tag_filter": tag_name
            }, "list_droplets")
            
        except ValidationError as e:
            return format_error_response(str(e), "list_droplets")
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "list_droplets")
    
    @mcp.tool()
    def do_get_droplet(droplet_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific droplet
        
        Args:
            droplet_id: DigitalOcean droplet ID
        """
        try:
            client = get_client()
            
            droplet_resp = client.droplets.get(droplet_id=droplet_id)
            droplet = droplet_resp.get('droplet', {})
            
            # Enhanced droplet information
            droplet_info = format_droplet_info(droplet)
            droplet_info.update({
                "vcpus": droplet.get("vcpus"),
                "memory": droplet.get("memory"),
                "disk": droplet.get("disk"),
                "locked": droplet.get("locked", False),
                "kernel": droplet.get("kernel", {}).get("name"),
                "next_backup_window": droplet.get("next_backup_window"),
                "backup_ids": droplet.get("backup_ids", []),
                "snapshot_ids": droplet.get("snapshot_ids", []),
                "features": droplet.get("features", []),
                "tags": droplet.get("tags", [])
            })
            
            return format_success_response(droplet_info, "get_droplet")
            
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "get_droplet")
    
    @mcp.tool()
    def do_create_droplet(
        name: str,
        region: str,
        size: str,
        image: str,
        ssh_keys: Optional[List[str]] = None,
        backups: bool = False,
        ipv6: bool = False,
        monitoring: bool = False,
        tags: Optional[List[str]] = None,
        user_data: Optional[str] = None,
        vpc_uuid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new DigitalOcean droplet
        
        Args:
            name: Droplet name
            region: DigitalOcean region (e.g., 'nyc3', 'sfo3')
            size: Droplet size (e.g., 's-1vcpu-1gb', 's-2vcpu-2gb')
            image: Image slug (e.g., 'ubuntu-22-04-x64')
            ssh_keys: List of SSH key IDs or fingerprints
            backups: Enable automated backups
            ipv6: Enable IPv6
            monitoring: Enable monitoring
            tags: List of tags to apply
            user_data: Cloud-init user data script
            vpc_uuid: VPC to place droplet in
        """
        try:
            client = get_client()
            
            # Validate required fields
            validate_required_fields({
                "name": name,
                "region": region,
                "size": size,
                "image": image
            }, ["name", "region", "size", "image"])
            
            # Build droplet request
            droplet_req = {
                "name": name,
                "region": region,
                "size": size,
                "image": image,
                "backups": backups,
                "ipv6": ipv6,
                "monitoring": monitoring
            }
            
            if ssh_keys:
                droplet_req["ssh_keys"] = ssh_keys
            if tags:
                droplet_req["tags"] = tags
            if user_data:
                droplet_req["user_data"] = user_data
            if vpc_uuid:
                droplet_req["vpc_uuid"] = vpc_uuid
            
            create_resp = client.droplets.create(body=droplet_req)
            new_droplet = create_resp.get('droplet', {})
            
            return format_success_response({
                "droplet": format_droplet_info(new_droplet),
                "action_id": create_resp.get('action', {}).get('id'),
                "estimated_time": "1-2 minutes for initial boot"
            }, "create_droplet")
            
        except ValidationError as e:
            return format_error_response(str(e), "create_droplet")
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "create_droplet")
    
    @mcp.tool()
    def do_delete_droplet(droplet_id: int) -> Dict[str, Any]:
        """Delete a DigitalOcean droplet
        
        Args:
            droplet_id: DigitalOcean droplet ID
        """
        try:
            client = get_client()
            
            # Get droplet info before deletion
            try:
                droplet_resp = client.droplets.get(droplet_id=droplet_id)
                droplet_name = droplet_resp.get('droplet', {}).get('name', 'Unknown')
            except:
                droplet_name = 'Unknown'
            
            # Delete droplet
            client.droplets.destroy(droplet_id=droplet_id)
            
            return format_success_response({
                "droplet_id": droplet_id,
                "droplet_name": droplet_name,
                "status": "deleted"
            }, "delete_droplet")
            
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "delete_droplet")
    
    @mcp.tool()
    def do_droplet_action(
        droplet_id: int,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Perform an action on a DigitalOcean droplet
        
        Args:
            droplet_id: DigitalOcean droplet ID
            action: Action type (power_on, power_off, reboot, power_cycle, shutdown, resize, snapshot, etc.)
            **kwargs: Additional parameters for specific actions
        """
        try:
            client = get_client()
            
            # Validate action type
            valid_actions = [
                "power_on", "power_off", "reboot", "power_cycle", "shutdown",
                "resize", "snapshot", "rebuild", "restore", "enable_backups", 
                "disable_backups", "enable_ipv6", "enable_private_networking"
            ]
            
            if action not in valid_actions:
                raise ValidationError(f"Invalid action. Must be one of: {', '.join(valid_actions)}")
            
            # Build action request
            action_req = {"type": action}
            
            # Add action-specific parameters
            if action == "resize" and "size" in kwargs:
                action_req["size"] = kwargs["size"]
                action_req["disk"] = kwargs.get("disk", True)
            elif action == "snapshot" and "name" in kwargs:
                action_req["name"] = kwargs["name"]
            elif action == "rebuild" and "image" in kwargs:
                action_req["image"] = kwargs["image"]
            elif action == "restore" and "image" in kwargs:
                action_req["image"] = kwargs["image"]
            
            # Execute action
            action_resp = client.droplet_actions.post(
                droplet_id=droplet_id,
                body=action_req
            )
            
            action_info = action_resp.get('action', {})
            
            return format_success_response({
                "droplet_id": droplet_id,
                "action": action,
                "action_id": action_info.get('id'),
                "status": action_info.get('status'),
                "started_at": action_info.get('started_at'),
                "resource_type": action_info.get('resource_type')
            }, "droplet_action")
            
        except ValidationError as e:
            return format_error_response(str(e), "droplet_action")
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "droplet_action")
    
    @mcp.tool()
    def do_list_images(
        image_type: Optional[str] = None,
        private: bool = False
    ) -> Dict[str, Any]:
        """List DigitalOcean images
        
        Args:
            image_type: Filter by type ('distribution', 'application', or None for all)
            private: Include private images (snapshots)
        """
        try:
            client = get_client()
            
            params = {}
            if image_type:
                if image_type not in ["distribution", "application"]:
                    raise ValidationError("image_type must be 'distribution' or 'application'")
                params["type"] = image_type
            if private:
                params["private"] = private
            
            images_resp = client.images.list(**params)
            images = images_resp.get('images', [])
            
            image_list = []
            for image in images:
                image_info = {
                    "id": image.get('id'),
                    "name": image.get('name'),
                    "slug": image.get('slug'),
                    "distribution": image.get('distribution'),
                    "public": image.get('public', False),
                    "regions": image.get('regions', []),
                    "created_at": image.get('created_at'),
                    "min_disk_size": image.get('min_disk_size'),
                    "size_gigabytes": image.get('size_gigabytes'),
                    "type": image.get('type'),
                    "status": image.get('status')
                }
                image_list.append(image_info)
            
            return format_success_response({
                "images": image_list,
                "total": len(image_list),
                "type_filter": image_type,
                "private": private
            }, "list_images")
            
        except ValidationError as e:
            return format_error_response(str(e), "list_images")
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "list_images")
    
    @mcp.tool()
    def do_list_domains() -> Dict[str, Any]:
        """List DigitalOcean domains"""
        try:
            client = get_client()
            
            domains_resp = client.domains.list()
            domains = domains_resp.get('domains', [])
            
            domain_list = []
            for domain in domains:
                domain_info = {
                    "name": domain.get('name'),
                    "ttl": domain.get('ttl'),
                    "zone_file": domain.get('zone_file')
                }
                domain_list.append(domain_info)
            
            return format_success_response({
                "domains": domain_list,
                "total": len(domain_list)
            }, "list_domains")
            
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "list_domains")
    
    @mcp.tool()
    def do_list_dns_records(domain_name: str) -> Dict[str, Any]:
        """List DNS records for a domain
        
        Args:
            domain_name: Domain name to list records for
        """
        try:
            client = get_client()
            
            records_resp = client.domains.list_records(domain_name=domain_name)
            records = records_resp.get('domain_records', [])
            
            record_list = []
            for record in records:
                record_info = {
                    "id": record.get('id'),
                    "type": record.get('type'),
                    "name": record.get('name'),
                    "data": record.get('data'),
                    "priority": record.get('priority'),
                    "port": record.get('port'),
                    "ttl": record.get('ttl'),
                    "weight": record.get('weight'),
                    "flags": record.get('flags'),
                    "tag": record.get('tag')
                }
                record_list.append(record_info)
            
            return format_success_response({
                "domain": domain_name,
                "records": record_list,
                "total": len(record_list)
            }, "list_dns_records")
            
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "list_dns_records")
    
    @mcp.tool()
    def do_create_dns_record(
        domain_name: str,
        record_type: str,
        name: str,
        data: str,
        priority: Optional[int] = None,
        port: Optional[int] = None,
        ttl: int = 3600,
        weight: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a DNS record
        
        Args:
            domain_name: Domain name
            record_type: DNS record type (A, AAAA, CNAME, MX, TXT, etc.)
            name: Record name (subdomain or @ for root)
            data: Record data (IP address, domain name, etc.)
            priority: Priority for MX/SRV records
            port: Port for SRV records
            ttl: Time to live in seconds
            weight: Weight for SRV records
        """
        try:
            client = get_client()
            
            # Validate inputs
            validate_dns_record_type(record_type)
            validate_required_fields({
                "domain_name": domain_name,
                "record_type": record_type,
                "name": name,
                "data": data
            }, ["domain_name", "record_type", "name", "data"])
            
            # Build record request
            record_req = {
                "type": record_type.upper(),
                "name": name,
                "data": data,
                "ttl": ttl
            }
            
            if priority is not None:
                record_req["priority"] = priority
            if port is not None:
                record_req["port"] = port
            if weight is not None:
                record_req["weight"] = weight
            
            record_resp = client.domains.create_record(
                domain_name=domain_name,
                body=record_req
            )
            
            new_record = record_resp.get('domain_record', {})
            
            return format_success_response({
                "domain": domain_name,
                "record": {
                    "id": new_record.get('id'),
                    "type": new_record.get('type'),
                    "name": new_record.get('name'),
                    "data": new_record.get('data'),
                    "ttl": new_record.get('ttl'),
                    "priority": new_record.get('priority'),
                    "port": new_record.get('port'),
                    "weight": new_record.get('weight')
                }
            }, "create_dns_record")
            
        except ValidationError as e:
            return format_error_response(str(e), "create_dns_record")
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "create_dns_record")
    
    @mcp.tool()
    def do_delete_dns_record(
        domain_name: str,
        record_id: int
    ) -> Dict[str, Any]:
        """Delete a DNS record
        
        Args:
            domain_name: Domain name
            record_id: DNS record ID
        """
        try:
            client = get_client()
            
            # Delete record
            client.domains.destroy_record(
                domain_name=domain_name,
                domain_record_id=record_id
            )
            
            return format_success_response({
                "domain": domain_name,
                "record_id": record_id,
                "status": "deleted"
            }, "delete_dns_record")
            
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "delete_dns_record")
    
    @mcp.tool()
    def do_get_account() -> Dict[str, Any]:
        """Get DigitalOcean account information"""
        try:
            client = get_client()
            
            account_resp = client.account.get()
            account = account_resp.get('account', {})
            
            account_info = {
                "uuid": account.get('uuid'),
                "email": account.get('email'),
                "status": account.get('status'),
                "status_message": account.get('status_message'),
                "droplet_limit": account.get('droplet_limit'),
                "floating_ip_limit": account.get('floating_ip_limit'),
                "volume_limit": account.get('volume_limit'),
                "email_verified": account.get('email_verified')
            }
            
            return format_success_response(account_info, "get_account")
            
        except Exception as e:
            return format_error_response(f"DigitalOcean API error: {e}", "get_account")