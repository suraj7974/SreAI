#!/bin/bash
# Service Kill Chaos Script
# Usage: service_kill.sh start <service_name> | stop

set -e

PID_FILE="/var/run/chaos-service.pid"

start_chaos() {
    local service=${1:-nginx}
    
    echo "Stopping service: ${service}"
    
    if [ -f "$PID_FILE" ]; then
        echo "Service chaos already running"
        exit 1
    fi
    
    systemctl stop $service
    echo "$service" > "$PID_FILE"
    
    echo "Service chaos started (stopped ${service})"
}

stop_chaos() {
    echo "Restarting service..."
    
    if [ ! -f "$PID_FILE" ]; then
        echo "No service chaos running"
        exit 0
    fi
    
    local service=$(cat "$PID_FILE")
    systemctl start $service
    
    rm -f "$PID_FILE"
    echo "Service chaos stopped (restarted ${service})"
}

case "$1" in
    start)
        start_chaos "$2"
        ;;
    stop)
        stop_chaos
        ;;
    *)
        echo "Usage: $0 {start <service_name>|stop}"
        exit 1
        ;;
esac
