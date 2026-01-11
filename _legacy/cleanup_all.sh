#!/bin/bash
# Cleanup script - stops all chaos scripts and cleans up artifacts

echo "🧹 AI Chaos Handler - Cleanup Script"
echo "====================================="

# Stop all chaos scripts
echo ""
echo "Stopping chaos scripts..."
for script in cpu_spike memory_leak disk_fill net_latency service_kill db_conn_exhaust; do
    if [ -f "/opt/chaos-scripts/${script}.sh" ]; then
        sudo /opt/chaos-scripts/${script}.sh stop 2>/dev/null || true
        echo "  ✓ Stopped ${script}"
    fi
done

# Clean up PID files
echo ""
echo "Cleaning up PID files..."
sudo rm -f /var/run/chaos-*.pid
echo "  ✓ PID files removed"

# Clean up chaos artifacts
echo ""
echo "Cleaning up chaos artifacts..."
sudo rm -rf /tmp/chaos_fill
sudo rm -f /tmp/test_chaos.db
echo "  ✓ Artifacts removed"

# Check for running processes
echo ""
echo "Checking for lingering processes..."
STRESS_PROCS=$(pgrep stress-ng 2>/dev/null || true)
if [ -n "$STRESS_PROCS" ]; then
    echo "  ⚠ Found stress-ng processes, killing..."
    sudo killall -9 stress-ng 2>/dev/null || true
fi

PYTHON_CHAOS=$(pgrep -f "chaos.*python" 2>/dev/null || true)
if [ -n "$PYTHON_CHAOS" ]; then
    echo "  ⚠ Found Python chaos processes, killing..."
    kill -9 $PYTHON_CHAOS 2>/dev/null || true
fi

echo ""
echo "✅ Cleanup complete!"
