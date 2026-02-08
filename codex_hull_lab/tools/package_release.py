#!/usr/bin/env python3
"""Release packaging automation for codex_hull_lab."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PRESETS = (
    "gcsc_default",
    "gcsc_fast_print",
    "gcsc_high_stability",
    "gcsc_experiment",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_openscad(openscad_path: str | None) -> str:
    candidates: list[str] = []
    if openscad_path:
        candidates.append(openscad_path)
    env_path = os.environ.get("OPENSCAD_PATH", "").strip()
    if env_path:
        candidates.append(env_path)
    which_path = shutil.which("openscad")
    if which_path:
        candidates.append(which_path)
    candidates.append(r"C:\Program Files\OpenSCAD\openscad.exe")
    for candidate in candidates:
        if not candidate:
            continue
        resolved = shutil.which(candidate) or candidate
        if Path(resolved).exists():
            return str(Path(resolved))
    raise FileNotFoundError("OpenSCAD binary not found. Set OPENSCAD_PATH or pass --openscad-path.")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(
        description="Export release artifacts (STL/3MF) with provenance and validation reports."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=project_root,
        help="Repository root. Defaults to auto-detected root.",
    )
    parser.add_argument(
        "--version",
        default=f"v{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        help="Release bundle version folder name.",
    )
    parser.add_argument(
        "--release-root",
        type=Path,
        default=project_root / "_codex" / "releases",
        help="Root directory where release bundles are created.",
    )
    parser.add_argument(
        "--presets",
        nargs="+",
        default=list(DEFAULT_PRESETS),
        help="Preset names to export.",
    )
    parser.add_argument(
        "--openscad-path",
        default=None,
        help="Path to OpenSCAD binary. Falls back to OPENSCAD_PATH, PATH, then Windows default.",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validate_full.py before packaging.",
    )
    parser.add_argument(
        "--allow-signature-drift",
        action="store_true",
        help="Pass allow-signature-drift override to validate_full.py.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing release folder.",
    )
    return parser.parse_args()


def relative_include(wrapper_dir: Path, target: Path) -> str:
    try:
        return os.path.relpath(target, start=wrapper_dir).replace("\\", "/")
    except ValueError:
        return target.resolve().as_posix()


def run_command(argv: list[str], cwd: Path, timeout_s: int = 3600) -> dict[str, Any]:
    start = time.monotonic()
    started_utc = now_utc()
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=timeout_s,
    )
    return {
        "argv": argv,
        "cwd": str(cwd),
        "started_utc": started_utc,
        "duration_s": round(time.monotonic() - start, 3),
        "returncode": int(result.returncode),
        "pass": result.returncode == 0,
        "stdout_tail": "\n".join((result.stdout or "").splitlines()[-80:]),
        "stderr_tail": "\n".join((result.stderr or "").splitlines()[-80:]),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def detect_git_commit(project_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    if result.returncode != 0:
        return None
    commit = (result.stdout or "").strip()
    return commit or None


def export_preset(
    *,
    openscad_bin: str,
    project_root: Path,
    preset: str,
    wrapper_dir: Path,
    stl_path: Path,
    three_mf_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    preset_file = project_root / "codex_hull_lab" / "presets" / f"{preset}.scad"
    hull_core = project_root / "codex_hull_lab" / "src" / "gcsc_hull_core.scad"
    if not preset_file.exists():
        return (
            {"preset": preset, "pass": False, "error": f"Missing preset file: {preset_file}"},
            [],
        )
    if not hull_core.exists():
        return (
            {"preset": preset, "pass": False, "error": f"Missing hull core file: {hull_core}"},
            [],
        )

    wrapper_dir.mkdir(parents=True, exist_ok=True)
    wrapper_path = wrapper_dir / f"{preset}_release_entry.scad"
    wrapper_text = "\n".join(
        [
            f"include <{relative_include(wrapper_dir, preset_file)}>;",
            f"include <{relative_include(wrapper_dir, hull_core)}>;",
            "",
            "gcsc_hull_build();",
            "",
        ]
    )
    wrapper_path.write_text(wrapper_text, encoding="utf-8")

    stl_cmd = [openscad_bin, "--render", "-o", str(stl_path), str(wrapper_path)]
    three_mf_cmd = [openscad_bin, "--render", "-o", str(three_mf_path), str(wrapper_path)]
    stl_record = run_command(stl_cmd, cwd=project_root, timeout_s=1800)
    three_mf_record = run_command(three_mf_cmd, cwd=project_root, timeout_s=1800)

    pass_all = (
        stl_record["pass"]
        and three_mf_record["pass"]
        and stl_path.exists()
        and three_mf_path.exists()
    )
    export_record = {
        "preset": preset,
        "wrapper": str(wrapper_path),
        "pass": bool(pass_all),
        "stl": stl_record,
        "three_mf": three_mf_record,
        "stl_path": str(stl_path),
        "three_mf_path": str(three_mf_path),
    }
    return export_record, [stl_record, three_mf_record]


def write_provenance(
    *,
    artifact_path: Path,
    preset: str,
    format_name: str,
    openscad_bin: str,
    git_commit: str | None,
    validation_report_path: Path,
    manifest_rel_path: str,
) -> Path:
    provenance = {
        "timestamp_utc": now_utc(),
        "preset": preset,
        "format": format_name,
        "artifact_file": str(artifact_path),
        "artifact_sha256": sha256_file(artifact_path),
        "artifact_bytes": int(artifact_path.stat().st_size),
        "openscad_path": openscad_bin,
        "git_commit": git_commit,
        "validation_report": str(validation_report_path),
        "release_manifest": manifest_rel_path,
    }
    provenance_path = artifact_path.with_suffix(artifact_path.suffix + ".provenance.json")
    provenance_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return provenance_path


def collect_report_paths(reports_dir: Path, full_report_path: Path) -> list[Path]:
    selected: set[Path] = set()
    if full_report_path.exists():
        selected.add(full_report_path.resolve())
        try:
            full_report = json.loads(full_report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            full_report = {}
        if isinstance(full_report, dict):
            baseline_reports = full_report.get("baseline_reports", {})
            if isinstance(baseline_reports, dict):
                for key in ("reference_fit_report", "shape_sensitivity_report"):
                    value = baseline_reports.get(key)
                    if isinstance(value, str):
                        path = Path(value)
                        if not path.is_absolute():
                            path = reports_dir / path
                        if path.exists():
                            selected.add(path.resolve())
            sweep = full_report.get("robustness_sweep", {})
            if isinstance(sweep, dict):
                scenarios = sweep.get("scenarios", [])
                if isinstance(scenarios, list):
                    for scenario in scenarios:
                        if not isinstance(scenario, dict):
                            continue
                        value = scenario.get("report_path")
                        if isinstance(value, str):
                            path = Path(value)
                            if not path.is_absolute():
                                path = reports_dir / path
                            if path.exists():
                                selected.add(path.resolve())
    if not selected:
        for report in reports_dir.glob("*.json"):
            selected.add(report.resolve())
    return sorted(selected)


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    release_root = args.release_root.resolve()
    release_dir = release_root / args.version
    reports_dir = project_root / "_codex" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    if release_dir.exists() and not args.overwrite:
        print(f"Release directory exists. Use --overwrite to replace: {release_dir}", file=sys.stderr)
        return 2
    if release_dir.exists() and args.overwrite:
        shutil.rmtree(release_dir)

    openscad_bin = resolve_openscad(args.openscad_path)
    git_commit = detect_git_commit(project_root)

    release_artifacts_dir = release_dir / "artifacts"
    release_stl_dir = release_artifacts_dir / "stl"
    release_3mf_dir = release_artifacts_dir / "3mf"
    release_reports_dir = release_dir / "reports"
    generated_dir = release_dir / "_generated_scad"
    release_stl_dir.mkdir(parents=True, exist_ok=True)
    release_3mf_dir.mkdir(parents=True, exist_ok=True)
    release_reports_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    validation_record: dict[str, Any] | None = None
    validation_report_path = reports_dir / "full_validation_report.json"
    if not args.skip_validation:
        validate_script = project_root / "codex_hull_lab" / "tools" / "validate_full.py"
        validate_cmd = [
            sys.executable,
            str(validate_script),
            "--project-root",
            str(project_root),
            "--output-json",
            str(validation_report_path),
        ]
        if args.openscad_path:
            validate_cmd.extend(["--openscad-path", args.openscad_path])
        if args.allow_signature_drift:
            validate_cmd.append("--allow-signature-drift")
        validation_record = run_command(validate_cmd, cwd=project_root, timeout_s=10800)
        if not validation_record["pass"]:
            print("Validation failed; release packaging aborted.", file=sys.stderr)
            print(validation_record["stderr_tail"], file=sys.stderr)
            return 1

    export_records: list[dict[str, Any]] = []
    artifact_entries: list[dict[str, Any]] = []
    all_pass = True

    for preset in args.presets:
        stl_path = release_stl_dir / f"{preset}.stl"
        three_mf_path = release_3mf_dir / f"{preset}.3mf"
        export_record, _ = export_preset(
            openscad_bin=openscad_bin,
            project_root=project_root,
            preset=preset,
            wrapper_dir=generated_dir,
            stl_path=stl_path,
            three_mf_path=three_mf_path,
        )
        export_records.append(export_record)
        if not export_record.get("pass"):
            all_pass = False
            continue

        stl_prov = write_provenance(
            artifact_path=stl_path,
            preset=preset,
            format_name="stl",
            openscad_bin=openscad_bin,
            git_commit=git_commit,
            validation_report_path=validation_report_path,
            manifest_rel_path="release_manifest.json",
        )
        three_mf_prov = write_provenance(
            artifact_path=three_mf_path,
            preset=preset,
            format_name="3mf",
            openscad_bin=openscad_bin,
            git_commit=git_commit,
            validation_report_path=validation_report_path,
            manifest_rel_path="release_manifest.json",
        )

        artifact_entries.append(
            {
                "preset": preset,
                "stl": {
                    "path": str(stl_path),
                    "sha256": sha256_file(stl_path),
                    "bytes": int(stl_path.stat().st_size),
                    "provenance": str(stl_prov),
                },
                "three_mf": {
                    "path": str(three_mf_path),
                    "sha256": sha256_file(three_mf_path),
                    "bytes": int(three_mf_path.stat().st_size),
                    "provenance": str(three_mf_prov),
                },
            }
        )

    copied_reports: list[str] = []
    report_paths = collect_report_paths(reports_dir=reports_dir, full_report_path=validation_report_path)
    for report in report_paths:
        dest = release_reports_dir / report.name
        shutil.copy2(report, dest)
        copied_reports.append(str(dest))

    manifest = {
        "version": args.version,
        "created_utc": now_utc(),
        "project_root": str(project_root),
        "git_commit": git_commit,
        "openscad_path": openscad_bin,
        "validation": validation_record,
        "validation_report": str(validation_report_path),
        "reports_copied": copied_reports,
        "exports": export_records,
        "artifacts": artifact_entries,
        "pass": bool(all_pass and (validation_record is None or validation_record.get("pass"))),
    }
    manifest_path = release_dir / "release_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Release bundle: {release_dir}")
    print(f"Manifest: {manifest_path}")
    print(f"PASS: {manifest['pass']}")
    return 0 if manifest["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
