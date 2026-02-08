#!/usr/bin/env python3
"""Unit tests for package_release.py helpers."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "codex_hull_lab" / "tools" / "package_release.py"


def load_package_release_module():
    spec = importlib.util.spec_from_file_location("package_release_under_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


class TestPackageReleaseHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package_release = load_package_release_module()

    def test_collect_report_paths_prefers_manifest_referenced_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports_dir = root / "_codex" / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            full_report = reports_dir / "full_validation_report.json"
            reference_fit = reports_dir / "reference_fit_report.json"
            shape = reports_dir / "shape_sensitivity_report.json"
            sweep_report = reports_dir / "reference_fit_sweep_gcsc_default.json"

            for path in (reference_fit, shape, sweep_report):
                path.write_text("{}", encoding="utf-8")

            full_report.write_text(
                json.dumps(
                    {
                        "baseline_reports": {
                            "reference_fit_report": str(reference_fit),
                            "shape_sensitivity_report": str(shape),
                        },
                        "robustness_sweep": {
                            "scenarios": [
                                {
                                    "name": "gcsc_default:baseline",
                                    "report_path": str(sweep_report),
                                }
                            ]
                        },
                    }
                ),
                encoding="utf-8",
            )

            selected = self.package_release.collect_report_paths(
                reports_dir=reports_dir,
                full_report_path=full_report,
            )
            selected_set = {path.resolve() for path in selected}
            self.assertIn(full_report.resolve(), selected_set)
            self.assertIn(reference_fit.resolve(), selected_set)
            self.assertIn(shape.resolve(), selected_set)
            self.assertIn(sweep_report.resolve(), selected_set)

    def test_write_provenance_includes_hash_and_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "gcsc_default.stl"
            artifact.write_bytes(b"mock-stl-data")
            validation_report = root / "full_validation_report.json"
            validation_report.write_text("{}", encoding="utf-8")

            provenance_path = self.package_release.write_provenance(
                artifact_path=artifact,
                preset="gcsc_default",
                format_name="stl",
                openscad_bin="openscad",
                git_commit="abc123",
                validation_report_path=validation_report,
                manifest_rel_path="release_manifest.json",
            )

            payload = json.loads(provenance_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["preset"], "gcsc_default")
            self.assertEqual(payload["format"], "stl")
            self.assertEqual(payload["artifact_file"], str(artifact))
            self.assertEqual(payload["artifact_bytes"], artifact.stat().st_size)
            self.assertEqual(
                payload["artifact_sha256"],
                self.package_release.sha256_file(artifact),
            )


if __name__ == "__main__":
    unittest.main()
