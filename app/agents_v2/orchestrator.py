"""Multi-Agent Orchestrator using LangGraph"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from app.agents_v2 import AgentState
from app.agents_v2.simplified_diagnostic_agent import SimplifiedDiagnosticAgent
from app.utils import generate_incident_id, ensure_incident_dir, append_trace_event

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Orchestrates autonomous AI agents using LangGraph.
    Agents collaborate, make decisions, and adapt based on their findings.
    
    Using simplified agents to avoid Gemini tool calling issues.
    """
    
    def __init__(self, storage_path: str = "./incidents"):
        self.storage_path = storage_path
        
        # Initialize simplified agent (others to be added)
        self.diagnostic_agent = SimplifiedDiagnosticAgent()
        
        # Build agent graph
        self.workflow = self._build_workflow()
        
        logger.info("Multi-Agent Orchestrator initialized (simplified version)")
    
    def _build_workflow(self) -> StateGraph:
        """Build the agent collaboration workflow"""
        
        workflow = StateGraph(AgentState)
        
        # Add agent node
        workflow.add_node("diagnostic", self.diagnostic_agent)
        
        # For now, just diagnostic agent
        workflow.set_entry_point("diagnostic")
        workflow.set_finish_point("diagnostic")
        
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
                {"name": "DiagnosticAgent", "status": "online", "capability": "data_collection"}
            ],
            "orchestrator": "LangGraph",
            "autonomous": True,
            "collaborative": True,
            "note": "Simplified version - full multi-agent system coming soon"
        }
