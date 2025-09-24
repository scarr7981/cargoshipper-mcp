# DigitalOcean API Reference for CargoShipper MCP

## Overview

This document provides comprehensive reference for DigitalOcean operations using the official PyDo Python client library. PyDo wraps the DigitalOcean OpenAPI specification to support all DigitalOcean HTTP APIs.

## Installation

```bash
pip install pydo
```

## Authentication

All DigitalOcean API requests require authentication using a Personal Access Token.

```python
from pydo import Client

# Initialize client with token
client = Client(token="your_digitalocean_token_here")

# Token can also be set via environment variable
# export DIGITALOCEAN_TOKEN="your_token_here"
client = Client()  # Will read from DIGITALOCEAN_TOKEN env var
```

## Account Operations

### Get Account Information

```python
# Get current account details
account_resp = client.account.get()
account = account_resp['account']

print(f"Email: {account['email']}")
print(f"UUID: {account['uuid']}")
print(f"Status: {account['status']}")
print(f"Droplet Limit: {account['droplet_limit']}")
print(f"Floating IP Limit: {account['floating_ip_limit']}")
```

### Get Balance

```python
# Get current account balance
balance_resp = client.balance.get()
balance = balance_resp['balance']

print(f"Month-to-date Balance: ${balance['month_to_date_balance']}")
print(f"Account Balance: ${balance['account_balance']}")
print(f"Generated At: {balance['generated_at']}")
```

## Droplet Operations

### List Droplets

```python
# List all droplets
droplets_resp = client.droplets.list()
droplets = droplets_resp['droplets']

# With pagination
droplets_resp = client.droplets.list(per_page=10, page=1)

# With tag filtering
tagged_droplets = client.droplets.list(tag_name="web")
```

### Get Droplet

```python
# Get specific droplet by ID
droplet_resp = client.droplets.get(droplet_id=12345)
droplet = droplet_resp['droplet']

print(f"Name: {droplet['name']}")
print(f"Status: {droplet['status']}")
print(f"IP Address: {droplet['networks']['v4'][0]['ip_address']}")
print(f"Region: {droplet['region']['name']}")
print(f"Size: {droplet['size']['slug']}")
```

### Create Droplet

```python
# Basic droplet creation
droplet_req = {
    "name": "web-server-01",
    "region": "nyc3",
    "size": "s-1vcpu-1gb",
    "image": "ubuntu-22-04-x64",
}

create_resp = client.droplets.create(body=droplet_req)
new_droplet = create_resp['droplet']

# Advanced droplet creation
droplet_req = {
    "name": "web-server-01",
    "region": "nyc3", 
    "size": "s-2vcpu-2gb",
    "image": "ubuntu-22-04-x64",
    "ssh_keys": ["12:34:56:78:90:ab:cd:ef"],  # SSH key fingerprints or IDs
    "backups": True,
    "ipv6": True,
    "monitoring": True,
    "tags": ["web", "production"],
    "user_data": """#!/bin/bash
        apt update
        apt install -y nginx
        systemctl start nginx
        systemctl enable nginx
    """,
    "vpc_uuid": "vpc-12345",  # VPC to place droplet in
    "volumes": ["vol-12345"],  # Attach volumes by ID
}

create_resp = client.droplets.create(body=droplet_req)
```

### Droplet Actions

```python
# Power on/off
client.droplet_actions.post(
    droplet_id=12345,
    body={"type": "power_on"}
)

client.droplet_actions.post(
    droplet_id=12345,
    body={"type": "power_off"}
)

# Reboot (graceful)
client.droplet_actions.post(
    droplet_id=12345,
    body={"type": "reboot"}
)

# Power cycle (hard reset)
client.droplet_actions.post(
    droplet_id=12345,
    body={"type": "power_cycle"}
)

# Shutdown (graceful)
client.droplet_actions.post(
    droplet_id=12345,
    body={"type": "shutdown"}
)

# Resize droplet (requires power off first)
client.droplet_actions.post(
    droplet_id=12345,
    body={
        "type": "resize",
        "size": "s-2vcpu-4gb",
        "disk": True  # Increase disk size permanently
    }
)

# Take snapshot
client.droplet_actions.post(
    droplet_id=12345,
    body={
        "type": "snapshot",
        "name": "web-server-backup-2024-01-01"
    }
)

# Rebuild from image
client.droplet_actions.post(
    droplet_id=12345,
    body={
        "type": "rebuild",
        "image": "ubuntu-22-04-x64"
    }
)

# Restore from snapshot
client.droplet_actions.post(
    droplet_id=12345,
    body={
        "type": "restore",
        "image": 67890  # Snapshot ID
    }
)

# Enable/disable features
client.droplet_actions.post(
    droplet_id=12345,
    body={"type": "enable_backups"}
)

client.droplet_actions.post(
    droplet_id=12345,
    body={"type": "disable_backups"}
)
```

