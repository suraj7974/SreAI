# DigitalOcean Droplet Provisioning Guide

This guide explains how to set up a DigitalOcean Droplet for the AI Chaos Handler system.

## Prerequisites

- DigitalOcean account
- `doctl` CLI tool (optional but recommended)
- SSH key pair

## Option 1: Using DigitalOcean Web Console

### Step 1: Create Droplet

1. Log in to [DigitalOcean Console](https://cloud.digitalocean.com)
2. Click "Create" → "Droplets"
3. Choose configuration:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic - 2 vCPU, 4GB RAM, 25GB SSD ($24/month)
   - **Region**: Choose closest to you
   - **Authentication**: SSH keys (upload your public key)
   - **Hostname**: `ai-chaos-target`

### Step 2: Initial Setup

SSH into your droplet:

```bash
ssh root@<droplet-ip>
```

Create the `sre-demo` user:

```bash
# Create user
adduser sre-demo

# Add to sudo group
usermod -aG sudo sre-demo

# Copy SSH keys
mkdir -p /home/sre-demo/.ssh
cp /root/.ssh/authorized_keys /home/sre-demo/.ssh/
chown -R sre-demo:sre-demo /home/sre-demo/.ssh
chmod 700 /home/sre-demo/.ssh
chmod 600 /home/sre-demo/.ssh/authorized_keys
```

### Step 3: Install Dependencies

```bash
# Switch to sre-demo user
su - sre-demo

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip stress-ng iproute2

# Install optional packages
sudo apt install -y docker.io nginx
```

### Step 4: Deploy Chaos Scripts

Copy chaos scripts to the droplet:

```bash
# On your local machine
scp -r chaos-scripts/* sre-demo@<droplet-ip>:/tmp/

# On the droplet
sudo mkdir -p /opt/chaos-scripts
sudo mv /tmp/*.sh /opt/chaos-scripts/
sudo chmod +x /opt/chaos-scripts/*.sh
```

### Step 5: Setup Metrics Endpoint (Optional)

Create a simple metrics server:

```bash
cat > /tmp/metrics_server.py << 'EOF'
#!/usr/bin/env python3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import psutil

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            metrics = {
                'cpu_usage_percent': psutil.cpu_percent(interval=1),
                'memory_usage_percent': psutil.virtual_memory().percent,
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'load_1min': psutil.getloadavg()[0],
                'load_5min': psutil.getloadavg()[1],
                'load_15min': psutil.getloadavg()[2],
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(metrics).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print("Starting metrics server on port 9090...")
    server = HTTPServer(('0.0.0.0', 9090), MetricsHandler)
    server.serve_forever()
EOF

sudo mv /tmp/metrics_server.py /opt/metrics_server.py
sudo chmod +x /opt/metrics_server.py

# Install psutil
sudo pip3 install psutil
```

Create a systemd service:

```bash
sudo tee /etc/systemd/system/metrics-server.service << 'EOF'
[Unit]
Description=Metrics Server for AI Chaos Handler
After=network.target

[Service]
Type=simple
User=sre-demo
ExecStart=/usr/bin/python3 /opt/metrics_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable metrics-server
sudo systemctl start metrics-server
```

### Step 6: Configure Firewall

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow metrics port (from your IP only for security)
sudo ufw allow from YOUR_IP to any port 9090

# Enable firewall
sudo ufw --force enable
```

## Option 2: Using doctl CLI

```bash
# Install doctl
# macOS: brew install doctl
# Linux: snap install doctl

# Authenticate
doctl auth init

# Create SSH key (if not exists)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/ai_chaos_handler -N ""

# Upload SSH key to DigitalOcean
doctl compute ssh-key import ai-chaos-handler --public-key-file ~/.ssh/ai_chaos_handler.pub

# Get SSH key ID
KEY_ID=$(doctl compute ssh-key list --format ID --no-header | head -n 1)

# Create droplet
doctl compute droplet create ai-chaos-target \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc3 \
  --ssh-keys $KEY_ID \
  --wait

# Get droplet IP
DROPLET_IP=$(doctl compute droplet list ai-chaos-target --format PublicIPv4 --no-header)

echo "Droplet created with IP: $DROPLET_IP"

# Continue with Steps 2-6 above
```

## Option 3: Using Terraform

See `vm_provisioning/terraform/` directory for Terraform configurations.

## Security Best Practices

1. **Use SSH keys only** - Disable password authentication
2. **Restrict firewall** - Only allow necessary ports
3. **Limit SSH access** - Use IP whitelisting
4. **Regular updates** - Keep system packages updated
5. **Monitoring** - Set up DigitalOcean monitoring
6. **Snapshots** - Take regular backups before chaos experiments

## Cleanup Script

To stop all chaos scripts:

```bash
#!/bin/bash
# cleanup_all.sh

echo "Stopping all chaos scripts..."

# Stop all known chaos scripts
for script in cpu_spike memory_leak disk_fill net_latency service_kill db_conn_exhaust; do
    sudo /opt/chaos-scripts/${script}.sh stop 2>/dev/null || true
done

# Clean up PID files
sudo rm -f /var/run/chaos-*.pid

# Clean up chaos artifacts
sudo rm -rf /tmp/chaos_fill
sudo rm -f /tmp/test_chaos.db

echo "Cleanup complete"
```

## Testing the Setup

Test chaos scripts:

```bash
# Test CPU spike
sudo /opt/chaos-scripts/cpu_spike.sh start 10 2
sleep 5
top -bn1 | head -20
sudo /opt/chaos-scripts/cpu_spike.sh stop

# Test metrics endpoint
curl http://localhost:9090/metrics
```

## Estimated Costs

- **Basic Droplet**: $24/month (2 vCPU, 4GB RAM)
- **Snapshots**: $0.05/GB per month
- **Bandwidth**: 4TB included, $0.01/GB after

**Recommendation**: Destroy droplet when not in use to save costs.

## Next Steps

1. Update `.env` file with droplet IP and SSH key path
2. Test SSH connection from coordinator
3. Run your first incident with `POST /start_incident`
