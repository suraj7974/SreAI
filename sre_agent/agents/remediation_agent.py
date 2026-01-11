"""
SRE Agent - Remediation Agent

This agent generates and executes remediation plans.
It implements human-in-the-loop for approval before execution.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Literal, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from sre_agent.state import (
    SREAgentState,
    IncidentStatus,
    Severity,
    RemediationAction,
    RemediationPlan,
)
from sre_agent.tools import REMEDIATION_TOOLS, run_ssh_command
from sre_agent.config import settings

logger = logging.getLogger(__name__)


REMEDIATION_SYSTEM_PROMPT = """You are an expert SRE Remediation Agent. Your job is to:

1. PLAN: Create a safe remediation plan based on the diagnosis
2. VALIDATE: Ensure actions are safe and reversible where possible
3. EXECUTE: Run approved remediation actions (only after approval)
4. VERIFY: Confirm the fix worked

You have access to these tools:
- execute_ssh_command: Run commands on the target system
- restart_service: Restart a systemd service
- kill_process: Send signals to processes
- check_service_status: Verify service health

SAFETY RULES:
1. NEVER execute destructive commands without explicit approval
2. Always include rollback procedures when possible
3. Start with least invasive actions first
4. Verify system state after each action
5. Document every action taken

RISK LEVELS:
- LOW: Read-only commands, service restarts, log rotation
- MEDIUM: Process termination, configuration changes
- HIGH: Data deletion, system reboots, package operations

For each remediation action, provide:
1. Description of what it does
2. The exact command
3. Risk level (low/medium/high)
4. Expected outcome
5. Rollback command if applicable

