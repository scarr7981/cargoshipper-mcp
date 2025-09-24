# Docker API Reference for CargoShipper MCP

## Overview

This document provides comprehensive reference for Docker operations that CargoShipper MCP implements. It uses the official Docker SDK for Python (`docker-py`).

## Installation

```bash
pip install docker
```

## Client Initialization

```python
import docker

# Connect to Docker daemon
client = docker.from_env()  # Uses environment variables and docker socket

# Alternative: explicit connection
client = docker.DockerClient(base_url='unix://var/run/docker.sock')

# For remote Docker
client = docker.DockerClient(base_url='tcp://127.0.0.1:2375')
```

## Container Operations

### List Containers

```python
# List all containers
containers = client.containers.list(all=True)

# List running containers only
running = client.containers.list()

# With filters
containers = client.containers.list(
    filters={
        'status': 'running',
        'label': 'com.example.app=web'
    }
)
```

### Get Container

```python
# By ID or name
container = client.containers.get('container_id_or_name')

# Properties
print(container.id)
print(container.name)
print(container.status)  # 'running', 'exited', etc.
print(container.attrs)   # Full inspection data
```

### Create and Run Container

```python
# Simple run
container = client.containers.run(
    "ubuntu:latest",
    "echo hello world",
    detach=True
)

# Advanced run with options
container = client.containers.run(
    image="nginx:latest",
    name="my-nginx",
    ports={'80/tcp': 8080},
    volumes={
        '/host/path': {'bind': '/container/path', 'mode': 'rw'},
        'named_volume': {'bind': '/data', 'mode': 'rw'}
    },
    environment={
        "ENV_VAR": "value",
        "DEBUG": "true"
    },
    labels={
        "app": "web",
        "env": "prod"
    },
    restart_policy={"Name": "always"},
    detach=True,
    remove=False,
    network="my-network",
    command=None,  # Use image default
    entrypoint=None,  # Use image default
    working_dir="/app",
    user="1000:1000",
    mem_limit="512m",
    cpu_quota=50000,  # 50% of a CPU
    dns=['8.8.8.8', '8.8.4.4'],
    healthcheck={
        "test": ["CMD", "curl", "-f", "http://localhost/health"],
        "interval": 30000000000,  # 30s in nanoseconds
        "timeout": 10000000000,   # 10s
        "retries": 3,
        "start_period": 40000000000  # 40s
    }
)
```

### Container Lifecycle

```python
# Start
container.start()

# Stop (with timeout)
container.stop(timeout=10)

# Restart
container.restart(timeout=10)

# Pause/Unpause
container.pause()
container.unpause()

# Kill
container.kill(signal="SIGTERM")

# Remove
container.remove(force=True, v=True)  # v=True removes volumes too
```

### Container Execution

```python
# Execute command in running container
result = container.exec_run(
    cmd="ls -la /",
    stdout=True,
    stderr=True,
    stdin=False,
    tty=False,
    environment={"CUSTOM": "value"},
    workdir="/app",
    user="root",
    detach=False
)

print(result.exit_code)
print(result.output.decode())

# Interactive exec
exec_instance = container.exec_run(
    cmd="/bin/bash",
    stdin=True,
    tty=True,
    detach=True
)
```

### Container Logs

```python
# Get logs
logs = container.logs(
    stdout=True,
    stderr=True,
    stream=False,  # Return all at once
    timestamps=True,
    tail=100,  # Last 100 lines
    since=datetime.now() - timedelta(hours=1),  # Last hour
    follow=False
)

# Stream logs
for line in container.logs(stream=True, follow=True):
    print(line.decode().strip())
```

### Container Stats

```python
# Get one-time stats
stats = container.stats(stream=False)

# Stream stats
for stat in container.stats(stream=True):
    cpu_delta = stat['cpu_stats']['cpu_usage']['total_usage'] - \
                stat['precpu_stats']['cpu_usage']['total_usage']
    system_delta = stat['cpu_stats']['system_cpu_usage'] - \
                   stat['precpu_stats']['system_cpu_usage']
    cpu_percent = (cpu_delta / system_delta) * 100.0
    
    memory_usage = stat['memory_stats']['usage']
    memory_limit = stat['memory_stats']['limit']
    memory_percent = (memory_usage / memory_limit) * 100.0
```

