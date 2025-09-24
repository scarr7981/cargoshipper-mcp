# CloudFlare API Reference for CargoShipper MCP

## Overview

This document provides comprehensive reference for CloudFlare operations using the official CloudFlare Python SDK. The library provides convenient access to the CloudFlare REST API from Python 3.8+ applications.

## Installation

```bash
pip install cloudflare
```

## Authentication

CloudFlare API supports multiple authentication methods:

### API Token (Recommended)

```python
import cloudflare

# Using API token (recommended)
cf = cloudflare.Cloudflare(api_token="your_api_token_here")

# From environment variable
# export CLOUDFLARE_API_TOKEN="your_token_here"
cf = cloudflare.Cloudflare()  # Will read from CLOUDFLARE_API_TOKEN
```

### Global API Key (Legacy)

```python
# Using email + global API key (legacy method)
cf = cloudflare.Cloudflare(
    api_email="user@example.com",
    api_key="your_global_api_key"
)

# From environment variables
# export CLOUDFLARE_EMAIL="user@example.com"
# export CLOUDFLARE_API_KEY="your_global_api_key"
cf = cloudflare.Cloudflare()
```

## Account Operations

### Get Account Information

```python
# List accounts
accounts = cf.accounts.list()

for account in accounts:
    print(f"Account ID: {account.id}")
    print(f"Name: {account.name}")
    print(f"Type: {account.type}")

# Get specific account
account_id = "your_account_id"
account = cf.accounts.get(account_id=account_id)
```

### Account Settings

```python
# Get account settings
settings = cf.accounts.settings.get(account_id=account_id)

# Update account settings
cf.accounts.settings.update(
    account_id=account_id,
    body={
        "enforce_twofactor": True,
        "use_account_custom_ns_by_default": False
    }
)
```

## Zone Operations

### List Zones

```python
# List all zones
zones = cf.zones.list()

for zone in zones:
    print(f"Zone ID: {zone.id}")
    print(f"Name: {zone.name}")
    print(f"Status: {zone.status}")
    print(f"Name servers: {zone.name_servers}")

# With pagination
zones = cf.zones.list(per_page=50, page=1)

# With filters
zones = cf.zones.list(
    name="example.com",
    status="active",
    account={"id": account_id}
)
```

### Get Zone

```python
# Get specific zone
zone_id = "your_zone_id"
zone = cf.zones.get(zone_id=zone_id)

print(f"Zone: {zone.name}")
print(f"Status: {zone.status}")
print(f"Paused: {zone.paused}")
print(f"Development Mode: {zone.development_mode}")
print(f"Name Servers: {zone.name_servers}")
```

### Create Zone

```python
# Create new zone
new_zone = cf.zones.create(
    body={
        "name": "example.com",
        "account": {"id": account_id},
        "jump_start": True,  # Import existing DNS records
        "type": "full"  # Full setup (vs partial)
    }
)

print(f"Created zone: {new_zone.id}")
print(f"Name servers: {new_zone.name_servers}")
```

### Zone Settings

```python
# Get zone settings
settings = cf.zones.settings.get(zone_id=zone_id)

# Update specific setting
cf.zones.settings.ssl.update(
    zone_id=zone_id,
    value="flexible"  # off, flexible, full, strict
)

cf.zones.settings.always_use_https.update(
    zone_id=zone_id,
    value="on"
)

cf.zones.settings.security_level.update(
    zone_id=zone_id,
    value="medium"  # off, essentially_off, low, medium, high, under_attack
)

cf.zones.settings.cache_level.update(
    zone_id=zone_id,
    value="aggressive"  # aggressive, basic, simplified
)

cf.zones.settings.development_mode.update(
    zone_id=zone_id,
    value="on"  # Bypasses cache for 3 hours
)
```

### Delete Zone

```python
# Delete zone
cf.zones.delete(zone_id=zone_id)
```

## DNS Record Operations

