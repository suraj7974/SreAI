"""TesterAgent - AI-Powered risk assessment"""

import json
from typing import Dict, Any
from app.agents import BaseAgent
from app.utils import append_trace_event, save_artifact
from app.utils.llm_client import get_llm_client


class TesterAgent(BaseAgent):
    """Agent responsible for AI-powered risk assessment of proposed fixes"""
    
    async def run(self) -> Dict[str, Any]:
        """Perform AI risk assessment on proposed fixes"""
        
        append_trace_event(
            self.incident_id,
            "TesterAgent",
            "diagnosis",
            "Performing AI-powered risk assessment",
            meta={"phase": "testing", "ai_enabled": True}
        )
        
        # Get fix suggestions
        fix_data = self.config.get("fix_data", {})
        
        # AI risk assessment
        llm = get_llm_client()
        risk_assessment = await llm.assess_risks(
            fix_data.get("fixes", {}),
            {
                "incident_id": self.incident_id,
                "scenario": self.config.get("scenario", "unknown")
            }
        )
        
        # Save risk assessment
        save_artifact(
            self.incident_id,
            "risk_assessment.json",
            json.dumps(risk_assessment, indent=2)
        )
        
        overall_risk = risk_assessment.get("overall_risk", "medium")
        confidence = risk_assessment.get("confidence", 0.9)
        
        append_trace_event(
            self.incident_id,
            "TesterAgent",
            "evidence",
            f"AI Risk Assessment: Overall risk is {overall_risk.upper()}",
            evidence=["risk_assessment.json"],
            confidence=confidence,
            meta={
                "overall_risk": overall_risk,
                "assessments_count": len(risk_assessment.get("risk_assessments", []))
            }
        )
        
        return {
            "risk_assessment": risk_assessment,
            "overall_risk": overall_risk,
            "confidence": confidence
        }