## Image Operations

### List Images

```python
# List all images
images = client.images.list()

# With filters
images = client.images.list(
    filters={'dangling': False}
)

# Get specific image
image = client.images.get('nginx:latest')
```

### Pull Images

```python
# Simple pull
image = client.images.pull('ubuntu:latest')

# With authentication
image = client.images.pull(
    'private-registry.com/myimage:latest',
    auth_config={
        'username': 'user',
        'password': 'pass'
    }
)

# Pull with progress
for line in client.api.pull('ubuntu:latest', stream=True, decode=True):
    print(line)
```

### Build Images

```python
# Build from Dockerfile
image, logs = client.images.build(
    path='/path/to/dockerfile/directory',
    tag='myapp:latest',
    dockerfile='Dockerfile',  # Dockerfile name
    buildargs={
        'HTTP_PROXY': 'http://proxy.com:8080',
        'APP_VERSION': '1.0'
    },
    nocache=True,
    rm=True,  # Remove intermediate containers
    pull=True,  # Always pull base image
    forcerm=True,  # Always remove intermediate containers
    labels={'version': '1.0', 'env': 'prod'}
)

# Build from file-like object
with open('Dockerfile', 'rb') as f:
    image = client.images.build(
        fileobj=f,
        tag='myapp:latest'
    )
```

### Push Images

```python
# Push to registry
client.images.push(
    'myregistry.com/myimage:latest',
    auth_config={
        'username': 'user',
        'password': 'pass'
    }
)

# With progress
for line in client.images.push('myimage:latest', stream=True, decode=True):
    print(line)
```

### Remove Images

```python
# Remove image
client.images.remove('image:tag', force=True, noprune=False)

# Prune unused images
client.images.prune(filters={'dangling': True})
```

## Volume Operations

### Create Volumes

```python
# Create named volume
volume = client.volumes.create(
    name='my-volume',
    driver='local',
    driver_opts={
        'type': 'nfs',
        'o': 'addr=10.0.0.1,rw',
        'device': ':/path/to/share'
    },
    labels={'app': 'database'}
)
```

### List and Manage Volumes

```python
# List volumes
volumes = client.volumes.list()

# Get specific volume
volume = client.volumes.get('volume-name')

# Remove volume
volume.remove(force=True)

# Prune unused volumes
client.volumes.prune()
```

## Network Operations

### Create Networks

```python
# Create network
network = client.networks.create(
    name="my-network",
    driver="bridge",  # or "overlay", "host", "none"
    options={
        "com.docker.network.bridge.name": "docker1"
    },
    ipam={
        "Driver": "default",
        "Config": [{
            "Subnet": "172.20.0.0/16",
            "Gateway": "172.20.0.1"
        }]
    },
    labels={"env": "prod"},
    internal=False,
    attachable=True,
    enable_ipv6=False
)
```

### Network Management

```python
# List networks
networks = client.networks.list()

# Get network
network = client.networks.get('network-id-or-name')

# Connect container to network
network.connect(
    container,
    aliases=['web', 'app'],
    ipv4_address='172.20.0.5'
)

# Disconnect
network.disconnect(container, force=True)

# Remove network
network.remove()
```

## Docker Compose Operations

While docker-py doesn't directly support docker-compose, you can work with compose projects:

```python
# Parse compose file and create resources
import yaml

with open('docker-compose.yml', 'r') as f:
    compose_dict = yaml.safe_load(f)

# Create networks from compose
for network_name, network_config in compose_dict.get('networks', {}).items():
    client.networks.create(name=network_name, **network_config)

# Create volumes from compose
for volume_name, volume_config in compose_dict.get('volumes', {}).items():
    client.volumes.create(name=volume_name, **volume_config)

# Create services (containers) from compose
for service_name, service_config in compose_dict['services'].items():
    # Transform compose format to docker run format
    container_config = {
        'image': service_config['image'],
        'name': f"{project_name}_{service_name}_1",
        'environment': service_config.get('environment', {}),
        'volumes': service_config.get('volumes', []),
        'ports': service_config.get('ports', {}),
        'command': service_config.get('command'),
        'labels': service_config.get('labels', {}),
        'detach': True
    }
    client.containers.run(**container_config)
```

