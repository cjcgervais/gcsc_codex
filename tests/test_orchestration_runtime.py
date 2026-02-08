#!/usr/bin/env python3
"""Unit tests for orchestration runtime contracts, event log, and replay."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.orchestration.runtime import (
    MESSAGE_TYPES,
    get_runtime_paths,
    materialize_session_state,
    record_agent,
    record_gate,
    record_message,
    record_note,
    record_task,
    replay_session,
    start_session,
    validate_message_contract,
    validate_orchestration_state,
)


class TestOrchestrationRuntime(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.project_root = Path(self._tmpdir.name)
        self.session_id = "orch-test-001"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_message_contract_validation(self) -> None:
        good = {
            "id": "msg-1",
            "type": "dispatch",
            "from": "GovernanceAgent",
            "to": "HullDesigner",
            "payload": {"task_id": "task-1"},
        }
        self.assertEqual(validate_message_contract(good), [])

        bad = {
            "id": "",
            "type": "unknown_type",
            "from": "",
            "to": "Verifier",
            "payload": [],
        }
        errors = validate_message_contract(bad)
        self.assertTrue(any("id must be a non-empty string" in e for e in errors))
        self.assertTrue(any("type must be one of" in e for e in errors))
        self.assertTrue(any("from must be a non-empty string" in e for e in errors))
        self.assertTrue(any("payload must be an object" in e for e in errors))

    def test_replay_is_deterministic_and_schema_valid(self) -> None:
        start_session(self.session_id, initiated_by="tester", project_root=self.project_root)
        record_task(
            self.session_id,
            task={
                "id": "task-001",
                "description": "Implement curved gunwale",
                "status": "in_progress",
            },
            actor="GovernanceAgent",
            project_root=self.project_root,
        )
        record_gate(
            self.session_id,
            gate={
                "id": "gate-fr3",
                "description": "Curved gunwale verified",
                "status": "pending",
            },
            actor="Verifier",
            project_root=self.project_root,
        )
        record_agent(
            self.session_id,
            agent_name="HullDesigner",
            agent_state={"status": "working", "current_task": "task-001"},
            actor="GovernanceAgent",
            project_root=self.project_root,
        )
        record_message(
            self.session_id,
            message={
                "id": "msg-dispatch-001",
                "type": "dispatch",
                "from": "GovernanceAgent",
                "to": "HullDesigner",
                "payload": {"task_id": "task-001"},
            },
            actor="GovernanceAgent",
            project_root=self.project_root,
        )
        record_note(
            self.session_id,
            note="FR-3 gate pending verification evidence.",
            actor="Verifier",
            project_root=self.project_root,
        )

        state_one = replay_session(self.session_id, project_root=self.project_root)
        state_two = replay_session(self.session_id, project_root=self.project_root)
        self.assertEqual(state_one, state_two)

        state_errors = validate_orchestration_state(state_one)
        self.assertEqual(state_errors, [])

        self.assertEqual(state_one["session_id"], self.session_id)
        self.assertEqual(state_one["initiated_by"], "tester")
        self.assertEqual(len(state_one["tasks"]), 1)
        self.assertEqual(len(state_one["gates"]), 1)
        self.assertIn("HullDesigner", state_one["agents"])
        self.assertEqual(state_one["messages"][0]["type"], "dispatch")
        self.assertIn(state_one["messages"][0]["type"], MESSAGE_TYPES)
        self.assertEqual(len(state_one["notes"]), 1)

        paths = get_runtime_paths(self.project_root)
        events = []
        with paths["events_file"].open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line)
                if event.get("session_id") == self.session_id:
                    events.append(event)
        first_event = sorted(events, key=lambda e: int(e["seq"]))[0]
        self.assertEqual(state_one["created_at"], first_event["timestamp"])

    def test_sequence_is_strictly_increasing(self) -> None:
        start_session(self.session_id, initiated_by="tester", project_root=self.project_root)
        record_note(self.session_id, note="note-a", actor="agent-a", project_root=self.project_root)
        record_note(self.session_id, note="note-b", actor="agent-b", project_root=self.project_root)
        materialize_session_state(self.session_id, project_root=self.project_root)

        paths = get_runtime_paths(self.project_root)
        events = []
        with paths["events_file"].open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                events.append(json.loads(line))

        seq_values = [int(e["seq"]) for e in events if e["session_id"] == self.session_id]
        self.assertGreaterEqual(len(seq_values), 3)
        self.assertEqual(seq_values, sorted(seq_values))
        self.assertEqual(seq_values, list(range(1, len(seq_values) + 1)))

    def test_materialized_state_file_is_written(self) -> None:
        start_session(self.session_id, initiated_by="tester", project_root=self.project_root)
        state = record_note(self.session_id, note="persist me", actor="tester", project_root=self.project_root)

        paths = get_runtime_paths(self.project_root)
        state_file = paths["state_dir"] / f"{self.session_id}.json"
        self.assertTrue(state_file.exists())

        on_disk = json.loads(state_file.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["session_id"], self.session_id)
        self.assertEqual(on_disk["notes"], state["notes"])


if __name__ == "__main__":
    unittest.main()
