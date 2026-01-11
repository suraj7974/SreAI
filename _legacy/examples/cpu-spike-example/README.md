# Example Incident: CPU Spike

This directory contains an example of a completed incident response for a CPU spike scenario.

## Scenario

A CPU spike was triggered on the target VM using the `cpu_spike.sh` chaos script, causing CPU usage to exceed 90% for 60 seconds.

## Timeline

1. **Incident Started**: 2024-12-02 10:00:00 UTC
2. **Chaos Triggered**: CPU spike with 2 workers for 60s
3. **LogAgent**: Collected system logs (10:00:15)
4. **MetricsAgent**: Detected high CPU anomaly (10:00:30)
5. **FixerAgent**: Proposed mitigation steps (10:00:45)
6. **TesterAgent**: Assessed risk as medium (10:01:00)
7. **ReporterAgent**: Generated final report (10:01:15)
8. **Incident Complete**: 2024-12-02 10:01:20 UTC

## Key Findings

- **CPU Usage**: 95.2%
- **Load Average**: 5.8 (1min)
- **Root Cause**: Chaos-induced stress test
- **Anomalies Detected**: 1 (CPU threshold exceeded)

## Artifacts

This directory would contain actual incident artifacts from a real run.
