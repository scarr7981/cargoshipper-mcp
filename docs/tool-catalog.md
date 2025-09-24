# CargoShipper MCP Tool Catalog

## Overview

This document provides a comprehensive catalog of all tools and resources available in the CargoShipper MCP server. Each tool is designed to provide Claude with direct access to Docker, DigitalOcean, and CloudFlare operations through a standardized interface.

## Tool Categories

### 🐳 Docker Tools

#### Container Management

##### `docker_run_container`
**Description**: Run a Docker container with specified configuration  
**Parameters**:
- `image` (str, required): Docker image name (e.g., "ubuntu:latest", "nginx:alpine")
- `name` (str, optional): Container name
- `command` (str, optional): Command to run in container
- `ports` (dict, optional): Port mappings (e.g., {"80/tcp": 8080})
- `environment` (dict, optional): Environment variables
- `volumes` (dict, optional): Volume mounts (host_path: container_path)
- `detach` (bool, default=True): Run in detached mode
- `remove` (bool, default=False): Remove container when it exits

**Returns**: Container ID, name, status, and image information

**Example Usage**:
```python
# Basic container
docker_run_container(image="nginx:latest", name="web-server")

# Advanced container with ports and volumes
docker_run_container(
    image="postgres:15",
    name="database",
    environment={"POSTGRES_DB": "myapp", "POSTGRES_PASSWORD": "secret"},
    ports={"5432/tcp": 5432},
    volumes={"/host/data": "/var/lib/postgresql/data"}
)
```

##### `docker_list_containers`
**Description**: List Docker containers  
**Parameters**:
- `all_containers` (bool, default=True): Include stopped containers
- `filters` (dict, optional): Filter containers (e.g., {"status": "running"})

**Returns**: List of containers with ID, name, image, status, creation time, and ports

##### `docker_stop_container`
**Description**: Stop a running Docker container  
**Parameters**:
- `container_id` (str, required): Container ID or name
- `timeout` (int, default=10): Seconds to wait before killing

**Returns**: Container ID, name, and new status

##### `docker_start_container`
**Description**: Start a stopped Docker container  
**Parameters**:
- `container_id` (str, required): Container ID or name

**Returns**: Container ID, name, and new status

##### `docker_restart_container`
**Description**: Restart a Docker container  
**Parameters**:
- `container_id` (str, required): Container ID or name
- `timeout` (int, default=10): Seconds to wait before killing

##### `docker_remove_container`
**Description**: Remove a Docker container  
**Parameters**:
- `container_id` (str, required): Container ID or name
- `force` (bool, default=False): Force removal of running container
- `remove_volumes` (bool, default=False): Remove associated volumes

##### `docker_get_logs`
**Description**: Get logs from a Docker container  
**Parameters**:
- `container_id` (str, required): Container ID or name
- `tail` (int, default=100): Number of lines from end of logs
- `follow` (bool, default=False): Follow log output
- `timestamps` (bool, default=True): Show timestamps

**Returns**: Container info and log content

##### `docker_exec_command`
**Description**: Execute command in running container  
**Parameters**:
- `container_id` (str, required): Container ID or name
- `command` (str, required): Command to execute
- `workdir` (str, optional): Working directory
- `environment` (dict, optional): Environment variables
- `user` (str, optional): User to run command as

**Returns**: Exit code and output

#### Image Management

##### `docker_list_images`
**Description**: List Docker images  
**Parameters**:
- `filters` (dict, optional): Filter images (e.g., {"dangling": False})

**Returns**: List of images with ID, tags, size, and creation time

##### `docker_pull_image`
**Description**: Pull Docker image from registry  
**Parameters**:
- `image` (str, required): Image name to pull
- `tag` (str, default="latest"): Image tag
- `auth_config` (dict, optional): Registry authentication

**Returns**: Image ID and pull status

##### `docker_build_image`
**Description**: Build Docker image from Dockerfile  
**Parameters**:
- `path` (str, required): Path to build context
- `tag` (str, required): Image tag
- `dockerfile` (str, default="Dockerfile"): Dockerfile name
- `build_args` (dict, optional): Build arguments
- `no_cache` (bool, default=False): Don't use cache

**Returns**: Image ID and build logs

##### `docker_remove_image`
**Description**: Remove Docker image  
**Parameters**:
- `image` (str, required): Image ID or name
- `force` (bool, default=False): Force removal
- `no_prune` (bool, default=False): Don't delete untagged parents

