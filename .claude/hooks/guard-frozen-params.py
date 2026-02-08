#!/usr/bin/env python3
"""GCSC2 Frozen Parameter Guard Hook (PreToolUse)

Blocks edits that would modify Article 0.6 frozen parameters.
These 7 parameters are constitutionally immutable:
  LOA=148, beam=64, freeboard=45, z_pivot_seat=38,
  slot_diameter=7.5, frame_x_offset=16, slot_y_position=31

SCOPE: ALL .scad files are checked for frozen parameter redefinitions.
This prevents circumvention by creating new param files. The hook:
  - BLOCKS assignment of frozen params to wrong values in ANY .scad file
  - ALLOWS assignment of frozen params to CORRECT values (redundant but safe)
  - ALLOWS USAGE of frozen params (e.g., width = LOA * 2;)
  - ALLOWS include/use statements that reference param files
  - IGNORES text inside comments (P3.1 fix: "// beam 9.6" won't trigger)

Hook protocol:
  - Receives JSON on stdin with tool_name and tool_input
  - Exit 0 = allow
  - Exit 2 = block (reason on stderr)
"""

import sys
import json
import re

# Article 0.6 frozen parameters and their canonical values
FROZEN_PARAMS = {
    "LOA": "148",
    "beam": "64",
    "freeboard": "45",
    "z_pivot_seat": "38",
    "slot_diameter": "7.5",
    "frame_x_offset": "16",
    "slot_y_position": "31",
}

# Canonical files for frozen parameters (for reference and special handling)
# Note: Protection now extends to ALL .scad files, not just these
CANONICAL_PARAM_FILES = [
    "frozen_dimensions.scad",  # Must contain ALL frozen params with correct values
    "dimensions.scad",         # Primary param source in each phase
]


def strip_comments(text: str) -> str:
    """Remove OpenSCAD comments from text to avoid false positives.

    P3.1 Fix: Comments like "// beam 9.6" were triggering false blocks.
    """
    # Remove single-line comments (// ...)
    text = re.sub(r'//[^\n]*', '', text)
    # Remove multi-line comments (/* ... */)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    return text


def check_edit(tool_input: dict) -> str | None:
    """Check if an edit would modify frozen parameters. Returns reason or None."""
    file_path = tool_input.get("file_path", "")
    new_string = tool_input.get("new_string", "")
    old_string = tool_input.get("old_string", "")

    # Check ALL .scad files for frozen parameter redefinitions
    # This prevents circumvention by creating alternate param files
    if not file_path.endswith('.scad'):
        return None  # Only check .scad files

    # P3.1 Fix: Strip comments to avoid matching text in comments
    new_string_code = strip_comments(new_string)
    old_string_code = strip_comments(old_string)

    # Check if the edit introduces or modifies any frozen parameter assignment
    for param, canonical_value in FROZEN_PARAMS.items():
        # Pattern: param = <number> (OpenSCAD assignment, with or without semicolon)
        # This matches "LOA = 200" but NOT "width = LOA * 2" (usage, not assignment)
        pattern = rf'\b{param}\s*=\s*([\d.]+)'

        old_matches = re.findall(pattern, old_string_code)
        new_matches = re.findall(pattern, new_string_code)

        if not old_matches and not new_matches:
            continue

        # Case 1: NEW assignment of frozen param with WRONG value
        # (Catches creating new files or adding params to existing files)
        if not old_matches and new_matches:
            for new_val in new_matches:
                if new_val != canonical_value:
                    return (
                        f"BLOCKED: Article 0.6 frozen parameter '{param}' "
                        f"cannot be assigned value {new_val}. The canonical "
                        f"value is {canonical_value}. These parameters are "
                        f"constitutionally immutable per GCSC2_Constitution.md."
                    )

        # Case 2: CHANGING a frozen param from correct to wrong value
        for old_val in old_matches:
            if old_val == canonical_value:
                # The old string has the canonical value — check if new changes it
                for new_val in new_matches:
                    if new_val != canonical_value:
                        return (
                            f"BLOCKED: Article 0.6 frozen parameter '{param}' "
                            f"cannot be changed from {canonical_value} to "
                            f"{new_val}. These parameters are "
                            f"constitutionally immutable per GCSC2_Constitution.md."
                        )

        # Case 3: REMOVING a frozen param from a canonical file
        # Only block removal from canonical param files, not other .scad files
        basename = file_path.replace("\\", "/").split("/")[-1] if file_path else ""
        if old_matches and not new_matches and basename in CANONICAL_PARAM_FILES:
            return (
                f"BLOCKED: Article 0.6 frozen parameter '{param}' "
                f"cannot be removed from {basename}. These parameters are "
                f"constitutionally immutable per GCSC2_Constitution.md."
            )

    return None


def check_write(tool_input: dict) -> str | None:
    """Check if a file write would introduce wrong frozen parameter values."""
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    # Only check .scad files
    if not file_path.endswith('.scad'):
        return None

    basename = file_path.replace("\\", "/").split("/")[-1] if file_path else ""

    # P3.1 Fix: Strip comments to avoid matching text in comments
    content_code = strip_comments(content)

    # Special handling for frozen_dimensions.scad: MUST have ALL frozen params
    if basename == "frozen_dimensions.scad":
        for param, canonical_value in FROZEN_PARAMS.items():
            pattern = rf'\b{param}\s*=\s*{re.escape(canonical_value)}\s*;'
            if not re.search(pattern, content_code):
                # Check if param exists with wrong value
                wrong_pattern = rf'\b{param}\s*=\s*([\d.]+)\s*;'
                wrong_match = re.search(wrong_pattern, content_code)
                if wrong_match:
                    return (
                        f"BLOCKED: frozen_dimensions.scad write has {param}="
                        f"{wrong_match.group(1)} but Article 0.6 requires "
                        f"{param}={canonical_value}."
                    )
                else:
                    return (
                        f"BLOCKED: frozen_dimensions.scad write is missing "
                        f"frozen parameter {param}={canonical_value}."
                    )
        return None

    # For ALL other .scad files: block any frozen param with wrong value
    # This catches circumvention attempts (creating my_params.scad with LOA=200)
    for param, canonical_value in FROZEN_PARAMS.items():
        # Pattern matches assignment: "LOA = 200" but not usage: "width = LOA * 2"
        pattern = rf'\b{param}\s*=\s*([\d.]+)'
        match = re.search(pattern, content_code)
        if match:
            assigned_value = match.group(1)
            if assigned_value != canonical_value:
                return (
                    f"BLOCKED: Cannot assign {param}={assigned_value} in {basename}. "
                    f"Article 0.6 requires {param}={canonical_value}. "
                    f"Use 'include <params/dimensions.scad>' instead of redefining."
                )

    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # Can't parse input, allow by default

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    reason = None

    if tool_name == "Edit":
        reason = check_edit(tool_input)
    elif tool_name == "Write":
        reason = check_write(tool_input)

    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
