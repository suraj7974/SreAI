"""Complete incident response agent - generates only 4 files"""

import json
import logging
from typing import Dict, Any
from datetime import datetime
from app.utils import (
    run_ssh_command, save_artifact, append_trace_event,
    generate_incident_id, ensure_incident_dir
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import os

logger = logging.getLogger(__name__)


class CompleteIncidentAgent:
    """
    Single agent that generates only 4 files:
    1. logs.txt - Raw logs from VM
    2. metrics.json - System metrics
    3. diagnostic_analysis.md - AI analysis
    4. fix_commands.sh - Fix script
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        self.llm = None
    
    def _get_llm(self):
        """Lazy load LLM"""
        if self.llm is None:
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not set in environment")
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.3,
                max_output_tokens=3000
            )
        return self.llm
    
    async def collect_logs(self, target_vm: Dict[str, Any]) -> str:
        """Collect logs from VM"""
        logger.info("Collecting VM logs...")
        
        commands = [
            ("System Journal", "sudo journalctl -n 500 --no-pager"),
            ("Syslog", "tail -n 200 /var/log/syslog 2>/dev/null || echo 'Not available'"),
            ("Error Logs", "sudo journalctl -p err -n 100 --no-pager"),
            ("Failed Services", "systemctl list-units --state=failed --no-pager"),
        ]
        
        log_sections = []
        for section_name, cmd in commands:
            try:
                stdout, stderr, _ = await run_ssh_command(
                    host=target_vm['host'],
                    port=target_vm.get('port', 22),
                    username=target_vm['user'],
                    key_path=target_vm['key_path'],
                    command=cmd,
                    timeout=30
                )
                log_sections.append(f"\n{'='*60}\n{section_name}\n{'='*60}\n{stdout}\n")
            except Exception as e:
                log_sections.append(f"\n{'='*60}\n{section_name}\n{'='*60}\nError: {str(e)}\n")
        
        return "\n".join(log_sections)
    
    async def collect_metrics(self, target_vm: Dict[str, Any]) -> Dict[str, Any]:
        """Collect system metrics"""
        logger.info("Collecting VM metrics...")
        
        metrics = {}
        
        metric_commands = {
            "cpu_usage": "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'",
            "memory_usage": "free | grep Mem | awk '{print ($3/$2) * 100.0}'",
            "disk_usage": "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'",
            "load_average": "uptime | awk -F'load average:' '{print $2}'",
            "active_connections": "netstat -an | grep ESTABLISHED | wc -l",
            "total_processes": "ps aux | wc -l",
        }
        
        for metric_name, cmd in metric_commands.items():
            try:
                stdout, _, _ = await run_ssh_command(
                    host=target_vm['host'],
                    port=target_vm.get('port', 22),
                    username=target_vm['user'],
                    key_path=target_vm['key_path'],
                    command=cmd,
                    timeout=10
                )
                value = stdout.strip()
                try:
                    metrics[metric_name] = float(value.split(',')[0]) if value else 0.0
                except:
                    metrics[metric_name] = value
            except Exception as e:
                metrics[metric_name] = f"Error: {str(e)}"
        
        metrics["timestamp"] = datetime.utcnow().isoformat()
        return metrics
    
    async def analyze_with_ai(
        self,
        scenario: str,
        logs: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AI analysis of logs and metrics"""
        logger.info("Analyzing with AI...")
        
        llm = self._get_llm()
        
        prompt = f"""You are an expert SRE analyzing a {scenario} incident.

LOGS (truncated):
{logs[:3000]}

METRICS:
{json.dumps(metrics, indent=2)}

Provide comprehensive analysis in JSON format:
{{
  "summary": "One-line issue summary",
  "root_cause": "Detailed root cause",
  "severity": "critical/high/medium/low",
  "affected_components": ["component1", "component2"],
  "timeline": "What happened and when",
  "impact": "System impact",
  "key_findings": ["finding1", "finding2"],
  "recommendations": ["rec1", "rec2"],
  "confidence": 0.85
}}

Be specific and technical."""
        
        try:
            messages = [
                SystemMessage(content="You are an expert SRE. Provide detailed technical analysis."),
                HumanMessage(content=prompt)
            ]
            response = await llm.ainvoke(messages)
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "summary": "Analysis failed",
                "root_cause": f"Error: {str(e)}",
                "severity": "unknown",
                "affected_components": [],
                "timeline": "Unknown",
                "impact": "Unknown",
                "key_findings": [],
                "recommendations": [],
                "confidence": 0.0
            }
    
    async def generate_fix_commands(
        self,
        scenario: str,
        analysis: Dict[str, Any]
    ) -> str:
        """Generate fix commands"""
        logger.info("Generating fix commands...")
        
        llm = self._get_llm()
        
        prompt = f"""You are an expert SRE creating fix commands for a {scenario} incident.

ANALYSIS:
{json.dumps(analysis, indent=2)}

Generate a bash script with:
1. Diagnostic commands
2. Fix commands with clear comments
3. Verification commands
4. Rollback commands if needed

Return ONLY the bash script, no explanations."""
        
        try:
            messages = [
                SystemMessage(content="You are an expert SRE. Generate safe bash commands."),
                HumanMessage(content=prompt)
            ]
            response = await llm.ainvoke(messages)
            
            content = response.content
            if "```bash" in content:
                content = content.split("```bash")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            script = f"""#!/bin/bash
# Incident Fix Script
# Generated: {datetime.utcnow().isoformat()}
# Scenario: {scenario}
# Severity: {analysis.get('severity', 'unknown')}
#
# WARNING: Review before execution!

set -e
set -u

{content.strip()}
"""
            return script
        except Exception as e:
            logger.error(f"Fix generation failed: {e}")
            return f"#!/bin/bash\n# Error generating fix: {str(e)}\n"
    
    def format_diagnostic_report(self, analysis: Dict[str, Any], scenario: str) -> str:
        """Format analysis as markdown"""
        
        report = f"""# Diagnostic Analysis Report

**Generated:** {datetime.utcnow().isoformat()}  
**Scenario:** {scenario}  
**Severity:** {analysis.get('severity', 'Unknown').upper()}  
**Confidence:** {analysis.get('confidence', 0.0) * 100:.1f}%

---

## Summary

{analysis.get('summary', 'No summary available')}

---

## Root Cause

{analysis.get('root_cause', 'Unknown')}

---

## Affected Components

{chr(10).join(f'- {comp}' for comp in analysis.get('affected_components', ['None identified']))}

---

## Timeline

{analysis.get('timeline', 'Timeline not available')}

---

## Impact

{analysis.get('impact', 'Impact unknown')}

---

## Key Findings

{chr(10).join(f'{i+1}. {finding}' for i, finding in enumerate(analysis.get('key_findings', [])))}

---

## Recommendations

{chr(10).join(f'{i+1}. {rec}' for i, rec in enumerate(analysis.get('recommendations', [])))}

---

## Next Steps

1. Review the fix commands in `fix_commands.sh`
2. Test fixes in non-production if possible
3. Create backup/snapshot before applying
4. Execute during maintenance window
5. Monitor after applying fixes
6. Document in runbook

---

*Generated by AI Chaos Handler*
"""
        return report
    
    async def handle_incident(
        self,
        scenario: str,
        target_vm: Dict[str, Any],
        storage_path: str = "./incidents"
    ) -> str:
        """Main incident handling workflow"""
        
        # Generate incident ID
        incident_id = generate_incident_id()
        incident_dir = ensure_incident_dir(incident_id, storage_path)
        
        logger.info(f"Starting incident response: {incident_id}")
        
        # Log start
        append_trace_event(
            incident_id, "CompleteIncidentAgent", "start",
            f"Starting incident response for: {scenario}",
            meta={"scenario": scenario},
            base_path=storage_path
        )
        
        try:
            # 1. Collect logs
            logs = await self.collect_logs(target_vm)
            save_artifact(incident_id, "logs.txt", logs, base_path=storage_path)
            logger.info(f"✓ Saved logs.txt ({len(logs)} bytes)")
            
            # 2. Collect metrics
            metrics = await self.collect_metrics(target_vm)
            save_artifact(
                incident_id, "metrics.json",
                json.dumps(metrics, indent=2),
                base_path=storage_path
            )
            logger.info(f"✓ Saved metrics.json")
            
            # 3. AI Analysis
            analysis = await self.analyze_with_ai(scenario, logs, metrics)
            diagnostic_report = self.format_diagnostic_report(analysis, scenario)
            save_artifact(
                incident_id, "diagnostic_analysis.md",
                diagnostic_report,
                base_path=storage_path
            )
            logger.info(f"✓ Saved diagnostic_analysis.md")
            
            # 4. Generate fix commands
            fix_script = await self.generate_fix_commands(scenario, analysis)
            save_artifact(
                incident_id, "fix_commands.sh",
                fix_script,
                base_path=storage_path
            )
            logger.info(f"✓ Saved fix_commands.sh")
            
            # Log completion
            append_trace_event(
                incident_id, "CompleteIncidentAgent", "complete",
                "Incident response completed - 4 files generated",
                meta={
                    "files": ["logs.txt", "metrics.json", "diagnostic_analysis.md", "fix_commands.sh"],
                    "severity": analysis.get("severity", "unknown")
                },
                base_path=storage_path
            )
            
            logger.info(f"✅ Incident {incident_id} completed successfully")
            return incident_id
            
        except Exception as e:
            logger.error(f"Incident response failed: {e}", exc_info=True)
            append_trace_event(
                incident_id, "CompleteIncidentAgent", "error",
                f"Failed: {str(e)}",
                meta={"error": str(e)},
                base_path=storage_path
            )
            raise
