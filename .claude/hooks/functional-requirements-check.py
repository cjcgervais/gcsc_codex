#!/usr/bin/env python3
"""GCSC2 Functional Requirements Check Hook (PostToolUse)

Validates geometry changes against CANONICAL_DESIGN_REQUIREMENTS.md.
Runs after edits to hull/frame module files and Phase 2 directories.

This hook exists because v6.1.0 "Beautiful Hull" passed all automated skills
(95/100 eval score) but FAILED human verification due to:
  - V-keel making hull unstable (FR-1 violation)
  - Slot obstructions blocking ball insertion (FR-2 violation)
  - Flat freeboard cut losing canoe character (FR-3 violation)

Hook protocol:
  - Receives JSON on stdin with tool_name and tool_input
  - Exit 0 = allow (optionally print warnings)
  - Exit 2 = block on CRITICAL violations:
    - known regex criticals (for example slot rotation bug)
    - deterministic mechanics gate failures from reference_fit_report.json

Reference: CANONICAL_DESIGN_REQUIREMENTS.md
"""

import sys
import json
import re
import os
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple

# Directories and files where functional requirements apply
WATCHED_PATHS = [
    "modules/",              # Phase 1 hull/frame modules
    "02_Production_BOSL2/",  # Phase 2 BOSL2 implementation
    "codex_hull_lab/",       # Active codex hull lab geometry
]

# Specific files that contain hull/frame geometry
HULL_FILES = [
    "hull_simple.scad",
    "hull.scad",
    "hull_bosl2.scad",
]

FRAME_FILES = [
    "frame_simple.scad",
    "frame.scad",
    "frame_bosl2.scad",
]

SLOT_FILES = HULL_FILES  # Slots are in hull files


def _discover_project_root() -> Path:
    """Resolve project root from env override or repository-relative fallback."""
    env_root = os.environ.get("GCSC_PROJECT_ROOT", "").strip()
    if env_root:
        candidate = Path(env_root).expanduser()
        if candidate.exists():
            return candidate.resolve()
    # .claude/hooks/functional-requirements-check.py -> repo root is parents[2]
    return Path(__file__).resolve().parents[2]


def _read_report_max_age_hours() -> float:
    """Read max report age from env, defaulting to 72h if invalid."""
    raw = os.environ.get("GCSC_REFERENCE_REPORT_MAX_AGE_HOURS", "72").strip()
    try:
        value = float(raw)
        return max(0.0, value)
    except ValueError:
        return 72.0


PROJECT_ROOT = _discover_project_root()
DEFAULT_REFERENCE_FIT_REPORT = PROJECT_ROOT / "_codex" / "reports" / "reference_fit_report.json"
REFERENCE_REPORT_MAX_AGE_HOURS = _read_report_max_age_hours()

# =============================================================================
# FR-1: Flat Bottom Check
# =============================================================================

# Patterns that suggest V-keel or unstable bottom geometry
V_KEEL_PATTERNS = [
    # Excessive deadrise angle (>15 degrees makes unstable bottom)
    (r'deadrise_angle\s*=\s*([\d.]+)', "deadrise_angle", 15.0, "high"),
    # V-bottom or keel geometry that protrudes below flat base
    (r'keel_depth\s*=\s*([\d.]+)', "keel_depth", 0.0, "nonzero"),
    # Rocker that affects bottom stability (exaggerated rocker OK for bowl)
    (r'bottom_rocker\s*=\s*([\d.]+)', "bottom_rocker", 5.0, "high"),
]

# Code patterns that suggest unstable hull bottom
UNSTABLE_HULL_PATTERNS = [
    r'translate\s*\(\s*\[\s*0\s*,\s*0\s*,\s*-',  # Downward translation (possible keel)
    r'rotate\s*\(\s*\[\s*[\d.]+\s*,\s*0\s*,\s*0\s*\]\s*\)',  # Roll rotation at bottom
]