##### `docker_push_image`
**Description**: Push image to registry  
**Parameters**:
- `image` (str, required): Image name to push
- `auth_config` (dict, optional): Registry authentication

#### Volume Management

##### `docker_create_volume`
**Description**: Create Docker volume  
**Parameters**:
- `name` (str, required): Volume name
- `driver` (str, default="local"): Volume driver
- `driver_opts` (dict, optional): Driver options
- `labels` (dict, optional): Volume labels

##### `docker_list_volumes`
**Description**: List Docker volumes  
**Parameters**:
- `filters` (dict, optional): Filter volumes

**Returns**: List of volumes with name, driver, mountpoint, and labels

##### `docker_remove_volume`
**Description**: Remove Docker volume  
**Parameters**:
- `volume_name` (str, required): Volume name
- `force` (bool, default=False): Force removal

#### Network Management

##### `docker_create_network`
**Description**: Create Docker network  
**Parameters**:
- `name` (str, required): Network name
- `driver` (str, default="bridge"): Network driver
- `subnet` (str, optional): Network subnet (e.g., "172.20.0.0/16")
- `gateway` (str, optional): Network gateway
- `labels` (dict, optional): Network labels

##### `docker_list_networks`
**Description**: List Docker networks  
**Returns**: List of networks with ID, name, driver, and scope

##### `docker_connect_container_to_network`
**Description**: Connect container to network  
**Parameters**:
- `container_id` (str, required): Container ID or name
- `network_id` (str, required): Network ID or name
- `aliases` (list, optional): Network aliases for container
- `ip_address` (str, optional): Static IP address

##### `docker_disconnect_container_from_network`
**Description**: Disconnect container from network  
**Parameters**:
- `container_id` (str, required): Container ID or name
- `network_id` (str, required): Network ID or name
- `force` (bool, default=False): Force disconnection

#### System Operations

##### `docker_system_info`
**Description**: Get Docker system information  
**Returns**: Docker version, system info, resource usage

##### `docker_system_prune`
**Description**: Clean up unused Docker resources  
**Parameters**:
- `containers` (bool, default=True): Remove stopped containers
- `images` (bool, default=True): Remove unused images
- `networks` (bool, default=True): Remove unused networks
- `volumes` (bool, default=True): Remove unused volumes
- `all_images` (bool, default=False): Remove all unused images, not just dangling

### 🌊 DigitalOcean Tools

#### Droplet Management

##### `do_list_droplets`
**Description**: List DigitalOcean droplets  
**Parameters**:
- `tag_name` (str, optional): Filter by tag
- `per_page` (int, default=20): Results per page

**Returns**: List of droplets with ID, name, status, IP addresses, region, and size

##### `do_get_droplet`
**Description**: Get detailed droplet information  
**Parameters**:
- `droplet_id` (int, required): Droplet ID

**Returns**: Complete droplet details including networks, volumes, and kernel

##### `do_create_droplet`
**Description**: Create new DigitalOcean droplet  
**Parameters**:
- `name` (str, required): Droplet name
- `region` (str, required): Region slug (e.g., "nyc3", "sfo3")
- `size` (str, required): Size slug (e.g., "s-1vcpu-1gb", "s-2vcpu-4gb")
- `image` (str, required): Image slug or ID (e.g., "ubuntu-22-04-x64")
- `ssh_keys` (list, optional): SSH key fingerprints or IDs
- `backups` (bool, default=False): Enable backups
- `ipv6` (bool, default=False): Enable IPv6
- `monitoring` (bool, default=False): Enable monitoring
- `tags` (list, optional): Droplet tags
- `user_data` (str, optional): Cloud-init user data
- `vpc_uuid` (str, optional): VPC UUID

**Returns**: New droplet details

##### `do_destroy_droplet`
**Description**: Destroy DigitalOcean droplet  
**Parameters**:
- `droplet_id` (int, required): Droplet ID

##### `do_power_on_droplet`
**Description**: Power on droplet  
**Parameters**:
- `droplet_id` (int, required): Droplet ID

##### `do_power_off_droplet`
**Description**: Power off droplet  
**Parameters**:
- `droplet_id` (int, required): Droplet ID

##### `do_reboot_droplet`
**Description**: Reboot droplet  
**Parameters**:
- `droplet_id` (int, required): Droplet ID

##### `do_resize_droplet`
**Description**: Resize droplet  
**Parameters**:
- `droplet_id` (int, required): Droplet ID
- `size` (str, required): New size slug
- `disk` (bool, default=False): Resize disk permanently

