"""Simple auto-monitoring service that always runs in background"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from app.utils import run_ssh_command
from app.config import settings

logger = logging.getLogger(__name__)


class AutoMonitor:
    """Automatically monitors VM and triggers incidents when chaos detected"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.running = False
        self.check_interval = 30  # Check every 30 seconds
        self.last_incident_time = None
        self.cooldown = 180  # 3 minutes cooldown between incidents
    
    async def check_vm(self) -> Dict[str, Any]:
        """Check VM health"""
        
        if not settings.vm_host:
            return {"healthy": True}
        
        try:
            # Check CPU
            cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'"
            cpu_out, _, _ = await run_ssh_command(
                settings.vm_host, settings.vm_port, settings.vm_user,
                settings.vm_key_path, cpu_cmd, timeout=10
            )
            cpu = float(cpu_out.strip()) if cpu_out.strip() else 0.0
            
            # Check memory
            mem_cmd = "free | grep Mem | awk '{print ($3/$2) * 100.0}'"
            mem_out, _, _ = await run_ssh_command(
                settings.vm_host, settings.vm_port, settings.vm_user,
                settings.vm_key_path, mem_cmd, timeout=10
            )
            mem = float(mem_out.strip()) if mem_out.strip() else 0.0
            
            # Check errors
            err_cmd = "sudo journalctl -n 50 --no-pager | grep -iE '(error|critical|fail)' | wc -l"
            err_out, _, _ = await run_ssh_command(
                settings.vm_host, settings.vm_port, settings.vm_user,
                settings.vm_key_path, err_cmd, timeout=10
            )
            errors = int(err_out.strip()) if err_out.strip() else 0
            
            # Detect chaos
            if cpu > 80:
                return {"healthy": False, "type": "cpu_spike", "value": cpu}
            if mem > 85:
                return {"healthy": False, "type": "memory_leak", "value": mem}
            if errors > 10:
                return {"healthy": False, "type": "error_logs", "value": errors}
            
            return {"healthy": True, "cpu": cpu, "mem": mem, "errors": errors}
            
        except Exception as e:
            logger.debug(f"Health check failed: {e}")
            return {"healthy": True}
    
    async def trigger_incident(self, chaos_type: str):
        """Trigger incident response"""
        
        # Check cooldown
        if self.last_incident_time:
            elapsed = (datetime.now() - self.last_incident_time).total_seconds()
            if elapsed < self.cooldown:
                logger.debug(f"Cooldown active ({int(elapsed)}s/{self.cooldown}s)")
                return
        
        logger.warning(f"🚨 Chaos detected! Auto-triggering incident: {chaos_type}")
        
        try:
            incident_id = await self.orchestrator.start_incident(
                scenario=chaos_type,
                target_vm={
                    "host": settings.vm_host,
                    "port": settings.vm_port,
                    "user": settings.vm_user,
                    "key_path": settings.vm_key_path
                }
            )
            logger.info(f"✅ Auto-incident created: {incident_id}")
            self.last_incident_time = datetime.now()
        except Exception as e:
            logger.error(f"Failed to trigger incident: {e}")
    
    async def monitor_loop(self):
        """Main monitoring loop - runs forever"""
        
        self.running = True
        logger.info(f"🔍 Auto-Monitor started (checking every {self.check_interval}s)")
        
        while self.running:
            try:
                health = await self.check_vm()
                
                if not health["healthy"]:
                    await self.trigger_incident(health["type"])
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            
            await asyncio.sleep(self.check_interval)
    
    def start(self):
        """Start monitoring"""
        if not self.running:
            asyncio.create_task(self.monitor_loop())
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Auto-Monitor stopped")
