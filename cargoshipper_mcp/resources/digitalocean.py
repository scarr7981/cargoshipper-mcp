"""DigitalOcean resources for CargoShipper MCP server"""

from typing import Callable
from ..utils.formatters import format_droplet_info


def register_resources(mcp, get_client: Callable):
    """Register DigitalOcean resources"""
    
    @mcp.resource("digitalocean://droplets")
    def list_droplets_resource() -> str:
        """Resource to list all DigitalOcean droplets"""
        try:
            client = get_client()
            droplets_resp = client.droplets.list()
            droplets = droplets_resp.get('droplets', [])
            
            if not droplets:
                return "# DigitalOcean Droplets\n\nNo droplets found."
            
            output = ["# DigitalOcean Droplets\n"]
            running_count = 0
            stopped_count = 0
            total_cost = 0
            
            for droplet in droplets:
                status = droplet.get('status', 'unknown')
                status_emoji = "🟢" if status == "active" else "🔴"
                
                if status == "active":
                    running_count += 1
                else:
                    stopped_count += 1
                
                # Calculate approximate cost (this is a rough estimate)
                size_info = droplet.get('size', {})
                monthly_cost = size_info.get('price_monthly', 0)
                total_cost += monthly_cost
                
                droplet_info = format_droplet_info(droplet)
                
                output.append(f"## {status_emoji} {droplet_info['name']}")
                output.append(f"- **ID**: {droplet_info['id']}")
                output.append(f"- **Status**: {droplet_info['status']}")
                output.append(f"- **Size**: {droplet_info['size']}")
                output.append(f"- **Region**: {droplet_info['region']}")
                output.append(f"- **IP**: {droplet_info['ip_address']}")
                output.append(f"- **Image**: {droplet_info['image']}")
                output.append(f"- **Monthly Cost**: ${monthly_cost}")
                output.append(f"- **Created**: {droplet_info['created_at']}")
                
                # Tags
                tags = droplet.get('tags', [])
                if tags:
                    output.append(f"- **Tags**: {', '.join(tags)}")
                
                # Features
                features = droplet.get('features', [])
                if features:
                    output.append(f"- **Features**: {', '.join(features)}")
                
                output.append("")
            
            summary = f"**Summary**: {running_count} active, {stopped_count} inactive"
            if total_cost > 0:
                summary += f", ~${total_cost:.2f}/month estimated cost"
            output.insert(1, summary + "\n")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# DigitalOcean Droplets\n\nError accessing DigitalOcean: {e}"
    
    @mcp.resource("digitalocean://droplet/{droplet_id}")
    def get_droplet_resource(droplet_id: str) -> str:
        """Resource to get detailed information about a specific droplet"""
        try:
            client = get_client()
            droplet_resp = client.droplets.get(droplet_id=int(droplet_id))
            droplet = droplet_resp.get('droplet', {})
            
            output = [f"# Droplet: {droplet.get('name', 'Unknown')}\n"]
            
            # Basic information
            output.append("## Basic Information")
            output.append(f"- **ID**: {droplet.get('id')}")
            output.append(f"- **Name**: {droplet.get('name')}")
            output.append(f"- **Status**: {droplet.get('status')}")
            output.append(f"- **Region**: {droplet.get('region', {}).get('name')}")
            output.append(f"- **Size**: {droplet.get('size', {}).get('slug')}")
            output.append(f"- **Image**: {droplet.get('image', {}).get('name')}")
            output.append(f"- **Created**: {droplet.get('created_at')}")
            
            # Resource specifications
            output.append("\n## Specifications")
            output.append(f"- **vCPUs**: {droplet.get('vcpus', 'N/A')}")
            output.append(f"- **Memory**: {droplet.get('memory', 'N/A')} MB")
            output.append(f"- **Disk**: {droplet.get('disk', 'N/A')} GB")
            
            size_info = droplet.get('size', {})
            if size_info:
                output.append(f"- **Monthly Cost**: ${size_info.get('price_monthly', 0)}")
                output.append(f"- **Hourly Cost**: ${size_info.get('price_hourly', 0)}")
            
            # Network information
            networks = droplet.get('networks', {})
            if networks:
                output.append("\n## Network")
                
                # IPv4 addresses
                v4_networks = networks.get('v4', [])
                if v4_networks:
                    output.append("### IPv4 Addresses")
                    for network in v4_networks:
                        net_type = network.get('type', 'unknown')
                        ip = network.get('ip_address', 'N/A')
                        gateway = network.get('gateway', 'N/A')
                        netmask = network.get('netmask', 'N/A')
                        output.append(f"- **{net_type.title()}**: {ip} (Gateway: {gateway}, Netmask: {netmask})")
                
                # IPv6 addresses
                v6_networks = networks.get('v6', [])
                if v6_networks:
                    output.append("### IPv6 Addresses")
                    for network in v6_networks:
                        net_type = network.get('type', 'unknown')
                        ip = network.get('ip_address', 'N/A')
                        gateway = network.get('gateway', 'N/A')
                        netmask = network.get('netmask', 'N/A')
                        output.append(f"- **{net_type.title()}**: {ip} (Gateway: {gateway}, Netmask: {netmask})")
            
            # Features and settings
            features = droplet.get('features', [])
            if features:
                output.append("\n## Features")
                for feature in features:
                    output.append(f"- {feature}")
            
            # Tags
            tags = droplet.get('tags', [])
            if tags:
                output.append("\n## Tags")
                output.append(f"- {', '.join(tags)}")
            
            # Kernel information
            kernel = droplet.get('kernel')
            if kernel:
                output.append("\n## Kernel")
                output.append(f"- **Name**: {kernel.get('name', 'N/A')}")
                output.append(f"- **Version**: {kernel.get('version', 'N/A')}")
            
            # Backup information
            backup_ids = droplet.get('backup_ids', [])
            if backup_ids:
                output.append("\n## Backups")
                output.append(f"- **Backup IDs**: {', '.join(map(str, backup_ids))}")
            
            next_backup = droplet.get('next_backup_window')
            if next_backup:
                output.append(f"- **Next Backup Window**: {next_backup.get('start')} to {next_backup.get('end')}")
            
            # Snapshot information
            snapshot_ids = droplet.get('snapshot_ids', [])
            if snapshot_ids:
                output.append("\n## Snapshots")
                output.append(f"- **Snapshot IDs**: {', '.join(map(str, snapshot_ids))}")
            
            # Volume attachments
            volume_ids = droplet.get('volume_ids', [])
            if volume_ids:
                output.append("\n## Attached Volumes")
                output.append(f"- **Volume IDs**: {', '.join(volume_ids)}")
            
            # VPC information
            vpc_uuid = droplet.get('vpc_uuid')
            if vpc_uuid:
                output.append("\n## VPC")
                output.append(f"- **VPC UUID**: {vpc_uuid}")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# Droplet Error\n\nError accessing droplet `{droplet_id}`: {e}"
    
    @mcp.resource("digitalocean://account")
    def account_info_resource() -> str:
        """Resource to get DigitalOcean account information"""
        try:
            client = get_client()
            account_resp = client.account.get()
            account = account_resp.get('account', {})
            
            output = ["# DigitalOcean Account Information\n"]
            
            # Basic account info
            output.append("## Account Details")
            output.append(f"- **Email**: {account.get('email', 'N/A')}")
            output.append(f"- **UUID**: {account.get('uuid', 'N/A')}")
            output.append(f"- **Status**: {account.get('status', 'N/A')}")
            
            status_message = account.get('status_message')
            if status_message:
                output.append(f"- **Status Message**: {status_message}")
            
            output.append(f"- **Email Verified**: {'Yes' if account.get('email_verified') else 'No'}")
            
            # Limits
            output.append("\n## Resource Limits")
            output.append(f"- **Droplet Limit**: {account.get('droplet_limit', 'N/A')}")
            output.append(f"- **Floating IP Limit**: {account.get('floating_ip_limit', 'N/A')}")
            output.append(f"- **Volume Limit**: {account.get('volume_limit', 'N/A')}")
            
            # Try to get balance information
            try:
                balance_resp = client.balance.get()
                balance = balance_resp.get('balance', {})
                
                if balance:
                    output.append("\n## Billing Information")
                    output.append(f"- **Account Balance**: ${balance.get('account_balance', '0.00')}")
                    output.append(f"- **Month-to-Date Balance**: ${balance.get('month_to_date_balance', '0.00')}")
                    output.append(f"- **Generated At**: {balance.get('generated_at', 'N/A')}")
            except:
                # Balance information might not be available
                pass
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# DigitalOcean Account\n\nError accessing account information: {e}"
    
    @mcp.resource("digitalocean://domains")
    def list_domains_resource() -> str:
        """Resource to list DigitalOcean domains"""
        try:
            client = get_client()
            domains_resp = client.domains.list()
            domains = domains_resp.get('domains', [])
            
            if not domains:
                return "# DigitalOcean Domains\n\nNo domains found."
            
            output = ["# DigitalOcean Domains\n"]
            output.append(f"**Total Domains**: {len(domains)}\n")
            
            for domain in domains:
                output.append(f"## {domain.get('name', 'Unknown')}")
                output.append(f"- **TTL**: {domain.get('ttl', 'N/A')} seconds")
                
                # Try to get record count
                try:
                    records_resp = client.domains.list_records(domain_name=domain.get('name'))
                    record_count = len(records_resp.get('domain_records', []))
                    output.append(f"- **DNS Records**: {record_count}")
                except:
                    output.append(f"- **DNS Records**: Unable to fetch")
                
                output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# DigitalOcean Domains\n\nError accessing domains: {e}"
    
    @mcp.resource("digitalocean://domain/{domain_name}/records")
    def domain_records_resource(domain_name: str) -> str:
        """Resource to list DNS records for a specific domain"""
        try:
            client = get_client()
            records_resp = client.domains.list_records(domain_name=domain_name)
            records = records_resp.get('domain_records', [])
            
            if not records:
                return f"# DNS Records for {domain_name}\n\nNo DNS records found."
            
            output = [f"# DNS Records for {domain_name}\n"]
            output.append(f"**Total Records**: {len(records)}\n")
            
            # Group records by type
            record_types = {}
            for record in records:
                record_type = record.get('type', 'UNKNOWN')
                if record_type not in record_types:
                    record_types[record_type] = []
                record_types[record_type].append(record)
            
            for record_type, type_records in record_types.items():
                output.append(f"## {record_type} Records ({len(type_records)})")
                
                for record in type_records:
                    name = record.get('name', '@')
                    data = record.get('data', 'N/A')
                    ttl = record.get('ttl', 3600)
                    record_id = record.get('id', 'N/A')
                    
                    output.append(f"### {name}")
                    output.append(f"- **ID**: {record_id}")
                    output.append(f"- **Data**: {data}")
                    output.append(f"- **TTL**: {ttl} seconds")
                    
                    # Type-specific fields
                    if record_type in ['MX', 'SRV']:
                        priority = record.get('priority')
                        if priority is not None:
                            output.append(f"- **Priority**: {priority}")
                    
                    if record_type == 'SRV':
                        port = record.get('port')
                        weight = record.get('weight')
                        if port is not None:
                            output.append(f"- **Port**: {port}")
                        if weight is not None:
                            output.append(f"- **Weight**: {weight}")
                    
                    output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# DNS Records for {domain_name}\n\nError accessing DNS records: {e}"
    
    @mcp.resource("digitalocean://images")
    def list_images_resource() -> str:
        """Resource to list DigitalOcean images"""
        try:
            client = get_client()
            
            # Get distribution images
            dist_images_resp = client.images.list(type="distribution")
            dist_images = dist_images_resp.get('images', [])
            
            # Get custom images (snapshots)
            custom_images_resp = client.images.list(private=True)
            custom_images = custom_images_resp.get('images', [])
            
            output = ["# DigitalOcean Images\n"]
            
            if dist_images:
                output.append(f"## Distribution Images ({len(dist_images)})\n")
                
                # Group by distribution
                distributions = {}
                for image in dist_images:
                    dist_name = image.get('distribution', 'Other')
                    if dist_name not in distributions:
                        distributions[dist_name] = []
                    distributions[dist_name].append(image)
                
                for dist_name, images in distributions.items():
                    output.append(f"### {dist_name}")
                    for image in images[:5]:  # Show first 5 to avoid clutter
                        output.append(f"- **{image.get('name', 'N/A')}** (`{image.get('slug', 'N/A')}`)")
                    if len(images) > 5:
                        output.append(f"- ... and {len(images) - 5} more")
                    output.append("")
            
            if custom_images:
                output.append(f"## Custom Images/Snapshots ({len(custom_images)})\n")
                for image in custom_images:
                    output.append(f"### {image.get('name', 'Unknown')}")
                    output.append(f"- **ID**: {image.get('id')}")
                    output.append(f"- **Size**: {image.get('size_gigabytes', 'N/A')} GB")
                    output.append(f"- **Status**: {image.get('status', 'N/A')}")
                    output.append(f"- **Created**: {image.get('created_at', 'N/A')}")
                    
                    regions = image.get('regions', [])
                    if regions:
                        output.append(f"- **Available Regions**: {', '.join(regions)}")
                    
                    output.append("")
            
            if not dist_images and not custom_images:
                output.append("No images found.")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"# DigitalOcean Images\n\nError accessing images: {e}"