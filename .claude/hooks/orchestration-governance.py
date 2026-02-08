#!/usr/bin/env python3
"""GCSC2 Orchestration Governance Hook (PostToolUse)

Monitors Task tool invocations for multi-agent coordination patterns.
Provides advisory warnings when orchestration best practices are not followed.

This hook checks for:
1. Multiple agents spawned without GovernanceAgent coordination
2. Agents spawned without role specification
3. Complex work without bounded authority specification

Hook protocol:
  - Receives JSON on stdin with tool_name and tool_input
  - Exit 0 = allow (optionally print recommendations)
  - This is ADVISORY only - does not block operations

Logging:
  - Appends orchestration events to ORCHESTRATION_LOG.md
"""

import sys
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.orchestration.runtime import (
        record_agent,
        record_message,
        record_note,
        start_session,
    )

    ORCHESTRATION_RUNTIME_AVAILABLE = True
except Exception:
    ORCHESTRATION_RUNTIME_AVAILABLE = False


def _discover_project_root() -> Path:
    """Resolve project root from env override or repository-relative fallback."""
    env_root = os.environ.get("GCSC_PROJECT_ROOT", "").strip()
    if env_root:
        p = Path(env_root).expanduser()
        if p.exists():
            return p.resolve()
    # .claude/hooks/orchestration-governance.py -> repo root is parents[2]
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _discover_project_root()
ORCHESTRATION_LOG = PROJECT_ROOT / "ORCHESTRATION_LOG.md"

# Track spawned agents within a session (persisted via log file parsing)
# Keywords that indicate different agent types/roles
GOVERNANCE_AGENT_KEYWORDS = [
    "GovernanceAgent",
    "governance",
    "coordinator",
    "orchestrator",
    "supervisor",
]

ROLE_SPECIFICATION_KEYWORDS = [
    "role:",
    "agent role",
    "responsibility:",
    "bounded authority",
    "authority:",
    "scope:",
    "delegate",
]

COMPLEXITY_INDICATORS = [
    "multi-step",
    "complex",
    "coordinate",
    "parallel",
    "multiple files",
    "refactor",
    "architecture",
    "full build",
    "complete rewrite",
]


def get_log_header() -> str:
    """Return the header for a new ORCHESTRATION_LOG.md file."""
    return """# GCSC2 Orchestration Log

This log tracks multi-agent coordination events for governance transparency.
Generated automatically by `orchestration-governance.py` hook.

---

## Event Log

"""


def ensure_log_exists():
    """Create ORCHESTRATION_LOG.md if it doesn't exist."""
    if not ORCHESTRATION_LOG.exists():
        ORCHESTRATION_LOG.write_text(get_log_header(), encoding="utf-8")


def append_to_log(event: Dict[str, Any]):
    """Append an orchestration event to the log file."""
    ensure_log_exists()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry_lines = [
        f"### {timestamp}",
        "",
        f"**Task Type:** {event.get('task_type', 'Unknown')}",
        f"**Agents Spawned:** {event.get('agent_count', 'N/A')}",
        f"**Coordination Pattern:** {event.get('coordination_pattern', 'None detected')}",
        f"**Has Governance:** {event.get('has_governance', False)}",
        f"**Has Role Spec:** {event.get('has_role_spec', False)}",
        "",
    ]

    if event.get('warnings'):
        entry_lines.append("**Warnings:**")
        for warning in event['warnings']:
            entry_lines.append(f"- {warning}")
        entry_lines.append("")

    if event.get('task_description'):
        # Truncate long descriptions
        desc = event['task_description'][:200]
        if len(event['task_description']) > 200:
            desc += "..."
        entry_lines.append(f"**Task Summary:** {desc}")
        entry_lines.append("")

    entry_lines.append("---")
    entry_lines.append("")

    with open(ORCHESTRATION_LOG, "a", encoding="utf-8") as f:
        f.write("\n".join(entry_lines))