def check_fr1_flat_bottom(content: str, filename: str) -> List[str]:
    """Check for FR-1 violations: hull must sit flat on sink."""
    warnings = []

    for pattern, param_name, threshold, check_type in V_KEEL_PATTERNS:
        matches = re.finditer(pattern, content)
        for match in matches:
            try:
                value = float(match.group(1))
                if check_type == "high" and value > threshold:
                    warnings.append(
                        f"FR-1 RISK: {param_name}={value} may prevent hull from sitting flat. "
                        f"Values >{threshold} can create unstable V-keel geometry."
                    )
                elif check_type == "nonzero" and value > 0:
                    warnings.append(
                        f"FR-1 RISK: {param_name}={value} adds keel protrusion. "
                        f"Hull must have flat bottom for sink stability."
                    )
            except ValueError:
                pass

    # Check for structural patterns that suggest keel geometry
    for pattern in UNSTABLE_HULL_PATTERNS:
        if re.search(pattern, content):
            # Only warn if in hull geometry context
            if "hull" in filename.lower() or "keel" in content.lower():
                warnings.append(
                    f"FR-1 ADVISORY: Detected geometry transformation that may affect bottom flatness. "
                    f"Verify hull sits stably on flat surface."
                )
                break

    return warnings


# =============================================================================
# FR-2: Ball Insertion Path Check
# =============================================================================

# Patterns that might indicate slot obstructions
SLOT_OBSTRUCTION_PATTERNS = [
    # Anything that might block the vertical insertion path
    (r'slot.*difference\s*\(\s*\)', "difference() in slot context"),
    (r'slot.*intersection\s*\(\s*\)', "intersection() in slot context"),
    # Slot diameter being reduced
    (r'slot_diameter\s*-\s*([\d.]+)', "slot diameter reduction"),
    # Slot being shortened or having internal geometry
    (r'slot.*cube\s*\(\s*\[', "cube geometry in slot context"),
]

# Slot clearance checks
SLOT_CLEARANCE_PARAMS = [
    (r'slot_clearance\s*=\s*([\d.]+)', "slot_clearance", 0.25, "low"),
    (r'ball_clearance\s*=\s*([\d.]+)', "ball_clearance", 0.25, "low"),
]


def check_fr2_ball_insertion(content: str, filename: str) -> List[str]:
    """Check for FR-2 violations: frame balls must be insertable from above."""
    warnings = []

    # Check if this file modifies slot geometry
    if "slot" not in content.lower() and filename not in SLOT_FILES:
        return warnings

    # Look for patterns that might obstruct slot
    for pattern, description in SLOT_OBSTRUCTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            warnings.append(
                f"FR-2 ADVISORY: {description} detected. "
                f"Verify clear vertical path from slot top to hemisphere seat."
            )

    # Check clearance values
    for pattern, param_name, min_val, check_type in SLOT_CLEARANCE_PARAMS:
        matches = re.finditer(pattern, content)
        for match in matches:
            try:
                value = float(match.group(1))
                if check_type == "low" and value < min_val:
                    warnings.append(
                        f"FR-2 RISK: {param_name}={value}mm is tight. "
                        f"Minimum {min_val}mm recommended for reliable ball insertion."
                    )
            except ValueError:
                pass

    # Check for the known slot rotation bug (critical!)
    if re.search(r'pivot_slot.*rotate\s*\(\s*\[\s*0\s*,\s*90\s*,\s*0\s*\]', content, re.DOTALL):
        warnings.append(
            "FR-2 CRITICAL: Possible slot rotation bug detected! "
            "rotate([0,90,0]) creates fore/aft orientation (BROKEN). "
            "Use rotate([90,0,0]) for port/starboard orientation (CORRECT)."
        )

    return warnings


# =============================================================================
# FR-3: Curved Gunwale Check
# =============================================================================

# Patterns that suggest flat freeboard cut
FLAT_FREEBOARD_PATTERNS = [
    # Constant Z plane cut without curve
    (r'difference\s*\(\s*\).*translate\s*\(\s*\[\s*0\s*,\s*0\s*,\s*freeboard',
     "flat freeboard plane cut"),
    # Hull top created by simple cube intersection
    (r'intersection\s*\(\s*\).*cube.*freeboard',
     "cube intersection at freeboard"),
]

# Parameters that indicate proper sheer curve
SHEER_PARAMS = [
    (r'sheer_rise\s*=\s*([\d.]+)', "sheer_rise", 10.0, "low"),
    (r'bow_rise\s*=\s*([\d.]+)', "bow_rise", 5.0, "low"),
    (r'stern_rise\s*=\s*([\d.]+)', "stern_rise", 5.0, "low"),
    (r'gunwale_curve\s*=\s*([\d.]+)', "gunwale_curve", 5.0, "low"),
]


