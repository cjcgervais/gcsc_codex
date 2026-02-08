#!/usr/bin/env python3
"""State + event runtime for GCSC2 multi-agent orchestration.

Provides:
- State schema validation
- Message contract validation
- Deterministic append-only event log with sequence IDs
- Session replay and state materialization
"""

from __future__ import annotations

import argparse
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"

TASK_STATUSES = {"pending", "in_progress", "blocked", "completed", "failed"}
GATE_STATUSES = {"pending", "passed", "failed"}
AGENT_STATUSES = {"idle", "working", "blocked", "waiting_review"}

MESSAGE_TYPES = {
    "dispatch",
    "work_submission",
    "verification_result",
    "build_request",
    "build_report",
    "research_request",
    "research_report",
    "approval_request",
    "approval_decision",
    "failure_report",
    "human_review_required",
}

ORCHESTRATION_STATE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "schema_version",
        "session_id",
        "initiated_by",
        "created_at",
        "updated_at",
        "tasks",
        "gates",
        "agents",
        "messages",
        "notes",
    ],
    "properties": {
        "schema_version": {"type": "string"},
        "session_id": {"type": "string"},
        "initiated_by": {"type": "string"},
        "created_at": {"type": "string"},
        "updated_at": {"type": "string"},
        "tasks": {"type": "array"},
        "gates": {"type": "array"},
        "agents": {"type": "object"},
        "messages": {"type": "array"},
        "notes": {"type": "array"},
    },
}

MESSAGE_CONTRACT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["id", "type", "from", "to", "payload"],
    "properties": {
        "id": {"type": "string"},
        "type": {"type": "string", "enum": sorted(MESSAGE_TYPES)},
        "from": {"type": "string"},
        "to": {"type": "string"},
        "timestamp": {"type": "string"},
        "payload": {"type": "object"},
    },
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _discover_project_root(project_root: str | Path | None = None) -> Path:
    if project_root:
        p = Path(project_root).expanduser().resolve()
        return p
    env_root = os.environ.get("GCSC_PROJECT_ROOT", "").strip()
    if env_root:
        p = Path(env_root).expanduser()
        if p.exists():
            return p.resolve()
    # scripts/orchestration/runtime.py -> repo root is parents[2]
    return Path(__file__).resolve().parents[2]


def get_runtime_paths(project_root: str | Path | None = None) -> dict[str, Path]:
    root = _discover_project_root(project_root)
    runtime_root = root / "_codex" / "orchestration"
    return {
        "project_root": root,
        "runtime_root": runtime_root,
        "events_file": runtime_root / "events.jsonl",
        "sequence_file": runtime_root / "sequence.txt",
        "lock_file": runtime_root / "events.lock",
        "state_dir": runtime_root / "state",
    }


def _ensure_runtime_layout(paths: dict[str, Path]) -> None:
    paths["runtime_root"].mkdir(parents=True, exist_ok=True)
    paths["state_dir"].mkdir(parents=True, exist_ok=True)


@contextmanager
def _file_lock(lock_file: Path, timeout_seconds: float = 10.0, poll_seconds: float = 0.05):
    """Cross-platform lock via exclusive lock file creation."""
    start = time.time()
    while True:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii", errors="ignore"))
            os.close(fd)
            break
        except FileExistsError:
            if time.time() - start >= timeout_seconds:
                raise TimeoutError(f"Timed out waiting for lock: {lock_file}")
            time.sleep(poll_seconds)

    try:
        yield
    finally:
        try:
            lock_file.unlink(missing_ok=True)
        except OSError:
            pass


def _next_sequence(sequence_file: Path) -> int:
    current = 0
    if sequence_file.exists():
        raw = sequence_file.read_text(encoding="ascii", errors="ignore").strip()
        if raw:
            try:
                current = int(raw)
            except ValueError:
                current = 0
    next_seq = current + 1
    sequence_file.write_text(f"{next_seq}\n", encoding="ascii")
    return next_seq


def default_session_state(session_id: str, initiated_by: str = "unknown") -> dict[str, Any]:
    now = _utc_now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "initiated_by": initiated_by,
        "created_at": now,
        "updated_at": now,
        "tasks": [],
        "gates": [],
        "agents": {},
        "messages": [],
        "notes": [],
    }


