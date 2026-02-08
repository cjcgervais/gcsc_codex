#!/usr/bin/env python3
"""GCSC2 OpenSCAD MCP Server

Custom MCP server for the GCSC2 project providing:
- File-based OpenSCAD rendering with named camera presets
- STL export
- Syntax validation (fast .csg export check)
- Camera preset management

Designed for GCSC2's modular file-based workflow with include/use dependencies.
"""

import subprocess
import os
import sys
import json
import tempfile
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("gcsc-openscad")

# Configuration - override via environment variables
OPENSCAD_PATH = os.environ.get(
    "OPENSCAD_PATH",
    r"C:\Program Files\OpenSCAD\openscad.exe"
)


def _discover_project_root() -> str:
    """Resolve project root from env override or repository-relative fallback."""
    env_root = os.environ.get("GCSC_PROJECT_ROOT", "").strip()
    if env_root:
        p = Path(env_root).expanduser()
        if p.exists():
            return str(p.resolve())
    # scripts/openscad_mcp_server.py -> repo root is parent of scripts/
    return str(Path(__file__).resolve().parent.parent)


PROJECT_ROOT = _discover_project_root()

# Named camera presets extracted from the GCSC2 workflow
# Format: translate_x,y,z,rot_x,y,z,dist
CAMERA_PRESETS = {
    "iso":           "50,50,35,60,0,35,220",
    "top":           "0,0,150,0,0,0,200",
    "side":          "0,60,35,70,0,25,180",
    "front":         "0,100,45,75,0,0,250",
    "slot_detail":   "16,33,38,0,0,25,80",
    "assembly":      "50,50,35,60,0,35,250",
    "cross_section": "0,80,38,75,0,0,180",
    "frame_detail":  "70,70,50,60,0,35,250",
    "side_close":    "0,60,20,70,0,0,200",
    "alignment":     "0,0,50,55,0,25,300",
}

DEFAULT_IMG_SIZE = (1024, 768)


def _resolve_path(file_path: str) -> str:
    """Resolve a file path relative to project root if not absolute."""
    p = Path(file_path)
    if not p.is_absolute():
        p = Path(PROJECT_ROOT) / p
    return str(p)


def _run_openscad(args: list[str], timeout: int = 120) -> dict:
    """Run OpenSCAD with given arguments, return result dict."""
    cmd = [OPENSCAD_PATH] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=PROJECT_ROOT,
        )
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"OpenSCAD timed out after {timeout}s",
        }
    except FileNotFoundError:
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"OpenSCAD not found at: {OPENSCAD_PATH}",
        }


@mcp.tool()
def render_file(
    file_path: str,
    camera: str = "iso",
    output_path: str = "",
    width: int = 1024,
    height: int = 768,
) -> str:
    """Render an OpenSCAD file to PNG.

    Args:
        file_path: Path to .scad file (relative to project root or absolute)
        camera: Named preset (iso, top, side, front, slot_detail, assembly,
                cross_section, frame_detail, side_close, alignment) or
                custom camera string (translate_x,y,z,rot_x,y,z,dist)
        output_path: Where to save PNG (relative to project root or absolute).
                     If empty, saves to renders/ directory with auto-generated name.
        width: Image width in pixels (default 1024)
        height: Image height in pixels (default 768)

    Returns:
        JSON string with success status, output path, and file size.
    """
    scad_path = _resolve_path(file_path)
    if not os.path.exists(scad_path):
        return json.dumps({"success": False, "error": f"File not found: {scad_path}"})

    # Resolve camera preset or use custom string
    camera_str = CAMERA_PRESETS.get(camera, camera)

    # Auto-generate output path if not specified
    if not output_path:
        stem = Path(scad_path).stem
        preset_name = camera if camera in CAMERA_PRESETS else "custom"
        # Determine renders dir relative to the scad file's parent
        scad_dir = Path(scad_path).parent
        renders_dir = scad_dir / "renders"
        renders_dir.mkdir(exist_ok=True)
        output_path = str(renders_dir / f"{stem}_{preset_name}.png")
    else:
        output_path = _resolve_path(output_path)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    args = [
        "--render",
        f"--camera={camera_str}",
        f"--imgsize={width},{height}",
        "-o", output_path,
        scad_path,
    ]

    result = _run_openscad(args)
    if result["success"]:
        file_size = os.path.getsize(output_path)
        return json.dumps({
            "success": True,
            "output_path": output_path,
            "file_size_bytes": file_size,
            "camera_preset": camera if camera in CAMERA_PRESETS else "custom",
            "camera_string": camera_str,
            "resolution": f"{width}x{height}",
        })
    else:
        return json.dumps({
            "success": False,
            "error": result["stderr"],
            "exit_code": result["exit_code"],
        })


