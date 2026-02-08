#!/usr/bin/env python3
"""GCSC2 Aesthetic Consistency Check Hook (PostToolUse)

Validates aesthetic parameter changes against design research guidelines.
Runs after edits to hull-related .scad files.

Hook protocol:
  - Receives JSON on stdin with tool_name and tool_input
  - Exit 0 = allow (optionally print recommendations)
  - Exit 2 = block (reason on stderr)

This hook provides RECOMMENDATIONS, not hard blocks (unlike frozen params).
"""

import sys
import json
import re
from typing import Optional, Dict, List, Tuple

# Aesthetic guideline ranges (from research documents)
AESTHETIC_GUIDELINES = {
    # Sheer line guidance
    "sheer_rise": {
        "min": 10,
        "max": 30,
        "optimal": 25,
        "unit": "mm",
        "guidance": "Sheer rise should be 10-25% of freeboard for dramatic but authentic canoe profile"
    },
    # Tumblehome guidance
    "tumblehome_angle": {
        "min": 5,
        "max": 12,
        "optimal": 10,
        "unit": "degrees",
        "guidance": "Tumblehome 5-12 degrees creates elegant inward curve without stability loss"
    },
    # Deadrise guidance
    "deadrise_angle": {
        "min": 8,
        "max": 15,
        "optimal": 12,
        "unit": "degrees",
        "guidance": "Deadrise 8-15 degrees provides shallow V character"
    },
    # Keel rocker (highly exaggerated for soap bowl function)
    "keel_rocker": {
        "min": 35,
        "max": 50,
        "optimal": 45,
        "unit": "mm",
        "guidance": "Rocker is exaggerated for soap bowl function (not authentic canoe proportions)"
    },
    # Wall thickness
    "wall_thickness": {
        "min": 5,
        "max": 8,
        "optimal": 6,
        "unit": "mm",
        "guidance": "Wall thickness 5-8mm balances structural integrity with visual refinement"
    },
    # Rail dimensions
    "rail_thickness": {
        "min": 3,
        "max": 5,
        "optimal": 4,
        "unit": "mm",
        "guidance": "Rail thickness 3-5mm provides adequate visual weight for frame"
    },
    "rail_vertical_height": {
        "min": 5,
        "max": 8,
        "optimal": 7,
        "unit": "mm",
        "guidance": "Rail height 5-8mm creates visible cradle structure"
    }
}

# Files that contain aesthetic parameters
AESTHETIC_FILES = [
    "dimensions.scad",
    "hull_simple.scad",
    "frame_simple.scad",
    "design_parameters.scad"
]


def extract_parameter_changes(content: str) -> Dict[str, float]:
    """Extract parameter assignments from OpenSCAD content."""
    params = {}
    # Match: param_name = value; (OpenSCAD assignment)
    pattern = r'(\w+)\s*=\s*([\d.]+)\s*;'
    for match in re.finditer(pattern, content):
        param_name = match.group(1)
        try:
            param_value = float(match.group(2))
            params[param_name] = param_value
        except ValueError:
            pass
    return params


def check_aesthetic_guidelines(params: Dict[str, float]) -> List[Tuple[str, str, str]]:
    """Check parameters against aesthetic guidelines.

    Returns list of (param_name, severity, message) tuples.
    Severity: "info", "warning", "suggestion"
    """
    findings = []

    for param_name, value in params.items():
        if param_name not in AESTHETIC_GUIDELINES:
            continue

        guide = AESTHETIC_GUIDELINES[param_name]
        min_val = guide["min"]
        max_val = guide["max"]
        optimal = guide["optimal"]
        unit = guide["unit"]
        guidance = guide["guidance"]

        # Check if outside recommended range
        if value < min_val:
            findings.append((
                param_name,
                "warning",
                f"{param_name}={value}{unit} is below aesthetic minimum ({min_val}{unit}). "
                f"{guidance}"
            ))
        elif value > max_val:
            findings.append((
                param_name,
                "warning",
                f"{param_name}={value}{unit} exceeds aesthetic maximum ({max_val}{unit}). "
                f"{guidance}"
            ))
        elif abs(value - optimal) > (max_val - min_val) * 0.3:
            # More than 30% away from optimal within range
            findings.append((
                param_name,
                "suggestion",
                f"{param_name}={value}{unit} — consider {optimal}{unit} for optimal aesthetics. "
                f"{guidance}"
            ))

    return findings


def check_edit(tool_input: dict) -> Optional[str]:
    """Check an edit operation for aesthetic implications."""
    file_path = tool_input.get("file_path", "")
    new_string = tool_input.get("new_string", "")

    # Only check aesthetic-related files
    basename = file_path.replace("\\", "/").split("/")[-1] if file_path else ""
    if basename not in AESTHETIC_FILES:
        return None

    # Extract parameter changes from new content
    params = extract_parameter_changes(new_string)
    if not params:
        return None

    # Check against guidelines
    findings = check_aesthetic_guidelines(params)
    if not findings:
        return None

    # Format output as recommendations (not blocks)
    output_lines = ["\n=== AESTHETIC CONSISTENCY CHECK ==="]

    warnings = [f for f in findings if f[1] == "warning"]
    suggestions = [f for f in findings if f[1] == "suggestion"]

    if warnings:
        output_lines.append("\nWARNINGS (outside recommended range):")
        for param, _, msg in warnings:
            output_lines.append(f"  [!] {msg}")

    if suggestions:
        output_lines.append("\nSUGGESTIONS (optimization opportunities):")
        for param, _, msg in suggestions:
            output_lines.append(f"  [~] {msg}")

    output_lines.append("\nReference: docs/CANOE_HULL_AESTHETICS_GUIDE.md")
    output_lines.append("Run /aesthetic hull for full assessment")
    output_lines.append("")

    return "\n".join(output_lines)


def check_write(tool_input: dict) -> Optional[str]:
    """Check a write operation for aesthetic implications."""
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    basename = file_path.replace("\\", "/").split("/")[-1] if file_path else ""
    if basename not in AESTHETIC_FILES:
        return None

    params = extract_parameter_changes(content)
    if not params:
        return None

    findings = check_aesthetic_guidelines(params)
    if not findings:
        return None

    # Same output formatting as check_edit
    output_lines = ["\n=== AESTHETIC CONSISTENCY CHECK ==="]

    warnings = [f for f in findings if f[1] == "warning"]
    suggestions = [f for f in findings if f[1] == "suggestion"]

    if warnings:
        output_lines.append("\nWARNINGS (outside recommended range):")
        for param, _, msg in warnings:
            output_lines.append(f"  [!] {msg}")

    if suggestions:
        output_lines.append("\nSUGGESTIONS (optimization opportunities):")
        for param, _, msg in suggestions:
            output_lines.append(f"  [~] {msg}")

    output_lines.append("\nReference: docs/CANOE_HULL_AESTHETICS_GUIDE.md")
    output_lines.append("Run /aesthetic hull for full assessment")
    output_lines.append("")

    return "\n".join(output_lines)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # Can't parse input, allow by default

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    output = None

    if tool_name == "Edit":
        output = check_edit(tool_input)
    elif tool_name == "Write":
        output = check_write(tool_input)

    if output:
        # Print recommendations to stdout (informational, not blocking)
        print(output)

    # Always exit 0 - this hook provides guidance, not hard blocks
    # Only frozen parameters are blocked (by guard-frozen-params.py)
    sys.exit(0)


if __name__ == "__main__":
    main()