def validate_message_contract(message: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(message, dict):
        return ["message must be an object"]

    required_fields = MESSAGE_CONTRACT_SCHEMA["required"]
    for field in required_fields:
        if field not in message:
            errors.append(f"missing required field: {field}")

    for field in ("id", "type", "from", "to"):
        if field in message and (not isinstance(message[field], str) or not message[field].strip()):
            errors.append(f"{field} must be a non-empty string")

    if "type" in message and isinstance(message.get("type"), str):
        if message["type"] not in MESSAGE_TYPES:
            errors.append(f"type must be one of: {sorted(MESSAGE_TYPES)}")

    payload = message.get("payload")
    if "payload" in message and not isinstance(payload, dict):
        errors.append("payload must be an object")

    ts = message.get("timestamp")
    if ts is not None and not isinstance(ts, str):
        errors.append("timestamp must be a string when provided")

    return errors


def validate_orchestration_state(state: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(state, dict):
        return ["state must be an object"]

    required_fields = ORCHESTRATION_STATE_SCHEMA["required"]
    for field in required_fields:
        if field not in state:
            errors.append(f"missing required field: {field}")

    if not isinstance(state.get("session_id", ""), str) or not state.get("session_id", "").strip():
        errors.append("session_id must be a non-empty string")

    if not isinstance(state.get("tasks", []), list):
        errors.append("tasks must be an array")
    else:
        for idx, task in enumerate(state["tasks"]):
            if not isinstance(task, dict):
                errors.append(f"tasks[{idx}] must be an object")
                continue
            status = task.get("status")
            if status is not None and status not in TASK_STATUSES:
                errors.append(f"tasks[{idx}].status invalid: {status}")

    if not isinstance(state.get("gates", []), list):
        errors.append("gates must be an array")
    else:
        for idx, gate in enumerate(state["gates"]):
            if not isinstance(gate, dict):
                errors.append(f"gates[{idx}] must be an object")
                continue
            status = gate.get("status")
            if status is not None and status not in GATE_STATUSES:
                errors.append(f"gates[{idx}].status invalid: {status}")

    if not isinstance(state.get("agents", {}), dict):
        errors.append("agents must be an object")
    else:
        for name, agent in state["agents"].items():
            if not isinstance(name, str):
                errors.append("agents keys must be strings")
                continue
            if not isinstance(agent, dict):
                errors.append(f"agents[{name}] must be an object")
                continue
            status = agent.get("status")
            if status is not None and status not in AGENT_STATUSES:
                errors.append(f"agents[{name}].status invalid: {status}")

    if not isinstance(state.get("messages", []), list):
        errors.append("messages must be an array")
    else:
        for idx, message in enumerate(state["messages"]):
            msg_errors = validate_message_contract(message)
            for msg_error in msg_errors:
                errors.append(f"messages[{idx}]: {msg_error}")

    if not isinstance(state.get("notes", []), list):
        errors.append("notes must be an array")

    return errors


def append_event(
    session_id: str,
    event_type: str,
    data: dict[str, Any] | None = None,
    actor: str = "system",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    if not session_id or not session_id.strip():
        raise ValueError("session_id must be non-empty")
    if not event_type or not event_type.strip():
        raise ValueError("event_type must be non-empty")
    if data is not None and not isinstance(data, dict):
        raise ValueError("data must be an object")

    paths = get_runtime_paths(project_root)
    _ensure_runtime_layout(paths)

    with _file_lock(paths["lock_file"]):
        seq = _next_sequence(paths["sequence_file"])
        event = {
            "seq": seq,
            "timestamp": _utc_now_iso(),
            "session_id": session_id,
            "event_type": event_type,
            "actor": actor,
            "data": data or {},
        }

        with paths["events_file"].open("a", encoding="utf-8", newline="\n") as f:
            f.write(_canonical_json(event) + "\n")

    return event


def _read_events(events_file: Path) -> list[dict[str, Any]]:
    if not events_file.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in events_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def _upsert_list_item(items: list[dict[str, Any]], item: dict[str, Any], key: str = "id") -> None:
    item_id = item.get(key)
    if item_id is None:
        items.append(item)
        return
    for idx, existing in enumerate(items):
        if existing.get(key) == item_id:
            items[idx] = {**existing, **item}
            return
    items.append(item)


def _apply_event(state: dict[str, Any] | None, event: dict[str, Any]) -> dict[str, Any]:
    session_id = str(event.get("session_id", "unknown"))
    event_type = str(event.get("event_type", "unknown"))
    data = event.get("data", {})
    if not isinstance(data, dict):
        data = {"raw": data}

    if state is None:
        initiated_by = str(data.get("initiated_by", "unknown"))
        state = default_session_state(session_id, initiated_by=initiated_by)
        first_ts = str(event.get("timestamp", _utc_now_iso()))
        state["created_at"] = first_ts
        state["updated_at"] = first_ts

    if event_type == "session_started":
        initiated_by = str(data.get("initiated_by", state.get("initiated_by", "unknown")))
        state["initiated_by"] = initiated_by
    elif event_type == "task_upsert":
        task = data.get("task")
        if isinstance(task, dict):
            _upsert_list_item(state["tasks"], task, key="id")
    elif event_type == "gate_upsert":
        gate = data.get("gate")
        if isinstance(gate, dict):
            _upsert_list_item(state["gates"], gate, key="id")
    elif event_type == "agent_upsert":
        agent_name = data.get("agent_name")
        agent_state = data.get("agent_state")
        if isinstance(agent_name, str) and isinstance(agent_state, dict):
            state["agents"][agent_name] = {**state["agents"].get(agent_name, {}), **agent_state}
    elif event_type == "message_add":
        message = data.get("message")
        if isinstance(message, dict):
            msg_errors = validate_message_contract(message)
            if not msg_errors:
                state["messages"].append(message)
            else:
                state.setdefault("message_errors", []).append(
                    {"message_id": message.get("id"), "errors": msg_errors}
                )
    elif event_type == "note_add":
        note = data.get("note")
        if isinstance(note, str) and note.strip():
            state["notes"].append(note.strip())
    else:
        state.setdefault("unhandled_events", []).append(
            {"seq": event.get("seq"), "event_type": event_type}
        )

    state["updated_at"] = str(event.get("timestamp", _utc_now_iso()))
    return state


def replay_session(session_id: str, project_root: str | Path | None = None) -> dict[str, Any]:
    paths = get_runtime_paths(project_root)
    events = _read_events(paths["events_file"])
    filtered = [e for e in events if e.get("session_id") == session_id]
    filtered.sort(key=lambda e: int(e.get("seq", 0)))

    state: dict[str, Any] | None = None
    for event in filtered:
        state = _apply_event(state, event)

    if state is None:
        state = default_session_state(session_id, initiated_by="unknown")

    return state


def _state_file_for_session(paths: dict[str, Path], session_id: str) -> Path:
    return paths["state_dir"] / f"{session_id}.json"


def materialize_session_state(session_id: str, project_root: str | Path | None = None) -> dict[str, Any]:
    paths = get_runtime_paths(project_root)
    _ensure_runtime_layout(paths)
    state = replay_session(session_id, project_root=project_root)
    state_file = _state_file_for_session(paths, session_id)
    state_file.write_text(
        json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return state


def start_session(
    session_id: str,
    initiated_by: str = "user",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    append_event(
        session_id=session_id,
        event_type="session_started",
        data={"initiated_by": initiated_by},
        actor=initiated_by,
        project_root=project_root,
    )
    return materialize_session_state(session_id, project_root=project_root)


def record_task(
    session_id: str,
    task: dict[str, Any],
    actor: str = "system",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    if not isinstance(task, dict):
        raise ValueError("task must be an object")
    if "status" in task and task["status"] not in TASK_STATUSES:
        raise ValueError(f"task.status must be one of {sorted(TASK_STATUSES)}")
    append_event(
        session_id=session_id,
        event_type="task_upsert",
        data={"task": task},
        actor=actor,
        project_root=project_root,
    )
    return materialize_session_state(session_id, project_root=project_root)


def record_gate(
    session_id: str,
    gate: dict[str, Any],
    actor: str = "system",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    if not isinstance(gate, dict):
        raise ValueError("gate must be an object")
    if "status" in gate and gate["status"] not in GATE_STATUSES:
        raise ValueError(f"gate.status must be one of {sorted(GATE_STATUSES)}")
    append_event(
        session_id=session_id,
        event_type="gate_upsert",
        data={"gate": gate},
        actor=actor,
        project_root=project_root,
    )
    return materialize_session_state(session_id, project_root=project_root)


def record_agent(
    session_id: str,
    agent_name: str,
    agent_state: dict[str, Any],
    actor: str = "system",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    if not agent_name.strip():
        raise ValueError("agent_name must be non-empty")
    if not isinstance(agent_state, dict):
        raise ValueError("agent_state must be an object")
    status = agent_state.get("status")
    if status is not None and status not in AGENT_STATUSES:
        raise ValueError(f"agent_state.status must be one of {sorted(AGENT_STATUSES)}")

    append_event(
        session_id=session_id,
        event_type="agent_upsert",
        data={"agent_name": agent_name, "agent_state": agent_state},
        actor=actor,
        project_root=project_root,
    )
    return materialize_session_state(session_id, project_root=project_root)


def record_message(
    session_id: str,
    message: dict[str, Any],
    actor: str = "system",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    errors = validate_message_contract(message)
    if errors:
        raise ValueError("; ".join(errors))
    if "timestamp" not in message:
        message = {**message, "timestamp": _utc_now_iso()}
    append_event(
        session_id=session_id,
        event_type="message_add",
        data={"message": message},
        actor=actor,
        project_root=project_root,
    )
    return materialize_session_state(session_id, project_root=project_root)


def record_note(
    session_id: str,
    note: str,
    actor: str = "system",
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    if not note.strip():
        raise ValueError("note must be non-empty")
    append_event(
        session_id=session_id,
        event_type="note_add",
        data={"note": note.strip()},
        actor=actor,
        project_root=project_root,
    )
    return materialize_session_state(session_id, project_root=project_root)


def _parse_json_or_die(raw: str) -> dict[str, Any]:
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError("JSON payload must be an object")
    return obj


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GCSC2 orchestration runtime CLI")
    parser.add_argument("--project-root", default="", help="Override repository root")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="Start or refresh a session")
    p_start.add_argument("session_id")
    p_start.add_argument("--initiated-by", default="user")

    p_task = sub.add_parser("task", help="Upsert a task")
    p_task.add_argument("session_id")
    p_task.add_argument("--task-json", required=True)
    p_task.add_argument("--actor", default="system")

    p_gate = sub.add_parser("gate", help="Upsert a gate")
    p_gate.add_argument("session_id")
    p_gate.add_argument("--gate-json", required=True)
    p_gate.add_argument("--actor", default="system")

    p_agent = sub.add_parser("agent", help="Upsert an agent state")
    p_agent.add_argument("session_id")
    p_agent.add_argument("--name", required=True)
    p_agent.add_argument("--state-json", required=True)
    p_agent.add_argument("--actor", default="system")

    p_message = sub.add_parser("message", help="Append a message")
    p_message.add_argument("session_id")
    p_message.add_argument("--message-json", required=True)
    p_message.add_argument("--actor", default="system")

    p_note = sub.add_parser("note", help="Append a note")
    p_note.add_argument("session_id")
    p_note.add_argument("--text", required=True)
    p_note.add_argument("--actor", default="system")

    p_replay = sub.add_parser("replay", help="Replay a session")
    p_replay.add_argument("session_id")

    p_validate_msg = sub.add_parser("validate-message", help="Validate message contract")
    p_validate_msg.add_argument("--message-json", required=True)

    p_validate_state = sub.add_parser("validate-state", help="Validate state schema")
    p_validate_state.add_argument("--state-json", required=True)

    return parser


def main() -> int:
    parser = _build_cli()
    args = parser.parse_args()

    project_root = args.project_root or None

    if args.command == "start":
        state = start_session(args.session_id, initiated_by=args.initiated_by, project_root=project_root)
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    if args.command == "task":
        task = _parse_json_or_die(args.task_json)
        state = record_task(args.session_id, task=task, actor=args.actor, project_root=project_root)
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    if args.command == "gate":
        gate = _parse_json_or_die(args.gate_json)
        state = record_gate(args.session_id, gate=gate, actor=args.actor, project_root=project_root)
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    if args.command == "agent":
        agent_state = _parse_json_or_die(args.state_json)
        state = record_agent(
            args.session_id,
            agent_name=args.name,
            agent_state=agent_state,
            actor=args.actor,
            project_root=project_root,
        )
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    if args.command == "message":
        message = _parse_json_or_die(args.message_json)
        state = record_message(args.session_id, message=message, actor=args.actor, project_root=project_root)
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    if args.command == "note":
        state = record_note(args.session_id, note=args.text, actor=args.actor, project_root=project_root)
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    if args.command == "replay":
        state = replay_session(args.session_id, project_root=project_root)
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    if args.command == "validate-message":
        msg = _parse_json_or_die(args.message_json)
        errors = validate_message_contract(msg)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, sort_keys=True, ensure_ascii=True))
            return 1
        print(json.dumps({"valid": True}, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    if args.command == "validate-state":
        state = _parse_json_or_die(args.state_json)
        errors = validate_orchestration_state(state)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, indent=2, sort_keys=True, ensure_ascii=True))
            return 1
        print(json.dumps({"valid": True}, indent=2, sort_keys=True, ensure_ascii=True))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
