"""Unit tests for AI Chaos Handler agents"""

import pytest
import json
from pathlib import Path
from app.agents.log_agent import LogAgent
from app.agents.metrics_agent import MetricsAgent
from app.agents.fixer_agent import FixerAgent
from app.agents.tester_agent import TesterAgent
from app.agents.reporter_agent import ReporterAgent


@pytest.fixture
def mock_incident_dir(tmp_path):
    """Create a mock incident directory"""
    incident_id = "inc-test-001"
    incident_dir = tmp_path / incident_id
    incident_dir.mkdir()
    (incident_dir / "artifacts").mkdir()
    
    # Create trace file
    trace_file = incident_dir / "trace.json"
    trace_file.write_text("[]")
    
    return str(tmp_path), incident_id


def test_log_agent_pattern_extraction():
    """Test log pattern extraction"""
    agent = LogAgent("test-001", {})
    
    logs = """
    2024-01-01 10:00:00 ERROR: Connection failed
    2024-01-01 10:00:01 FATAL: Out of memory
    2024-01-01 10:00:02 Warning: High CPU usage
    2024-01-01 10:00:03 error in processing request
    """
    
    patterns = agent._extract_patterns(logs)
    
    assert len(patterns) > 0
    assert any(p["category"] == "error" for p in patterns)
    assert any(p["category"] == "fatal" for p in patterns)


def test_metrics_agent_anomaly_detection():
    """Test anomaly detection in metrics"""
    agent = MetricsAgent("test-001", {})
    
    # Mock metrics with high CPU
    metrics = {
        "cpu_usage_percent": 95.0,
        "memory_usage_percent": 50.0,
        "disk_usage_percent": 70.0,
        "load_1min": 2.5
    }
    
    anomalies = agent._detect_anomalies(metrics)
    
    assert len(anomalies) > 0
    assert any(a["metric"] == "cpu_usage_percent" for a in anomalies)
    
    # Check severity
    cpu_anomaly = next(a for a in anomalies if a["metric"] == "cpu_usage_percent")
    assert cpu_anomaly["severity"] == "high"


def test_fixer_agent_generates_suggestions():
    """Test fix generation"""
    agent = FixerAgent("test-001", {
        "log_data": {"patterns": []},
        "metrics_data": {
            "anomalies": [{
                "metric": "cpu_usage_percent",
                "value": 95.0,
                "severity": "high"
            }]
        }
    })
    
    suggestions = agent._generate_fixes(
        {"patterns": []},
        {"anomalies": [{
            "metric": "cpu_usage_percent",
            "value": 95.0,
            "severity": "high"
        }]}
    )
    
    assert len(suggestions) > 0
    assert suggestions[0]["title"] == "Mitigate High CPU Usage"
    assert "commands" in suggestions[0]


def test_tester_agent_risk_assessment():
    """Test risk assessment"""
    agent = TesterAgent("test-001", {})
    
    suggestions = [{
        "id": "test-001",
        "title": "Test Fix",
        "commands": ["ps aux", "rm -rf /data"],
        "risk_level": "high"
    }]
    
    assessments = agent._assess_risks(suggestions)
    
    assert len(assessments) > 0
    assert assessments[0]["risk_score"] > 0
    
    # Should detect dangerous rm -rf
    assert any("rm -rf" in str(r) for r in assessments[0]["risks"])


def test_overall_risk_calculation():
    """Test overall risk calculation"""
    agent = TesterAgent("test-001", {})
    
    assessments = [
        {"risk_score": 3, "approved": True},
        {"risk_score": 8, "approved": False},
        {"risk_score": 5, "approved": True}
    ]
    
    overall = agent._calculate_overall_risk(assessments)
    
    assert overall["max_score"] == 8
    assert overall["level"] == "high"
    assert overall["total_count"] == 3


def test_fix_script_generation():
    """Test shell script generation"""
    agent = FixerAgent("test-001", {})
    
    suggestions = [{
        "id": "test-001",
        "title": "Test Fix",
        "rationale": "Testing",
        "risk_level": "low",
        "confidence": 0.9,
        "commands": ["echo 'test'", "ps aux"]
    }]
    
    script = agent._generate_fix_script(suggestions)
    
    assert "#!/bin/bash" in script
    assert "Test Fix" in script
    assert "echo 'test'" in script


@pytest.mark.asyncio
async def test_reporter_slack_summary():
    """Test Slack summary generation"""
    agent = ReporterAgent("test-001", {"storage_path": "./incidents"})
    
    trace = [
        {"agent": "LogAgent", "content": "Collected logs", "timestamp": "2024-01-01T10:00:00Z"},
        {"agent": "MetricsAgent", "content": "Collected metrics", "meta": {"anomalies_count": 2}, "timestamp": "2024-01-01T10:01:00Z"}
    ]
    
    summary = agent._generate_slack_summary(trace)
    
    assert "Incident Report" in summary
    assert "test-001" in summary
    assert "Anomalies Detected: 2" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
