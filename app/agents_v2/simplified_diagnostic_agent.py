"""Simplified Diagnostic Agent without tool calling issues"""

import json
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from app.agents_v2 import AgentState
from app.agents_v2.tools import collect_system_logs, collect_system_metrics, save_analysis_artifact, log_agent_decision
import os


class SimplifiedDiagnosticAgent:
    """
    Simplified autonomous agent that investigates incidents.
    Uses direct tool calls instead of tool calling agent to avoid Gemini issues.
    """
    
    def __init__(self, llm_model: str = None):
        self.name = "DiagnosticAgent"
        
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = llm_model or os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        self.llm = None  # Lazy initialization
    
    def _get_llm(self):
        """Lazy load LLM only when needed"""
        if self.llm is None:
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not set in environment")
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=0.3,
                max_output_tokens=2000
            )
        return self.llm
    
    async def __call__(self, state: AgentState) -> AgentState:
        """Execute diagnostic analysis"""
        
        incident_id = state["incident_id"]
        scenario = state["scenario"]
        target_vm = state["target_vm"]
        
        print(f"\n🔍 {self.name} starting investigation...")
        
        # Step 1: Collect data using tools
        print(f"  → Collecting system logs...")
        try:
            # Call the tool function directly
            from app.utils import run_ssh_command, save_artifact
            
            commands = [
                "sudo journalctl -n 500 --no-pager",
                "tail -n 200 /var/log/syslog 2>/dev/null || echo 'syslog not available'"
            ]
            
            combined_logs = []
            for cmd in commands:
                try:
                    stdout, stderr, exit_code = await run_ssh_command(
                        host=target_vm.get('host'),
                        port=target_vm.get('port', 22),
                        username=target_vm.get('user'),
                        key_path=target_vm.get('key_path'),
                        command=cmd
                    )
                    
                    if stdout:
                        combined_logs.append(f"=== {cmd} ===\n{stdout[:500]}\n")
                except Exception as e:
                    combined_logs.append(f"=== ERROR: {str(e)} ===\n")
            
            logs = "\n".join(combined_logs)
            save_artifact(incident_id, "raw_logs.txt", logs)
            state["logs_raw"] = logs
            
        except Exception as e:
            print(f"  ⚠️  Log collection failed: {e}")
            logs = f"Error collecting logs: {str(e)}"
            state["logs_raw"] = logs
        
        print(f"  → Collecting system metrics...")
        try:
            from app.utils import run_ssh_command, save_artifact
            
            metrics = {}
            
            # CPU usage
            cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | sed 's/%us,//'"
            cpu_out, _, _ = await run_ssh_command(
                host=target_vm.get('host'),
                port=target_vm.get('port', 22),
                username=target_vm.get('user'),
                key_path=target_vm.get('key_path'),
                command=cpu_cmd
            )
            metrics["cpu_usage_percent"] = float(cpu_out.strip()) if cpu_out.strip() else 0.0
            
            # Memory usage
            mem_cmd = "free | grep Mem | awk '{print ($3/$2) * 100.0}'"
            mem_out, _, _ = await run_ssh_command(
                host=target_vm.get('host'),
                port=target_vm.get('port', 22),
                username=target_vm.get('user'),
                key_path=target_vm.get('key_path'),
                command=mem_cmd
            )
            metrics["memory_usage_percent"] = float(mem_out.strip()) if mem_out.strip() else 0.0
            
            save_artifact(incident_id, "metrics.json", json.dumps(metrics, indent=2))
            state["metrics_raw"] = metrics
            
        except Exception as e:
            print(f"  ⚠️  Metrics collection failed: {e}")
            state["metrics_raw"] = {"error": str(e)}
        
        # Step 2: Analyze with LLM
        print(f"  → Analyzing data with AI...")
        
        llm = self._get_llm()
        
        prompt = f"""You are an expert SRE analyzing a {scenario} incident.

Logs Summary (truncated):
{logs[:1000]}

Metrics:
{json.dumps(state["metrics_raw"], indent=2)}

Analyze this data and provide:
1. Root cause
2. Severity (low/medium/high/critical)
3. Key findings
4. Recommended next steps

Return as JSON:
{{
  "root_cause": "...",
  "severity": "...",
  "key_findings": ["..."],
  "recommendations": ["..."],
  "confidence": 0.8
}}
"""
        
        try:
            messages = [
                SystemMessage(content="You are an expert SRE. Analyze incidents and return structured JSON."),
                HumanMessage(content=prompt)
            ]
            response = await llm.ainvoke(messages)
            
            # Extract JSON from response
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            analysis = json.loads(content.strip())
            state["logs_analysis"] = analysis
            
            # Save analysis
            from app.utils import save_artifact, append_trace_event
            
            save_artifact(
                incident_id=incident_id,
                filename="diagnostic_analysis.json",
                content=json.dumps(analysis, indent=2)
            )
            
            # Log decision
            append_trace_event(
                incident_id=incident_id,
                agent=self.name,
                event_type="decision",
                content=f"Investigation complete - Root cause: {analysis.get('root_cause', 'Unknown')}",
                meta={"reasoning": f"Analysis confidence: {analysis.get('confidence', 0.0)}"}
            )
            
            print(f"  ✅ Analysis complete - {analysis.get('severity', 'unknown')} severity")
            
        except Exception as e:
            print(f"  ⚠️  Analysis failed: {e}")
            state["logs_analysis"] = {
                "root_cause": "Analysis failed",
                "severity": "unknown",
                "error": str(e),
                "confidence": 0.0
            }
        
        # Update messages
        state["messages"].append({
            "agent": self.name,
            "content": json.dumps(state["logs_analysis"]),
            "type": "diagnostic"
        })
        
        # Record decision
        state["agent_decisions"].append({
            "agent": self.name,
            "decision": "Investigation complete",
            "findings": state["logs_analysis"].get("root_cause", "Unknown"),
            "confidence": state["logs_analysis"].get("confidence", 0.7)
        })
        
        # Decide next agent
        state["next_agent"] = "remediation"
        
        return state