@mcp.tool()
def render_standard_views(
    file_path: str,
    views: list[str] | None = None,
    width: int = 1024,
    height: int = 768,
) -> str:
    """Render multiple standard views of an OpenSCAD file.

    Args:
        file_path: Path to .scad file
        views: List of preset names to render. Defaults to [iso, top, side].
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        JSON with results for each view.
    """
    if views is None:
        views = ["iso", "top", "side"]

    results = {}
    for view in views:
        if view not in CAMERA_PRESETS:
            results[view] = {"success": False, "error": f"Unknown preset: {view}"}
            continue

        scad_path = _resolve_path(file_path)
        stem = Path(scad_path).stem
        scad_dir = Path(scad_path).parent
        renders_dir = scad_dir / "renders"
        renders_dir.mkdir(exist_ok=True)
        out = str(renders_dir / f"{stem}_{view}.png")

        args = [
            "--render",
            f"--camera={CAMERA_PRESETS[view]}",
            f"--imgsize={width},{height}",
            "-o", out,
            scad_path,
        ]

        r = _run_openscad(args)
        if r["success"]:
            results[view] = {
                "success": True,
                "output_path": out,
                "file_size_bytes": os.path.getsize(out),
            }
        else:
            results[view] = {"success": False, "error": r["stderr"]}

    return json.dumps(results, indent=2)


