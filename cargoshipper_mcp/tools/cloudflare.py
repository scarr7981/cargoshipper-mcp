"""CloudFlare API integration tools for CargoShipper MCP server"""

from typing import Dict, Any, List, Optional, Callable

from ..utils.validation import validate_required_fields, validate_dns_record_type, validate_zone_name
from ..utils.formatters import format_success_response, format_error_response, format_zone_info
from ..utils.errors import CargoShipperError, ValidationError


def register_tools(mcp, get_client: Callable):
    """Register CloudFlare tools with MCP server"""
    
    @mcp.tool()
    def cf_list_zones(
        per_page: int = 50,
        page: int = 1,
        name: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List CloudFlare zones
        
        Args:
            per_page: Number of zones per page (5-50)
            page: Page number to retrieve  
            name: Filter by zone name
            status: Filter by status (active, pending, initializing, moved, deleted, deactivated)
        """
        try:
            client = get_client()
            
            # Validate pagination
            if per_page < 5 or per_page > 50:
                raise ValidationError("per_page must be between 5 and 50")
            if page < 1:
                raise ValidationError("page must be >= 1")
            
            # Build filters
            params = {"per_page": per_page, "page": page}
            if name:
                validate_zone_name(name)
                params["name"] = name
            if status:
                valid_statuses = ["active", "pending", "initializing", "moved", "deleted", "deactivated"]
                if status not in valid_statuses:
                    raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
                params["status"] = status
            
            zones_resp = client.zones.list(**params)
            
            zone_list = []
            for zone in zones_resp:
                zone_info = format_zone_info(zone.__dict__)
                zone_list.append(zone_info)
            
            return format_success_response({
                "zones": zone_list,
                "total": len(zone_list),
                "page": page,
                "per_page": per_page,
                "filters": {k: v for k, v in params.items() if k not in ["page", "per_page"]}
            }, "list_zones")
            
        except ValidationError as e:
            return format_error_response(str(e), "list_zones")
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "list_zones")
    
    @mcp.tool()
    def cf_get_zone(zone_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific zone
        
        Args:
            zone_id: CloudFlare zone ID
        """
        try:
            client = get_client()
            
            zone_resp = client.zones.get(zone_id=zone_id)
            zone_info = format_zone_info(zone_resp.__dict__)
            
            # Add additional details
            zone_info.update({
                "paused": getattr(zone_resp, 'paused', None),
                "development_mode": getattr(zone_resp, 'development_mode', None),
                "original_name_servers": getattr(zone_resp, 'original_name_servers', []),
                "original_registrar": getattr(zone_resp, 'original_registrar', None),
                "original_dnshost": getattr(zone_resp, 'original_dnshost', None),
                "type": getattr(zone_resp, 'type', None),
                "verification_key": getattr(zone_resp, 'verification_key', None)
            })
            
            return format_success_response(zone_info, "get_zone")
            
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "get_zone")
    
    @mcp.tool()
    def cf_create_zone(
        name: str,
        account_id: str,
        jump_start: bool = True,
        zone_type: str = "full"
    ) -> Dict[str, Any]:
        """Create a new CloudFlare zone
        
        Args:
            name: Domain name for the zone
            account_id: CloudFlare account ID
            jump_start: Import existing DNS records automatically
            zone_type: Zone type ('full' or 'partial')
        """
        try:
            client = get_client()
            
            # Validate inputs
            validate_zone_name(name)
            validate_required_fields({
                "name": name,
                "account_id": account_id
            }, ["name", "account_id"])
            
            if zone_type not in ["full", "partial"]:
                raise ValidationError("zone_type must be 'full' or 'partial'")
            
            # Create zone
            zone_req = {
                "name": name,
                "account": {"id": account_id},
                "jump_start": jump_start,
                "type": zone_type
            }
            
            new_zone = client.zones.create(body=zone_req)
            zone_info = format_zone_info(new_zone.__dict__)
            
            return format_success_response({
                "zone": zone_info,
                "instructions": "Update your domain's nameservers to the ones listed above",
                "jump_start": jump_start
            }, "create_zone")
            
        except ValidationError as e:
            return format_error_response(str(e), "create_zone")
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "create_zone")
    
    @mcp.tool()
    def cf_delete_zone(zone_id: str) -> Dict[str, Any]:
        """Delete a CloudFlare zone
        
        Args:
            zone_id: CloudFlare zone ID
        """
        try:
            client = get_client()
            
            # Get zone name before deletion
            try:
                zone = client.zones.get(zone_id=zone_id)
                zone_name = getattr(zone, 'name', 'Unknown')
            except:
                zone_name = 'Unknown'
            
            # Delete zone
            client.zones.delete(zone_id=zone_id)
            
            return format_success_response({
                "zone_id": zone_id,
                "zone_name": zone_name,
                "status": "deleted"
            }, "delete_zone")
            
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "delete_zone")
    
    @mcp.tool()
    def cf_list_dns_records(
        zone_id: str,
        record_type: Optional[str] = None,
        name: Optional[str] = None,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """List DNS records for a zone
        
        Args:
            zone_id: CloudFlare zone ID
            record_type: Filter by record type (A, AAAA, CNAME, etc.)
            name: Filter by record name
            content: Filter by record content
        """
        try:
            client = get_client()
            
            # Build filters
            filters = {}
            if record_type:
                validate_dns_record_type(record_type)
                filters["type"] = record_type.upper()
            if name:
                filters["name"] = name
            if content:
                filters["content"] = content
            
            records_resp = client.dns.records.list(zone_id=zone_id, **filters)
            
            record_list = []
            for record in records_resp:
                record_info = {
                    "id": getattr(record, 'id', None),
                    "type": getattr(record, 'type', None),
                    "name": getattr(record, 'name', None),
                    "content": getattr(record, 'content', None),
                    "ttl": getattr(record, 'ttl', None),
                    "proxied": getattr(record, 'proxied', None),
                    "priority": getattr(record, 'priority', None),
                    "created_on": getattr(record, 'created_on', None),
                    "modified_on": getattr(record, 'modified_on', None),
                    "proxiable": getattr(record, 'proxiable', None),
                    "locked": getattr(record, 'locked', None)
                }
                record_list.append(record_info)
            
            return format_success_response({
                "zone_id": zone_id,
                "records": record_list,
                "total": len(record_list),
                "filters": filters
            }, "list_dns_records")
            
        except ValidationError as e:
            return format_error_response(str(e), "list_dns_records")
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "list_dns_records")
    
    @mcp.tool()
    def cf_create_dns_record(
        zone_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 1,
        proxied: bool = False,
        priority: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a DNS record
        
        Args:
            zone_id: CloudFlare zone ID
            record_type: DNS record type (A, AAAA, CNAME, MX, TXT, etc.)
            name: Record name (subdomain or @ for root)
            content: Record content (IP address, domain name, etc.)
            ttl: Time to live (1 = Auto, 120-7200 seconds)
            proxied: Whether to proxy through CloudFlare (orange cloud)
            priority: Priority for MX records
        """
        try:
            client = get_client()
            
            # Validate inputs
            validate_dns_record_type(record_type)
            validate_required_fields({
                "zone_id": zone_id,
                "record_type": record_type,
                "name": name,
                "content": content
            }, ["zone_id", "record_type", "name", "content"])
            
            # Validate TTL
            if ttl != 1 and (ttl < 120 or ttl > 7200):
                raise ValidationError("TTL must be 1 (Auto) or between 120-7200 seconds")
            
            # Build record request
            record_req = {
                "type": record_type.upper(),
                "name": name,
                "content": content,
                "ttl": ttl
            }
            
            # Add proxied setting for compatible record types
            proxy_compatible = ["A", "AAAA", "CNAME"]
            if record_type.upper() in proxy_compatible:
                record_req["proxied"] = proxied
            
            # Add priority for MX records
            if record_type.upper() == "MX":
                if priority is None:
                    raise ValidationError("Priority is required for MX records")
                record_req["priority"] = priority
            
            new_record = client.dns.records.create(zone_id=zone_id, **record_req)
            
            record_info = {
                "id": getattr(new_record, 'id', None),
                "type": getattr(new_record, 'type', None),
                "name": getattr(new_record, 'name', None),
                "content": getattr(new_record, 'content', None),
                "ttl": getattr(new_record, 'ttl', None),
                "proxied": getattr(new_record, 'proxied', None),
                "priority": getattr(new_record, 'priority', None)
            }
            
            return format_success_response({
                "zone_id": zone_id,
                "record": record_info
            }, "create_dns_record")
            
        except ValidationError as e:
            return format_error_response(str(e), "create_dns_record")
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "create_dns_record")
    
    @mcp.tool()
    def cf_update_dns_record(
        zone_id: str,
        record_id: str,
        record_type: Optional[str] = None,
        name: Optional[str] = None,
        content: Optional[str] = None,
        ttl: Optional[int] = None,
        proxied: Optional[bool] = None,
        priority: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update a DNS record
        
        Args:
            zone_id: CloudFlare zone ID
            record_id: DNS record ID
            record_type: DNS record type (if changing)
            name: Record name (if changing)
            content: Record content (if changing)
            ttl: Time to live (if changing)
            proxied: Proxy status (if changing)
            priority: Priority for MX records (if changing)
        """
        try:
            client = get_client()
            
            # Get current record to preserve unchanged values
            current_record = client.dns.records.get(zone_id=zone_id, dns_record_id=record_id)
            
            # Build update request with current values as defaults
            record_req = {
                "type": record_type or getattr(current_record, 'type'),
                "name": name or getattr(current_record, 'name'),
                "content": content or getattr(current_record, 'content'),
                "ttl": ttl or getattr(current_record, 'ttl')
            }
            
            # Validate record type if provided
            if record_type:
                validate_dns_record_type(record_type)
            
            # Handle proxied setting
            if proxied is not None:
                record_req["proxied"] = proxied
            elif hasattr(current_record, 'proxied'):
                record_req["proxied"] = getattr(current_record, 'proxied')
            
            # Handle priority for MX records
            current_priority = getattr(current_record, 'priority', None)
            if priority is not None:
                record_req["priority"] = priority
            elif current_priority is not None:
                record_req["priority"] = current_priority
            
            # Update record
            updated_record = client.dns.records.update(
                zone_id=zone_id,
                dns_record_id=record_id,
                **record_req
            )
            
            record_info = {
                "id": getattr(updated_record, 'id', None),
                "type": getattr(updated_record, 'type', None),
                "name": getattr(updated_record, 'name', None),
                "content": getattr(updated_record, 'content', None),
                "ttl": getattr(updated_record, 'ttl', None),
                "proxied": getattr(updated_record, 'proxied', None),
                "priority": getattr(updated_record, 'priority', None)
            }
            
            return format_success_response({
                "zone_id": zone_id,
                "record": record_info
            }, "update_dns_record")
            
        except ValidationError as e:
            return format_error_response(str(e), "update_dns_record")
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "update_dns_record")
    
    @mcp.tool()
    def cf_delete_dns_record(
        zone_id: str,
        record_id: str
    ) -> Dict[str, Any]:
        """Delete a DNS record
        
        Args:
            zone_id: CloudFlare zone ID
            record_id: DNS record ID
        """
        try:
            client = get_client()
            
            # Get record info before deletion
            try:
                record = client.dns.records.get(zone_id=zone_id, dns_record_id=record_id)
                record_name = getattr(record, 'name', 'Unknown')
                record_type = getattr(record, 'type', 'Unknown')
            except:
                record_name = 'Unknown'
                record_type = 'Unknown'
            
            # Delete record
            client.dns.records.delete(zone_id=zone_id, dns_record_id=record_id)
            
            return format_success_response({
                "zone_id": zone_id,
                "record_id": record_id,
                "record_name": record_name,
                "record_type": record_type,
                "status": "deleted"
            }, "delete_dns_record")
            
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "delete_dns_record")
    
    @mcp.tool()
    def cf_purge_cache(
        zone_id: str,
        purge_everything: bool = False,
        files: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        hosts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Purge CloudFlare cache
        
        Args:
            zone_id: CloudFlare zone ID
            purge_everything: Purge all cache (use carefully)
            files: List of specific URLs to purge
            tags: List of cache tags to purge
            hosts: List of hostnames to purge
        """
        try:
            client = get_client()
            
            # Validate that at least one purge method is specified
            if not any([purge_everything, files, tags, hosts]):
                raise ValidationError("Must specify at least one purge method")
            
            # Build purge request
            purge_req = {}
            
            if purge_everything:
                purge_req["purge_everything"] = True
            else:
                if files:
                    purge_req["files"] = files
                if tags:
                    purge_req["tags"] = tags
                if hosts:
                    purge_req["hosts"] = hosts
            
            # Execute purge
            purge_resp = client.zones.purge_cache.create(zone_id=zone_id, body=purge_req)
            
            return format_success_response({
                "zone_id": zone_id,
                "purge_id": getattr(purge_resp, 'id', None),
                "purge_everything": purge_everything,
                "files_count": len(files) if files else 0,
                "tags_count": len(tags) if tags else 0,
                "hosts_count": len(hosts) if hosts else 0,
                "message": "Cache purge initiated successfully"
            }, "purge_cache")
            
        except ValidationError as e:
            return format_error_response(str(e), "purge_cache")
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "purge_cache")
    
    @mcp.tool()
    def cf_get_zone_settings(zone_id: str) -> Dict[str, Any]:
        """Get CloudFlare zone settings
        
        Args:
            zone_id: CloudFlare zone ID
        """
        try:
            client = get_client()
            
            settings_resp = client.zones.settings.get(zone_id=zone_id)
            
            # Extract key settings
            settings_info = {}
            for setting in settings_resp:
                setting_dict = setting.__dict__
                settings_info[setting_dict.get('id', 'unknown')] = {
                    "value": setting_dict.get('value'),
                    "editable": setting_dict.get('editable'),
                    "modified_on": setting_dict.get('modified_on')
                }
            
            return format_success_response({
                "zone_id": zone_id,
                "settings": settings_info,
                "total_settings": len(settings_info)
            }, "get_zone_settings")
            
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "get_zone_settings")
    
    @mcp.tool()
    def cf_update_zone_setting(
        zone_id: str,
        setting: str,
        value: Any
    ) -> Dict[str, Any]:
        """Update a specific zone setting
        
        Args:
            zone_id: CloudFlare zone ID
            setting: Setting name (e.g., 'ssl', 'always_use_https', 'security_level')
            value: New value for the setting
        """
        try:
            client = get_client()
            
            # Validate common settings
            valid_settings = {
                "ssl": ["off", "flexible", "full", "strict"],
                "always_use_https": ["on", "off"],
                "security_level": ["off", "essentially_off", "low", "medium", "high", "under_attack"],
                "cache_level": ["aggressive", "basic", "simplified"],
                "development_mode": ["on", "off"],
                "minify": {"css": ["on", "off"], "html": ["on", "off"], "js": ["on", "off"]}
            }
            
            if setting in valid_settings and isinstance(valid_settings[setting], list):
                if value not in valid_settings[setting]:
                    raise ValidationError(f"Invalid value for {setting}. Must be one of: {', '.join(valid_settings[setting])}")
            
            # Update setting using the appropriate endpoint
            if hasattr(client.zones.settings, setting):
                setting_client = getattr(client.zones.settings, setting)
                updated_setting = setting_client.update(zone_id=zone_id, value=value)
            else:
                raise ValidationError(f"Unknown setting: {setting}")
            
            return format_success_response({
                "zone_id": zone_id,
                "setting": setting,
                "value": getattr(updated_setting, 'value', value),
                "modified_on": getattr(updated_setting, 'modified_on', None)
            }, "update_zone_setting")
            
        except ValidationError as e:
            return format_error_response(str(e), "update_zone_setting")
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "update_zone_setting")
    
    @mcp.tool()
    def cf_get_analytics(
        zone_id: str,
        since: str,
        until: str,
        continuous: bool = True
    ) -> Dict[str, Any]:
        """Get zone analytics
        
        Args:
            zone_id: CloudFlare zone ID
            since: Start time (ISO 8601 format)
            until: End time (ISO 8601 format)
            continuous: Return continuous data (True) or time series (False)
        """
        try:
            client = get_client()
            
            analytics_resp = client.zones.analytics.dashboard.get(
                zone_id=zone_id,
                since=since,
                until=until,
                continuous=continuous
            )
            
            # Extract analytics data
            if hasattr(analytics_resp, 'totals'):
                totals = analytics_resp.totals.__dict__
                analytics_data = {
                    "totals": {
                        "requests": totals.get('requests', {}),
                        "bandwidth": totals.get('bandwidth', {}),
                        "threats": totals.get('threats', {}),
                        "pageviews": totals.get('pageviews', {}),
                        "uniques": totals.get('uniques', {})
                    },
                    "since": since,
                    "until": until,
                    "continuous": continuous
                }
            else:
                analytics_data = {
                    "message": "Analytics data format not recognized",
                    "raw_data": str(analytics_resp)
                }
            
            return format_success_response({
                "zone_id": zone_id,
                "analytics": analytics_data
            }, "get_analytics")
            
        except Exception as e:
            return format_error_response(f"CloudFlare API error: {e}", "get_analytics")