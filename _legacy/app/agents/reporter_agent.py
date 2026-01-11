"""ReporterAgent - AI-Powered incident report generation"""

import json
from typing import Dict, Any
from app.agents import BaseAgent
from app.utils import append_trace_event, save_artifact
from app.utils.llm_client import get_llm_client


class ReporterAgent(BaseAgent):
    """Agent responsible for generating comprehensive AI-powered incident reports"""
    
    async def run(self) -> Dict[str, Any]:
        """Generate AI-powered incident report"""
        
        append_trace_event(
            self.incident_id,
            "ReporterAgent",
            "diagnosis",
            "Generating comprehensive AI incident report",
            meta={"phase": "reporting", "ai_enabled": True}
        )
        
        # Gather all evidence
        log_data = self.config.get("log_data", {})
        metrics_data = self.config.get("metrics_data", {})
        fix_data = self.config.get("fix_data", {})
        test_data = self.config.get("test_data", {})
        
        # Generate AI report
        llm = get_llm_client()
        report = await llm.generate_report(
            log_data.get("analysis", {}),
            metrics_data.get("analysis", {}),
            fix_data.get("fixes", {}),
            test_data.get("risk_assessment", {}),
            {
                "incident_id": self.incident_id,
                "scenario": self.config.get("scenario", "unknown"),
                "start_time": self.config.get("start_time", ""),
                "target_vm": self.config.get("ssh_host", "unknown")
            }
        )
        
        # Save report
        save_artifact(self.incident_id, "incident_report.md", report)
        
        # Also save as JSON for API
        report_summary = {
            "incident_id": self.incident_id,
            "generated_by": "AI (Google Gemini)",
            "report_length": len(report),
            "format": "markdown"
        }
        save_artifact(self.incident_id, "report_summary.json", json.dumps(report_summary, indent=2))
        
        append_trace_event(
            self.incident_id,
            "ReporterAgent",
            "evidence",
            f"AI generated comprehensive incident report ({len(report)} characters)",
            evidence=["incident_report.md", "report_summary.json"],
            confidence=0.95,
            meta={"report_length": len(report)}
        )
        
        return {
            "report": report,
            "report_path": f"incidents/{self.incident_id}/incident_report.md",
            "summary": report_summary
        }
