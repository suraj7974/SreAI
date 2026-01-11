"""
SRE Agent - Monitor Agent

This agent continuously monitors systems and detects anomalies.
It uses Prometheus to query metrics and decides when to escalate.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Literal

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, END

from sre_agent.state import SREAgentState, IncidentStatus, Severity
from sre_agent.tools import MONITORING_TOOLS, prometheus
from sre_agent.config import settings

logger = logging.getLogger(__name__)


MONITOR_SYSTEM_PROMPT = """You are an expert SRE Monitor Agent. Your job is to:

1. OBSERVE: Query Prometheus metrics to understand system health
2. ANALYZE: Detect anomalies, trends, and potential issues
3. DECIDE: Determine if this requires investigation or is a false alarm

You have access to these tools:
- query_prometheus: Run PromQL queries for current metrics
- query_prometheus_range: Get historical data for trend analysis
- get_active_alerts: Check for firing Prometheus alerts
- get_system_metrics: Get comprehensive metrics for a specific instance

THRESHOLDS:
- CPU Warning: {cpu_warning}% | Critical: {cpu_critical}%
- Memory Warning: {memory_warning}% | Critical: {memory_critical}%
- Disk Warning: {disk_warning}% | Critical: {disk_critical}%

When you detect an issue:
1. Gather sufficient evidence (multiple metrics, trends)
2. Determine severity based on thresholds and impact
3. Provide a clear summary of what you observed

