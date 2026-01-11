"""
SRE Agent - Diagnostic Agent

This agent performs deep analysis to identify root causes.
It uses both Prometheus queries and SSH commands to gather evidence.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from sre_agent.state import SREAgentState, IncidentStatus, Severity
from sre_agent.tools import DIAGNOSTIC_TOOLS
from sre_agent.config import settings

logger = logging.getLogger(__name__)


DIAGNOSTIC_SYSTEM_PROMPT = """You are an expert SRE Diagnostic Agent. Your job is to:

1. INVESTIGATE: Deep dive into the issue using metrics, logs, and system commands
2. CORRELATE: Find relationships between symptoms and potential causes
3. DIAGNOSE: Identify the root cause with supporting evidence

You have access to these tools:
- query_prometheus / query_prometheus_range: Query metrics and trends
- get_system_metrics: Get comprehensive system metrics
- execute_ssh_command: Run diagnostic commands on the target
- get_system_logs: Retrieve and filter system logs
- get_top_processes: See top CPU/memory consumers
- check_service_status: Check systemd service status

DIAGNOSTIC METHODOLOGY:
1. Start with the symptoms (metrics showing the issue)
2. Look at trends - when did the issue start?
3. Check logs around that timeframe
4. Identify resource-hungry processes
5. Check related services
6. Form a hypothesis and gather evidence

Common root causes to consider:
- Runaway process consuming CPU/memory
- Memory leak in application
- Disk filling up from logs or temp files
- Network issues causing timeouts
- Service crash/restart loop
- OOM killer activity
- Resource exhaustion (file descriptors, connections)

Be systematic and thorough. Document your reasoning.
Your diagnosis should include:
1. Root cause identification
2. Evidence supporting the diagnosis
3. Confidence level (0-1)
4. Affected components
5. Recommended actions
"""


def get_diagnostic_llm():
    """Get the LLM for the diagnostic agent"""
    return ChatGoogleGenerativeAI(
        model=settings.google_model,
        google_api_key=settings.google_api_key,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_tokens,
    )


def create_diagnostic_agent():
    """Create the ReAct diagnostic agent with tools"""
    llm = get_diagnostic_llm()
    return create_react_agent(
        llm,
        tools=DIAGNOSTIC_TOOLS,
        state_modifier=DIAGNOSTIC_SYSTEM_PROMPT,
    )


async def diagnostic_node(state: SREAgentState) -> SREAgentState:
    """
    Diagnostic Agent Node

    Performs deep analysis to identify root cause and gather evidence.
    """
    logger.info(
        f"[DiagnosticAgent] Starting diagnosis for incident {state.get('incident_id', 'N/A')}"
    )

    instance = state.get("target_instance", "")
    metrics = state.get("metrics", {})
    alerts = state.get("alerts", [])
    severity = state.get("severity", Severity.WARNING)

    thoughts = state.get("agent_thoughts", [])
    thoughts.append(
        {
            "agent_name": "DiagnosticAgent",
            "thought": f"Starting root cause analysis for {severity.value} severity incident",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    try:
        agent = create_diagnostic_agent()

        # Construct detailed diagnostic task
        task = f"""
        Perform root cause analysis for this incident:
        
        INCIDENT DETAILS:
        - Instance: {instance}
        - Severity: {severity.value}
        - Incident ID: {state.get("incident_id", "N/A")}
        
        CURRENT METRICS:
        {json.dumps(metrics, indent=2)}
        
        ALERTS:
        {json.dumps(alerts, indent=2)}
        
        DIAGNOSTIC TASKS:
        1. Analyze the metric patterns - identify what's abnormal
        2. Query historical data to find when the issue started
        3. Check system logs for errors around that time
        4. Identify top resource consumers (processes)
        5. Check relevant service statuses
        6. Look for correlations between symptoms
        
        Based on your investigation, provide:
        1. ROOT CAUSE: Clear explanation of what's causing the issue
        2. EVIDENCE: List of facts supporting your diagnosis
        3. CONFIDENCE: Your confidence level (0.0 to 1.0)
        4. AFFECTED_COMPONENTS: List of affected services/components
        5. RECOMMENDATIONS: What actions should be taken to fix this
        
        Format your final diagnosis as JSON:
        {{
            "root_cause": "...",
            "evidence": ["...", "..."],
            "confidence": 0.85,
            "affected_components": ["...", "..."],
            "recommendations": ["...", "..."],
            "timeline": "When the issue started and progressed"
        }}
        """

        result = await agent.ainvoke({"messages": [HumanMessage(content=task)]})

        final_message = result["messages"][-1].content if result.get("messages") else ""

        # Parse diagnosis from response
        diagnosis = _parse_diagnosis(final_message)

        # Collect logs for storage
        logs = await _collect_relevant_logs(instance)

        thoughts.append(
            {
                "agent_name": "DiagnosticAgent",
                "thought": f"Diagnosis complete. Root cause: {diagnosis.get('root_cause', 'Unknown')}",
                "action": "Performed comprehensive analysis",
                "observation": f"Confidence: {diagnosis.get('confidence', 0)}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Determine if remediation is needed based on confidence and severity
        needs_remediation = (
            diagnosis.get("confidence", 0) >= 0.6
            and severity in [Severity.WARNING, Severity.CRITICAL]
            and len(diagnosis.get("recommendations", [])) > 0
        )

        return {
            **state,
            "diagnosis": diagnosis,
            "logs": logs,
            "status": IncidentStatus.DIAGNOSED,
            "agent_thoughts": thoughts,
            "current_agent": "diagnostic",
            "next_agent": "remediation" if needs_remediation else "end",
            "should_continue": needs_remediation,
            "updated_at": datetime.utcnow().isoformat(),
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    except Exception as e:
        logger.error(f"[DiagnosticAgent] Error: {e}", exc_info=True)
        thoughts.append(
            {
                "agent_name": "DiagnosticAgent",
                "thought": f"Error during diagnosis: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        return {
            **state,
            "error": str(e),
            "agent_thoughts": thoughts,
            "diagnosis": {"root_cause": "Diagnosis failed", "error": str(e)},
            "status": IncidentStatus.FAILED,
            "should_continue": False,
        }


def _parse_diagnosis(response: str) -> Dict[str, Any]:
    """Parse diagnosis JSON from agent response"""
    try:
        # Try to extract JSON from response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        elif "{" in response:
            # Find JSON object in response
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
        else:
            return {
                "root_cause": response[:500],
                "evidence": [],
                "confidence": 0.5,
                "affected_components": [],
                "recommendations": [],
            }

        return json.loads(json_str)
    except Exception as e:
        logger.warning(f"Failed to parse diagnosis JSON: {e}")
        return {
            "root_cause": response[:500] if response else "Unable to determine",
            "evidence": [],
            "confidence": 0.5,
            "affected_components": [],
            "recommendations": [],
            "parse_error": str(e),
        }


async def _collect_relevant_logs(instance: str) -> str:
    """Collect relevant logs for the incident"""
    from sre_agent.tools import run_ssh_command

    try:
        # Get the host from instance (strip port if present)
        host = instance.split(":")[0]

        # Collect error logs
        stdout, stderr, _ = await run_ssh_command(
            host, "sudo journalctl -p err -n 200 --no-pager"
        )
        return stdout if stdout else f"Failed to collect logs: {stderr}"
    except Exception as e:
        return f"Error collecting logs: {str(e)}"


def should_continue_diagnostic(state: SREAgentState) -> Literal["remediation", "end"]:
    """Routing function to decide next step after diagnosis"""
    if state.get("should_continue") and state.get("next_agent") == "remediation":
        return "remediation"
    return "end"