##### `do_snapshot_droplet`
**Description**: Take droplet snapshot  
**Parameters**:
- `droplet_id` (int, required): Droplet ID
- `name` (str, required): Snapshot name

#### Volume Management

##### `do_create_volume`
**Description**: Create DigitalOcean volume  
**Parameters**:
- `name` (str, required): Volume name
- `size_gigabytes` (int, required): Volume size in GB
- `region` (str, required): Region slug
- `description` (str, optional): Volume description
- `tags` (list, optional): Volume tags

##### `do_list_volumes`
**Description**: List volumes  
**Parameters**:
- `region` (str, optional): Filter by region
- `name` (str, optional): Filter by name

##### `do_attach_volume`
**Description**: Attach volume to droplet  
**Parameters**:
- `volume_id` (str, required): Volume ID
- `droplet_id` (int, required): Droplet ID

##### `do_detach_volume`
**Description**: Detach volume from droplet  
**Parameters**:
- `volume_id` (str, required): Volume ID
- `droplet_id` (int, required): Droplet ID

#### DNS Management

##### `do_list_domains`
**Description**: List DNS domains  
**Returns**: List of domains with name and TTL

##### `do_create_domain`
**Description**: Create DNS domain  
**Parameters**:
- `name` (str, required): Domain name
- `ip_address` (str, optional): IP address for default A record

##### `do_list_domain_records`
**Description**: List DNS records for domain  
**Parameters**:
- `domain_name` (str, required): Domain name
- `type` (str, optional): Filter by record type

##### `do_create_domain_record`
**Description**: Create DNS record  
**Parameters**:
- `domain_name` (str, required): Domain name
- `type` (str, required): Record type (A, AAAA, CNAME, MX, TXT, SRV, NS)
- `name` (str, required): Record name
- `data` (str, required): Record data
- `priority` (int, optional): Priority (for MX and SRV records)
- `port` (int, optional): Port (for SRV records)
- `ttl` (int, default=3600): Time to live
- `weight` (int, optional): Weight (for SRV records)

##### `do_update_domain_record`
**Description**: Update DNS record  
**Parameters**:
- `domain_name` (str, required): Domain name
- `record_id` (int, required): Record ID
- `type` (str, optional): Record type
- `name` (str, optional): Record name
- `data` (str, optional): Record data
- `ttl` (int, optional): Time to live

##### `do_delete_domain_record`
**Description**: Delete DNS record  
**Parameters**:
- `domain_name` (str, required): Domain name
- `record_id` (int, required): Record ID

#### Kubernetes Management

##### `do_list_kubernetes_clusters`
**Description**: List Kubernetes clusters  
**Returns**: List of clusters with ID, name, region, version, and status

##### `do_create_kubernetes_cluster`
**Description**: Create Kubernetes cluster  
**Parameters**:
- `name` (str, required): Cluster name
- `region` (str, required): Region slug
- `version` (str, required): Kubernetes version
- `node_pools` (list, required): List of node pool configurations
- `auto_upgrade` (bool, default=False): Enable auto-upgrade
- `ha` (bool, default=False): High availability control plane

##### `do_get_kubeconfig`
**Description**: Get kubeconfig for cluster  
**Parameters**:
- `cluster_id` (str, required): Cluster UUID

**Returns**: Kubeconfig YAML content

#### Load Balancer Management

##### `do_create_load_balancer`
**Description**: Create load balancer  
**Parameters**:
- `name` (str, required): Load balancer name
- `algorithm` (str, default="round_robin"): Load balancing algorithm
- `forwarding_rules` (list, required): List of forwarding rules
- `health_check` (dict, required): Health check configuration
- `region` (str, required): Region slug
- `droplet_ids` (list, optional): Backend droplet IDs
- `tag` (str, optional): Backend droplet tag

##### `do_list_load_balancers`
**Description**: List load balancers  
**Returns**: List of load balancers

##### `do_add_droplets_to_load_balancer`
**Description**: Add droplets to load balancer  
**Parameters**:
- `lb_id` (str, required): Load balancer ID
- `droplet_ids` (list, required): List of droplet IDs

### ☁️ CloudFlare Tools

#### Zone Management

##### `cf_list_zones`
**Description**: List CloudFlare zones  
**Parameters**:
- `name` (str, optional): Filter by zone name
- `status` (str, optional): Filter by status (active, pending, etc.)

**Returns**: List of zones with ID, name, status, and name servers

##### `cf_get_zone`
**Description**: Get zone details  
**Parameters**:
- `zone_id` (str, required): Zone ID

**Returns**: Complete zone information

