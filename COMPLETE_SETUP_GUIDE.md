# 🚀 AI Chaos-Handler - Complete Setup Guide

**Version:** 1.0.0  
**Last Updated:** December 2024  
**Platform:** Linux (Ubuntu/Debian)  
**Prerequisites:** VM already provisioned and configured

This guide will walk you through setting up the AI Chaos-Handler on Linux with an existing VM.

---

## 📋 Table of Contents

1. [Quick Start (Linux Users with VM)](#quick-start-linux-users-with-vm)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)
9. [FAQ](#faq)

---

## Quick Start (Linux Users with VM)

**If you already have a configured VM (from digitalocean-setup.md), start here:**

```bash
# 1. Clone and navigate
cd ~/projects
git clone <your-repo-url>
cd ai-chaos-handler

# 2. Run automated setup
./start.sh

# 3. Configure your VM details
nano .env
# Update: AI_CHAOS_SSH_HOST, AI_CHAOS_SSH_KEY_PATH, AI_CHAOS_SSH_USER

# 4. Test connection
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP

# 5. Generate demo incident
python3 demo.py

# 6. Start frontend (in new terminal)
cd frontend
pnpm dev

# 7. Open browser
firefox http://localhost:3000
```

**Done!** Your system is ready. Skip to [Testing](#testing) section.

---

## Prerequisites

### For Linux Users (Ubuntu/Debian)

**Assumed:** You've already provisioned and configured your VM following `vm_provisioning/digitalocean-setup.md`.

### Required Software

#### 1. Python 3.11 or Higher

**Check if installed:**
```bash
python3 --version
```

**Install on Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
```

**Verify installation:**
```bash
python3 --version  # Should show 3.11.x or higher
pip3 --version
```

#### 2. Node.js 18+ and pnpm

**Check if installed:**
```bash
node --version
pnpm --version
```

**Install on Ubuntu/Debian:**
```bash
# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install pnpm
curl -fsSL https://get.pnpm.io/install.sh | sh -

# Add to PATH (if not automatic)
export PATH="$HOME/.local/share/pnpm:$PATH"

# Verify
node --version   # Should be v18.x or higher
pnpm --version   # Should be 8.x or higher
```

**Alternative - Install via npm:**
```bash
sudo npm install -g pnpm
```

#### 3. Git

**Check if installed:**
```bash
git --version
```

**Install on Ubuntu/Debian:**
```bash
sudo apt install git -y
```

#### 4. SSH Client

Pre-installed on Linux. Verify:
```bash
ssh -V  # Should show OpenSSH version
```

### Recommended Tools

```bash
# Development tools
sudo apt install -y \
  build-essential \
  curl \
  wget \
  vim \
  htop \
  jq

# Optional: tmux for persistent sessions
sudo apt install tmux -y
```

---

## System Requirements

### Your Linux Development Machine

| Component | Minimum | Your System |
|-----------|---------|-------------|
| CPU | 2 cores | Check: `nproc` |
| RAM | 4 GB | Check: `free -h` |
| Disk | 10 GB free | Check: `df -h` |
| OS | Ubuntu 20.04+ | Check: `lsb_release -a` |

**Quick check:**
```bash
echo "CPU Cores: $(nproc)"
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Disk Free: $(df -h / | awk 'NR==2 {print $4}')"
echo "OS: $(lsb_release -d | cut -f2)"
```

### Target VM (Already Configured)

✅ Your VM should already have:
- Ubuntu 22.04 LTS
- SSH access configured
- Chaos scripts deployed to `/opt/chaos-scripts/`
- Metrics server running on port 9090
- Firewall configured

**Verify VM status:**
```bash
# Test SSH connection
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP

# Once connected, verify:
ls -l /opt/chaos-scripts/      # Should show 6 scripts
systemctl status metrics-server # Should be active
curl http://localhost:9090/metrics  # Should return JSON
```

---

## Installation Steps

### Step 1: Clone the Repository

```bash
# Navigate to your projects directory (or wherever you prefer)
cd ~/projects

# Clone the repository (replace with your actual repo URL)
git clone <your-repo-url>
cd ai-chaos-handler

# Check current location
pwd

# Verify files
ls -la
```

**Expected output:**
```bash
drwxr-xr-x  app/
drwxr-xr-x  chaos-scripts/
drwxr-xr-x  frontend/
drwxr-xr-x  tests/
-rw-r--r--  requirements.txt
-rwxr-xr-x  start.sh
-rw-r--r--  COMPLETE_SETUP_GUIDE.md
-rw-r--r--  readme.md
...
```

**If files are missing:**
```bash
# Ensure you're in the right directory
ls -1 | head -5
# Should show: app, chaos-scripts, frontend, etc.
```

### Step 2: Set Up Python Environment

#### Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (Linux)
source venv/bin/activate

# Your prompt should now show (venv)
# Example: (venv) user@hostname:~/projects/ai-chaos-handler$

# Verify activation
which python
# Should output: /home/youruser/projects/ai-chaos-handler/venv/bin/python
```

**Troubleshooting activation:**
```bash
# If source command fails
bash  # Switch to bash if using different shell
source venv/bin/activate

# Or use full path
source ~/projects/ai-chaos-handler/venv/bin/activate
```

#### Install Python Dependencies

```bash
# Ensure venv is activated (you should see (venv) in prompt)
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This will install ~15 packages, takes 1-2 minutes
```

**Verify installation:**
```bash
pip list | grep -E "fastapi|uvicorn|paramiko"
# Should show:
# fastapi      0.104.1
# uvicorn      0.24.0
# paramiko     3.4.0
```

**If installation fails:**
```bash
# Update system packages first
sudo apt update
sudo apt install python3-dev -y

# Try again
pip install -r requirements.txt
```

### Step 3: Set Up Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install pnpm dependencies (takes 2-3 minutes)
pnpm install

# You should see: "Packages: +162" or similar

# Verify installation
ls -la node_modules/ | wc -l
# Should show many directories (160+)

# Return to root
cd ..
```

**If pnpm install fails:**
```bash
# Clear any existing modules
rm -rf node_modules pnpm-lock.yaml

# Try again
pnpm install

# If still fails, check Node version
node --version  # Must be 18.x or higher

# Update Node if needed
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Step 4: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with nano (or vim if you prefer)
nano .env
```

**Update these values with YOUR actual VM details:**

```bash
# SSH Configuration (REQUIRED - UPDATE THESE!)
AI_CHAOS_SSH_KEY_PATH=/home/suraj/.ssh/ai_chaos_handler  # Your actual path
AI_CHAOS_SSH_USER=sre-demo                                 # Your VM user
AI_CHAOS_SSH_HOST=YOUR_VM_IP_HERE                         # Your VM IP
AI_CHAOS_SSH_PORT=22

# Storage (Default is fine)
INCIDENT_STORAGE_PATH=./incidents

# API Security (GENERATE NEW TOKEN!)
API_AUTH_TOKEN=your-super-secret-token-here

# CORS (Default is fine for local dev)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Optional (Leave empty for now)
SLACK_WEBHOOK_URL=
METRICS_PORT=9090

# Server (Default is fine)
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

**Generate a secure API token:**
```bash
# Generate and copy to clipboard
openssl rand -hex 32

# Or generate and set directly in .env
echo "API_AUTH_TOKEN=$(openssl rand -hex 32)" >> .env
```

**Find your VM IP:**
```bash
# If using DigitalOcean, from your local machine:
doctl compute droplet list
# Or check your DigitalOcean dashboard

# Or if you already know it:
cat ~/vm_ip.txt  # If you saved it
```

**Complete example .env:**
```bash
AI_CHAOS_SSH_KEY_PATH=/home/suraj/.ssh/ai_chaos_handler
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=159.89.123.456  # Example IP
AI_CHAOS_SSH_PORT=22
INCIDENT_STORAGE_PATH=./incidents
API_AUTH_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
SLACK_WEBHOOK_URL=
METRICS_PORT=9090
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

**Save and exit nano:**
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

### Step 5: Verify SSH Keys

**Since you already configured your VM, your SSH keys should exist:**

```bash
# Check if SSH key exists
ls -l ~/.ssh/ai_chaos_handler

# If it exists, verify permissions
chmod 600 ~/.ssh/ai_chaos_handler

# Test SSH connection to your VM
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP

# If connection succeeds, you'll see your VM's prompt
# Type 'exit' to return to your local machine
```

**If SSH key doesn't exist:**
```bash
# This shouldn't happen if you followed digitalocean-setup.md
# But if needed, generate new keys:
ssh-keygen -t rsa -b 4096 -f ~/.ssh/ai_chaos_handler -N ""

# Copy to VM
ssh-copy-id -i ~/.ssh/ai_chaos_handler.pub sre-demo@YOUR_VM_IP
```

**Troubleshoot SSH connection:**
```bash
# Test with verbose output
ssh -i ~/.ssh/ai_chaos_handler -v sre-demo@YOUR_VM_IP

# Common issues:
# 1. Wrong permissions: chmod 600 ~/.ssh/ai_chaos_handler
# 2. Wrong IP: Check .env file
# 3. Firewall: Ensure port 22 is open on VM
# 4. Wrong user: Should be 'sre-demo' not 'root'
```

---

## Configuration

Since you've already provisioned your VM using the DigitalOcean guide, let's verify everything is working:

### Verify VM Configuration

```bash
# 1. Test SSH connection
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP "echo 'SSH OK'"

# 2. Check chaos scripts
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP "ls -l /opt/chaos-scripts/"

# 3. Check metrics server
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP "curl -s http://localhost:9090/metrics | jq"

# 4. Test a chaos script (10 second CPU spike)
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP "sudo /opt/chaos-scripts/cpu_spike.sh start 10 2"

# Wait 15 seconds, then verify it stopped
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP "ps aux | grep stress"
```

**Expected results:**
- ✅ SSH connection works
- ✅ 6 chaos scripts exist in `/opt/chaos-scripts/`
- ✅ Metrics server returns JSON with CPU, memory, etc.
- ✅ Chaos scripts can start and stop

**If any check fails, refer to:**
- `vm_provisioning/digitalocean-setup.md` for VM setup
- [Troubleshooting](#troubleshooting) section below

---

## ~~VM Provisioning~~ (Skip - Already Done)

**Note:** Since you've already configured your VM, skip this entire section.

For reference, your VM should have been set up with:

### ✅ Completed VM Setup Checklist

#### A1. Manual Setup via Web Console

1. **Login to DigitalOcean**
   - Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
   - Click "Create" → "Droplets"

2. **Choose Configuration**
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic
   - **CPU Options:** Regular Intel - 2 vCPU, 4GB RAM ($24/mo)
   - **Datacenter:** Choose closest region
   - **Authentication:** SSH keys
     - Click "New SSH Key"
     - Paste your public key from `~/.ssh/ai_chaos_handler.pub`
     - Name it "AI Chaos Handler"
   - **Hostname:** `ai-chaos-target`
   - Click "Create Droplet"

3. **Wait for Creation**
   - Takes 1-2 minutes
   - Note the IP address once created

#### A2. Automated Setup via doctl

```bash
# Install doctl
# macOS
brew install doctl

# Linux
snap install doctl

# Authenticate
doctl auth init
# Enter your API token from DigitalOcean dashboard

# Upload SSH key
doctl compute ssh-key import ai-chaos-handler \
  --public-key-file ~/.ssh/ai_chaos_handler.pub

# Get key ID
KEY_ID=$(doctl compute ssh-key list --format ID,Name --no-header | grep ai-chaos-handler | awk '{print $1}')

# Create droplet
doctl compute droplet create ai-chaos-target \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc3 \
  --ssh-keys $KEY_ID \
  --wait

# Get IP address
DROPLET_IP=$(doctl compute droplet list ai-chaos-target --format PublicIPv4 --no-header)
echo "Droplet IP: $DROPLET_IP"

# Update .env with this IP
```

### Option B: Local VM (For Testing)

#### Using VirtualBox

1. **Download Ubuntu ISO**
   ```bash
   wget https://releases.ubuntu.com/22.04/ubuntu-22.04.3-live-server-amd64.iso
   ```

2. **Create VM in VirtualBox**
   - Name: ai-chaos-target
   - Type: Linux
   - Version: Ubuntu (64-bit)
   - Memory: 4096 MB
   - Hard disk: 25 GB VDI
   - Network: Bridged Adapter

3. **Install Ubuntu**
   - Follow installation wizard
   - Create user: `sre-demo`
   - Install OpenSSH server

4. **Configure SSH**
   ```bash
   # On VM
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh
   
   # From host, copy SSH key
   ssh-copy-id -i ~/.ssh/ai_chaos_handler.pub sre-demo@VM_IP
   ```

### Option C: AWS/GCP/Azure

See `vm_provisioning/cloud-providers.md` for specific instructions.

---

## VM Setup

Once your VM is created, configure it:

### Step 1: Initial Connection

```bash
# Test SSH connection
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP

# If successful, you'll see Ubuntu prompt
```

### Step 2: Update System

```bash
# Update package lists
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  python3 \
  python3-pip \
  stress-ng \
  iproute2 \
  htop \
  vim

# Optional packages
sudo apt install -y nginx docker.io
```

### Step 3: Deploy Chaos Scripts

```bash
# On your local machine, from project root
scp -i ~/.ssh/ai_chaos_handler -r chaos-scripts/* sre-demo@YOUR_VM_IP:/tmp/

# On the VM
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP

# Move scripts to /opt
sudo mkdir -p /opt/chaos-scripts
sudo mv /tmp/*.sh /opt/chaos-scripts/
sudo chmod +x /opt/chaos-scripts/*.sh

# Verify
ls -l /opt/chaos-scripts/
```

**Expected output:**
```
-rwxr-xr-x 1 root root 1234 Dec  3 12:00 cpu_spike.sh
-rwxr-xr-x 1 root root 1234 Dec  3 12:00 memory_leak.sh
-rwxr-xr-x 1 root root 1234 Dec  3 12:00 disk_fill.sh
-rwxr-xr-x 1 root root 1234 Dec  3 12:00 net_latency.sh
-rwxr-xr-x 1 root root 1234 Dec  3 12:00 service_kill.sh
-rwxr-xr-x 1 root root 1234 Dec  3 12:00 db_conn_exhaust.sh
```

### Step 4: Setup Metrics Server

```bash
# Create metrics server script
sudo tee /opt/metrics_server.py << 'EOF'
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
    
    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == '__main__':
    print("Starting metrics server on port 9090...")
    server = HTTPServer(('0.0.0.0', 9090), MetricsHandler)
    server.serve_forever()
EOF

# Make executable
sudo chmod +x /opt/metrics_server.py

# Install psutil
sudo pip3 install psutil

# Create systemd service
sudo tee /etc/systemd/system/metrics-server.service << 'EOF'
[Unit]
Description=Metrics Server for AI Chaos Handler
After=network.target

[Service]
Type=simple
User=sre-demo
ExecStart=/usr/bin/python3 /opt/metrics_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable metrics-server
sudo systemctl start metrics-server

# Verify it's running
sudo systemctl status metrics-server
curl http://localhost:9090/metrics
```

### Step 5: Configure Firewall

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow metrics port (from your IP only)
sudo ufw allow from YOUR_LOCAL_IP to any port 9090

# Enable firewall
sudo ufw --force enable

# Check status
sudo ufw status
```

### Step 6: Test Chaos Scripts

```bash
# Test CPU spike (10 seconds)
sudo /opt/chaos-scripts/cpu_spike.sh start 10 2

# Monitor (in another terminal)
htop

# Wait 10 seconds, then verify it stopped
ps aux | grep stress

# Test metrics endpoint
curl http://localhost:9090/metrics
```

---

## Configuration

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AI_CHAOS_SSH_KEY_PATH` | Yes | - | Path to SSH private key |
| `AI_CHAOS_SSH_USER` | Yes | `sre-demo` | SSH username |
| `AI_CHAOS_SSH_HOST` | Yes | - | VM IP address |
| `AI_CHAOS_SSH_PORT` | No | `22` | SSH port |
| `INCIDENT_STORAGE_PATH` | No | `./incidents` | Where to store incidents |
| `API_AUTH_TOKEN` | Yes | - | API authentication token |
| `ALLOWED_ORIGINS` | No | `*` | CORS allowed origins |
| `SLACK_WEBHOOK_URL` | No | - | Slack webhook for notifications |
| `DO_API_TOKEN` | No | - | DigitalOcean API token |
| `METRICS_PORT` | No | `9090` | Metrics server port on VM |
| `HOST` | No | `0.0.0.0` | Server bind address |
| `PORT` | No | `8000` | Server port |
| `DEBUG` | No | `False` | Enable debug mode |

### Update .env File

```bash
# Edit .env with your actual values
nano .env
```

**Example complete .env:**
```bash
# SSH Configuration
AI_CHAOS_SSH_KEY_PATH=/home/user/.ssh/ai_chaos_handler
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=203.0.113.10
AI_CHAOS_SSH_PORT=22

# Storage
INCIDENT_STORAGE_PATH=./incidents

# API Security
API_AUTH_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://203.0.113.10

# Slack (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Metrics
METRICS_PORT=9090

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

---

## Running the Application

### Option 1: Automated Start (Recommended)

```bash
# Run the start script
./start.sh
```

This will:
- Activate virtual environment
- Install/update dependencies
- Build frontend
- Start the server

**Expected output:**
```
🚀 AI Chaos Handler - Quick Start
==================================
✅ Python OK
✅ Virtual environment created
✅ Dependencies installed
✅ Frontend built
✅ Directory created
==================================
✅ Setup complete!

Starting AI Chaos Handler...
Dashboard will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

Press Ctrl+C to stop
==================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Option 2: Manual Start

```bash
# Activate virtual environment
source venv/bin/activate

# Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

In another terminal:
```bash
# Navigate to frontend
cd frontend

# Start React dev server
npm start
```

### Verify Installation

1. **Check API Health**
   ```bash
   curl http://localhost:8000/health
   ```
   
   Expected response:
   ```json
   {"status":"healthy","version":"1.0.0"}
   ```

2. **Check API Docs**
   Open browser: `http://localhost:8000/docs`

3. **Check Frontend**
   Open browser: `http://localhost:3000`

---

## Testing

### Run Demo Mode (No VM Required)

```bash
# Generate demo incident
python3 demo.py
```

**Expected output:**
```
🎬 AI Chaos Handler - Demo Mode
==================================================
✅ Created incident directory: incidents/inc-demo-001
✅ Created trace.json with 11 events
✅ Created raw_logs.txt
✅ Created metrics.json
✅ Created fix_suggestion.json
✅ Created fix.sh
✅ Created risk_assessment.json
✅ Created report.md
✅ Created slack_summary.txt

==================================================
✅ Demo incident created successfully!

📁 Incident directory: incidents/inc-demo-001
📊 Dashboard URL: http://localhost:3000/dashboard/inc-demo-001
📄 Report: incidents/inc-demo-001/report.md
```

### View Demo Dashboard

```bash
# Open in browser
open http://localhost:3000/dashboard/inc-demo-001
# or
xdg-open http://localhost:3000/dashboard/inc-demo-001
```

### Run Unit Tests

```bash
# Activate venv
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Expected test output:**
```
tests/test_agents.py::test_log_agent_pattern_extraction PASSED
tests/test_agents.py::test_metrics_agent_anomaly_detection PASSED
tests/test_agents.py::test_fixer_agent_generates_suggestions PASSED
tests/test_agents.py::test_tester_agent_risk_assessment PASSED
tests/test_utils.py::test_generate_incident_id PASSED
tests/test_utils.py::test_trace_operations PASSED

====== 6 passed in 2.34s ======
```

### Test Real Incident (With VM)

```bash
# Create test request file
cat > test_incident.json << 'EOF'
{
  "scenario": "cpu_spike",
  "target_vm": {
    "host": "YOUR_VM_IP",
    "port": 22,
    "user": "sre-demo",
    "key_path": "/home/user/.ssh/ai_chaos_handler"
  },
  "options": {
    "trigger_chaos": true,
    "duration": 30
  }
}
EOF

# Trigger incident
curl -X POST http://localhost:8000/start_incident \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_incident.json

# Response will include incident_id
```

Monitor in browser: `http://localhost:3000/dashboard/inc-YYYYMMDD-HHMMSS`

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn app.main:app --port 8001
```

#### 2. SSH Connection Failed

**Error:** `Permission denied (publickey)`

**Solution:**
```bash
# Check key permissions
chmod 600 ~/.ssh/ai_chaos_handler

# Test connection manually
ssh -i ~/.ssh/ai_chaos_handler -v sre-demo@YOUR_VM_IP

# Check if key is on VM
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP 'cat ~/.ssh/authorized_keys'
```

#### 3. Frontend Not Building

**Error:** `Module not found`

**Solution:**
```bash
cd frontend

# Clean install
rm -rf node_modules package-lock.json
npm install

# Build again
npm run build
```

#### 4. Chaos Scripts Not Found

**Error:** `No such file or directory: /opt/chaos-scripts/`

**Solution:**
```bash
# Re-deploy scripts
scp -i ~/.ssh/ai_chaos_handler -r chaos-scripts/* sre-demo@YOUR_VM_IP:/tmp/

# On VM
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP
sudo mkdir -p /opt/chaos-scripts
sudo mv /tmp/*.sh /opt/chaos-scripts/
sudo chmod +x /opt/chaos-scripts/*.sh
```

#### 5. Metrics Server Not Responding

**Error:** `Connection refused on port 9090`

**Solution:**
```bash
# SSH to VM
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP

# Check service status
sudo systemctl status metrics-server

# Restart service
sudo systemctl restart metrics-server

# Check logs
sudo journalctl -u metrics-server -f

# Test locally on VM
curl http://localhost:9090/metrics

# Check firewall
sudo ufw status
```

#### 6. Python Dependencies Conflicts

**Error:** `Version conflict`

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install again
pip install --upgrade pip
pip install -r requirements.txt
```

### Debug Mode

Enable debug logging:

```bash
# In .env
DEBUG=True

# Restart server
```

Check logs:
```bash
# Server logs
tail -f app.log

# Incident traces
cat incidents/inc-*/trace.json | jq
```

---

## Production Deployment

### Preparation

1. **Security Hardening**
   ```bash
   # Generate strong API token
   openssl rand -hex 32 > .api_token
   
   # Set in .env
   API_AUTH_TOKEN=$(cat .api_token)
   
   # Disable debug
   DEBUG=False
   ```

2. **Setup Reverse Proxy (nginx)**
   ```bash
   sudo apt install nginx
   
   sudo tee /etc/nginx/sites-available/ai-chaos-handler << 'EOF'
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   EOF
   
   sudo ln -s /etc/nginx/sites-available/ai-chaos-handler /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Setup SSL/TLS (Let's Encrypt)**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Systemd Service

Create service file:

```bash
sudo tee /etc/systemd/system/ai-chaos-handler.service << 'EOF'
[Unit]
Description=AI Chaos Handler Service
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/ai-chaos-handler
Environment="PATH=/home/yourusername/ai-chaos-handler/venv/bin"
ExecStart=/home/yourusername/ai-chaos-handler/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ai-chaos-handler
sudo systemctl start ai-chaos-handler

# Check status
sudo systemctl status ai-chaos-handler
```

### Monitoring

Setup monitoring with PM2 or Supervisor:

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start "uvicorn app.main:app --host 0.0.0.0 --port 8000" --name ai-chaos-handler

# Save configuration
pm2 save
pm2 startup
```

### Backups

```bash
# Backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups/ai-chaos-handler
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/incidents-$DATE.tar.gz incidents/
tar -czf $BACKUP_DIR/config-$DATE.tar.gz .env

# Keep last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup.sh") | crontab -
```

---

## FAQ

### Q1: Can I run this without a VM?

**A:** Yes! Use the demo mode:
```bash
python3 demo.py
```
This creates a mock incident with all artifacts.

### Q2: How do I add a new chaos scenario?

**A:** 
1. Create script in `chaos-scripts/my_scenario.sh`
2. Add to coordinator's scenario map
3. Deploy to VM
4. Document in USAGE.md

### Q3: Can I use AWS/GCP instead of DigitalOcean?

**A:** Yes! Any Linux VM with SSH access works. Just update the SSH configuration in `.env`.

### Q4: How do I integrate with Slack?

**A:**
1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Add to `.env`: `SLACK_WEBHOOK_URL=https://hooks.slack.com/...`
3. Reports will be sent automatically

### Q5: Is this safe to run on production?

**A:** **NO!** This is designed for dedicated test VMs only. Chaos scripts can disrupt services.

### Q6: How do I stop a running incident?

**A:**
```bash
curl -X POST http://localhost:8000/stop/inc-YYYYMMDD-HHMMSS \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Or use the dashboard Stop button.

### Q7: Can I run multiple incidents concurrently?

**A:** Yes, but it's not recommended. One incident at a time ensures clean results.

### Q8: How do I customize the dashboard?

**A:** Edit `frontend/src/` files. The React components are in `frontend/src/components/`.

### Q9: What if the VM becomes unresponsive?

**A:**
1. SSH directly: `ssh -i ~/.ssh/ai_chaos_handler sre-demo@VM_IP`
2. Run cleanup: `sudo /path/to/cleanup_all.sh`
3. Reboot if necessary: `sudo reboot`

### Q10: How do I upgrade?

**A:**
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
cd frontend && npm install && npm run build
```

---

## Next Steps

✅ **Setup Complete!** You now have:
- Working AI Chaos-Handler installation
- Configured VM with chaos scripts
- Running backend and frontend
- Demo incident to explore

**Recommended next actions:**

1. **Read Documentation**
   - [USAGE.md](USAGE.md) - API and usage guide
   - [STRUCTURE.md](STRUCTURE.md) - Architecture details

2. **Run Test Incident**
   ```bash
   # Use demo mode first
   python3 demo.py
   
   # Then try real VM
   # Edit test_incident.json and trigger
   ```

3. **Explore Dashboard**
   - View real-time traces
   - Download reports
   - Check risk assessments

4. **Customize**
   - Add new chaos scenarios
   - Modify agents
   - Integrate with your tools

5. **Deploy to Production** (staging environment)
   - Setup systemd service
   - Configure nginx
   - Enable SSL
   - Setup monitoring

---

## Support & Resources

- **Documentation**: All `.md` files in project root
- **Examples**: `examples/` directory
- **Tests**: `tests/` directory
- **Issues**: Create GitHub issue
- **Community**: Join discussions

---

## License

MIT License - See [LICENSE](LICENSE) file

---

**Congratulations! 🎉 Your AI Chaos-Handler is ready to use!**

For questions or issues, refer to the [Troubleshooting](#troubleshooting) section or create an issue on GitHub.
