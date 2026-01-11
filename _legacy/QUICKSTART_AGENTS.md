# Quick Start: Real AI Agents

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create or update `.env` file:
```bash
# Google AI API Key (required)
GOOGLE_API_KEY=your_api_key_here
GOOGLE_MODEL=gemini-1.5-flash

# VM Connection (optional for testing)
VM_HOST=your_vm_ip
VM_PORT=22
VM_USER=ubuntu
VM_KEY_PATH=/path/to/ssh/key

# API Settings
API_AUTH_TOKEN=your_token
```

### 3. Test Real Agents
```bash
python test_real_agents.py
```

## Usage

### Start API Server
```bash
python -m app.main
```

### Use Real Agent System (API v2)
```bash
curl -X POST http://localhost:8000/v2/start_incident \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "cpu_spike",
    "target_vm": {
      "host": "10.0.0.5",
      "port": 22,
      "user": "ubuntu",
      "key_path": "/path/to/key"
    }
  }'
```

### Check Agent Status
```bash
curl http://localhost:8000/agents/status
```

Response:
```json
{
  "agents": [
    {"name": "DiagnosticAgent", "status": "online", "capability": "data_collection"},
    {"name": "RemediationAgent", "status": "online", "capability": "fix_generation"},
    {"name": "ValidationAgent", "status": "online", "capability": "risk_assessment"},
    {"name": "ReporterAgent", "status": "online", "capability": "reporting"}
  ],
  "orchestrator": "LangGraph",
  "autonomous": true,
  "collaborative": true
}
```

## What Happens

### 1. DiagnosticAgent (Autonomous Investigation)
- **Decides** what data to collect
- **Uses tools**: `collect_system_logs`, `collect_system_metrics`
- **Analyzes** patterns autonomously
- **Logs decisions** with reasoning
- **Determines** when investigation is complete

### 2. RemediationAgent (Intelligent Fix Generation)
- **Reviews** diagnostic findings
- **Queries** historical incidents (learns from past)
- **Generates** remediation proposals
- **Assesses** risk for each fix
- **Creates** executable scripts with rollback plans

### 3. ValidationAgent (Safety Assessment)
- **Validates** each proposed fix
- **Executes** safe read-only commands for verification
- **Makes decisions**: APPROVE / REJECT / MANUAL_REVIEW
- **Identifies** prerequisites and dependencies
- **Recommends** safer alternatives when needed

### 4. ReporterAgent (Documentation)
- **Synthesizes** all findings
- **Creates** executive summary
- **Documents** technical details
- **Provides** next steps and recommendations

## Key Features

### Autonomy
Agents decide:
- Which tools to use
- What data to gather
- When to proceed
- How to analyze findings

### Tools Available
- `collect_system_logs` - Gather VM logs
- `collect_system_metrics` - Get performance data
- `execute_ssh_command` - Run specific commands
- `query_previous_incidents` - Learn from history
- `log_agent_decision` - Record reasoning
- `save_analysis_artifact` - Store findings

### Collaboration
- Agents share state through `AgentState`
- Build on each other's findings
- Can loop back if validation fails
- Dynamic workflow routing

### Memory
- Shared state across all agents
- Context preserved throughout workflow
- Decision history tracked
- Artifacts saved for review

## Example Output

```
Incident ID: inc_20231203_1234

Artifacts Generated:
├── raw_logs.txt              (DiagnosticAgent)
├── metrics.json              (DiagnosticAgent)
├── log_analysis.json         (DiagnosticAgent decision)
├── fix_suggestions.json      (RemediationAgent)
├── fix.sh                    (RemediationAgent)
├── validation_report.json    (ValidationAgent decision)
└── incident_report.md        (ReporterAgent)

Agent Decisions:
1. DiagnosticAgent: "High CPU detected, investigating process tree"
2. RemediationAgent: "Proposing service restart with graceful shutdown"
3. ValidationAgent: "APPROVE_WITH_CONDITIONS - requires maintenance window"
4. ReporterAgent: "Report generated with actionable recommendations"
```

## Comparison

### Old System (v1)
```python
# app/agents/log_agent.py
logs = collect_logs()
analysis = llm.analyze_logs(logs)  # Just an API call
return analysis
```

### Real Agents (v2)
```python
# app/agents_v2/diagnostic_agent.py
agent = create_tool_calling_agent(llm, tools, prompt)
result = await agent.ainvoke(state)  # Agent decides what to do
# Agent autonomously:
# 1. Chooses to use collect_system_logs tool
# 2. Analyzes the output
# 3. Decides if more data needed
# 4. Uses collect_system_metrics
# 5. Determines root cause
# 6. Logs its reasoning
# 7. Saves artifacts
```

## Frontend Integration

The UI now shows real agent count:
```typescript
// Fetches from /agents/status
const onlineAgents = response.data.agents.filter(
  a => a.status === "online"
).length;  // Shows 4 (not hardcoded 3)
```

## Next Steps

1. **Run the test**: `python test_real_agents.py`
2. **Start the API**: `python -m app.main`
3. **Check the frontend**: Open http://localhost:8000
4. **Read the docs**: `REAL_AI_AGENTS.md`

## Troubleshooting

### "GOOGLE_API_KEY not found"
Add your API key to `.env`:
```bash
GOOGLE_API_KEY=your_key_here
```

### "VM not reachable"
Agents will still work, but data collection will fail gracefully. They'll log the error and proceed with mock data.

### "Module not found: langgraph"
Install dependencies:
```bash
pip install -r requirements.txt
```

## Learn More

- `REAL_AI_AGENTS.md` - Architecture details
- `app/agents_v2/` - Agent implementations
- `test_real_agents.py` - Demo script
