# 🚀 AI Chaos Handler - Complete Setup Guide

**Platform:** Linux (Ubuntu/Debian)  
**Prerequisites:** VM already provisioned  
**Time:** 15-20 minutes

---

## 📋 Quick Navigation

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Your Linux Development Machine:**
- Ubuntu 20.04+ or Debian 10+
- 2+ CPU cores
- 4+ GB RAM
- 10 GB free disk space
- Internet connection

**Quick Check:**
```bash
echo "CPU Cores: $(nproc)"
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Disk Free: $(df -h / | awk 'NR==2 {print $4}')"
echo "OS: $(lsb_release -d | cut -f2)"
```

### Required Software

#### 1. Python 3.11+

```bash
# Check version
python3 --version

# Install if needed
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y

# Verify
python3 --version  # Should show 3.11.x or higher
```

#### 2. Node.js 18+ and pnpm

```bash
# Check versions
node --version
pnpm --version

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install pnpm
curl -fsSL https://get.pnpm.io/install.sh | sh -

# Reload shell or run:
export PATH="$HOME/.local/share/pnpm:$PATH"

# Verify
node --version   # v18.x or higher
pnpm --version   # 8.x or higher
```

#### 3. SSH (Pre-installed on Linux)

```bash
# Verify
ssh -V  # Should show OpenSSH version
```

### Target VM Requirements

✅ **Your VM should already have:**
- Ubuntu 22.04 LTS
- SSH access configured
- SSH key: `~/.ssh/ai_chaos_handler`
- User: `sre-demo`
- Chaos scripts in `/opt/chaos-scripts/`
- Metrics server on port 9090

**Verify VM:**
```bash
# Test SSH
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP "echo 'VM OK'"

# Check chaos scripts
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP "ls /opt/chaos-scripts/"

# Check metrics server
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP "curl -s http://localhost:9090/metrics"
```

---

## Installation

### Step 1: Clone Repository

```bash
# Navigate to projects directory
cd ~/projects

# Clone (replace with your repo URL)
git clone <your-repo-url>
cd ai-chaos-handler

# Verify files
ls -la
# Should see: app/, chaos-scripts/, frontend/, requirements.txt, start.sh, etc.
```

### Step 2: Backend Setup

#### Create Python Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (Linux)
source venv/bin/activate

# Your prompt should show: (venv)

# Verify activation
which python
# Should output: /home/yourusername/projects/ai-chaos-handler/venv/bin/python
```

#### Install Python Dependencies

```bash
# Ensure venv is activated
pip install --upgrade pip

# Install all dependencies (includes AI packages)
pip install -r requirements.txt

# This installs:
# - FastAPI, Uvicorn (backend)
# - Paramiko (SSH)
# - LangChain, Google Gemini (AI)
# - Pytest (testing)
# Takes 1-2 minutes
```

**Verify:**
```bash
pip list | grep -E "fastapi|uvicorn|paramiko|langchain"
# Should show all packages installed
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies with pnpm
pnpm install
# Takes 2-3 minutes

# Return to root
cd ..
```

**Verify:**
```bash
ls frontend/node_modules/ | wc -l
# Should show 160+ packages
```

---

## Configuration

### Step 1: Create .env File

```bash
# Copy example
cp .env.example .env

# Edit
nano .env
```

### Step 2: Update Required Variables

**Essential configuration:**

```bash
# SSH Configuration (REQUIRED - Update with YOUR values)
AI_CHAOS_SSH_KEY_PATH=/home/suraj/.ssh/ai_chaos_handler
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=YOUR_VM_IP_HERE
AI_CHAOS_SSH_PORT=22

# Google Gemini AI (REQUIRED - Get from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=AIzaSy_your_actual_gemini_key_here
GOOGLE_MODEL=gemini-pro
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# API Security (REQUIRED - Generate new token)
API_AUTH_TOKEN=your-super-secret-token-here

# Storage (Default is fine)
INCIDENT_STORAGE_PATH=./incidents

# CORS (Default is fine for local dev)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Optional (Leave empty for now)
SLACK_WEBHOOK_URL=
METRICS_PORT=9090

# Server (Default is fine)
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

### Step 3: Get Gemini API Key

