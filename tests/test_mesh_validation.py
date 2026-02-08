#!/usr/bin/env python3
"""GCSC2 Mesh Validation Fixture Tests

Validates that mesh validation correctly identifies:
- Good fixtures: manifold, valid geometry
- Bad fixtures: non-manifold, degenerate geometry

This test ensures the governance system can catch geometry defects.

Usage:
    python tests/test_mesh_validation.py
    # or with pytest:
    pytest tests/test_mesh_validation.py -v
"""

import subprocess
import tempfile
import os
import sys
import re
from pathlib import Path

# Configuration
OPENSCAD_PATH = os.environ.get(
    "OPENSCAD_PATH",
    r"C:\Program Files\OpenSCAD\openscad.exe"
)

# Fallback for Linux CI
if not os.path.exists(OPENSCAD_PATH):
    OPENSCAD_PATH = "openscad"

PROJECT_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
FIXTURES_SPEC_PATH = FIXTURES_DIR / "FIXTURES_SPEC.json"


def load_fixtures_spec() -> dict:
    """Load the fixtures specification with expected metrics."""
    if FIXTURES_SPEC_PATH.exists():
        import json
        with open(FIXTURES_SPEC_PATH) as f:
            return json.load(f)
    return {"good": {}, "bad": {}}


def export_stl(scad_path: Path, stl_path: Path) -> bool:
    """Export a .scad file to STL using OpenSCAD."""
    try:
        result = subprocess.run(
            [OPENSCAD_PATH, "--render", "-o", str(stl_path), str(scad_path)],
            capture_output=True, text=True, timeout=120
        )
        return result.returncode == 0 and stl_path.exists()
    except Exception as e:
        print(f"Export failed: {e}")
        return False


def validate_mesh_admesh(stl_path: Path) -> dict:
    """Validate mesh using admesh."""
    try:
        command = ["admesh", "--check", str(stl_path)]
        result = subprocess.run(
            command,
            capture_output=True, text=True, timeout=60
        )
        output = result.stdout + result.stderr
        if result.returncode != 0 and "unrecognized option '--check'" in output:
            command = ["admesh", str(stl_path)]
            result = subprocess.run(
                command,
                capture_output=True, text=True, timeout=60
            )
            output = result.stdout + result.stderr

        # Parse key metrics from admesh output across output-format variants.
        lower = output.lower()
        edges_fixed = None
        degenerate_count = None

        edges_match = re.search(r"(\d+)\s+edges?\s+fixed", lower)
        if edges_match:
            edges_fixed = int(edges_match.group(1))
        else:
            edges_match_alt = re.search(r"edges?\s+fixed[^0-9]*(\d+)", lower)
            if edges_match_alt:
                edges_fixed = int(edges_match_alt.group(1))

        degenerate_match = re.search(r"(\d+)\s+degenerate", lower)
        if degenerate_match:
            degenerate_count = int(degenerate_match.group(1))
        else:
            degenerate_match_alt = re.search(r"degenerate[^0-9]*(\d+)", lower)
            if degenerate_match_alt:
                degenerate_count = int(degenerate_match_alt.group(1))

        is_manifold = True if edges_fixed is None else edges_fixed == 0
        has_degenerate = False if degenerate_count is None else degenerate_count > 0

        return {
            "tool": "admesh",
            "command": command,
            "available": True,
            "manifold": is_manifold,
            "degenerate": has_degenerate,
            "edges_fixed": edges_fixed,
            "degenerate_count": degenerate_count,
            "valid": is_manifold and not has_degenerate,
            "output": output[:500],
        }
    except FileNotFoundError:
        return {"tool": "admesh", "available": False}
    except Exception as e:
        return {"tool": "admesh", "available": False, "error": str(e)}


def validate_mesh_basic(stl_path: Path) -> dict:
    """Basic STL validation when admesh is unavailable."""
    try:
        file_size = stl_path.stat().st_size
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

        # Basic heuristics
        size_ok = file_size > 1000  # At least 1KB
        facets_ok = num_facets > 10  # At least some geometry

        return {
            "tool": "basic_parser",
            "available": True,
            "file_size": file_size,
            "facets": num_facets,
            "valid": size_ok and facets_ok,
        }
    except Exception as e:
        return {"tool": "basic_parser", "available": False, "error": str(e)}


def validate_mesh(stl_path: Path) -> dict:
    """Validate mesh, preferring admesh if available."""
    result = validate_mesh_admesh(stl_path)
    if result.get("available"):
        return result
    return validate_mesh_basic(stl_path)