### List DNS Records

```python
# List all DNS records for a zone
records = cf.dns_records.list(zone_id=zone_id)

for record in records:
    print(f"ID: {record.id}")
    print(f"Type: {record.type}")
    print(f"Name: {record.name}")
    print(f"Content: {record.content}")
    print(f"TTL: {record.ttl}")

# With filters
records = cf.dns_records.list(
    zone_id=zone_id,
    type="A",
    name="www.example.com"
)
```

### Get DNS Record

```python
# Get specific DNS record
record_id = "dns_record_id"
record = cf.dns_records.get(zone_id=zone_id, dns_record_id=record_id)
```

### Create DNS Record

```python
# Create A record
a_record = cf.dns_records.create(
    zone_id=zone_id,
    body={
        "type": "A",
        "name": "www",
        "content": "192.0.2.1",
        "ttl": 3600,
        "proxied": True  # Orange cloud (proxied through Cloudflare)
    }
)

# Create CNAME record
cname_record = cf.dns_records.create(
    zone_id=zone_id,
    body={
        "type": "CNAME",
        "name": "blog",
        "content": "example.com",
        "ttl": 1,  # 1 = Auto
        "proxied": False
    }
)

# Create MX record
mx_record = cf.dns_records.create(
    zone_id=zone_id,
    body={
        "type": "MX",
        "name": "@",  # Root domain
        "content": "mail.example.com",
        "priority": 10,
        "ttl": 3600
    }
)

# Create TXT record
txt_record = cf.dns_records.create(
    zone_id=zone_id,
    body={
        "type": "TXT",
        "name": "@",
        "content": "v=spf1 include:_spf.google.com ~all",
        "ttl": 3600
    }
)

# Create SRV record
srv_record = cf.dns_records.create(
    zone_id=zone_id,
    body={
        "type": "SRV",
        "name": "_sip._tcp",
        "data": {
            "service": "_sip",
            "proto": "_tcp",
            "name": "example.com",
            "priority": 10,
            "weight": 5,
            "port": 5060,
            "target": "sip.example.com"
        },
        "ttl": 3600
    }
)
```

### Update DNS Record

```python
# Update DNS record
cf.dns_records.update(
    zone_id=zone_id,
    dns_record_id=record_id,
    body={
        "type": "A",
        "name": "www",
        "content": "192.0.2.100",  # New IP
        "ttl": 1800,  # New TTL
        "proxied": False  # Disable proxy
    }
)
```

### Delete DNS Record

```python
# Delete DNS record
cf.dns_records.delete(zone_id=zone_id, dns_record_id=record_id)
```

## SSL/TLS Operations

### SSL Settings

```python
# Get SSL settings
ssl_settings = cf.zones.settings.ssl.get(zone_id=zone_id)

# Update SSL mode
cf.zones.settings.ssl.update(
    zone_id=zone_id,
    value="strict"  # off, flexible, full, strict
)

# Enable Always Use HTTPS
cf.zones.settings.always_use_https.update(
    zone_id=zone_id,
    value="on"
)

# Enable HTTP Strict Transport Security (HSTS)
cf.zones.settings.security_header.update(
    zone_id=zone_id,
    value={
        "strict_transport_security": {
            "enabled": True,
            "max_age": 31536000,  # 1 year
            "include_subdomains": True,
            "preload": True
        }
    }
)
```

### Custom SSL Certificates

```python
# Upload custom SSL certificate
custom_cert = cf.custom_certificates.create(
    zone_id=zone_id,
    body={
        "certificate": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
        "bundle_method": "ubiquitous"  # ubiquitous, optimal, force
    }
)

# List custom certificates
certificates = cf.custom_certificates.list(zone_id=zone_id)

# Update certificate priority
cf.custom_certificates.prioritize.update(
    zone_id=zone_id,
    body={
        "certificates": [
            {"id": cert_id, "priority": 1},
            {"id": cert_id_2, "priority": 2}
        ]
    }
)
```

