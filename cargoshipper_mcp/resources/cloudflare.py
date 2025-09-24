"""CloudFlare resources for CargoShipper MCP server"""

from typing import Callable
from ..utils.formatters import format_zone_info


def register_resources(mcp, get_client: Callable):
    """Register CloudFlare resources"""
    
    @mcp.resource("cloudflare://zones")
    def list_zones_resource() -> str:
        """Resource to list all CloudFlare zones"""
        try:
            client = get_client()
            zones_resp = client.zones.list()
            
            if not zones_resp:
                return "# CloudFlare Zones\n\nNo zones found."
            
            output = ["# CloudFlare Zones\n"]
            active_count = 0
            pending_count = 0
            other_count = 0
            
            for zone in zones_resp:
                status = getattr(zone, 'status', 'unknown')
                status_emoji = "🟢" if status == "active" else "🟡" if status == "pending" else "🔴"
                
                if status == "active":
                    active_count += 1
                elif status == "pending":
                    pending_count += 1
                else:
                    other_count += 1
                
                zone_info = format_zone_info(zone.__dict__)
                
                output.append(f"## {status_emoji} {zone_info['name']}")
                output.append(f"- **ID**: {zone_info['id']}")
                output.append(f"- **Status**: {zone_info['status']}")
                output.append(f"- **Created**: {zone_info.get('created_on', 'N/A')}")
                output.append(f"- **Modified**: {zone_info.get('modified_on', 'N/A')}")
                
                # Name servers
                name_servers = zone_info.get('name_servers', [])
                if name_servers:
                    output.append(f"- **Name Servers**: {', '.join(name_servers)}")
                
                # Zone settings
                paused = getattr(zone, 'paused', None)
                dev_mode = getattr(zone, 'development_mode', None)
                
                settings = []
                if paused is not None:
                    settings.append(f"Paused: {'Yes' if paused else 'No'}")
                if dev_mode is not None:
                    settings.append(f"Dev Mode: {'On' if dev_mode else 'Off'}")
                
                if settings:
                    output.append(f"- **Settings**: {', '.join(settings)}")
                
                output.append("")
            
            summary = f"**Summary**: {active_count} active, {pending_count} pending"
            if other_count > 0:
                summary += f", {other_count} other"
            output.insert(1, summary + "\n")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# CloudFlare Zones\n\nError accessing CloudFlare: {e}"
    
    @mcp.resource("cloudflare://zone/{zone_id}")
    def get_zone_resource(zone_id: str) -> str:
        """Resource to get detailed information about a specific zone"""
        try:
            client = get_client()
            zone_resp = client.zones.get(zone_id=zone_id)
            
            output = [f"# Zone: {getattr(zone_resp, 'name', 'Unknown')}\n"]
            
            # Basic information
            output.append("## Basic Information")
            output.append(f"- **ID**: {getattr(zone_resp, 'id', 'N/A')}")
            output.append(f"- **Name**: {getattr(zone_resp, 'name', 'N/A')}")
            output.append(f"- **Status**: {getattr(zone_resp, 'status', 'N/A')}")
            output.append(f"- **Type**: {getattr(zone_resp, 'type', 'N/A')}")
            output.append(f"- **Created**: {getattr(zone_resp, 'created_on', 'N/A')}")
            output.append(f"- **Modified**: {getattr(zone_resp, 'modified_on', 'N/A')}")
            
            # Zone settings
            output.append("\n## Zone Settings")
            paused = getattr(zone_resp, 'paused', None)
            dev_mode = getattr(zone_resp, 'development_mode', None)
            
            output.append(f"- **Paused**: {'Yes' if paused else 'No'}")
            output.append(f"- **Development Mode**: {'On' if dev_mode else 'Off'}")
            
            verification_key = getattr(zone_resp, 'verification_key', None)
            if verification_key:
                output.append(f"- **Verification Key**: {verification_key}")
            
            # Name servers
            name_servers = getattr(zone_resp, 'name_servers', [])
            if name_servers:
                output.append("\n## CloudFlare Name Servers")
                for i, ns in enumerate(name_servers, 1):
                    output.append(f"{i}. {ns}")
            
            # Original name servers
            original_ns = getattr(zone_resp, 'original_name_servers', [])
            if original_ns:
                output.append("\n## Original Name Servers")
                for i, ns in enumerate(original_ns, 1):
                    output.append(f"{i}. {ns}")
            
            # Original registrar
            original_registrar = getattr(zone_resp, 'original_registrar', None)
            if original_registrar:
                output.append(f"\n## Original Configuration")
                output.append(f"- **Original Registrar**: {original_registrar}")
            
            original_dnshost = getattr(zone_resp, 'original_dnshost', None)
            if original_dnshost:
                output.append(f"- **Original DNS Host**: {original_dnshost}")
            
            # Account information
            account = getattr(zone_resp, 'account', None)
            if account:
                account_dict = account.__dict__ if hasattr(account, '__dict__') else account
                if isinstance(account_dict, dict):
                    output.append(f"\n## Account")
                    output.append(f"- **Account ID**: {account_dict.get('id', 'N/A')}")
                    output.append(f"- **Account Name**: {account_dict.get('name', 'N/A')}")
            
            # Plan information  
            plan = getattr(zone_resp, 'plan', None)
            if plan:
                plan_dict = plan.__dict__ if hasattr(plan, '__dict__') else plan
                if isinstance(plan_dict, dict):
                    output.append(f"\n## Plan")
                    output.append(f"- **Plan Name**: {plan_dict.get('name', 'N/A')}")
                    output.append(f"- **Plan ID**: {plan_dict.get('id', 'N/A')}")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# Zone Error\n\nError accessing zone `{zone_id}`: {e}"
    
    @mcp.resource("cloudflare://zone/{zone_id}/dns")
    def zone_dns_records_resource(zone_id: str) -> str:
        """Resource to list DNS records for a specific zone"""
        try:
            client = get_client()
            
            # Get zone name first
            try:
                zone = client.zones.get(zone_id=zone_id)
                zone_name = getattr(zone, 'name', 'Unknown')
            except:
                zone_name = 'Unknown'
            
            records_resp = client.dns_records.list(zone_id=zone_id)
            
            if not records_resp:
                return f"# DNS Records for {zone_name}\n\nNo DNS records found."
            
            output = [f"# DNS Records for {zone_name}\n"]
            output.append(f"**Total Records**: {len(list(records_resp))}\n")
            
            # Group records by type
            record_types = {}
            for record in records_resp:
                record_type = getattr(record, 'type', 'UNKNOWN')
                if record_type not in record_types:
                    record_types[record_type] = []
                record_types[record_type].append(record)
            
            for record_type, type_records in record_types.items():
                output.append(f"## {record_type} Records ({len(type_records)})")
                
                for record in type_records:
                    name = getattr(record, 'name', 'N/A')
                    content = getattr(record, 'content', 'N/A')
                    ttl = getattr(record, 'ttl', 'N/A')
                    proxied = getattr(record, 'proxied', None)
                    priority = getattr(record, 'priority', None)
                    record_id = getattr(record, 'id', 'N/A')
                    
                    # Format name for display
                    display_name = name.replace(f'.{zone_name}', '') if name.endswith(f'.{zone_name}') else name
                    if display_name == zone_name:
                        display_name = '@'
                    
                    output.append(f"### {display_name}")
                    output.append(f"- **ID**: {record_id}")
                    output.append(f"- **Content**: {content}")
                    output.append(f"- **TTL**: {ttl} {'(Auto)' if ttl == 1 else 'seconds'}")
                    
                    # Proxy status for applicable records
                    if proxied is not None:
                        proxy_status = "🟠 Proxied" if proxied else "⚫ DNS Only"
                        output.append(f"- **Proxy**: {proxy_status}")
                    
                    # Priority for MX records
                    if priority is not None:
                        output.append(f"- **Priority**: {priority}")
                    
                    # Timestamps
                    created = getattr(record, 'created_on', None)
                    modified = getattr(record, 'modified_on', None)
                    if created:
                        output.append(f"- **Created**: {created}")
                    if modified and modified != created:
                        output.append(f"- **Modified**: {modified}")
                    
                    output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# DNS Records Error\n\nError accessing DNS records for zone `{zone_id}`: {e}"
    
    @mcp.resource("cloudflare://zone/{zone_id}/settings")
    def zone_settings_resource(zone_id: str) -> str:
        """Resource to get zone settings"""
        try:
            client = get_client()
            
            # Get zone name first
            try:
                zone = client.zones.get(zone_id=zone_id)
                zone_name = getattr(zone, 'name', 'Unknown')
            except:
                zone_name = 'Unknown'
            
            settings_resp = client.zones.settings.get(zone_id=zone_id)
            
            output = [f"# Settings for {zone_name}\n"]
            
            # Group settings by category
            categories = {
                "Security": ["security_level", "challenge_ttl", "browser_integrity_check", "privacy_pass"],
                "SSL/TLS": ["ssl", "always_use_https", "tls_1_3", "automatic_https_rewrites", "opportunistic_encryption"],
                "Cache": ["cache_level", "browser_cache_ttl", "development_mode", "sort_query_string_for_cache"],
                "Performance": ["minify", "rocket_loader", "mirage", "polish", "webp", "brotli"],
                "Network": ["ipv6", "websockets", "pseudo_ipv4", "ip_geolocation", "max_upload"],
                "DNS": ["cname_flattening", "dnssec"],
                "Other": []
            }
            
            # Categorize settings
            categorized_settings = {cat: [] for cat in categories.keys()}
            uncategorized = []
            
            for setting in settings_resp:
                setting_dict = setting.__dict__
                setting_id = setting_dict.get('id', 'unknown')
                
                # Find category
                found_category = None
                for category, setting_ids in categories.items():
                    if category != "Other" and setting_id in setting_ids:
                        found_category = category
                        break
                
                if found_category:
                    categorized_settings[found_category].append(setting)
                else:
                    uncategorized.append(setting)
            
            # Add uncategorized to "Other"
            categorized_settings["Other"] = uncategorized
            
            # Output settings by category
            for category, settings in categorized_settings.items():
                if not settings:
                    continue
                    
                output.append(f"## {category} Settings")
                
                for setting in settings:
                    setting_dict = setting.__dict__
                    setting_id = setting_dict.get('id', 'unknown')
                    value = setting_dict.get('value', 'N/A')
                    editable = setting_dict.get('editable', True)
                    modified = setting_dict.get('modified_on', None)
                    
                    # Format setting name
                    setting_name = setting_id.replace('_', ' ').title()
                    
                    # Format value
                    if isinstance(value, dict):
                        # Handle complex values like minify settings
                        if setting_id == "minify":
                            value_str = f"CSS: {value.get('css', 'off')}, HTML: {value.get('html', 'off')}, JS: {value.get('js', 'off')}"
                        else:
                            value_str = str(value)
                    elif isinstance(value, bool):
                        value_str = "On" if value else "Off"
                    else:
                        value_str = str(value)
                    
                    output.append(f"### {setting_name}")
                    output.append(f"- **Value**: {value_str}")
                    output.append(f"- **Editable**: {'Yes' if editable else 'No'}")
                    if modified:
                        output.append(f"- **Modified**: {modified}")
                    output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# Zone Settings Error\n\nError accessing settings for zone `{zone_id}`: {e}"
    
    @mcp.resource("cloudflare://zone/{zone_id}/analytics")
    def zone_analytics_resource(zone_id: str) -> str:
        """Resource to get recent zone analytics"""
        try:
            client = get_client()
            
            # Get zone name first
            try:
                zone = client.zones.get(zone_id=zone_id)
                zone_name = getattr(zone, 'name', 'Unknown')
            except:
                zone_name = 'Unknown'
            
            # Get analytics for the last 24 hours
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            yesterday = now - timedelta(days=1)
            
            analytics_resp = client.zones.analytics.dashboard.get(
                zone_id=zone_id,
                since=yesterday.isoformat() + "Z",
                until=now.isoformat() + "Z",
                continuous=True
            )
            
            output = [f"# Analytics for {zone_name}\n"]
            output.append("**Last 24 Hours**\n")
            
            if hasattr(analytics_resp, 'totals'):
                totals = analytics_resp.totals.__dict__
                
                # Requests
                requests = totals.get('requests', {})
                if isinstance(requests, dict):
                    output.append("## Requests")
                    output.append(f"- **Total**: {requests.get('all', 0):,}")
                    output.append(f"- **Cached**: {requests.get('cached', 0):,}")
                    output.append(f"- **Uncached**: {requests.get('uncached', 0):,}")
                    
                    # Calculate cache hit ratio
                    total_req = requests.get('all', 0)
                    cached_req = requests.get('cached', 0)
                    if total_req > 0:
                        cache_ratio = (cached_req / total_req) * 100
                        output.append(f"- **Cache Hit Ratio**: {cache_ratio:.1f}%")
                    output.append("")
                
                # Bandwidth
                bandwidth = totals.get('bandwidth', {})
                if isinstance(bandwidth, dict):
                    output.append("## Bandwidth")
                    all_bytes = bandwidth.get('all', 0)
                    cached_bytes = bandwidth.get('cached', 0)
                    uncached_bytes = bandwidth.get('uncached', 0)
                    
                    # Convert bytes to human readable
                    def format_bytes(bytes_val):
                        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                            if bytes_val < 1024:
                                return f"{bytes_val:.1f} {unit}"
                            bytes_val /= 1024
                        return f"{bytes_val:.1f} PB"
                    
                    output.append(f"- **Total**: {format_bytes(all_bytes)}")
                    output.append(f"- **Cached**: {format_bytes(cached_bytes)}")
                    output.append(f"- **Uncached**: {format_bytes(uncached_bytes)}")
                    output.append("")
                
                # Threats
                threats = totals.get('threats', {})
                if isinstance(threats, dict):
                    output.append("## Security")
                    output.append(f"- **Threats Blocked**: {threats.get('all', 0):,}")
                    output.append("")
                
                # Page views
                pageviews = totals.get('pageviews', {})
                if isinstance(pageviews, dict):
                    output.append("## Page Views")
                    output.append(f"- **Total**: {pageviews.get('all', 0):,}")
                    output.append("")
                
                # Unique visitors
                uniques = totals.get('uniques', {})
                if isinstance(uniques, dict):
                    output.append("## Unique Visitors")
                    output.append(f"- **Total**: {uniques.get('all', 0):,}")
            else:
                output.append("Analytics data not available or in unexpected format.")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# Zone Analytics Error\n\nError accessing analytics for zone `{zone_id}`: {e}"
    
    @mcp.resource("cloudflare://accounts")
    def list_accounts_resource() -> str:
        """Resource to list CloudFlare accounts"""
        try:
            client = get_client()
            accounts_resp = client.accounts.list()
            
            if not accounts_resp:
                return "# CloudFlare Accounts\n\nNo accounts found."
            
            output = ["# CloudFlare Accounts\n"]
            
            for account in accounts_resp:
                account_dict = account.__dict__
                
                output.append(f"## {account_dict.get('name', 'Unknown Account')}")
                output.append(f"- **ID**: {account_dict.get('id', 'N/A')}")
                output.append(f"- **Type**: {account_dict.get('type', 'N/A')}")
                
                # Settings
                settings = account_dict.get('settings', {})
                if settings:
                    if settings.get('enforce_twofactor'):
                        output.append("- **Two-Factor**: Enforced")
                    
                # Created date
                created = account_dict.get('created_on')
                if created:
                    output.append(f"- **Created**: {created}")
                
                output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# CloudFlare Accounts\n\nError accessing accounts: {e}"