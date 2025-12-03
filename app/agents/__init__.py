"""Base Agent class for all AI Chaos Handler agents"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import logging


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, incident_id: str, config: Dict[str, Any]):
        self.incident_id = incident_id
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.start_time = None
        self.end_time = None
    
    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """Execute the agent's main logic. Must be implemented by subclasses."""
        pass
    
    def _start_timer(self):
        """Start timing the agent execution"""
        self.start_time = datetime.utcnow()
    
    def _end_timer(self):
        """End timing the agent execution"""
        self.end_time = datetime.utcnow()
    
    def _get_duration_ms(self) -> int:
        """Get execution duration in milliseconds"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() * 1000)
        return 0
    
    async def execute(self) -> Dict[str, Any]:
        """Wrapper that times and logs agent execution"""
        self._start_timer()
        self.logger.info(f"Starting {self.__class__.__name__} for incident {self.incident_id}")
        
        try:
            result = await self.run()
            self._end_timer()
            
            result["duration_ms"] = self._get_duration_ms()
            result["status"] = "success"
            
            self.logger.info(f"Completed {self.__class__.__name__} in {result['duration_ms']}ms")
            return result
            
        except Exception as e:
            self._end_timer()
            self.logger.error(f"Error in {self.__class__.__name__}: {str(e)}", exc_info=True)
            
            return {
                "status": "error",
                "error": str(e),
                "duration_ms": self._get_duration_ms()
            }