**This is required for AI agents to work:**

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)
5. Paste into `.env` as `GOOGLE_API_KEY`

**FREE tier includes:**
- 60 requests per minute
- Unlimited daily requests
- No credit card required

### Step 4: Generate API Token

```bash
# Generate secure token
openssl rand -hex 32

# Copy output and paste into .env as API_AUTH_TOKEN
```

### Step 5: Verify Configuration

```bash
# Check .env has required values
grep -E "SSH_HOST|GOOGLE_API_KEY|API_AUTH_TOKEN" .env

# Should show your actual values (not example placeholders)
```

**Save and exit nano:**
- Press `Ctrl + O` to save
- Press `Enter` to confirm
- Press `Ctrl + X` to exit

### Step 6: Verify SSH Connection

```bash
# Test SSH to your VM
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP

# If successful, you'll see VM prompt
# Type 'exit' to return

# Test from config
SSH_KEY=$(grep SSH_KEY_PATH .env | cut -d'=' -f2)
SSH_USER=$(grep SSH_USER .env | cut -d'=' -f2)
SSH_HOST=$(grep SSH_HOST .env | cut -d'=' -f2)
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "echo 'Config OK'"
```

---

## Running the Application

### Option 1: Quick Start (Recommended)

```bash
# Run automated start script
./start.sh
```

**Expected output:**
```
🚀 AI Chaos Handler - Quick Start
==================================
✅ Python OK
✅ Virtual environment activated
✅ Dependencies up to date
✅ Frontend built
✅ Directories created
==================================
✅ Setup complete!

Starting AI Chaos Handler...
Dashboard: http://localhost:8000
API docs: http://localhost:8000/docs

Press Ctrl+C to stop
==================================

INFO: Uvicorn running on http://0.0.0.0:8000
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
# Activate venv
source venv/bin/activate

# Start backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
# Navigate to frontend
cd frontend

# Start dev server
pnpm dev

# Opens at http://localhost:3000
```

### Verify Installation

1. **API Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `{"status":"healthy","version":"1.0.0"}`

2. **API Documentation:**
   Open browser: http://localhost:8000/docs

3. **Frontend:**
   Open browser: http://localhost:3000

---

## Testing

### 1. Demo Mode (No VM Required)

```bash
# Generate demo incident with AI analysis
python3 demo.py
```

**Expected output:**
```
🎬 AI Chaos Handler - Demo Mode
==================================================
✅ Created incident: incidents/inc-demo-20241203-135430
✅ Created trace.jsonl with AI agent events
✅ Created raw_logs.txt
✅ Created log_analysis.json (AI)
✅ Created metrics.json
✅ Created metrics_analysis.json (AI)
✅ Created fix_suggestions.json (AI)
✅ Created risk_assessment.json (AI)
✅ Created incident_report.md (AI)
==================================================
✅ Demo incident created!

📁 Incident: incidents/inc-demo-20241203-135430
🌐 Dashboard: http://localhost:3000/dashboard/inc-demo-20241203-135430
📄 Report: incidents/inc-demo-20241203-135430/incident_report.md
```

### 2. View AI Analysis

```bash
# View AI-generated incident report
cat incidents/inc-demo-*/incident_report.md

# View AI log analysis
cat incidents/inc-demo-*/log_analysis.json | jq

# View AI fix suggestions
cat incidents/inc-demo-*/fix_suggestions.json | jq

# View AI risk assessment
cat incidents/inc-demo-*/risk_assessment.json | jq
```

### 3. View in Dashboard

```bash
# Open dashboard
xdg-open http://localhost:3000

# Or manually open browser to:
# http://localhost:3000/dashboard/inc-demo-XXXXXXXX
```

### 4. Test with Real VM

```bash
# Create test request
cat > test_incident.json << 'EOFTEST'
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
EOFTEST

# Trigger incident
curl -X POST http://localhost:8000/start_incident \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @test_incident.json

# Response includes incident_id
# Monitor in dashboard: http://localhost:3000/dashboard/inc-XXXXXX
```

---

## Troubleshooting

### 1. Port Already in Use

**Error:** `Address already in use`

```bash
# Find process on port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn app.main:app --port 8001
```

