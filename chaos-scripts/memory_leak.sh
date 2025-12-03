#!/bin/bash
# Memory Leak Chaos Script
# Usage: memory_leak.sh start <target_mb> <duration> | stop

set -e

PID_FILE="/var/run/chaos-memory.pid"
MAX_RUNTIME=300

start_chaos() {
    local target_mb=${1:-1024}
    local duration=${2:-60}
    
    echo "Starting memory leak: ${target_mb}MB for ${duration}s"
    
    if [ -f "$PID_FILE" ]; then
        echo "Memory chaos already running"
        exit 1
    fi
    
    # Python memory allocator
    python3 - <<EOF &
import time
import sys

target_mb = $target_mb
duration = $duration
chunk_mb = 100

data = []
allocated = 0

print(f"Allocating {target_mb}MB of memory...")

while allocated < target_mb:
    # Allocate 100MB chunks
    chunk_size = min(chunk_mb, target_mb - allocated)
    data.append(' ' * (chunk_size * 1024 * 1024))
    allocated += chunk_size
    print(f"Allocated {allocated}MB")
    time.sleep(0.5)

print(f"Holding {allocated}MB for {duration}s...")
time.sleep(duration)

print("Releasing memory...")
data.clear()
print("Memory chaos complete")
EOF
    
    echo $! > "$PID_FILE"
    
    # Auto-cleanup
    (
        sleep $MAX_RUNTIME
        $0 stop 2>/dev/null || true
    ) &
    
    echo "Memory chaos started"
}

stop_chaos() {
    echo "Stopping memory leak..."
    
    if [ ! -f "$PID_FILE" ]; then
        echo "No memory chaos running"
        exit 0
    fi
    
    kill -9 $(cat "$PID_FILE") 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "Memory chaos stopped"
}

case "$1" in
    start)
        start_chaos "$2" "$3"
        ;;
    stop)
        stop_chaos
        ;;
    *)
        echo "Usage: $0 {start <target_mb> <duration>|stop}"
        exit 1
        ;;
esac