Always explain your reasoning. Be thorough but efficient - don't query unnecessary metrics.
""".format(
    cpu_warning=settings.cpu_warning_threshold,
    cpu_critical=settings.cpu_critical_threshold,
    memory_warning=settings.memory_warning_threshold,
    memory_critical=settings.memory_critical_threshold,
    disk_warning=settings.disk_warning_threshold,
    disk_critical=settings.disk_critical_threshold,
)


def get_monitor_llm():
    """Get the LLM for the monitor agent"""
    return ChatGoogleGenerativeAI(
        model=settings.google_model,
        google_api_key=settings.google_api_key,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_tokens,
    )


def create_monitor_agent():
    """Create the ReAct monitor agent with tools"""
    llm = get_monitor_llm()
    return create_react_agent(
        llm,
        tools=MONITORING_TOOLS,
        state_modifier=MONITOR_SYSTEM_PROMPT,
    )


async def monitor_node(state: SREAgentState) -> SREAgentState:
    """
    Monitor Agent Node

    Queries Prometheus, analyzes metrics, and decides if escalation is needed.
    """
    logger.info(
        f"[MonitorAgent] Starting monitoring for incident {state.get('incident_id', 'N/A')}"
    )

    instance = state.get("target_instance", "")
    if not instance:
        logger.warning("[MonitorAgent] No target instance specified")
        return {
            **state,
            "error": "No target instance specified",
            "should_continue": False,
        }

    # Record that we're in monitoring phase
    thoughts = state.get("agent_thoughts", [])
    thoughts.append(
        {
            "agent_name": "MonitorAgent",
            "thought": f"Starting health check for instance {instance}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    try:
        # Create the ReAct agent
        agent = create_monitor_agent()

        # Construct the monitoring task
        task = f"""
        Perform a comprehensive health check on instance: {instance}
        
        Current context:
        - Incident ID: {state.get("incident_id", "N/A")}
        - Trigger source: {state.get("trigger_source", "manual")}
        - Alerts received: {json.dumps(state.get("alerts", []))}
        
        Tasks:
        1. Get current system metrics (CPU, memory, disk, load)
        2. Check for any active alerts on this instance
        3. Look at trends over the last 15 minutes
        4. Identify any anomalies or concerning patterns
        
        Provide your analysis including:
        - Current health status
        - Any issues detected
        - Severity assessment
        - Whether further investigation is needed
        """

        # Run the agent
        result = await agent.ainvoke({"messages": [HumanMessage(content=task)]})

        # Extract the final response
        final_message = result["messages"][-1].content if result.get("messages") else ""

        # Parse the agent's findings
        metrics_collected = await _collect_metrics_summary(instance)

        # Determine severity from analysis
        severity = _determine_severity(metrics_collected, state.get("alerts", []))

        # Record the analysis
        thoughts.append(
            {
                "agent_name": "MonitorAgent",
                "thought": "Completed health check analysis",
                "action": "Collected metrics and analyzed system health",
                "observation": final_message[:500],  # Truncate for storage
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Determine if we need to escalate to diagnostic
        needs_investigation = severity in [Severity.WARNING, Severity.CRITICAL]

        return {
            **state,
            "metrics": metrics_collected,
            "severity": severity,
            "status": IncidentStatus.INVESTIGATING
            if needs_investigation
            else IncidentStatus.RESOLVED,
            "agent_thoughts": thoughts,
            "current_agent": "monitor",
            "next_agent": "diagnostic" if needs_investigation else "end",
            "should_continue": needs_investigation,
            "updated_at": datetime.utcnow().isoformat(),
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    except Exception as e:
        logger.error(f"[MonitorAgent] Error: {e}", exc_info=True)
        thoughts.append(
            {
                "agent_name": "MonitorAgent",
                "thought": f"Error during monitoring: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        return {
            **state,
            "error": str(e),
            "agent_thoughts": thoughts,
            "should_continue": False,
        }


async def _collect_metrics_summary(instance: str) -> Dict[str, Any]:
    """Collect a summary of key metrics for the instance"""
    metrics = {}

    queries = {
        "cpu_usage": f'100 - (avg by(instance) (irate(node_cpu_seconds_total{{instance=~"{instance}.*",mode="idle"}}[5m])) * 100)',
        "memory_usage": f'(1 - (node_memory_MemAvailable_bytes{{instance=~"{instance}.*"}} / node_memory_MemTotal_bytes{{instance=~"{instance}.*"}})) * 100',
        "disk_usage": f'(1 - (node_filesystem_avail_bytes{{instance=~"{instance}.*",mountpoint="/"}} / node_filesystem_size_bytes{{instance=~"{instance}.*",mountpoint="/"}})) * 100',
        "load_1m": f'node_load1{{instance=~"{instance}.*"}}',
    }

    for name, query in queries.items():
        try:
            result = await prometheus.query(query)
            if result.get("data", {}).get("result"):
                value = result["data"]["result"][0].get("value", [None, None])[1]
                metrics[name] = float(value) if value else None
            else:
                metrics[name] = None
        except Exception as e:
            metrics[name] = f"Error: {str(e)}"

    metrics["timestamp"] = datetime.utcnow().isoformat()
    metrics["instance"] = instance

    return metrics


def _determine_severity(metrics: Dict[str, Any], alerts: list) -> Severity:
    """Determine incident severity based on metrics and alerts"""

    # Check for critical alerts
    for alert in alerts:
        if alert.get("severity") == "critical":
            return Severity.CRITICAL

    # Check metric thresholds
    cpu = metrics.get("cpu_usage")
    memory = metrics.get("memory_usage")
    disk = metrics.get("disk_usage")

    if isinstance(cpu, (int, float)) and cpu > settings.cpu_critical_threshold:
        return Severity.CRITICAL
    if isinstance(memory, (int, float)) and memory > settings.memory_critical_threshold:
        return Severity.CRITICAL
    if isinstance(disk, (int, float)) and disk > settings.disk_critical_threshold:
        return Severity.CRITICAL

    if isinstance(cpu, (int, float)) and cpu > settings.cpu_warning_threshold:
        return Severity.WARNING
    if isinstance(memory, (int, float)) and memory > settings.memory_warning_threshold:
        return Severity.WARNING
    if isinstance(disk, (int, float)) and disk > settings.disk_warning_threshold:
        return Severity.WARNING

    return Severity.INFO


def should_continue_monitoring(state: SREAgentState) -> Literal["diagnostic", "end"]:
    """Routing function to decide next step after monitoring"""
    if state.get("should_continue") and state.get("next_agent") == "diagnostic":
        return "diagnostic"
    return "end"