##### `cf_create_zone`
**Description**: Create new zone  
**Parameters**:
- `name` (str, required): Domain name
- `account_id` (str, required): Account ID
- `jump_start` (bool, default=True): Import existing DNS records
- `type` (str, default="full"): Zone type (full or partial)

##### `cf_delete_zone`
**Description**: Delete zone  
**Parameters**:
- `zone_id` (str, required): Zone ID

#### DNS Record Management

##### `cf_list_dns_records`
**Description**: List DNS records for zone  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `type` (str, optional): Filter by record type
- `name` (str, optional): Filter by record name

##### `cf_create_dns_record`
**Description**: Create DNS record  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `type` (str, required): Record type
- `name` (str, required): Record name
- `content` (str, required): Record content
- `ttl` (int, default=3600): Time to live (1 for auto)
- `proxied` (bool, default=False): Proxy through CloudFlare
- `priority` (int, optional): Priority for MX records

##### `cf_update_dns_record`
**Description**: Update DNS record  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `record_id` (str, required): Record ID
- `type` (str, optional): Record type
- `name` (str, optional): Record name
- `content` (str, optional): Record content
- `ttl` (int, optional): Time to live
- `proxied` (bool, optional): Proxy status

##### `cf_delete_dns_record`
**Description**: Delete DNS record  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `record_id` (str, required): Record ID

#### SSL/TLS Management

##### `cf_get_ssl_settings`
**Description**: Get SSL/TLS settings for zone  
**Parameters**:
- `zone_id` (str, required): Zone ID

##### `cf_update_ssl_mode`
**Description**: Update SSL mode  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `mode` (str, required): SSL mode (off, flexible, full, strict)

##### `cf_enable_always_use_https`
**Description**: Enable Always Use HTTPS  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `enabled` (bool, required): Enable or disable

##### `cf_upload_custom_certificate`
**Description**: Upload custom SSL certificate  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `certificate` (str, required): Certificate content (PEM format)
- `private_key` (str, required): Private key content (PEM format)
- `bundle_method` (str, default="ubiquitous"): Bundle method

#### Firewall Rules

##### `cf_create_firewall_rule`
**Description**: Create firewall rule  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `expression` (str, required): Rule expression
- `action` (str, required): Action (allow, block, challenge, js_challenge, managed_challenge)
- `priority` (int, optional): Rule priority
- `description` (str, optional): Rule description

##### `cf_list_firewall_rules`
**Description**: List firewall rules for zone  
**Parameters**:
- `zone_id` (str, required): Zone ID

##### `cf_create_ip_access_rule`
**Description**: Create IP-based access rule  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `mode` (str, required): Rule mode (block, challenge, whitelist, js_challenge)
- `target` (str, required): Target type (ip, ip_range, country, asn)
- `value` (str, required): Target value
- `notes` (str, optional): Rule notes

#### Page Rules

##### `cf_create_page_rule`
**Description**: Create page rule  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `url_pattern` (str, required): URL pattern to match
- `actions` (list, required): List of actions to apply
- `priority` (int, optional): Rule priority
- `status` (str, default="active"): Rule status

##### `cf_list_page_rules`
**Description**: List page rules for zone  
**Parameters**:
- `zone_id` (str, required): Zone ID

#### Cache Management

##### `cf_purge_cache`
**Description**: Purge cache  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `purge_everything` (bool, default=False): Purge all cache
- `files` (list, optional): Specific URLs to purge
- `tags` (list, optional): Cache tags to purge
- `hosts` (list, optional): Hostnames to purge

#### Analytics

##### `cf_get_zone_analytics`
**Description**: Get zone analytics  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `since` (str, required): Start date (ISO format)
- `until` (str, required): End date (ISO format)
- `continuous` (bool, default=True): Continuous or time series data

**Returns**: Analytics data including requests, bandwidth, threats, and page views

#### Workers

##### `cf_deploy_worker`
**Description**: Deploy CloudFlare Worker  
**Parameters**:
- `account_id` (str, required): Account ID
- `script_name` (str, required): Worker script name
- `script_content` (str, required): JavaScript code
- `bindings` (list, optional): Worker bindings (KV, secrets, etc.)

##### `cf_create_worker_route`
**Description**: Create worker route  
**Parameters**:
- `zone_id` (str, required): Zone ID
- `pattern` (str, required): Route pattern
- `script` (str, required): Worker script name

##### `cf_list_worker_routes`
**Description**: List worker routes  
**Parameters**:
- `zone_id` (str, required): Zone ID