def check_fr3_curved_gunwale(content: str, filename: str) -> List[str]:
    """Check for FR-3 violations: gunwale must curve up at bow/stern."""
    warnings = []

    # Only check hull-related files
    if filename not in HULL_FILES and "hull" not in filename.lower():
        return warnings

    # Check for flat freeboard patterns
    for pattern, description in FLAT_FREEBOARD_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
            warnings.append(
                f"FR-3 RISK: {description} may create flat-topped hull. "
                f"Canoe gunwale must curve upward at bow and stern."
            )

    # Check sheer parameters
    has_sheer = False
    for pattern, param_name, min_val, check_type in SHEER_PARAMS:
        matches = re.finditer(pattern, content)
        for match in matches:
            has_sheer = True
            try:
                value = float(match.group(1))
                if check_type == "low" and value < min_val:
                    warnings.append(
                        f"FR-3 ADVISORY: {param_name}={value}mm is subtle. "
                        f"Consider {min_val}+ mm for recognizable canoe sheer line."
                    )
            except ValueError:
                pass

    # If modifying hull and no sheer parameters found, warn
    if not has_sheer and "freeboard" in content and "hull" in content.lower():
        warnings.append(
            "FR-3 ADVISORY: No sheer rise parameters detected in hull definition. "
            "Canoe hulls need curved gunwale (sheer line) rising at bow/stern."
        )

    return warnings


# =============================================================================
# FR-4: BOSL2 Check (Phase 2 only)
# =============================================================================

def check_fr4_bosl2(content: str, file_path: str) -> List[str]:
    """Check for FR-4: Phase 2 must use BOSL2 for curved surfaces."""
    warnings = []

    # Only check Phase 2 files
    if "02_Production_BOSL2" not in file_path:
        return warnings

    # Check for BOSL2 include
    has_bosl2 = bool(re.search(r'include\s*<.*BOSL2', content))

    # Check for CSG primitives that should be replaced with BOSL2
    csg_primitives = [
        (r'\bhull\s*\(\s*\)', "hull()"),
        (r'\bsphere\s*\(\s*r\s*=', "sphere()"),
        (r'\bcylinder\s*\(', "cylinder()"),
    ]

    if not has_bosl2:
        for pattern, primitive in csg_primitives:
            if re.search(pattern, content):
                warnings.append(
                    f"FR-4 ADVISORY: {primitive} detected in Phase 2 without BOSL2 include. "
                    f"Phase 2 designs should use BOSL2 skin(), path_sweep(), etc. for curved surfaces."
                )
                break

    return warnings


# =============================================================================
# Deterministic Mechanics Report Check
# =============================================================================

def resolve_file_path(file_path: str) -> Path:
    """Resolve tool-provided file path against repository root when needed."""
    path = Path(file_path)
    if path.is_absolute():
        return path.resolve()
    return (PROJECT_ROOT / path).resolve()


def resolve_reference_fit_report_path() -> Path:
    """Resolve deterministic mechanics report path, honoring env override."""
    override = os.environ.get("GCSC_REFERENCE_FIT_REPORT", "").strip()
    if override:
        override_path = Path(override).expanduser()
        if not override_path.is_absolute():
            override_path = PROJECT_ROOT / override_path
        return override_path.resolve()
    return DEFAULT_REFERENCE_FIT_REPORT.resolve()


def _normalized_path(path_value: str) -> str:
    """Normalize path text for case-insensitive project-root comparisons."""
    try:
        return Path(path_value).expanduser().resolve().as_posix().lower()
    except OSError:
        return Path(path_value).as_posix().lower()


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_mm(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f} mm"


def load_reference_fit_report(report_path: Path) -> Tuple[Optional[dict], Optional[str]]:
    """Load deterministic mechanics report JSON if present."""
    if not report_path.exists():
        return None, None

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, (
            "MECHANICS ADVISORY: Failed to parse deterministic mechanics report at "
            f"{report_path}: {exc}"
        )

    if not isinstance(report, dict):
        return None, (
            "MECHANICS ADVISORY: Deterministic mechanics report is not a JSON object. "
            "Re-run verify_reference_fit.py."
        )

    return report, None


