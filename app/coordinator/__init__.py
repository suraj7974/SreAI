"""Coordinator - Orchestrates the incident response workflow"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from app.agents.log_agent import LogAgent
from app.agents.metrics_agent import MetricsAgent
from app.agents.fixer_agent import FixerAgent
from app.agents.tester_agent import TesterAgent
from app.agents.reporter_agent import ReporterAgent
from app.utils import (
    generate_incident_id,
    ensure_incident_dir,
    append_trace_event,
    run_ssh_command
)


class IncidentCoordinator:
    """Coordinates the multi-agent incident response workflow"""
    
    def __init__(self, storage_path: str = "./incidents"):
        self.storage_path = storage_path
        self.logger = logging.getLogger("IncidentCoordinator")
        self.active_incidents: Dict[str, Dict[str, Any]] = {}
    
    async def start_incident(
        self,
        scenario: str,
        target_vm: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> str:
        """Start a new incident response workflow"""
        
        # Generate incident ID
        incident_id = generate_incident_id()
        
        # Create incident directory
        incident_dir = ensure_incident_dir(incident_id, self.storage_path)
        
        # Initialize incident state
        self.active_incidents[incident_id] = {
            "id": incident_id,
            "scenario": scenario,
            "target_vm": target_vm,
            "options": options or {},
            "phase": "initializing",
            "status": "running"
        }
        
        # Log incident start
        append_trace_event(
            incident_id,
            "Coordinator",
            "diagnosis",
            f"Incident {incident_id} started with scenario: {scenario}",
            meta={"phase": "initializing", "scenario": scenario},
            base_path=self.storage_path
        )
        
        # Trigger chaos script if requested
        if options and options.get("trigger_chaos"):
            await self._trigger_chaos(incident_id, scenario, target_vm, options)
        
        # Start orchestration in background
        asyncio.create_task(self._orchestrate_incident(incident_id, target_vm, options or {}))
        
        return incident_id
    
    async def _trigger_chaos(
        self,
        incident_id: str,
        scenario: str,
        target_vm: Dict[str, Any],
        options: Dict[str, Any]
    ):
        """Trigger chaos script on target VM"""
        
        append_trace_event(
            incident_id,
            "Coordinator",
            "diagnosis",
            f"Triggering chaos scenario: {scenario}",
            meta={"phase": "chaos_trigger"},
            base_path=self.storage_path
        )
        
        # Map scenario to script
        script_map = {
            "cpu_spike": "cpu_spike.sh",
            "memory_leak": "memory_leak.sh",
            "disk_fill": "disk_fill.sh",
            "net_latency": "net_latency.sh",
            "service_kill": "service_kill.sh",
            "db_conn_exhaust": "db_conn_exhaust.sh"
        }
        
        script_name = script_map.get(scenario)
        if not script_name:
            self.logger.warning(f"Unknown scenario: {scenario}")
            return
        
        # Build chaos command
        duration = options.get("duration", 60)
        script_path = f"/opt/chaos-scripts/{script_name}"
        
        if scenario == "cpu_spike":
            chaos_cmd = f"sudo {script_path} start {duration} 2"
        elif scenario == "memory_leak":
            target_mb = options.get("target_mb", 1024)
            chaos_cmd = f"sudo {script_path} start {target_mb} {duration}"
        elif scenario == "disk_fill":
            size_mb = options.get("size_mb", 5000)
            chaos_cmd = f"sudo {script_path} start {size_mb}"
        else:
            chaos_cmd = f"sudo {script_path} start {duration}"
        
        try:
            stdout, stderr, exit_code = await run_ssh_command(
                host=target_vm.get("host"),
                port=target_vm.get("port", 22),
                username=target_vm.get("user"),
                key_path=target_vm.get("key_path"),
                command=chaos_cmd
            )
            
            if exit_code == 0:
                append_trace_event(
                    incident_id,
                    "Coordinator",
                    "diagnosis",
                    f"Chaos script {script_name} triggered successfully",
                    base_path=self.storage_path
                )
            else:
                append_trace_event(
                    incident_id,
                    "Coordinator",
                    "diagnosis",
                    f"Chaos script failed: {stderr}",
                    base_path=self.storage_path
                )
        except Exception as e:
            self.logger.error(f"Failed to trigger chaos: {e}")
            append_trace_event(
                incident_id,
                "Coordinator",
                "diagnosis",
                f"Chaos trigger error: {str(e)}",
                base_path=self.storage_path
            )
    
    async def _orchestrate_incident(
        self,
        incident_id: str,
        target_vm: Dict[str, Any],
        options: Dict[str, Any]
    ):
        """Orchestrate the complete incident response workflow"""
        
        try:
            # Wait for chaos to take effect if triggered
            if options.get("trigger_chaos"):
                await asyncio.sleep(10)
            
            # Phase 1: Log Collection
            self.active_incidents[incident_id]["phase"] = "log_collection"
            log_agent = LogAgent(incident_id, {
                "ssh_host": target_vm.get("host"),
                "ssh_port": target_vm.get("port", 22),
                "ssh_user": target_vm.get("user"),
                "ssh_key_path": target_vm.get("key_path"),
            })
            log_result = await log_agent.execute()
            
            # Phase 2: Metrics Collection
            self.active_incidents[incident_id]["phase"] = "metrics_collection"
            metrics_agent = MetricsAgent(incident_id, {
                "ssh_host": target_vm.get("host"),
                "ssh_port": target_vm.get("port", 22),
                "ssh_user": target_vm.get("user"),
                "ssh_key_path": target_vm.get("key_path"),
                "metrics_port": options.get("metrics_port", 9090),
            })
            metrics_result = await metrics_agent.execute()
            
            # Phase 3: Fix Generation
            self.active_incidents[incident_id]["phase"] = "fix_generation"
            fixer_agent = FixerAgent(incident_id, {
                "log_data": log_result,
                "metrics_data": metrics_result,
            })
            fix_result = await fixer_agent.execute()
            
            # Phase 4: Risk Testing
            self.active_incidents[incident_id]["phase"] = "risk_testing"
            tester_agent = TesterAgent(incident_id, {
                "fix_data": fix_result,
            })
            test_result = await tester_agent.execute()
            
            # Phase 5: Report Generation
            self.active_incidents[incident_id]["phase"] = "reporting"
            reporter_agent = ReporterAgent(incident_id, {
                "storage_path": self.storage_path,
                "slack_webhook_url": options.get("slack_webhook_url"),
            })
            report_result = await reporter_agent.execute()
            
            # Mark as complete
            self.active_incidents[incident_id]["phase"] = "complete"
            self.active_incidents[incident_id]["status"] = "complete"
            
            append_trace_event(
                incident_id,
                "Coordinator",
                "report",
                "Incident response workflow completed successfully",
                meta={"phase": "complete"},
                base_path=self.storage_path
            )
            
        except Exception as e:
            self.logger.error(f"Error in incident orchestration: {e}", exc_info=True)
            self.active_incidents[incident_id]["status"] = "error"
            self.active_incidents[incident_id]["error"] = str(e)
            
            append_trace_event(
                incident_id,
                "Coordinator",
                "diagnosis",
                f"Incident workflow failed: {str(e)}",
                meta={"phase": "error"},
                base_path=self.storage_path
            )
    
    def get_incident_status(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an incident"""
        return self.active_incidents.get(incident_id)
    
    async def stop_incident(self, incident_id: str):
        """Stop an active incident (stops chaos scripts)"""
        
        if incident_id not in self.active_incidents:
            return False
        
        incident = self.active_incidents[incident_id]
        target_vm = incident.get("target_vm", {})
        scenario = incident.get("scenario")
        
        # Map scenario to script
        script_map = {
            "cpu_spike": "cpu_spike.sh",
            "memory_leak": "memory_leak.sh",
            "disk_fill": "disk_fill.sh",
            "net_latency": "net_latency.sh",
            "service_kill": "service_kill.sh",
            "db_conn_exhaust": "db_conn_exhaust.sh"
        }
        
        script_name = script_map.get(scenario)
        if script_name:
            script_path = f"/opt/chaos-scripts/{script_name}"
            stop_cmd = f"sudo {script_path} stop"
            
            try:
                await run_ssh_command(
                    host=target_vm.get("host"),
                    port=target_vm.get("port", 22),
                    username=target_vm.get("user"),
                    key_path=target_vm.get("key_path"),
                    command=stop_cmd
                )
                
                append_trace_event(
                    incident_id,
                    "Coordinator",
                    "diagnosis",
                    f"Chaos script {script_name} stopped",
                    base_path=self.storage_path
                )
            except Exception as e:
                self.logger.error(f"Failed to stop chaos: {e}")
        
        return True
