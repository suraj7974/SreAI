"""Validation Agent - Autonomous agent that assesses risks and validates fixes"""

import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agents_v2 import AgentState
from app.agents_v2.tools import execute_ssh_command, log_agent_decision, save_analysis_artifact
import os


class ValidationAgent:
    """
    Autonomous agent that validates remediation plans and assesses risks.
    Can make decisions about whether fixes are safe to apply.
    """
    
    def __init__(self, llm_model: str = None):
        self.name = "ValidationAgent"
        
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = llm_model or os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.2,  # Very low temperature for safety-critical decisions
            max_output_tokens=2000
        )
        
        self.tools = [
            execute_ssh_command,
            log_agent_decision,
            save_analysis_artifact
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE Validation Agent. Your mission is to assess risks and validate remediation plans.

Your capabilities:
- Analyze proposed fixes for potential risks
- Execute validation commands to test assumptions
- Make go/no-go decisions on remediation actions
- Identify potential side effects
- Recommend safer alternatives when needed

Your approach:
1. Review each proposed fix carefully
2. Assess risks: data loss, service disruption, cascading failures
3. Execute safe validation commands to verify system state
4. Check for prerequisites and dependencies
5. Make a decision: APPROVE, APPROVE_WITH_CONDITIONS, or REJECT
6. Document your reasoning clearly

Be conservative. Safety is paramount. When in doubt, recommend manual review.

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
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    async def __call__(self, state: AgentState) -> AgentState:
        """Validate remediation plan"""
        
        incident_id = state["incident_id"]
        scenario = state["scenario"]
        fixes = state.get("fixes_proposed", [])
        target_vm = state["target_vm"]
        
        input_text = f"""Validate these proposed fixes:

{json.dumps(fixes, indent=2)}

VM Details for validation:
- Host: {target_vm.get('host')}
- Port: {target_vm.get('port', 22)}
- User: {target_vm.get('user')}
- Key Path: {target_vm.get('key_path')}

Your tasks:
1. For each fix, assess:
   - Risk level accuracy
   - Command safety
   - Potential side effects
   - Prerequisites
2. You can execute safe read-only validation commands using execute_ssh_command
3. Make a decision for each fix: APPROVE, APPROVE_WITH_CONDITIONS, or REJECT
4. Log your decision and reasoning
5. Save validation report using save_analysis_artifact

Provide assessment in JSON format:
{{
  "overall_decision": "APPROVE|APPROVE_WITH_CONDITIONS|REJECT",
  "assessments": [
    {{
      "fix_id": "fix-1",
      "decision": "APPROVE",
      "risk_confirmed": true,
      "concerns": [],
      "conditions": [],
      "safer_alternative": null
    }}
  ],
  "requires_manual_review": false,
  "confidence": 0.90
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
            "type": "validation"
        })
        
        # Extract assessment
        assessment = self._extract_assessment(output)
        state["risk_assessment"] = assessment
        
        state["agent_decisions"].append({
            "agent": self.name,
            "decision": assessment.get("overall_decision", "MANUAL_REVIEW"),
            "requires_manual_review": assessment.get("requires_manual_review", True),
            "confidence": assessment.get("confidence", 0.7)
        })
        
        # Decide next agent
        state["next_agent"] = "reporter"
        
        return state
    
    def _extract_assessment(self, output: str) -> Dict[str, Any]:
        """Extract validation assessment from output"""
        try:
            if "```json" in output:
                json_str = output.split("```json")[1].split("```")[0]
                return json.loads(json_str.strip())
            elif "{" in output:
                start = output.find("{")
                end = output.rfind("}") + 1
                return json.loads(output[start:end])
        except:
            pass
        
        return {
            "overall_decision": "MANUAL_REVIEW",
            "assessments": [],
            "requires_manual_review": True,
            "confidence": 0.5
        }
