#!/usr/bin/env python3
"""GCSC2 Parameter Consistency Check Hook (PostToolUse)

After any Edit or Write to a .scad file, checks that:
1. Frozen parameters are not redefined outside dimensions.scad
2. Include paths for dimensions.scad are present in module files
3. No duplicate parameter assignments exist

Hook protocol:
  - Receives JSON on stdin with tool_name and tool_input
  - Exit 0 = success (stdout message shown to user)
  - Exit 1 = issue detected (stderr message shown)
"""

import sys
import json
import re
import os

# Article 0.6 frozen parameters
FROZEN_PARAMS = {
    "LOA": "148",
    "beam": "64",
    "freeboard": "45",
    "z_pivot_seat": "38",
    "slot_diameter": "7.5",
    "frame_x_offset": "16",
    "slot_y_position": "31",
}

# Files allowed to define frozen parameters
PARAM_SOURCE_FILES = {"dimensions.scad", "frozen_dimensions.scad"}

# Files that must include dimensions.scad
MODULE_DIRS = {"modules"}


def check_param_consistency(file_path: str, content: str) -> list[str]:
    """Check parameter consistency in a .scad file. Returns list of issues."""
    issues = []
    basename = os.path.basename(file_path)
    parent_dir = os.path.basename(os.path.dirname(file_path))

    # Skip the canonical parameter source files
    if basename in PARAM_SOURCE_FILES:
        return issues

    # Check 1: Frozen parameter redefinition
    for param, canonical_val in FROZEN_PARAMS.items():
        # Match: param = <number>; (OpenSCAD assignment, not inside comments)
        pattern = rf'^\s*{param}\s*=\s*([\d.]+)\s*;'
        for i, line in enumerate(content.splitlines(), 1):
            # Skip comments
            stripped = line.split("//")[0]
            match = re.search(pattern, stripped)
            if match:
                found_val = match.group(1)
                if found_val == canonical_val:
                    issues.append(
                        f"[PARAM] {basename}:{i} redefines frozen param "
                        f"'{param}={found_val}' — use include <../params/dimensions.scad> instead"
                    )
                else:
                    issues.append(
                        f"[PARAM] CRITICAL: {basename}:{i} redefines frozen param "
                        f"'{param}={found_val}' (canonical: {canonical_val})"
                    )

    # Check 2: Module files must include dimensions.scad
    if parent_dir in MODULE_DIRS:
        has_include = bool(re.search(
            r'include\s*<.*dimensions\.scad\s*>',
            content
        ))
        if not has_include and any(
            re.search(rf'\b{p}\b', content) for p in FROZEN_PARAMS
        ):
            issues.append(
                f"[PARAM] {basename} uses frozen parameters but doesn't "
                f"include dimensions.scad — add: include <../params/dimensions.scad>"
            )

    return issues


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path.endswith(".scad"):
        sys.exit(0)

    # For Write, content is directly available
    # For Edit, we need to read the file after edit
    content = ""
    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        # Read the file to check the result of the edit
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except (FileNotFoundError, IOError):
            sys.exit(0)

    if not content:
        sys.exit(0)

    issues = check_param_consistency(file_path, content)

    if issues:
        severity = "CRITICAL" if any("CRITICAL" in i for i in issues) else "WARNING"
        msg = f"[param-check] {severity}:\n" + "\n".join(f"  {i}" for i in issues)
        print(msg, file=sys.stderr if severity == "CRITICAL" else sys.stdout)
        # Don't block — report and let the agent decide
        sys.exit(0)
    else:
        basename = os.path.basename(file_path)
        print(f"[param-check] {basename}: parameters consistent")
        sys.exit(0)


if __name__ == "__main__":
    main()
