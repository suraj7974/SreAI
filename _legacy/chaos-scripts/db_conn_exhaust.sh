#!/bin/bash
# Database Connection Exhaustion Chaos Script
# Usage: db_conn_exhaust.sh start <conn_string> <clients> | stop

set -e

PID_FILE="/var/run/chaos-db.pid"
MAX_RUNTIME=300

start_chaos() {
    local conn_string=${1:-"sqlite:///tmp/test.db"}
    local clients=${2:-50}
    
    echo "Starting DB connection exhaustion: ${clients} clients"
    
    if [ -f "$PID_FILE" ]; then
        echo "DB chaos already running"
        exit 1
    fi
    
    # Python script to hold connections
    python3 - <<EOF &
import time
import sqlite3

clients = $clients
connections = []

print(f"Opening {clients} database connections...")

for i in range(clients):
    try:
        conn = sqlite3.connect('/tmp/test_chaos.db', check_same_thread=False)
        connections.append(conn)
        print(f"Connection {i+1}/{clients} opened")
        time.sleep(0.1)
    except Exception as e:
        print(f"Failed to open connection {i+1}: {e}")

print(f"Holding {len(connections)} connections for 60s...")
time.sleep(60)

print("Closing connections...")
for conn in connections:
    conn.close()

print("DB chaos complete")
EOF
    
    echo $! > "$PID_FILE"
    
    # Auto-cleanup
    (
        sleep $MAX_RUNTIME
        $0 stop 2>/dev/null || true
    ) &
    
    echo "DB chaos started"
}

stop_chaos() {
    echo "Stopping DB connection exhaustion..."
    
    if [ ! -f "$PID_FILE" ]; then
        echo "No DB chaos running"
        exit 0
    fi
    
    kill -9 $(cat "$PID_FILE") 2>/dev/null || true
    rm -f "$PID_FILE"
    echo "DB chaos stopped"
}

case "$1" in
    start)
        start_chaos "$2" "$3"
        ;;
    stop)
        stop_chaos
        ;;
    *)
        echo "Usage: $0 {start <conn_string> <clients>|stop}"
        exit 1
        ;;
esac
