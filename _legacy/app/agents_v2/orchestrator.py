"""Multi-Agent Orchestrator - Now uses Complete Agent for 4-file output"""

import logging
from typing import Dict, Any
from app.agents_v2.complete_agent import CompleteIncidentAgent

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Simplified orchestrator that uses CompleteIncidentAgent.
    Generates only 4 files: logs.txt, metrics.json, diagnostic_analysis.md, fix_commands.sh
    """
    
    def __init__(self, storage_path: str = "./incidents"):
        self.storage_path = storage_path
        self.agent = CompleteIncidentAgent()
        logger.info("Multi-Agent Orchestrator initialized with Complete Agent")
    
    async def start_incident(
        self,
        scenario: str,
        target_vm: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> str:
        """Start incident response - generates only 4 files"""
        logger.info(f"Starting incident response for scenario: {scenario}")
        
        try:
            incident_id = await self.agent.handle_incident(
                scenario=scenario,
                target_vm=target_vm,
                storage_path=self.storage_path
            )
            return incident_id
        except Exception as e:
            logger.error(f"Incident response failed: {e}", exc_info=True)
            raise
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "agents": [
                {"name": "CompleteIncidentAgent", "status": "online", "capability": "full_incident_response"}
            ],
            "output_files": ["logs.txt", "metrics.json", "diagnostic_analysis.md", "fix_commands.sh"],
            "autonomous": True
        }
