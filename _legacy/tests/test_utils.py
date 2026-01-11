"""Test utilities and helper functions"""

import pytest
from app.utils import generate_incident_id, append_trace_event, read_trace
from pathlib import Path


def test_generate_incident_id():
    """Test incident ID generation"""
    incident_id = generate_incident_id()
    
    assert incident_id.startswith("inc-")
    assert len(incident_id) > 10


def test_trace_operations(tmp_path):
    """Test trace file operations"""
    incident_id = "test-trace-001"
    base_path = str(tmp_path)
    
    # Create incident dir
    incident_dir = tmp_path / incident_id
    incident_dir.mkdir()
    (incident_dir / "trace.json").write_text("[]")
    
    # Append event
    append_trace_event(
        incident_id,
        "TestAgent",
        "test",
        "Test content",
        evidence=["test.txt"],
        confidence=0.9,
        meta={"key": "value"},
        base_path=base_path
    )
    
    # Read trace
    trace = read_trace(incident_id, base_path=base_path)
    
    assert len(trace) == 1
    assert trace[0]["agent"] == "TestAgent"
    assert trace[0]["content"] == "Test content"
    assert trace[0]["confidence"] == 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
