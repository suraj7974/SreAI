"""Reporter Agent - Generates comprehensive incident reports"""

import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agents_v2 import AgentState
from app.agents_v2.tools import save_analysis_artifact, log_agent_decision
import os


class ReporterAgent:
    """
    Autonomous agent that generates comprehensive incident reports.
    Synthesizes findings from all other agents into actionable documentation.
    """
    
    def __init__(self, llm_model: str = None):
        self.name = "ReporterAgent"
        
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = llm_model or os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.4,
            max_output_tokens=4000
        )
        
        self.tools = [
            save_analysis_artifact,
            log_agent_decision
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE Reporter Agent. Your mission is to create clear, actionable incident reports.

Your capabilities:
- Synthesize findings from all agents
- Create executive summaries for stakeholders
- Document technical details for engineers
- Provide clear next steps and recommendations

Your report should include:
1. Executive Summary (non-technical)
2. Incident Timeline
3. Root Cause Analysis
4. Impact Assessment
5. Remediation Actions (approved/pending)
6. Lessons Learned
7. Recommendations for Prevention

Use clear Markdown formatting. Be concise but comprehensive.

Current context:
- Incident ID: {incident_id}
- Scenario: {scenario}
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    async def __call__(self, state: AgentState) -> AgentState:
        """Generate incident report"""
        
        incident_id = state["incident_id"]
        scenario = state["scenario"]
        
        # Gather all agent findings
        diagnostic_findings = state.get("logs_analysis", {})
        fixes = state.get("fixes_proposed", [])
        validation = state.get("risk_assessment", {})
        agent_decisions = state.get("agent_decisions", [])
        
        input_text = f"""Generate comprehensive incident report:

Diagnostic Findings:
{json.dumps(diagnostic_findings, indent=2)}

Proposed Fixes:
{json.dumps(fixes, indent=2)}

Validation Results:
{json.dumps(validation, indent=2)}

Agent Decisions:
{json.dumps(agent_decisions, indent=2)}

Your tasks:
1. Create a comprehensive Markdown report with all sections
2. Highlight key decisions made by autonomous agents
3. Provide clear next steps
4. Save the report as 'incident_report.md' using save_analysis_artifact
5. Log completion decision

Make the report professional, clear, and actionable."""

        result = await self.executor.ainvoke({
            "input": input_text,
            "incident_id": incident_id,
            "scenario": scenario,
            "chat_history": state.get("messages", [])
        })
        
        output = result.get("output", "")
        
        state["messages"].append({
            "agent": self.name,
            "content": output,
            "type": "report"
        })
        
        state["final_report"] = output
        
        state["agent_decisions"].append({
            "agent": self.name,
            "decision": "Report generated",
            "confidence": 1.0
        })
        
        state["next_agent"] = "END"
        
        return state
