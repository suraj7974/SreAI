"""FastAPI Main Application"""

from fastapi import FastAPI, HTTPException, Depends, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pathlib import Path
import logging

from app.config import settings
from app.coordinator import IncidentCoordinator
from app.agents_v2.orchestrator import MultiAgentOrchestrator
from app.utils import setup_logging, read_trace

# Setup logging
setup_logging()
logger = logging.getLogger("main")

# Initialize FastAPI app
app = FastAPI(
    title="AI Chaos-Handler",
    description="Autonomous Multi-Agent Incident Response System",
    version="1.0.0"
)

# CORS middleware
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize coordinator (old system)
coordinator = IncidentCoordinator(storage_path=settings.incident_storage_path)

# Initialize multi-agent orchestrator (new system)
multi_agent_orchestrator = MultiAgentOrchestrator(storage_path=settings.incident_storage_path)

# Templates for dashboard
templates = Jinja2Templates(directory="frontend")

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
except RuntimeError:
    logger.warning("Static files directory not found, dashboard may not work")


# Pydantic models
class TargetVM(BaseModel):
    host: str
    port: int = 22
    user: str
    key_path: str


class StartIncidentRequest(BaseModel):
    scenario: str
    target_vm: TargetVM
    options: Optional[Dict[str, Any]] = {}


class IncidentResponse(BaseModel):
    incident_id: str
    status: str


