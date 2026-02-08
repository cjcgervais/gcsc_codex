#!/usr/bin/env python3
"""GCSC2 BOSL2 Enforcement Hook (PreToolUse)

Blocks edits to Phase 2 hull files that use CSG primitives for primary
hull construction. Allows hull() for visualization/debug contexts.

Per CLAUDE.md Section 2.5 (FR-4) and Section 15:
  "Phase 2 geometry MUST use BOSL2"
  "Do not use hull() of spheres for Phase 2 hull construction"

Exit 0 = allow
Exit 2 = block
"""

import sys
import json
import re
import os

# Primary hull construction patterns (FORBIDDEN in Phase 2 hull modules)
FORBIDDEN_HULL_PATTERNS = [
    # hull() of spheres pattern (Phase 1 style)
    (r'hull\s*\(\s*\)\s*\{[^}]*sphere[^}]*sphere',
     "hull() of spheres pattern (Phase 1 style forbidden in Phase 2)"),
]

# Required patterns (MUST be present in Phase 2 hull modules)
REQUIRED_BOSL2_PATTERNS = [
    r'include\s*<.*BOSL2.*std\.scad\s*>',
    r'include\s*<.*lib/BOSL2/std\.scad\s*>',
    r'include\s*<BOSL2/std\.scad\s*>',
]

# Files that are primary hull modules in Phase 2
PHASE2_HULL_FILES = [
    "hull_bosl2.scad",
    "hull_v7_bosl2.scad",
    "hull_surface.scad",
    "hull_main.scad",
]


def check_content(content: str, file_path: str) -> str:
    """Check content for BOSL2 compliance. Returns error message or None."""
    file_path = file_path.replace("\\", "/")

    # Only check Phase 2 files
    if "02_Production_BOSL2" not in file_path:
        return None

    basename = os.path.basename(file_path)

    # Skip params files
    if "/params/" in file_path:
        return None

    # Skip non-hull files (frame files can use CSG)
    is_hull_file = (
        basename in PHASE2_HULL_FILES or
        ("hull" in basename.lower() and "frame" not in basename.lower())
    )

    if not is_hull_file:
        return None

    # Check for required BOSL2 include
    has_bosl2 = any(re.search(p, content) for p in REQUIRED_BOSL2_PATTERNS)
    if not has_bosl2:
        return (
            f"BLOCKED (FR-4): Phase 2 hull file '{basename}' missing BOSL2 include.\n"
            f"Add: include <lib/BOSL2/std.scad>\n"
            f"Phase 2 hull files MUST use BOSL2 for curved surfaces.\n"
            f"\n"
            f"Reference: CLAUDE.md Section 2.5 (Mandatory Functional Requirements)"
        )

    # Check for forbidden patterns
    for pattern, message in FORBIDDEN_HULL_PATTERNS:
        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            return (
                f"BLOCKED (FR-4): {message}\n"
                f"Use BOSL2 skin() for hull construction instead of CSG hull().\n"
                f"\n"
                f"Example:\n"
                f"  skin([section1, section2, section3], slices=0, refine=10);\n"
                f"\n"
                f"Reference: CLAUDE.md Section 15 (Phase 2 Development Guide)"
            )

    return None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        new_string = tool_input.get("new_string", "")

        # For edits, we need to check the result, not just new_string
        # Read current file and apply edit to check
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                current = f.read()
            old_string = tool_input.get("old_string", "")
            if old_string in current:
                result = current.replace(old_string, new_string, 1)
                error = check_content(result, file_path)
                if error:
                    print(error, file=sys.stderr)
                    sys.exit(2)
        except FileNotFoundError:
            # New file being created via Edit - check new_string
            error = check_content(new_string, file_path)
            if error:
                print(error, file=sys.stderr)
                sys.exit(2)

    elif tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")
        error = check_content(content, file_path)
        if error:
            print(error, file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