Format remediation plan as JSON:
{{
    "plan_summary": "Brief description of the plan",
    "estimated_time": "5-10 minutes",
    "actions": [
        {{
            "description": "What this action does",
            "command": "the command to run",
            "risk_level": "low|medium|high",
            "expected_outcome": "What should happen",
            "rollback_command": "How to undo if needed"
        }}
    ]
}}
"""


def get_remediation_llm():
    """Get the LLM for the remediation agent"""
    return ChatGoogleGenerativeAI(
        model=settings.google_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,  # Lower temperature for more precise commands
        max_output_tokens=settings.llm_max_tokens,
    )


def create_remediation_agent():
    """Create the ReAct remediation agent with tools"""
    llm = get_remediation_llm()
    return create_react_agent(
        llm,
        tools=REMEDIATION_TOOLS,
        state_modifier=REMEDIATION_SYSTEM_PROMPT,
    )


async def remediation_planning_node(state: SREAgentState) -> SREAgentState:
    """
    Remediation Planning Node

    Generates a remediation plan based on diagnosis.
    Does NOT execute - waits for human approval.
    """
    logger.info(
        f"[RemediationAgent] Creating plan for incident {state.get('incident_id', 'N/A')}"
    )

    instance = state.get("target_instance", "")
    diagnosis = state.get("diagnosis", {})
    severity = state.get("severity", Severity.WARNING)

    thoughts = state.get("agent_thoughts", [])
    thoughts.append(
        {
            "agent_name": "RemediationAgent",
            "thought": "Generating remediation plan based on diagnosis",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    try:
        llm = get_remediation_llm()

        # Generate remediation plan (no tool use, just planning)
        task = f"""
        Create a remediation plan for this incident:
        
        INSTANCE: {instance}
        SEVERITY: {severity.value}
        
        DIAGNOSIS:
        Root Cause: {diagnosis.get("root_cause", "Unknown")}
        Confidence: {diagnosis.get("confidence", 0)}
        Affected Components: {json.dumps(diagnosis.get("affected_components", []))}
        Recommendations: {json.dumps(diagnosis.get("recommendations", []))}
        
        Create a step-by-step remediation plan. For each action:
        1. Describe what it does in plain English
        2. Provide the exact command to run
        3. Assess the risk level
        4. Include rollback if possible
        
        Prioritize:
        - Safe, reversible actions first
        - Quick wins that reduce impact
        - Then more invasive fixes if needed
        
        Output your plan as JSON with the structure shown in your instructions.
        """

        response = await llm.ainvoke(
            [
                SystemMessage(content=REMEDIATION_SYSTEM_PROMPT),
                HumanMessage(content=task),
            ]
        )

        # Parse the plan
        plan_data = _parse_remediation_plan(response.content)

        # Create formal plan object
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        remediation_plan = {
            "plan_id": plan_id,
            "incident_id": state.get("incident_id", ""),
            "actions": plan_data.get("actions", []),
            "estimated_resolution_time": plan_data.get("estimated_time", "Unknown"),
            "plan_summary": plan_data.get("plan_summary", ""),
            "created_at": datetime.utcnow().isoformat(),
            "approved": False,
            "approved_by": None,
            "approved_at": None,
        }

        # Add action IDs
        for i, action in enumerate(remediation_plan["actions"]):
            action["action_id"] = f"{plan_id}-action-{i + 1}"
            action["requires_approval"] = action.get("risk_level", "high") != "low"

        thoughts.append(
            {
                "agent_name": "RemediationAgent",
                "thought": f"Generated plan with {len(remediation_plan['actions'])} actions",
                "action": "Created remediation plan, awaiting approval",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        logger.info(
            f"[RemediationAgent] Plan created: {plan_id} with {len(remediation_plan['actions'])} actions"
        )

        return {
            **state,
            "remediation_plan": remediation_plan,
            "status": IncidentStatus.AWAITING_APPROVAL,
            "awaiting_approval": True,
            "approval_request_id": plan_id,
            "agent_thoughts": thoughts,
            "current_agent": "remediation",
            "next_agent": "approval_wait",
            "should_continue": True,
            "updated_at": datetime.utcnow().isoformat(),
            "iteration_count": state.get("iteration_count", 0) + 1,
        }

    except Exception as e:
        logger.error(f"[RemediationAgent] Error creating plan: {e}", exc_info=True)
        thoughts.append(
            {
                "agent_name": "RemediationAgent",
                "thought": f"Failed to create remediation plan: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        return {
            **state,
            "error": str(e),
            "agent_thoughts": thoughts,
            "status": IncidentStatus.FAILED,
            "should_continue": False,
        }


async def remediation_execution_node(state: SREAgentState) -> SREAgentState:
    """
    Remediation Execution Node

    Executes approved remediation actions.
    Only runs if plan has been approved.
    """
    logger.info(
        f"[RemediationAgent] Executing plan for incident {state.get('incident_id', 'N/A')}"
    )

    plan = state.get("remediation_plan", {})
    instance = state.get("target_instance", "")

    if not plan.get("approved"):
        logger.warning("[RemediationAgent] Plan not approved, skipping execution")
        return {
            **state,
            "error": "Remediation plan not approved",
            "should_continue": False,
        }

    thoughts = state.get("agent_thoughts", [])
    thoughts.append(
        {
            "agent_name": "RemediationAgent",
            "thought": f"Executing approved plan {plan.get('plan_id')}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    # Execute each action
    results = []
    host = instance.split(":")[0]

    for action in plan.get("actions", []):
        action_id = action.get("action_id", "unknown")
        command = action.get("command", "")

        if not command:
            results.append(
                {
                    "action_id": action_id,
                    "success": False,
                    "error": "No command specified",
                }
            )
            continue

        logger.info(
            f"[RemediationAgent] Executing action {action_id}: {command[:50]}..."
        )

        try:
            stdout, stderr, exit_code = await run_ssh_command(host, command)

            success = exit_code == 0
            results.append(
                {
                    "action_id": action_id,
                    "command": command,
                    "success": success,
                    "exit_code": exit_code,
                    "stdout": stdout[:1000] if stdout else "",
                    "stderr": stderr[:500] if stderr else "",
                    "executed_at": datetime.utcnow().isoformat(),
                }
            )

            thoughts.append(
                {
                    "agent_name": "RemediationAgent",
                    "action": f"Executed: {command[:50]}...",
                    "observation": f"Exit code: {exit_code}, Success: {success}",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            if not success:
                logger.warning(
                    f"[RemediationAgent] Action {action_id} failed: {stderr}"
                )
                # Don't continue if an action fails
                break

        except Exception as e:
            logger.error(f"[RemediationAgent] Action {action_id} error: {e}")
            results.append(
                {
                    "action_id": action_id,
                    "command": command,
                    "success": False,
                    "error": str(e),
                    "executed_at": datetime.utcnow().isoformat(),
                }
            )
            break

    # Determine overall success
    all_success = all(r.get("success", False) for r in results)

    final_status = IncidentStatus.RESOLVED if all_success else IncidentStatus.FAILED

    thoughts.append(
        {
            "agent_name": "RemediationAgent",
            "thought": f"Remediation {'completed successfully' if all_success else 'had failures'}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    return {
        **state,
        "remediation_results": results,
        "status": final_status,
        "agent_thoughts": thoughts,
        "current_agent": "remediation",
        "next_agent": "end",
        "should_continue": False,
        "awaiting_approval": False,
        "updated_at": datetime.utcnow().isoformat(),
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


def _parse_remediation_plan(response: str) -> Dict[str, Any]:
    """Parse remediation plan JSON from response"""
    try:
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        elif "{" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            json_str = response[start:end]
        else:
            return {"actions": [], "plan_summary": response[:200]}

        return json.loads(json_str)
    except Exception as e:
        logger.warning(f"Failed to parse remediation plan: {e}")
        return {
            "actions": [],
            "plan_summary": "Failed to parse plan",
            "parse_error": str(e),
        }


def should_execute_remediation(state: SREAgentState) -> Literal["execute", "wait"]:
    """Check if remediation should execute"""
    plan = state.get("remediation_plan", {})
    if plan.get("approved"):
        return "execute"
    return "wait"
