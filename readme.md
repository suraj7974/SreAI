# SRE Agent
**Autonomous Multi-Agent Incident Response System**

A true agentic SRE system built with LangGraph that autonomously monitors infrastructure, diagnoses issues, and recommends fixes with human-in-the-loop approval.

---

## Key Features

- **True Agent Architecture**: LangGraph-based ReAct agents that reason, plan, and execute autonomously
- **Multi-Agent System**: Specialized agents for monitoring, diagnosis, and remediation
- **Prometheus Integration**: Pull-based metrics collection from Node Exporter
- **Grafana Dashboards**: Pre-configured visualization for infrastructure metrics
- **Human-in-the-Loop**: Remediation actions require explicit approval before execution
- **Alertmanager Webhooks**: Automatic incident creation from Prometheus alerts

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SRE Agent System                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐    ┌─────────────────┐    ┌───────────────────┐          │
│   │   Monitor   │───▶│   Diagnostic    │───▶│   Remediation     │          │
│   │   Agent     │    │   Agent         │    │   Agent           │          │
│   └─────────────┘    └─────────────────┘    └───────────────────┘          │
│         │                   │                        │                      │
│    Query Prometheus    Analyze root cause    Generate fix plan             │
│    Detect anomalies    Gather evidence       ──▶ [HUMAN APPROVAL]          │
│    Classify severity   Make diagnosis             │                        │
│         │                   │               Execute fixes                   │
│         ▼                   ▼                      ▼                        │
│   (continue/escalate)  (continue/end)          (end)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
              ┌─────▼─────┐               ┌───────▼───────┐
              │ Prometheus │               │   Grafana     │
              │  (Metrics) │               │ (Dashboards)  │
              └─────┬─────┘               └───────────────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
    ┌────▼────┐ ┌───▼───┐ ┌───▼───┐
    │  Node   │ │ Node  │ │ Node  │
    │Exporter │ │Exporter│ │Exporter│
    │ (VM 1)  │ │ (VM 2) │ │ (VM N) │
    └─────────┘ └───────┘ └───────┘
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Google Gemini API key

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repo-url>
cd SreAI

# Copy and edit environment variables
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY and other settings
```

### 2. Start the Stack

```bash
# Start all services (Prometheus, Grafana, Alertmanager, SRE Agent)
docker-compose up -d

# View logs
docker-compose logs -f sre-agent
```

### 3. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| SRE Agent API | http://localhost:8000 | Bearer token from .env |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |

### 4. Add Target VMs

Install Node Exporter on each VM you want to monitor:

```bash
# On target VM
./scripts/install_node_exporter.sh
```

Then add the VM to Prometheus (`monitoring/prometheus/prometheus.yml`):

```yaml
scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets:
        - 'your-vm-ip:9100'
```

Reload Prometheus:
```bash
docker-compose exec prometheus kill -HUP 1
```

---

## API Reference

### Health Check
```bash
GET /health
```

### Start Monitoring
```bash
POST /incidents/start
Content-Type: application/json

{
  "target": "192.168.1.10:9100"  # Optional, monitors all targets if not specified
}
```

### Get Incident Status
```bash
GET /incidents/{incident_id}
```

### List All Incidents
```bash
GET /incidents
```

### Approve Remediation
```bash
POST /incidents/{incident_id}/approve
Content-Type: application/json

{
  "approved": true,
  "approver": "engineer@example.com"
}
```

### Reject Remediation
```bash
POST /incidents/{incident_id}/approve
Content-Type: application/json

