# AI Chaos-Handler Usage Guide

Complete guide to using the AI Chaos-Handler system.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-chaos-handler

# Run the quick start script
./start.sh
```

The script will:
- Create a Python virtual environment
- Install all dependencies
- Build the frontend
- Start the FastAPI server

### 2. Configuration

Edit `.env` file with your settings:

```bash
# SSH Configuration (required)
AI_CHAOS_SSH_KEY_PATH=/path/to/your/private/key
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=your-droplet-ip
AI_CHAOS_SSH_PORT=22

# API Security
API_AUTH_TOKEN=your-secret-token

# Optional
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 3. Provision Target VM

Follow the [DigitalOcean Setup Guide](vm_provisioning/digitalocean-setup.md) to:
1. Create a droplet
2. Install dependencies
3. Deploy chaos scripts
4. Setup metrics endpoint

### 4. Trigger Your First Incident

Using curl:

```bash
curl -X POST http://localhost:8000/start_incident \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "cpu_spike",
    "target_vm": {
      "host": "your-droplet-ip",
      "port": 22,
      "user": "sre-demo",
      "key_path": "/path/to/key"
    },
    "options": {
      "trigger_chaos": true,
      "duration": 60
    }
  }'
```

Response:
```json
{
  "incident_id": "inc-20241202-100000",
  "status": "started"
}
```

### 5. Monitor in Dashboard

Open your browser:
```
http://localhost:8000/dashboard/inc-20241202-100000
```

The dashboard will show:
- Real-time agent trace
- Evidence and artifacts
- Metrics anomalies
- Fix suggestions

### 6. Review the Report

Download the report:
```bash
curl -X GET http://localhost:8000/report/inc-20241202-100000 \
  -H "Authorization: Bearer your-secret-token" \
  -o report.md
```

## Available Scenarios

### 1. CPU Spike

Triggers high CPU usage using stress-ng or shell loops.

```json
{
  "scenario": "cpu_spike",
  "options": {
    "trigger_chaos": true,
    "duration": 60
  }
}
```

### 2. Memory Leak

Allocates memory until target is reached.

```json
{
  "scenario": "memory_leak",
  "options": {
    "trigger_chaos": true,
    "target_mb": 2048,
    "duration": 60
  }
}
```

### 3. Disk Fill

Fills disk space with dummy files.

```json
{
  "scenario": "disk_fill",
  "options": {
    "trigger_chaos": true,
    "size_mb": 5000
  }
}
```

### 4. Network Latency

Adds network delay and packet loss.

```json
{
  "scenario": "net_latency",
  "options": {
    "trigger_chaos": true,
    "interface": "eth0",
    "delay_ms": 100,
    "loss_pct": 5
  }
}
```

### 5. Service Kill

Stops a systemd service.

```json
{
  "scenario": "service_kill",
  "options": {
    "trigger_chaos": true,
    "service_name": "nginx"
  }
}
```

### 6. DB Connection Exhaustion

Opens many database connections.

```json
{
  "scenario": "db_conn_exhaust",
  "options": {
    "trigger_chaos": true,
    "clients": 50
  }
}
```

## API Reference

### POST /start_incident

Start a new incident.

**Request:**
```json
{
  "scenario": "cpu_spike",
  "target_vm": {
    "host": "203.0.113.10",
    "port": 22,
    "user": "sre-demo",
    "key_path": "/path/to/key"
  },
  "options": {
    "trigger_chaos": true,
    "duration": 60
  }
}
```

**Response:**
```json
{
  "incident_id": "inc-20241202-100000",
  "status": "started"
}
```

### GET /status/{incident_id}

Get incident status and trace.

**Response:**
```json
{
  "incident_id": "inc-20241202-100000",
  "phase": "metrics_collection",
  "status": "running",
  "scenario": "cpu_spike",
  "trace": [...]
}
```

### GET /report/{incident_id}

Download markdown report.

### GET /report/{incident_id}/pdf

Download PDF report (if available).

### GET /incidents/{incident_id}/artifacts/{artifact_name}

Download specific artifact (trace.json, fix.sh, etc).

### POST /stop/{incident_id}

Stop incident and chaos scripts.

### GET /incidents

List all incidents.

### GET /health

Health check endpoint.

## Agent Workflow

The system runs agents in sequence:

1. **Coordinator**: Initializes incident, triggers chaos
2. **LogAgent**: Collects system logs via SSH
3. **MetricsAgent**: Gathers metrics (CPU, memory, disk, load)
4. **FixerAgent**: Analyzes evidence and proposes fixes
5. **TesterAgent**: Assesses risk of proposed fixes
6. **ReporterAgent**: Generates final report and summary

Each agent appends events to `trace.json` with:
- Timestamp
- Agent name
- Event type (diagnosis, evidence, suggestion, test, report)
- Content
- Confidence score
- Metadata

## Best Practices

### Safety

1. **Never run on production** - Use dedicated test VMs only
2. **Create snapshots** - Before running chaos experiments
3. **Review fixes** - Always review `fix.sh` before executing
4. **Monitor actively** - Watch the dashboard during incidents
5. **Set limits** - Use short durations for chaos scripts

### Security

1. **Protect SSH keys** - Use proper file permissions (600)
2. **Rotate tokens** - Change API_AUTH_TOKEN regularly
3. **Restrict firewall** - Allow SSH only from known IPs
4. **Use separate user** - Don't use root for SSH
5. **Enable logging** - Monitor API access

### Performance

1. **Cleanup regularly** - Remove old incidents to save disk space
2. **Limit concurrency** - Run one incident at a time
3. **Use local VM** - For faster iteration during development
4. **Mock mode** - Use --mock flag for offline testing

## Troubleshooting

### SSH Connection Failed

```
Check:
- SSH key path is correct
- User has sudo privileges
- Firewall allows SSH
- Key permissions are 600
```

### Chaos Script Not Found

```
Ensure scripts are deployed:
scp -r chaos-scripts/* user@host:/tmp/
ssh user@host 'sudo mv /tmp/*.sh /opt/chaos-scripts/ && sudo chmod +x /opt/chaos-scripts/*.sh'
```

### Dashboard Not Loading

```
Check:
- FastAPI server is running
- Frontend CSS is built (npm run build:css)
- Browser can reach http://localhost:8000
```

### Metrics Not Collected

```
Verify:
- Metrics server is running on port 9090
- Firewall allows port 9090
- psutil is installed (pip3 install psutil)
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_agents.py::test_log_agent_pattern_extraction -v
```

### Adding New Agents

1. Create agent class inheriting from `BaseAgent`
2. Implement `async def run(self)` method
3. Use `append_trace_event()` to log progress
4. Add to coordinator orchestration
5. Write tests

### Adding New Scenarios

1. Create chaos script in `chaos-scripts/`
2. Add to scenario map in coordinator
3. Document in this guide
4. Add example in `examples/`

## Examples

See the `examples/` directory for:
- `cpu-spike-example/` - Complete CPU spike incident
- Sample trace.json files
- Example reports and fixes

## Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the FAQ in README.md
- Review existing examples

## License

MIT License - See LICENSE file for details.
