# AI Chaos Handler - Simple Guide

## 🚀 How It Works

### **AI Agents Are Always Watching**

The system automatically monitors your VM **every 30 seconds** for:
- High CPU usage (> 80%)
- High memory usage (> 85%)  
- Error logs (> 10 errors)

When chaos is detected, AI agents **automatically create an incident** and investigate.

---

## 📁 Output Files (Only 4)

Each incident generates **exactly 4 files**:

1. **`logs.txt`** - Raw VM logs (journal, syslog, errors)
2. **`metrics.json`** - System metrics (CPU, memory, disk, etc.)
3. **`diagnostic_analysis.md`** - AI analysis (root cause, severity, recommendations)
4. **`fix_commands.sh`** - Bash script to fix the issue

---

## ⚙️ Setup

### 1. Configure VM in `.env`

```bash
# VM Configuration (required for auto-monitoring)
VM_HOST=your-vm-ip-or-hostname
VM_PORT=22
VM_USER=root
VM_KEY_PATH=/path/to/ssh/key.pem

# API Configuration
API_AUTH_TOKEN=your-secret-token
GOOGLE_API_KEY=your-google-api-key
```

### 2. Start the system

```bash
./start.sh
```

**That's it!** Auto-monitoring starts automatically.

---

## 🎯 Usage

### Auto-Monitoring (Default - Always On)

Just start the system. AI agents will watch your VM automatically.

```bash
# Check monitor status
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "auto_monitor": true,
  "vm_configured": true
}
```

### Manual Incident Trigger

You can also manually trigger incidents:

```bash
curl -X POST http://localhost:8000/start_incident \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "cpu_spike",
    "target_vm": {
      "host": "192.168.1.100",
      "port": 22,
      "user": "root",
      "key_path": "/home/user/.ssh/id_rsa"
    }
  }'
```

---

## 📊 Dashboard

Visit: **http://localhost:3001**

- View all incidents (real-time, no static data)
- Click any incident to view all 4 files
- See live VM metrics

---

## 🧪 Testing

### Cause CPU Chaos

```bash
ssh root@your-vm "stress-ng --cpu 8 --timeout 60s"
```

Wait 30 seconds. AI agents will:
1. Detect high CPU
2. Create incident automatically
3. Collect logs & metrics
4. Analyze with AI
5. Generate fix script

Check dashboard to see the new incident!

---

## 🔧 Configuration

### Change Check Interval

Edit `app/auto_monitor.py`:

```python
self.check_interval = 30  # Change to 60 for every 60 seconds
```

### Change Thresholds

Edit `app/auto_monitor.py`:

```python
if cpu > 80:  # Change 80 to your threshold
    return {"healthy": False, "type": "cpu_spike", "value": cpu}
```

### Disable Auto-Monitoring

Set in `.env`:
```bash
VM_HOST=  # Leave empty
```

---

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check system health & monitor status |
| `/start_incident` | POST | Manually trigger incident |
| `/incidents` | GET | List all incidents |
| `/incidents/{id}` | GET | Get incident details & files |
| `/agents/status` | GET | Get AI agent status |

---

## 🎬 Example Workflow

1. **Start system**: `./start.sh`
2. **Verify monitoring**: `curl http://localhost:8000/health`
3. **Cause chaos**: SSH to VM and run `stress-ng`
4. **Wait 30 seconds**: AI detects anomaly
5. **Check dashboard**: See new incident with 4 files
6. **Review fix**: Open `fix_commands.sh`
7. **Apply fix**: Run the script (after review!)

---

## 🚨 Important Notes

- **Auto-monitoring is always on** when VM is configured
- **3-minute cooldown** between auto-incidents
- **Only 4 files** generated per incident
- **No static/demo data** - all data is real from your VM
- **AI agents watch continuously** - no manual intervention needed

---

## ❓ FAQ

**Q: How do I know if monitoring is working?**
```bash
curl http://localhost:8000/health
# Check "auto_monitor": true
```

**Q: Can I disable auto-monitoring?**
Yes, remove `VM_HOST` from `.env` or set it empty.

**Q: How often does it check the VM?**
Every 30 seconds by default.

**Q: What triggers an incident?**
- CPU > 80%
- Memory > 85%
- Error logs > 10

**Q: Can I change thresholds?**
Yes, edit `app/auto_monitor.py`.

---

## 🎉 That's It!

Your AI agents are now **always watching** your VM and will automatically respond to any chaos!