@mcp.tool()
def export_stl(file_path: str, output_path: str = "") -> str:
    """Export an OpenSCAD file to STL.

    Args:
        file_path: Path to .scad file
        output_path: Where to save STL. If empty, saves to STL_Exports/ directory.

    Returns:
        JSON with success status, output path, file size, and provenance info.
    """
    import hashlib
    from datetime import datetime, timezone

    scad_path = _resolve_path(file_path)
    if not os.path.exists(scad_path):
        return json.dumps({"success": False, "error": f"File not found: {scad_path}"})

    if not output_path:
        stem = Path(scad_path).stem
        scad_dir = Path(scad_path).parent
        stl_dir = scad_dir / "STL_Exports"
        stl_dir.mkdir(exist_ok=True)
        output_path = str(stl_dir / f"{stem}.stl")
    else:
        output_path = _resolve_path(output_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # P0 FIX: Always use --render for canonical geometry export (not preview mode)
    # This ensures CGAL-accurate geometry instead of OpenGL approximation
    result = _run_openscad(["--render", "-o", output_path, scad_path], timeout=300)
    if result["success"]:
        import platform

        file_size = os.path.getsize(output_path)

        # P3: Generate provenance info
        # Calculate source file hash
        with open(scad_path, "rb") as f:
            source_hash = hashlib.sha256(f.read()).hexdigest()[:16]
        # Calculate STL hash
        with open(output_path, "rb") as f:
            stl_hash = hashlib.sha256(f.read()).hexdigest()[:16]

        # Get git commit if available
        try:
            git_result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, cwd=PROJECT_ROOT
            )
            git_commit = git_result.stdout.strip() if git_result.returncode == 0 else "unknown"
        except Exception:
            git_commit = "unknown"

        # Get OpenSCAD version
        try:
            version_result = subprocess.run(
                [OPENSCAD_PATH, "--version"],
                capture_output=True, text=True, timeout=10
            )
            # OpenSCAD outputs version to stderr
            openscad_version = (version_result.stderr or version_result.stdout).strip()
        except Exception:
            openscad_version = "unknown"

        # Get BOSL2 submodule commit (if present)
        bosl2_commit = "unknown"
        bosl2_path = Path(PROJECT_ROOT) / "02_Production_BOSL2" / "lib" / "BOSL2"
        if bosl2_path.exists():
            try:
                bosl2_result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    capture_output=True, text=True, cwd=str(bosl2_path)
                )
                if bosl2_result.returncode == 0:
                    bosl2_commit = bosl2_result.stdout.strip()
            except Exception:
                pass

        # Collect validator metrics (for determinism signature)
        validator_metrics = {}
        try:
            import trimesh
            mesh = trimesh.load(output_path)
            validator_metrics = {
                "validator": "trimesh",
                "watertight": mesh.is_watertight,
                "is_volume": mesh.is_volume,
                "euler_number": mesh.euler_number,
                "body_count": 1,  # trimesh loads as single mesh
                "vertices": len(mesh.vertices),
                "faces": len(mesh.faces),
                "bounds": {
                    "min": mesh.bounds[0].tolist() if mesh.bounds is not None else None,
                    "max": mesh.bounds[1].tolist() if mesh.bounds is not None else None,
                },
            }
        except ImportError:
            # trimesh not available, try admesh
            try:
                admesh_result = subprocess.run(
                    ["admesh", "--check", output_path],
                    capture_output=True, text=True, timeout=60
                )
                if admesh_result.returncode == 0:
                    import re
                    output = admesh_result.stdout + admesh_result.stderr
                    facets = re.search(r"(\d+)\s+facets", output)
                    edges = re.search(r"(\d+)\s+edges fixed", output)
                    validator_metrics = {
                        "validator": "admesh",
                        "facets": int(facets.group(1)) if facets else None,
                        "edges_fixed": int(edges.group(1)) if edges else 0,
                        "manifold": (int(edges.group(1)) if edges else 0) == 0,
                    }
            except Exception:
                validator_metrics = {"validator": "none", "error": "no validator available"}
        except Exception as e:
            validator_metrics = {"validator": "trimesh", "error": str(e)}

        provenance = {
            "source_file": scad_path,
            "source_hash": source_hash,
            "stl_hash": stl_hash,
            "git_commit": git_commit,
            "export_timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "render_mode": "full",  # --render flag used
            "openscad_path": OPENSCAD_PATH,
            "openscad_version": openscad_version,
            "bosl2_commit": bosl2_commit,
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": platform.python_version(),
            },
            "validator_metrics": validator_metrics,
        }

        # P1.1: Write provenance sidecar file
        provenance_path = output_path + ".provenance.json"
        with open(provenance_path, "w") as f:
            json.dump(provenance, f, indent=2)

        return json.dumps({
            "success": True,
            "output_path": output_path,
            "file_size_bytes": file_size,
            "file_size_kb": round(file_size / 1024, 1),
            "provenance": provenance,
            "provenance_sidecar": provenance_path,  # P1.1: Sidecar file location
        })
    else:
        return json.dumps({
            "success": False,
            "error": result["stderr"],
        })


