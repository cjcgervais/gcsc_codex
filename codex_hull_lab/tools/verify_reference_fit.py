#!/usr/bin/env python3
"""Deterministic mechanical verification for GCSC hull/frame reference fit."""

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
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from trimesh.proximity import signed_distance


CANONICAL_REFERENCE_CONSTANTS = {
    "REFERENCE_PIVOT_Y": 33.0,
    "REFERENCE_PIVOT_Z": 38.0,
    "REFERENCE_SLOT_DIAMETER": 7.5,
    "REFERENCE_BALL_DIAMETER": 7.25,
    "REFERENCE_SLOT_ENTRY_Z": 45.0,
    "REFERENCE_FRAME_SPACING": 16.0,
    "REFERENCE_FRAME_BOTTOM_Z": 17.0,
    "REFERENCE_COORDINATE_RIM_Z": 45.0,
    "REFERENCE_MODEL_RIM_Z": 0.0,
}

REQUIRED_REFERENCE_CONSTANTS = tuple(CANONICAL_REFERENCE_CONSTANTS.keys())


@dataclass
class VerificationThresholds:
    axis_tolerance_mm: float = 0.25
    slot_depth_target_mm: float = 7.0
    slot_depth_tolerance_mm: float = 0.05
    corridor_radial_clearance_min_mm: float = 0.08
    frame_penetration_max_mm: float = 0.01
    frame_min_gap_mm: float = 0.08
    floor_clearance_min_mm: float = 2.0
    axis_scan_radius_mm: float = 0.8
    axis_scan_step_mm: float = 0.1
    corridor_samples: int = 29
    frame_bottom_z_tolerance_mm: float = 0.05


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    default_report = project_root / "_codex" / "reports" / "reference_fit_report.json"
    default_export_dir = project_root / "_codex" / "reports" / "reference_fit_tmp"

    parser = argparse.ArgumentParser(
        description="Verify canonical slot/frame/floor mechanics against exported hull geometry."
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
        help="Preset used when exporting hull STL (default: gcsc_default).",
    )
    parser.add_argument(
        "--openscad-path",
        default=None,
        help="Path to OpenSCAD binary. Falls back to OPENSCAD_PATH, system PATH, then Windows default.",
    )
    parser.add_argument(
        "--export-dir",
        type=Path,
        default=default_export_dir,
        help="Directory for generated wrappers and STLs.",
    )
    parser.add_argument("--hull-stl", type=Path, default=None, help="Use existing hull STL.")
    parser.add_argument("--frame-stl", type=Path, default=None, help="Use existing canonical frame STL.")
    parser.add_argument("--slot-plug-stl", type=Path, default=None, help="Use existing canonical slot plug STL.")
    parser.add_argument(
        "--reuse-exported-stls",
        action="store_true",
        help="Reuse existing STLs under --export-dir instead of forcing fresh exports.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=default_report,
        help="Output JSON report path.",
    )

    parser.add_argument("--axis-tolerance-mm", type=float, default=VerificationThresholds.axis_tolerance_mm)
    parser.add_argument(
        "--slot-depth-target-mm",
        type=float,
        default=VerificationThresholds.slot_depth_target_mm,
    )
    parser.add_argument(
        "--slot-depth-tolerance-mm",
        type=float,
        default=VerificationThresholds.slot_depth_tolerance_mm,
    )
    parser.add_argument(
        "--corridor-radial-clearance-min-mm",
        type=float,
        default=VerificationThresholds.corridor_radial_clearance_min_mm,
    )
    parser.add_argument(
        "--frame-penetration-max-mm",
        type=float,
        default=VerificationThresholds.frame_penetration_max_mm,
    )
    parser.add_argument("--frame-min-gap-mm", type=float, default=VerificationThresholds.frame_min_gap_mm)
    parser.add_argument(
        "--floor-clearance-min-mm",
        type=float,
        default=VerificationThresholds.floor_clearance_min_mm,
    )
    parser.add_argument("--axis-scan-radius-mm", type=float, default=VerificationThresholds.axis_scan_radius_mm)
    parser.add_argument("--axis-scan-step-mm", type=float, default=VerificationThresholds.axis_scan_step_mm)
    parser.add_argument("--corridor-samples", type=int, default=VerificationThresholds.corridor_samples)
    parser.add_argument(
        "--frame-bottom-z-tolerance-mm",
        type=float,
        default=VerificationThresholds.frame_bottom_z_tolerance_mm,
    )
    return parser.parse_args()


