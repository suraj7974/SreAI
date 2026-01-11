"""
SRE Agent - Supervisor Graph

This is the main LangGraph that orchestrates all agents.
It implements the flow: Monitor -> Diagnose -> Remediate (with human approval)
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Literal

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from sre_agent.state import SREAgentState, IncidentStatus, create_initial_state
from sre_agent.agents import (
    monitor_node,
    diagnostic_node,
    remediation_planning_node,
    remediation_execution_node,
)
from sre_agent.config import settings

logger = logging.getLogger(__name__)


def route_after_monitor(state: SREAgentState) -> Literal["diagnostic", "__end__"]:
    """Route after monitor agent completes"""
    if state.get("should_continue") and state.get("next_agent") == "diagnostic":
        return "diagnostic"
    return "__end__"


def route_after_diagnostic(
    state: SREAgentState,
) -> Literal["remediation_plan", "__end__"]:
    """Route after diagnostic agent completes"""
    if state.get("should_continue") and state.get("next_agent") == "remediation":
        return "remediation_plan"
    return "__end__"


def route_after_remediation_plan(
    state: SREAgentState,
) -> Literal["human_approval", "__end__"]:
    """Route after remediation plan is created"""
    if state.get("awaiting_approval"):
        return "human_approval"
    return "__end__"


def route_after_approval(
    state: SREAgentState,
) -> Literal["remediation_execute", "__end__"]:
    """Route after human approval decision"""
    plan = state.get("remediation_plan", {})
    if plan.get("approved"):
        return "remediation_execute"
    return "__end__"


async def human_approval_node(state: SREAgentState) -> SREAgentState:
    """
    Human Approval Node

    This is a checkpoint where the graph pauses for human approval.
    The graph will be resumed when approval is granted via API.
    """
    logger.info(
        f"[HumanApproval] Waiting for approval on incident {state.get('incident_id')}"
    )

    plan = state.get("remediation_plan", {})

    # This node just marks that we're waiting
    # The actual approval happens via the API, which updates the state
    # and resumes the graph

    thoughts = state.get("agent_thoughts", [])
    thoughts.append(
        {
            "agent_name": "HumanApproval",
            "thought": f"Waiting for human approval of remediation plan {plan.get('plan_id')}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return {
        **state,
        "agent_thoughts": thoughts,
        "current_agent": "human_approval",
        "status": IncidentStatus.AWAITING_APPROVAL,
        "updated_at": datetime.utcnow().isoformat(),
    }


def build_sre_agent_graph() -> StateGraph:
    """
    Build the main SRE Agent graph.

    Flow:
    1. Monitor -> detects issues, gathers metrics
    2. Diagnostic -> analyzes root cause
    3. Remediation Plan -> creates fix plan
    4. Human Approval -> waits for approval (interrupt)
    5. Remediation Execute -> applies fixes
    6. END

    The graph supports:
    - Human-in-the-loop at remediation step
    - Early termination if no issues found
    - State persistence for resumption
    """

    # Create the graph
    graph = StateGraph(SREAgentState)

    # Add nodes
    graph.add_node("monitor", monitor_node)
    graph.add_node("diagnostic", diagnostic_node)
    graph.add_node("remediation_plan", remediation_planning_node)
    graph.add_node("human_approval", human_approval_node)
    graph.add_node("remediation_execute", remediation_execution_node)

    # Set entry point
    graph.set_entry_point("monitor")

    # Add conditional edges
    graph.add_conditional_edges(
        "monitor", route_after_monitor, {"diagnostic": "diagnostic", "__end__": END}
    )

    graph.add_conditional_edges(
        "diagnostic",
        route_after_diagnostic,
        {"remediation_plan": "remediation_plan", "__end__": END},
    )

    graph.add_conditional_edges(
        "remediation_plan",
        route_after_remediation_plan,
        {"human_approval": "human_approval", "__end__": END},
    )

    graph.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {"remediation_execute": "remediation_execute", "__end__": END},
    )

    # Remediation execute always goes to end
    graph.add_edge("remediation_execute", END)

    return graph


# Create compiled graph with memory checkpoint for state persistence
memory = MemorySaver()
sre_agent_graph = build_sre_agent_graph().compile(
    checkpointer=memory,
    interrupt_before=["human_approval"],  # Interrupt before human approval
)


class SREAgentOrchestrator:
    """
    High-level orchestrator for the SRE Agent system.

    Provides methods to:
    - Start new incidents
    - Resume incidents after approval
    - Query incident status
    - Approve/reject remediation plans
    """

    def __init__(self):
        self.graph = sre_agent_graph
        self.active_incidents: Dict[str, SREAgentState] = {}

    async def start_incident(
        self, target_instance: str, alerts: list = None, trigger_source: str = "manual"
    ) -> str:
        """Start a new incident investigation"""

        incident_id = f"inc-{uuid.uuid4().hex[:12]}"

        initial_state = create_initial_state(
            incident_id=incident_id,
            target_instance=target_instance,
            alerts=alerts or [],
            trigger_source=trigger_source,
        )

        logger.info(f"Starting incident {incident_id} for {target_instance}")

        # Create thread config for this incident
        config = {"configurable": {"thread_id": incident_id}}

        try:
            # Run the graph until it hits an interrupt or completes
            result = await self.graph.ainvoke(initial_state, config)
            self.active_incidents[incident_id] = result

            logger.info(f"Incident {incident_id} reached state: {result.get('status')}")
            return incident_id

        except Exception as e:
            logger.error(f"Error starting incident {incident_id}: {e}", exc_info=True)
            raise

    async def approve_remediation(
        self, incident_id: str, approved_by: str, feedback: str = None
    ) -> Dict[str, Any]:
        """Approve a remediation plan and resume execution"""

        config = {"configurable": {"thread_id": incident_id}}

        # Get current state
        current_state = await self.graph.aget_state(config)
        if not current_state or not current_state.values:
            raise ValueError(f"Incident {incident_id} not found")

        state = dict(current_state.values)

        # Update state with approval
        plan = state.get("remediation_plan", {})
        plan["approved"] = True
        plan["approved_by"] = approved_by
        plan["approved_at"] = datetime.utcnow().isoformat()

        state["remediation_plan"] = plan
        state["awaiting_approval"] = False
        state["human_feedback"] = feedback

        # Update the state
        await self.graph.aupdate_state(config, state)

        logger.info(f"Remediation approved for incident {incident_id} by {approved_by}")

        # Resume execution
        result = await self.graph.ainvoke(None, config)
        self.active_incidents[incident_id] = result

        return result

    async def reject_remediation(
        self, incident_id: str, rejected_by: str, reason: str = None
    ) -> Dict[str, Any]:
        """Reject a remediation plan"""

        config = {"configurable": {"thread_id": incident_id}}

        current_state = await self.graph.aget_state(config)
        if not current_state or not current_state.values:
            raise ValueError(f"Incident {incident_id} not found")

        state = dict(current_state.values)

        # Update state with rejection
        plan = state.get("remediation_plan", {})
        plan["approved"] = False
        plan["rejected_by"] = rejected_by
        plan["rejected_at"] = datetime.utcnow().isoformat()
        plan["rejection_reason"] = reason

        state["remediation_plan"] = plan
        state["awaiting_approval"] = False
        state["human_feedback"] = reason
        state["status"] = IncidentStatus.FAILED
        state["should_continue"] = False

        await self.graph.aupdate_state(config, state)

        logger.info(f"Remediation rejected for incident {incident_id} by {rejected_by}")

        # Resume to reach end state
        result = await self.graph.ainvoke(None, config)
        self.active_incidents[incident_id] = result

        return result

    async def get_incident_state(self, incident_id: str) -> Dict[str, Any]:
        """Get the current state of an incident"""

        config = {"configurable": {"thread_id": incident_id}}

        current_state = await self.graph.aget_state(config)
        if not current_state or not current_state.values:
            return None

        return dict(current_state.values)

    async def get_pending_approvals(self) -> list:
        """Get all incidents waiting for approval"""

        pending = []
        for incident_id, state in self.active_incidents.items():
            if state.get("awaiting_approval"):
                pending.append(
                    {
                        "incident_id": incident_id,
                        "target_instance": state.get("target_instance"),
                        "severity": state.get("severity"),
                        "diagnosis": state.get("diagnosis", {}).get("root_cause"),
                        "remediation_plan": state.get("remediation_plan"),
                        "created_at": state.get("created_at"),
                    }
                )

        return pending


# Global orchestrator instance
orchestrator = SREAgentOrchestrator()
