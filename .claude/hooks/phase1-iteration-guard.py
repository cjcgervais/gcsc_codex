#!/usr/bin/env python3
"""GCSC2 Phase 1 Iteration Guard Hook (PreToolUse)

Blocks major modifications to Phase 1 hull files. Per CLAUDE.md Section 2.6:
"Do not iterate on Phase 1 CSG. Proceed to Phase 2 BOSL2 implementation."

Phase 1 CSG primitives (hull() of spheres) cannot produce true curved surfaces.
Further iteration yields diminishing returns. The v6.1.0 failure proved this.

Small bug fixes (<500 chars) are allowed.

Exit 0 = allow
Exit 2 = block
"""

import sys
import json
import os

# Protected Phase 1 hull files (the primary geometry files)
PROTECTED_FILES = [
    "hull_simple.scad",
]

# Path markers for Phase 1 directory
PHASE1_PATH_MARKERS = [
    "01_Prototype_Simple",
]

# Allow small edits (bug fixes)
MAX_ALLOWED_CHANGE_SIZE = 500


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "").replace("\\", "/")
    basename = os.path.basename(file_path)

    # Check if editing protected Phase 1 files
    in_phase1 = any(marker in file_path for marker in PHASE1_PATH_MARKERS)

    if in_phase1 and basename in PROTECTED_FILES:
        # Check change size
        if tool_name == "Edit":
            change_size = len(tool_input.get("new_string", ""))
        else:
            # For Write, compare to current file size
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    current = f.read()
                new_content = tool_input.get("content", "")
                # Measure difference
                change_size = abs(len(new_content) - len(current))
            except FileNotFoundError:
                # New file - measure full content
                change_size = len(tool_input.get("content", ""))

        if change_size > MAX_ALLOWED_CHANGE_SIZE:
            print(
                f"BLOCKED: Major modification to Phase 1 hull file '{basename}'.\n"
                f"\n"
                f"Per CLAUDE.md Section 2.6 (Phase 1 Lessons Learned):\n"
                f'  "Do not iterate on Phase 1 CSG. Proceed to Phase 2 BOSL2."\n'
                f"\n"
                f"Phase 1 CSG primitives (hull() of spheres) CANNOT produce true\n"
                f"curved surfaces. Further iteration yields diminishing returns.\n"
                f"\n"
                f"The v6.1.0 'Beautiful Hull' scored 95/100 but FAILED human\n"
                f"verification. This proves Phase 1 CSG has reached its limits.\n"
                f"\n"
                f"RECOMMENDED: Work in 02_Production_BOSL2/ with BOSL2 skin()\n"
                f"\n"
                f"Small bug fixes (<{MAX_ALLOWED_CHANGE_SIZE} chars) are allowed.\n"
                f"Your change: {change_size} chars",
                file=sys.stderr
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