### Universal SSL

```python
# Get Universal SSL settings
universal_ssl = cf.ssl.universal.settings.get(zone_id=zone_id)

# Update Universal SSL settings
cf.ssl.universal.settings.edit(
    zone_id=zone_id,
    body={"enabled": True}
)
```

## Page Rules

### Create Page Rule

```python
# Create page rule
page_rule = cf.pagerules.create(
    zone_id=zone_id,
    body={
        "targets": [
            {
                "target": "url",
                "constraint": {
                    "operator": "matches",
                    "value": "*example.com/images/*"
                }
            }
        ],
        "actions": [
            {
                "id": "cache_level",
                "value": "cache_everything"
            },
            {
                "id": "edge_cache_ttl",
                "value": 86400  # 24 hours
            }
        ],
        "priority": 1,
        "status": "active"
    }
)

# Common page rule actions:
actions = [
    {"id": "always_online", "value": "on"},
    {"id": "always_use_https", "value": True},
    {"id": "browser_cache_ttl", "value": 3600},
    {"id": "browser_check", "value": "on"},
    {"id": "cache_level", "value": "cache_everything"},
    {"id": "disable_apps", "value": True},
    {"id": "disable_performance", "value": True},
    {"id": "disable_railgun", "value": True},
    {"id": "disable_security", "value": True},
    {"id": "edge_cache_ttl", "value": 86400},
    {"id": "email_obfuscation", "value": "on"},
    {"id": "forwarding_url", "value": {"url": "https://example.com", "status_code": 301}},
    {"id": "ip_geolocation", "value": "on"},
    {"id": "mirage", "value": "on"},
    {"id": "opportunistic_encryption", "value": "on"},
    {"id": "polish", "value": "lossless"},
    {"id": "resolve_override", "value": "example.com"},
    {"id": "rocket_loader", "value": "on"},
    {"id": "security_level", "value": "medium"},
    {"id": "server_side_exclude", "value": "on"},
    {"id": "ssl", "value": "flexible"},
    {"id": "waf", "value": "on"}
]
```

### List and Manage Page Rules

```python
# List page rules
page_rules = cf.pagerules.list(zone_id=zone_id)

# Update page rule
cf.pagerules.update(
    zone_id=zone_id,
    pagerule_id=page_rule_id,
    body={
        "targets": [...],
        "actions": [...],
        "priority": 2,
        "status": "disabled"
    }
)

# Delete page rule
cf.pagerules.delete(zone_id=zone_id, pagerule_id=page_rule_id)
```

## CloudFlare Workers

### Deploy Worker

```python
# Upload worker script
worker_script = """
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  return new Response('Hello from Cloudflare Worker!', {
    headers: { 'content-type': 'text/plain' },
  })
}
"""

# Deploy worker
worker = cf.workers.scripts.update(
    account_id=account_id,
    script_name="my-worker",
    body=worker_script,
    metadata={
        "body_part": "script",
        "content_type": "application/javascript"
    }
)

# With bindings
worker_with_bindings = cf.workers.scripts.update(
    account_id=account_id,
    script_name="my-worker",
    body=worker_script,
    metadata={
        "bindings": [
            {
                "name": "MY_KV",
                "type": "kv_namespace",
                "namespace_id": "kv_namespace_id"
            },
            {
                "name": "MY_SECRET",
                "type": "secret_text",
                "text": "secret_value"
            }
        ]
    }
)
```

### Worker Routes

```python
# Create worker route
route = cf.workers.routes.create(
    zone_id=zone_id,
    body={
        "pattern": "example.com/api/*",
        "script": "my-worker"
    }
)

# List worker routes
routes = cf.workers.routes.list(zone_id=zone_id)

# Update worker route
cf.workers.routes.update(
    zone_id=zone_id,
    route_id=route_id,
    body={
        "pattern": "example.com/api/v2/*",
        "script": "my-worker-v2"
    }
)

# Delete worker route
cf.workers.routes.delete(zone_id=zone_id, route_id=route_id)
```

