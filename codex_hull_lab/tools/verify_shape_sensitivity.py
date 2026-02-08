#!/usr/bin/env python3
"""Deterministic shape-sensitivity verification for profile controls."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


METRIC_KEYS = (
    "bow_tip_half_beam_mm",
    "stern_tip_half_beam_mm",
    "bow_tip_top_half_beam_mm",
    "stern_tip_top_half_beam_mm",
    "bow_taper_response_mm",
    "stern_taper_response_mm",
)

METRIC_PATTERN = re.compile(
    r"GCSC_SENSITIVITY_METRIC\|([a-zA-Z0-9_]+)\|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)"
)


@dataclass
class SensitivityThresholds:
    inset_mm: float = 16.0
    bow_delta_min_mm: float = 0.35
    stern_delta_min_mm: float = 0.35
    gunwale_delta_min_mm: float = 0.20


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    default_output = project_root / "_codex" / "reports" / "shape_sensitivity_report.json"
    default_tmp_dir = project_root / "_codex" / "reports" / "shape_sensitivity_tmp"

    parser = argparse.ArgumentParser(
        description="Verify that key profile parameters produce measurable geometry deltas."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=project_root,
        help="Repository root. Defaults to auto-detected root.",
    )
    parser.add_argument(
        "--preset",
        default="gcsc_default",
        help="Preset used as baseline for sensitivity checks (default: gcsc_default).",
    )
    parser.add_argument(
        "--openscad-path",
        default=None,
        help="Path to OpenSCAD binary. Falls back to OPENSCAD_PATH, system PATH, then Windows default.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=default_output,
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--tmp-dir",
        type=Path,
        default=default_tmp_dir,
        help="Temporary directory for generated sensitivity wrappers.",
    )
    parser.add_argument("--inset-mm", type=float, default=SensitivityThresholds.inset_mm)
    parser.add_argument(
        "--bow-delta-min-mm",
        type=float,
        default=SensitivityThresholds.bow_delta_min_mm,
    )
    parser.add_argument(
        "--stern-delta-min-mm",
        type=float,
        default=SensitivityThresholds.stern_delta_min_mm,
    )
    parser.add_argument(
        "--gunwale-delta-min-mm",
        type=float,
        default=SensitivityThresholds.gunwale_delta_min_mm,
    )
    parser.add_argument(
        "--bow-curvature-test-value",
        type=float,
        default=0.82,
        help="Probe value for curvature_bow in bow sensitivity check.",
    )
    parser.add_argument(
        "--stern-curvature-test-value",
        type=float,
        default=0.0,
        help="Probe value for curvature_stern in stern sensitivity check.",
    )
    parser.add_argument(
        "--gunwale-tip-merge-ratio-test-value",
        type=float,
        default=0.58,
        help="Probe value for gunwale_tip_merge_ratio in gunwale sensitivity check.",
    )
    return parser.parse_args()


def build_thresholds(args: argparse.Namespace) -> SensitivityThresholds:
    return SensitivityThresholds(
        inset_mm=max(1.0, args.inset_mm),
        bow_delta_min_mm=max(0.001, args.bow_delta_min_mm),
        stern_delta_min_mm=max(0.001, args.stern_delta_min_mm),
        gunwale_delta_min_mm=max(0.001, args.gunwale_delta_min_mm),
    )


def resolve_openscad(openscad_path: str | None) -> str:
    candidates: list[str] = []
    if openscad_path:
        candidates.append(openscad_path)
    env_path = os.environ.get("OPENSCAD_PATH")
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
            return str(resolved)

    raise FileNotFoundError(
        "OpenSCAD binary not found. Set OPENSCAD_PATH or pass --openscad-path."
    )


def relative_include(wrapper_dir: Path, target: Path) -> str:
    try:
        return os.path.relpath(target, start=wrapper_dir).replace("\\", "/")
    except ValueError:
        return target.resolve().as_posix()


def format_assignment(name: str, value: float) -> str:
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    return f"{name} = {text};"


def write_metric_wrapper(
    wrapper_path: Path,
    preset_file: Path,
    profile_file: Path,
    inset_mm: float,
    overrides: dict[str, float],
) -> None:
    inset_text = f"{inset_mm:.8f}".rstrip("0").rstrip(".")
    lines = [f"include <{relative_include(wrapper_path.parent, preset_file)}>"]
    for name, value in sorted(overrides.items()):
        lines.append(format_assignment(name, value))
    lines.append(f"include <{relative_include(wrapper_path.parent, profile_file)}>")
    lines.append("")
    for metric in METRIC_KEYS:
        fn = metric.replace("_mm", "")
        lines.append(
            f'echo(str("GCSC_SENSITIVITY_METRIC|{metric}|", gcsc_{fn}_mm({inset_text})));'
        )
    lines.append("cube([0.1, 0.1, 0.1], center = true);")
    lines.append("")
    wrapper_path.write_text("\n".join(lines), encoding="utf-8")


def run_metric_probe(
    openscad_bin: str,
    project_root: Path,
    wrapper_path: Path,
    output_path: Path,
) -> dict[str, float]:
    result = subprocess.run(
        [openscad_bin, "-o", str(output_path), str(wrapper_path)],
        capture_output=True,
        text=True,
        cwd=str(project_root),
        timeout=300,
    )
    combined = "\n".join([result.stdout, result.stderr])
    metrics: dict[str, float] = {}
    for match in METRIC_PATTERN.finditer(combined):
        metrics[match.group(1)] = float(match.group(2))

    missing = [name for name in METRIC_KEYS if name not in metrics]
    if result.returncode != 0 or missing:
        raise RuntimeError(
            "\n".join(
                [
                    f"OpenSCAD sensitivity probe failed for {wrapper_path.name}",
                    f"Return code: {result.returncode}",
                    f"Missing metrics: {missing}",
                    f"STDOUT:\n{result.stdout}",
                    f"STDERR:\n{result.stderr}",
                ]
            )
        )
    return metrics


def probe_variant(
    variant_name: str,
    openscad_bin: str,
    project_root: Path,
    tmp_dir: Path,
    preset_file: Path,
    profile_file: Path,
    inset_mm: float,
    overrides: dict[str, float],
) -> dict[str, float]:
    wrapper = tmp_dir / f"{variant_name}.scad"
    output = tmp_dir / f"{variant_name}.csg"
    write_metric_wrapper(
        wrapper_path=wrapper,
        preset_file=preset_file,
        profile_file=profile_file,
        inset_mm=inset_mm,
        overrides=overrides,
    )
    return run_metric_probe(
        openscad_bin=openscad_bin,
        project_root=project_root,
        wrapper_path=wrapper,
        output_path=output,
    )


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    thresholds = build_thresholds(args)
    openscad_bin = resolve_openscad(args.openscad_path)
    preset_file = project_root / "codex_hull_lab" / "presets" / f"{args.preset}.scad"
    profile_file = project_root / "codex_hull_lab" / "src" / "gcsc_hull_profiles.scad"

    missing = [p for p in (preset_file, profile_file) if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required input files: " + ", ".join(str(p) for p in missing)
        )

    tmp_dir = args.tmp_dir.resolve()
    tmp_dir.mkdir(parents=True, exist_ok=True)

    baseline = probe_variant(
        variant_name="baseline",
        openscad_bin=openscad_bin,
        project_root=project_root,
        tmp_dir=tmp_dir,
        preset_file=preset_file,
        profile_file=profile_file,
        inset_mm=thresholds.inset_mm,
        overrides={},
    )
    bow_variant = probe_variant(
        variant_name="bow_probe",
        openscad_bin=openscad_bin,
        project_root=project_root,
        tmp_dir=tmp_dir,
        preset_file=preset_file,
        profile_file=profile_file,
        inset_mm=thresholds.inset_mm,
        overrides={"curvature_bow": args.bow_curvature_test_value},
    )
    stern_variant = probe_variant(
        variant_name="stern_probe",
        openscad_bin=openscad_bin,
        project_root=project_root,
        tmp_dir=tmp_dir,
        preset_file=preset_file,
        profile_file=profile_file,
        inset_mm=thresholds.inset_mm,
        overrides={"curvature_stern": args.stern_curvature_test_value},
    )
    gunwale_variant = probe_variant(
        variant_name="gunwale_probe",
        openscad_bin=openscad_bin,
        project_root=project_root,
        tmp_dir=tmp_dir,
        preset_file=preset_file,
        profile_file=profile_file,
        inset_mm=thresholds.inset_mm,
        overrides={"gunwale_tip_merge_ratio": args.gunwale_tip_merge_ratio_test_value},
    )

    bow_delta = abs(
        bow_variant["bow_tip_half_beam_mm"] - baseline["bow_tip_half_beam_mm"]
    )
    stern_delta = abs(
        stern_variant["stern_tip_half_beam_mm"] - baseline["stern_tip_half_beam_mm"]
    )
    gunwale_bow_delta = abs(
        gunwale_variant["bow_tip_top_half_beam_mm"] - baseline["bow_tip_top_half_beam_mm"]
    )
    gunwale_stern_delta = abs(
        gunwale_variant["stern_tip_top_half_beam_mm"]
        - baseline["stern_tip_top_half_beam_mm"]
    )
    gunwale_min_delta = min(gunwale_bow_delta, gunwale_stern_delta)

    gates = {
        "bow_curvature_response": bow_delta >= thresholds.bow_delta_min_mm,
        "stern_curvature_response": stern_delta >= thresholds.stern_delta_min_mm,
        "gunwale_tip_merge_response": gunwale_min_delta
        >= thresholds.gunwale_delta_min_mm,
    }
    overall_pass = all(gates.values())

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "project_root": str(project_root),
            "preset": args.preset,
            "preset_file": str(preset_file),
            "profile_file": str(profile_file),
            "openscad_path": openscad_bin,
        },
        "thresholds": asdict(thresholds),
        "probes": {
            "bow_curvature_test_value": args.bow_curvature_test_value,
            "stern_curvature_test_value": args.stern_curvature_test_value,
            "gunwale_tip_merge_ratio_test_value": args.gunwale_tip_merge_ratio_test_value,
        },
        "measurements": {
            "baseline": baseline,
            "bow_variant": bow_variant,
            "stern_variant": stern_variant,
            "gunwale_variant": gunwale_variant,
            "deltas": {
                "bow_tip_half_beam_mm": bow_delta,
                "stern_tip_half_beam_mm": stern_delta,
                "gunwale_bow_tip_top_half_beam_mm": gunwale_bow_delta,
                "gunwale_stern_tip_top_half_beam_mm": gunwale_stern_delta,
                "gunwale_min_tip_top_half_beam_mm": gunwale_min_delta,
            },
        },
        "gates": gates,
        "pass": overall_pass,
    }

    output_path = args.output_json.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== Shape Sensitivity Verification ===")
    print(f"Preset: {args.preset}")
    print(f"Bow tip half-beam delta (mm): {bow_delta:.6f}")
    print(f"Stern tip half-beam delta (mm): {stern_delta:.6f}")
    print(f"Gunwale min top-half-beam delta (mm): {gunwale_min_delta:.6f}")
    print(f"Report: {output_path}")
    print(f"PASS: {overall_pass}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
