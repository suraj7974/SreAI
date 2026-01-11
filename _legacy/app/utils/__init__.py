"""Utility functions for AI Chaos Handler"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List
import asyncio


def setup_logging():
    """Setup structured JSON logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def generate_incident_id() -> str:
    """Generate a unique incident ID"""
    now = datetime.utcnow()
    return f"inc-{now.strftime('%Y%m%d-%H%M%S')}"


def ensure_incident_dir(incident_id: str, base_path: str = "./incidents") -> Path:
    """Create and return incident directory path"""
    incident_path = Path(base_path) / incident_id
    incident_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (incident_path / "artifacts").mkdir(exist_ok=True)
    
    # Initialize trace file
    trace_file = incident_path / "trace.json"
    if not trace_file.exists():
        trace_file.write_text("[]")
    
    return incident_path


def append_trace_event(
    incident_id: str,
    agent: str,
    event_type: str,
    content: str,
    evidence: List[str] = None,
    confidence: float = None,
    meta: Dict[str, Any] = None,
    base_path: str = "./incidents"
):
    """Append an event to the trace.json file"""
    trace_file = Path(base_path) / incident_id / "trace.json"
    
    # Read existing trace
    if trace_file.exists():
        trace = json.loads(trace_file.read_text())
    else:
        trace = []
    
    # Create event
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent,
        "type": event_type,
        "content": content
    }
    
    if evidence:
        event["evidence"] = evidence
    if confidence is not None:
        event["confidence"] = confidence
    if meta:
        event["meta"] = meta
    
    # Append and write
    trace.append(event)
    trace_file.write_text(json.dumps(trace, indent=2))
    
    return event


def read_trace(incident_id: str, base_path: str = "./incidents") -> List[Dict[str, Any]]:
    """Read the trace.json file"""
    trace_file = Path(base_path) / incident_id / "trace.json"
    
    if not trace_file.exists():
        return []
    
    return json.loads(trace_file.read_text())


async def run_ssh_command(host: str, port: int, username: str, key_path: str, command: str, timeout: int = 10) -> tuple:
    """Execute a command via SSH and return (stdout, stderr, exit_code)"""
    import paramiko
    import os
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Expand ~ in path
        key_path = os.path.expanduser(key_path)
        
        # Try to load the key - support both RSA and Ed25519
        key = None
        try:
            key = paramiko.RSAKey.from_private_key_file(key_path)
        except paramiko.ssh_exception.SSHException:
            try:
                key = paramiko.Ed25519Key.from_private_key_file(key_path)
            except paramiko.ssh_exception.SSHException:
                try:
                    key = paramiko.ECDSAKey.from_private_key_file(key_path)
                except:
                    # Last resort - try DSS
                    key = paramiko.DSSKey.from_private_key_file(key_path)
        
        client.connect(hostname=host, port=port, username=username, pkey=key, timeout=timeout)
        
        stdin, stdout, stderr = client.exec_command(command)
        
        stdout_text = stdout.read().decode('utf-8')
        stderr_text = stderr.read().decode('utf-8')
        exit_code = stdout.channel.recv_exit_status()
        
        return stdout_text, stderr_text, exit_code
    finally:
        client.close()


def save_artifact(incident_id: str, filename: str, content: str, base_path: str = "./incidents"):
    """Save an artifact file"""
    artifact_path = Path(base_path) / incident_id / filename
    artifact_path.write_text(content)
    return str(artifact_path)
