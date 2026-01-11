"""LLM Client for AI Agents using Google Gemini"""

import os
import json
import logging
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client for all AI agents"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = os.getenv("GOOGLE_MODEL", "gemini-pro")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens
        )
        
        logger.info(f"LLM Client initialized with model: {self.model_name}")
    
    async def analyze_logs(self, logs: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered log analysis"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE analyzing system logs to diagnose incidents.
Analyze the logs and provide structured insights in JSON format.

Return JSON with this structure:
{
  "summary": "Brief overview of what's happening",
  "errors_found": ["list", "of", "key", "errors"],
  "root_cause": "Most likely root cause based on log patterns",
  "severity": "low/medium/high/critical",
  "timeline": ["chronological", "sequence", "of", "events"],
  "recommendations": ["immediate", "actions", "to", "take"],
  "confidence": 0.85
}
"""),
            ("user", "Analyze these logs:\n\n{logs}\n\nContext: {context}")
        ])
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "logs": logs[:10000],  # Limit to avoid token limits
                "context": json.dumps(context, indent=2)
            })
            
            # Parse JSON from response
            content = response.content
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            return result
            
        except Exception as e:
            logger.error(f"LLM log analysis failed: {e}")
            return {
                "summary": "AI analysis unavailable",
                "errors_found": [],
                "root_cause": "Unable to determine",
                "severity": "medium",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def analyze_metrics(self, metrics: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered metrics analysis"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE analyzing system metrics to identify anomalies and performance issues.

Analyze the metrics and return JSON:
{
  "summary": "Overview of system health",
  "anomalies": [
    {
      "metric": "cpu_usage_percent",
      "value": 95.5,
      "severity": "high",
      "analysis": "Why this is concerning",
      "impact": "What it affects"
    }
  ],
  "patterns": ["observed", "patterns"],
  "predictions": "What might happen next",
  "recommendations": ["actions", "to", "take"],
  "confidence": 0.90
}
"""),
            ("user", "Analyze these metrics:\n\n{metrics}\n\nContext: {context}")
        ])
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "metrics": json.dumps(metrics, indent=2),
                "context": json.dumps(context, indent=2)
            })
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            return result
            
        except Exception as e:
            logger.error(f"LLM metrics analysis failed: {e}")
            return {
                "summary": "AI analysis unavailable",
                "anomalies": [],
                "recommendations": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def generate_fixes(self, 
                           logs_analysis: Dict[str, Any],
                           metrics_analysis: Dict[str, Any],
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered fix generation"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE proposing remediation actions for incidents.
Generate concrete, actionable fix suggestions with proper risk assessment.

Return JSON:
{
  "root_cause_summary": "Concise root cause",
  "fixes": [
    {
      "id": "fix-1",
      "priority": 1,
      "timeline": "immediate/short-term/long-term",
      "title": "Clear action title",
      "description": "Detailed explanation",
      "commands": ["actual", "commands", "to", "run"],
      "risk": "low/medium/high",
      "risk_rationale": "Why this risk level",
      "expected_outcome": "What will happen",
      "rollback_plan": "How to undo if needed"
    }
  ],
  "validation_steps": ["how", "to", "verify", "fix", "worked"],
  "confidence": 0.85
}
"""),
            ("user", """Generate remediation fixes for this incident:

Log Analysis:
{logs_analysis}

Metrics Analysis:
{metrics_analysis}

Context:
{context}
""")
        ])
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "logs_analysis": json.dumps(logs_analysis, indent=2),
                "metrics_analysis": json.dumps(metrics_analysis, indent=2),
                "context": json.dumps(context, indent=2)
            })
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            return result
            
        except Exception as e:
            logger.error(f"LLM fix generation failed: {e}")
            return {
                "root_cause_summary": "Unable to determine",
                "fixes": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def assess_risks(self, fixes: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered risk assessment"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE assessing risks of proposed remediation actions.
Provide detailed risk analysis for each fix.

Return JSON:
{
  "overall_risk": "low/medium/high",
  "risk_assessments": [
    {
      "fix_id": "fix-1",
      "risk_score": 0.3,
      "risk_level": "low",
      "concerns": ["potential", "issues"],
      "mitigation": "How to reduce risk",
      "approval_required": true/false,
      "testing_required": true/false
    }
  ],
  "recommended_order": ["fix-1", "fix-2"],
  "pre_execution_checklist": ["items", "to", "verify"],
  "confidence": 0.90
}
"""),
            ("user", "Assess risks for these fixes:\n\n{fixes}\n\nContext: {context}")
        ])
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "fixes": json.dumps(fixes, indent=2),
                "context": json.dumps(context, indent=2)
            })
            
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content.strip())
            return result
            
        except Exception as e:
            logger.error(f"LLM risk assessment failed: {e}")
            return {
                "overall_risk": "high",
                "risk_assessments": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def generate_report(self, 
                            logs_analysis: Dict[str, Any],
                            metrics_analysis: Dict[str, Any],
                            fixes: Dict[str, Any],
                            risk_assessment: Dict[str, Any],
                            context: Dict[str, Any]) -> str:
        """AI-powered incident report generation"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE writing comprehensive incident reports.
Generate a professional, detailed incident report in Markdown format.

Include:
1. Executive Summary
2. Incident Timeline
3. Root Cause Analysis
4. Impact Assessment
5. Remediation Actions
6. Lessons Learned
7. Recommendations

Use proper Markdown formatting with headers, lists, code blocks, etc.
"""),
            ("user", """Generate incident report:

Log Analysis:
{logs_analysis}

Metrics Analysis:
{metrics_analysis}

Proposed Fixes:
{fixes}

Risk Assessment:
{risk_assessment}

Context:
{context}
""")
        ])
        
        try:
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "logs_analysis": json.dumps(logs_analysis, indent=2),
                "metrics_analysis": json.dumps(metrics_analysis, indent=2),
                "fixes": json.dumps(fixes, indent=2),
                "risk_assessment": json.dumps(risk_assessment, indent=2),
                "context": json.dumps(context, indent=2)
            })
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM report generation failed: {e}")
            return f"# Incident Report\n\nError generating report: {str(e)}"


# Singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