## System Operations

### Docker Info

```python
# System info
info = client.info()
print(f"Containers: {info['Containers']}")
print(f"Images: {info['Images']}")
print(f"Docker Root: {info['DockerRootDir']}")
print(f"Storage Driver: {info['Driver']}")

# Version info
version = client.version()
print(f"Docker Version: {version['Version']}")
print(f"API Version: {version['ApiVersion']}")
```

### System Prune

```python
# Prune everything
client.containers.prune()  # Stopped containers
client.images.prune()      # Unused images
client.networks.prune()    # Unused networks
client.volumes.prune()     # Unused volumes

# Or all at once
client.prune(
    containers=True,
    images=True,
    networks=True,
    volumes=True
)
```

### Events

```python
# Monitor Docker events
for event in client.events(decode=True):
    print(f"Type: {event['Type']}")
    print(f"Action: {event['Action']}")
    if event['Type'] == 'container':
        print(f"Container: {event['Actor']['Attributes']['name']}")

# With filters
events = client.events(
    filters={'type': 'container', 'event': 'start'},
    since=datetime.now() - timedelta(hours=1)
)
```

## Registry Operations

### Login to Registry

```python
client.login(
    username='user',
    password='pass',
    email='user@example.com',
    registry='https://registry.hub.docker.com',
    dockercfg_path='~/.docker/config.json'
)
```

### Search Images

```python
# Search Docker Hub
results = client.search('nginx', limit=10)
for result in results:
    print(f"{result['name']}: {result['description']}")
```

## Error Handling

```python
from docker.errors import (
    ContainerError,
    ImageNotFound,
    APIError,
    NotFound,
    BuildError
)

try:
    container = client.containers.run('ubuntu', 'exit 1')
except ContainerError as e:
    print(f"Container exited with non-zero code: {e.exit_status}")
    print(f"Output: {e.output}")
except ImageNotFound:
    print("Image not found")
except APIError as e:
    print(f"Docker API error: {e}")
```

## Best Practices

### 1. Resource Cleanup
```python
# Use remove=True for temporary containers
container = client.containers.run('ubuntu', 'echo test', remove=True)

# Or cleanup manually
try:
    container = client.containers.run('ubuntu', 'echo test')
finally:
    container.remove(force=True)
```

### 2. Health Checks
```python
# Wait for container to be healthy
def wait_for_healthy(container, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        container.reload()
        health = container.attrs['State']['Health']['Status']
        if health == 'healthy':
            return True
        time.sleep(1)
    return False
```

### 3. Log Formatting
```python
# Pretty print logs with timestamps
for line in container.logs(stream=True, timestamps=True):
    timestamp, message = line.decode().split(' ', 1)
    print(f"[{timestamp}] {message.strip()}")
```

### 4. Safe Container Names
```python
import re

def safe_container_name(name):
    # Docker container names must match [a-zA-Z0-9][a-zA-Z0-9_.-]*
    return re.sub(r'[^a-zA-Z0-9_.-]', '-', name).lower()
```

## Common Patterns for MCP Tools

### Container Run Tool
```python
def run_container(image: str, command: str = None, **kwargs) -> dict:
    """Run a Docker container with specified configuration"""
    try:
        container = client.containers.run(
            image=image,
            command=command,
            detach=True,
            **kwargs
        )
        return {
            "success": True,
            "container_id": container.id,
            "container_name": container.name,
            "status": container.status
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### Image Management Tool
```python
def manage_image(action: str, image: str, **kwargs) -> dict:
    """Manage Docker images (pull, remove, build)"""
    if action == "pull":
        image_obj = client.images.pull(image)
        return {"success": True, "image_id": image_obj.id}
    elif action == "remove":
        client.images.remove(image, force=kwargs.get('force', False))
        return {"success": True, "message": f"Removed {image}"}
    elif action == "build":
        image_obj, logs = client.images.build(path=kwargs['path'], tag=image)
        return {"success": True, "image_id": image_obj.id, "logs": logs}
```

### Container Logs Tool
```python
def get_container_logs(container_id: str, tail: int = 100) -> str:
    """Get logs from a container"""
    container = client.containers.get(container_id)
    logs = container.logs(tail=tail, timestamps=True)
    return logs.decode('utf-8')
```