#!/usr/bin/env python3
"""GCSC2 Mesh Integrity Check Hook (PostToolUse)

P0 Governance: BLOCKS invalid mesh after STL export.

This hook exists because:
- hull_v7_bosl2 passed all syntax checks and visual verification
- But the exported STL had catastrophic geometry defects (lopsided, open ends)
- Mesh validation catches non-manifold, degenerate, and self-intersecting geometry

Hook protocol:
  - Receives JSON on stdin with tool_name and tool_result
  - Exit 0 = allow (mesh is valid)
  - Exit 2 = BLOCK (mesh is non-manifold or degenerate)
  - Prints mesh validation report after STL exports

BLOCKING BEHAVIOR (P0 enforcement):
  - AUTHORITATIVE validators: trimesh (preferred), admesh
  - HARD GATES (block on failure):
    - watertight = false → BLOCK
    - is_volume = false → BLOCK
    - non-manifold edges → BLOCK
    - no authoritative validator → BLOCK
    - export succeeded but STL missing → BLOCK
  - SOFT GATES (warn only):
    - euler_number != 2 → WARN (valid for multi-shell, cavities)
  - Invalid STL artifacts cannot be produced

Reference: GOVERNANCE_IMPROVEMENTS_REMAINING.md (P0.1)
"""

import sys
import json
import subprocess
import os
from pathlib import Path

# Threshold for file size sanity check (STL should be at least this many KB)
MIN_STL_SIZE_KB = 50


def validate_with_trimesh(stl_path: str) -> dict:
    """Try to validate mesh using trimesh (pip install trimesh)."""
    try:
        import trimesh
        mesh = trimesh.load(stl_path)
        return {
            "tool": "trimesh",
            "available": True,
            "manifold": mesh.is_watertight,
            "is_volume": mesh.is_volume,
            "euler_number": mesh.euler_number,
            "vertices": len(mesh.vertices),
            "faces": len(mesh.faces),
        }
    except ImportError:
        return {"tool": "trimesh", "available": False}
    except Exception as e:
        return {"tool": "trimesh", "available": False, "error": str(e)}