## Resources

Resources provide read-only access to system information and are accessed via URI patterns.

### Docker Resources

- `docker://containers` - List all containers with status
- `docker://container/{container_id}` - Detailed container information
- `docker://container/{container_id}/logs` - Container logs
- `docker://images` - List all images
- `docker://volumes` - List all volumes
- `docker://networks` - List all networks
- `docker://system/info` - Docker system information

### DigitalOcean Resources

- `do://account` - Account information and limits
- `do://droplets` - List all droplets
- `do://droplet/{droplet_id}` - Detailed droplet information
- `do://volumes` - List all volumes
- `do://domains` - List all domains
- `do://domain/{domain_name}/records` - DNS records for domain
- `do://kubernetes/clusters` - List Kubernetes clusters
- `do://load-balancers` - List load balancers

### CloudFlare Resources

- `cf://zones` - List all zones
- `cf://zone/{zone_id}` - Zone details and settings
- `cf://zone/{zone_id}/dns` - DNS records for zone
- `cf://zone/{zone_id}/analytics` - Zone analytics summary
- `cf://zone/{zone_id}/firewall` - Firewall rules
- `cf://zone/{zone_id}/page-rules` - Page rules
- `cf://workers/{account_id}` - Worker scripts and routes

## Usage Examples

### Docker Container Deployment

```python
# Deploy a web application
result = docker_run_container(
    image="nginx:alpine",
    name="my-web-app",
    ports={"80/tcp": 8080},
    volumes={"/host/www": "/usr/share/nginx/html"},
    environment={"NGINX_HOST": "example.com"}
)

# Check container status
containers = docker_list_containers(filters={"name": "my-web-app"})

# View logs
logs = docker_get_logs("my-web-app", tail=50)
```

### DigitalOcean Infrastructure Setup

```python
# Create droplet
droplet = do_create_droplet(
    name="web-server-01",
    region="nyc3",
    size="s-2vcpu-4gb",
    image="ubuntu-22-04-x64",
    tags=["web", "production"],
    backups=True,
    monitoring=True
)

# Create and attach volume
volume = do_create_volume(
    name="web-data",
    size_gigabytes=100,
    region="nyc3"
)
do_attach_volume(volume["id"], droplet["id"])

# Setup DNS
do_create_domain("example.com", droplet["networks"]["v4"][0]["ip_address"])
do_create_domain_record(
    domain_name="example.com",
    type="CNAME",
    name="www",
    data="example.com"
)
```

### CloudFlare Security Configuration

```python
# Setup zone with security
zone = cf_create_zone("example.com", account_id="your-account-id")

# Enable SSL
cf_update_ssl_mode(zone["id"], "strict")
cf_enable_always_use_https(zone["id"], True)

# Create firewall rules
cf_create_firewall_rule(
    zone_id=zone["id"],
    expression="(http.request.uri.path contains \"/admin\")",
    action="challenge",
    description="Challenge admin area access"
)

# Block malicious countries
cf_create_ip_access_rule(
    zone_id=zone["id"],
    mode="block",
    target="country",
    value="CN",
    notes="Block China traffic"
)

# Setup caching
cf_create_page_rule(
    zone_id=zone["id"],
    url_pattern="*example.com/images/*",
    actions=[
        {"id": "cache_level", "value": "cache_everything"},
        {"id": "edge_cache_ttl", "value": 86400}
    ]
)
```

## Error Handling

All tools return standardized responses:

### Success Response
```json
{
    "success": true,
    "operation": "operation_name",
    "timestamp": "2024-01-01T12:00:00Z",
    "data": { ... }
}
```

### Error Response
```json
{
    "success": false,
    "operation": "operation_name",
    "timestamp": "2024-01-01T12:00:00Z",
    "error": "Error description",
    "details": { ... }
}
```

## Best Practices for Claude

### Resource Planning
1. Always check current resources before creating new ones
2. Use consistent naming conventions for related resources
3. Tag resources appropriately for organization
4. Consider regional placement for performance

### Security First
1. Use least-privilege access for API tokens
2. Enable monitoring and logging where available
3. Implement proper firewall rules and SSL/TLS
4. Regularly audit and clean up unused resources

### Error Recovery
1. Always check tool responses for success/failure
2. Implement retry logic for transient failures
3. Clean up partially created resources on failure
4. Provide clear error messages to users

### Performance Optimization
1. Use appropriate resource sizes for workloads
2. Implement caching strategies
3. Monitor resource usage and adjust as needed
4. Use load balancing for high-availability applications