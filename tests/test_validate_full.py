#!/usr/bin/env python3
"""Unit tests for validate_full.py sweep profile and quick-mode behavior."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import trimesh


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "codex_hull_lab" / "tools" / "validate_full.py"


def load_validate_full_module():
    spec = importlib.util.spec_from_file_location("validate_full_under_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


class TestValidateFullConfigAndQuickMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validate_full = load_validate_full_module()

    def test_normalize_sweep_profile_loads_perturbations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "sweep.json"
            config_path.write_text(
                json.dumps(
                    {
                        "profiles": {
                            "full": {
                                "presets": ["gcsc_default", "gcsc_fast_print"],
                                "perturbations": [
                                    {
                                        "name": "floor_plus_0p80",
                                        "overrides": {"floor_mm": 10.8},
                                    }
                                ],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            profile = self.validate_full.normalize_sweep_profile(config_path, "full")
            self.assertEqual(profile["name"], "full")
            self.assertEqual(profile["presets"], ["gcsc_default", "gcsc_fast_print"])
            self.assertEqual(profile["perturbations"][0][0], "floor_plus_0p80")
            self.assertEqual(profile["perturbations"][0][1]["floor_mm"], 10.8)

    def test_normalize_sweep_profile_rejects_non_numeric_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "sweep.json"
            config_path.write_text(
                json.dumps(
                    {
                        "profiles": {
                            "full": {
                                "presets": ["gcsc_default"],
                                "perturbations": [
                                    {
                                        "name": "bad_override",
                                        "overrides": {"wall_mm": "thick"},
                                    }
                                ],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                self.validate_full.normalize_sweep_profile(config_path, "full")

    def test_build_command_suite_quick_mode_reduces_commands(self) -> None:
        quick_specs = self.validate_full.build_command_suite(
            project_root=PROJECT_ROOT,
            reports_dir=PROJECT_ROOT / "_codex" / "reports",
            openscad_path=None,
            floor_clearance_min_mm=2.0,
            baseline_preset="gcsc_default",
            quick_mode=True,
        )
        quick_names = [spec.name for spec in quick_specs]
        self.assertEqual(
            quick_names,
            ["verify_reference_fit", "verify_shape_sensitivity"],
        )

        full_specs = self.validate_full.build_command_suite(
            project_root=PROJECT_ROOT,
            reports_dir=PROJECT_ROOT / "_codex" / "reports",
            openscad_path=None,
            floor_clearance_min_mm=2.0,
            baseline_preset="gcsc_default",
            quick_mode=False,
        )
        full_names = [spec.name for spec in full_specs]
        self.assertIn("test_reference_fit", full_names)
        self.assertIn("test_shape_sensitivity", full_names)
        self.assertIn("test_functional_requirements_hook", full_names)


class TestValidateFullSweepCaching(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validate_full = load_validate_full_module()

    def test_robustness_sweep_reuses_cached_frame_and_slot_stls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports_dir = root / "_codex" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            (root / "codex_hull_lab" / "src").mkdir(parents=True, exist_ok=True)
            (root / "codex_hull_lab" / "presets").mkdir(parents=True, exist_ok=True)
            (root / "codex_hull_lab" / "reference").mkdir(parents=True, exist_ok=True)
            (root / "codex_hull_lab" / "src" / "gcsc_hull_core.scad").write_text(
                "module gcsc_hull_build(){}\n",
                encoding="utf-8",
            )
            (root / "codex_hull_lab" / "presets" / "gcsc_default.scad").write_text(
                "// preset\n",
                encoding="utf-8",
            )
            (root / "codex_hull_lab" / "reference" / "frame_v5_3_reference.scad").write_text(
                "module gcsc_reference_frame_v53_infill(){}\n",
                encoding="utf-8",
            )
            (root / "codex_hull_lab" / "reference" / "slot_plug_reference.scad").write_text(
                "module gcsc_reference_slot_plug(){}\n",
                encoding="utf-8",
            )

            args = argparse.Namespace(
                openscad_path=None,
                floor_clearance_min_mm=2.0,
            )

            export_calls: list[Path] = []
            ref_calls: list[dict[str, object]] = []

            def fake_export(*, openscad_bin: str, input_scad: Path, output_file: Path, cwd: Path):
                del openscad_bin, cwd
                export_calls.append(output_file)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text("solid mock\nendsolid mock\n", encoding="utf-8")
                return {
                    "name": "openscad_export",
                    "argv": ["openscad", "--render"],
                    "cwd": str(root),
                    "started_utc": "2026-02-08T00:00:00Z",
                    "duration_s": 0.01,
                    "returncode": 0,
                    "pass": True,
                    "stdout_tail": "",
                    "stderr_tail": "",
                    "output_file": str(output_file),
                }

            def fake_reference_fit(**kwargs):
                ref_calls.append(kwargs)
                report = {
                    "pass": True,
                    "gates": {
                        "slot_insertion_corridor": True,
                        "frame_interference": True,
                        "frame_floor_clearance": True,
                    },
                    "measurements": {
                        "slot_checks": [{"corridor_min_radial_clearance_mm": 0.25}],
                        "frame_checks": [{"min_gap_mm": 0.20, "max_penetration_mm": 0.0}],
                        "overall_floor_clearance_min_mm": 2.5,
                    },
                }
                return (
                    {
                        "name": "verify_reference_fit:explicit_stls",
                        "argv": ["python", "verify_reference_fit.py"],
                        "cwd": str(root),
                        "timeout_s": 2400,
                        "started_utc": "2026-02-08T00:00:00Z",
                        "duration_s": 0.5,
                        "timed_out": False,
                        "returncode": 0,
                        "pass": True,
                        "stdout_tail": "",
                        "stderr_tail": "",
                    },
                    report,
                )

            with mock.patch.object(self.validate_full, "run_openscad_export", side_effect=fake_export):
                with mock.patch.object(
                    self.validate_full, "run_reference_fit_command", side_effect=fake_reference_fit
                ):
                    result = self.validate_full.robustness_sweep(
                        args=args,
                        project_root=root,
                        reports_dir=reports_dir,
                        openscad_bin="openscad",
                        baseline_reference_report=None,
                        sweep_profile={
                            "name": "full",
                            "presets": ["gcsc_default"],
                            "perturbations": [("floor_plus_0p80", {"floor_mm": 10.8})],
                        },
                    )

            self.assertTrue(result["pass"])
            self.assertEqual(len(ref_calls), 2, "Expected baseline + perturbation reference-fit calls.")
            self.assertEqual(
                export_calls.count(Path(result["cache"]["frame_stl"])),
                1,
                "Frame STL should export once and be reused.",
            )
            self.assertEqual(
                export_calls.count(Path(result["cache"]["slot_plug_stl"])),
                1,
                "Slot-plug STL should export once and be reused.",
            )
            self.assertTrue(all(call.get("frame_stl") is not None for call in ref_calls))
            self.assertTrue(all(call.get("slot_plug_stl") is not None for call in ref_calls))


class TestValidateFullPolicyAndManufacturability(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validate_full = load_validate_full_module()

    def test_golden_signature_policy_blocks_without_override_and_logs_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports_dir = root / "_codex" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            hull_stl = root / "hull.stl"
            trimesh.creation.box(extents=[20.0, 10.0, 6.0]).export(hull_stl)

            baseline_report = reports_dir / "reference_fit_sweep_gcsc_default.json"
            baseline_report.write_text(
                json.dumps({"inputs": {"hull_stl": str(hull_stl)}}),
                encoding="utf-8",
            )

            signature_file = root / "golden_geometry_signatures.json"
            signature_file.write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "presets": {
                            "gcsc_default": {
                                "metrics": {
                                    "extent_x_mm": {"min": 1.0, "max": 2.0},
                                }
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            args = argparse.Namespace(
                signature_file=signature_file,
                allow_signature_drift=False,
                write_signature_baseline=False,
                signature_relative_band=0.03,
                signature_absolute_band_mm=0.5,
            )
            sweep_result = {
                "scenarios": [
                    {
                        "name": "gcsc_default:baseline",
                        "report_path": str(baseline_report),
                    }
                ]
            }

            with mock.patch.dict(os.environ, {}, clear=True):
                result = self.validate_full.golden_signature_validation(
                    args=args,
                    project_root=root,
                    sweep_result=sweep_result,
                    sweep_presets=["gcsc_default"],
                )
            self.assertFalse(result["raw_pass"])
            self.assertFalse(result["pass"])
            self.assertFalse(result["allow_drift_override"])
            self.assertEqual(result["policy"]["override_source"], "none")
            self.assertIn("gcsc_default", result["drifted_metrics_by_preset"])
            self.assertIn("extent_x_mm", result["drifted_metrics_by_preset"]["gcsc_default"])

            with mock.patch.dict(os.environ, {"GCSC_ALLOW_SIGNATURE_DRIFT": "1"}, clear=False):
                result_with_override = self.validate_full.golden_signature_validation(
                    args=args,
                    project_root=root,
                    sweep_result=sweep_result,
                    sweep_presets=["gcsc_default"],
                )
            self.assertTrue(result_with_override["pass"])
            self.assertFalse(result_with_override["raw_pass"])
            self.assertTrue(result_with_override["override_used"])
            self.assertEqual(result_with_override["policy"]["override_source"], "env")

    def test_manufacturability_uses_sampled_local_thickness_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            presets_dir = root / "codex_hull_lab" / "presets"
            presets_dir.mkdir(parents=True, exist_ok=True)
            preset_path = presets_dir / "gcsc_default.scad"
            preset_path.write_text(
                "\n".join(
                    [
                        "wall_mm = 1.60;",
                        "wall_end_taper_ratio = 1.00;",
                        "floor_mm = 2.00;",
                        "slot_outer_skin_min_mm = 1.40;",
                        "slot_skin_mm = 1.35;",
                        "feet_on = true;",
                        "foot_recess_depth_mm = 0.50;",
                        "foot_recess_skin_mm = 1.00;",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            hull_stl = root / "hull.stl"
            trimesh.creation.box(extents=[30.0, 14.0, 8.0]).export(hull_stl)
            baseline_reference_report = {
                "inputs": {
                    "preset": "gcsc_default",
                    "hull_stl": str(hull_stl),
                }
            }

            args = argparse.Namespace(
                min_wall_thickness_mm=1.0,
                wall_thickness_probe_count=200,
                wall_thickness_probe_min_valid=20,
                wall_thickness_probe_percentile=5.0,
                wall_thickness_probe_noise_floor_mm=0.25,
                min_recess_skin_mm=1.0,
                max_risky_overhang_ratio=1.0,
                max_overhang_from_horizontal_deg=45.0,
                contact_z_tolerance_mm=0.2,
                min_contact_area_mm2=0.0,
                min_contact_span_x_mm=0.0,
                min_contact_span_y_mm=0.0,
            )

            with mock.patch.object(
                self.validate_full,
                "sample_local_thickness_probes",
                return_value={
                    "status": "ok",
                    "probe_count": 200,
                    "valid_probe_count": 200,
                    "percentile_mm": 0.55,
                    "minimum_mm": 0.50,
                },
            ):
                result = self.validate_full.manufacturability_validation(
                    args=args,
                    project_root=root,
                    baseline_reference_report=baseline_reference_report,
                )

            self.assertTrue(result["gates"]["minimum_wall_thickness"])
            self.assertFalse(result["gates"]["sampled_local_wall_thickness"])
            self.assertIn("sampled_local_thickness_probes", result["measurements"])
            self.assertFalse(result["pass"])


if __name__ == "__main__":
    unittest.main()