def validate_with_admesh(stl_path: str) -> dict:
    """Try to validate mesh using admesh."""
    try:
        result = subprocess.run(
            ["admesh", "--check", stl_path],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            output = result.stdout + result.stderr
            return {
                "tool": "admesh",
                "available": True,
                "output": output,
                "manifold": "0 edges fixed" in output or "edges fixed" not in output,
            }
    except FileNotFoundError:
        return {"tool": "admesh", "available": False}
    except Exception as e:
        return {"tool": "admesh", "available": False, "error": str(e)}
    return {"tool": "admesh", "available": False}


def basic_stl_check(stl_path: str) -> dict:
    """Basic STL sanity checks when admesh is unavailable."""
    try:
        file_size = os.path.getsize(stl_path)
        file_size_kb = file_size / 1024

        with open(stl_path, "rb") as f:
            header = f.read(80)
            is_binary = not header.startswith(b"solid") or b"\x00" in header

        if is_binary:
            with open(stl_path, "rb") as f:
                f.seek(80)
                num_facets = int.from_bytes(f.read(4), "little")
        else:
            with open(stl_path, "r") as f:
                num_facets = f.read().count("facet normal")

        return {
            "tool": "basic_parser",
            "file_size_kb": round(file_size_kb, 1),
            "facets": num_facets,
            "is_binary": is_binary,
            "size_ok": file_size_kb >= MIN_STL_SIZE_KB,
            "facets_ok": num_facets > 100,
        }
    except Exception as e:
        return {"tool": "basic_parser", "error": str(e)}


def format_report(stl_path: str, results: dict, is_valid: bool) -> str:
    """Format mesh validation report."""
    lines = [
        "",
        "=== MESH INTEGRITY CHECK (P1 Governance) ===",
        f"STL: {Path(stl_path).name}",
        "",
    ]

    if results.get("tool") == "admesh" and results.get("available"):
        manifold = results.get("manifold", False)
        status = "PASS" if manifold else "BLOCKED"
        lines.append(f"Validator: admesh")
        lines.append(f"Manifold: {status}")
        if not manifold:
            lines.append("  [!] BLOCKED: Non-manifold mesh cannot be exported")
            lines.append("  [!] Fix geometry before proceeding")
    else:
        basic = results
        size_ok = basic.get("size_ok", False)
        facets_ok = basic.get("facets_ok", False)
        status = "PASS" if (size_ok and facets_ok) else "BLOCKED"

        lines.append(f"Validator: basic (admesh not available)")
        lines.append(f"File size: {basic.get('file_size_kb', '?')} KB (min {MIN_STL_SIZE_KB} KB)")
        lines.append(f"Facets: {basic.get('facets', '?')}")
        lines.append(f"Status: {status}")

        if not size_ok:
            lines.append("  [!] BLOCKED: STL file too small - geometry may be incomplete")
        if not facets_ok:
            lines.append("  [!] BLOCKED: Low facet count - geometry may be degenerate")

    if not is_valid:
        lines.append("")
        lines.append(">>> MESH VALIDATION FAILED - Edit blocked <<<")

    lines.append("")
    if results.get("tool") != "admesh" or not results.get("available"):
        lines.append("Install admesh for full mesh validation: apt install admesh")
        lines.append("")

    return "\n".join(lines)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_result = data.get("tool_result", {})

    # Only check after STL export via MCP
    if tool_name != "mcp__gcsc-openscad__export_stl":
        sys.exit(0)

    # Parse the result (it's JSON string from MCP)
    try:
        if isinstance(tool_result, str):
            result_data = json.loads(tool_result)
        else:
            result_data = tool_result
    except (json.JSONDecodeError, TypeError):
        sys.exit(0)

    # If export explicitly failed, let that error propagate (don't double-block)
    if not result_data.get("success"):
        sys.exit(0)

    # CRITICAL: If export "succeeded" but file is missing → BLOCK
    # This catches silent failures where export returns success but produces nothing
    stl_path = result_data.get("output_path", "")
    if not stl_path:
        print("BLOCKED: Export succeeded but no output_path in result", file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(stl_path):
        print(f"BLOCKED: Export succeeded but STL file missing: {stl_path}", file=sys.stderr)
        sys.exit(2)

    if os.path.getsize(stl_path) == 0:
        print(f"BLOCKED: Export succeeded but STL file is empty: {stl_path}", file=sys.stderr)
        sys.exit(2)

    # Run mesh validation with CANONICAL VALIDATOR POLICY:
    # - Authoritative: trimesh (preferred) or admesh
    # - Non-authoritative: basic_parser → ALWAYS FAIL
    # This prevents "works locally, fails in CI" due to different validators

    # Try trimesh first (more commonly available via pip)
    trimesh_result = validate_with_trimesh(stl_path)
    if trimesh_result.get("available"):
        results = trimesh_result
        # HARD GATES (block on failure):
        #   - watertight (manifold)
        #   - is_volume
        # SOFT GATES (warn only):
        #   - euler_number (valid volumes can have euler != 2 for multi-shell, cavities)
        is_watertight = results.get("manifold", False)
        is_volume = results.get("is_volume", False)
        euler = results.get("euler_number", 0)

        is_valid = is_watertight and is_volume

        print("")
        print("=== MESH INTEGRITY CHECK (P1 Governance) ===")
        print(f"STL: {Path(stl_path).name}")
        print("")
        print("Validator: trimesh (AUTHORITATIVE)")
        print(f"  Watertight: {is_watertight} {'PASS' if is_watertight else 'BLOCKED'}")
        print(f"  Is Volume: {is_volume} {'PASS' if is_volume else 'BLOCKED'}")
        print(f"  Euler Number: {euler} {'(typical for simple solid)' if euler == 2 else '(complex topology)'}")
        print(f"  Vertices: {results.get('vertices')}")
        print(f"  Faces: {results.get('faces')}")
        print(f"  Status: {'PASS' if is_valid else 'BLOCKED'}")

        # Euler warning (not blocking) for unexpected values
        if euler != 2 and is_valid:
            print(f"  [!] Note: Euler={euler} suggests multi-shell or cavity (verify intent)")

        print("")

        if not is_valid:
            print(">>> MESH VALIDATION FAILED <<<")
            print("BLOCKED: Mesh validation failed (trimesh: invalid topology)", file=sys.stderr)
            sys.exit(2)
        sys.exit(0)

    # Fall back to admesh
    admesh_result = validate_with_admesh(stl_path)
    if admesh_result.get("available"):
        results = admesh_result
        is_valid = results.get("manifold", False)
        report = format_report(stl_path, results, is_valid)
        print(report)

        if not is_valid:
            print("BLOCKED: Mesh validation failed (admesh: non-manifold)", file=sys.stderr)
            sys.exit(2)
        sys.exit(0)

    # NO authoritative validator available → FAIL
    # basic_parser is NOT authoritative and cannot approve meshes
    results = basic_stl_check(stl_path)
    print("")
    print("=== MESH INTEGRITY CHECK (P1 Governance) ===")
    print(f"STL: {Path(stl_path).name}")
    print("")
    print("Validator: NONE AVAILABLE")
    print("  [!] No authoritative validator found")
    print("")
    print("Basic parser metrics (NON-AUTHORITATIVE - cannot approve):")
    print(f"  File size: {results.get('file_size_kb', '?')} KB")
    print(f"  Facets: {results.get('facets', '?')}")
    print("")
    print(">>> BLOCKED: No authoritative mesh validator available <<<")
    print(">>> Install one of: <<<")
    print(">>>   pip install trimesh  (recommended) <<<")
    print(">>>   apt install admesh   (Linux) <<<")
    print("")
    print("BLOCKED: No authoritative validator (basic_parser cannot approve)", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
