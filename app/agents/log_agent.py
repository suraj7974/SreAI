"""LogAgent - AI-Powered log collection and analysis"""

import json
from typing import Dict, Any
from app.agents import BaseAgent
from app.utils import append_trace_event, save_artifact, run_ssh_command
from app.utils.llm_client import get_llm_client


class LogAgent(BaseAgent):
    """Agent responsible for collecting and analyzing logs from the VM"""
    
    async def run(self) -> Dict[str, Any]:
        """Collect logs from VM and analyze with AI"""
        
        append_trace_event(
            self.incident_id,
            "LogAgent",
            "diagnosis",
            "Starting AI-powered log analysis",
            meta={"phase": "collection", "ai_enabled": True}
        )
        
        # Collect logs via SSH
        logs = await self._collect_logs()
        
        # Save raw logs
        save_artifact(self.incident_id, "raw_logs.txt", logs)
        
        # AI Analysis
        llm = get_llm_client()
        analysis = await llm.analyze_logs(logs, {
            "incident_id": self.incident_id,
            "scenario": self.config.get("scenario", "unknown")
        })
        
        # Save AI analysis
        save_artifact(self.incident_id, "log_analysis.json", json.dumps(analysis, indent=2))
        
        # Append AI analysis to trace
        append_trace_event(
            self.incident_id,
            "LogAgent",
            "evidence",
            f"AI Analysis: {analysis.get('summary', 'No summary')}",
            evidence=["raw_logs.txt", "log_analysis.json"],
            confidence=analysis.get("confidence", 0.8),
            meta={
                "log_lines": len(logs.splitlines()),
                "errors_found": len(analysis.get("errors_found", [])),
                "severity": analysis.get("severity", "unknown"),
                "root_cause": analysis.get("root_cause", "")[:100]
            }
        )
        
        return {
            "logs_collected": len(logs.splitlines()),
            "analysis": analysis,
            "raw_logs_path": f"incidents/{self.incident_id}/raw_logs.txt",
            "analysis_path": f"incidents/{self.incident_id}/log_analysis.json"
        }
    
    async def _collect_logs(self) -> str:
        """Collect logs from the VM via SSH"""
        
        # Build log collection command
        commands = [
            "sudo journalctl -n 500 --no-pager",
            "tail -n 200 /var/log/syslog 2>/dev/null || echo 'syslog not available'",
            "dmesg | tail -n 100 2>/dev/null || echo 'dmesg not available'"
        ]
        
        combined_logs = []
        
        for cmd in commands:
            try:
                stdout, stderr, exit_code = await run_ssh_command(
                    host=self.config.get("ssh_host"),
                    port=self.config.get("ssh_port", 22),
                    username=self.config.get("ssh_user"),
                    key_path=self.config.get("ssh_key_path"),
                    command=cmd
                )
                
                if stdout:
                    combined_logs.append(f"=== {cmd} ===\n{stdout}\n")
                if stderr and exit_code != 0:
                    combined_logs.append(f"=== STDERR from {cmd} ===\n{stderr}\n")
                    
            except Exception as e:
                self.logger.warning(f"Failed to execute {cmd}: {e}")
                combined_logs.append(f"=== ERROR executing {cmd}: {str(e)} ===\n")
        
        return "\n".join(combined_logs)
    

