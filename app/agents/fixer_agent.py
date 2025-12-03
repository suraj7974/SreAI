"""FixerAgent - AI-Powered remediation plan generation"""

import json
from typing import Dict, Any
from app.agents import BaseAgent
from app.utils import append_trace_event, save_artifact
from app.utils.llm_client import get_llm_client


class FixerAgent(BaseAgent):
    """Agent responsible for generating intelligent fix suggestions using AI"""
    
    async def run(self) -> Dict[str, Any]:
        """Generate AI-powered fix suggestions"""
        
        append_trace_event(
            self.incident_id,
            "FixerAgent",
            "diagnosis",
            "Generating AI-powered remediation plan",
            meta={"phase": "remediation", "ai_enabled": True}
        )
        
        # Get evidence from previous agents
        log_data = self.config.get("log_data", {})
        metrics_data = self.config.get("metrics_data", {})
        
        # AI-powered fix generation
        llm = get_llm_client()
        fixes = await llm.generate_fixes(
            log_data.get("analysis", {}),
            metrics_data.get("analysis", {}),
            {
                "incident_id": self.incident_id,
                "scenario": self.config.get("scenario", "unknown")
            }
        )
        
        # Save fix suggestions
        save_artifact(
            self.incident_id,
            "fix_suggestions.json",
            json.dumps(fixes, indent=2)
        )
        
        # Generate shell script from fixes
        fix_script = self._generate_fix_script(fixes)
        save_artifact(self.incident_id, "fix.sh", fix_script)
        
        confidence = fixes.get("confidence", 0.8)
        fix_count = len(fixes.get("fixes", []))
        
        append_trace_event(
            self.incident_id,
            "FixerAgent",
            "suggestion",
            f"AI generated {fix_count} remediation actions. Root cause: {fixes.get('root_cause_summary', 'Unknown')[:100]}",
            evidence=["fix_suggestions.json", "fix.sh"],
            confidence=confidence,
            meta={"fix_count": fix_count}
        )
        
        return {
            "fixes": fixes,
            "fix_script_path": f"incidents/{self.incident_id}/fix.sh",
            "confidence": confidence
        }
    
    def _generate_fix_script(self, fixes: Dict[str, Any]) -> str:
        """Generate executable shell script from AI fixes"""
        
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated fix script from AI Chaos Handler",
            f"# Incident ID: {self.incident_id}",
            f"# Root Cause: {fixes.get('root_cause_summary', 'Unknown')}",
            "",
            "set -e  # Exit on error",
            "",
            "echo '=== AI Chaos Handler Remediation Script ==='",
            f"echo 'Incident: {self.incident_id}'",
            "echo ''",
            ""
        ]
        
        for i, fix in enumerate(fixes.get("fixes", []), 1):
            script_lines.extend([
                f"# Fix {i}: {fix.get('title', 'Unknown')}",
                f"# Priority: {fix.get('priority', 'N/A')}",
                f"# Risk: {fix.get('risk', 'unknown')}",
                f"# Timeline: {fix.get('timeline', 'unknown')}",
                f"echo 'Executing Fix {i}: {fix.get('title', 'Unknown')}'",
                ""
            ])
            
            for cmd in fix.get("commands", []):
                script_lines.append(f"{cmd}")
            
            script_lines.extend([
                "",
                f"echo 'Fix {i} completed'",
                "echo ''",
                ""
            ])
        
        script_lines.extend([
            "echo '=== All fixes completed ==='",
            "echo 'Verify system health after applying fixes'"
        ])
        
        return "\n".join(script_lines)
