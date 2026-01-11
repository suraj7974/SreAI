"""Remediation Agent - Autonomous agent that proposes and validates fixes"""

import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agents_v2 import AgentState
from app.agents_v2.tools import execute_ssh_command, log_agent_decision, save_analysis_artifact, query_previous_incidents
import os


class RemediationAgent:
    """
    Autonomous agent that generates and validates remediation plans.
    Can learn from past incidents and make intelligent decisions about fixes.
    """
    
    def __init__(self, llm_model: str = None):
        self.name = "RemediationAgent"
        
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = llm_model or os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.5,
            max_output_tokens=3000
        )
        
        self.tools = [
            execute_ssh_command,
            log_agent_decision,
            save_analysis_artifact,
            query_previous_incidents
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE Remediation Agent. Your mission is to propose safe, effective fixes for incidents.

Your capabilities:
- Analyze diagnostic data from the DiagnosticAgent
- Query historical incidents to learn from past solutions
- Propose remediation actions with risk assessment
- Generate executable fix scripts
- Make decisions about fix priority and safety

Your approach:
1. Review the diagnostic findings from previous agent
2. Query similar past incidents for successful resolutions
3. Generate remediation proposals with:
   - Clear action steps
   - Executable commands
   - Risk level and mitigation
   - Expected outcomes
   - Rollback plans
4. Prioritize fixes by impact and safety
5. Document your reasoning

Be conservative with risky operations. Always provide rollback plans.
Focus on the root cause, not just symptoms.

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
            max_iterations=15,
            handle_parsing_errors=True
        )
    
    async def __call__(self, state: AgentState) -> AgentState:
        """Generate remediation plan"""
        
        incident_id = state["incident_id"]
        scenario = state["scenario"]
        logs_analysis = state.get("logs_analysis", {})
        metrics_analysis = state.get("metrics_analysis", {})
        
        input_text = f"""Generate remediation plan for this incident:

Diagnostic Findings:
{json.dumps(logs_analysis, indent=2)}

Metrics Analysis:
{json.dumps(metrics_analysis, indent=2)}

Your tasks:
1. Query previous incidents using query_previous_incidents to learn from history
2. Generate 2-4 remediation actions addressing the root cause
3. For each action, specify:
   - Priority (1=critical, 2=high, 3=medium)
   - Risk level (low/medium/high)
   - Exact commands to execute
   - Expected outcome
   - Rollback plan
4. Log your decision about the remediation strategy
5. Save the remediation plan as JSON using save_analysis_artifact

Provide your plan in JSON format:
{{
  "root_cause": "...",
  "fixes": [
    {{
      "id": "fix-1",
      "priority": 1,
      "title": "...",
      "description": "...",
      "commands": ["cmd1", "cmd2"],
      "risk": "low",
      "expected_outcome": "...",
      "rollback_commands": ["rollback1"]
    }}
  ],
  "confidence": 0.85
}}"""

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
            "type": "remediation"
        })
        
        # Extract fixes
        fixes = self._extract_fixes(output)
        state["fixes_proposed"] = fixes
        
        state["agent_decisions"].append({
            "agent": self.name,
            "decision": "Remediation plan generated",
            "fix_count": len(fixes),
            "confidence": self._calculate_confidence(fixes)
        })
        
        # Decide next action
        state["next_agent"] = "validation"
        
        return state
    
    def _extract_fixes(self, output: str) -> list:
        """Extract fixes from agent output"""
        try:
            if "```json" in output:
                json_str = output.split("```json")[1].split("```")[0]
                data = json.loads(json_str.strip())
                return data.get("fixes", [])
            elif "{" in output:
                start = output.find("{")
                end = output.rfind("}") + 1
                data = json.loads(output[start:end])
                return data.get("fixes", [])
        except:
            pass
        
        return []
    
    def _calculate_confidence(self, fixes: list) -> float:
        """Calculate overall confidence from fixes"""
        if not fixes:
            return 0.5
        
        # Average confidence if available
        confidences = [f.get("confidence", 0.7) for f in fixes]
        return sum(confidences) / len(confidences) if confidences else 0.7