def build_thresholds(args: argparse.Namespace) -> VerificationThresholds:
    return VerificationThresholds(
        axis_tolerance_mm=args.axis_tolerance_mm,
        slot_depth_target_mm=args.slot_depth_target_mm,
        slot_depth_tolerance_mm=args.slot_depth_tolerance_mm,
        corridor_radial_clearance_min_mm=args.corridor_radial_clearance_min_mm,
        frame_penetration_max_mm=args.frame_penetration_max_mm,
        frame_min_gap_mm=args.frame_min_gap_mm,
        floor_clearance_min_mm=args.floor_clearance_min_mm,
        axis_scan_radius_mm=args.axis_scan_radius_mm,
        axis_scan_step_mm=args.axis_scan_step_mm,
        corridor_samples=max(2, args.corridor_samples),
        frame_bottom_z_tolerance_mm=max(0.001, args.frame_bottom_z_tolerance_mm),
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
        # Windows cross-drive temp paths cannot be expressed as relative paths.
        return target.resolve().as_posix()


def write_wrapper(path: Path, includes: list[str], body: str) -> None:
    lines = [f"include <{inc}>" for inc in includes]
    lines.append("")
    lines.append(body.strip())
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def ensure_export_inputs(project_root: Path, export_dir: Path, preset: str) -> dict[str, Path]:
    wrapper_dir = export_dir / "_generated_scad"
    wrapper_dir.mkdir(parents=True, exist_ok=True)

    preset_file = project_root / "codex_hull_lab" / "presets" / f"{preset}.scad"
    hull_core = project_root / "codex_hull_lab" / "src" / "gcsc_hull_core.scad"
    frame_ref = project_root / "codex_hull_lab" / "reference" / "frame_v5_3_reference.scad"
    plug_ref = project_root / "codex_hull_lab" / "reference" / "slot_plug_reference.scad"

    missing = [p for p in (preset_file, hull_core, frame_ref, plug_ref) if not p.exists()]
    if missing:
        missing_text = ", ".join(str(p) for p in missing)
        raise FileNotFoundError(f"Required export source files missing: {missing_text}")

    hull_wrapper = wrapper_dir / "reference_fit_hull.scad"
    frame_wrapper = wrapper_dir / "reference_fit_frame.scad"
    plug_wrapper = wrapper_dir / "reference_fit_slot_plug.scad"

    write_wrapper(
        hull_wrapper,
        includes=[
            relative_include(wrapper_dir, preset_file),
            relative_include(wrapper_dir, hull_core),
        ],
        body="gcsc_hull_build();",
    )
    write_wrapper(
        frame_wrapper,
        includes=[relative_include(wrapper_dir, frame_ref)],
        body="gcsc_reference_frame_v53_infill();",
    )
    write_wrapper(
        plug_wrapper,
        includes=[relative_include(wrapper_dir, plug_ref)],
        body="gcsc_reference_slot_plug();",
    )

    return {
        "hull_wrapper": hull_wrapper,
        "frame_wrapper": frame_wrapper,
        "plug_wrapper": plug_wrapper,
    }


def run_openscad_export(openscad_bin: str, input_scad: Path, output_stl: Path, cwd: Path) -> None:
    output_stl.parent.mkdir(parents=True, exist_ok=True)
    cmd = [openscad_bin, "--render", "-o", str(output_stl), str(input_scad)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=900)
    if result.returncode != 0 or not output_stl.exists():
        raise RuntimeError(
            "\n".join(
                [
                    f"OpenSCAD export failed for {input_scad}",
                    f"Return code: {result.returncode}",
                    f"STDOUT:\n{result.stdout}",
                    f"STDERR:\n{result.stderr}",
                ]
            )
        )


def load_mesh(path: Path, label: str) -> trimesh.Trimesh:
    if not path.exists():
        raise FileNotFoundError(f"{label} STL not found: {path}")

    mesh = trimesh.load(path, force="mesh")
    if isinstance(mesh, trimesh.Scene):
        if not mesh.geometry:
            raise ValueError(f"{label} STL contains no geometry: {path}")
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"{label} STL did not resolve to a mesh: {path}")
    mesh.remove_unreferenced_vertices()
    return mesh