### Delete Droplet

```python
# Delete droplet by ID
client.droplets.destroy(droplet_id=12345)

# Delete by tag (deletes all droplets with tag)
client.droplets.destroy_by_tag(tag_name="old-servers")
```

## Image Operations

### List Images

```python
# List all images (distribution + custom)
images_resp = client.images.list()

# List only distribution images
distributions = client.images.list(type="distribution")

# List only custom images (snapshots)
custom_images = client.images.list(type="application")

# List private images
private_images = client.images.list(private=True)
```

### Get Image

```python
# Get image by ID or slug
image_resp = client.images.get(image_id="ubuntu-22-04-x64")
# or
image_resp = client.images.get(image_id=12345)
```

### Update Image

```python
# Update image name
client.images.update(
    image_id=12345,
    body={"name": "Updated Image Name"}
)
```

### Delete Image

```python
# Delete custom image
client.images.destroy(image_id=12345)
```

## Volume Operations

### Create Volume

```python
# Create volume
volume_req = {
    "type": "ext4",
    "name": "database-volume",
    "size_gigabytes": 100,
    "description": "Volume for database storage",
    "region": "nyc3",
    "tags": ["database", "production"]
}

volume_resp = client.volumes.create(body=volume_req)
new_volume = volume_resp['volume']
```

### List Volumes

```python
# List all volumes
volumes_resp = client.volumes.list()

# Filter by region
volumes_in_nyc = client.volumes.list(region="nyc3")

# Filter by name
named_volumes = client.volumes.list(name="database-volume")
```

### Volume Actions

```python
# Attach volume to droplet
client.volume_actions.post(
    volume_id="vol-12345",
    body={
        "type": "attach",
        "droplet": 98765,  # Droplet ID
        "region": "nyc3"
    }
)

# Detach volume
client.volume_actions.post(
    volume_id="vol-12345",
    body={
        "type": "detach",
        "droplet": 98765,
        "region": "nyc3"
    }
)

# Resize volume
client.volume_actions.post(
    volume_id="vol-12345",
    body={
        "type": "resize",
        "size_gigabytes": 200,
        "region": "nyc3"
    }
)
```

### Delete Volume

```python
# Delete volume by ID
client.volumes.destroy(volume_id="vol-12345")

# Delete by name and region
client.volumes.destroy_by_name(name="database-volume", region="nyc3")
```

## Kubernetes Operations

### List Clusters

```python
# List all Kubernetes clusters
clusters_resp = client.kubernetes.list_clusters()
clusters = clusters_resp['kubernetes_clusters']
```

### Create Cluster

```python
# Create Kubernetes cluster
cluster_req = {
    "name": "production-cluster",
    "region": "nyc3",
    "version": "1.28.2-do.0",
    "auto_upgrade": True,
    "surge_upgrade": True,
    "ha": True,  # High availability control plane
    "node_pools": [
        {
            "size": "s-2vcpu-4gb",
            "count": 3,
            "name": "worker-pool",
            "auto_scale": True,
            "min_nodes": 2,
            "max_nodes": 10,
            "tags": ["production", "workers"],
            "taints": [],
            "labels": {"environment": "production"}
        }
    ],
    "tags": ["production", "kubernetes"]
}

cluster_resp = client.kubernetes.create_cluster(body=cluster_req)
```

### Get Cluster

```python
# Get cluster details
cluster_resp = client.kubernetes.get_cluster(cluster_id="cluster-uuid")
cluster = cluster_resp['kubernetes_cluster']

print(f"Name: {cluster['name']}")
print(f"Status: {cluster['status']['state']}")
print(f"Endpoint: {cluster['endpoint']}")
print(f"Version: {cluster['version']['kubernetes']}")
```

### Get Kubeconfig