def reference_report_is_fresh(report: dict, report_path: Path, edited_path: Path) -> bool:
    """Use only fresh report output to avoid stale false blocks."""
    try:
        report_mtime = report_path.stat().st_mtime
    except OSError:
        return False

    if REFERENCE_REPORT_MAX_AGE_HOURS > 0.0:
        age_seconds = max(0.0, time.time() - report_mtime)
        if age_seconds > (REFERENCE_REPORT_MAX_AGE_HOURS * 3600.0):
            return False

    if edited_path.exists():
        try:
            if report_mtime < edited_path.stat().st_mtime:
                return False
        except OSError:
            return False

    inputs = report.get("inputs")
    report_root = ""
    if isinstance(inputs, dict):
        raw_root = inputs.get("project_root")
        if isinstance(raw_root, str):
            report_root = raw_root.strip()

    if report_root:
        if _normalized_path(report_root) != _normalized_path(str(PROJECT_ROOT)):
            return False

    return True


def _min_measurement(items: Any, key: str) -> Optional[float]:
    values: List[float] = []
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            value = _safe_float(item.get(key))
            if value is not None:
                values.append(value)
    if not values:
        return None
    return min(values)


def _max_measurement(items: Any, key: str) -> Optional[float]:
    values: List[float] = []
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            value = _safe_float(item.get(key))
            if value is not None:
                values.append(value)
    if not values:
        return None
    return max(values)


def check_deterministic_mechanics(file_path: str) -> List[str]:
    """Consume deterministic mechanics report and hard-block known key failures."""
    warnings: List[str] = []
    report_path = resolve_reference_fit_report_path()

    report, advisory = load_reference_fit_report(report_path)
    if advisory:
        warnings.append(advisory)
        return warnings

    if report is None:
        return warnings

    edited_path = resolve_file_path(file_path)
    if not reference_report_is_fresh(report, report_path, edited_path):
        return warnings

    gates = report.get("gates")
    measurements = report.get("measurements")
    thresholds = report.get("thresholds")

    if not isinstance(gates, dict):
        warnings.append(
            "MECHANICS ADVISORY: Deterministic mechanics report missing `gates`. "
            "Re-run verify_reference_fit.py."
        )
        return warnings
    if not isinstance(measurements, dict):
        measurements = {}
    if not isinstance(thresholds, dict):
        thresholds = {}

    if gates.get("slot_insertion_corridor") is False:
        min_corridor = _min_measurement(
            measurements.get("slot_checks"),
            "corridor_min_radial_clearance_mm",
        )
        corridor_threshold = _safe_float(thresholds.get("corridor_radial_clearance_min_mm"))
        warnings.append(
            "MECHANICS CRITICAL: Deterministic gate `slot_insertion_corridor` failed "
            f"(min radial clearance {_format_mm(min_corridor)}, "
            f"threshold {_format_mm(corridor_threshold)})."
        )

    if gates.get("frame_interference") is False:
        min_gap = _min_measurement(measurements.get("frame_checks"), "min_gap_mm")
        max_penetration = _max_measurement(measurements.get("frame_checks"), "max_penetration_mm")
        min_gap_threshold = _safe_float(thresholds.get("frame_min_gap_mm"))
        penetration_threshold = _safe_float(thresholds.get("frame_penetration_max_mm"))
        warnings.append(
            "MECHANICS CRITICAL: Deterministic gate `frame_interference` failed "
            f"(min gap {_format_mm(min_gap)} vs {_format_mm(min_gap_threshold)}, "
            f"max penetration {_format_mm(max_penetration)} vs {_format_mm(penetration_threshold)})."
        )

    if gates.get("frame_floor_clearance") is False:
        measured_floor = _safe_float(measurements.get("overall_floor_clearance_min_mm"))
        floor_threshold = _safe_float(thresholds.get("floor_clearance_min_mm"))
        warnings.append(
            "MECHANICS CRITICAL: Deterministic gate `frame_floor_clearance` failed "
            f"(measured {_format_mm(measured_floor)}, threshold {_format_mm(floor_threshold)})."
        )

    if any("MECHANICS CRITICAL" in warning for warning in warnings):
        warnings.append(
            "MECHANICS ADVISORY: Re-run `python codex_hull_lab/tools/verify_reference_fit.py "
            "--output-json _codex/reports/reference_fit_report.json` after geometry fixes."
        )

    return warnings


