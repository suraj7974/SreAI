"""MetricsAgent - AI-Powered system metrics collection and analysis"""

import json
import httpx
from typing import Dict, Any
from app.agents import BaseAgent
from app.utils import append_trace_event, save_artifact, run_ssh_command
from app.utils.llm_client import get_llm_client


class MetricsAgent(BaseAgent):
    """Agent responsible for collecting and analyzing system metrics"""
    
    async def run(self) -> Dict[str, Any]:
        """Collect metrics from VM and analyze with AI"""
        
        append_trace_event(
            self.incident_id,
            "MetricsAgent",
            "diagnosis",
            "Starting AI-powered metrics analysis",
            meta={"phase": "collection", "ai_enabled": True}
        )
        
        # Collect metrics
        metrics = await self._collect_metrics()
        
        # Save metrics
        save_artifact(self.incident_id, "metrics.json", json.dumps(metrics, indent=2))
        
        # AI Analysis
        llm = get_llm_client()
        analysis = await llm.analyze_metrics(metrics, {
            "incident_id": self.incident_id,
            "scenario": self.config.get("scenario", "unknown")
        })
        
        # Save AI analysis
        save_artifact(self.incident_id, "metrics_analysis.json", json.dumps(analysis, indent=2))
        
        # Append analysis results
        append_trace_event(
            self.incident_id,
            "MetricsAgent",
            "evidence",
            f"AI Analysis: {analysis.get('summary', 'No summary')}",
            evidence=["metrics.json", "metrics_analysis.json"],
            confidence=analysis.get("confidence", 0.9),
            meta={
                "anomalies_count": len(analysis.get("anomalies", [])),
                "metrics_collected": len(metrics)
            }
        )
        
        return {
            "metrics": metrics,
            "analysis": analysis,
            "metrics_path": f"incidents/{self.incident_id}/metrics.json",
            "analysis_path": f"incidents/{self.incident_id}/metrics_analysis.json"
        }
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect system metrics from VM"""
        
        metrics = {}
        
        # Try HTTP endpoint first
        try:
            metrics_url = f"http://{self.config.get('ssh_host')}:{self.config.get('metrics_port', 9090)}/metrics"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(metrics_url)
                if response.status_code == 200:
                    metrics = response.json()
                    return metrics
        except Exception as e:
            self.logger.info(f"HTTP metrics endpoint not available, falling back to SSH: {e}")
        
        # Fallback to SSH-based collection
        try:
            metrics = await self._collect_via_ssh()
        except Exception as e:
            self.logger.error(f"Failed to collect metrics via SSH: {e}")
            metrics = {"error": str(e)}
        
        return metrics
    
    async def _collect_via_ssh(self) -> Dict[str, Any]:
        """Collect metrics via SSH commands"""
        
        metrics = {}
        
        # CPU usage
        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'"
        cpu_out, _, _ = await run_ssh_command(
            self.config.get("ssh_host"),
            self.config.get("ssh_port", 22),
            self.config.get("ssh_user"),
            self.config.get("ssh_key_path"),
            cpu_cmd
        )
        try:
            metrics["cpu_usage_percent"] = float(cpu_out.strip())
        except:
            metrics["cpu_usage_percent"] = 0.0
        
        # Memory usage
        mem_cmd = "free | grep Mem | awk '{print ($3/$2) * 100.0}'"
        mem_out, _, _ = await run_ssh_command(
            self.config.get("ssh_host"),
            self.config.get("ssh_port", 22),
            self.config.get("ssh_user"),
            self.config.get("ssh_key_path"),
            mem_cmd
        )
        try:
            metrics["memory_usage_percent"] = float(mem_out.strip())
        except:
            metrics["memory_usage_percent"] = 0.0
        
        # Disk usage
        disk_cmd = "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
        disk_out, _, _ = await run_ssh_command(
            self.config.get("ssh_host"),
            self.config.get("ssh_port", 22),
            self.config.get("ssh_user"),
            self.config.get("ssh_key_path"),
            disk_cmd
        )
        try:
            metrics["disk_usage_percent"] = float(disk_out.strip())
        except:
            metrics["disk_usage_percent"] = 0.0
        
        # Load average
        load_cmd = "cat /proc/loadavg | awk '{print $1, $2, $3}'"
        load_out, _, _ = await run_ssh_command(
            self.config.get("ssh_host"),
            self.config.get("ssh_port", 22),
            self.config.get("ssh_user"),
            self.config.get("ssh_key_path"),
            load_cmd
        )
        try:
            loads = load_out.strip().split()
            metrics["load_1min"] = float(loads[0])
            metrics["load_5min"] = float(loads[1])
            metrics["load_15min"] = float(loads[2])
        except:
            metrics["load_1min"] = 0.0
            metrics["load_5min"] = 0.0
            metrics["load_15min"] = 0.0
        
        return metrics
    