def parse_reference_constants(reference_file: Path) -> dict[str, float]:
    if not reference_file.exists():
        raise FileNotFoundError(f"Reference constants file not found: {reference_file}")

    assignment_pattern = re.compile(r"^\s*(REFERENCE_[A-Z0-9_]+)\s*=\s*(.+?)\s*;\s*$")
    expressions: dict[str, str] = {}
    for line in reference_file.read_text(encoding="utf-8").splitlines():
        match = assignment_pattern.match(line)
        if not match:
            continue
        expressions[match.group(1)] = match.group(2).strip()

    constants: dict[str, float] = {}

    def eval_expression(expr: str) -> float:
        allowed_bin_ops = {
            ast.Add: lambda a, b: a + b,
            ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b,
            ast.Div: lambda a, b: a / b,
        }
        allowed_unary_ops = {
            ast.UAdd: lambda v: +v,
            ast.USub: lambda v: -v,
        }

        def walk(node: ast.AST) -> float:
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return float(node.value)
            if isinstance(node, ast.Name):
                if node.id not in constants:
                    raise KeyError(node.id)
                return float(constants[node.id])
            if isinstance(node, ast.BinOp) and type(node.op) in allowed_bin_ops:
                left = walk(node.left)
                right = walk(node.right)
                return float(allowed_bin_ops[type(node.op)](left, right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary_ops:
                value = walk(node.operand)
                return float(allowed_unary_ops[type(node.op)](value))
            raise ValueError(f"Unsupported expression: {expr}")

        parsed = ast.parse(expr, mode="eval")
        return walk(parsed.body)

    unresolved = dict(expressions)
    while unresolved:
        progressed = False
        for name in list(unresolved.keys()):
            expr = unresolved[name]
            try:
                constants[name] = eval_expression(expr)
            except KeyError:
                continue
            progressed = True
            unresolved.pop(name)
        if not progressed:
            unresolved_text = ", ".join(f"{k}={v}" for k, v in unresolved.items())
            raise ValueError(f"Could not resolve reference constants: {unresolved_text}")

    missing = [name for name in REQUIRED_REFERENCE_CONSTANTS if name not in constants]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Missing required reference constants: {missing_text}")

    return constants


def evaluate_reference_constant_lock(constants: dict[str, float]) -> tuple[bool, list[dict[str, float]]]:
    deltas = []
    locked = True
    for name, expected in CANONICAL_REFERENCE_CONSTANTS.items():
        observed = constants.get(name)
        delta = float(observed - expected)
        if abs(delta) > 1e-6:
            locked = False
        deltas.append(
            {
                "name": name,
                "expected": float(expected),
                "observed": float(observed),
                "delta_mm": delta,
            }
        )
    return locked, deltas


def slot_scan_grid(expected_x: float, expected_y: float, seat_z: float, radius: float, step: float) -> np.ndarray:
    points_per_axis = int(round((2 * radius) / step)) + 1
    xs = np.linspace(expected_x - radius, expected_x + radius, points_per_axis)
    ys = np.linspace(expected_y - radius, expected_y + radius, points_per_axis)
    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    zz = np.full(xx.size, seat_z, dtype=float)
    return np.column_stack((xx.reshape(-1), yy.reshape(-1), zz))


def measure_slot_geometry(
    hull_mesh: trimesh.Trimesh,
    expected_x: float,
    expected_y: float,
    seat_z: float,
    entry_z: float,
    ball_radius: float,
    thresholds: VerificationThresholds,
) -> dict[str, Any]:
    grid = slot_scan_grid(
        expected_x=expected_x,
        expected_y=expected_y,
        seat_z=seat_z,
        radius=thresholds.axis_scan_radius_mm,
        step=thresholds.axis_scan_step_mm,
    )
    scan_signed = signed_distance(hull_mesh, grid)
    scan_free_radius = -scan_signed
    best_idx = int(np.argmax(scan_free_radius))

    observed_x = float(grid[best_idx, 0])
    observed_y = float(grid[best_idx, 1])
    seat_free_radius = float(scan_free_radius[best_idx])
    seat_radial_clearance = float(seat_free_radius - ball_radius)
    axis_error = float(math.hypot(observed_x - expected_x, observed_y - expected_y))

    zs = np.linspace(seat_z, entry_z, thresholds.corridor_samples)
    path = np.column_stack(
        (
            np.full_like(zs, observed_x, dtype=float),
            np.full_like(zs, observed_y, dtype=float),
            zs,
        )
    )
    corridor_signed = signed_distance(hull_mesh, path)
    corridor_free_radius = -corridor_signed
    corridor_min_free_radius = float(np.min(corridor_free_radius))
    corridor_min_radial_clearance = float(corridor_min_free_radius - ball_radius)

    return {
        "expected_x_mm": float(expected_x),
        "expected_y_mm": float(expected_y),
        "observed_x_mm": observed_x,
        "observed_y_mm": observed_y,
        "axis_error_mm": axis_error,
        "seat_free_radius_mm": seat_free_radius,
        "seat_radial_clearance_mm": seat_radial_clearance,
        "corridor_min_free_radius_mm": corridor_min_free_radius,
        "corridor_min_radial_clearance_mm": corridor_min_radial_clearance,
        "axis_pass": axis_error <= thresholds.axis_tolerance_mm,
        "corridor_pass": corridor_min_radial_clearance >= thresholds.corridor_radial_clearance_min_mm,
    }


def measure_floor_clearances(hull_mesh: trimesh.Trimesh, bottom_points: np.ndarray) -> list[float]:
    if bottom_points.size == 0:
        return []

    origins = bottom_points + np.array([0.0, 0.0, -1e-4], dtype=float)
    directions = np.repeat(np.array([[0.0, 0.0, -1.0]], dtype=float), len(origins), axis=0)
    locations, index_ray, _ = hull_mesh.ray.intersects_location(origins, directions, multiple_hits=True)

    clearances: list[float] = []
    for ray_idx, point in enumerate(bottom_points):
        hits = locations[index_ray == ray_idx]
        if hits.size == 0:
            continue
        z_hits = hits[:, 2]
        z_hits = z_hits[z_hits < point[2] - 1e-6]
        if z_hits.size == 0:
            continue
        floor_z = float(np.max(z_hits))
        clearances.append(float(point[2] - floor_z))
    return clearances


def analyze_frame_fit(
    hull_mesh: trimesh.Trimesh,
    frame_mesh: trimesh.Trimesh,
    frame_spacing_mm: float,
    frame_alignment_z_mm: float,
    thresholds: VerificationThresholds,
) -> list[dict[str, Any]]:
    sample_points = np.vstack((frame_mesh.vertices, frame_mesh.triangles_center))
    frame_results: list[dict[str, Any]] = []

    for x_sign in (-1, 1):
        x_offset = x_sign * frame_spacing_mm
        translation = np.array([x_offset, 0.0, frame_alignment_z_mm], dtype=float)
        transformed_samples = sample_points + translation
        sample_signed = signed_distance(hull_mesh, transformed_samples)

        max_penetration = max(0.0, float(np.max(sample_signed)))
        penetrating_points = int(np.count_nonzero(sample_signed > 0.0))
        penetrating_points_over_tolerance = int(
            np.count_nonzero(sample_signed > thresholds.frame_penetration_max_mm)
        )
        non_penetrating = sample_signed <= 0.0
        min_gap = float(np.min(-sample_signed[non_penetrating])) if np.any(non_penetrating) else 0.0

        frame_vertices = frame_mesh.vertices + translation
        min_z = float(np.min(frame_vertices[:, 2]))
        bottom_mask = np.abs(frame_vertices[:, 2] - min_z) <= thresholds.frame_bottom_z_tolerance_mm
        bottom_points = frame_vertices[bottom_mask]
        floor_clearances = measure_floor_clearances(hull_mesh, bottom_points)
        floor_clearance_min = float(min(floor_clearances)) if floor_clearances else None

        frame_results.append(
            {
                "placement_x_mm": float(x_offset),
                "sample_point_count": int(len(transformed_samples)),
                "max_penetration_mm": max_penetration,
                "penetrating_points": penetrating_points,
                "penetrating_points_over_tolerance": penetrating_points_over_tolerance,
                "min_gap_mm": min_gap,
                "frame_bottom_z_mm": min_z,
                "bottom_probe_count": int(len(bottom_points)),
                "floor_clearance_min_mm": floor_clearance_min,
                "floor_clearance_samples_mm": [float(v) for v in floor_clearances],
                "interference_pass": (
                    penetrating_points_over_tolerance == 0 and min_gap >= thresholds.frame_min_gap_mm
                ),
                "floor_clearance_pass": (
                    floor_clearance_min is not None
                    and floor_clearance_min >= thresholds.floor_clearance_min_mm
                ),
            }
        )

    return frame_results


def analyze_reference_fit(
    hull_mesh: trimesh.Trimesh,
    frame_mesh: trimesh.Trimesh,
    slot_plug_mesh: trimesh.Trimesh,
    reference_constants: dict[str, float],
    thresholds: VerificationThresholds,
    reference_constants_locked: bool,
) -> dict[str, Any]:
    frame_spacing = reference_constants["REFERENCE_FRAME_SPACING"]
    pivot_y = reference_constants["REFERENCE_PIVOT_Y"]
    slot_diameter = reference_constants["REFERENCE_SLOT_DIAMETER"]
    ball_diameter = reference_constants["REFERENCE_BALL_DIAMETER"]
    pivot_z = reference_constants["REFERENCE_PIVOT_Z"]
    slot_entry_z = reference_constants["REFERENCE_SLOT_ENTRY_Z"]
    coordinate_rim_z = reference_constants["REFERENCE_COORDINATE_RIM_Z"]
    model_rim_z = reference_constants["REFERENCE_MODEL_RIM_Z"]

    seat_z_model = pivot_z - coordinate_rim_z + model_rim_z
    entry_z_model = slot_entry_z - coordinate_rim_z + model_rim_z
    frame_alignment_z = model_rim_z - coordinate_rim_z
    slot_depth = slot_entry_z - pivot_z
    ball_radius = ball_diameter / 2.0

    slot_results: list[dict[str, Any]] = []
    for x_sign in (-1, 1):
        for y_sign in (-1, 1):
            slot_results.append(
                measure_slot_geometry(
                    hull_mesh=hull_mesh,
                    expected_x=x_sign * frame_spacing,
                    expected_y=y_sign * pivot_y,
                    seat_z=seat_z_model,
                    entry_z=entry_z_model,
                    ball_radius=ball_radius,
                    thresholds=thresholds,
                )
            )

    frame_results = analyze_frame_fit(
        hull_mesh=hull_mesh,
        frame_mesh=frame_mesh,
        frame_spacing_mm=frame_spacing,
        frame_alignment_z_mm=frame_alignment_z,
        thresholds=thresholds,
    )

    overall_min_gap = min(result["min_gap_mm"] for result in frame_results) if frame_results else None
    floor_values = [result["floor_clearance_min_mm"] for result in frame_results if result["floor_clearance_min_mm"] is not None]
    overall_floor_clearance_min = min(floor_values) if floor_values else None

    slot_axis_pass = all(result["axis_pass"] for result in slot_results)
    slot_corridor_pass = all(result["corridor_pass"] for result in slot_results)
    slot_depth_pass = abs(slot_depth - thresholds.slot_depth_target_mm) <= thresholds.slot_depth_tolerance_mm
    frame_interference_pass = all(result["interference_pass"] for result in frame_results)
    frame_floor_pass = all(result["floor_clearance_pass"] for result in frame_results)

    gates = {
        "hull_mesh_watertight": bool(hull_mesh.is_watertight),
        "reference_constants_locked": bool(reference_constants_locked),
        "slot_axis_positions": bool(slot_axis_pass),
        "slot_depth": bool(slot_depth_pass),
        "slot_insertion_corridor": bool(slot_corridor_pass),
        "frame_interference": bool(frame_interference_pass),
        "frame_floor_clearance": bool(frame_floor_pass),
    }

    measurements = {
        "seat_z_model_mm": float(seat_z_model),
        "entry_z_model_mm": float(entry_z_model),
        "frame_alignment_z_mm": float(frame_alignment_z),
        "slot_depth_mm": float(slot_depth),
        "slot_diameter_mm": float(slot_diameter),
        "ball_diameter_mm": float(ball_diameter),
        "slot_radial_clearance_target_mm": float((slot_diameter - ball_diameter) / 2.0),
        "slot_checks": slot_results,
        "frame_checks": frame_results,
        "overall_min_frame_gap_mm": float(overall_min_gap) if overall_min_gap is not None else None,
        "overall_floor_clearance_min_mm": (
            float(overall_floor_clearance_min) if overall_floor_clearance_min is not None else None
        ),
        "hull_mesh_faces": int(len(hull_mesh.faces)),
        "frame_mesh_faces": int(len(frame_mesh.faces)),
        "slot_plug_mesh_faces": int(len(slot_plug_mesh.faces)),
        "slot_plug_mesh_watertight": bool(slot_plug_mesh.is_watertight),
    }

    return {
        "measurements": measurements,
        "gates": gates,
        "pass": all(gates.values()),
    }


def ensure_geometry_inputs(
    project_root: Path,
    export_dir: Path,
    preset: str,
    openscad_path: str | None,
    hull_stl: Path,
    frame_stl: Path,
    slot_plug_stl: Path,
    reuse_exported_stls: bool,
    explicit_input_stls: bool,
) -> tuple[Path, Path, Path]:
    if explicit_input_stls:
        missing = [p for p in (hull_stl, frame_stl, slot_plug_stl) if not p.exists()]
        if missing:
            raise FileNotFoundError(
                "Explicit STL input path(s) missing: " + ", ".join(str(p) for p in missing)
            )
        return hull_stl, frame_stl, slot_plug_stl

    if (
        reuse_exported_stls
        and hull_stl.exists()
        and frame_stl.exists()
        and slot_plug_stl.exists()
    ):
        return hull_stl, frame_stl, slot_plug_stl

    export_inputs = ensure_export_inputs(project_root=project_root, export_dir=export_dir, preset=preset)
    openscad_bin = resolve_openscad(openscad_path)

    if not reuse_exported_stls or not hull_stl.exists():
        run_openscad_export(
            openscad_bin=openscad_bin,
            input_scad=export_inputs["hull_wrapper"],
            output_stl=hull_stl,
            cwd=project_root,
        )
    if not reuse_exported_stls or not frame_stl.exists():
        run_openscad_export(
            openscad_bin=openscad_bin,
            input_scad=export_inputs["frame_wrapper"],
            output_stl=frame_stl,
            cwd=project_root,
        )
    if not reuse_exported_stls or not slot_plug_stl.exists():
        run_openscad_export(
            openscad_bin=openscad_bin,
            input_scad=export_inputs["plug_wrapper"],
            output_stl=slot_plug_stl,
            cwd=project_root,
        )
    return hull_stl, frame_stl, slot_plug_stl


def print_summary(report: dict[str, Any]) -> None:
    gates = report["gates"]
    measurements = report["measurements"]

    print("=== Reference Fit Verification ===")
    print(f"Reference constants locked: {gates['reference_constants_locked']}")
    print(f"Slot axis positions:       {gates['slot_axis_positions']}")
    print(f"Slot depth target:         {gates['slot_depth']}")
    print(f"Slot insertion corridor:   {gates['slot_insertion_corridor']}")
    print(f"Frame interference:        {gates['frame_interference']}")
    print(f"Frame floor clearance:     {gates['frame_floor_clearance']}")
    print(f"Hull watertight:           {gates['hull_mesh_watertight']}")
    print(f"Overall min frame gap mm:  {measurements['overall_min_frame_gap_mm']}")
    print(f"Overall floor clear mm:    {measurements['overall_floor_clearance_min_mm']}")
    print(f"OVERALL: {'PASS' if report['pass'] else 'FAIL'}")


def main() -> int:
    args = parse_args()

    try:
        import rtree  # noqa: F401  pylint: disable=unused-import
    except ModuleNotFoundError:
        print(
            "Missing dependency: rtree. Install with `pip install -r requirements-dev.txt`.",
            file=sys.stderr,
        )
        return 2

    project_root = args.project_root.resolve()
    export_dir = args.export_dir.resolve()
    output_json = args.output_json.resolve()

    hull_stl = (args.hull_stl or (export_dir / "hull_default.stl")).resolve()
    frame_stl = (args.frame_stl or (export_dir / "frame_reference.stl")).resolve()
    slot_plug_stl = (args.slot_plug_stl or (export_dir / "slot_plug_reference.stl")).resolve()
    explicit_input_stls = bool(args.hull_stl and args.frame_stl and args.slot_plug_stl)

    thresholds = build_thresholds(args)

    reference_file = project_root / "codex_hull_lab" / "src" / "gcsc_reference_params.scad"
    reference_constants = parse_reference_constants(reference_file)
    reference_constants_locked, reference_constant_deltas = evaluate_reference_constant_lock(reference_constants)

    hull_stl, frame_stl, slot_plug_stl = ensure_geometry_inputs(
        project_root=project_root,
        export_dir=export_dir,
        preset=args.preset,
        openscad_path=args.openscad_path,
        hull_stl=hull_stl,
        frame_stl=frame_stl,
        slot_plug_stl=slot_plug_stl,
        reuse_exported_stls=args.reuse_exported_stls,
        explicit_input_stls=explicit_input_stls,
    )

    hull_mesh = load_mesh(hull_stl, "Hull")
    frame_mesh = load_mesh(frame_stl, "Frame")
    slot_plug_mesh = load_mesh(slot_plug_stl, "Slot plug")

    analysis = analyze_reference_fit(
        hull_mesh=hull_mesh,
        frame_mesh=frame_mesh,
        slot_plug_mesh=slot_plug_mesh,
        reference_constants=reference_constants,
        thresholds=thresholds,
        reference_constants_locked=reference_constants_locked,
    )

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "project_root": str(project_root),
            "preset": args.preset,
            "hull_stl": str(hull_stl),
            "frame_stl": str(frame_stl),
            "slot_plug_stl": str(slot_plug_stl),
            "reuse_exported_stls": bool(args.reuse_exported_stls),
            "reference_constants_file": str(reference_file),
        },
        "thresholds": asdict(thresholds),
        "reference_constants": reference_constants,
        "reference_constant_deltas": reference_constant_deltas,
        "assumptions": [
            "Frame neutral pose is evaluated at x = +/-REFERENCE_FRAME_SPACING with reference rim alignment.",
            "Floor clearance is the vertical distance from frame bottom points to first hull intersection below each point.",
            "Slot corridor check follows the optimized slot axis on seat plane from seat Z to entry Z.",
        ],
    }
    report.update(analysis)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print_summary(report)
    print(f"Report written: {output_json}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
