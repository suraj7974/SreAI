#!/bin/bash
# =============================================================================
# Node Exporter Installation Script for Target VMs
# 
# Run this on each VM you want to monitor with Prometheus
# =============================================================================

set -e

NODE_EXPORTER_VERSION="1.6.1"
NODE_EXPORTER_USER="node_exporter"

echo "Installing Node Exporter v${NODE_EXPORTER_VERSION}..."

# Create user if not exists
if ! id "$NODE_EXPORTER_USER" &>/dev/null; then
    sudo useradd --no-create-home --shell /bin/false $NODE_EXPORTER_USER
fi

# Download and extract
cd /tmp
wget -q "https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"
tar xzf "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"

# Install binary
sudo mv "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64/node_exporter" /usr/local/bin/
sudo chown $NODE_EXPORTER_USER:$NODE_EXPORTER_USER /usr/local/bin/node_exporter

# Cleanup
rm -rf "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64" "node_exporter-${NODE_EXPORTER_VERSION}.linux-amd64.tar.gz"

# Create systemd service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'EOF'
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
    --collector.systemd \
    --collector.processes

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable node_exporter
sudo systemctl start node_exporter

# Verify
if systemctl is-active --quiet node_exporter; then
    echo "Node Exporter installed and running on port 9100"
    echo "Test: curl http://localhost:9100/metrics"
else
    echo "ERROR: Node Exporter failed to start"
    sudo systemctl status node_exporter
    exit 1
fi

# Firewall (if UFW is active)
if command -v ufw &> /dev/null && sudo ufw status | grep -q "active"; then
    echo "Opening port 9100 in UFW..."
    sudo ufw allow 9100/tcp
fi

echo ""
echo "============================================"
echo "Node Exporter v${NODE_EXPORTER_VERSION} installed!"
echo ""
echo "Add this target to your Prometheus config:"
echo "  - targets: ['$(hostname -I | awk '{print $1}'):9100']"
echo "============================================"