```python
# Get kubeconfig for cluster access
kubeconfig_resp = client.kubernetes.get_kubeconfig(cluster_id="cluster-uuid")
kubeconfig = kubeconfig_resp  # Returns raw YAML content

# Save to file
with open('kubeconfig.yaml', 'w') as f:
    f.write(kubeconfig)
```

### Cluster Actions

```python
# Upgrade cluster
client.kubernetes.upgrade_cluster(
    cluster_id="cluster-uuid",
    body={"version": "1.29.0-do.0"}
)

# Delete cluster
client.kubernetes.destroy_cluster(cluster_id="cluster-uuid")
```

### Node Pool Operations

```python
# Add node pool
node_pool_req = {
    "size": "s-4vcpu-8gb",
    "count": 2,
    "name": "high-memory-pool",
    "auto_scale": False,
    "tags": ["high-memory"],
    "labels": {"workload": "memory-intensive"}
}

client.kubernetes.add_node_pool(
    cluster_id="cluster-uuid",
    body=node_pool_req
)

# Update node pool
client.kubernetes.update_node_pool(
    cluster_id="cluster-uuid",
    node_pool_id="pool-uuid",
    body={
        "count": 5,
        "auto_scale": True,
        "min_nodes": 2,
        "max_nodes": 10
    }
)

# Delete node pool
client.kubernetes.destroy_node_pool(
    cluster_id="cluster-uuid",
    node_pool_id="pool-uuid"
)
```

## Database Operations

### List Databases

```python
# List all managed databases
dbs_resp = client.databases.list()
databases = dbs_resp['databases']
```

### Create Database

```python
# Create managed database
db_req = {
    "name": "production-postgres",
    "engine": "pg",
    "version": "15",
    "region": "nyc3",
    "size": "db-s-2vcpu-4gb",
    "num_nodes": 1,
    "tags": ["production", "postgres"],
    "backup_restore": {
        "database_name": "defaultdb",
        "backup_created_at": "2023-01-01T00:00:00Z"
    }
}

db_resp = client.databases.create(body=db_req)
new_db = db_resp['database']
```

### Database Configuration

```python
# Create database within cluster
client.databases.add_database(
    database_cluster_uuid="db-cluster-uuid",
    body={"name": "app_production"}
)

# Create database user
client.databases.add_user(
    database_cluster_uuid="db-cluster-uuid",
    body={
        "name": "app_user",
        "role": "normal"  # or "primary"
    }
)

# Get connection details
connection_resp = client.databases.get_connection_pool(
    database_cluster_uuid="db-cluster-uuid",
    pool_name="connection-pool"
)
```

### Database Maintenance

```python
# Create backup
client.databases.add_backup(database_cluster_uuid="db-cluster-uuid")

# List backups
backups_resp = client.databases.list_backups(database_cluster_uuid="db-cluster-uuid")

# Resize database
client.databases.resize(
    database_cluster_uuid="db-cluster-uuid",
    body={
        "size": "db-s-4vcpu-8gb",
        "num_nodes": 2
    }
)
```

## Domain and DNS Operations

### List Domains

```python
# List all domains
domains_resp = client.domains.list()
domains = domains_resp['domains']
```

### Create Domain

```python
# Create domain
domain_req = {
    "name": "example.com",
    "ip_address": "192.168.1.1"  # Optional, creates A record
}

domain_resp = client.domains.create(body=domain_req)
```

### DNS Records

```python
# List DNS records for domain
records_resp = client.domains.list_records(domain_name="example.com")
records = records_resp['domain_records']

# Create DNS record
record_req = {
    "type": "A",
    "name": "www",
    "data": "192.168.1.100",
    "priority": None,
    "port": None,
    "ttl": 3600,
    "weight": None,
    "flags": None,
    "tag": None
}

record_resp = client.domains.create_record(
    domain_name="example.com",
    body=record_req
)

# Update DNS record
client.domains.update_record(
    domain_name="example.com",
    domain_record_id=12345,
    body={
        "name": "www",
        "data": "192.168.1.200",
        "ttl": 1800
    }
)

# Delete DNS record
client.domains.destroy_record(
    domain_name="example.com",
    domain_record_id=12345
)
```

## Load Balancer Operations

### Create Load Balancer

