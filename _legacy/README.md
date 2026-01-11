# Legacy Code - DEPRECATED

This directory contains the original AI Chaos Handler implementation which has been replaced by the new agentic SRE system in `sre_agent/`.

## Why Deprecated?

The original system was an "AI wrapper" rather than a true agent system:
- Hardcoded workflow pipelines (collect logs → collect metrics → AI analysis → generate fix)
- LLM used only for text generation, not autonomous decision-making
- No reasoning loop, planning, or self-correction capabilities
- Manual SSH-based metric collection (inefficient, not scalable)

## New System

The replacement in `sre_agent/` provides:
- LangGraph-based ReAct agents with autonomous reasoning
- Prometheus pull-based metrics collection
- Grafana dashboards for visualization
- Human-in-the-loop approval for remediation actions
- True multi-agent architecture with supervisor coordination

## Contents

- `app/` - Original Python backend (FastAPI coordinator, SSH-based agents)
- `frontend/` - Original React dashboard

## Should I Delete This?

Keep this directory if you need to:
- Reference the original implementation
- Migrate specific features to the new system
- Understand the evolution of the project

Otherwise, it's safe to delete this entire `_legacy/` directory.
