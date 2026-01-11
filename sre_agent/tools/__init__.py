"""
SRE Agent - Shared Tools

These tools are available to all agents for interacting with:
- Prometheus (metrics)
- Target VMs (SSH)
- Incident storage
- Notifications
"""

import httpx
import asyncio
import asyncssh
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from langchain_core.tools import tool
from sre_agent.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Prometheus Tools
# =============================================================================


class PrometheusClient:
    """Client for querying Prometheus"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.prometheus_url

    async def query(self, promql: str) -> Dict[str, Any]:
        """Execute an instant query"""
        async with httpx.AsyncClient(
            timeout=settings.prometheus_query_timeout
        ) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/query", params={"query": promql}
            )
            response.raise_for_status()
            return response.json()

    async def query_range(
        self,
        promql: str,
        start: datetime = None,
        end: datetime = None,
        step: str = "15s",
    ) -> Dict[str, Any]:
        """Execute a range query"""
        end = end or datetime.utcnow()
        start = start or (end - timedelta(minutes=15))

        async with httpx.AsyncClient(
            timeout=settings.prometheus_query_timeout
        ) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/query_range",
                params={
                    "query": promql,
                    "start": start.isoformat() + "Z",
                    "end": end.isoformat() + "Z",
                    "step": step,
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_alerts(self) -> Dict[str, Any]:
        """Get active alerts from Prometheus"""
        async with httpx.AsyncClient(
            timeout=settings.prometheus_query_timeout
        ) as client:
            response = await client.get(f"{self.base_url}/api/v1/alerts")
            response.raise_for_status()
            return response.json()

    async def get_targets(self) -> Dict[str, Any]:
        """Get scrape targets and their health"""
        async with httpx.AsyncClient(
            timeout=settings.prometheus_query_timeout
        ) as client:
            response = await client.get(f"{self.base_url}/api/v1/targets")
            response.raise_for_status()
            return response.json()


# Global Prometheus client instance
prometheus = PrometheusClient()


@tool
async def query_prometheus(promql: str) -> str:
    """
    Execute a PromQL query against Prometheus.

    Use this to get current metric values. Returns JSON with query results.

    Common queries:
    - CPU: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
    - Memory: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
    - Disk: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
    - Load: node_load1

    Args:
        promql: The PromQL query to execute
    """
    try:
        result = await prometheus.query(promql)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "query": promql})


@tool
async def query_prometheus_range(promql: str, minutes_back: int = 15) -> str:
    """
    Execute a PromQL range query to get historical data.

    Use this to analyze trends over time.

    Args:
        promql: The PromQL query to execute
        minutes_back: How many minutes of history to retrieve (default: 15)
    """
    try:
        end = datetime.utcnow()
        start = end - timedelta(minutes=minutes_back)
        result = await prometheus.query_range(promql, start, end)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "query": promql})


@tool
async def get_active_alerts() -> str:
    """
    Get all currently active alerts from Prometheus.

    Returns a list of firing alerts with their labels and annotations.
    """
    try:
        result = await prometheus.get_alerts()
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
async def get_system_metrics(instance: str) -> str:
    """
    Get comprehensive system metrics for a specific instance.

    Queries CPU, memory, disk, load, and network metrics.

    Args:
        instance: The instance to query (e.g., "192.168.1.10:9100")
    """
    queries = {
        "cpu_usage_percent": f'100 - (avg by(instance) (irate(node_cpu_seconds_total{{instance="{instance}",mode="idle"}}[5m])) * 100)',
        "memory_usage_percent": f'(1 - (node_memory_MemAvailable_bytes{{instance="{instance}"}} / node_memory_MemTotal_bytes{{instance="{instance}"}})) * 100',
        "disk_usage_percent": f'(1 - (node_filesystem_avail_bytes{{instance="{instance}",mountpoint="/"}} / node_filesystem_size_bytes{{instance="{instance}",mountpoint="/"}})) * 100',
        "load_1m": f'node_load1{{instance="{instance}"}}',
        "load_5m": f'node_load5{{instance="{instance}"}}',
        "load_15m": f'node_load15{{instance="{instance}"}}',
        "network_receive_bytes": f'rate(node_network_receive_bytes_total{{instance="{instance}",device!~"lo|docker.*"}}[5m])',
        "network_transmit_bytes": f'rate(node_network_transmit_bytes_total{{instance="{instance}",device!~"lo|docker.*"}}[5m])',
    }

    results = {}
    for name, query in queries.items():
        try:
            result = await prometheus.query(query)
            if result.get("data", {}).get("result"):
                value = result["data"]["result"][0].get("value", [None, None])[1]
                results[name] = float(value) if value else None
            else:
                results[name] = None
        except Exception as e:
            results[name] = f"Error: {str(e)}"

    results["instance"] = instance
    results["timestamp"] = datetime.utcnow().isoformat()

    return json.dumps(results, indent=2)


# =============================================================================
# SSH Tools
# =============================================================================


async def run_ssh_command(
    host: str,
    command: str,
    username: str = None,
    key_path: str = None,
    port: int = None,
    timeout: int = None,
) -> Tuple[str, str, int]:
    """
    Execute a command on a remote host via SSH.

    Returns: (stdout, stderr, exit_code)
    """
    username = username or settings.ssh_user
    key_path = key_path or settings.ssh_key_path
    port = port or settings.ssh_port
    timeout = timeout or settings.ssh_timeout

    try:
        async with (
            asyncssh.connect(
                host,
                port=port,
                username=username,
                client_keys=[key_path] if key_path else None,
                known_hosts=None,  # Disable host key checking (configure properly in production)
            ) as conn
        ):
            result = await asyncio.wait_for(conn.run(command), timeout=timeout)
            return result.stdout or "", result.stderr or "", result.exit_status or 0
    except Exception as e:
        logger.error(f"SSH command failed on {host}: {e}")
        return "", str(e), 1


@tool
async def execute_ssh_command(host: str, command: str) -> str:
    """
    Execute a command on a remote host via SSH.

    Use this for diagnostic commands or remediation actions.

    Args:
        host: Target hostname or IP address
        command: Command to execute
    """
    stdout, stderr, exit_code = await run_ssh_command(host, command)
    return json.dumps(
        {
            "host": host,
            "command": command,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": exit_code,
            "success": exit_code == 0,
        },
        indent=2,
    )


@tool
async def get_system_logs(
    host: str, lines: int = 100, filter_pattern: str = None
) -> str:
    """
    Retrieve system logs from a remote host.

    Args:
        host: Target hostname or IP address
        lines: Number of recent log lines to retrieve
        filter_pattern: Optional grep pattern to filter logs
    """
    if filter_pattern:
        cmd = f"sudo journalctl -n {lines} --no-pager | grep -iE '{filter_pattern}'"
    else:
        cmd = f"sudo journalctl -n {lines} --no-pager"

    stdout, stderr, exit_code = await run_ssh_command(host, cmd)
    return json.dumps(
        {
            "host": host,
            "logs": stdout,
            "error": stderr if exit_code != 0 else None,
            "lines_requested": lines,
            "filter": filter_pattern,
        },
        indent=2,
    )


@tool
async def get_top_processes(host: str, sort_by: str = "cpu", count: int = 10) -> str:
    """
    Get top processes by CPU or memory usage.

    Args:
        host: Target hostname or IP address
        sort_by: Sort by "cpu" or "memory"
        count: Number of top processes to return
    """
    if sort_by == "memory":
        cmd = f"ps aux --sort=-%mem | head -n {count + 1}"
    else:
        cmd = f"ps aux --sort=-%cpu | head -n {count + 1}"

    stdout, stderr, exit_code = await run_ssh_command(host, cmd)
    return json.dumps(
        {
            "host": host,
            "sort_by": sort_by,
            "processes": stdout,
            "error": stderr if exit_code != 0 else None,
        },
        indent=2,
    )


@tool
async def check_service_status(host: str, service_name: str) -> str:
    """
    Check the status of a systemd service.

    Args:
        host: Target hostname or IP address
        service_name: Name of the service (e.g., "nginx", "docker")
    """
    cmd = f"systemctl status {service_name} --no-pager"
    stdout, stderr, exit_code = await run_ssh_command(host, cmd)

    # Also get if service is enabled
    enabled_cmd = f"systemctl is-enabled {service_name}"
    enabled_out, _, _ = await run_ssh_command(host, enabled_cmd)

    return json.dumps(
        {
            "host": host,
            "service": service_name,
            "status_output": stdout,
            "is_enabled": enabled_out.strip(),
            "is_active": "active (running)" in stdout.lower(),
            "error": stderr if exit_code != 0 else None,
        },
        indent=2,
    )


@tool
async def restart_service(host: str, service_name: str) -> str:
    """
    Restart a systemd service.

    WARNING: This action modifies system state. Use with caution.

    Args:
        host: Target hostname or IP address
        service_name: Name of the service to restart
    """
    cmd = f"sudo systemctl restart {service_name}"
    stdout, stderr, exit_code = await run_ssh_command(host, cmd)

    # Verify service started
    verify_cmd = f"systemctl is-active {service_name}"
    verify_out, _, _ = await run_ssh_command(host, verify_cmd)

    return json.dumps(
        {
            "host": host,
            "service": service_name,
            "action": "restart",
            "success": exit_code == 0,
            "is_now_active": verify_out.strip() == "active",
            "error": stderr if exit_code != 0 else None,
        },
        indent=2,
    )


@tool
async def kill_process(host: str, pid: int, signal: str = "TERM") -> str:
    """
    Send a signal to a process.

    WARNING: This action modifies system state. Use with caution.

    Args:
        host: Target hostname or IP address
        pid: Process ID to signal
        signal: Signal to send (TERM, KILL, HUP, etc.)
    """
    cmd = f"sudo kill -{signal} {pid}"
    stdout, stderr, exit_code = await run_ssh_command(host, cmd)

    return json.dumps(
        {
            "host": host,
            "pid": pid,
            "signal": signal,
            "success": exit_code == 0,
            "error": stderr if exit_code != 0 else None,
        },
        indent=2,
    )


# =============================================================================
# Incident Storage Tools
# =============================================================================


@tool
def save_incident_artifact(incident_id: str, filename: str, content: str) -> str:
    """
    Save an artifact (log, analysis, etc.) to the incident directory.

    Args:
        incident_id: The incident ID
        filename: Name of the file to save
        content: Content to write
    """
    import os

    incident_dir = os.path.join(settings.incident_storage_path, incident_id)
    os.makedirs(incident_dir, exist_ok=True)

    filepath = os.path.join(incident_dir, filename)
    with open(filepath, "w") as f:
        f.write(content)

    return json.dumps(
        {
            "incident_id": incident_id,
            "filename": filename,
            "path": filepath,
            "size_bytes": len(content),
        }
    )


@tool
def log_agent_reasoning(
    incident_id: str,
    agent_name: str,
    thought: str,
    action: str = None,
    observation: str = None,
) -> str:
    """
    Log agent reasoning for transparency and debugging.

    Args:
        incident_id: The incident ID
        agent_name: Name of the agent logging
        thought: The agent's reasoning
        action: What action the agent decided to take
        observation: What the agent observed from the action
    """
    import os

    incident_dir = os.path.join(settings.incident_storage_path, incident_id)
    os.makedirs(incident_dir, exist_ok=True)

    trace_file = os.path.join(incident_dir, "agent_trace.jsonl")

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "thought": thought,
        "action": action,
        "observation": observation,
    }

    with open(trace_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return json.dumps({"logged": True, "entry": entry})


# =============================================================================
# Notification Tools
# =============================================================================


@tool
async def send_slack_notification(
    message: str, channel: str = None, severity: str = "info"
) -> str:
    """
    Send a notification to Slack.

    Args:
        message: The message to send
        channel: Slack channel (uses default if not specified)
        severity: Message severity (info, warning, critical)
    """
    if not settings.slack_webhook_url:
        return json.dumps({"sent": False, "reason": "Slack webhook not configured"})

    color_map = {"info": "#36a64f", "warning": "#ffcc00", "critical": "#ff0000"}

    payload = {
        "attachments": [
            {
                "color": color_map.get(severity, "#36a64f"),
                "title": f"SRE Agent Alert ({severity.upper()})",
                "text": message,
                "footer": "SRE Agent",
                "ts": int(datetime.utcnow().timestamp()),
            }
        ]
    }

    if channel:
        payload["channel"] = channel

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.slack_webhook_url, json=payload)
            return json.dumps(
                {
                    "sent": response.status_code == 200,
                    "status_code": response.status_code,
                }
            )
    except Exception as e:
        return json.dumps({"sent": False, "error": str(e)})


# =============================================================================
# Export all tools
# =============================================================================

MONITORING_TOOLS = [
    query_prometheus,
    query_prometheus_range,
    get_active_alerts,
    get_system_metrics,
]

DIAGNOSTIC_TOOLS = [
    query_prometheus,
    query_prometheus_range,
    get_system_metrics,
    execute_ssh_command,
    get_system_logs,
    get_top_processes,
    check_service_status,
]

REMEDIATION_TOOLS = [
    execute_ssh_command,
    restart_service,
    kill_process,
    check_service_status,
]

ALL_TOOLS = [
    query_prometheus,
    query_prometheus_range,
    get_active_alerts,
    get_system_metrics,
    execute_ssh_command,
    get_system_logs,
    get_top_processes,
    check_service_status,
    restart_service,
    kill_process,
    save_incident_artifact,
    log_agent_reasoning,
    send_slack_notification,
]
