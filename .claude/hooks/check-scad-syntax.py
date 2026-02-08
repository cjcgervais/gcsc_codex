#!/usr/bin/env python3
"""GCSC2 OpenSCAD Syntax Check Hook (PostToolUse)

After any Edit or Write to a .scad file, runs a fast syntax check
using OpenSCAD's .csg export (CSG tree only, no geometry computation).

Catches syntax errors, undefined variables, and missing includes
immediately — before a full render attempt wastes time.

Hook protocol:
  - Receives JSON on stdin with tool_name and tool_input
  - Exit 0 = success (stdout message shown to user)
  - Exit 1 = syntax error detected (stderr message shown)
"""

import sys
import json
import subprocess
import tempfile
import os
from pathlib import Path

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
    # .claude/hooks/check-scad-syntax.py -> repo root is parents[2]
    return str(Path(__file__).resolve().parents[2])


PROJECT_ROOT = _discover_project_root()


def check_syntax(scad_path: str) -> tuple[bool, str]:
    """Run fast syntax check via .csg export. Returns (ok, message)."""
    if not os.path.exists(scad_path):
        return True, ""  # File doesn't exist yet, skip

    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".csg")
    os.close(tmp_fd)

    try:
        result = subprocess.run(
            [OPENSCAD_PATH, "-o", tmp_path, scad_path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=PROJECT_ROOT,
        )

        if result.returncode == 0:
            # Extract WARNING lines from stderr (non-fatal but useful)
            warnings = [
                line for line in result.stderr.splitlines()
                if "WARNING" in line
            ]
            if warnings:
                return True, f"Syntax OK ({len(warnings)} warning(s))"
            return True, "Syntax OK"
        else:
            # Extract ERROR lines
            errors = [
                line for line in result.stderr.splitlines()
                if "ERROR" in line or "error" in line.lower()
            ]
            error_msg = "\n".join(errors) if errors else result.stderr
            return False, error_msg

    except subprocess.TimeoutExpired:
        return True, "Syntax check timed out (skipped)"
    except FileNotFoundError:
        return True, f"OpenSCAD not found at {OPENSCAD_PATH} (skipped)"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


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

    # Get the file path from tool input
    file_path = tool_input.get("file_path", "")
    if not file_path.endswith(".scad"):
        sys.exit(0)

    ok, message = check_syntax(file_path)

    if ok:
        if message:
            print(f"[scad] {os.path.basename(file_path)}: {message}")
        sys.exit(0)
    else:
        print(
            f"[scad] SYNTAX ERROR in {os.path.basename(file_path)}:\n{message}",
            file=sys.stderr,
        )
        # Exit 0 — don't block the edit, just report the error.
        # The file is already written; blocking now would be confusing.
        # The user/Claude sees the error and can fix it.
        sys.exit(0)


if __name__ == "__main__":
    main()
