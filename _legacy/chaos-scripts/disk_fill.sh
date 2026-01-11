#!/bin/bash
# Disk Fill Chaos Script
# Usage: disk_fill.sh start <size_mb> | stop

set -e

FILL_DIR="/tmp/chaos_fill"
PID_FILE="/var/run/chaos-disk.pid"

start_chaos() {
    local size_mb=${1:-5000}
    
    echo "Starting disk fill: ${size_mb}MB"
    
    if [ -f "$PID_FILE" ]; then
        echo "Disk chaos already running"
        exit 1
    fi
    
    mkdir -p "$FILL_DIR"
    
    # Create a large file
    dd if=/dev/zero of="${FILL_DIR}/fill.dat" bs=1M count=$size_mb 2>/dev/null || true
    
    echo $$ > "$PID_FILE"
    echo "Disk chaos started (filled ${size_mb}MB)"
}

stop_chaos() {
    echo "Stopping disk fill..."
    
    if [ -d "$FILL_DIR" ]; then
        rm -rf "$FILL_DIR"
        echo "Disk chaos stopped (cleaned up $FILL_DIR)"
    fi
    
    rm -f "$PID_FILE"
}

case "$1" in
    start)
        start_chaos "$2"
        ;;
    stop)
        stop_chaos
        ;;
    *)
        echo "Usage: $0 {start <size_mb>|stop}"
        exit 1
        ;;
esac
