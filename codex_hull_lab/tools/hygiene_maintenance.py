#!/usr/bin/env python3
"""Long-term hygiene utilities for codex_hull_lab."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MOJIBAKE_REPLACEMENTS = {
    "Â°": "°",
    "Â±": "±",
    "Ã—": "×",
    "â€™": "'",
    "â€œ": '"',
    "â€": '"',
    "â€“": "-",
    "â€”": "-",
    "â€¦": "...",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Cleanup stale _codex/tmp_* artifacts and normalize mojibake in inherited docs."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=project_root,
        help="Repository root. Defaults to auto-detected root.",
    )
    parser.add_argument(
        "--tmp-max-age-days",
        type=float,
        default=2.0,
        help="Age threshold in days for archiving _codex/tmp_* artifacts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report actions without modifying files.",
    )
    parser.add_argument(
        "--skip-tmp-cleanup",
        action="store_true",
        help="Skip _codex/tmp_* cleanup.",
    )
    parser.add_argument(
        "--skip-encoding-normalization",
        action="store_true",
        help="Skip mojibake normalization pass.",
    )
    return parser.parse_args()


def archive_stale_tmp_items(project_root: Path, max_age_days: float, dry_run: bool) -> dict[str, Any]:
    codex_dir = project_root / "_codex"
    if not codex_dir.exists():
        return {
            "scanned": 0,
            "moved": 0,
            "archive_dir": None,
            "items": [],
        }

    threshold_seconds = max(0.0, max_age_days) * 24.0 * 3600.0
    now = time.time()
    candidates = sorted(codex_dir.glob("tmp_*"), key=lambda p: p.name.lower())
    stale: list[Path] = []
    for path in candidates:
        try:
            age_seconds = now - path.stat().st_mtime
        except OSError:
            continue
        if age_seconds >= threshold_seconds:
            stale.append(path)

    archive_dir = codex_dir / "archive" / "tmp_cleanup" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    moved_items: list[dict[str, str]] = []
    if stale and not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)
        for src in stale:
            dest = archive_dir / src.name
            shutil.move(str(src), str(dest))
            moved_items.append({"from": str(src), "to": str(dest)})
    else:
        for src in stale:
            moved_items.append({"from": str(src), "to": str(archive_dir / src.name)})

    return {
        "scanned": len(candidates),
        "moved": len(stale),
        "archive_dir": str(archive_dir) if stale else None,
        "items": moved_items,
    }


def normalize_mojibake(project_root: Path, dry_run: bool) -> dict[str, Any]:
    targets = [
        project_root / "codex_hull_lab" / "Inheritable_Dimensions",
        project_root / "docs" / "archive" / "agent_artifacts",
    ]
    extensions = {".md", ".scad", ".txt"}

    scanned = 0
    changed_files: list[dict[str, Any]] = []
    for base in targets:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in extensions:
                continue
            scanned += 1
            try:
                original = path.read_text(encoding="utf-8")
            except OSError:
                continue
            updated = original
            replacement_counts: dict[str, int] = {}
            for bad, good in MOJIBAKE_REPLACEMENTS.items():
                count = updated.count(bad)
                if count > 0:
                    updated = updated.replace(bad, good)
                    replacement_counts[bad] = count
            if updated != original:
                if not dry_run:
                    path.write_text(updated, encoding="utf-8")
                changed_files.append(
                    {
                        "file": str(path),
                        "replacements": replacement_counts,
                    }
                )

    return {
        "scanned_files": scanned,
        "changed_files": changed_files,
        "changed_count": len(changed_files),
    }


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()

    tmp_cleanup = {"skipped": True}
    if not args.skip_tmp_cleanup:
        tmp_cleanup = archive_stale_tmp_items(
            project_root=project_root,
            max_age_days=args.tmp_max_age_days,
            dry_run=args.dry_run,
        )

    encoding = {"skipped": True}
    if not args.skip_encoding_normalization:
        encoding = normalize_mojibake(project_root=project_root, dry_run=args.dry_run)

    report = {
        "timestamp_utc": now_utc(),
        "project_root": str(project_root),
        "dry_run": bool(args.dry_run),
        "tmp_cleanup": tmp_cleanup,
        "encoding_normalization": encoding,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

