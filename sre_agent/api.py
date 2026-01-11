"""
SRE Agent - FastAPI Application

Main API for interacting with the SRE Agent system.
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from sre_agent.config import settings
from sre_agent.graph import orchestrator
from sre_agent.tools import prometheus

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Prometheus Metrics
# =============================================================================

INCIDENTS_CREATED = Counter(
    "sre_agent_incidents_created_total",
    "Total number of incidents created",
    ["trigger_source", "severity"],
)

INCIDENTS_RESOLVED = Counter(
    "sre_agent_incidents_resolved_total",
    "Total number of incidents resolved",
    ["resolution_type"],
)

AGENT_DURATION = Histogram(
    "sre_agent_processing_seconds", "Time spent processing incidents", ["agent_name"]
)


# =============================================================================
# Request/Response Models
# =============================================================================


class StartIncidentRequest(BaseModel):
    target_instance: str = Field(..., description="Target VM instance (IP:port)")
    alerts: Optional[List[dict]] = Field(
        default=None, description="Alertmanager alerts"
    )
    trigger_source: str = Field(default="manual", description="Source of the trigger")


class StartIncidentResponse(BaseModel):
    incident_id: str
    status: str
    message: str


class ApprovalRequest(BaseModel):
    approved_by: str = Field(..., description="Name/ID of approver")
    feedback: Optional[str] = Field(default=None, description="Optional feedback")


class RejectionRequest(BaseModel):
    rejected_by: str = Field(..., description="Name/ID of rejector")
    reason: Optional[str] = Field(default=None, description="Reason for rejection")


class IncidentStateResponse(BaseModel):
    incident_id: str
    status: str
    severity: str
    target_instance: str
    created_at: str
    updated_at: str
    diagnosis: Optional[dict] = None
    remediation_plan: Optional[dict] = None
    awaiting_approval: bool = False
    agent_thoughts: List[dict] = []


class AlertmanagerWebhook(BaseModel):
    """Alertmanager webhook payload"""

    version: str
    groupKey: str
    status: str
    receiver: str
    alerts: List[dict]


# =============================================================================
# Auth Dependency
# =============================================================================


async def verify_token(authorization: str = Header(None)):
    """Verify API token"""
    if settings.api_auth_token == "dev-token-change-in-production":
        return True  # Skip auth in dev mode

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization[7:]
    if token != settings.api_auth_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    return True


# =============================================================================
# Background Monitoring Task
# =============================================================================

monitoring_task = None


async def background_monitor():
    """Background task that periodically checks all targets"""
    logger.info("Starting background monitoring loop")

    while True:
        try:
            # Check for active alerts
            alerts_response = await prometheus.get_alerts()
            firing_alerts = [
                a
                for a in alerts_response.get("data", {}).get("alerts", [])
                if a.get("state") == "firing"
            ]

            if firing_alerts:
                logger.info(f"Found {len(firing_alerts)} firing alerts")
                # Group alerts by instance
                alerts_by_instance = {}
                for alert in firing_alerts:
                    instance = alert.get("labels", {}).get("instance", "unknown")
                    if instance not in alerts_by_instance:
                        alerts_by_instance[instance] = []
                    alerts_by_instance[instance].append(alert)

                # Start incidents for each instance with alerts
                for instance, instance_alerts in alerts_by_instance.items():
                    # Check if we already have an active incident for this instance
                    existing = [
                        inc
                        for inc in orchestrator.active_incidents.values()
                        if inc.get("target_instance") == instance
                        and inc.get("status") not in ["resolved", "failed"]
                    ]

                    if not existing:
                        logger.info(
                            f"Starting incident for {instance} with {len(instance_alerts)} alerts"
                        )
                        await orchestrator.start_incident(
                            target_instance=instance,
                            alerts=instance_alerts,
                            trigger_source="prometheus",
                        )

        except Exception as e:
            logger.error(f"Background monitor error: {e}")

        await asyncio.sleep(settings.monitoring_interval)


# =============================================================================
# Lifespan
# =============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global monitoring_task

    logger.info("SRE Agent starting up...")

    # Start background monitoring
    monitoring_task = asyncio.create_task(background_monitor())

    yield

    # Cleanup
    if monitoring_task:
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

    logger.info("SRE Agent shut down")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="SRE Agent API",
    description="Agentic SRE system for monitoring, diagnosis, and remediation",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Endpoints
# =============================================================================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "prometheus_url": settings.prometheus_url,
        "active_incidents": len(orchestrator.active_incidents),
    }


@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/incidents", response_model=StartIncidentResponse)
async def start_incident(
    request: StartIncidentRequest, _: bool = Depends(verify_token)
):
    """Start a new incident investigation"""
    try:
        incident_id = await orchestrator.start_incident(
            target_instance=request.target_instance,
            alerts=request.alerts,
            trigger_source=request.trigger_source,
        )

        state = await orchestrator.get_incident_state(incident_id)

        INCIDENTS_CREATED.labels(
            trigger_source=request.trigger_source,
            severity=state.get("severity", "unknown") if state else "unknown",
        ).inc()

        return StartIncidentResponse(
            incident_id=incident_id,
            status=state.get("status", "unknown") if state else "unknown",
            message="Incident created and investigation started",
        )

    except Exception as e:
        logger.error(f"Failed to start incident: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/incidents/{incident_id}", response_model=IncidentStateResponse)
async def get_incident(incident_id: str, _: bool = Depends(verify_token)):
    """Get incident details"""
    state = await orchestrator.get_incident_state(incident_id)

    if not state:
        raise HTTPException(status_code=404, detail="Incident not found")

    return IncidentStateResponse(
        incident_id=state.get("incident_id", incident_id),
        status=state.get("status", "unknown"),
        severity=state.get("severity", "unknown"),
        target_instance=state.get("target_instance", ""),
        created_at=state.get("created_at", ""),
        updated_at=state.get("updated_at", ""),
        diagnosis=state.get("diagnosis"),
        remediation_plan=state.get("remediation_plan"),
        awaiting_approval=state.get("awaiting_approval", False),
        agent_thoughts=state.get("agent_thoughts", []),
    )


@app.get("/incidents")
async def list_incidents(_: bool = Depends(verify_token)):
    """List all incidents"""
    incidents = []
    for incident_id, state in orchestrator.active_incidents.items():
        incidents.append(
            {
                "incident_id": incident_id,
                "status": state.get("status"),
                "severity": state.get("severity"),
                "target_instance": state.get("target_instance"),
                "created_at": state.get("created_at"),
                "awaiting_approval": state.get("awaiting_approval", False),
            }
        )

    return {"incidents": incidents, "total": len(incidents)}


@app.get("/approvals/pending")
async def get_pending_approvals(_: bool = Depends(verify_token)):
    """Get incidents awaiting approval"""
    pending = await orchestrator.get_pending_approvals()
    return {"pending_approvals": pending, "total": len(pending)}


@app.post("/incidents/{incident_id}/approve")
async def approve_remediation(
    incident_id: str, request: ApprovalRequest, _: bool = Depends(verify_token)
):
    """Approve a remediation plan"""
    try:
        result = await orchestrator.approve_remediation(
            incident_id=incident_id,
            approved_by=request.approved_by,
            feedback=request.feedback,
        )

        return {
            "incident_id": incident_id,
            "status": result.get("status"),
            "message": "Remediation approved and execution started",
            "results": result.get("remediation_results", []),
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to approve remediation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidents/{incident_id}/reject")
async def reject_remediation(
    incident_id: str, request: RejectionRequest, _: bool = Depends(verify_token)
):
    """Reject a remediation plan"""
    try:
        result = await orchestrator.reject_remediation(
            incident_id=incident_id,
            rejected_by=request.rejected_by,
            reason=request.reason,
        )

        return {
            "incident_id": incident_id,
            "status": result.get("status"),
            "message": "Remediation rejected",
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to reject remediation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/alertmanager")
async def alertmanager_webhook(
    payload: AlertmanagerWebhook, background_tasks: BackgroundTasks
):
    """
    Receive alerts from Alertmanager.

    This endpoint is called by Alertmanager when alerts fire or resolve.
    """
    logger.info(
        f"Received alertmanager webhook: status={payload.status}, alerts={len(payload.alerts)}"
    )

    if payload.status == "firing":
        # Group alerts by instance
        alerts_by_instance = {}
        for alert in payload.alerts:
            instance = alert.get("labels", {}).get("instance", "unknown")
            if instance not in alerts_by_instance:
                alerts_by_instance[instance] = []
            alerts_by_instance[instance].append(alert)

        # Start incidents for each instance
        for instance, alerts in alerts_by_instance.items():
            # Check for existing active incident
            existing = any(
                inc.get("target_instance") == instance
                and inc.get("status") not in ["resolved", "failed"]
                for inc in orchestrator.active_incidents.values()
            )

            if not existing:
                background_tasks.add_task(
                    orchestrator.start_incident,
                    target_instance=instance,
                    alerts=alerts,
                    trigger_source="alertmanager",
                )

    return {"status": "received", "alerts_count": len(payload.alerts)}


@app.get("/prometheus/alerts")
async def get_prometheus_alerts(_: bool = Depends(verify_token)):
    """Get current alerts from Prometheus"""
    try:
        result = await prometheus.get_alerts()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prometheus/targets")
async def get_prometheus_targets(_: bool = Depends(verify_token)):
    """Get Prometheus scrape targets"""
    try:
        result = await prometheus.get_targets()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prometheus/query")
async def query_prometheus(query: str, _: bool = Depends(verify_token)):
    """Execute a PromQL query"""
    try:
        result = await prometheus.query(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "sre_agent.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