{
  "approved": false,
  "reason": "Fix is too risky for production"
}
```

### Alertmanager Webhook (receives alerts automatically)
```bash
POST /webhooks/alertmanager
```

---

## Project Structure

```
DevAI/
├── sre_agent/                    # New agent system
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── state.py                  # LangGraph state schema
│   ├── graph.py                  # LangGraph supervisor graph
│   ├── api.py                    # FastAPI endpoints
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── monitor_agent.py      # Prometheus monitoring agent
│   │   ├── diagnostic_agent.py   # Root cause analysis agent
│   │   └── remediation_agent.py  # Fix generation agent
│   └── tools/
│       └── __init__.py           # Shared tools (Prometheus, SSH, Slack)
│
├── monitoring/                   # Monitoring infrastructure
│   ├── prometheus/
│   │   ├── prometheus.yml        # Prometheus config
│   │   └── alerts.yml            # Alert rules
│   ├── alertmanager/
│   │   └── alertmanager.yml      # Alertmanager config
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/
│       │   └── dashboards/
│       └── dashboards/
│           └── sre-dashboard.json
│
├── scripts/
│   └── install_node_exporter.sh  # VM setup script
│
├── docker-compose.yml            # Full stack deployment
├── Dockerfile                    # SRE Agent container
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
│
├── app/                          # [LEGACY] Old manual system
├── frontend/                     # [LEGACY] Old React dashboard
└── chaos-scripts/                # Chaos engineering scripts
```

---

## Agent Details

### Monitor Agent
- **Purpose**: Continuously monitor infrastructure health
- **Tools**: `query_prometheus`, `get_alert_status`
- **Behavior**: 
  - Queries Prometheus for CPU, memory, disk, network metrics
  - Detects anomalies based on configured thresholds
  - Classifies severity (info, warning, critical)
  - Decides whether to escalate to Diagnostic Agent

### Diagnostic Agent
- **Purpose**: Perform root cause analysis
- **Tools**: `query_prometheus`, `run_ssh_command`, `get_process_list`
- **Behavior**:
  - Gathers additional evidence (logs, process info, historical metrics)
  - Correlates symptoms to identify root cause
  - Generates diagnosis with confidence score
  - Escalates to Remediation Agent if fix is needed

### Remediation Agent
- **Purpose**: Generate and execute fixes (with approval)
- **Tools**: `run_ssh_command`, `send_notification`
- **Behavior**:
  - Creates remediation plan with specific commands
  - Assesses risk and potential impact
  - **Waits for human approval** before execution
  - Executes approved fixes and verifies success

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API key | (required) |
| `GOOGLE_MODEL` | Model to use | gemini-2.0-flash-exp |
| `PROMETHEUS_URL` | Prometheus server | http://prometheus:9090 |
| `GRAFANA_URL` | Grafana server | http://grafana:3000 |
| `REQUIRE_HUMAN_APPROVAL` | Require approval for fixes | true |
| `CPU_THRESHOLD_CRITICAL` | CPU critical threshold (%) | 90 |
| `MEMORY_THRESHOLD_CRITICAL` | Memory critical threshold (%) | 85 |
| `DISK_THRESHOLD_CRITICAL` | Disk critical threshold (%) | 85 |

### Alert Rules

Pre-configured alerts in `monitoring/prometheus/alerts.yml`:

- **HighCPUUsage**: CPU > 90% for 5 minutes
- **HighMemoryUsage**: Memory > 85% for 5 minutes  
- **DiskSpaceLow**: Disk > 85% full
- **InstanceDown**: Target unreachable for 1 minute
- **HighNetworkErrors**: Network errors detected

---

## Development

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the agent
cd sre_agent
uvicorn api:app --reload --port 8000
```

### Running Tests

```bash
pytest tests/ -v
```

---

## Human-in-the-Loop Flow

1. **Alert Fires** → Alertmanager sends webhook to SRE Agent
2. **Monitor Agent** → Validates alert, gathers current metrics
3. **Diagnostic Agent** → Analyzes root cause, creates diagnosis
4. **Remediation Agent** → Generates fix plan
5. **Graph Interrupts** → Waits at `human_approval` node
6. **Human Reviews** → Approves or rejects via API/Slack
7. **If Approved** → Remediation Agent executes fixes
8. **Verification** → Agent confirms fix was successful

---

## Migrating from Legacy System

The legacy system in `app/` used:
- Manual SSH-based metric collection
- Hardcoded workflow pipelines
- AI as text generator only (not decision maker)

The new system in `sre_agent/` uses:
- Prometheus pull-based metrics
- LangGraph ReAct agents with autonomous reasoning
- Human-in-the-loop for safety

To migrate:
1. Deploy new stack with `docker-compose up`
2. Install Node Exporter on target VMs
3. Configure Prometheus targets
4. Update integrations to use new API endpoints
5. (Optional) Archive `app/` and `frontend/` directories

---

## Safety & Security

- **Human Approval Required**: All remediation actions require explicit approval
- **SSH Key Security**: Store SSH keys securely, never commit to repo
- **API Authentication**: All endpoints protected with Bearer token
- **Audit Trail**: All actions logged with timestamps and approvers
- **Dry-Run Mode**: Test fixes before applying to production

---

## Troubleshooting

### Prometheus can't scrape targets
```bash
# Check target is reachable
curl http://target-ip:9100/metrics

# Check Prometheus targets page
open http://localhost:9090/targets
```

### Agent not receiving alerts
```bash
# Test Alertmanager webhook
curl -X POST http://localhost:8000/webhooks/alertmanager \
  -H "Content-Type: application/json" \
  -d '{"alerts": [{"labels": {"alertname": "test"}}]}'
```

### Graph stuck at human_approval
```bash
# List pending incidents
curl http://localhost:8000/incidents?status=pending_approval

# Approve incident
curl -X POST http://localhost:8000/incidents/{id}/approve \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'
```
