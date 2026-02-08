#!/usr/bin/env python3
"""Regression checks for mechanics-locked preset split and shape sensitivity."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "codex_hull_lab" / "tools" / "verify_shape_sensitivity.py"
PRESETS_DIR = PROJECT_ROOT / "codex_hull_lab" / "presets"
MECHANICS_BASE_PRESET = PRESETS_DIR / "gcsc_mechanics_locked.scad"
STYLE_PRESETS = (
    PRESETS_DIR / "gcsc_default.scad",
    PRESETS_DIR / "gcsc_fast_print.scad",
    PRESETS_DIR / "gcsc_high_stability.scad",
    PRESETS_DIR / "gcsc_experiment.scad",
)
WINDOWS_OPENSCAD = Path(r"C:\Program Files\OpenSCAD\openscad.exe")

LOCKED_KEYS = (
    "length_mm",
    "beam_mm",
    "depth_mm",
    "draft_mm",
    "wall_mm",
    "floor_mm",
    "seat_on",
    "anchor_on",
    "feet_on",
    "slot_skin_mm",
    "slot_column_diameter_mm",
    "slot_entry_overcut_mm",
    "slot_interior_bias_mm",
    "slot_outer_skin_min_mm",
)


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


class TestMechanicsPresetSplit(unittest.TestCase):
    def test_mechanics_locked_base_exists_with_core_dimensions(self) -> None:
        self.assertTrue(
            MECHANICS_BASE_PRESET.exists(),
            f"Missing mechanics-locked preset: {MECHANICS_BASE_PRESET}",
        )
        content = MECHANICS_BASE_PRESET.read_text(encoding="utf-8")
        for key in ("length_mm", "beam_mm", "depth_mm", "wall_mm", "floor_mm"):
            self.assertIsNotNone(
                re.search(rf"^\s*{key}\s*=", content, flags=re.MULTILINE),
                msg=f"Expected `{key}` assignment in {MECHANICS_BASE_PRESET}",
            )

    def test_style_presets_include_mechanics_locked_without_locked_overrides(self) -> None:
        for preset in STYLE_PRESETS:
            self.assertTrue(preset.exists(), f"Missing style preset: {preset}")
            content = preset.read_text(encoding="utf-8")
            self.assertIn(
                "include <gcsc_mechanics_locked.scad>",
                content,
                msg=f"{preset} must include gcsc_mechanics_locked.scad",
            )

            for key in LOCKED_KEYS:
                self.assertIsNone(
                    re.search(rf"^\s*{key}\s*=", content, flags=re.MULTILINE),
                    msg=f"{preset} should not override locked key `{key}`",
                )


class TestShapeSensitivityVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not SCRIPT_PATH.exists():
            raise unittest.SkipTest(f"Shape sensitivity script missing: {SCRIPT_PATH}")

        openscad_path = detect_openscad()
        if not openscad_path:
            raise unittest.SkipTest("OpenSCAD binary not found in test environment.")

        cls._tmpdir = tempfile.TemporaryDirectory()
        cls.tmp_path = Path(cls._tmpdir.name)
        cls.report_path = cls.tmp_path / "shape_sensitivity_report.json"

        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--project-root",
            str(PROJECT_ROOT),
            "--openscad-path",
            openscad_path,
            "--output-json",
            str(cls.report_path),
            "--tmp-dir",
            str(cls.tmp_path / "tmp"),
        ]
        cls.initial_result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1200,
        )

        if not cls.report_path.exists():
            raise RuntimeError(
                "Shape sensitivity report not produced.\n"
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
                "verify_shape_sensitivity.py failed.\n"
                f"STDOUT:\n{self.initial_result.stdout}\n"
                f"STDERR:\n{self.initial_result.stderr}"
            ),
        )
        self.assertTrue(self.report.get("pass"), "Expected pass=true in sensitivity report.")

    def test_required_metrics_and_gates_exist(self) -> None:
        baseline = self.report["measurements"]["baseline"]
        deltas = self.report["measurements"]["deltas"]

        for key in (
            "bow_tip_half_beam_mm",
            "stern_tip_half_beam_mm",
            "bow_tip_top_half_beam_mm",
            "stern_tip_top_half_beam_mm",
        ):
            self.assertIn(key, baseline, msg=f"Missing baseline metric `{key}`")

        for key in (
            "bow_tip_half_beam_mm",
            "stern_tip_half_beam_mm",
            "gunwale_min_tip_top_half_beam_mm",
        ):
            self.assertIn(key, deltas, msg=f"Missing delta metric `{key}`")
            self.assertGreater(
                deltas[key],
                0.0,
                msg=f"Expected positive sensitivity delta for `{key}`",
            )

        for gate in (
            "bow_curvature_response",
            "stern_curvature_response",
            "gunwale_tip_merge_response",
        ):
            self.assertIn(gate, self.report["gates"], msg=f"Missing gate `{gate}`")
            self.assertTrue(self.report["gates"][gate], msg=f"Expected gate `{gate}` to pass")

    def test_strict_bow_threshold_blocks_gate(self) -> None:
        measured_bow_delta = self.report["measurements"]["deltas"]["bow_tip_half_beam_mm"]
        strict_bow_threshold = measured_bow_delta + 0.25
        strict_report = self.tmp_path / "shape_sensitivity_strict.json"

        openscad_path = detect_openscad()
        self.assertIsNotNone(openscad_path, "OpenSCAD unexpectedly unavailable.")

        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--project-root",
            str(PROJECT_ROOT),
            "--openscad-path",
            str(openscad_path),
            "--output-json",
            str(strict_report),
            "--tmp-dir",
            str(self.tmp_path / "tmp_strict"),
            "--bow-delta-min-mm",
            f"{strict_bow_threshold:.6f}",
            "--stern-delta-min-mm",
            "0.01",
            "--gunwale-delta-min-mm",
            "0.01",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
        self.assertNotEqual(result.returncode, 0, "Expected strict bow threshold to fail.")

        strict = json.loads(strict_report.read_text(encoding="utf-8"))
        self.assertFalse(strict["gates"]["bow_curvature_response"])
        self.assertFalse(strict["pass"])


if __name__ == "__main__":
    unittest.main()