```python
# Create load balancer
lb_req = {
    "name": "web-lb-01",
    "algorithm": "round_robin",  # or "least_connections"
    "status": "active",
    "forwarding_rules": [
        {
            "entry_protocol": "https",
            "entry_port": 443,
            "target_protocol": "http",
            "target_port": 80,
            "certificate_id": "cert-uuid",
            "tls_passthrough": False
        },
        {
            "entry_protocol": "http",
            "entry_port": 80,
            "target_protocol": "http",
            "target_port": 80
        }
    ],
    "health_check": {
        "protocol": "http",
        "port": 80,
        "path": "/health",
        "check_interval_seconds": 10,
        "response_timeout_seconds": 5,
        "unhealthy_threshold": 3,
        "healthy_threshold": 2
    },
    "sticky_sessions": {
        "type": "cookies",
        "cookie_name": "lb",
        "cookie_ttl_seconds": 300
    },
    "region": "nyc3",
    "vpc_uuid": "vpc-12345",
    "droplet_ids": [123, 456, 789],
    "tag": "web-servers",
    "redirect_http_to_https": True,
    "enable_proxy_protocol": False,
    "enable_backend_keepalive": False,
    "http_idle_timeout_seconds": 60,
    "project_id": "project-uuid",
    "size": "lb-small"  # or "lb-medium", "lb-large"
}

lb_resp = client.load_balancers.create(body=lb_req)
```

### Load Balancer Management

```python
# List load balancers
lbs_resp = client.load_balancers.list()

# Get specific load balancer
lb_resp = client.load_balancers.get(lb_id="lb-uuid")

# Update load balancer
client.load_balancers.update(
    lb_id="lb-uuid",
    body={
        "name": "updated-lb-name",
        "algorithm": "least_connections",
        "droplet_ids": [123, 456]  # Update backend droplets
    }
)

# Delete load balancer
client.load_balancers.destroy(lb_id="lb-uuid")
```

## Firewall Operations

### Create Firewall

```python
# Create firewall
firewall_req = {
    "name": "web-firewall",
    "inbound_rules": [
        {
            "protocol": "tcp",
            "ports": "22",
            "sources": {
                "addresses": ["10.0.0.0/8", "192.168.1.0/24"],
                "tags": ["admin"],
                "droplet_ids": [123]
            }
        },
        {
            "protocol": "tcp",
            "ports": "80",
            "sources": {
                "addresses": ["0.0.0.0/0", "::/0"]
            }
        },
        {
            "protocol": "tcp",
            "ports": "443",
            "sources": {
                "addresses": ["0.0.0.0/0", "::/0"]
            }
        }
    ],
    "outbound_rules": [
        {
            "protocol": "tcp",
            "ports": "all",
            "destinations": {
                "addresses": ["0.0.0.0/0", "::/0"]
            }
        }
    ],
    "droplet_ids": [456, 789],
    "tags": ["web-servers"]
}

firewall_resp = client.firewalls.create(body=firewall_req)
```

### Firewall Management

```python
# List firewalls
firewalls_resp = client.firewalls.list()

# Get firewall
firewall_resp = client.firewalls.get(firewall_id="fw-uuid")

# Assign droplets to firewall
client.firewalls.assign_droplets(
    firewall_id="fw-uuid",
    body={"droplet_ids": [101, 102, 103]}
)

# Remove droplets from firewall
client.firewalls.unassign_droplets(
    firewall_id="fw-uuid",
    body={"droplet_ids": [101]}
)

# Update firewall rules
client.firewalls.update(
    firewall_id="fw-uuid",
    body={
        "inbound_rules": [
            {
                "protocol": "tcp",
                "ports": "22",
                "sources": {"addresses": ["10.0.0.0/8"]}
            }
        ]
    }
)
```

## VPC Operations

### Create VPC

```python
# Create VPC
vpc_req = {
    "name": "production-vpc",
    "region": "nyc3",
    "ip_range": "10.0.0.0/16",
    "description": "Production environment VPC"
}

vpc_resp = client.vpcs.create(body=vpc_req)
```

### VPC Management

```python
# List VPCs
vpcs_resp = client.vpcs.list()

# Get VPC
vpc_resp = client.vpcs.get(vpc_id="vpc-uuid")

# Update VPC
client.vpcs.update(
    vpc_id="vpc-uuid",
    body={
        "name": "updated-vpc-name",
        "description": "Updated description"
    }
)

# Delete VPC
client.vpcs.destroy(vpc_id="vpc-uuid")
```

