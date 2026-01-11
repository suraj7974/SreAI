# Real AI Agent System with LangGraph

## Overview

This is a **true multi-agent AI system** using LangGraph, not just API wrappers. The agents are autonomous, collaborative, and capable of making their own decisions.

## Key Differences: Real Agents vs API Wrappers

### Old System (API Wrappers)
```python
# Just a function call with prompt
result = llm.analyze_logs(logs)
# No autonomy, no tools, no memory
```

### New System (Real AI Agents)
```python
# Autonomous agent with tools, memory, and decision-making
agent = DiagnosticAgent()
result = await agent(state)  # Agent decides what tools to use
```

## Real Agent Characteristics

### 1. **Autonomy**
- Agents decide which tools to use and when
- Make their own decisions about next steps
- Can adapt strategy based on findings

### 2. **Tool Use**
- Each agent has access to tools:
  - `collect_system_logs()` - Gather log data
  - `collect_system_metrics()` - Get system metrics
  - `execute_ssh_command()` - Run arbitrary commands
  - `query_previous_incidents()` - Learn from history
  - `log_agent_decision()` - Record reasoning
  - `save_analysis_artifact()` - Store findings

### 3. **Memory & Context**
- Shared state across all agents (`AgentState`)
- Agents can read what previous agents discovered
- Build on each other's findings

### 4. **Collaboration**
- Agents communicate through shared state
- Can influence each other's decisions
- Workflow adapts based on agent choices

### 5. **Reasoning**
- Agents use tool-calling and ReAct patterns
- Explain their decisions and reasoning
- Can loop and iterate until satisfied

## Agent Architecture

### DiagnosticAgent
**Role:** Investigate incidents and gather evidence

**Tools:**
- `collect_system_logs`
- `collect_system_metrics`
- `log_agent_decision`
- `save_analysis_artifact`

**Autonomous Decisions:**
- What data to collect
- When to stop investigating
- Whether more information is needed
- Root cause hypotheses

### RemediationAgent
**Role:** Propose fixes and remediation strategies

**Tools:**
- `execute_ssh_command` (for validation)
- `query_previous_incidents` (learning)
- `log_agent_decision`
- `save_analysis_artifact`

**Autonomous Decisions:**
- Which fixes to propose
- Fix priority and ordering
- Risk assessment
- Whether to query historical data

### ValidationAgent
**Role:** Assess risks and validate fixes

**Tools:**
- `execute_ssh_command` (safe validation)
- `log_agent_decision`
- `save_analysis_artifact`

**Autonomous Decisions:**
- APPROVE / REJECT / APPROVE_WITH_CONDITIONS
- What validation commands to run
- Risk level confirmation
- Whether manual review is needed

### ReporterAgent
**Role:** Synthesize findings into reports

**Tools:**
- `save_analysis_artifact`
- `log_agent_decision`

**Autonomous Decisions:**
- Report structure and emphasis
- What to highlight for stakeholders
- Next steps and recommendations

## Workflow with LangGraph

```
┌─────────────────┐
│ DiagnosticAgent │ ─────> Investigates incident
└────────┬────────┘        Uses tools autonomously
         │
         ▼
┌─────────────────┐
│RemediationAgent │ ─────> Proposes fixes
└────────┬────────┘        Learns from history
         │
         ▼
┌─────────────────┐
│ ValidationAgent │ ─────> Validates safety
└────────┬────────┘        Makes go/no-go decisions
         │
         ▼
┌─────────────────┐
│ ReporterAgent   │ ─────> Creates report
└─────────────────┘        Synthesizes findings
```

**Conditional Routing:** Agents can decide to:
- Skip steps if not needed
- Loop back for more validation
- End early if critical issue found

## Example Agent Reasoning

### DiagnosticAgent thinking:
```
1. "I need to understand the CPU spike incident"
2. "Let me collect logs first" → uses collect_system_logs()
3. "Now I need metrics" → uses collect_system_metrics()
4. "I see high CPU in the logs, let me analyze patterns"
5. "Root cause: process X consuming resources"
6. "Logging my decision" → uses log_agent_decision()
7. "Saving analysis" → uses save_analysis_artifact()
8. "I have enough information, moving to remediation"
```

### RemediationAgent thinking:
```
1. "DiagnosticAgent found process X is the problem"
2. "Let me check historical incidents" → uses query_previous_incidents()
3. "Found similar incident resolved by restarting service"
4. "Proposing fix: restart service X"
5. "This is medium risk, providing rollback plan"
6. "Logging my remediation strategy"
```

### ValidationAgent thinking:
```
1. "RemediationAgent proposes restarting service X"
2. "Let me verify service X exists" → uses execute_ssh_command()
3. "Checking dependencies"
4. "This could cause 30s downtime - acceptable"
5. "Decision: APPROVE_WITH_CONDITIONS"
6. "Condition: Run during maintenance window"
```

## How to Use

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# .env file
GOOGLE_API_KEY=your_api_key
GOOGLE_MODEL=gemini-1.5-flash
VM_HOST=your_vm_ip
VM_USER=your_user
VM_KEY_PATH=/path/to/key
```

### 3. Start Incident with Real Agents
```python
from app.agents_v2.orchestrator import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()

incident_id = await orchestrator.start_incident(
    scenario="cpu_spike",
    target_vm={
        "host": "10.0.0.5",
        "port": 22,
        "user": "ubuntu",
        "key_path": "/path/to/key"
    }
)
```

### 4. Agents Execute Autonomously
The orchestrator releases the agents and they:
- Collaborate automatically
- Make their own decisions
- Use tools as needed
- Generate complete incident response

## Benefits Over Old System

| Feature | Old System | Real Agents |
|---------|-----------|-------------|
| Autonomy | ❌ Hardcoded flow | ✅ Self-directed |
| Tools | ❌ No tools | ✅ 6+ tools |
| Memory | ❌ Stateless | ✅ Shared state |
| Learning | ❌ None | ✅ Query history |
| Reasoning | ❌ Simple prompt | ✅ ReAct pattern |
| Collaboration | ❌ Sequential | ✅ Interactive |
| Adaptability | ❌ Fixed | ✅ Dynamic routing |

## Future Enhancements

1. **Agent Memory** - Add vector DB for long-term memory
2. **Human-in-the-Loop** - Allow agents to request human input
3. **More Tools** - Add Kubernetes, Docker, database tools
4. **Learning** - Implement reinforcement learning from outcomes
5. **Multi-Model** - Use different LLMs for different agents
6. **Parallel Execution** - Run independent agents in parallel

## Architecture Diagram

```
┌──────────────────────────────────────────────┐
│         MultiAgentOrchestrator               │
│              (LangGraph)                     │
└──────────────────┬───────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌───────────────┐     ┌───────────────┐
│ Agent State   │◄────┤  Agent Tools  │
│ (Shared)      │     │               │
└───────────────┘     └───────────────┘
        ▲                     ▲
        │                     │
        │                     │
  ┌─────┴─────┬─────┬─────┬──┴────┐
  │           │     │     │        │
  ▼           ▼     ▼     ▼        ▼
┌─────┐   ┌─────┐ ┌─────┐ ┌─────┐
│Diag │   │Remed│ │Valid│ │Rept │
│Agent│   │Agent│ │Agent│ │Agent│
└─────┘   └─────┘ └─────┘ └─────┘
```

## Conclusion

This is a **real AI agent system** with:
- ✅ Autonomous decision-making
- ✅ Tool use capabilities
- ✅ Collaborative workflow
- ✅ Memory and state management
- ✅ Reasoning and planning
- ✅ Adaptability

Not just API calls wrapped in classes!
