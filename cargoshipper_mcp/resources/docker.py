"""Docker resources for CargoShipper MCP server"""

from typing import Callable
from docker.errors import NotFound, DockerException


def register_resources(mcp, get_client: Callable):
    """Register Docker resources"""
    
    @mcp.resource("docker://containers")
    def list_containers_resource() -> str:
        """Resource to list all Docker containers"""
        try:
            client = get_client()
            containers = client.containers.list(all=True)
            
            if not containers:
                return "# Docker Containers\n\nNo containers found."
            
            output = ["# Docker Containers\n"]
            running_count = 0
            stopped_count = 0
            
            for container in containers:
                status_emoji = "🟢" if container.status == "running" else "🔴"
                if container.status == "running":
                    running_count += 1
                else:
                    stopped_count += 1
                    
                output.append(f"## {status_emoji} {container.name}")
                output.append(f"- **ID**: {container.id[:12]}")
                output.append(f"- **Image**: {container.image.tags[0] if container.image.tags else container.image.id[:12]}")
                output.append(f"- **Status**: {container.status}")
                output.append(f"- **Created**: {container.attrs['Created']}")
                
                # Port information
                ports = container.attrs['NetworkSettings']['Ports']
                if ports:
                    port_mappings = []
                    for container_port, host_bindings in ports.items():
                        if host_bindings:
                            for binding in host_bindings:
                                port_mappings.append(f"{container_port} → {binding['HostIp']}:{binding['HostPort']}")
                        else:
                            port_mappings.append(f"{container_port} (not bound)")
                    if port_mappings:
                        output.append(f"- **Ports**: {', '.join(port_mappings)}")
                
                output.append("")
            
            output.insert(1, f"**Summary**: {running_count} running, {stopped_count} stopped\n")
            
            return "\n".join(output)
            
        except DockerException as e:
            return f"# Docker Containers\n\nError accessing Docker: {e}"
    
    @mcp.resource("docker://container/{container_id}")
    def get_container_resource(container_id: str) -> str:
        """Resource to get detailed information about a specific container"""
        try:
            client = get_client()
            container = client.containers.get(container_id)
            
            output = [f"# Container: {container.name}\n"]
            
            # Basic information
            output.append("## Basic Information")
            output.append(f"- **ID**: {container.id}")
            output.append(f"- **Name**: {container.name}")
            output.append(f"- **Status**: {container.status}")
            output.append(f"- **Image**: {container.image.tags[0] if container.image.tags else container.image.id[:12]}")
            output.append(f"- **Created**: {container.attrs['Created']}")
            output.append(f"- **Started**: {container.attrs['State']['StartedAt']}")
            
            # State information
            state = container.attrs['State']
            output.append("\n## State")
            output.append(f"- **Running**: {state.get('Running', False)}")
            output.append(f"- **Exit Code**: {state.get('ExitCode', 'N/A')}")
            output.append(f"- **Error**: {state.get('Error', 'None')}")
            
            # Network information
            networks = container.attrs['NetworkSettings']['Networks']
            if networks:
                output.append("\n## Networks")
                for network_name, network_info in networks.items():
                    ip_address = network_info.get('IPAddress', 'N/A')
                    gateway = network_info.get('Gateway', 'N/A')
                    output.append(f"- **{network_name}**: {ip_address} (Gateway: {gateway})")
            
            # Port mappings
            ports = container.attrs['NetworkSettings']['Ports']
            if ports:
                output.append("\n## Port Mappings")
                for container_port, host_bindings in ports.items():
                    if host_bindings:
                        for binding in host_bindings:
                            output.append(f"- **{container_port}** → {binding['HostIp']}:{binding['HostPort']}")
                    else:
                        output.append(f"- **{container_port}** (not bound)")
            
            # Environment variables
            env_vars = container.attrs['Config']['Env']
            if env_vars:
                output.append("\n## Environment Variables")
                for env_var in env_vars:
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        # Hide sensitive values
                        if any(sensitive in key.lower() for sensitive in ['password', 'token', 'key', 'secret']):
                            value = '***'
                        output.append(f"- **{key}**: {value}")
            
            # Volume mounts
            mounts = container.attrs.get('Mounts', [])
            if mounts:
                output.append("\n## Volume Mounts")
                for mount in mounts:
                    mount_type = mount.get('Type', 'unknown')
                    source = mount.get('Source', 'N/A')
                    destination = mount.get('Destination', 'N/A')
                    mode = mount.get('Mode', 'N/A')
                    output.append(f"- **{mount_type}**: {source} → {destination} ({mode})")
            
            # Resource limits
            host_config = container.attrs.get('HostConfig', {})
            if host_config:
                output.append("\n## Resource Limits")
                memory = host_config.get('Memory', 0)
                cpu_shares = host_config.get('CpuShares', 0)
                if memory > 0:
                    memory_mb = memory // (1024 * 1024)
                    output.append(f"- **Memory**: {memory_mb} MB")
                if cpu_shares > 0:
                    output.append(f"- **CPU Shares**: {cpu_shares}")
            
            return "\n".join(output)
            
        except NotFound:
            return f"# Container Not Found\n\nContainer `{container_id}` not found."
        except DockerException as e:
            return f"# Container Error\n\nError accessing container `{container_id}`: {e}"
    
    @mcp.resource("docker://container/{container_id}/logs")
    def get_container_logs_resource(container_id: str) -> str:
        """Resource to get logs from a specific container"""
        try:
            client = get_client()
            container = client.containers.get(container_id)
            
            logs = container.logs(tail=50, timestamps=True)
            log_output = logs.decode('utf-8') if isinstance(logs, bytes) else str(logs)
            
            output = [f"# Logs for {container.name}"]
            output.append(f"**Container ID**: {container.id[:12]}")
            output.append(f"**Status**: {container.status}")
            output.append("")
            output.append("```")
            output.append(log_output.strip())
            output.append("```")
            
            return "\n".join(output)
            
        except NotFound:
            return f"# Container Not Found\n\nContainer `{container_id}` not found."
        except DockerException as e:
            return f"# Container Logs Error\n\nError getting logs for `{container_id}`: {e}"
    
    @mcp.resource("docker://images")
    def list_images_resource() -> str:
        """Resource to list all Docker images"""
        try:
            client = get_client()
            images = client.images.list()
            
            if not images:
                return "# Docker Images\n\nNo images found."
            
            output = ["# Docker Images\n"]
            total_size = 0
            
            for image in images:
                size = image.attrs.get("Size", 0)
                total_size += size
                size_mb = size // (1024 * 1024)
                
                # Get the first tag or use image ID
                display_name = image.tags[0] if image.tags else image.id[:12]
                
                output.append(f"## {display_name}")
                output.append(f"- **ID**: {image.id[:12]}")
                if image.tags:
                    output.append(f"- **Tags**: {', '.join(image.tags)}")
                output.append(f"- **Size**: {size_mb} MB")
                output.append(f"- **Created**: {image.attrs.get('Created', 'Unknown')}")
                output.append("")
            
            total_size_mb = total_size // (1024 * 1024)
            output.insert(1, f"**Total Images**: {len(images)} ({total_size_mb} MB)\n")
            
            return "\n".join(output)
            
        except DockerException as e:
            return f"# Docker Images\n\nError accessing Docker images: {e}"
    
    @mcp.resource("docker://system")
    def system_info_resource() -> str:
        """Resource to get Docker system information"""
        try:
            client = get_client()
            info = client.info()
            
            output = ["# Docker System Information\n"]
            
            # Basic system info
            output.append("## System")
            output.append(f"- **Server Version**: {info.get('ServerVersion', 'Unknown')}")
            output.append(f"- **Operating System**: {info.get('OperatingSystem', 'Unknown')}")
            output.append(f"- **Architecture**: {info.get('Architecture', 'Unknown')}")
            output.append(f"- **CPUs**: {info.get('NCPU', 'Unknown')}")
            memory_gb = info.get('MemTotal', 0) // (1024 * 1024 * 1024)
            output.append(f"- **Memory**: {memory_gb} GB")
            
            # Container statistics
            output.append("\n## Containers")
            output.append(f"- **Total**: {info.get('Containers', 0)}")
            output.append(f"- **Running**: {info.get('ContainersRunning', 0)}")
            output.append(f"- **Paused**: {info.get('ContainersPaused', 0)}")
            output.append(f"- **Stopped**: {info.get('ContainersStopped', 0)}")
            
            # Image statistics
            output.append("\n## Images")
            output.append(f"- **Total Images**: {info.get('Images', 0)}")
            
            # Storage information
            output.append("\n## Storage")
            output.append(f"- **Storage Driver**: {info.get('Driver', 'Unknown')}")
            
            # Registry information
            registry_config = info.get('RegistryConfig', {})
            if registry_config:
                insecure_registries = registry_config.get('InsecureRegistryCIDRs', [])
                if insecure_registries:
                    output.append("\n## Registry Configuration")
                    output.append(f"- **Insecure Registries**: {', '.join(insecure_registries)}")
            
            return "\n".join(output)
            
        except DockerException as e:
            return f"# Docker System Information\n\nError accessing Docker system info: {e}"