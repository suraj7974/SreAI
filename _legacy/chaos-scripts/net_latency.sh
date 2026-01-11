#!/bin/bash
# Network Latency Chaos Script
# Usage: net_latency.sh start <interface> <delay_ms> <loss_pct> | stop

set -e

PID_FILE="/var/run/chaos-network.pid"

start_chaos() {
    local iface=${1:-eth0}
    local delay_ms=${2:-100}
    local loss_pct=${3:-0}
    
    echo "Starting network latency: ${delay_ms}ms delay, ${loss_pct}% loss on ${iface}"
    
    if [ -f "$PID_FILE" ]; then
        echo "Network chaos already running"
        exit 1
    fi
    
    # Add network delay and loss using tc
    tc qdisc add dev $iface root netem delay ${delay_ms}ms loss ${loss_pct}%
    
    echo "$iface" > "$PID_FILE"
    echo "Network chaos started"
}

stop_chaos() {
    echo "Stopping network latency..."
    
    if [ ! -f "$PID_FILE" ]; then
        echo "No network chaos running"
        exit 0
    fi
    
    local iface=$(cat "$PID_FILE")
    tc qdisc del dev $iface root 2>/dev/null || true
    
    rm -f "$PID_FILE"
    echo "Network chaos stopped"
}

case "$1" in
    start)
        start_chaos "$2" "$3" "$4"
        ;;
    stop)
        stop_chaos
        ;;
    *)
        echo "Usage: $0 {start <interface> <delay_ms> <loss_pct>|stop}"
        exit 1
        ;;
esac