### KV Storage

```python
# Create KV namespace
kv_namespace = cf.kv.namespaces.create(
    account_id=account_id,
    body={"title": "my-kv-store"}
)
namespace_id = kv_namespace.id

# Write to KV
cf.kv.namespaces.values.update(
    account_id=account_id,
    namespace_id=namespace_id,
    key_name="my-key",
    value="my-value"
)

# Read from KV
value = cf.kv.namespaces.values.get(
    account_id=account_id,
    namespace_id=namespace_id,
    key_name="my-key"
)

# List KV keys
keys = cf.kv.namespaces.keys.list(
    account_id=account_id,
    namespace_id=namespace_id
)

# Delete KV key
cf.kv.namespaces.values.delete(
    account_id=account_id,
    namespace_id=namespace_id,
    key_name="my-key"
)
```

## Analytics

### Zone Analytics

```python
# Get zone analytics dashboard
analytics = cf.zones.analytics.dashboard.get(
    zone_id=zone_id,
    since="2024-01-01T00:00:00Z",
    until="2024-01-31T23:59:59Z",
    continuous=True
)

print(f"Total requests: {analytics.totals['requests']['all']}")
print(f"Bandwidth: {analytics.totals['bandwidth']['all']}")
print(f"Threats: {analytics.totals['threats']['all']}")
print(f"Page views: {analytics.totals['pageviews']['all']}")

# Get zone analytics by time series
time_series = cf.zones.analytics.dashboard.get(
    zone_id=zone_id,
    since="2024-01-01T00:00:00Z",
    until="2024-01-31T23:59:59Z",
    continuous=False  # Get time series data
)
```

### DNS Analytics

```python
# Get DNS analytics
dns_analytics = cf.zones.dns_analytics.report.get(
    zone_id=zone_id,
    since="2024-01-01T00:00:00Z",
    until="2024-01-31T23:59:59Z",
    dimensions="queryType,responseCode",
    metrics="queryCount,uncachedCount"
)
```

## Firewall Rules

### Create Firewall Rule

```python
# Create firewall rule
firewall_rule = cf.firewall.rules.create(
    zone_id=zone_id,
    body=[
        {
            "filter": {
                "expression": "(http.request.uri.path contains \"/admin\")",
                "paused": False
            },
            "action": "challenge",  # allow, block, challenge, js_challenge, managed_challenge
            "priority": 1000,
            "paused": False,
            "description": "Challenge requests to admin area"
        }
    ]
)

# More complex rule
complex_rule = cf.firewall.rules.create(
    zone_id=zone_id,
    body=[
        {
            "filter": {
                "expression": "(http.request.uri.path eq \"/api/login\" and not cf.client.bot) or (ip.geoip.country eq \"CN\")",
                "paused": False
            },
            "action": "block",
            "priority": 500,
            "paused": False,
            "description": "Block suspicious login attempts and China traffic"
        }
    ]
)
```

### Access Rules (IP-based)

```python
# Create IP access rule
access_rule = cf.firewall.access_rules.rules.create(
    zone_id=zone_id,
    body={
        "mode": "block",  # block, challenge, whitelist, js_challenge
        "configuration": {
            "target": "ip",
            "value": "192.0.2.0/24"  # Can be IP, IP range, country code, ASN
        },
        "notes": "Block suspicious IP range"
    }
)

# Create country access rule
country_rule = cf.firewall.access_rules.rules.create(
    zone_id=zone_id,
    body={
        "mode": "challenge",
        "configuration": {
            "target": "country",
            "value": "CN"
        },
        "notes": "Challenge traffic from China"
    }
)
```

## Rate Limiting

### Create Rate Limit Rule