### 2. SSH Connection Failed

**Error:** `Permission denied (publickey)`

```bash
# Check key permissions
chmod 600 ~/.ssh/ai_chaos_handler

# Test connection with verbose
ssh -i ~/.ssh/ai_chaos_handler -v sre-demo@YOUR_VM_IP

# Verify key is on VM
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP 'cat ~/.ssh/authorized_keys'
```

### 3. Gemini API Key Error

**Error:** `GOOGLE_API_KEY not set` or `Invalid API key`

```bash
# Check .env file
cat .env | grep GOOGLE_API_KEY

# Should show: GOOGLE_API_KEY=AIzaSy...

# If empty, get key from: https://makersuite.google.com/app/apikey
nano .env
# Add: GOOGLE_API_KEY=AIzaSy_your_actual_key_here
```

### 4. Module Not Found

**Error:** `Module 'langchain' not found`

```bash
# Activate venv
source venv/bin/activate

# Install AI dependencies
pip install langchain==0.1.20 langchain-google-genai==0.0.6 google-generativeai==0.3.2

# Or reinstall all
pip install -r requirements.txt
```

### 5. Frontend Build Errors

**Error:** `Module not found` or build fails

```bash
cd frontend

# Clean install
rm -rf node_modules pnpm-lock.yaml
pnpm install

# Check Node version
node --version  # Must be 18.x or higher

# Build again
pnpm build
```

### 6. VM Not Responding

```bash
# SSH directly
ssh -i ~/.ssh/ai_chaos_handler sre-demo@YOUR_VM_IP

# Check chaos scripts are not running
ps aux | grep -E "stress|chaos"

# Kill if found
sudo pkill -f stress
sudo pkill -f chaos

# Check metrics server
sudo systemctl status metrics-server

# Restart if needed
sudo systemctl restart metrics-server
```

### 7. AI Analysis Fails

**Error:** `AI analysis unavailable` in results

```bash
# Check Gemini API key
echo $GOOGLE_API_KEY  # Should not be empty

# Test LLM client
python3 << 'EOFPY'
import os
os.environ['GOOGLE_API_KEY'] = 'your-key-here'
from app.utils.llm_client import get_llm_client
llm = get_llm_client()
print('✅ LLM Client OK')
EOFPY

# Check API rate limits (60/min on free tier)
# Wait a minute and retry
```

---

## Quick Reference

### Start Services

```bash
# Backend
./start.sh

# Or manually
source venv/bin/activate && uvicorn app.main:app --reload
```

### Stop Services

```bash
# Press Ctrl+C in terminal

# Or kill process
pkill -f uvicorn
```

### View Logs

```bash
# Application logs
tail -f app.log

# Incident traces
cat incidents/inc-*/trace.jsonl | jq

# AI analysis
cat incidents/inc-*/log_analysis.json | jq
```

### Reset Environment

```bash
# Clean Python
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Clean Frontend
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
cd ..

# Clean incidents
rm -rf incidents/
```

---

## Next Steps

✅ **Setup Complete!**

**Now you can:**

1. **Read AI Implementation Details**
   - See `AI_AGENTS_IMPLEMENTED.md` for AI agent architecture
   - See `ENV_API_CONFIGURATION.md` for all config options

2. **Explore the Dashboard**
   - View incident traces
   - Read AI analysis
   - Download reports

3. **Create Real Incidents**
   - Use API to trigger chaos scenarios
   - Let AI agents analyze and suggest fixes
   - View risk assessments

4. **Integrate with Your Stack**
   - Add Slack notifications
   - Customize chaos scenarios
   - Build on the AI agents

---

## Support

**Documentation:**
- `AI_AGENTS_IMPLEMENTED.md` - AI agent details
- `ENV_API_CONFIGURATION.md` - Configuration reference
- `USAGE.md` - API usage guide
- `readme.md` - Project overview

**Need Help?**
1. Check troubleshooting sections above
2. Review AI_AGENTS_IMPLEMENTED.md
3. Verify .env configuration
4. Check logs: `tail -f app.log`

---

**🎉 Congratulations! Your AI Chaos Handler is ready!**

Generate your first AI-powered incident with: `python3 demo.py`
