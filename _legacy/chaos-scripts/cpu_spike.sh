#!/bin/bash
# CPU Spike Chaos Script
# Usage: cpu_spike.sh start <duration> <workers> | stop

set -e

PID_FILE="/var/run/chaos-cpu.pid"
MAX_RUNTIME=300  # 5 minutes failsafe

start_chaos() {
    local duration=${1:-60}
    local workers=${2:-2}
    
    echo "Starting CPU spike: ${workers} workers for ${duration}s"
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        echo "CPU chaos already running (PID: $(cat $PID_FILE))"
        exit 1
    fi
    
    # Use stress-ng if available, otherwise fallback to shell
    if command -v stress-ng &> /dev/null; then
        stress-ng --cpu $workers --timeout ${duration}s &
        echo $! > "$PID_FILE"
    else
        # Fallback: bash CPU burner
        for i in $(seq 1 $workers); do
            (
                end_time=$(($(date +%s) + duration))
                while [ $(date +%s) -lt $end_time ]; do
                    : # Busy loop
                done
            ) &
            echo $! >> "$PID_FILE"
        done
    fi
    
    # Auto-cleanup after max runtime
    (
        sleep $MAX_RUNTIME
        $0 stop 2>/dev/null || true
    ) &
    
    echo "CPU chaos started (duration: ${duration}s)"
}

stop_chaos() {
    echo "Stopping CPU spike..."
    
    if [ ! -f "$PID_FILE" ]; then
        echo "No CPU chaos running"
        exit 0
    fi
    
    # Kill all PIDs
    while read pid; do
        kill -9 $pid 2>/dev/null || true
    done < "$PID_FILE"
    
    rm -f "$PID_FILE"
    echo "CPU chaos stopped"
}

case "$1" in
    start)
        start_chaos "$2" "$3"
        ;;
    stop)
        stop_chaos
        ;;
    *)
        echo "Usage: $0 {start <duration> <workers>|stop}"
        exit 1
        ;;
esac
