"""Multi-Agent Orchestrator using LangGraph"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.agents_v2 import AgentState
from app.agents_v2.diagnostic_agent import DiagnosticAgent
from app.agents_v2.remediation_agent import RemediationAgent
from app.agents_v2.validation_agent import ValidationAgent
from app.agents_v2.reporter_agent import ReporterAgent
from app.utils import generate_incident_id, ensure_incident_dir, append_trace_event

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Orchestrates autonomous AI agents using LangGraph.
    Agents collaborate, make decisions, and adapt based on their findings.
    """
    
    def __init__(self, storage_path: str = "./incidents"):
        self.storage_path = storage_path
        
        # Initialize agents
        self.diagnostic_agent = DiagnosticAgent()
        self.remediation_agent = RemediationAgent()
        self.validation_agent = ValidationAgent()
        self.reporter_agent = ReporterAgent()
        
        # Build agent graph
        self.workflow = self._build_workflow()
        
        logger.info("Multi-Agent Orchestrator initialized with LangGraph")
    
    def _build_workflow(self) -> StateGraph:
        """Build the agent collaboration workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("diagnostic", self.diagnostic_agent)
        workflow.add_node("remediation", self.remediation_agent)
        workflow.add_node("validation", self.validation_agent)
        workflow.add_node("reporter", self.reporter_agent)
        
        # Define workflow edges (agent collaboration flow)
        workflow.set_entry_point("diagnostic")
        
        # Conditional routing based on agent decisions
        def route_after_diagnostic(state: AgentState) -> str:
            """Decide where to go after diagnostic"""
            next_agent = state.get("next_agent", "remediation")
            if next_agent == "END":
                return END
            return next_agent
        
        def route_after_remediation(state: AgentState) -> str:
            """Decide where to go after remediation"""
            next_agent = state.get("next_agent", "validation")
            # Agent could decide to skip validation for low-risk fixes
            if next_agent == "END":
                return END
            return next_agent
        
        def route_after_validation(state: AgentState) -> str:
            """Decide where to go after validation"""
            next_agent = state.get("next_agent", "reporter")
            if next_agent == "END":
                return END
            return next_agent
        
        def route_after_reporter(state: AgentState) -> str:
            """Always end after reporter"""
            return END
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "diagnostic",
            route_after_diagnostic,
            {
                "remediation": "remediation",
                END: END
            }
        )
        
        workflow.add_conditional_edges(
            "remediation",
            route_after_remediation,
            {
                "validation": "validation",
                "reporter": "reporter",
                END: END
            }
        )
        
        workflow.add_conditional_edges(
            "validation",
            route_after_validation,
            {
                "reporter": "reporter",
                "remediation": "remediation",  # Could loop back if validation fails
                END: END
            }
        )
        
        workflow.add_conditional_edges(
            "reporter",
            route_after_reporter,
            {END: END}
        )
        
        return workflow.compile()
    
    async def start_incident(
        self,
        scenario: str,
        target_vm: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> str:
        """Start autonomous multi-agent incident response"""
        
        # Generate incident ID
        incident_id = generate_incident_id()
        
        # Create incident directory
        incident_dir = ensure_incident_dir(incident_id, self.storage_path)
        
        # Log incident start
        append_trace_event(
            incident_id,
            "MultiAgentOrchestrator",
            "diagnosis",
            f"Starting autonomous multi-agent incident response for scenario: {scenario}",
            meta={
                "phase": "initializing",
                "scenario": scenario,
                "agent_system": "LangGraph",
                "autonomous": True
            },
            base_path=self.storage_path
        )
        
        # Initialize agent state
        initial_state: AgentState = {
            "messages": [],
            "incident_id": incident_id,
            "target_vm": target_vm,
            "scenario": scenario,
            "logs_raw": "",
            "logs_analysis": {},
            "metrics_raw": {},
            "metrics_analysis": {},
            "fixes_proposed": [],
            "risk_assessment": {},
            "test_results": {},
            "final_report": "",
            "next_agent": "diagnostic",
            "agent_decisions": []
        }
        
        # Execute agent workflow
        try:
            logger.info(f"Starting agent workflow for incident {incident_id}")
            
            # Run the graph - agents will collaborate autonomously
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Log completion
            append_trace_event(
                incident_id,
                "MultiAgentOrchestrator",
                "report",
                "Autonomous multi-agent incident response completed",
                meta={
                    "phase": "complete",
                    "agents_executed": len(final_state.get("agent_decisions", [])),
                    "total_messages": len(final_state.get("messages", []))
                },
                base_path=self.storage_path
            )
            
            logger.info(f"Incident {incident_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error in multi-agent workflow: {e}", exc_info=True)
            append_trace_event(
                incident_id,
                "MultiAgentOrchestrator",
                "diagnosis",
                f"Multi-agent workflow failed: {str(e)}",
                meta={"phase": "error"},
                base_path=self.storage_path
            )
        
        return incident_id
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "agents": [
                {"name": "DiagnosticAgent", "status": "online", "capability": "data_collection"},
                {"name": "RemediationAgent", "status": "online", "capability": "fix_generation"},
                {"name": "ValidationAgent", "status": "online", "capability": "risk_assessment"},
                {"name": "ReporterAgent", "status": "online", "capability": "reporting"}
            ],
            "orchestrator": "LangGraph",
            "autonomous": True,
            "collaborative": True
        }