# Auth dependency
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API token"""
    if settings.api_auth_token and credentials.credentials != settings.api_auth_token:
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    return credentials


# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


# Start incident endpoint
@app.post("/start_incident", response_model=IncidentResponse)
async def start_incident(
    request: StartIncidentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Start a new incident response workflow"""
    
    try:
        incident_id = await coordinator.start_incident(
            scenario=request.scenario,
            target_vm=request.target_vm.dict(),
            options=request.options
        )
        
        return IncidentResponse(
            incident_id=incident_id,
            status="started"
        )
    except Exception as e:
        logger.error(f"Failed to start incident: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Start incident with real AI agents
@app.post("/v2/start_incident", response_model=IncidentResponse)
async def start_incident_v2(
    request: StartIncidentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Start incident response with real AI agents (LangGraph multi-agent system)"""
    
    try:
        incident_id = await multi_agent_orchestrator.start_incident(
            scenario=request.scenario,
            target_vm=request.target_vm.dict(),
            options=request.options
        )
        
        return IncidentResponse(
            incident_id=incident_id,
            status="started"
        )
    except Exception as e:
        logger.error(f"Failed to start incident with AI agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get agent status
@app.get("/agents/status")
async def get_agents_status():
    """Get status of all AI agents"""
    
    try:
        status = await multi_agent_orchestrator.get_agent_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get incident status
@app.get("/status/{incident_id}")
async def get_status(
    incident_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Get current incident status and trace"""
    
    # Get incident info
    incident = coordinator.get_incident_status(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Read trace
    trace = read_trace(incident_id, base_path=settings.incident_storage_path)
    
    return {
        "incident_id": incident_id,
        "phase": incident.get("phase"),
        "status": incident.get("status"),
        "trace": trace,
        "scenario": incident.get("scenario")
    }


# Get incident report
@app.get("/report/{incident_id}")
async def get_report(
    incident_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Get incident report"""
    
    report_path = Path(settings.incident_storage_path) / incident_id / "report.md"
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        report_path,
        media_type="text/markdown",
        filename=f"{incident_id}_report.md"
    )


# Get incident PDF report
@app.get("/report/{incident_id}/pdf")
async def get_report_pdf(
    incident_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Get incident PDF report"""
    
    pdf_path = Path(settings.incident_storage_path) / incident_id / "report.pdf"
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF report not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{incident_id}_report.pdf"
    )


# Get incident artifacts
@app.get("/incidents/{incident_id}/artifacts/{artifact_name}")
async def get_artifact(
    incident_id: str,
    artifact_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Get specific incident artifact"""
    
    artifact_path = Path(settings.incident_storage_path) / incident_id / artifact_name
    
    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return FileResponse(artifact_path)


# Dashboard UI
@app.get("/dashboard/{incident_id}")
async def dashboard(
    incident_id: str,
    request: Request
):
    """Serve dashboard UI for an incident"""
    
    # Check if incident exists
    incident = coordinator.get_incident_status(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "incident_id": incident_id,
            "api_base": f"http://{request.url.netloc}"
        }
    )


# Stop incident
@app.post("/stop/{incident_id}")
async def stop_incident(
    incident_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """Stop an active incident and its chaos scripts"""
    
    success = await coordinator.stop_incident(incident_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return {"status": "stopped", "incident_id": incident_id}


# List all incidents
@app.get("/incidents")
async def list_incidents(
    credentials: HTTPAuthorizationCredentials = Depends(verify_token)
):
    """List all incidents"""
    
    incidents_path = Path(settings.incident_storage_path)
    
    if not incidents_path.exists():
        return {"incidents": []}
    
    incidents = []
    for incident_dir in incidents_path.iterdir():
        if incident_dir.is_dir():
            trace = read_trace(incident_dir.name, base_path=settings.incident_storage_path)
            
            incidents.append({
                "incident_id": incident_dir.name,
                "events_count": len(trace),
                "latest_event": trace[-1] if trace else None
            })
    
    return {"incidents": incidents}


# Get VM system metrics (no auth for dashboard polling)
@app.get("/vm/metrics")
async def get_vm_metrics():
    """Get real-time VM system metrics"""
    from app.utils import run_ssh_command
    import asyncio
    
    # Get VM config from settings
    if not settings.vm_host:
        return {"error": "VM not configured"}
    
    try:
        # Collect metrics in parallel
        async def get_cpu():
            cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'"
            out, _, _ = await run_ssh_command(
                settings.vm_host, settings.vm_port, settings.vm_user, 
                settings.vm_key_path, cmd, timeout=5
            )
            return float(out.strip()) if out.strip() else 0.0
        
        async def get_memory():
            cmd = "free | grep Mem | awk '{print ($3/$2) * 100.0}'"
            out, _, _ = await run_ssh_command(
                settings.vm_host, settings.vm_port, settings.vm_user, 
                settings.vm_key_path, cmd, timeout=5
            )
            return float(out.strip()) if out.strip() else 0.0
        
        async def get_disk():
            cmd = "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
            out, _, _ = await run_ssh_command(
                settings.vm_host, settings.vm_port, settings.vm_user, 
                settings.vm_key_path, cmd, timeout=5
            )
            return float(out.strip()) if out.strip() else 0.0
        
        async def get_uptime():
            cmd = "uptime -p"
            out, _, _ = await run_ssh_command(
                settings.vm_host, settings.vm_port, settings.vm_user, 
                settings.vm_key_path, cmd, timeout=5
            )
            return out.strip() if out.strip() else "unknown"
        
        cpu, memory, disk, uptime = await asyncio.gather(
            get_cpu(), get_memory(), get_disk(), get_uptime(),
            return_exceptions=True
        )
        
        return {
            "cpuUsage": cpu if not isinstance(cpu, Exception) else 0.0,
            "memoryUsage": memory if not isinstance(memory, Exception) else 0.0,
            "diskUsage": disk if not isinstance(disk, Exception) else 0.0,
            "uptime": uptime if not isinstance(uptime, Exception) else "unknown",
            "timestamp": logger.handlers[0].formatter.formatTime(logging.LogRecord("", 0, "", 0, "", (), None)) if logger.handlers else ""
        }
    except Exception as e:
        logger.error(f"Failed to get VM metrics: {e}")
        return {"error": str(e)}


# Get real-time VM logs and incidents (no auth for dashboard polling)
@app.get("/vm/logs")
async def get_vm_logs():
    """Get real-time VM logs and parse for incidents"""
    from app.utils import run_ssh_command
    import re
    from datetime import datetime
    
    # Get VM config from settings
    if not settings.vm_host:
        return {"error": "VM not configured"}
    
    try:
        # Get recent logs with errors and warnings
        cmd = """
        sudo journalctl -n 100 --no-pager --output=json 2>/dev/null | jq -r '. | select(.PRIORITY <= "4") | "[\(.PRIORITY)][\(.__REALTIME_TIMESTAMP)][\(.SYSLOG_IDENTIFIER // "system")] \(.MESSAGE)"' 2>/dev/null || \
        sudo journalctl -n 100 --no-pager | grep -iE '(error|warn|fail|critical|alert)' | tail -20
        """
        
        stdout, stderr, exit_code = await run_ssh_command(
            settings.vm_host, settings.vm_port, settings.vm_user, 
            settings.vm_key_path, cmd, timeout=10
        )
        
        if not stdout or exit_code != 0:
            return {"incidents": [], "message": "No recent incidents found"}
        
        # Parse logs into incidents
        incidents = []
        lines = stdout.strip().split('\n')
        
        for line in lines[-20:]:  # Last 20 log entries
            if not line.strip():
                continue
                
            # Determine severity
            severity = 'info'
            if re.search(r'(critical|alert|emerg)', line, re.I):
                severity = 'error'
            elif re.search(r'(error|err)', line, re.I):
                severity = 'error'
            elif re.search(r'(warn|warning)', line, re.I):
                severity = 'warning'
            elif re.search(r'(fail|failure)', line, re.I):
                severity = 'error'
            else:
                severity = 'info'
            
            # Extract service name if possible
            service_match = re.search(r'\[([^\]]+)\].*\[([^\]]+)\]', line)
            service = service_match.group(2) if service_match and service_match.lastindex >= 2 else "system"
            
            # Clean message
            message = re.sub(r'\[\d+\]\[\d+\]', '', line).strip()
            message = re.sub(r'\[.*?\]', '', message, count=1).strip()
            
            incidents.append({
                "type": severity,
                "service": service,
                "message": message[:200],  # Limit message length
                "timestamp": datetime.now().isoformat()
            })
        
        return {"incidents": incidents}
        
    except Exception as e:
        logger.error(f"Failed to get VM logs: {e}")
        return {"error": str(e), "incidents": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
