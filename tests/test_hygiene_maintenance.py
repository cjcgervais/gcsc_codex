#!/usr/bin/env python3
"""Unit tests for hygiene_maintenance.py helper behavior."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "codex_hull_lab" / "tools" / "hygiene_maintenance.py"


def load_hygiene_module():
    spec = importlib.util.spec_from_file_location("hygiene_maintenance_under_test", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module


class TestHygieneMaintenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hygiene = load_hygiene_module()

    def test_archive_stale_tmp_items_moves_only_old_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            codex_dir = project_root / "_codex"
            codex_dir.mkdir(parents=True, exist_ok=True)

            stale = codex_dir / "tmp_stale.txt"
            fresh = codex_dir / "tmp_fresh.txt"
            stale.write_text("old", encoding="utf-8")
            fresh.write_text("new", encoding="utf-8")

            old_time = time.time() - (5 * 24 * 3600)
            os.utime(stale, (old_time, old_time))

            result = self.hygiene.archive_stale_tmp_items(
                project_root=project_root,
                max_age_days=2.0,
                dry_run=False,
            )

            self.assertEqual(result["scanned"], 2)
            self.assertEqual(result["moved"], 1)
            self.assertFalse(stale.exists())
            self.assertTrue(fresh.exists())
            moved_dest = Path(result["items"][0]["to"])
            self.assertTrue(moved_dest.exists())

    def test_archive_stale_tmp_items_dry_run_does_not_move(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            codex_dir = project_root / "_codex"
            codex_dir.mkdir(parents=True, exist_ok=True)

            stale = codex_dir / "tmp_stale.txt"
            stale.write_text("old", encoding="utf-8")
            old_time = time.time() - (4 * 24 * 3600)
            os.utime(stale, (old_time, old_time))

            result = self.hygiene.archive_stale_tmp_items(
                project_root=project_root,
                max_age_days=1.0,
                dry_run=True,
            )

            self.assertEqual(result["moved"], 1)
            self.assertTrue(stale.exists(), "Dry run should not move stale files.")

    def test_normalize_mojibake_rewrites_known_sequences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            target_one = project_root / "codex_hull_lab" / "Inheritable_Dimensions"
            target_two = project_root / "docs" / "archive" / "agent_artifacts"
            target_one.mkdir(parents=True, exist_ok=True)
            target_two.mkdir(parents=True, exist_ok=True)

            replacement_items = list(self.hygiene.MOJIBAKE_REPLACEMENTS.items())
            bad_degree, good_degree = replacement_items[0]
            bad_plusminus, good_plusminus = replacement_items[1]
            file_one = target_one / "notes.md"
            file_two = target_two / "handoff.txt"
            file_one.write_text(f"Angle is 45{bad_degree}.", encoding="utf-8")
            file_two.write_text(f"Range is {bad_plusminus}0.2", encoding="utf-8")

            result = self.hygiene.normalize_mojibake(project_root=project_root, dry_run=False)

            self.assertEqual(result["changed_count"], 2)
            content_one = file_one.read_text(encoding="utf-8")
            content_two = file_two.read_text(encoding="utf-8")
            self.assertIn(good_degree, content_one)
            self.assertNotIn(bad_degree, content_one)
            self.assertIn(good_plusminus, content_two)
            self.assertNotIn(bad_plusminus, content_two)


if __name__ == "__main__":
    unittest.main()