@mcp.tool()
def check_syntax(file_path: str) -> str:
    """Quick syntax validation of an OpenSCAD file.

    Uses fast .csg export (CSG tree only, no geometry computation) to check
    for syntax errors, undefined variables, and missing includes.

    Args:
        file_path: Path to .scad file

    Returns:
        JSON with syntax check result.
    """
    scad_path = _resolve_path(file_path)
    if not os.path.exists(scad_path):
        return json.dumps({"success": False, "error": f"File not found: {scad_path}"})

    with tempfile.NamedTemporaryFile(suffix=".csg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        result = _run_openscad(["-o", tmp_path, scad_path], timeout=30)
        return json.dumps({
            "valid": result["success"],
            "file": scad_path,
            "errors": result["stderr"] if not result["success"] else "",
            "echo_output": result["stdout"] if result["success"] else "",
        })
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@mcp.tool()
def validate_mesh(stl_path: str) -> str:
    """Validate an STL file for mesh integrity (P1: Mesh Validation).

    Checks for:
    - Manifold (watertight) mesh
    - Degenerate facets (zero-area triangles)
    - Self-intersections (where detectable)

    Uses admesh if available, falls back to basic STL parsing.

    Args:
        stl_path: Path to .stl file

    Returns:
        JSON with validation results.
    """
    stl_path = _resolve_path(stl_path)
    if not os.path.exists(stl_path):
        return json.dumps({"valid": False, "error": f"File not found: {stl_path}"})

    # Try admesh first (best mesh validation)
    try:
        result = subprocess.run(
            ["admesh", "--check", stl_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            output = result.stdout + result.stderr
            # Parse admesh output for key metrics
            is_manifold = "0 edges fixed" in output or "edges fixed" not in output
            has_degenerate = "degenerate" in output.lower() and "0 degenerate" not in output
            has_holes = "holes" in output.lower() and "0 holes" not in output

            # Extract specific numbers if possible
            import re
            facets_match = re.search(r"(\d+)\s+facets", output)
            edges_fixed_match = re.search(r"(\d+)\s+edges fixed", output)
            degenerate_match = re.search(r"(\d+)\s+degenerate", output)
            holes_match = re.search(r"(\d+)\s+holes", output)

            facets = int(facets_match.group(1)) if facets_match else None
            edges_fixed = int(edges_fixed_match.group(1)) if edges_fixed_match else 0
            degenerate_count = int(degenerate_match.group(1)) if degenerate_match else 0
            holes_count = int(holes_match.group(1)) if holes_match else 0

            is_valid = edges_fixed == 0 and degenerate_count == 0 and holes_count == 0

            return json.dumps({
                "valid": is_valid,
                "tool": "admesh",
                "manifold": edges_fixed == 0,
                "degenerate_facets": degenerate_count,
                "holes": holes_count,
                "total_facets": facets,
                "raw_output": output[:500],  # Truncate for brevity
            })
    except FileNotFoundError:
        pass  # admesh not installed, fall back
    except Exception as e:
        pass  # Fall back on any error

    # Fallback: Basic STL parsing
    try:
        file_size = os.path.getsize(stl_path)
        with open(stl_path, "rb") as f:
            header = f.read(80)
            is_binary = not header.startswith(b"solid") or b"\x00" in header

        if is_binary:
            with open(stl_path, "rb") as f:
                f.seek(80)  # Skip header
                num_facets = int.from_bytes(f.read(4), "little")
        else:
            with open(stl_path, "r") as f:
                content = f.read()
                num_facets = content.count("facet normal")

        # Basic sanity checks
        min_expected_size = num_facets * 50 if is_binary else num_facets * 200
        is_reasonable_size = file_size > min_expected_size * 0.5

        return json.dumps({
            "valid": is_reasonable_size and num_facets > 0,
            "tool": "basic_stl_parser",
            "facets": num_facets,
            "file_size_bytes": file_size,
            "is_binary": is_binary,
            "warning": "admesh not available for full validation",
        })
    except Exception as e:
        return json.dumps({
            "valid": False,
            "error": f"Failed to parse STL: {str(e)}",
        })


@mcp.tool()
def list_camera_presets() -> str:
    """List all available named camera presets.

    Returns:
        JSON mapping preset names to camera coordinate strings.
        Camera format: translate_x,y,z,rot_x,y,z,dist
    """
    return json.dumps({
        "presets": CAMERA_PRESETS,
        "format": "translate_x,translate_y,translate_z,rot_x,rot_y,rot_z,distance",
        "note": "Use preset name in render_file() camera parameter, or pass custom coordinates",
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
