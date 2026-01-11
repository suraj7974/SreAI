"""
SRE Agent - Shared State Models

Defines the state schema that flows through the agent graph.
"""

from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class Severity(str, Enum):
    """Alert/Incident severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident lifecycle status"""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    DIAGNOSED = "diagnosed"
    AWAITING_APPROVAL = "awaiting_approval"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    FAILED = "failed"


class Alert(BaseModel):
    """Represents a Prometheus/Alertmanager alert"""

    alert_name: str
    instance: str
    severity: Severity
    category: str
    summary: str
    description: str
    value: Optional[float] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    starts_at: datetime = Field(default_factory=datetime.utcnow)


class Metric(BaseModel):
    """A single metric data point"""

    name: str
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DiagnosticResult(BaseModel):
    """Result from diagnostic analysis"""

    root_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    related_metrics: List[Metric] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class RemediationAction(BaseModel):
    """A proposed remediation action"""

    action_id: str
    description: str
    command: str
    risk_level: Literal["low", "medium", "high"]
    requires_approval: bool = True
    estimated_impact: str
    rollback_command: Optional[str] = None


class RemediationPlan(BaseModel):
    """Complete remediation plan"""

    plan_id: str
    incident_id: str
    actions: List[RemediationAction] = Field(default_factory=list)
    estimated_resolution_time: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class AgentThought(BaseModel):
    """Captures agent reasoning for transparency"""

    agent_name: str
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# LangGraph State Definition
# =============================================================================


class SREAgentState(TypedDict, total=False):
    """
    Shared state that flows through the SRE Agent graph.

    This state is passed between all agents and accumulates information
    as the incident progresses through detection -> diagnosis -> remediation.
    """

    # --------------------------------------------------------------------------
    # Incident Information
    # --------------------------------------------------------------------------
    incident_id: str
    status: IncidentStatus
    severity: Severity
    created_at: str
    updated_at: str

    # --------------------------------------------------------------------------
    # Alert & Trigger Information
    # --------------------------------------------------------------------------
    alerts: List[Dict[str, Any]]  # Raw alerts that triggered the incident
    trigger_source: str  # "prometheus", "alertmanager", "manual", "monitoring"

    # --------------------------------------------------------------------------
    # Target Information
    # --------------------------------------------------------------------------
    target_instance: str  # IP/hostname of affected system
    target_labels: Dict[str, str]  # Labels from Prometheus

    # --------------------------------------------------------------------------
    # Metrics & Data
    # --------------------------------------------------------------------------
    metrics: Dict[str, Any]  # Collected metrics
    logs: str  # Collected logs

    # --------------------------------------------------------------------------
    # Diagnostic Information
    # --------------------------------------------------------------------------
    diagnosis: Dict[str, Any]  # DiagnosticResult as dict
    diagnostic_queries_run: List[str]  # PromQL queries executed

    # --------------------------------------------------------------------------
    # Remediation Information
    # --------------------------------------------------------------------------
    remediation_plan: Dict[str, Any]  # RemediationPlan as dict
    remediation_results: List[Dict[str, Any]]  # Results of executed actions

    # --------------------------------------------------------------------------
    # Human-in-the-Loop
    # --------------------------------------------------------------------------
    awaiting_approval: bool
    approval_request_id: Optional[str]
    approval_timeout: Optional[str]
    human_feedback: Optional[str]

    # --------------------------------------------------------------------------
    # Agent Reasoning (for transparency/debugging)
    # --------------------------------------------------------------------------
    agent_thoughts: List[Dict[str, Any]]  # List of AgentThought dicts
    current_agent: str

    # --------------------------------------------------------------------------
    # Control Flow
    # --------------------------------------------------------------------------
    next_agent: str  # Which agent should run next
    should_continue: bool  # Whether to continue the agent loop
    error: Optional[str]  # Error message if something failed
    iteration_count: int  # Track iterations to prevent infinite loops


def create_initial_state(
    incident_id: str,
    target_instance: str,
    alerts: List[Dict[str, Any]] = None,
    trigger_source: str = "manual",
) -> SREAgentState:
    """Create initial state for a new incident"""
    return SREAgentState(
        incident_id=incident_id,
        status=IncidentStatus.DETECTED,
        severity=Severity.WARNING,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
        alerts=alerts or [],
        trigger_source=trigger_source,
        target_instance=target_instance,
        target_labels={},
        metrics={},
        logs="",
        diagnosis={},
        diagnostic_queries_run=[],
        remediation_plan={},
        remediation_results=[],
        awaiting_approval=False,
        approval_request_id=None,
        approval_timeout=None,
        human_feedback=None,
        agent_thoughts=[],
        current_agent="",
        next_agent="monitor",
        should_continue=True,
        error=None,
        iteration_count=0,
    )
