"""Docker API integration tools for CargoShipper MCP server"""

from typing import Dict, Any, List, Optional, Callable
import docker
from docker.errors import DockerException, NotFound, APIError

from ..utils.validation import validate_container_name, validate_image_name, validate_port
from ..utils.formatters import format_success_response, format_error_response, format_container_info
from ..utils.errors import CargoShipperError, ValidationError


def register_tools(mcp, get_client: Callable):
    """Register Docker tools with MCP server"""
    
    @mcp.tool()
    def docker_run_container(
        image: str,
        name: Optional[str] = None,
        command: Optional[str] = None,
        ports: Optional[Dict[str, int]] = None,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, str]] = None,
        detach: bool = True,
        remove: bool = False
    ) -> Dict[str, Any]:
        """Run a Docker container with specified configuration
        
        Args:
            image: Docker image name (e.g., 'nginx:latest')
            name: Optional container name
            command: Optional command to run
            ports: Optional port mappings {"container_port": host_port}
            environment: Optional environment variables
            volumes: Optional volume mounts {"host_path": "container_path"}
            detach: Run in detached mode (default: True)
            remove: Remove container when it stops (default: False)
        """
        try:
            client = get_client()
            
            # Validate inputs
            validate_image_name(image)
            if name:
                validate_container_name(name)
            if ports:
                for container_port, host_port in ports.items():
                    validate_port(host_port)
            
            # Prepare run arguments
            run_kwargs = {
                "image": image,
                "detach": detach,
                "remove": remove
            }
            
            if name:
                run_kwargs["name"] = name
            if command:
                run_kwargs["command"] = command
            if ports:
                run_kwargs["ports"] = ports
            if environment:
                run_kwargs["environment"] = environment
            if volumes:
                # Convert simple dict to volume mount format
                volume_mounts = {}
                for host_path, container_path in volumes.items():
                    volume_mounts[host_path] = {"bind": container_path, "mode": "rw"}
                run_kwargs["volumes"] = volume_mounts
            
            # Run container
            container = client.containers.run(**run_kwargs)
            
            return format_success_response({
                "container_id": container.id,
                "container_name": container.name,
                "status": container.status,
                "image": image,
                "detached": detach
            }, "run_container")
            
        except ValidationError as e:
            return format_error_response(str(e), "run_container")
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "run_container")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "run_container")
    
    @mcp.tool()
    def docker_list_containers(
        all_containers: bool = True,
        filters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """List Docker containers
        
        Args:
            all_containers: Include stopped containers (default: True)
            filters: Optional filters {"key": "value"}
        """
        try:
            client = get_client()
            
            containers = client.containers.list(all=all_containers, filters=filters or {})
            
            container_list = []
            for container in containers:
                container_info = format_container_info(container)
                container_list.append(container_info)
            
            return format_success_response({
                "containers": container_list,
                "total": len(container_list),
                "all_containers": all_containers,
                "filters": filters or {}
            }, "list_containers")
            
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "list_containers")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "list_containers")
    
    @mcp.tool()
    def docker_stop_container(
        container_id: str,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """Stop a Docker container
        
        Args:
            container_id: Container ID or name
            timeout: Timeout in seconds before forcefully killing
        """
        try:
            client = get_client()
            
            container = client.containers.get(container_id)
            container.stop(timeout=timeout)
            
            return format_success_response({
                "container_id": container.id[:12],
                "name": container.name,
                "status": "stopped",
                "timeout": timeout
            }, "stop_container")
            
        except NotFound:
            return format_error_response(f"Container {container_id} not found", "stop_container")
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "stop_container")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "stop_container")
    
    @mcp.tool()
    def docker_start_container(container_id: str) -> Dict[str, Any]:
        """Start a stopped Docker container
        
        Args:
            container_id: Container ID or name
        """
        try:
            client = get_client()
            
            container = client.containers.get(container_id)
            container.start()
            
            return format_success_response({
                "container_id": container.id[:12],
                "name": container.name,
                "status": container.status
            }, "start_container")
            
        except NotFound:
            return format_error_response(f"Container {container_id} not found", "start_container")
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "start_container")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "start_container")
    
    @mcp.tool()
    def docker_remove_container(
        container_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """Remove a Docker container
        
        Args:
            container_id: Container ID or name
            force: Force remove running container
        """
        try:
            client = get_client()
            
            container = client.containers.get(container_id)
            container_name = container.name
            container.remove(force=force)
            
            return format_success_response({
                "container_id": container_id[:12] if len(container_id) > 12 else container_id,
                "name": container_name,
                "status": "removed",
                "force": force
            }, "remove_container")
            
        except NotFound:
            return format_error_response(f"Container {container_id} not found", "remove_container")
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "remove_container")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "remove_container")
    
    @mcp.tool()
    def docker_get_logs(
        container_id: str,
        tail: int = 100,
        follow: bool = False,
        timestamps: bool = True
    ) -> Dict[str, Any]:
        """Get logs from a Docker container
        
        Args:
            container_id: Container ID or name
            tail: Number of lines from end of logs (default: 100)
            follow: Follow log output (default: False)
            timestamps: Include timestamps (default: True)
        """
        try:
            client = get_client()
            
            container = client.containers.get(container_id)
            logs = container.logs(
                tail=tail,
                follow=follow,
                timestamps=timestamps
            )
            
            log_output = logs.decode('utf-8') if isinstance(logs, bytes) else str(logs)
            
            return format_success_response({
                "container_id": container.id[:12],
                "name": container.name,
                "logs": log_output,
                "lines": len(log_output.splitlines()),
                "tail": tail,
                "timestamps": timestamps
            }, "get_logs")
            
        except NotFound:
            return format_error_response(f"Container {container_id} not found", "get_logs")
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "get_logs")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "get_logs")
    
    @mcp.tool()
    def docker_list_images() -> Dict[str, Any]:
        """List Docker images"""
        try:
            client = get_client()
            
            images = client.images.list()
            
            image_list = []
            for image in images:
                image_info = {
                    "id": image.id[:12],
                    "tags": image.tags,
                    "created": image.attrs["Created"],
                    "size": image.attrs["Size"]
                }
                image_list.append(image_info)
            
            return format_success_response({
                "images": image_list,
                "total": len(image_list)
            }, "list_images")
            
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "list_images")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "list_images")
    
    @mcp.tool()
    def docker_pull_image(image: str) -> Dict[str, Any]:
        """Pull a Docker image
        
        Args:
            image: Image name to pull (e.g., 'nginx:latest')
        """
        try:
            client = get_client()
            
            validate_image_name(image)
            
            pulled_image = client.images.pull(image)
            
            return format_success_response({
                "image": image,
                "id": pulled_image.id[:12],
                "tags": pulled_image.tags,
                "size": pulled_image.attrs["Size"]
            }, "pull_image")
            
        except ValidationError as e:
            return format_error_response(str(e), "pull_image")
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "pull_image")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "pull_image")
    
    @mcp.tool()
    def docker_system_info() -> Dict[str, Any]:
        """Get Docker system information"""
        try:
            client = get_client()
            
            info = client.info()
            
            # Extract key information
            system_info = {
                "server_version": info.get("ServerVersion"),
                "containers": info.get("Containers"),
                "containers_running": info.get("ContainersRunning"),
                "containers_paused": info.get("ContainersPaused"),
                "containers_stopped": info.get("ContainersStopped"),
                "images": info.get("Images"),
                "driver": info.get("Driver"),
                "memory_total": info.get("MemTotal"),
                "ncpu": info.get("NCPU"),
                "os": info.get("OperatingSystem"),
                "architecture": info.get("Architecture")
            }
            
            return format_success_response(system_info, "system_info")
            
        except DockerException as e:
            return format_error_response(f"Docker error: {e}", "system_info")
        except Exception as e:
            return format_error_response(f"Unexpected error: {e}", "system_info")