# =============================================================================
# Main Hook Logic
# =============================================================================

def is_watched_file(file_path: str) -> bool:
    """Check if this file should be validated for functional requirements."""
    # Normalize path separators
    normalized = file_path.replace("\\", "/").lower()

    # Check if in watched paths
    for watched in WATCHED_PATHS:
        if watched.lower() in normalized:
            return True

    # Check if it's a known hull/frame file
    basename = os.path.basename(normalized)
    if basename in HULL_FILES or basename in FRAME_FILES:
        return True

    return False


def run_checks(content: str, file_path: str) -> List[str]:
    """Run all functional requirement checks."""
    filename = os.path.basename(file_path)
    all_warnings = []

    all_warnings.extend(check_fr1_flat_bottom(content, filename))
    all_warnings.extend(check_fr2_ball_insertion(content, filename))
    all_warnings.extend(check_fr3_curved_gunwale(content, filename))
    all_warnings.extend(check_fr4_bosl2(content, file_path))
    all_warnings.extend(check_deterministic_mechanics(file_path))

    return all_warnings


def format_output(warnings: List[str], filename: str) -> str:
    """Format warnings for display."""
    if not warnings:
        return ""

    lines = [
        "",
        "=== FUNCTIONAL REQUIREMENTS CHECK ===",
        f"File: {filename}",
        "Reference: CANONICAL_DESIGN_REQUIREMENTS.md",
        "",
    ]

    # Group by severity
    critical = [w for w in warnings if "CRITICAL" in w]
    risks = [w for w in warnings if "RISK" in w and "CRITICAL" not in w]
    advisories = [w for w in warnings if "ADVISORY" in w]

    if critical:
        lines.append("CRITICAL ISSUES (likely failures):")
        for w in critical:
            lines.append(f"  [X] {w}")
        lines.append("")

    if risks:
        lines.append("RISKS (may cause failures):")
        for w in risks:
            lines.append(f"  [!] {w}")
        lines.append("")

    if advisories:
        lines.append("ADVISORIES (verify manually):")
        for w in advisories:
            lines.append(f"  [?] {w}")
        lines.append("")

    lines.extend([
        "The Soap Dish Test:",
        "  1. Sits flat on sink?   (FR-1)",
        "  2. Frame insertable?    (FR-2)",
        "  3. Looks like canoe?    (FR-3)",
        "",
        "Run /verify for full visual verification",
        "",
    ])

    return "\n".join(lines)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only check after Edit or Write
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path.endswith(".scad"):
        sys.exit(0)

    # Check if this file needs functional requirements validation
    if not is_watched_file(file_path):
        sys.exit(0)

    resolved_file_path = resolve_file_path(file_path)

    # Get content
    content = ""
    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        try:
            with open(resolved_file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (FileNotFoundError, IOError):
            sys.exit(0)

    if not content:
        sys.exit(0)

    # Run checks
    warnings = run_checks(content, str(resolved_file_path))

    # Output results
    if warnings:
        output = format_output(warnings, resolved_file_path.name)
        print(output)

    # Check for critical FR violations - these BLOCK the operation
    # Advisory warnings (ADVISORY, RISK) still pass through
    critical_violations = [w for w in warnings if "CRITICAL" in w]
    if critical_violations:
        # Critical FR violation detected - BLOCK
        print(
            "\n" + "=" * 60,
            "BLOCKED: Critical Functional Requirement Violation",
            "=" * 60,
            "",
            sep="\n",
            file=sys.stderr
        )
        for v in critical_violations:
            print(f"  [X] {v}", file=sys.stderr)
        print(
            "",
            "This edit would violate mandatory functional requirements",
            "or deterministic mechanics gates.",
            "Reference: CANONICAL_DESIGN_REQUIREMENTS.md",
            "",
            "The v6.1.0 'Beautiful Hull' passed all automated skills (95/100)",
            "but FAILED human verification due to FR violations.",
            "",
            "Fix the critical issue before proceeding.",
            sep="\n",
            file=sys.stderr
        )
        sys.exit(2)

    # Non-critical warnings pass through (ADVISORY, RISK)
    sys.exit(0)


if __name__ == "__main__":
    main()
