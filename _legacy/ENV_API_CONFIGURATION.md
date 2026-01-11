# 🔐 Environment Variables & API Configuration Guide

**Complete reference for all environment variables, API keys, and configuration options**

---

## 📋 Table of Contents

1. [Environment Variables Reference](#environment-variables-reference)
2. [API Keys & Tokens Setup](#api-keys--tokens-setup)
3. [Slack Integration](#slack-integration)
4. [AI Agent Configuration (LLM Integration)](#ai-agent-configuration-llm-integration)
5. [Security Best Practices](#security-best-practices)
6. [Configuration Examples](#configuration-examples)

---

## Environment Variables Reference

### Complete `.env` File Template

```bash
# ============================================
# SSH Configuration (REQUIRED)
# ============================================
AI_CHAOS_SSH_KEY_PATH=/home/suraj/.ssh/ai_chaos_handler
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=159.89.123.456
AI_CHAOS_SSH_PORT=22

# ============================================
# Storage Configuration
# ============================================
INCIDENT_STORAGE_PATH=./incidents

# ============================================
# API Authentication (REQUIRED)
# ============================================
API_AUTH_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6

# ============================================
# AI/LLM Configuration (REQUIRED FOR REAL AI AGENTS)
# ============================================
# Choose ONE LLM provider below and configure accordingly

# Option 1: OpenAI (Recommended)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_BASE_URL=https://api.openai.com/v1

# Option 2: Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-opus-20240229

# Option 3: Google Gemini
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_MODEL=gemini-pro

# Option 4: Azure OpenAI
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Option 5: Local LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:70b

# Option 6: LM Studio (Local)
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=local-model

# LLM Settings
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=60

# ============================================
# CORS Configuration
# ============================================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# ============================================
# Slack Integration (OPTIONAL)
# ============================================
SLACK_WEBHOOK_URL=<url>
SLACK_CHANNEL=#incidents
SLACK_USERNAME=AI Chaos Handler
SLACK_ICON_EMOJI=:robot_face:

# ============================================
# Metrics Configuration
# ============================================
METRICS_PORT=9090
METRICS_COLLECTION_INTERVAL=5

# ============================================
# Server Configuration
# ============================================
HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO

# ============================================
# DigitalOcean API (OPTIONAL)
# ============================================
DO_API_TOKEN=dop_v1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# Agent Configuration
# ============================================
USE_REAL_AI_AGENTS=True
AGENT_REASONING_DEPTH=medium  # low, medium, high
ENABLE_AGENT_MEMORY=True
MAX_AGENT_RETRIES=3
AGENT_TIMEOUT=120

# ============================================
# Advanced Settings
# ============================================
ENABLE_PDF_REPORTS=False  # Requires wkhtmltopdf
ENABLE_SLACK_NOTIFICATIONS=False
ENABLE_AUTO_REMEDIATION=False  # Dangerous! Auto-execute fixes
MAX_CONCURRENT_INCIDENTS=1
```

---

## API Keys & Tokens Setup

### 1. API_AUTH_TOKEN (Required)

**Purpose:** Secures your FastAPI endpoints

**How to generate:**
```bash
# Method 1: Using OpenSSL (Recommended)
openssl rand -hex 32

# Method 2: Using Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Method 3: Using /dev/urandom
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1
```

**Example:**
```bash
API_AUTH_TOKEN=c4f8a912b3d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1
```

**How it's used:**
- Authenticates all API requests
- Must be included in `Authorization: Bearer <token>` header
- Frontend sends this with every request
- Without valid token, requests are rejected with 401

**Example API call:**
```bash
curl -X POST http://localhost:8000/start_incident \
  -H "Authorization: Bearer c4f8a912b3d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### 2. SSH Configuration (Required)

**Purpose:** Connect to target VM for chaos injection and data collection

**SSH_KEY_PATH:**
```bash
# Full path to your private SSH key
AI_CHAOS_SSH_KEY_PATH=/home/suraj/.ssh/ai_chaos_handler

# Find your key location
ls -l ~/.ssh/
```

**SSH_HOST:**
```bash
# Your VM's public IP address
AI_CHAOS_SSH_HOST=159.89.123.456

# Get from DigitalOcean
doctl compute droplet list

# Or from dashboard
# DigitalOcean Dashboard > Droplets > Your Droplet > Public IP
```

**SSH_USER:**
```bash
# Username on target VM (default: sre-demo)
AI_CHAOS_SSH_USER=sre-demo
```

**Test SSH config:**
```bash
ssh -i $AI_CHAOS_SSH_KEY_PATH $AI_CHAOS_SSH_USER@$AI_CHAOS_SSH_HOST
```

### 3. LLM API Keys (Required for Real AI Agents)

Currently, your agents are **static/rule-based**. To make them truly intelligent AI agents, you need an LLM API key.

#### Option A: OpenAI (Recommended - Most Powerful)

**Get API Key:**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-proj-` or `sk-`)
6. **Save it immediately** - you won't see it again!

**Cost:** ~$0.002 per incident (very cheap)

**Configuration:**
```bash
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz1234567890abcdefgh
OPENAI_MODEL=gpt-4-turbo-preview  # Or gpt-3.5-turbo (cheaper)
OPENAI_BASE_URL=https://api.openai.com/v1
```

**Models to choose:**
- `gpt-4-turbo-preview` - Most intelligent, $0.01/1K tokens
- `gpt-4` - Very intelligent, $0.03/1K tokens
- `gpt-3.5-turbo` - Fast and cheap, $0.0005/1K tokens (recommended for testing)

#### Option B: Anthropic Claude

**Get API Key:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create new key
5. Copy key (starts with `sk-ant-`)

**Configuration:**
```bash
ANTHROPIC_API_KEY=sk-ant-1234567890abcdefghijklmnopqrstuvwxyz1234567890
ANTHROPIC_MODEL=claude-3-opus-20240229
```

**Models:**
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fast and cheap

#### Option C: Google Gemini (Free tier available!)

**Get API Key:**
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

**Configuration:**
```bash
GOOGLE_API_KEY=AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890
GOOGLE_MODEL=gemini-pro
```

**Free tier:** 60 requests per minute!

#### Option D: Local LLM (Ollama - Free but requires GPU)

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2:70b  # or llama2:13b for less RAM

# Start Ollama server
ollama serve
```

**Configuration:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:70b
```

**Pros:** Free, private, no internet required
**Cons:** Requires powerful GPU (24GB+ VRAM for 70B model)

---

## Slack Integration

### What is Slack Integration?

**Purpose:** Send real-time notifications to your team's Slack channel when:
- 🚨 New incident starts
- 📊 Incident completes with summary
- ⚠️ High-risk fixes are proposed
- ✅ Remediation is successful
- ❌ Errors occur during incident handling

### Why Use Slack?

**Benefits:**
1. **Team Awareness** - Everyone knows when incidents happen
2. **Fast Response** - Get notified immediately on mobile
3. **Historical Record** - Incidents logged in channel
4. **Collaboration** - Team can discuss in thread
5. **Dashboard Link** - Direct link to incident dashboard

**Example Slack Message:**
```
🚨 Incident Report: inc-20241203-130000

Time: 2024-12-03 13:00:00 UTC

Agents Executed: 5
Anomalies Detected: 2
Fixes Proposed: 3
Risk Level: Medium

📊 Full Report: http://localhost:3000/dashboard/inc-20241203-130000

Generated by AI Chaos Handler
```

### Setup Slack Webhook

**Step 1: Create Slack App**
1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name: "AI Chaos Handler"
5. Select your workspace

**Step 2: Enable Incoming Webhooks**
1. In your app settings, click "Incoming Webhooks"
2. Toggle "Activate Incoming Webhooks" to ON
3. Click "Add New Webhook to Workspace"
4. Select channel (e.g., #incidents or #sre-alerts)
5. Click "Allow"

**Step 3: Copy Webhook URL**
```
<url>
```

**Step 4: Add to .env**
```bash
SLACK_WEBHOOK_URL=<url>
SLACK_CHANNEL=#incidents  # Optional override
ENABLE_SLACK_NOTIFICATIONS=True
```

**Test Webhook:**
```bash
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test from AI Chaos Handler! 🚀"}'
```

### When Slack Notifications are Sent

1. **Incident Start:**
   ```
   🚀 New incident started: inc-20241203-130000
   Scenario: cpu_spike
   Target: 159.89.123.456
   Dashboard: http://localhost:3000/dashboard/inc-20241203-130000
   ```

2. **Incident Complete:**
   ```
   ✅ Incident complete: inc-20241203-130000
   Duration: 2m 15s
   Anomalies: 2
   Fixes proposed: 3
   Risk assessment: Medium
   Report: [Download]
   ```

3. **High Risk Alert:**
   ```
   ⚠️ HIGH RISK fix proposed in inc-20241203-130000
   Title: Restart database service
   Risk score: 8/10
   Approval required before execution
   ```

4. **Error Alert:**
   ```
   ❌ Error in incident inc-20241203-130000
   Agent: FixerAgent
   Error: SSH connection timeout
   Check logs for details
   ```

---

## AI Agent Configuration (LLM Integration)

### Current vs Real AI Agents

#### Current Implementation (Static/Rule-Based)

Your agents currently use **hardcoded rules**:

**Example - Current LogAgent:**
```python
def analyze_logs(self, logs):
    patterns = []
    if "ERROR" in logs:
        patterns.append({"type": "error", "message": "Found ERROR"})
    if "out of memory" in logs.lower():
        patterns.append({"type": "oom", "message": "OOM detected"})
    return patterns
```

**Limitations:**
- ❌ Can't understand context
- ❌ Misses subtle patterns
- ❌ No reasoning capability
- ❌ Static responses only
- ❌ Can't learn from past incidents

#### Real AI Agents (LLM-Powered)

With LLM integration, agents become **truly intelligent**:

**Example - Real AI LogAgent:**
```python
def analyze_logs(self, logs):
    prompt = f"""
    You are an expert SRE analyzing system logs.
    
    Logs:
    {logs}
    
    Analyze these logs and:
    1. Identify all errors and warnings
    2. Explain the root cause
    3. Assess severity (low/medium/high)
    4. Suggest investigation steps
    
    Return structured JSON.
    """
    
    response = llm.complete(prompt)
    return parse_json(response)
```

**Benefits:**
- ✅ Understands context and relationships
- ✅ Explains reasoning ("Because X happened, Y will occur")
- ✅ Learns from patterns
- ✅ Natural language understanding
- ✅ Can handle novel situations
- ✅ Provides detailed explanations

### How to Enable Real AI Agents

**Step 1: Install LangChain (if not already installed)**
```bash
# Activate venv
source venv/bin/activate

# Install LangChain
pip install langchain openai anthropic google-generativeai

# Or add to requirements.txt
echo "langchain==0.1.0" >> requirements.txt
echo "openai==1.10.0" >> requirements.txt
pip install -r requirements.txt
```

**Step 2: Configure LLM in .env**
```bash
# Choose your provider
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-3.5-turbo  # Start with this (cheap)

# Enable AI agents
USE_REAL_AI_AGENTS=True
```

**Step 3: Update Agent Code**

I'll need to modify the agents to use LLM. Here's what needs to change:

**File: `app/agents/log_agent.py`**
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

class LogAgent(BaseAgent):
    def __init__(self, incident_id, context):
        super().__init__(incident_id, context)
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=0.7
        )
    
    async def run(self):
        logs = self._collect_logs()
        
        # Use LLM to analyze
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert SRE analyzing system logs..."),
            ("user", "Analyze these logs:\n\n{logs}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"logs": logs})
        
        analysis = parse_llm_response(response.content)
        
        self._save_analysis(analysis)
        return {"status": "success", "analysis": analysis}
```

**Similar changes needed for:**
- `metrics_agent.py` - AI analyzes metrics patterns
- `fixer_agent.py` - AI generates intelligent fixes
- `tester_agent.py` - AI assesses risks with reasoning
- `reporter_agent.py` - AI writes comprehensive reports

### Agent Reasoning Levels

```bash
AGENT_REASONING_DEPTH=medium
```

**Options:**
- `low` - Fast, simple analysis (1-2 LLM calls per agent)
- `medium` - Balanced reasoning (3-4 LLM calls per agent) **[Recommended]**
- `high` - Deep analysis with chain-of-thought (5+ LLM calls per agent)

**Cost comparison (per incident with OpenAI gpt-3.5-turbo):**
- Low: ~$0.001 (~100 tokens)
- Medium: ~$0.005 (~500 tokens)
- High: ~$0.02 (~2000 tokens)

---

## Security Best Practices

### 1. Protect API Keys

**Never commit secrets to git:**
```bash
# Add to .gitignore (already done)
.env
.env.local
*.key
```

**Use environment variables only:**
```bash
# Bad - hardcoded
OPENAI_API_KEY = "sk-proj-1234567890..."

# Good - from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### 2. Rotate Tokens Regularly

```bash
# Rotate API_AUTH_TOKEN every 30 days
openssl rand -hex 32 > .new_token
# Update .env
# Update frontend .env
# Restart services
```

### 3. Restrict SSH Keys

```bash
# Proper permissions
chmod 600 ~/.ssh/ai_chaos_handler
chmod 644 ~/.ssh/ai_chaos_handler.pub

# Restrict to specific IP
# In VM: /etc/ssh/sshd_config
AllowUsers sre-demo@YOUR_LOCAL_IP
```

### 4. Use Read-Only API Keys

**For LLM providers:**
- OpenAI: Use project-scoped keys with spending limits
- Anthropic: Set rate limits on keys
- Google: Use API key restrictions (HTTP referrers, IP addresses)

### 5. Monitor API Usage

**OpenAI:**
- Dashboard: https://platform.openai.com/usage
- Set spending alerts
- Review usage logs

**Set budget limits:**
```bash
# In OpenAI dashboard:
# Settings > Billing > Usage limits
# Set hard limit: $10/month
```

---

## Configuration Examples

### Example 1: Development (Local with OpenAI)

```bash
# .env for local development
AI_CHAOS_SSH_KEY_PATH=/home/suraj/.ssh/ai_chaos_handler
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=192.168.1.100  # Local VM
AI_CHAOS_SSH_PORT=22

INCIDENT_STORAGE_PATH=./incidents

API_AUTH_TOKEN=dev-token-change-in-production

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo
USE_REAL_AI_AGENTS=True

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# No Slack in dev
ENABLE_SLACK_NOTIFICATIONS=False

HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=DEBUG
```

### Example 2: Production (DigitalOcean + Claude)

```bash
# .env for production
AI_CHAOS_SSH_KEY_PATH=/opt/chaos-handler/.ssh/id_rsa
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=159.89.123.456
AI_CHAOS_SSH_PORT=22

INCIDENT_STORAGE_PATH=/var/incidents

API_AUTH_TOKEN=c4f8a912b3d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-sonnet-20240229
USE_REAL_AI_AGENTS=True
AGENT_REASONING_DEPTH=high

ALLOWED_ORIGINS=https://chaos.yourdomain.com

# Slack enabled
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00/B00/XXXX
ENABLE_SLACK_NOTIFICATIONS=True
SLACK_CHANNEL=#sre-alerts

HOST=0.0.0.0
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

### Example 3: Budget-Friendly (Free Gemini)

```bash
# .env with Google Gemini (FREE!)
AI_CHAOS_SSH_KEY_PATH=/home/suraj/.ssh/ai_chaos_handler
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=159.89.123.456
AI_CHAOS_SSH_PORT=22

INCIDENT_STORAGE_PATH=./incidents

API_AUTH_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

# Google Gemini - FREE!
GOOGLE_API_KEY=AIzaSyABCDEFGHIJKLMNOPQRSTUVWXYZ
GOOGLE_MODEL=gemini-pro
USE_REAL_AI_AGENTS=True
AGENT_REASONING_DEPTH=medium

ALLOWED_ORIGINS=http://localhost:3000

HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### Example 4: Privacy-First (Local Ollama)

```bash
# .env with local LLM (no internet required!)
AI_CHAOS_SSH_KEY_PATH=/home/suraj/.ssh/ai_chaos_handler
AI_CHAOS_SSH_USER=sre-demo
AI_CHAOS_SSH_HOST=192.168.1.100
AI_CHAOS_SSH_PORT=22

INCIDENT_STORAGE_PATH=./incidents

API_AUTH_TOKEN=local-dev-token-123456

# Ollama (running locally)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2:13b
USE_REAL_AI_AGENTS=True
AGENT_REASONING_DEPTH=low  # Local models are slower

HOST=0.0.0.0
PORT=8000
DEBUG=True
```

---

## Frontend Environment Variables

**File: `frontend/.env`**

```bash
# API Connection
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TOKEN=c4f8a912b3d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1

# Polling Configuration
VITE_POLL_INTERVAL=2000  # milliseconds

# Feature Flags
VITE_ENABLE_AUTO_REFRESH=true
VITE_ENABLE_NOTIFICATIONS=true
```

**Must match backend `API_AUTH_TOKEN`!**

---

## Quick Reference

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `API_AUTH_TOKEN` | ✅ Yes | None | API authentication |
| `OPENAI_API_KEY` | For AI | None | OpenAI integration |
| `SLACK_WEBHOOK_URL` | Optional | None | Slack notifications |
| `AI_CHAOS_SSH_HOST` | ✅ Yes | None | Target VM IP |
| `USE_REAL_AI_AGENTS` | Optional | False | Enable LLM agents |
| `DEBUG` | Optional | False | Debug logging |

---

## Troubleshooting

### "Invalid API token"
- Check `API_AUTH_TOKEN` matches in backend `.env` and frontend `.env`
- Regenerate token: `openssl rand -hex 32`

### "OpenAI API error"
- Verify `OPENAI_API_KEY` starts with `sk-proj-` or `sk-`
- Check billing: https://platform.openai.com/account/billing
- Test key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

### "Slack webhook failed"
- Test webhook URL with curl
- Check webhook isn't deleted in Slack app settings
- Ensure channel still exists

### "SSH connection failed"
- Verify `AI_CHAOS_SSH_HOST` is correct
- Test manually: `ssh -i $AI_CHAOS_SSH_KEY_PATH $AI_CHAOS_SSH_USER@$AI_CHAOS_SSH_HOST`
- Check firewall allows port 22

---

## Next Steps

1. ✅ Generate all required tokens
2. ✅ Choose LLM provider (OpenAI recommended)
3. ✅ Setup Slack webhook (optional but useful)
4. ✅ Update `.env` file
5. ✅ Restart application
6. ✅ Run test incident: `python3 demo.py`
7. ✅ Check Slack for notification

**Need help?** See [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) or create an issue.
