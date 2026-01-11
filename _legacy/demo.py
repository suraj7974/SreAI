#!/usr/bin/env python3
"""
Demo script for AI Chaos Handler
Simulates an incident without requiring a real VM
"""

import json
import time
from pathlib import Path

# Mock configuration
MOCK_CONFIG = {
    "incident_id": "inc-demo-001",
    "scenario": "cpu_spike",
    "storage_path": "./incidents"
}


def create_mock_incident():
    """Create a mock incident with all artifacts"""
    
    print("🎬 AI Chaos Handler - Demo Mode")
    print("=" * 50)
    print()
    
    incident_id = MOCK_CONFIG["incident_id"]
    storage_path = Path(MOCK_CONFIG["storage_path"])
    incident_dir = storage_path / incident_id
    
    # Create directories
    incident_dir.mkdir(parents=True, exist_ok=True)
    (incident_dir / "artifacts").mkdir(exist_ok=True)
    
    print(f"✅ Created incident directory: {incident_dir}")
    
    # Create trace.json
    trace = [
        {
            "timestamp": "2024-12-02T10:00:00Z",
            "agent": "Coordinator",
            "type": "diagnosis",
            "content": "Incident inc-demo-001 started with scenario: cpu_spike",
            "meta": {"phase": "initializing", "scenario": "cpu_spike"}
        },
        {
            "timestamp": "2024-12-02T10:00:15Z",
            "agent": "LogAgent",
            "type": "diagnosis",
            "content": "Starting log collection from target VM",
            "meta": {"phase": "collection"}
        },
        {
            "timestamp": "2024-12-02T10:00:30Z",
            "agent": "LogAgent",
            "type": "evidence",
            "content": "Collected 250 log lines, found 3 error patterns",
            "evidence": ["raw_logs.txt"],
            "confidence": 0.85,
            "meta": {"patterns_found": 3, "log_lines": 250}
        },
        {
            "timestamp": "2024-12-02T10:00:45Z",
            "agent": "MetricsAgent",
            "type": "diagnosis",
            "content": "Starting metrics collection from target VM",
            "meta": {"phase": "collection"}
        },
        {
            "timestamp": "2024-12-02T10:01:00Z",
            "agent": "MetricsAgent",
            "type": "evidence",
            "content": "Collected metrics snapshot, detected 1 anomalies",
            "evidence": ["metrics.json"],
            "confidence": 0.90,
            "meta": {"anomalies_count": 1, "metrics_collected": 6}
        },
        {
            "timestamp": "2024-12-02T10:01:15Z",
            "agent": "FixerAgent",
            "type": "diagnosis",
            "content": "Analyzing evidence and generating fix suggestions",
            "meta": {"phase": "remediation"}
        },
        {
            "timestamp": "2024-12-02T10:01:30Z",
            "agent": "FixerAgent",
            "type": "suggestion",
            "content": "Generated 1 fix suggestions with average confidence 0.85",
            "evidence": ["fix_suggestion.json", "fix.sh"],
            "confidence": 0.85,
            "meta": {"suggestions_count": 1}
        },
        {
            "timestamp": "2024-12-02T10:01:45Z",
            "agent": "TesterAgent",
            "type": "test",
            "content": "Completed risk assessment: medium risk with score 4.0/10",
            "evidence": ["risk_assessment.json"],
            "confidence": 0.85,
            "meta": {"risk_level": "medium", "risk_score": 4.0}
        },
        {
            "timestamp": "2024-12-02T10:02:00Z",
            "agent": "ReporterAgent",
            "type": "report",
            "content": "Report generated successfully. PDF: False, Slack: False",
            "evidence": ["report.md", "slack_summary.txt"],
            "confidence": 1.0,
            "meta": {"pdf_generated": False, "slack_sent": False}
        },
        {
            "timestamp": "2024-12-02T10:02:05Z",
            "agent": "Coordinator",
            "type": "report",
            "content": "Incident response workflow completed successfully",
            "meta": {"phase": "complete"}
        }
    ]
    
    (incident_dir / "trace.json").write_text(json.dumps(trace, indent=2))
    print(f"✅ Created trace.json with {len(trace)} events")
    
    # Create raw_logs.txt
    logs = """2024-12-02 10:00:00 kernel: CPU temperature above threshold
2024-12-02 10:00:05 systemd[1]: stress-ng started
2024-12-02 10:00:10 kernel: CPU0: Core temperature/speed normal
2024-12-02 10:00:15 kernel: CPU utilization high: 95%"""
    
    (incident_dir / "raw_logs.txt").write_text(logs)
    print("✅ Created raw_logs.txt")
    
    # Create metrics.json
    metrics = {
        "cpu_usage_percent": 95.2,
        "memory_usage_percent": 45.8,
        "disk_usage_percent": 62.3,
        "load_1min": 5.8,
        "load_5min": 3.2,
        "load_15min": 2.1
    }
    
    (incident_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print("✅ Created metrics.json")
    
    # Create fix_suggestion.json
    suggestions = [{
        "id": "fix-cpu-001",
        "title": "Mitigate High CPU Usage",
        "rationale": "CPU usage is at 95.2%, which is high severity",
        "actions": [
            "Identify top CPU-consuming processes",
            "Consider restarting high-CPU services if appropriate",
            "Check for runaway processes or loops"
        ],
        "commands": [
            "ps aux --sort=-%cpu | head -10",
            "top -bn1 | head -20"
        ],
        "confidence": 0.85,
        "risk_level": "medium",
        "rollback": "None - informational commands only"
    }]
    
    (incident_dir / "fix_suggestion.json").write_text(json.dumps(suggestions, indent=2))
    print("✅ Created fix_suggestion.json")
    
    # Create fix.sh
    fix_script = """#!/bin/bash
# AI Chaos Handler - Suggested Fix Script
# Incident: inc-demo-001
# WARNING: Review this script before executing!

set -e
set -u

echo '=== AI Chaos Handler Fix Script ==='
echo 'Incident ID: inc-demo-001'
echo ''

# Mitigate High CPU Usage
# Risk Level: medium
# Confidence: 0.85
# Rationale: CPU usage is at 95.2%, which is high severity
echo ''
echo '--- Mitigate High CPU Usage ---'
echo 'Executing: ps aux --sort=-%cpu | head -10'
ps aux --sort=-%cpu | head -10
echo 'Executing: top -bn1 | head -20'
top -bn1 | head -20
echo ''

echo '=== Fix Script Complete ==='
"""
    
    (incident_dir / "fix.sh").write_text(fix_script)
    print("✅ Created fix.sh")
    
    # Create risk_assessment.json
    risk = [{
        "suggestion_id": "fix-cpu-001",
        "title": "Mitigate High CPU Usage",
        "risks": [],
        "risk_score": 0,
        "approved": True,
        "recommendations": ["Low risk - can be executed with standard precautions"],
        "simulation": {
            "dry_run_possible": True,
            "estimated_duration": "< 1 minute",
            "side_effects": ["Minimal side effects expected"]
        }
    }]
    
    (incident_dir / "risk_assessment.json").write_text(json.dumps(risk, indent=2))
    print("✅ Created risk_assessment.json")
    
    # Create report.md
    report = """# Incident Report: inc-demo-001

**Generated:** 2024-12-02 10:02:00 UTC

---

## Executive Summary

An incident was detected and analyzed by the AI Chaos Handler system.
The system collected 250 log lines and identified 1 metric anomalies.

---

## Timeline

### 2024-12-02T10:00:00Z - Coordinator
Incident inc-demo-001 started with scenario: cpu_spike

### 2024-12-02T10:01:00Z - MetricsAgent
**Confidence:** 90.00%
Collected metrics snapshot, detected 1 anomalies
**Evidence:** metrics.json

### 2024-12-02T10:01:30Z - FixerAgent
**Confidence:** 85.00%
Generated 1 fix suggestions with average confidence 0.85
**Evidence:** fix_suggestion.json, fix.sh

### 2024-12-02T10:02:00Z - ReporterAgent
**Confidence:** 100.00%
Report generated successfully. PDF: False, Slack: False
**Evidence:** report.md, slack_summary.txt

---

## Recommended Fixes

### Mitigate High CPU Usage
**ID:** `fix-cpu-001`
**Confidence:** 85.00%
**Risk Level:** MEDIUM

**Rationale:** CPU usage is at 95.2%, which is high severity

**Actions:**
- Identify top CPU-consuming processes
- Consider restarting high-CPU services if appropriate
- Check for runaway processes or loops

**Commands:**
```bash
ps aux --sort=-%cpu | head -10
top -bn1 | head -20
```

**Rollback Plan:** None - informational commands only

---

## Risk Assessment

### Mitigate High CPU Usage
**Risk Score:** 0/10
**Approved:** ✅ Yes

**Recommendations:**
- Low risk - can be executed with standard precautions

---

## Next Steps

1. **Review** this report and the recommended fixes
2. **Validate** the fix script at `fix.sh`
3. **Create** a VM snapshot before applying changes
4. **Execute** approved fixes during a maintenance window
5. **Monitor** system health after applying fixes
6. **Document** outcomes and update runbooks

---

*Report generated by AI Chaos Handler v1.0.0 at 2024-12-02 10:02:00 UTC*
"""
    
    (incident_dir / "report.md").write_text(report)
    print("✅ Created report.md")
    
    # Create slack_summary.txt
    slack = """🚨 *Incident Report: inc-demo-001*

*Time:* 2024-12-02 10:02:00 UTC

*Agents Executed:* 5
*Anomalies Detected:* 1
*Fixes Proposed:* 1

📊 *Full Report:* `incidents/inc-demo-001/report.md`

_Generated by AI Chaos Handler_"""
    
    (incident_dir / "slack_summary.txt").write_text(slack)
    print("✅ Created slack_summary.txt")
    
    print()
    print("=" * 50)
    print("✅ Demo incident created successfully!")
    print()
    print(f"📁 Incident directory: {incident_dir}")
    print(f"📊 Dashboard URL: http://localhost:8000/dashboard/{incident_id}")
    print(f"📄 Report: {incident_dir / 'report.md'}")
    print()
    print("To view in dashboard, start the server:")
    print("  ./start.sh")
    print()


if __name__ == "__main__":
    create_mock_incident()
