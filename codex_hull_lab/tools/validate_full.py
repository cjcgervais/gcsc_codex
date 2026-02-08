#!/usr/bin/env python3
"""Authoritative full validation entrypoint for codex_hull_lab.

This script is the single source of truth for local and CI validation.
It orchestrates existing deterministic checks and adds:
  - deterministic robustness sweeps across presets and bounded perturbations
  - sampled swing-path kinematic collision checks
  - manufacturability gates
  - golden geometry signature checks
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from trimesh.proximity import signed_distance


SWEEP_PROFILE_FULL = "full"
SWEEP_PROFILE_QUICK = "quick"


@dataclass(frozen=True)
class CommandSpec:
    name: str
    argv: list[str]
    timeout_s: int


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    reports_dir = project_root / "_codex" / "reports"
    default_full_report = reports_dir / "full_validation_report.json"
    default_signature_file = (
        project_root / "codex_hull_lab" / "reference" / "golden_geometry_signatures.json"
    )
    default_sweep_config = (
        project_root / "codex_hull_lab" / "reference" / "validation_sweep_config.json"
    )

    parser = argparse.ArgumentParser(
        description="Run full deterministic GCSC hull validation and emit one machine-readable report."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=project_root,
        help="Repository root. Defaults to auto-detected root.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=default_full_report,
        help="Full report output path.",
    )
    parser.add_argument(
        "--openscad-path",
        default=None,
        help="Path to OpenSCAD binary. Falls back to OPENSCAD_PATH, PATH, then Windows default.",
    )
    parser.add_argument(
        "--floor-clearance-min-mm",
        type=float,
        default=2.0,
        help="Floor clearance gate threshold used for reference-fit calls.",
    )
    parser.add_argument(
        "--allow-signature-drift",
        action="store_true",
        help="Explicit override to allow golden signature drift without failing overall validation.",
    )
    parser.add_argument(
        "--signature-file",
        type=Path,
        default=default_signature_file,
        help="Golden geometry signature bands JSON path.",
    )
    parser.add_argument(
        "--write-signature-baseline",
        action="store_true",
        help="Write/refresh golden signature bands from current observed geometry (explicit baseline update).",
    )
    parser.add_argument(
        "--signature-relative-band",
        type=float,
        default=0.03,
        help="Relative +/- band for volume and area when writing golden signatures.",
    )
    parser.add_argument(
        "--signature-absolute-band-mm",
        type=float,
        default=0.50,
        help="Absolute +/- band in mm for dimension metrics when writing golden signatures.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Fast local loop: run a reduced command suite and default to quick sweep profile.",
    )
    parser.add_argument(
        "--sweep-config",
        type=Path,
        default=default_sweep_config,
        help="JSON config containing sweep profiles/presets/perturbations.",
    )
    parser.add_argument(
        "--sweep-profile",
        choices=(SWEEP_PROFILE_FULL, SWEEP_PROFILE_QUICK),
        default=None,
        help="Sweep profile loaded from --sweep-config. Defaults to quick when --quick is set, else full.",
    )
    parser.add_argument(
        "--sweep-presets",
        nargs="+",
        default=None,
        help="Optional preset override for the selected sweep profile.",
    )
    parser.add_argument(
        "--kinematic-angle-min-deg",
        type=float,
        default=-24.0,
        help="Minimum sampled swing angle (deg) for dynamic kinematic validation.",
    )
    parser.add_argument(
        "--kinematic-angle-max-deg",
        type=float,
        default=24.0,
        help="Maximum sampled swing angle (deg) for dynamic kinematic validation.",
    )
    parser.add_argument(
        "--kinematic-angle-step-deg",
        type=float,
        default=3.0,
        help="Swing angle sample step (deg).",
    )
    parser.add_argument(
        "--min-wall-thickness-mm",
        type=float,
        default=1.00,
        help="Minimum acceptable manufacturability wall thickness estimate.",
    )
    parser.add_argument(
        "--wall-thickness-probe-count",
        type=int,
        default=1200,
        help="Deterministic face-center probe count used for sampled local wall-thickness checks.",
    )
    parser.add_argument(
        "--wall-thickness-probe-min-valid",
        type=int,
        default=60,
        help="Minimum valid sampled thickness probes required for a trustworthy local-thickness gate.",
    )
    parser.add_argument(
        "--wall-thickness-probe-percentile",
        type=float,
        default=5.0,
        help="Percentile (0-100) used as robust sampled local-thickness metric.",
    )
    parser.add_argument(
        "--wall-thickness-probe-noise-floor-mm",
        type=float,
        default=0.25,
        help="Ignore sampled thickness values below this floor to reduce tangential-ray numerical noise.",
    )
    parser.add_argument(
        "--min-recess-skin-mm",
        type=float,
        default=1.00,
        help="Minimum acceptable recess skin thickness.",
    )
    parser.add_argument(
        "--max-risky-overhang-ratio",
        type=float,
        default=0.35,
        help="Maximum allowed ratio of risky downward overhang area.",
    )
    parser.add_argument(
        "--max-overhang-from-horizontal-deg",
        type=float,
        default=45.0,
        help="Downward faces flatter than this angle from horizontal are considered risky.",
    )
    parser.add_argument(
        "--contact-z-tolerance-mm",
        type=float,
        default=0.20,
        help="Z tolerance above min-Z used to identify contact footprint points.",
    )
    parser.add_argument(
        "--min-contact-area-mm2",
        type=float,
        default=700.0,
        help="Minimum convex-hull footprint area gate.",
    )
    parser.add_argument(
        "--min-contact-span-x-mm",
        type=float,
        default=60.0,
        help="Minimum X span of contact footprint points.",
    )
    parser.add_argument(
        "--min-contact-span-y-mm",
        type=float,
        default=18.0,
        help="Minimum Y span of contact footprint points.",
    )
    parser.add_argument(
        "--no-subcommand-fail-fast",
        action="store_true",
        help="Keep running the command suite after command failures to maximize report coverage.",
    )
    return parser.parse_args()


def tail_text(text: str, max_lines: int = 80) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text.strip()
    return "\n".join(lines[-max_lines:]).strip()


def run_command(spec: CommandSpec, cwd: Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = time.monotonic()
    started_utc = now_utc()
    timed_out = False
    stdout = ""
    stderr = ""
    returncode = -1
    try:
        result = subprocess.run(
            spec.argv,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            env=env,
            timeout=spec.timeout_s,
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        returncode = int(result.returncode)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        returncode = 124
    ended = time.monotonic()
    return {
        "name": spec.name,
        "argv": spec.argv,
        "cwd": str(cwd),
        "timeout_s": spec.timeout_s,
        "started_utc": started_utc,
        "duration_s": round(ended - started, 3),
        "timed_out": timed_out,
        "returncode": returncode,
        "pass": returncode == 0,
        "stdout_tail": tail_text(stdout),
        "stderr_tail": tail_text(stderr),
    }


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


def relative_include(wrapper_dir: Path, target: Path) -> str:
    try:
        return os.path.relpath(target, start=wrapper_dir).replace("\\", "/")
    except ValueError:
        return target.resolve().as_posix()


def format_scad_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.8f}".rstrip("0").rstrip(".")
    return str(value)


def run_openscad_export(openscad_bin: str, input_scad: Path, output_file: Path, cwd: Path) -> dict[str, Any]:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [openscad_bin, "--render", "-o", str(output_file), str(input_scad)]
    started = time.monotonic()
    started_utc = now_utc()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        timeout=900,
    )
    duration_s = round(time.monotonic() - started, 3)
    passed = result.returncode == 0 and output_file.exists()
    return {
        "name": "openscad_export",
        "argv": cmd,
        "cwd": str(cwd),
        "started_utc": started_utc,
        "duration_s": duration_s,
        "returncode": int(result.returncode),
        "pass": passed,
        "stdout_tail": tail_text(result.stdout or ""),
        "stderr_tail": tail_text(result.stderr or ""),
        "output_file": str(output_file),
    }


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def bool_from_env(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def resolve_signature_drift_override(args: argparse.Namespace) -> dict[str, Any]:
    cli_override = bool(args.allow_signature_drift)
    env_override = bool_from_env("GCSC_ALLOW_SIGNATURE_DRIFT")
    allow_drift = bool(cli_override or env_override)
    if cli_override:
        source = "cli"
    elif env_override:
        source = "env"
    else:
        source = "none"
    return {
        "enabled": allow_drift,
        "source": source,
        "cli": cli_override,
        "env": env_override,
    }


def _validate_perturbation_overrides(name: str, overrides: Any) -> dict[str, Any]:
    if not isinstance(overrides, dict):
        raise ValueError(f"Perturbation `{name}` overrides must be an object.")
    normalized: dict[str, Any] = {}
    for key, value in overrides.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError(f"Perturbation `{name}` contains an invalid override key.")
        if not isinstance(value, (bool, int, float)):
            raise ValueError(
                f"Perturbation `{name}` override `{key}` must be bool/int/float (got {type(value).__name__})."
            )
        normalized[key] = value
    if not normalized:
        raise ValueError(f"Perturbation `{name}` overrides must not be empty.")
    return normalized


def normalize_sweep_profile(config_path: Path, profile_name: str) -> dict[str, Any]:
    config_data = load_json(config_path)
    if config_data is None:
        raise ValueError(f"Sweep config missing or invalid JSON: {config_path}")

    raw_profiles = config_data.get("profiles")
    if not isinstance(raw_profiles, dict):
        raise ValueError(f"Sweep config missing `profiles` object: {config_path}")

    raw_profile = raw_profiles.get(profile_name)
    if not isinstance(raw_profile, dict):
        raise ValueError(
            f"Sweep profile `{profile_name}` missing in config: {config_path}"
        )

    raw_presets = raw_profile.get("presets")
    if not isinstance(raw_presets, list) or not raw_presets:
        raise ValueError(f"Sweep profile `{profile_name}` must define a non-empty `presets` list.")

    presets: list[str] = []
    for preset in raw_presets:
        if not isinstance(preset, str) or not preset.strip():
            raise ValueError(f"Sweep profile `{profile_name}` contains invalid preset value.")
        presets.append(preset.strip())

    raw_perturbations = raw_profile.get("perturbations", [])
    if not isinstance(raw_perturbations, list):
        raise ValueError(f"Sweep profile `{profile_name}` has non-list `perturbations`.")

    perturbations: list[tuple[str, dict[str, Any]]] = []
    for entry in raw_perturbations:
        if not isinstance(entry, dict):
            raise ValueError(f"Sweep profile `{profile_name}` has invalid perturbation entry.")
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Sweep profile `{profile_name}` has perturbation without valid `name`.")
        overrides = _validate_perturbation_overrides(name=name.strip(), overrides=entry.get("overrides"))
        perturbations.append((name.strip(), overrides))

    return {
        "name": profile_name,
        "presets": presets,
        "perturbations": perturbations,
        "source_file": str(config_path),
    }


def resolve_sweep_profile(args: argparse.Namespace, project_root: Path) -> dict[str, Any]:
    profile_name = args.sweep_profile or (SWEEP_PROFILE_QUICK if args.quick else SWEEP_PROFILE_FULL)
    config_path = args.sweep_config.resolve()

    profile = normalize_sweep_profile(config_path=config_path, profile_name=profile_name)
    if args.sweep_presets:
        presets = [str(name).strip() for name in args.sweep_presets if str(name).strip()]
        if not presets:
            raise ValueError("At least one non-empty preset is required when using --sweep-presets.")
        profile["presets"] = presets

    missing = [
        str(project_root / "codex_hull_lab" / "presets" / f"{preset}.scad")
        for preset in profile["presets"]
        if not (project_root / "codex_hull_lab" / "presets" / f"{preset}.scad").exists()
    ]
    if missing:
        raise ValueError("Sweep presets missing from codex_hull_lab/presets: " + ", ".join(missing))
    return profile


def metric_min(items: Any, key: str) -> float | None:
    values: list[float] = []
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                values.append(float(item[key]))
            except (KeyError, TypeError, ValueError):
                continue
    if not values:
        return None
    return float(min(values))


def metric_max(items: Any, key: str) -> float | None:
    values: list[float] = []
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            try:
                values.append(float(item[key]))
            except (KeyError, TypeError, ValueError):
                continue
    if not values:
        return None
    return float(max(values))


def reference_fit_scenario_summary(
    *,
    name: str,
    report_path: Path,
    report: dict[str, Any] | None,
    command_record: dict[str, Any],
) -> dict[str, Any]:
    gates = report.get("gates", {}) if isinstance(report, dict) else {}
    measurements = report.get("measurements", {}) if isinstance(report, dict) else {}
    slot_checks = measurements.get("slot_checks", [])
    frame_checks = measurements.get("frame_checks", [])
    scenario = {
        "name": name,
        "report_path": str(report_path),
        "command": command_record,
        "report_present": isinstance(report, dict),
        "report_pass": bool(report.get("pass")) if isinstance(report, dict) else False,
        "gates": gates if isinstance(gates, dict) else {},
        "key_measurements": {
            "corridor_min_radial_clearance_mm": metric_min(slot_checks, "corridor_min_radial_clearance_mm"),
            "frame_min_gap_mm": metric_min(frame_checks, "min_gap_mm"),
            "frame_max_penetration_mm": metric_max(frame_checks, "max_penetration_mm"),
            "overall_floor_clearance_min_mm": measurements.get("overall_floor_clearance_min_mm"),
        },
    }
    scenario["required_gate_pass"] = bool(
        scenario["gates"].get("slot_insertion_corridor")
        and scenario["gates"].get("frame_interference")
        and scenario["gates"].get("frame_floor_clearance")
    )
    return scenario


def run_reference_fit_command(
    *,
    project_root: Path,
    output_json: Path,
    openscad_path: str | None,
    floor_clearance_min_mm: float,
    preset: str | None = None,
    hull_stl: Path | None = None,
    frame_stl: Path | None = None,
    slot_plug_stl: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    verify_script = project_root / "codex_hull_lab" / "tools" / "verify_reference_fit.py"
    argv = [
        sys.executable,
        str(verify_script),
        "--project-root",
        str(project_root),
        "--output-json",
        str(output_json),
        "--floor-clearance-min-mm",
        str(floor_clearance_min_mm),
    ]
    if openscad_path:
        argv.extend(["--openscad-path", openscad_path])
    if preset:
        argv.extend(["--preset", preset])
    if hull_stl and frame_stl and slot_plug_stl:
        argv.extend(
            [
                "--hull-stl",
                str(hull_stl),
                "--frame-stl",
                str(frame_stl),
                "--slot-plug-stl",
                str(slot_plug_stl),
            ]
        )
    record = run_command(
        CommandSpec(name=f"verify_reference_fit:{preset or 'explicit_stls'}", argv=argv, timeout_s=2400),
        cwd=project_root,
    )
    return record, load_json(output_json)


def write_perturbed_hull_wrapper(
    *,
    wrapper_path: Path,
    base_preset_path: Path,
    hull_core_path: Path,
    overrides: dict[str, Any],
) -> None:
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"include <{relative_include(wrapper_path.parent, base_preset_path)}>"]
    for key in sorted(overrides.keys()):
        lines.append(f"{key} = {format_scad_value(overrides[key])};")
    lines.append(f"include <{relative_include(wrapper_path.parent, hull_core_path)}>")
    lines.append("")
    lines.append("gcsc_hull_build();")
    lines.append("")
    wrapper_path.write_text("\n".join(lines), encoding="utf-8")


def write_module_wrapper(
    *,
    wrapper_path: Path,
    includes: list[Path],
    module_call: str,
) -> None:
    wrapper_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"include <{relative_include(wrapper_path.parent, include_path)}>" for include_path in includes]
    lines.extend(["", module_call.strip(), ""])
    wrapper_path.write_text("\n".join(lines), encoding="utf-8")


def cached_openscad_export(
    *,
    openscad_bin: str,
    input_scad: Path,
    output_file: Path,
    cwd: Path,
) -> dict[str, Any]:
    cmd = [openscad_bin, "--render", "-o", str(output_file), str(input_scad)]
    if output_file.exists():
        return {
            "name": "openscad_export",
            "argv": cmd,
            "cwd": str(cwd),
            "started_utc": now_utc(),
            "duration_s": 0.0,
            "returncode": 0,
            "pass": True,
            "stdout_tail": "",
            "stderr_tail": "",
            "output_file": str(output_file),
            "cache_hit": True,
        }
    record = run_openscad_export(
        openscad_bin=openscad_bin,
        input_scad=input_scad,
        output_file=output_file,
        cwd=cwd,
    )
    record["cache_hit"] = False
    return record


def robustness_sweep(
    *,
    args: argparse.Namespace,
    project_root: Path,
    reports_dir: Path,
    openscad_bin: str | None,
    baseline_reference_report: dict[str, Any] | None,
    sweep_profile: dict[str, Any],
) -> dict[str, Any]:
    sweep_root = reports_dir / "full_validation_tmp" / "robustness_sweep"
    sweep_root.mkdir(parents=True, exist_ok=True)
    cache_root = sweep_root / "cached_stls"
    generated_root = sweep_root / "generated_presets"
    cache_root.mkdir(parents=True, exist_ok=True)
    generated_root.mkdir(parents=True, exist_ok=True)

    sweep_presets = [str(name) for name in sweep_profile.get("presets", [])]
    perturbations = list(sweep_profile.get("perturbations", []))

    scenarios: list[dict[str, Any]] = []
    errors: list[str] = []
    baseline_reports_by_preset: dict[str, dict[str, Any]] = {}
    cache_records: list[dict[str, Any]] = []
    base_frame_stl: Path | None = None
    base_slot_plug_stl: Path | None = None

    if openscad_bin is not None:
        frame_reference = project_root / "codex_hull_lab" / "reference" / "frame_v5_3_reference.scad"
        slot_plug_reference = project_root / "codex_hull_lab" / "reference" / "slot_plug_reference.scad"
        missing_reference_sources = [
            str(path)
            for path in (frame_reference, slot_plug_reference)
            if not path.exists()
        ]
        if missing_reference_sources:
            errors.append(
                "Sweep cache source file(s) missing: " + ", ".join(missing_reference_sources)
            )
        else:
            frame_wrapper = generated_root / "reference_fit_frame_cache.scad"
            slot_plug_wrapper = generated_root / "reference_fit_slot_plug_cache.scad"
            write_module_wrapper(
                wrapper_path=frame_wrapper,
                includes=[frame_reference],
                module_call="gcsc_reference_frame_v53_infill();",
            )
            write_module_wrapper(
                wrapper_path=slot_plug_wrapper,
                includes=[slot_plug_reference],
                module_call="gcsc_reference_slot_plug();",
            )

            frame_cached_path = cache_root / "frame_reference.stl"
            slot_plug_cached_path = cache_root / "slot_plug_reference.stl"
            frame_export = cached_openscad_export(
                openscad_bin=openscad_bin,
                input_scad=frame_wrapper,
                output_file=frame_cached_path,
                cwd=project_root,
            )
            slot_plug_export = cached_openscad_export(
                openscad_bin=openscad_bin,
                input_scad=slot_plug_wrapper,
                output_file=slot_plug_cached_path,
                cwd=project_root,
            )
            cache_records.extend([frame_export, slot_plug_export])
            if frame_export["pass"] and slot_plug_export["pass"]:
                base_frame_stl = frame_cached_path
                base_slot_plug_stl = slot_plug_cached_path
            else:
                errors.append("Unable to export/reuse cached frame and slot-plug STLs for sweep scenarios.")
    else:
        errors.append("OpenSCAD binary unavailable; perturbation sweep could not run.")

    if (base_frame_stl is None or base_slot_plug_stl is None) and isinstance(baseline_reference_report, dict):
        inputs = baseline_reference_report.get("inputs", {})
        if isinstance(inputs, dict):
            frame_path = inputs.get("frame_stl")
            plug_path = inputs.get("slot_plug_stl")
            if isinstance(frame_path, str) and Path(frame_path).exists():
                base_frame_stl = Path(frame_path)
            if isinstance(plug_path, str) and Path(plug_path).exists():
                base_slot_plug_stl = Path(plug_path)

    hull_core_path = project_root / "codex_hull_lab" / "src" / "gcsc_hull_core.scad"
    presets_dir = project_root / "codex_hull_lab" / "presets"

    for preset in sweep_presets:
        base_preset = presets_dir / f"{preset}.scad"
        if not base_preset.exists():
            errors.append(f"Preset missing for sweep scenario generation: {base_preset}")
            continue

        baseline_report_path = reports_dir / f"reference_fit_sweep_{preset}.json"
        baseline_hull_wrapper = generated_root / f"{preset}__baseline.scad"
        baseline_hull_stl = cache_root / "hulls" / f"{preset}__baseline.stl"

        baseline_export_record: dict[str, Any] | None = None
        if openscad_bin is not None and base_frame_stl and base_slot_plug_stl:
            write_perturbed_hull_wrapper(
                wrapper_path=baseline_hull_wrapper,
                base_preset_path=base_preset,
                hull_core_path=hull_core_path,
                overrides={},
            )
            baseline_export_record = cached_openscad_export(
                openscad_bin=openscad_bin,
                input_scad=baseline_hull_wrapper,
                output_file=baseline_hull_stl,
                cwd=project_root,
            )
            cache_records.append(baseline_export_record)

            if baseline_export_record["pass"]:
                record, report = run_reference_fit_command(
                    project_root=project_root,
                    output_json=baseline_report_path,
                    openscad_path=args.openscad_path,
                    floor_clearance_min_mm=args.floor_clearance_min_mm,
                    hull_stl=baseline_hull_stl,
                    frame_stl=base_frame_stl,
                    slot_plug_stl=base_slot_plug_stl,
                )
            else:
                record = baseline_export_record
                report = None
        else:
            record, report = run_reference_fit_command(
                project_root=project_root,
                output_json=baseline_report_path,
                openscad_path=args.openscad_path,
                floor_clearance_min_mm=args.floor_clearance_min_mm,
                preset=preset,
            )

        baseline_scenario = reference_fit_scenario_summary(
            name=f"{preset}:baseline",
            report_path=baseline_report_path,
            report=report,
            command_record=record,
        )
        if baseline_export_record is not None:
            baseline_scenario["hull_export"] = baseline_export_record
        if base_frame_stl and base_slot_plug_stl:
            baseline_scenario["cached_static_stls"] = {
                "frame_stl": str(base_frame_stl),
                "slot_plug_stl": str(base_slot_plug_stl),
            }
        scenarios.append(baseline_scenario)
        if isinstance(report, dict):
            baseline_reports_by_preset[preset] = report

        for perturb_name, overrides in perturbations:
            scenario_slug = f"{preset}__{perturb_name}"
            report_path = reports_dir / f"reference_fit_sweep_{scenario_slug}.json"
            wrapper_path = generated_root / f"{scenario_slug}.scad"
            hull_stl = cache_root / "hulls" / f"{scenario_slug}.stl"

            if openscad_bin is None or base_frame_stl is None or base_slot_plug_stl is None:
                scenarios.append(
                    {
                        "name": f"{preset}:perturb:{perturb_name}",
                        "report_path": str(report_path),
                        "command": {
                            "name": "sweep_perturbation_skipped",
                            "pass": False,
                            "reason": (
                                "Cached frame/slot-plug STL inputs unavailable; "
                                "cannot run perturbation scenario."
                            ),
                        },
                        "report_present": False,
                        "report_pass": False,
                        "gates": {},
                        "key_measurements": {},
                        "required_gate_pass": False,
                        "perturbation_overrides": overrides,
                    }
                )
                continue

            write_perturbed_hull_wrapper(
                wrapper_path=wrapper_path,
                base_preset_path=base_preset,
                hull_core_path=hull_core_path,
                overrides=overrides,
            )

            export_record = cached_openscad_export(
                openscad_bin=openscad_bin,
                input_scad=wrapper_path,
                output_file=hull_stl,
                cwd=project_root,
            )
            cache_records.append(export_record)
            if not export_record["pass"]:
                scenarios.append(
                    {
                        "name": f"{preset}:perturb:{perturb_name}",
                        "report_path": str(report_path),
                        "command": export_record,
                        "report_present": False,
                        "report_pass": False,
                        "gates": {},
                        "key_measurements": {},
                        "required_gate_pass": False,
                        "perturbation_overrides": overrides,
                    }
                )
                continue

            record, report = run_reference_fit_command(
                project_root=project_root,
                output_json=report_path,
                openscad_path=args.openscad_path,
                floor_clearance_min_mm=args.floor_clearance_min_mm,
                hull_stl=hull_stl,
                frame_stl=base_frame_stl,
                slot_plug_stl=base_slot_plug_stl,
            )
            scenario = reference_fit_scenario_summary(
                name=f"{preset}:perturb:{perturb_name}",
                report_path=report_path,
                report=report,
                command_record=record,
            )
            scenario["perturbation_overrides"] = overrides
            scenario["hull_export"] = export_record
            scenario["cached_static_stls"] = {
                "frame_stl": str(base_frame_stl),
                "slot_plug_stl": str(base_slot_plug_stl),
            }
            scenarios.append(scenario)

    overall_pass = bool(scenarios) and all(bool(item.get("required_gate_pass")) for item in scenarios) and not errors
    return {
        "scenarios": scenarios,
        "scenario_count": len(scenarios),
        "pass": overall_pass,
        "errors": errors,
        "profile": str(sweep_profile.get("name", "")),
        "cache": {
            "root": str(cache_root),
            "records": cache_records,
            "frame_stl": str(base_frame_stl) if base_frame_stl else None,
            "slot_plug_stl": str(base_slot_plug_stl) if base_slot_plug_stl else None,
        },
        "baseline_reports_by_preset": {
            preset: str(reports_dir / f"reference_fit_sweep_{preset}.json")
            for preset in baseline_reports_by_preset
        },
    }


def load_mesh(path: Path, label: str) -> trimesh.Trimesh:
    if not path.exists():
        raise FileNotFoundError(f"{label} STL not found: {path}")
    mesh = trimesh.load(path, force="mesh")
    if isinstance(mesh, trimesh.Scene):
        if not mesh.geometry:
            raise ValueError(f"{label} STL scene contains no geometry: {path}")
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"{label} STL did not resolve to mesh: {path}")
    mesh.remove_unreferenced_vertices()
    return mesh


def sampled_angles(min_deg: float, max_deg: float, step_deg: float) -> list[float]:
    if step_deg <= 0:
        return [min_deg, max_deg] if min_deg != max_deg else [min_deg]
    if max_deg < min_deg:
        min_deg, max_deg = max_deg, min_deg
    count = int(math.floor((max_deg - min_deg) / step_deg)) + 1
    values = [min_deg + step_deg * i for i in range(count)]
    if not values or values[-1] < max_deg - 1e-9:
        values.append(max_deg)
    return [round(v, 6) for v in values]


def dynamic_kinematic_validation(
    *,
    baseline_reference_report: dict[str, Any] | None,
    angle_min_deg: float,
    angle_max_deg: float,
    angle_step_deg: float,
) -> dict[str, Any]:
    if not isinstance(baseline_reference_report, dict):
        return {
            "pass": False,
            "error": "Baseline reference-fit report is unavailable; cannot run kinematic sweep.",
            "placements": [],
        }

    inputs = baseline_reference_report.get("inputs", {})
    thresholds = baseline_reference_report.get("thresholds", {})
    reference_constants = baseline_reference_report.get("reference_constants", {})
    measurements = baseline_reference_report.get("measurements", {})
    if not isinstance(inputs, dict):
        return {
            "pass": False,
            "error": "Baseline reference-fit report missing `inputs`.",
            "placements": [],
        }

    try:
        hull_mesh = load_mesh(Path(inputs["hull_stl"]), "Hull")
        frame_mesh = load_mesh(Path(inputs["frame_stl"]), "Frame")
    except (KeyError, OSError, ValueError, TypeError, FileNotFoundError) as exc:
        return {"pass": False, "error": f"Failed to load baseline meshes: {exc}", "placements": []}

    try:
        frame_spacing = float(reference_constants["REFERENCE_FRAME_SPACING"])
        seat_z_model = float(measurements["seat_z_model_mm"])
        frame_alignment_z = float(measurements["frame_alignment_z_mm"])
        penetration_tol = float(thresholds["frame_penetration_max_mm"])
        min_gap_tol = float(thresholds["frame_min_gap_mm"])
    except (KeyError, TypeError, ValueError) as exc:
        return {
            "pass": False,
            "error": f"Baseline reference-fit report missing required scalar values: {exc}",
            "placements": [],
        }

    angles = sampled_angles(angle_min_deg, angle_max_deg, angle_step_deg)
    frame_samples = np.vstack((frame_mesh.vertices, frame_mesh.triangles_center))
    placements: list[dict[str, Any]] = []
    overall_pass = True

    for x_sign in (-1, 1):
        x_offset = x_sign * frame_spacing
        neutral = frame_samples + np.array([x_offset, 0.0, frame_alignment_z], dtype=float)
        angle_results: list[dict[str, Any]] = []
        placement_pass = True

        for angle in angles:
            transform = trimesh.transformations.rotation_matrix(
                math.radians(angle),
                [0.0, 1.0, 0.0],
                [x_offset, 0.0, seat_z_model],
            )
            posed = trimesh.transform_points(neutral, transform)
            signed = signed_distance(hull_mesh, posed)
            max_penetration = max(0.0, float(np.max(signed)))
            non_penetrating = signed <= 0.0
            min_gap = float(np.min(-signed[non_penetrating])) if np.any(non_penetrating) else 0.0
            angle_pass = max_penetration <= penetration_tol and min_gap >= min_gap_tol
            if not angle_pass:
                placement_pass = False
                overall_pass = False

            angle_results.append(
                {
                    "angle_deg": float(angle),
                    "max_penetration_mm": max_penetration,
                    "min_gap_mm": min_gap,
                    "pass": angle_pass,
                }
            )

        placements.append(
            {
                "placement_x_mm": float(x_offset),
                "pivot_axis": {
                    "origin": [float(x_offset), 0.0, float(seat_z_model)],
                    "direction": [0.0, 1.0, 0.0],
                },
                "angles": angle_results,
                "pass": placement_pass,
            }
        )

    return {
        "pass": overall_pass,
        "angle_range_deg": {
            "min": float(min(angles)),
            "max": float(max(angles)),
            "step": float(angle_step_deg),
            "sample_count": int(len(angles)),
        },
        "thresholds": {
            "frame_penetration_max_mm": penetration_tol,
            "frame_min_gap_mm": min_gap_tol,
        },
        "placements": placements,
    }


ASSIGN_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s*;\s*$")
INCLUDE_RE = re.compile(r"^\s*include\s*<([^>]+)>\s*;?\s*$")


def parse_scad_value(expr: str, known: dict[str, Any]) -> Any:
    prepared = re.sub(r"\btrue\b", "True", expr, flags=re.IGNORECASE)
    prepared = re.sub(r"\bfalse\b", "False", prepared, flags=re.IGNORECASE)

    allowed_bin_ops = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
    }
    allowed_unary_ops = {
        ast.UAdd: lambda v: +v,
        ast.USub: lambda v: -v,
        ast.Not: lambda v: not v,
    }

    def walk(node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, bool)):
                return node.value
            raise ValueError("unsupported constant")
        if isinstance(node, ast.Name):
            if node.id not in known:
                raise KeyError(node.id)
            return known[node.id]
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_bin_ops:
            left = walk(node.left)
            right = walk(node.right)
            return allowed_bin_ops[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary_ops:
            return allowed_unary_ops[type(node.op)](walk(node.operand))
        raise ValueError("unsupported expression")

    parsed = ast.parse(prepared, mode="eval")
    return walk(parsed.body)


def parse_preset_parameters(entry_file: Path) -> dict[str, Any]:
    values: dict[str, Any] = {}
    visited: set[Path] = set()

    def process_file(path: Path) -> None:
        if path in visited:
            return
        visited.add(path)
        if not path.exists():
            return
        lines = path.read_text(encoding="utf-8").splitlines()
        for raw in lines:
            line = raw.split("//", 1)[0].strip()
            if not line:
                continue
            inc_match = INCLUDE_RE.match(line)
            if inc_match:
                include_path = (path.parent / inc_match.group(1)).resolve()
                process_file(include_path)
                continue
            assign_match = ASSIGN_RE.match(line)
            if not assign_match:
                continue
            key = assign_match.group(1)
            expr = assign_match.group(2)
            try:
                values[key] = parse_scad_value(expr, values)
            except Exception:
                # Non-literal expressions are ignored for this lightweight parser.
                continue

    process_file(entry_file.resolve())
    return values


def convex_hull_2d(points: np.ndarray) -> np.ndarray:
    if len(points) <= 1:
        return points

    pts = sorted({(float(p[0]), float(p[1])) for p in points})
    if len(pts) <= 1:
        return np.array(pts, dtype=float)

    def cross(o: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list[tuple[float, float]] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper: list[tuple[float, float]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    hull = lower[:-1] + upper[:-1]
    return np.array(hull, dtype=float)


def polygon_area(points: np.ndarray) -> float:
    if len(points) < 3:
        return 0.0
    x = points[:, 0]
    y = points[:, 1]
    return 0.5 * float(abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def sample_local_thickness_probes(
    *,
    mesh: trimesh.Trimesh,
    probe_count: int,
    probe_min_valid: int,
    percentile: float,
    noise_floor_mm: float,
) -> dict[str, Any]:
    triangle_centers = np.asarray(mesh.triangles_center, dtype=float)
    face_normals = np.asarray(mesh.face_normals, dtype=float)
    total_faces = int(len(triangle_centers))
    if total_faces == 0:
        return {
            "status": "no_faces",
            "error": "Mesh has no faces for thickness probing.",
            "probe_count": 0,
            "valid_probe_count": 0,
            "noise_floor_mm": max(0.0, float(noise_floor_mm)),
        }

    target_count = max(1, int(probe_count))
    order = np.lexsort((triangle_centers[:, 2], triangle_centers[:, 1], triangle_centers[:, 0]))
    if total_faces <= target_count:
        sample_index = order
    else:
        sample_positions = np.linspace(0, total_faces - 1, num=target_count, dtype=int)
        sample_index = order[sample_positions]

    probe_points = triangle_centers[sample_index]
    probe_normals = face_normals[sample_index]
    requested_percentile = float(percentile)
    percentile_clamped = min(100.0, max(0.0, requested_percentile))
    noise_floor = max(0.0, float(noise_floor_mm))
    min_required = max(1, int(probe_min_valid))

    thickness_fn = getattr(trimesh.proximity, "thickness", None)
    if not callable(thickness_fn):
        return {
            "status": "unavailable",
            "error": "trimesh.proximity.thickness is unavailable in current trimesh build.",
            "probe_count": int(len(probe_points)),
            "valid_probe_count": 0,
            "probe_min_valid": min_required,
            "requested_percentile": requested_percentile,
            "percentile_used": percentile_clamped,
            "noise_floor_mm": noise_floor,
        }

    attempts: list[dict[str, Any]] = []
    best_values: np.ndarray | None = None
    best_method: str | None = None
    for method in ("ray", "max_sphere"):
        try:
            raw_values = np.asarray(
                thickness_fn(mesh, probe_points, normals=probe_normals, method=method),
                dtype=float,
            ).reshape(-1)
        except Exception as exc:
            attempts.append({"method": method, "error": str(exc), "valid_probe_count": 0})
            continue
        finite_values = raw_values[np.isfinite(raw_values)]
        valid_values = finite_values[finite_values > max(1e-6, noise_floor)]
        attempts.append(
            {
                "method": method,
                "error": None,
                "valid_probe_count": int(len(valid_values)),
            }
        )
        if best_values is None or len(valid_values) > len(best_values):
            best_values = valid_values
            best_method = method
        if len(valid_values) >= min_required:
            break

    if best_values is None or len(best_values) == 0:
        return {
            "status": "probe_failed",
            "error": "No finite positive thickness values produced by trimesh probes.",
            "probe_count": int(len(probe_points)),
            "valid_probe_count": 0,
            "probe_min_valid": min_required,
            "requested_percentile": requested_percentile,
            "percentile_used": percentile_clamped,
            "noise_floor_mm": noise_floor,
            "method_attempts": attempts,
        }

    robust_value = float(np.percentile(best_values, percentile_clamped))
    summary = {
        "status": "ok" if len(best_values) >= min_required else "insufficient_valid_probes",
        "probe_count": int(len(probe_points)),
        "valid_probe_count": int(len(best_values)),
        "probe_min_valid": min_required,
        "requested_percentile": requested_percentile,
        "percentile_used": percentile_clamped,
        "noise_floor_mm": noise_floor,
        "method_used": best_method,
        "minimum_mm": float(np.min(best_values)),
        "percentile_mm": robust_value,
        "median_mm": float(np.percentile(best_values, 50.0)),
        "maximum_mm": float(np.max(best_values)),
        "method_attempts": attempts,
    }
    if summary["status"] != "ok":
        summary["error"] = "Valid probe count below required minimum."
    return summary


def manufacturability_validation(
    *,
    args: argparse.Namespace,
    project_root: Path,
    baseline_reference_report: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(baseline_reference_report, dict):
        return {
            "pass": False,
            "error": "Baseline reference-fit report is unavailable; cannot evaluate manufacturability.",
            "gates": {},
            "measurements": {},
        }

    inputs = baseline_reference_report.get("inputs", {})
    if not isinstance(inputs, dict):
        return {
            "pass": False,
            "error": "Baseline reference-fit report missing `inputs`.",
            "gates": {},
            "measurements": {},
        }

    preset = inputs.get("preset", "gcsc_default")
    preset_path = project_root / "codex_hull_lab" / "presets" / f"{preset}.scad"
    if not preset_path.exists():
        return {
            "pass": False,
            "error": f"Preset file not found for manufacturability check: {preset_path}",
            "gates": {},
            "measurements": {},
        }

    hull_path_raw = inputs.get("hull_stl")
    if not isinstance(hull_path_raw, str):
        return {
            "pass": False,
            "error": "Baseline reference-fit report missing `inputs.hull_stl`.",
            "gates": {},
            "measurements": {},
        }

    try:
        hull_mesh = load_mesh(Path(hull_path_raw), "Hull")
    except Exception as exc:
        return {
            "pass": False,
            "error": f"Failed to load hull mesh for manufacturability check: {exc}",
            "gates": {},
            "measurements": {},
        }

    params = parse_preset_parameters(preset_path)

    def get_float(name: str, fallback: float | None = None) -> float | None:
        value = params.get(name, fallback)
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return fallback

    def get_bool(name: str, fallback: bool = False) -> bool:
        value = params.get(name, fallback)
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(fallback)

    wall_mm = get_float("wall_mm", 0.0) or 0.0
    wall_end_ratio = get_float("wall_end_taper_ratio", 1.0) or 1.0
    floor_mm = get_float("floor_mm", 0.0) or 0.0
    slot_outer_skin_min_mm = get_float("slot_outer_skin_min_mm", 0.0) or 0.0
    slot_skin_mm = get_float("slot_skin_mm", 0.0) or 0.0
    feet_on = get_bool("feet_on", True)
    foot_recess_depth_mm = get_float("foot_recess_depth_mm", 0.0) or 0.0
    foot_recess_skin_mm = get_float("foot_recess_skin_mm", 0.0) or 0.0

    estimated_end_wall_mm = wall_mm * wall_end_ratio
    estimated_recess_skin_mm = floor_mm - foot_recess_depth_mm if feet_on else floor_mm

    wall_candidates = {
        "estimated_end_wall_mm": estimated_end_wall_mm,
        "slot_outer_skin_min_mm": slot_outer_skin_min_mm,
        "slot_skin_mm": slot_skin_mm,
    }
    min_wall_thickness_mm = float(min(wall_candidates.values())) if wall_candidates else 0.0
    local_thickness_probes = sample_local_thickness_probes(
        mesh=hull_mesh,
        probe_count=args.wall_thickness_probe_count,
        probe_min_valid=args.wall_thickness_probe_min_valid,
        percentile=args.wall_thickness_probe_percentile,
        noise_floor_mm=args.wall_thickness_probe_noise_floor_mm,
    )
    local_thickness_percentile_mm = local_thickness_probes.get("percentile_mm")
    sampled_local_wall_gate = (
        local_thickness_probes.get("status") == "ok"
        and isinstance(local_thickness_percentile_mm, (int, float))
        and float(local_thickness_percentile_mm) >= args.min_wall_thickness_mm
    )

    normals = hull_mesh.face_normals
    face_areas = hull_mesh.area_faces
    downward_mask = normals[:, 2] < -1e-6
    overhang_cos = math.cos(math.radians(args.max_overhang_from_horizontal_deg))
    risky_mask = downward_mask & (np.abs(normals[:, 2]) >= overhang_cos)
    downward_area = float(np.sum(face_areas[downward_mask])) if len(face_areas) else 0.0
    risky_area = float(np.sum(face_areas[risky_mask])) if len(face_areas) else 0.0
    risky_ratio = float(risky_area / downward_area) if downward_area > 1e-9 else 0.0

    z_min = float(np.min(hull_mesh.vertices[:, 2]))
    contact_points = hull_mesh.vertices[hull_mesh.vertices[:, 2] <= z_min + args.contact_z_tolerance_mm][:, :2]
    contact_hull = convex_hull_2d(contact_points) if len(contact_points) >= 3 else np.empty((0, 2))
    contact_area = polygon_area(contact_hull)
    contact_span_x = (
        float(np.max(contact_points[:, 0]) - np.min(contact_points[:, 0]))
        if len(contact_points)
        else 0.0
    )
    contact_span_y = (
        float(np.max(contact_points[:, 1]) - np.min(contact_points[:, 1]))
        if len(contact_points)
        else 0.0
    )

    gates = {
        "minimum_wall_thickness": min_wall_thickness_mm >= args.min_wall_thickness_mm,
        "sampled_local_wall_thickness": bool(sampled_local_wall_gate),
        "recess_skin_thickness": (
            estimated_recess_skin_mm >= args.min_recess_skin_mm
            and estimated_recess_skin_mm >= foot_recess_skin_mm
        ),
        "overhang_risk": risky_ratio <= args.max_risky_overhang_ratio,
        "stable_contact_footprint": (
            contact_area >= args.min_contact_area_mm2
            and contact_span_x >= args.min_contact_span_x_mm
            and contact_span_y >= args.min_contact_span_y_mm
        ),
    }

    measurements = {
        "preset": preset,
        "wall_candidates_mm": wall_candidates,
        "min_wall_thickness_mm": min_wall_thickness_mm,
        "sampled_local_thickness_probes": local_thickness_probes,
        "floor_mm": floor_mm,
        "foot_recess_depth_mm": foot_recess_depth_mm if feet_on else 0.0,
        "foot_recess_skin_declared_mm": foot_recess_skin_mm,
        "foot_recess_skin_estimated_mm": estimated_recess_skin_mm,
        "downward_area_mm2": downward_area,
        "risky_overhang_area_mm2": risky_area,
        "risky_overhang_ratio": risky_ratio,
        "contact_area_mm2": contact_area,
        "contact_span_x_mm": contact_span_x,
        "contact_span_y_mm": contact_span_y,
        "contact_point_count": int(len(contact_points)),
    }

    return {
        "pass": all(gates.values()),
        "gates": gates,
        "thresholds": {
            "min_wall_thickness_mm": args.min_wall_thickness_mm,
            "wall_thickness_probe_count": args.wall_thickness_probe_count,
            "wall_thickness_probe_min_valid": args.wall_thickness_probe_min_valid,
            "wall_thickness_probe_percentile": args.wall_thickness_probe_percentile,
            "wall_thickness_probe_noise_floor_mm": args.wall_thickness_probe_noise_floor_mm,
            "min_recess_skin_mm": args.min_recess_skin_mm,
            "max_risky_overhang_ratio": args.max_risky_overhang_ratio,
            "max_overhang_from_horizontal_deg": args.max_overhang_from_horizontal_deg,
            "min_contact_area_mm2": args.min_contact_area_mm2,
            "min_contact_span_x_mm": args.min_contact_span_x_mm,
            "min_contact_span_y_mm": args.min_contact_span_y_mm,
        },
        "measurements": measurements,
    }


def geometry_signature(mesh: trimesh.Trimesh) -> dict[str, float]:
    extents = mesh.extents
    return {
        "extent_x_mm": float(extents[0]),
        "extent_y_mm": float(extents[1]),
        "extent_z_mm": float(extents[2]),
        "volume_mm3": float(abs(mesh.volume)),
        "surface_area_mm2": float(mesh.area),
    }


def write_signature_baseline(
    *,
    file_path: Path,
    observed: dict[str, dict[str, float]],
    relative_band: float,
    absolute_band_mm: float,
) -> None:
    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "updated_utc": now_utc(),
        "description": "Approved codex_hull_lab geometry signatures. Intentional drifts require explicit override.",
        "presets": {},
    }
    for preset, metrics in observed.items():
        preset_metrics: dict[str, Any] = {}
        for name, value in metrics.items():
            if name in {"volume_mm3", "surface_area_mm2"}:
                margin = max(abs(value) * max(relative_band, 0.0), 0.1)
            else:
                margin = max(abs(absolute_band_mm), 0.05)
            preset_metrics[name] = {
                "min": float(value - margin),
                "max": float(value + margin),
            }
        payload["presets"][preset] = {"metrics": preset_metrics}
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def golden_signature_validation(
    *,
    args: argparse.Namespace,
    project_root: Path,
    sweep_result: dict[str, Any],
    sweep_presets: list[str],
) -> dict[str, Any]:
    observed_by_preset: dict[str, dict[str, float]] = {}

    scenario_by_name: dict[str, dict[str, Any]] = {}
    for scenario in sweep_result.get("scenarios", []):
        if not isinstance(scenario, dict):
            continue
        scenario_by_name[str(scenario.get("name", ""))] = scenario

    for preset in sweep_presets:
        key = f"{preset}:baseline"
        scenario = scenario_by_name.get(key)
        if not scenario:
            continue
        report_path = Path(str(scenario.get("report_path", "")))
        report = load_json(report_path)
        if not isinstance(report, dict):
            continue
        inputs = report.get("inputs", {})
        if not isinstance(inputs, dict):
            continue
        hull_path = inputs.get("hull_stl")
        if not isinstance(hull_path, str):
            continue
        try:
            mesh = load_mesh(Path(hull_path), f"Hull({preset})")
        except Exception:
            continue
        observed_by_preset[preset] = geometry_signature(mesh)

    signature_file = args.signature_file.resolve()
    override = resolve_signature_drift_override(args)
    allow_drift = bool(override["enabled"])

    if args.write_signature_baseline:
        write_signature_baseline(
            file_path=signature_file,
            observed=observed_by_preset,
            relative_band=args.signature_relative_band,
            absolute_band_mm=args.signature_absolute_band_mm,
        )

    expected = load_json(signature_file)
    if not isinstance(expected, dict):
        return {
            "pass": False,
            "raw_pass": False,
            "allow_drift_override": allow_drift,
            "override_source": str(override["source"]),
            "signature_file": str(signature_file),
            "error": "Golden signature file missing or invalid JSON.",
            "observed": observed_by_preset,
            "drifts": [],
            "drifted_metrics_by_preset": {},
            "missing_presets": list(sweep_presets),
            "policy": {
                "id": "signature_drift_blocking",
                "default_action": "fail_on_missing_or_drift",
                "override_flag": "--allow-signature-drift",
                "override_env": "GCSC_ALLOW_SIGNATURE_DRIFT",
                "override_enabled": allow_drift,
                "override_source": str(override["source"]),
                "drift_detected": False,
                "missing_presets_detected": bool(sweep_presets),
                "blocked_without_override": True,
            },
        }

    expected_presets = expected.get("presets", {})
    if not isinstance(expected_presets, dict):
        expected_presets = {}

    missing_presets: list[str] = []
    drifts: list[dict[str, Any]] = []

    for preset in sweep_presets:
        observed = observed_by_preset.get(preset)
        expected_entry = expected_presets.get(preset)
        if not observed or not isinstance(expected_entry, dict):
            missing_presets.append(preset)
            continue
        metrics = expected_entry.get("metrics", {})
        if not isinstance(metrics, dict):
            missing_presets.append(preset)
            continue
        for metric_name, bounds in metrics.items():
            if metric_name not in observed or not isinstance(bounds, dict):
                drifts.append(
                    {
                        "preset": preset,
                        "metric": metric_name,
                        "status": "missing_metric",
                    }
                )
                continue
            try:
                lower = float(bounds["min"])
                upper = float(bounds["max"])
                value = float(observed[metric_name])
            except (KeyError, TypeError, ValueError):
                drifts.append(
                    {
                        "preset": preset,
                        "metric": metric_name,
                        "status": "invalid_bounds",
                    }
                )
                continue
            if value < lower or value > upper:
                drifts.append(
                    {
                        "preset": preset,
                        "metric": metric_name,
                        "observed": value,
                        "min": lower,
                        "max": upper,
                        "delta_to_nearest_band_edge": (
                            value - lower if value < lower else value - upper
                        ),
                        "status": "out_of_band",
                    }
                )

    raw_pass = not missing_presets and not drifts
    pass_with_override = raw_pass or allow_drift
    drifted_metrics_by_preset: dict[str, list[str]] = {}
    for drift in drifts:
        if not isinstance(drift, dict):
            continue
        preset = drift.get("preset")
        metric = drift.get("metric")
        if not isinstance(preset, str) or not isinstance(metric, str):
            continue
        drifted_metrics_by_preset.setdefault(preset, [])
        if metric not in drifted_metrics_by_preset[preset]:
            drifted_metrics_by_preset[preset].append(metric)
    for preset in list(drifted_metrics_by_preset.keys()):
        drifted_metrics_by_preset[preset].sort()
    return {
        "pass": pass_with_override,
        "raw_pass": raw_pass,
        "allow_drift_override": allow_drift,
        "override_source": str(override["source"]),
        "override_used": bool(allow_drift and not raw_pass),
        "signature_file": str(signature_file),
        "observed": observed_by_preset,
        "drifts": drifts,
        "drifted_metrics_by_preset": drifted_metrics_by_preset,
        "missing_presets": missing_presets,
        "policy": {
            "id": "signature_drift_blocking",
            "default_action": "fail_on_missing_or_drift",
            "override_flag": "--allow-signature-drift",
            "override_env": "GCSC_ALLOW_SIGNATURE_DRIFT",
            "override_enabled": allow_drift,
            "override_source": str(override["source"]),
            "drift_detected": bool(drifts),
            "missing_presets_detected": bool(missing_presets),
            "blocked_without_override": bool(not raw_pass and not allow_drift),
        },
    }


def build_command_suite(
    *,
    project_root: Path,
    reports_dir: Path,
    openscad_path: str | None,
    floor_clearance_min_mm: float,
    baseline_preset: str,
    quick_mode: bool,
) -> list[CommandSpec]:
    verify_ref = project_root / "codex_hull_lab" / "tools" / "verify_reference_fit.py"
    verify_shape = project_root / "codex_hull_lab" / "tools" / "verify_shape_sensitivity.py"
    test_ref = project_root / "tests" / "test_reference_fit.py"
    test_shape = project_root / "tests" / "test_shape_sensitivity.py"
    test_hook = project_root / "tests" / "test_functional_requirements_hook.py"

    ref_report = reports_dir / "reference_fit_report.json"
    shape_report = reports_dir / "shape_sensitivity_report.json"

    ref_argv = [
        sys.executable,
        str(verify_ref),
        "--project-root",
        str(project_root),
        "--preset",
        str(baseline_preset),
        "--output-json",
        str(ref_report),
        "--floor-clearance-min-mm",
        str(floor_clearance_min_mm),
        "--reuse-exported-stls",
    ]
    shape_argv = [
        sys.executable,
        str(verify_shape),
        "--project-root",
        str(project_root),
        "--output-json",
        str(shape_report),
    ]
    if openscad_path:
        ref_argv.extend(["--openscad-path", openscad_path])
        shape_argv.extend(["--openscad-path", openscad_path])

    command_specs = [
        CommandSpec("verify_reference_fit", ref_argv, timeout_s=2400),
        CommandSpec("verify_shape_sensitivity", shape_argv, timeout_s=1800),
    ]
    if not quick_mode:
        command_specs.extend(
            [
                CommandSpec("test_reference_fit", [sys.executable, str(test_ref)], timeout_s=3600),
                CommandSpec("test_shape_sensitivity", [sys.executable, str(test_shape)], timeout_s=3000),
                CommandSpec("test_functional_requirements_hook", [sys.executable, str(test_hook)], timeout_s=300),
            ]
        )
    return command_specs


def print_summary(report: dict[str, Any]) -> None:
    gates = report.get("gates", {})
    signature = report.get("golden_geometry_signatures", {})
    print("=== Full Validation ===")
    print(f"Command suite:            {gates.get('command_suite')}")
    print(f"Robustness sweep:         {gates.get('robustness_sweep')}")
    print(f"Kinematic swing path:     {gates.get('kinematic_swing_path')}")
    print(f"Manufacturability:        {gates.get('manufacturability')}")
    print(f"Golden signatures:        {gates.get('golden_geometry_signatures')}")
    if isinstance(signature, dict):
        missing = signature.get("missing_presets", [])
        drifts = signature.get("drifts", [])
        if isinstance(missing, list) and missing:
            print(f"Signature missing presets: {', '.join(str(item) for item in missing)}")
        if isinstance(drifts, list) and drifts:
            print("Signature drifts:")
            for drift in drifts[:12]:
                if not isinstance(drift, dict):
                    continue
                preset = drift.get("preset", "?")
                metric = drift.get("metric", "?")
                status = drift.get("status", "unknown")
                if status == "out_of_band":
                    observed = drift.get("observed")
                    lower = drift.get("min")
                    upper = drift.get("max")
                    print(
                        f"  - {preset}.{metric}: observed={observed} expected=[{lower}, {upper}]"
                    )
                else:
                    print(f"  - {preset}.{metric}: {status}")
            if len(drifts) > 12:
                print(f"  ... {len(drifts) - 12} additional drift entries omitted.")
        policy = signature.get("policy", {})
        if isinstance(policy, dict):
            print(
                "Signature drift policy: "
                f"default={policy.get('default_action')} "
                f"override={policy.get('override_enabled')} "
                f"source={policy.get('override_source')}"
            )
    print(f"OVERALL: {'PASS' if report.get('pass') else 'FAIL'}")
    print(f"Report written: {report.get('output_json')}")


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    reports_dir = (project_root / "_codex" / "reports").resolve()
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_json = args.output_json.resolve()
    output_json.parent.mkdir(parents=True, exist_ok=True)

    try:
        sweep_profile = resolve_sweep_profile(args=args, project_root=project_root)
    except ValueError as exc:
        print(f"Sweep profile error: {exc}", file=sys.stderr)
        return 2
    sweep_presets = [str(name) for name in sweep_profile["presets"]]
    if not sweep_presets:
        print("Sweep profile has no presets after resolution.", file=sys.stderr)
        return 2
    baseline_preset = sweep_presets[0]

    openscad_bin: str | None = None
    openscad_error: str | None = None
    try:
        openscad_bin = resolve_openscad(args.openscad_path)
    except FileNotFoundError as exc:
        openscad_error = str(exc)

    command_specs = build_command_suite(
        project_root=project_root,
        reports_dir=reports_dir,
        openscad_path=args.openscad_path,
        floor_clearance_min_mm=args.floor_clearance_min_mm,
        baseline_preset=baseline_preset,
        quick_mode=bool(args.quick),
    )
    command_results: list[dict[str, Any]] = []

    fail_fast = not args.no_subcommand_fail_fast
    for spec in command_specs:
        result = run_command(spec, cwd=project_root)
        command_results.append(result)
        if fail_fast and not result["pass"]:
            break

    reference_fit_report_path = reports_dir / "reference_fit_report.json"
    shape_sensitivity_report_path = reports_dir / "shape_sensitivity_report.json"
    baseline_reference_report = load_json(reference_fit_report_path)
    baseline_shape_report = load_json(shape_sensitivity_report_path)

    sweep_result = robustness_sweep(
        args=args,
        project_root=project_root,
        reports_dir=reports_dir,
        openscad_bin=openscad_bin,
        baseline_reference_report=baseline_reference_report,
        sweep_profile=sweep_profile,
    )
    kinematic_result = dynamic_kinematic_validation(
        baseline_reference_report=baseline_reference_report,
        angle_min_deg=args.kinematic_angle_min_deg,
        angle_max_deg=args.kinematic_angle_max_deg,
        angle_step_deg=args.kinematic_angle_step_deg,
    )
    manufacturability_result = manufacturability_validation(
        args=args,
        project_root=project_root,
        baseline_reference_report=baseline_reference_report,
    )
    signature_result = golden_signature_validation(
        args=args,
        project_root=project_root,
        sweep_result=sweep_result,
        sweep_presets=sweep_presets,
    )

    command_suite_pass = (
        len(command_results) == len(command_specs)
        and all(item.get("pass") for item in command_results)
    )
    gates = {
        "command_suite": bool(command_suite_pass),
        "robustness_sweep": bool(sweep_result.get("pass")),
        "kinematic_swing_path": bool(kinematic_result.get("pass")),
        "manufacturability": bool(manufacturability_result.get("pass")),
        "golden_geometry_signatures": bool(signature_result.get("pass")),
    }

    report = {
        "timestamp_utc": now_utc(),
        "output_json": str(output_json),
        "inputs": {
            "project_root": str(project_root),
            "quick_mode": bool(args.quick),
            "sweep_profile": str(sweep_profile.get("name", "")),
            "sweep_config": str(Path(str(sweep_profile.get("source_file", args.sweep_config))).resolve()),
            "openscad_path": openscad_bin,
            "openscad_resolution_error": openscad_error,
            "floor_clearance_min_mm": args.floor_clearance_min_mm,
            "sweep_presets": sweep_presets,
            "sweep_perturbations": [
                {"name": name, "overrides": overrides}
                for name, overrides in sweep_profile.get("perturbations", [])
            ],
            "signature_file": str(args.signature_file.resolve()),
            "allow_signature_drift": bool(signature_result.get("allow_drift_override")),
            "signature_drift_override_source": str(signature_result.get("override_source", "none")),
            "write_signature_baseline": bool(args.write_signature_baseline),
        },
        "required_command_suite": [spec.name for spec in command_specs],
        "command_results": command_results,
        "baseline_reports": {
            "reference_fit_report": str(reference_fit_report_path),
            "shape_sensitivity_report": str(shape_sensitivity_report_path),
            "reference_fit_loaded": isinstance(baseline_reference_report, dict),
            "shape_sensitivity_loaded": isinstance(baseline_shape_report, dict),
        },
        "robustness_sweep": sweep_result,
        "dynamic_kinematic_validation": kinematic_result,
        "manufacturability_validation": manufacturability_result,
        "golden_geometry_signatures": signature_result,
        "gates": gates,
        "pass": all(gates.values()),
    }

    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print_summary(report)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
