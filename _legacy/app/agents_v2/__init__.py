"""Real AI Agents with LangGraph - Autonomous, tool-using, collaborative agents"""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import operator

class AgentState(TypedDict):
    """Shared state across all agents"""
    messages: Annotated[List[Dict[str, Any]], operator.add]
    incident_id: str
    target_vm: Dict[str, Any]
    scenario: str
    logs_raw: str
    logs_analysis: Dict[str, Any]
    metrics_raw: Dict[str, Any]
    metrics_analysis: Dict[str, Any]
    fixes_proposed: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    test_results: Dict[str, Any]
    final_report: str
    next_agent: str
    agent_decisions: List[Dict[str, Any]]