def analyze_task_input(tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a Task tool invocation for orchestration patterns."""

    # Extract the task description/prompt from various possible fields
    task_content = ""
    for field in ["description", "prompt", "task", "content", "message", "input"]:
        if field in tool_input:
            val = tool_input[field]
            if isinstance(val, str):
                task_content += " " + val
            elif isinstance(val, dict):
                task_content += " " + json.dumps(val)

    task_content = task_content.lower()

    # Check for governance agent presence
    has_governance = any(
        keyword.lower() in task_content
        for keyword in GOVERNANCE_AGENT_KEYWORDS
    )

    # Check for role specification
    has_role_spec = any(
        keyword.lower() in task_content
        for keyword in ROLE_SPECIFICATION_KEYWORDS
    )

    # Check for complexity indicators
    is_complex = any(
        indicator.lower() in task_content
        for indicator in COMPLEXITY_INDICATORS
    )

    # Estimate agent count from content patterns
    agent_count = 1
    agent_patterns = [
        r'spawn\s+(\d+)\s+agent',
        r'(\d+)\s+parallel\s+agent',
        r'create\s+(\d+)\s+worker',
        r'delegate\s+to\s+(\d+)',
    ]
    for pattern in agent_patterns:
        match = re.search(pattern, task_content)
        if match:
            try:
                agent_count = max(agent_count, int(match.group(1)))
            except ValueError:
                pass

    # Check for multiple agent references
    multi_agent_keywords = ["agents", "workers", "delegates", "parallel tasks"]
    if any(kw in task_content for kw in multi_agent_keywords):
        agent_count = max(agent_count, 2)

    # Determine coordination pattern
    coordination_pattern = "single-agent"
    if agent_count > 1:
        if has_governance:
            coordination_pattern = "governed-multi-agent"
        else:
            coordination_pattern = "ungoverned-multi-agent"
    elif is_complex:
        coordination_pattern = "complex-single-agent"

    # Determine task type
    task_type = "general"
    task_type_patterns = {
        "build": ["build", "compile", "export", "render"],
        "verification": ["verify", "check", "validate", "test"],
        "refactor": ["refactor", "restructure", "reorganize"],
        "documentation": ["document", "docs", "readme", "write-up"],
        "research": ["research", "investigate", "analyze", "explore"],
        "geometry": ["hull", "frame", "scad", "openscad", "mesh"],
    }
    for ttype, keywords in task_type_patterns.items():
        if any(kw in task_content for kw in keywords):
            task_type = ttype
            break

    return {
        "has_governance": has_governance,
        "has_role_spec": has_role_spec,
        "is_complex": is_complex,
        "agent_count": agent_count,
        "coordination_pattern": coordination_pattern,
        "task_type": task_type,
        "task_description": task_content.strip()[:500],
    }


def generate_warnings(analysis: Dict[str, Any]) -> List[str]:
    """Generate advisory warnings based on analysis."""
    warnings = []

    # Warning: Multiple agents without governance
    if analysis["agent_count"] > 1 and not analysis["has_governance"]:
        warnings.append(
            "Multiple agents spawned without GovernanceAgent coordination"
        )

    # Warning: No role specification for non-trivial work
    if (analysis["is_complex"] or analysis["agent_count"] > 1) and not analysis["has_role_spec"]:
        warnings.append(
            "Agent spawned without role specification - consider using /orchestrate"
        )

    # Info: Suggest orchestration for complex work
    if analysis["is_complex"] and analysis["coordination_pattern"] == "complex-single-agent":
        warnings.append(
            "Complex work detected - consider using /orchestrate skill for coordinated multi-agent work"
        )

    return warnings


def format_output(warnings: List[str], analysis: Dict[str, Any]) -> Optional[str]:
    """Format advisory output for the user."""
    if not warnings:
        return None

    output_lines = ["\n=== ORCHESTRATION GOVERNANCE CHECK ===", ""]

    # Categorize warnings by severity
    critical_warnings = [w for w in warnings if "Multiple agents" in w]
    advisory_warnings = [w for w in warnings if "without role" in w]
    info_notices = [
        w for w in warnings
        if "consider using" in w.lower() and w not in critical_warnings and w not in advisory_warnings
    ]

    if critical_warnings:
        for w in critical_warnings:
            output_lines.append(f"[!] WARNING: {w}")

    if advisory_warnings:
        for w in advisory_warnings:
            output_lines.append(f"[~] ADVISORY: {w}")

    if info_notices:
        for w in info_notices:
            output_lines.append(f"[i] INFO: {w}")

    output_lines.append("")
    output_lines.append(f"Coordination Pattern: {analysis['coordination_pattern']}")
    output_lines.append(f"Task Type: {analysis['task_type']}")
    output_lines.append("")
    output_lines.append("Reference: See CLAUDE.md for orchestration best practices")
    output_lines.append("")

    return "\n".join(output_lines)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # Can't parse input, allow by default

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only check Task tool invocations
    if tool_name != "Task":
        sys.exit(0)

    # Analyze the task
    analysis = analyze_task_input(tool_input)

    # Generate warnings
    warnings = generate_warnings(analysis)

    # Log the event (always, for transparency)
    log_event = {
        **analysis,
        "warnings": warnings,
    }

    try:
        append_to_log(log_event)
    except Exception as e:
        # Don't fail the hook if logging fails
        print(f"[orchestration] Warning: Could not write to log: {e}", file=sys.stderr)

    # Persist structured event/state for deterministic replay if runtime is available.
    if ORCHESTRATION_RUNTIME_AVAILABLE:
        try:
            session_id = f"taskhook-{datetime.now(timezone.utc).strftime('%Y%m%d')}"
            start_session(
                session_id=session_id,
                initiated_by="orchestration-governance-hook",
                project_root=PROJECT_ROOT,
            )

            message = {
                "id": f"task-{uuid4().hex[:12]}",
                "type": "dispatch",
                "from": "TaskTool",
                "to": "GovernanceAgent" if analysis["has_governance"] else "UnspecifiedAgent",
                "payload": {
                    "task_type": analysis["task_type"],
                    "coordination_pattern": analysis["coordination_pattern"],
                    "agent_count": analysis["agent_count"],
                    "has_role_spec": analysis["has_role_spec"],
                    "is_complex": analysis["is_complex"],
                    "task_description": analysis["task_description"],
                },
            }
            record_message(
                session_id=session_id,
                message=message,
                actor="orchestration-governance-hook",
                project_root=PROJECT_ROOT,
            )

            governance_status = "working" if analysis["has_governance"] else "idle"
            record_agent(
                session_id=session_id,
                agent_name="GovernanceAgent",
                agent_state={
                    "status": governance_status,
                    "current_task": analysis["task_type"],
                    "last_output": analysis["coordination_pattern"],
                },
                actor="orchestration-governance-hook",
                project_root=PROJECT_ROOT,
            )

            if warnings:
                record_note(
                    session_id=session_id,
                    note="; ".join(warnings),
                    actor="orchestration-governance-hook",
                    project_root=PROJECT_ROOT,
                )
        except Exception as e:
            print(f"[orchestration] Warning: Runtime logging failed: {e}", file=sys.stderr)

    # Output advisory messages
    output = format_output(warnings, analysis)
    if output:
        print(output)

    # Always exit 0 - this hook is advisory only
    sys.exit(0)


if __name__ == "__main__":
    main()
