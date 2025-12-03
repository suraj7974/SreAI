# AI Chaos-Handler
**Autonomous Multi-Agent Incident Response System**

---

## One-sentence summary
AI Chaos-Handler is an autonomous multi-agent system that simulates an SRE team: it detects and diagnoses system failures on a real cloud VM (DigitalOcean Droplet), proposes technical fixes, validates risk, and generates a polished incident report — all via a Python FastAPI coordinator and SSH-based agents.

---

## Table of Contents
1.  [Project goals](#1-project-goals)
2.  [High-level architecture](#2-high-level-architecture)
3.  [Incident lifecycle (flow)](#3-incident-lifecycle-flow)
4.  [Agent descriptions & responsibilities](#4-agent-descriptions--responsibilities)
5.  [Data & outputs (where AI sends outputs)](#5-data--outputs--where-ai-sends-outputs)
6.  [API design & examples](#6-api-design--examples)
7.  [Dashboard](#7-dashboard)
8.  [Chaos scenarios & scripts (detailed)](#8-chaos-scenarios--scripts-detailed)
9.  [DigitalOcean Droplet (primary) setup](#9-digitalocean-droplet-primary-setup--quick-guide)
10. [Local VM notes](#10-local-vm-notes)
11. [Demo walkthrough (end-to-end)](#11-demo-walkthrough-end-to-end)
12. [Directory structure](#12-directory-structure)
13. [Safety, cleanup, and rollback](#13-safety-cleanup-and-rollback)
14. [Testing & offline mode](#14-testing--offline-mode)
15. [Extensions & next steps](#15-extensions--next-steps)
16. [FAQ](#16-faq)

---

## 1. Project goals
- Demonstrate agentic AI in an ops context (multi-step reasoning, tool use, autonomy).
- Provide a safe sandbox to run chaos engineering experiments on a real VM.
- Produce readable, actionable incident outputs (Markdown, optional PDF, Slack-style summary).
- Be clear, auditable, and reproducible for a hiring-manager demo.

---

## 2. High-level architecture

```
                   ┌───────────────┐
                   │   Client/UI   │
                   │ (curl/Postman)│
                   └──────┬────────┘
                          │
                   ┌──────▼───────┐
                   │   FastAPI    │
                   │ (Coordinator)│
                   └──────┬───────┘
                          │
      ┌───────────────────┼────────────────────┐
      │                   │                    │
┌─────▼─────┐       ┌─────▼─────┐         ┌────▼────┐
│ LogAgent  │       │MetricsAgent│        │ Fixer   │
└─────┬─────┘       └─────┬─────┘         └────┬────┘
      │                   │                    │
      └─────────┬─────────┴────────┬───────────┘
                │                  │
            ┌───▼────┐        ┌────▼────┐
            │ Tester │        │ Reporter│
            └───┬────┘        └────┬────┘
                │                  │
                └──────┬───────────┘
                       ▼
            incidents/{incident_id}/ (storage)
```

- Agents communicate via structured JSON messages and actions are logged into `incidents/{id}/trace.json`.
- Coordinator handles sequencing, retries, and error states.

---

## 3. Incident lifecycle (flow)
1.  **User triggers incident:** `POST /start_incident` with scenario and VM details.
2.  **Coordinator:** creates `incident_id`, prepares incident folder, kicks off chaos script on VM (optional).
3.  **LogAgent:** collects logs from VM (SSH or logs API).
4.  **MetricsAgent:** fetches metrics snapshot.
5.  **Coordinator** passes log+metric evidence to **FixerAgent**.
6.  **FixerAgent:** suggests fix commands and rationale.
7.  **TesterAgent:** dry-run/simulate fixes and checks side-effects.
8.  **ReporterAgent:** compiles `report.md` and (optionally) `report.pdf`; posts short summary to configured slack webhook.
9.  **User** retrieves final report with `GET /report/{incident_id}`.

---

## 4. Agent descriptions & responsibilities

### Coordinator
- Creates `incident_id`, manages agent lifecycle, writes to `trace.json`.
- Handles retries and timeouts, and ensures safe sequencing.
- Exposes FastAPI endpoints.

### LogAgent
- Connects to VM via SSH, collects logs (system journal, service logs, app logs).
- Performs pattern matching (error regex, repeated entries).
- Outputs `raw_logs.txt` and a JSON summary entry in trace.

### MetricsAgent
- Connects to a metrics endpoint on VM (or reads `metrics.json`) and snapshots CPU, memory, disk, network, and application metrics.
- Performs simple anomaly detection (z-score or threshold checking).
- Outputs `metrics.json` and evidence entries.

### FixerAgent
- Uses evidence to build a remediation plan: structured suggestions and a shell command bundle.
- Produces `fix_suggestion.json` and `fix.sh` (text script, not auto-executed).
- Provides confidence and explanation for each suggested action.

### TesterAgent
- Simulates applying the fix (dry-run) when possible.
- Checks for obvious risks: downtime, data loss, dependency ripple effects.
- Appends a risk assessment to the trace log.

### ReporterAgent
- Aggregates all outputs into a human-friendly `report.md` (incident timeline, root cause, evidence, recommended fix, risk & rollback plan).
- Optionally generates `report.pdf`.
- Creates a short Slack-style summary (saved to file and optionally sent to webhook).

---

## 5. Data & outputs — Where AI sends outputs

All outputs are stored per-incident in the `incidents/` directory:

-   `trace.json` — chronological structured messages:
    ```json
    [
      { "timestamp": "...", "agent": "LogAgent", "type":"diagnosis", "content":"..." },
      { "timestamp": "...", "agent": "MetricsAgent", "type":"evidence", "content":"..." }
    ]
    ```
-   `raw_logs.txt` — collected logs
-   `metrics.json` — snapshot of metrics used for diagnosis
-   `fix_suggestion.json` — structured fix proposals
-   `fix.sh` — plain shell script with suggested commands (for human review)
-   `report.md` — final incident postmortem
-   `report.pdf` — optional PDF export
-   `slack_summary.txt` — short summary message
-   `artifacts/` — charts, anomaly plots, or debug artifacts

**Live access:** `GET /status/{incident_id}` returns a snapshot of `trace.json` so the UI or user can watch agent progress in near real-time.

---

## 6. API design & examples

### `POST /start_incident`
-   **Purpose:** kick off an incident pipeline
-   **Body example:**
    ```json
    {
      "scenario": "cpu_spike",
      "target_vm": {
        "host": "203.0.113.10",
        "port": 22,
        "user": "sre-demo",
        "key_path": "/home/you/.ssh/ai_chaos_handler"
      },
      "options": {"duration": 60}
    }
    ```
-   **Response example:**
    ```json
    {"incident_id":"inc-20251202-001","status":"started"}
    ```

### `GET /status/{incident_id}`
-   **Purpose:** fetch current trace and agent statuses
-   **Response:** JSON containing trace array and `phase` field

### `GET /report/{incident_id}`
-   **Purpose:** download `report.md` and optionally `report.pdf`
-   **Response:** attachments or links to files in `incidents/{id}/`

---

## 7. Dashboard
A fully functional incident dashboard.

### 1. Real-time trace feed
- Fetch from `GET /status/{incident_id}`
- Color-coded per agent
- Chronological timeline

### 2. Evidence Panels
- Logs panel
- Metrics panel with charts (CPU, RAM, Disk if available)
- Fix suggestions panel
- Risk evaluation panel

### 3. Incident Header
- `incident_id`
- current phase
- timestamp

### 4. Actions
- Download `report.md`
- Download `report.pdf`
- Refresh trace manually
- Optional: trigger stop/reset

### 5. UI Refresh
- Poll every 1–2 seconds
- Render new trace entries smoothly

### 6. Visual Design
- Clean minimal SRE/DevOps dashboard look
- TailwindCSS v4 or React styling
- Light/Dark theme (optional)

---

## 8. Chaos scenarios & scripts (detailed)

All chaos scripts live at `/opt/chaos-scripts/` on the VM. Each script supports:
-   `start <args>` — begins the chaos action
-   `stop` — stops and reverts the action

It writes a PID file to `/var/run/chaos-{name}.pid` and enforces a max runtime fallback (e.g., 300s) which auto-reverts.

### CPU spike (`cpu_spike.sh`)
-   **Implementation:** spawn `stress-ng` or Python compute loops
-   **Args:** `duration` (s), `load` (core-workers)
-   **Stop:** `kill` stress process or let it exit

### Memory leak (`memory_leak.sh`)
-   **Implementation:** Python allocator that keeps arrays until target MB reached
-   **Args:** `target_mb`, `duration`
-   **Stop:** `kill` process, free memory, or auto-release after duration

### Disk fill (`disk_fill.sh`)
-   **Implementation:** create files under `/tmp/chaos_fill` until target size
-   **Args:** `size_mb`
-   **Stop:** remove `/tmp/chaos_fill/*`

### Network latency (`net_latency.sh`)
-   **Implementation:** `tc qdisc netem` rules to add delay or loss on an interface
-   **Args:** `iface`, `delay_ms`, `loss_pct`
-   **Stop:** remove `tc qdisc`

### Service crash (`service_kill.sh`)
-   **Implementation:** `systemctl stop <service>` or `kill <pid>`
-   **Args:** `service_name`
-   **Stop:** `systemctl start <service>`

### DB connection exhaustion (`db_conn_exhaust.sh`)
-   **Implementation:** spawn many DB clients that hold connections; for demo, use SQLite mock or Postgres client
-   **Args:** `conn_string`, `clients`
-   **Stop:** `kill` connector processes

**Important:** Scripts must validate args, write logs, and provide status output.

---

## 9. DigitalOcean Droplet (primary) setup — quick guide

### Overview
We target an Ubuntu 22.04 LTS Droplet. Steps include:
1.  Create Droplet via DigitalOcean console or CLI.
2.  Add your SSH key for access when creating.
3.  SSH into droplet, create `sre-demo` user and give `sudo`.
4.  Install required packages: `python3`, `pip`, `docker` (optional), `tc`, `stress-ng` (optional).
5.  Copy chaos scripts to `/opt/chaos-scripts/` and make executable.
6.  Expose a small metrics HTTP endpoint (a tiny Python server) on a non-root port for `MetricsAgent`.

### Recommended droplet size (demo)
-   2 vCPU, 4GB RAM, 25GB disk — e.g., Basic Droplet
-   Add firewall rules to allow SSH only from your IP (or use jump host).

### SSH & keys
-   Generate keypair locally: `ssh-keygen -f ~/.ssh/ai_chaos_handler`
-   Add public key on droplet; use private key path in API request as `key_path`.

**Note:** The README includes a full example of the shell commands to provision the droplet via `doctl` or UI in the repo `vm_provisioning/` docs.

---

## 10. Local VM notes
If you prefer local testing (VirtualBox / Vagrant):
-   Use Ubuntu 22.04 image.
-   Forward the same ports (SSH and metrics port).
-   Place chaos scripts in `/opt/chaos-scripts/`.
-   Use snapshots to quickly rollback state between experiments.

---

## 11. Demo walkthrough (end-to-end)
1.  Provision the droplet and copy `ai_chaos_handler` SSH key to your machine.
2.  Ensure chaos scripts exist at `/opt/chaos-scripts/` and are executable.
3.  Start the FastAPI coordinator on your laptop or a separate server:
    -   Provide path to private key for target VM in env/config.
4.  Trigger a chaos action on VM (manual or via coordinator):
    -   **Option A:** Run `/opt/chaos-scripts/cpu_spike.sh start 60 2` on VM.
    -   **Option B:** Let coordinator trigger chaos as part of incident start.
5.  `POST /start_incident` with scenario `cpu_spike` and VM details.
6.  Watch `GET /status/{incident_id}` for progress:
    -   LogAgent picks logs, MetricsAgent picks metrics, FixerAgent proposes fix.
7.  Once complete, `GET /report/{incident_id}` to download the `report.md` and review `fix.sh`.
8.  Optionally view `report.pdf` if PDF generation succeeded.

**Expected artifacts:** `incidents/{id}/report.md`, `fix.sh`, `trace.json`.

---

## 12. Directory structure
```
ai-chaos-handler/
├── README.md                # (this file)
├── app/
│   ├── coordinator/         # orchestrator and FastAPI app (implementation)
│   ├── agents/              # LogAgent, MetricsAgent, FixerAgent, TesterAgent, ReporterAgent
│   └── utils/
├── chaos-scripts/           # local copies of vm chaos scripts
├── vm_provisioning/         # DigitalOcean / Terraform docs and scripts
├── examples/                # sample incidents with output
├── tests/                   # unit and integration tests (mocked SSH)
└── incidents/               # runtime artifact dir (created during runs)
```

---

## 13. Safety, cleanup, and rollback
-   Always use snapshots on droplets before running destructive scripts.
-   Chaos scripts have `stop` and `--max-runtime` to auto-revert.
-   Use firewall rules and restrict SSH keys.
-   **Do not run on production systems.**
-   Provide explicit big-red warnings in docs before running scripts.
-   Provide a `cleanup_all.sh` script to stop all running chaos processes and restore services.

---

## 14. Testing & offline mode
-   Provide mock logs in `/examples/mock_logs/` and metrics in `/examples/mock_metrics/`.
-   Agents should accept a `--mock` or `--offline` flag to run against local files instead of SSH for faster iteration.
-   Include unit tests for parse logic, anomaly detection heuristics, and trace writing.

---

## 15. Extensions & next steps
-   Add Slack and PagerDuty integrations for real alerts.
-   Add GitHub PR automation to apply configuration fixes via a patch (manual approval recommended).
-   Replace custom orchestrator with LangGraph/Autogen after prototype for visual flows.
-   Add a web dashboard showing live trace and agent chat transcripts.
-   Implement agent learning: store historical incidents, compute recurring root causes, and improve suggestions.

---

## 16. FAQ
*(This section can be filled out later with common questions and answers.)*