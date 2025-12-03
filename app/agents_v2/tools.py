"""Tools that agents can use autonomously"""

import json
import httpx
from typing import Dict, Any, Optional, List
from langchain_core.tools import tool
from app.utils import run_ssh_command, save_artifact, append_trace_event


@tool
async def collect_system_logs(ssh_host: str, ssh_port: int, ssh_user: str, ssh_key_path: str, incident_id: str) -> str:
    """
    Collect system logs from the target VM via SSH.
    Returns raw log data from journalctl, syslog, and dmesg.
    
    Args:
        ssh_host: Target VM hostname or IP
        ssh_port: SSH port (usually 22)
        ssh_user: SSH username
        ssh_key_path: Path to SSH private key
        incident_id: Current incident ID for tracking
    """
    commands = [
        "sudo journalctl -n 500 --no-pager",
        "tail -n 200 /var/log/syslog 2>/dev/null || echo 'syslog not available'",
        "dmesg | tail -n 100 2>/dev/null || echo 'dmesg not available'"
    ]
    
    combined_logs = []
    
    for cmd in commands:
        try:
            stdout, stderr, exit_code = await run_ssh_command(
                host=ssh_host,
                port=ssh_port,
                username=ssh_user,
                key_path=ssh_key_path,
                command=cmd
            )
            
            if stdout:
                combined_logs.append(f"=== {cmd} ===\n{stdout}\n")
            if stderr and exit_code != 0:
                combined_logs.append(f"=== STDERR from {cmd} ===\n{stderr}\n")
                
        except Exception as e:
            combined_logs.append(f"=== ERROR executing {cmd}: {str(e)} ===\n")
    
    logs = "\n".join(combined_logs)
    save_artifact(incident_id, "raw_logs.txt", logs)
    
    return logs[:5000]  # Return truncated version for agent context


@tool
async def collect_system_metrics(ssh_host: str, ssh_port: int, ssh_user: str, ssh_key_path: str, 
                                 metrics_port: int, incident_id: str) -> Dict[str, Any]:
    """
    Collect system metrics from the target VM.
    First tries HTTP endpoint, falls back to SSH commands.
    
    Args:
        ssh_host: Target VM hostname or IP
        ssh_port: SSH port
        ssh_user: SSH username
        ssh_key_path: Path to SSH private key
        metrics_port: HTTP metrics port (e.g., 9090)
        incident_id: Current incident ID
    """
    metrics = {}
    
    # Try HTTP endpoint first
    try:
        metrics_url = f"http://{ssh_host}:{metrics_port}/metrics"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(metrics_url)
            if response.status_code == 200:
                metrics = response.json()
                save_artifact(incident_id, "metrics.json", json.dumps(metrics, indent=2))
                return metrics
    except Exception:
        pass
    
    # Fallback to SSH
    try:
        # CPU usage
        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'"
        cpu_out, _, _ = await run_ssh_command(ssh_host, ssh_port, ssh_user, ssh_key_path, cpu_cmd)
        metrics["cpu_usage_percent"] = float(cpu_out.strip()) if cpu_out.strip() else 0.0
        
        # Memory usage
        mem_cmd = "free | grep Mem | awk '{print ($3/$2) * 100.0}'"
        mem_out, _, _ = await run_ssh_command(ssh_host, ssh_port, ssh_user, ssh_key_path, mem_cmd)
        metrics["memory_usage_percent"] = float(mem_out.strip()) if mem_out.strip() else 0.0
        
        # Disk usage
        disk_cmd = "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
        disk_out, _, _ = await run_ssh_command(ssh_host, ssh_port, ssh_user, ssh_key_path, disk_cmd)
        metrics["disk_usage_percent"] = float(disk_out.strip()) if disk_out.strip() else 0.0
        
        # Load average
        load_cmd = "cat /proc/loadavg | awk '{print $1, $2, $3}'"
        load_out, _, _ = await run_ssh_command(ssh_host, ssh_port, ssh_user, ssh_key_path, load_cmd)
        loads = load_out.strip().split()
        metrics["load_1min"] = float(loads[0]) if len(loads) > 0 else 0.0
        metrics["load_5min"] = float(loads[1]) if len(loads) > 1 else 0.0
        metrics["load_15min"] = float(loads[2]) if len(loads) > 2 else 0.0
        
    except Exception as e:
        metrics["error"] = str(e)
    
    save_artifact(incident_id, "metrics.json", json.dumps(metrics, indent=2))
    return metrics


@tool
async def execute_ssh_command(ssh_host: str, ssh_port: int, ssh_user: str, 
                              ssh_key_path: str, command: str) -> Dict[str, Any]:
    """
    Execute a specific command on the target VM via SSH.
    Use this to investigate specific issues or apply fixes.
    
    Args:
        ssh_host: Target VM hostname or IP
        ssh_port: SSH port
        ssh_user: SSH username
        ssh_key_path: Path to SSH private key
        command: Command to execute
    """
    try:
        stdout, stderr, exit_code = await run_ssh_command(
            host=ssh_host,
            port=ssh_port,
            username=ssh_user,
            key_path=ssh_key_path,
            command=command
        )
        
        return {
            "success": exit_code == 0,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command
        }


@tool
def save_analysis_artifact(incident_id: str, filename: str, content: str) -> str:
    """
    Save analysis results or any artifact to the incident directory.
    
    Args:
        incident_id: Current incident ID
        filename: Name of file to save
        content: Content to write
    """
    save_artifact(incident_id, filename, content)
    return f"Saved {filename} to incident {incident_id}"


@tool
def log_agent_decision(incident_id: str, agent_name: str, decision: str, reasoning: str) -> str:
    """
    Log an agent's decision and reasoning for transparency.
    
    Args:
        incident_id: Current incident ID
        agent_name: Name of the agent making decision
        decision: What the agent decided to do
        reasoning: Why the agent made this decision
    """
    append_trace_event(
        incident_id,
        agent_name,
        "decision",
        f"Decision: {decision}",
        meta={"reasoning": reasoning}
    )
    return f"Logged decision for {agent_name}"


@tool
async def query_previous_incidents(incident_type: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Query historical incidents of similar type to learn from past resolutions.
    This enables agents to learn from experience.
    
    Args:
        incident_type: Type of incident (e.g., 'cpu_spike', 'memory_leak')
        limit: Maximum number of incidents to return
    """
    # TODO: Implement actual database query
    # For now, return empty list
    return []


# Export all tools
ALL_TOOLS = [
    collect_system_logs,
    collect_system_metrics,
    execute_ssh_command,
    save_analysis_artifact,
    log_agent_decision,
    query_previous_incidents
]