def test_fixture(fixture_path: Path, expected_valid: bool, spec: dict = None) -> tuple[bool, str]:
    """Test a single fixture file against expected metrics.

    Args:
        fixture_path: Path to the .scad fixture file
        expected_valid: Whether the mesh should be valid
        spec: Optional dict with expected metrics from FIXTURES_SPEC.json

    Returns:
        (passed, message) tuple
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        stl_path = Path(tmpdir) / f"{fixture_path.stem}.stl"

        # Export to STL
        if not export_stl(fixture_path, stl_path):
            if not expected_valid:
                return (True, f"Export failed as expected (bad fixture)")
            return (False, f"Export failed unexpectedly")

        if not stl_path.exists() or stl_path.stat().st_size == 0:
            if not expected_valid:
                return (True, f"Empty STL as expected (bad fixture)")
            return (False, f"Empty or missing STL")

        # Validate mesh
        result = validate_mesh(stl_path)
        actual_valid = result.get("valid", False)

        # Check basic pass/fail
        if actual_valid != expected_valid:
            return (False, f"Expected valid={expected_valid}, got valid={actual_valid}")

        # If we have a spec, validate specific metrics
        if spec and result.get("tool") == "trimesh":
            issues = []

            # Check watertight
            if "watertight" in spec:
                if result.get("manifold") != spec["watertight"]:
                    issues.append(f"watertight: expected {spec['watertight']}, got {result.get('manifold')}")

            # Check is_volume
            if "is_volume" in spec:
                if result.get("is_volume") != spec["is_volume"]:
                    issues.append(f"is_volume: expected {spec['is_volume']}, got {result.get('is_volume')}")

            # Check euler_number
            if "euler_number" in spec:
                if result.get("euler_number") != spec["euler_number"]:
                    issues.append(f"euler: expected {spec['euler_number']}, got {result.get('euler_number')}")

            # Check facets_range
            if "facets_range" in spec:
                min_f, max_f = spec["facets_range"]
                actual_f = result.get("faces", 0)
                if not (min_f <= actual_f <= max_f):
                    issues.append(f"faces: {actual_f} not in range [{min_f}, {max_f}]")

            if issues:
                return (False, f"Metrics mismatch: {'; '.join(issues)}")

        status = "PASS" if expected_valid else "correctly REJECTED"
        return (True, f"{status} - {result.get('tool')}")


def run_tests() -> int:
    """Run all fixture tests."""
    print("=" * 60)
    print("GCSC2 Mesh Validation Fixture Tests")
    print("=" * 60)
    print()

    # Load fixture specifications
    fixtures_spec = load_fixtures_spec()
    good_specs = fixtures_spec.get("good", {})
    bad_specs = fixtures_spec.get("bad", {})

    passed = 0
    failed = 0

    # Test good fixtures (should be valid)
    good_dir = FIXTURES_DIR / "good"
    if good_dir.exists():
        print("Testing GOOD fixtures (expected: valid)")
        print("-" * 40)
        for fixture in good_dir.glob("*.scad"):
            spec = good_specs.get(fixture.name, {})
            success, message = test_fixture(fixture, expected_valid=True, spec=spec)
            status = "PASS" if success else "FAIL"
            print(f"  {status} {fixture.name}: {message}")
            if success:
                passed += 1
            else:
                failed += 1
        print()

    # Test bad fixtures (should be invalid)
    bad_dir = FIXTURES_DIR / "bad"
    if bad_dir.exists():
        print("Testing BAD fixtures (expected: invalid)")
        print("-" * 40)
        for fixture in bad_dir.glob("*.scad"):
            spec = bad_specs.get(fixture.name, {})
            success, message = test_fixture(fixture, expected_valid=False, spec=spec)
            status = "PASS" if success else "FAIL"
            print(f"  {status} {fixture.name}: {message}")
            if success:
                passed += 1
            else:
                failed += 1
        print()

    # Summary
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


# Pytest compatibility
def test_good_simple_cube():
    """Good fixture: simple cube should be valid."""
    fixture = FIXTURES_DIR / "good" / "simple_cube.scad"
    if fixture.exists():
        success, msg = test_fixture(fixture, expected_valid=True)
        assert success, msg


def test_good_hull_reference():
    """Good fixture: hull reference should be valid."""
    fixture = FIXTURES_DIR / "good" / "hull_reference.scad"
    if fixture.exists():
        success, msg = test_fixture(fixture, expected_valid=True)
        assert success, msg


def test_bad_open_surface():
    """Bad fixture: open surface should be invalid."""
    fixture = FIXTURES_DIR / "bad" / "open_surface.scad"
    if fixture.exists():
        success, msg = test_fixture(fixture, expected_valid=False)
        assert success, msg


def test_bad_zero_volume():
    """Bad fixture: zero volume should be invalid."""
    fixture = FIXTURES_DIR / "bad" / "zero_volume.scad"
    if fixture.exists():
        success, msg = test_fixture(fixture, expected_valid=False)
        assert success, msg


if __name__ == "__main__":
    sys.exit(run_tests())
