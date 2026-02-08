#!/usr/bin/env python3
"""Integration checks for deterministic reference fit verification."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "codex_hull_lab" / "tools" / "verify_reference_fit.py"
WINDOWS_OPENSCAD = Path(r"C:\Program Files\OpenSCAD\openscad.exe")


def detect_openscad() -> str | None:
    env_path = os.environ.get("OPENSCAD_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    from_path = shutil.which("openscad")
    if from_path:
        return from_path

    if WINDOWS_OPENSCAD.exists():
        return str(WINDOWS_OPENSCAD)

    return None


class TestReferenceFitVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not SCRIPT_PATH.exists():
            raise unittest.SkipTest(f"Verification script missing: {SCRIPT_PATH}")

        openscad_path = detect_openscad()
        if not openscad_path:
            raise unittest.SkipTest("OpenSCAD binary not found in test environment.")

        cls._tmpdir = tempfile.TemporaryDirectory()
        cls.tmp_path = Path(cls._tmpdir.name)
        cls.export_dir = cls.tmp_path / "exports"
        cls.report_path = cls.tmp_path / "reference_fit_report.json"

        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--project-root",
            str(PROJECT_ROOT),
            "--openscad-path",
            openscad_path,
            "--export-dir",
            str(cls.export_dir),
            "--output-json",
            str(cls.report_path),
            "--floor-clearance-min-mm",
            "2.0",
        ]
        cls.initial_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,
        )

        if not cls.report_path.exists():
            raise RuntimeError(
                "Reference fit report not produced.\n"
                f"STDOUT:\n{cls.initial_result.stdout}\n"
                f"STDERR:\n{cls.initial_result.stderr}"
            )

        cls.report = json.loads(cls.report_path.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmpdir.cleanup()

    def test_initial_run_passes(self) -> None:
        self.assertEqual(
            self.initial_result.returncode,
            0,
            msg=(
                "verify_reference_fit.py failed.\n"
                f"STDOUT:\n{self.initial_result.stdout}\n"
                f"STDERR:\n{self.initial_result.stderr}"
            ),
        )
        self.assertTrue(self.report.get("pass"), "Expected pass=true in reference fit report.")

    def test_slot_checks_cover_all_locked_axes(self) -> None:
        slot_checks = self.report["measurements"]["slot_checks"]
        self.assertEqual(len(slot_checks), 4, "Expected four slot checks (x+/-, y+/-).")

        for slot in slot_checks:
            self.assertLessEqual(
                slot["axis_error_mm"],
                self.report["thresholds"]["axis_tolerance_mm"] + 1e-6,
            )
            self.assertGreaterEqual(
                slot["corridor_min_radial_clearance_mm"],
                self.report["thresholds"]["corridor_radial_clearance_min_mm"] - 1e-6,
            )

    def test_frame_metrics_are_present_and_positive(self) -> None:
        frame_checks = self.report["measurements"]["frame_checks"]
        self.assertEqual(len(frame_checks), 2, "Expected frame checks for x=-spacing and x=+spacing.")

        for frame in frame_checks:
            self.assertEqual(frame["penetrating_points_over_tolerance"], 0)
            self.assertGreater(frame["min_gap_mm"], 0.0)
            self.assertIsNotNone(frame["floor_clearance_min_mm"])
            self.assertGreaterEqual(
                frame["floor_clearance_min_mm"],
                self.report["thresholds"]["floor_clearance_min_mm"] - 1e-6,
            )

    def test_floor_gate_blocks_when_threshold_exceeds_measured_clearance(self) -> None:
        measured_floor = self.report["measurements"]["overall_floor_clearance_min_mm"]
        self.assertIsNotNone(measured_floor)

        strict_floor = measured_floor + 0.5
        strict_report = self.tmp_path / "reference_fit_strict.json"

        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--project-root",
            str(PROJECT_ROOT),
            "--hull-stl",
            self.report["inputs"]["hull_stl"],
            "--frame-stl",
            self.report["inputs"]["frame_stl"],
            "--slot-plug-stl",
            self.report["inputs"]["slot_plug_stl"],
            "--output-json",
            str(strict_report),
            "--floor-clearance-min-mm",
            str(strict_floor),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        self.assertNotEqual(result.returncode, 0, "Expected strict floor threshold to fail.")

        strict = json.loads(strict_report.read_text(encoding="utf-8"))
        self.assertFalse(strict["gates"]["frame_floor_clearance"])
        self.assertFalse(strict["pass"])


if __name__ == "__main__":
    unittest.main()