```python
# Create rate limit rule
rate_limit = cf.rate_limits.create(
    zone_id=zone_id,
    body={
        "match": {
            "request": {
                "methods": ["POST"],
                "schemes": ["HTTPS"],
                "url": "example.com/api/login"
            },
            "response": {
                "status": [200, 201, 202, 301, 302, 303, 307, 308]
            }
        },
        "threshold": 10,  # 10 requests
        "period": 60,     # per 60 seconds
        "action": {
            "mode": "ban",  # simulate, ban, challenge, js_challenge
            "timeout": 3600,  # 1 hour ban
            "response": {
                "content_type": "text/plain",
                "body": "Rate limit exceeded"
            }
        },
        "disabled": False,
        "description": "Rate limit login attempts",
        "bypass": [
            {
                "name": "url",
                "value": "example.com/api/health"
            }
        ]
    }
)
```

## Purge Cache

### Purge Operations

```python
# Purge everything
cf.zones.purge_cache.create(
    zone_id=zone_id,
    body={"purge_everything": True}
)

# Purge by URLs
cf.zones.purge_cache.create(
    zone_id=zone_id,
    body={
        "files": [
            "https://example.com/image.jpg",
            "https://example.com/styles.css"
        ]
    }
)

# Purge by cache tags
cf.zones.purge_cache.create(
    zone_id=zone_id,
    body={
        "tags": ["blog-posts", "user-content"]
    }
)

# Purge by hostname
cf.zones.purge_cache.create(
    zone_id=zone_id,
    body={
        "hosts": ["www.example.com", "api.example.com"]
    }
)
```

## Load Balancing

### Create Load Balancer

```python
# Create origin pool
pool = cf.load_balancers.pools.create(
    account_id=account_id,
    body={
        "name": "web-servers",
        "description": "Web server pool",
        "enabled": True,
        "monitor": "monitor_id",
        "origins": [
            {
                "name": "web-1",
                "address": "192.0.2.1",
                "enabled": True,
                "weight": 1
            },
            {
                "name": "web-2", 
                "address": "192.0.2.2",
                "enabled": True,
                "weight": 1
            }
        ],
        "notification_email": "admin@example.com"
    }
)

# Create load balancer
load_balancer = cf.load_balancers.create(
    zone_id=zone_id,
    body={
        "name": "www.example.com",
        "description": "Load balancer for web traffic",
        "ttl": 30,
        "proxied": True,
        "enabled": True,
        "default_pools": [pool.id],
        "fallback_pool": pool.id,
        "region_pools": {
            "WNAM": [pool.id],  # Western North America
            "ENAM": [pool.id]   # Eastern North America
        },
        "pop_pools": {},
        "country_pools": {},
        "steering_policy": "dynamic_latency"  # off, geo, dynamic_latency, random, proximity
    }
)
```

### Health Monitors

```python
# Create health monitor
monitor = cf.load_balancers.monitors.create(
    account_id=account_id,
    body={
        "type": "https",
        "description": "HTTPS health check",
        "method": "GET",
        "path": "/health",
        "header": {
            "Host": ["example.com"],
            "X-App-ID": ["abc123"]
        },
        "port": 443,
        "timeout": 10,
        "retries": 2,
        "interval": 60,
        "expected_body": "OK",
        "expected_codes": "200",
        "follow_redirects": True,
        "allow_insecure": False,
        "probe_zone": "example.com"
    }
)
```

## Error Handling

```python
from cloudflare import APIError, BadRequestError, AuthenticationError, NotFoundError

try:
    zone = cf.zones.get(zone_id="invalid_zone_id")
except NotFoundError as e:
    print(f"Zone not found: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except BadRequestError as e:
    print(f"Bad request: {e}")
except APIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")
```

## Common MCP Tool Patterns

### Zone Management Tool

