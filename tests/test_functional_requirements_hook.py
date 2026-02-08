#!/usr/bin/env python3
"""Regression checks for functional requirements hook deterministic mechanics gates."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOOK_PATH = PROJECT_ROOT / ".claude" / "hooks" / "functional-requirements-check.py"

PAYLOAD = {
    "tool_name": "Write",
    "tool_input": {
        "file_path": "codex_hull_lab/src/gcsc_hull_core.scad",
        "content": "module smoke_gate_test() {}",
    },
}


def build_report(
    *,
    slot_insertion_corridor: bool = True,
    frame_interference: bool = True,
    frame_floor_clearance: bool = True,
    corridor_min_radial_clearance_mm: float = 0.12,
    frame_min_gap_mm: float = 0.12,
    frame_max_penetration_mm: float = 0.0,
    overall_floor_clearance_min_mm: float = 3.0,
) -> dict[str, Any]:
    return {
        "timestamp_utc": "2026-02-08T00:00:00+00:00",
        "inputs": {
            "project_root": str(PROJECT_ROOT),
        },
        "thresholds": {
            "corridor_radial_clearance_min_mm": 0.08,
            "frame_min_gap_mm": 0.08,
            "frame_penetration_max_mm": 0.01,
            "floor_clearance_min_mm": 2.0,
        },
        "measurements": {
            "slot_checks": [
                {"corridor_min_radial_clearance_mm": corridor_min_radial_clearance_mm},
                {"corridor_min_radial_clearance_mm": corridor_min_radial_clearance_mm},
            ],
            "frame_checks": [
                {
                    "min_gap_mm": frame_min_gap_mm,
                    "max_penetration_mm": frame_max_penetration_mm,
                },
                {
                    "min_gap_mm": frame_min_gap_mm,
                    "max_penetration_mm": frame_max_penetration_mm,
                },
            ],
            "overall_floor_clearance_min_mm": overall_floor_clearance_min_mm,
        },
        "gates": {
            "hull_mesh_watertight": True,
            "reference_constants_locked": True,
            "slot_axis_positions": True,
            "slot_depth": True,
            "slot_insertion_corridor": slot_insertion_corridor,
            "frame_interference": frame_interference,
            "frame_floor_clearance": frame_floor_clearance,
        },
        "pass": (
            slot_insertion_corridor
            and frame_interference
            and frame_floor_clearance
        ),
    }


def run_hook(report: dict[str, Any], *, report_age_hours: float = 0.0, max_age_hours: float = 72.0) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        report_path = Path(tmp) / "reference_fit_report.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")

        if report_age_hours > 0:
            old_time = time.time() - (report_age_hours * 3600.0)
            os.utime(report_path, (old_time, old_time))

        env = os.environ.copy()
        env["GCSC_REFERENCE_FIT_REPORT"] = str(report_path)
        env["GCSC_REFERENCE_REPORT_MAX_AGE_HOURS"] = str(max_age_hours)

        return subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(PAYLOAD),
            text=True,
            capture_output=True,
            cwd=str(PROJECT_ROOT),
            env=env,
            timeout=60,
        )


class TestFunctionalRequirementsHookMechanicsGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not HOOK_PATH.exists():
            raise unittest.SkipTest(f"Hook missing: {HOOK_PATH}")

    def test_passes_with_clean_report(self) -> None:
        result = run_hook(build_report())
        self.assertEqual(
            result.returncode,
            0,
            msg=f"Unexpected block.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )

    def test_blocks_on_slot_insertion_corridor_failure(self) -> None:
        report = build_report(
            slot_insertion_corridor=False,
            corridor_min_radial_clearance_mm=0.02,
        )
        result = run_hook(report)
        self.assertEqual(result.returncode, 2, msg=f"Expected block.\nSTDERR:\n{result.stderr}")
        self.assertIn("slot_insertion_corridor", result.stderr)

    def test_blocks_on_frame_interference_failure(self) -> None:
        report = build_report(
            frame_interference=False,
            frame_min_gap_mm=0.01,
            frame_max_penetration_mm=0.09,
        )
        result = run_hook(report)
        self.assertEqual(result.returncode, 2, msg=f"Expected block.\nSTDERR:\n{result.stderr}")
        self.assertIn("frame_interference", result.stderr)

    def test_blocks_on_floor_clearance_failure(self) -> None:
        report = build_report(
            frame_floor_clearance=False,
            overall_floor_clearance_min_mm=1.25,
        )
        result = run_hook(report)
        self.assertEqual(result.returncode, 2, msg=f"Expected block.\nSTDERR:\n{result.stderr}")
        self.assertIn("frame_floor_clearance", result.stderr)

    def test_stale_report_is_ignored(self) -> None:
        # Fail-open for stale reports prevents stale JSON from deadlocking edits.
        report = build_report(frame_floor_clearance=False)
        result = run_hook(report, report_age_hours=3.0, max_age_hours=1.0)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"Stale report should not block.\nSTDERR:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
