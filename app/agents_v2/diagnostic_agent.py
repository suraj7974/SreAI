"""Diagnostic Agent - Autonomous agent that investigates incidents"""

import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.agents_v2 import AgentState
from app.agents_v2.tools import collect_system_logs, collect_system_metrics, log_agent_decision, save_analysis_artifact
import os


class DiagnosticAgent:
    """
    Autonomous agent that investigates incidents by collecting data and analyzing patterns.
    Uses tools to gather information and makes decisions about what to investigate.
    """
    
    def __init__(self, llm_model: str = None):
        self.name = "DiagnosticAgent"
        
        # Initialize LLM
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = llm_model or os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.3,  # Lower temperature for more focused analysis
            max_output_tokens=2000
        )
        
        # Define agent's tools
        self.tools = [
            collect_system_logs,
            collect_system_metrics,
            log_agent_decision,
            save_analysis_artifact
        ]
        
        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SRE Diagnostic Agent. Your mission is to investigate incidents autonomously.

Your capabilities:
- Collect system logs and metrics using your tools
- Analyze patterns and anomalies
- Make decisions about what to investigate next
- Document your findings

Your approach:
1. Understand the incident scenario
2. Decide what data you need to collect
3. Use tools to gather that data
4. Analyze the data for root causes
5. Document your findings with evidence
6. Decide if you need more information or if diagnosis is complete

Be thorough but efficient. Always log your decisions and reasoning.
When you have enough information to diagnose the incident, provide a structured analysis.

Current incident details:
- Incident ID: {incident_id}
- Scenario: {scenario}
- Target VM: {target_vm}
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create tool-calling agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    async def __call__(self, state: AgentState) -> AgentState:
        """Execute diagnostic analysis"""
        
        incident_id = state["incident_id"]
        scenario = state["scenario"]
        target_vm = state["target_vm"]
        
        # Prepare input for agent
        input_text = f"""Investigate this incident:
Scenario: {scenario}

Your tasks:
1. Collect system logs using collect_system_logs tool
2. Collect metrics using collect_system_metrics tool
3. Analyze the data to identify root cause
4. Log your decision about what you found using log_agent_decision
5. Save your analysis using save_analysis_artifact

VM Details:
- Host: {target_vm.get('host')}
- Port: {target_vm.get('port', 22)}
- User: {target_vm.get('user')}
- Key Path: {target_vm.get('key_path')}

Proceed with investigation."""

        # Execute agent
        result = await self.executor.ainvoke({
            "input": input_text,
            "incident_id": incident_id,
            "scenario": scenario,
            "target_vm": json.dumps(target_vm),
            "chat_history": state.get("messages", [])
        })
        
        # Parse agent's output
        output = result.get("output", "")
        
        # Update state
        state["messages"].append({
            "agent": self.name,
            "content": output,
            "type": "diagnostic"
        })
        
        # Try to extract structured analysis from output
        analysis = self._extract_analysis(output)
        state["logs_analysis"] = analysis
        
        # Record decision
        state["agent_decisions"].append({
            "agent": self.name,
            "decision": "Investigation complete",
            "findings": analysis.get("summary", "Analysis completed"),
            "confidence": analysis.get("confidence", 0.7)
        })
        
        # Decide next agent
        state["next_agent"] = "remediation"
        
        return state
    
    def _extract_analysis(self, output: str) -> Dict[str, Any]:
        """Extract structured analysis from agent output"""
        
        # Try to parse JSON if present
        try:
            if "```json" in output:
                json_str = output.split("```json")[1].split("```")[0]
                return json.loads(json_str.strip())
            elif "{" in output and "}" in output:
                # Try to extract JSON object
                start = output.find("{")
                end = output.rfind("}") + 1
                return json.loads(output[start:end])
        except:
            pass
        
        # Fallback: create basic structure from text
        return {
            "summary": output[:500],
            "confidence": 0.7,
            "findings": output,
            "severity": "medium"
        }