```python
def manage_zone(action: str, **kwargs) -> dict:
    """Manage CloudFlare zones"""
    try:
        if action == "list":
            zones = cf.zones.list()
            return {"success": True, "zones": [{"id": z.id, "name": z.name, "status": z.status} for z in zones]}
        elif action == "get":
            zone = cf.zones.get(zone_id=kwargs['zone_id'])
            return {"success": True, "zone": {"id": zone.id, "name": zone.name, "status": zone.status}}
        elif action == "create":
            zone = cf.zones.create(body=kwargs)
            return {"success": True, "zone_id": zone.id, "name_servers": zone.name_servers}
        elif action == "delete":
            cf.zones.delete(zone_id=kwargs['zone_id'])
            return {"success": True, "message": "Zone deleted"}
    except APIError as e:
        return {"success": False, "error": str(e), "status_code": e.status_code}
```

### DNS Management Tool

```python
def manage_dns(zone_id: str, action: str, **kwargs) -> dict:
    """Manage DNS records"""
    try:
        if action == "list":
            records = cf.dns_records.list(zone_id=zone_id)
            return {"success": True, "records": [
                {
                    "id": r.id, "type": r.type, "name": r.name, 
                    "content": r.content, "ttl": r.ttl, "proxied": r.proxied
                } for r in records
            ]}
        elif action == "create":
            record = cf.dns_records.create(zone_id=zone_id, body=kwargs)
            return {"success": True, "record_id": record.id}
        elif action == "update":
            cf.dns_records.update(
                zone_id=zone_id,
                dns_record_id=kwargs['record_id'],
                body=kwargs['data']
            )
            return {"success": True, "message": "Record updated"}
        elif action == "delete":
            cf.dns_records.delete(
                zone_id=zone_id,
                dns_record_id=kwargs['record_id']
            )
            return {"success": True, "message": "Record deleted"}
    except APIError as e:
        return {"success": False, "error": str(e)}
```

### Cache Management Tool

```python
def manage_cache(zone_id: str, action: str, **kwargs) -> dict:
    """Manage CloudFlare cache"""
    try:
        if action == "purge_all":
            cf.zones.purge_cache.create(
                zone_id=zone_id,
                body={"purge_everything": True}
            )
            return {"success": True, "message": "All cache purged"}
        elif action == "purge_urls":
            cf.zones.purge_cache.create(
                zone_id=zone_id,
                body={"files": kwargs['urls']}
            )
            return {"success": True, "message": f"Purged {len(kwargs['urls'])} URLs"}
        elif action == "purge_tags":
            cf.zones.purge_cache.create(
                zone_id=zone_id,
                body={"tags": kwargs['tags']}
            )
            return {"success": True, "message": f"Purged tags: {kwargs['tags']}"}
    except APIError as e:
        return {"success": False, "error": str(e)}
```

## Rate Limiting and Best Practices

CloudFlare API has rate limits:
- 1,200 requests per 5 minutes per API token
- Some endpoints have specific limits

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
                except APIError as e:
                    if e.status_code == 429 and attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                        continue
                    raise
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limited()
def safe_api_call():
    return cf.zones.list()
```

## Advanced Features

### Edge Certificates

```python
# Order dedicated certificate
cert_order = cf.ssl.certificate_packs.order.create(
    zone_id=zone_id,
    body={
        "type": "dedicated",
        "hosts": ["example.com", "www.example.com"],
        "validation_method": "txt",
        "validity_days": 365,
        "certificate_authority": "digicert"
    }
)
```

### WAF Rules

```python
# Get WAF packages
packages = cf.zones.firewall.waf.packages.list(zone_id=zone_id)

# Get WAF rules for a package
rules = cf.zones.firewall.waf.packages.rules.list(
    zone_id=zone_id,
    package_id=package_id
)

# Update WAF rule
cf.zones.firewall.waf.packages.rules.update(
    zone_id=zone_id,
    package_id=package_id,
    rule_id=rule_id,
    body={"mode": "block"}  # default, disable, simulate, block, challenge
)
```