## Monitoring and Alerts

### Get Droplet Monitoring

```python
# Get CPU metrics for droplet
metrics_resp = client.monitoring.get_droplet_cpu(
    host_id="12345",
    start="2024-01-01T00:00:00Z",
    end="2024-01-01T23:59:59Z"
)

# Get memory metrics
memory_resp = client.monitoring.get_droplet_memory(
    host_id="12345",
    start="2024-01-01T00:00:00Z",
    end="2024-01-01T23:59:59Z"
)
```

### Alert Policies

```python
# Create alert policy
alert_req = {
    "alerts": {
        "email": ["admin@example.com"],
        "slack": [
            {
                "channel": "#alerts",
                "url": "https://hooks.slack.com/services/..."
            }
        ]
    },
    "description": "High CPU usage alert",
    "enabled": True,
    "entities": ["12345"],  # Droplet IDs
    "tags": ["web-servers"],
    "type": "v1/insights/droplet/cpu",
    "compare": "GreaterThan",
    "value": 80,
    "window": "5m"
}

alert_resp = client.monitoring.create_alert_policy(body=alert_req)
```

## Projects

### List Projects

```python
# List all projects
projects_resp = client.projects.list()
projects = projects_resp['projects']
```

### Create Project

```python
# Create project
project_req = {
    "name": "Web Application",
    "description": "Production web application resources",
    "purpose": "Web Application",
    "environment": "Production"
}

project_resp = client.projects.create(body=project_req)
```

### Assign Resources to Project

```python
# Assign resources to project
client.projects.assign_resources(
    project_id="project-uuid",
    body={
        "resources": [
            "do:droplet:12345",
            "do:volume:vol-67890",
            "do:loadbalancer:lb-abcdef"
        ]
    }
)
```

## Error Handling

```python
from pydo import ClientException

try:
    droplet_resp = client.droplets.get(droplet_id=99999)
except ClientException as e:
    print(f"Error: {e}")
    if e.status == 404:
        print("Droplet not found")
    elif e.status == 401:
        print("Authentication failed")
    elif e.status == 429:
        print("Rate limit exceeded")
    else:
        print(f"API error: {e.status} - {e.body}")
```

## Common MCP Tool Patterns

### Droplet Management Tool

```python
def manage_droplet(action: str, **kwargs) -> dict:
    """Manage DigitalOcean droplets"""
    try:
        if action == "create":
            resp = client.droplets.create(body=kwargs)
            return {"success": True, "droplet": resp['droplet']}
        elif action == "list":
            resp = client.droplets.list()
            return {"success": True, "droplets": resp['droplets']}
        elif action == "get":
            resp = client.droplets.get(droplet_id=kwargs['droplet_id'])
            return {"success": True, "droplet": resp['droplet']}
        elif action == "destroy":
            client.droplets.destroy(droplet_id=kwargs['droplet_id'])
            return {"success": True, "message": "Droplet deleted"}
    except ClientException as e:
        return {"success": False, "error": str(e), "status": e.status}
```

### DNS Management Tool

```python
def manage_dns(domain: str, action: str, **kwargs) -> dict:
    """Manage DNS records for a domain"""
    try:
        if action == "list":
            resp = client.domains.list_records(domain_name=domain)
            return {"success": True, "records": resp['domain_records']}
        elif action == "create":
            resp = client.domains.create_record(domain_name=domain, body=kwargs)
            return {"success": True, "record": resp['domain_record']}
        elif action == "update":
            client.domains.update_record(
                domain_name=domain,
                domain_record_id=kwargs['record_id'],
                body=kwargs['data']
            )
            return {"success": True, "message": "Record updated"}
        elif action == "delete":
            client.domains.destroy_record(
                domain_name=domain,
                domain_record_id=kwargs['record_id']
            )
            return {"success": True, "message": "Record deleted"}
    except ClientException as e:
        return {"success": False, "error": str(e)}
```

## Rate Limiting and Best Practices

DigitalOcean API has rate limits:
- 5,000 requests per hour per token
- Some endpoints have lower limits

```python
import time
from functools import wraps

def rate_limited(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ClientException as e:
                    if e.status == 429 and attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    raise
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limited()
def safe_api_call():
    return client.droplets.list()
```