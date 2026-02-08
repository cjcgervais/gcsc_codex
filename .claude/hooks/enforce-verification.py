#!/usr/bin/env python3
"""GCSC2 Verification Enforcement Hook (PreToolUse)

Before git commit operations that include .scad or .stl changes,
checks that VERIFICATION_LOG.md has been updated with a completed
verification entry (not just placeholder text).

This prevents the exact failure mode that created the governance protocol:
committing geometry changes without visual verification.

Hook protocol:
  - Receives JSON on stdin with tool_name and tool_input
  - Exit 0 = allow
  - Exit 2 = block (reason on stderr)
"""

import sys
import json
import re
import os
from pathlib import Path


def _discover_project_root() -> Path:
    """Resolve project root from env override or repository-relative fallback."""
    env_root = os.environ.get("GCSC_PROJECT_ROOT", "").strip()
    if env_root:
        p = Path(env_root).expanduser()
        if p.exists():
            return p.resolve()
    # .claude/hooks/enforce-verification.py -> repo root is parents[2]
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _discover_project_root()

# Directories where .scad/.stl changes trigger verification requirement
WATCHED_DIRS = ["01_Prototype_Simple", "02_Production_BOSL2"]

# Patterns that indicate an incomplete verification
PLACEHOLDER_PATTERNS = [
    r"\[TO BE FILLED",
    r"\[Claude will document",
    r"\[Claude observations",
    r"\[Gemini output will be",
    r"\[low/medium/high\]",
    r"\[PASS/FAIL\]",
    r"\[YES/NO",
]


def is_geometry_commit(command: str) -> bool:
    """Check if a bash command is a git commit that might include geometry files."""
    if "git commit" not in command and "git add" not in command:
        return False
    # It's a git operation — check if it involves watched files
    # We check broadly: any commit in the project could include geometry
    return True


def get_staged_phase_dirs() -> set[str]:
    """Determine which phase directories have staged geometry files."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=10,
            cwd=PROJECT_ROOT
        )
        if result.returncode != 0:
            return set()

        staged = result.stdout.strip().splitlines()
        affected_dirs = set()
        for f in staged:
            if f.endswith((".scad", ".stl")):
                for watched in WATCHED_DIRS:
                    if f.startswith(watched):
                        affected_dirs.add(watched)
        return affected_dirs
    except Exception:
        return set()


def check_verification_log() -> tuple[bool, str]:
    """Check if VERIFICATION_LOG.md has a completed verification entry.

    Checks the appropriate verification log based on which phase directory
    has staged geometry files. Phase 1 and Phase 2 have separate logs.
    """
    # Determine which directories are affected by this commit
    affected_dirs = get_staged_phase_dirs()

    # If we can't determine (or no geometry files), check Phase 1 as default
    if not affected_dirs:
        affected_dirs = {"01_Prototype_Simple"}

    # Build list of logs to check based on affected directories
    log_paths = []
    for phase_dir in affected_dirs:
        log_paths.append(
            (phase_dir, Path(PROJECT_ROOT) / phase_dir / "VERIFICATION_LOG.md")
        )

    for phase_dir, log_path in log_paths:
        if not log_path.exists():
            return False, f"{phase_dir}/VERIFICATION_LOG.md not found at {log_path}"

        content = log_path.read_text(encoding="utf-8")

        # Check for at least one completed verification (has a Verdict line)
        has_verdict = bool(re.search(
            r"###\s*Verdict\s*\n+\s*\*\*(?:PASS|FAIL)\*\*",
            content
        ))

        if not has_verdict:
            return False, (
                f"{phase_dir}/VERIFICATION_LOG.md has no completed verification entry. "
                "Run /verify before committing geometry changes."
            )

        # NEW: Check for FR evidence in the latest verification entry
        # Per GOVERNANCE_AUDIT_2026-02-05.md - v6.1.0 failed because
        # verification asked "visible?" not "insertable?"
        FR_REQUIRED_PATTERNS = [
            (r'FR-1.*(?:PASS|FAIL|flat|bottom|stable)', "FR-1 (Flat Bottom) check"),
            (r'FR-2.*(?:PASS|FAIL|insert|ball|slot)', "FR-2 (Ball Insertion) check"),
            (r'FR-3.*(?:PASS|FAIL|gunwale|curve|sheer)', "FR-3 (Curved Gunwale) check"),
        ]

        # Get latest verification section
        sections = re.split(r'^##\s+Verification', content, flags=re.MULTILINE)
        if len(sections) >= 2:
            latest = sections[-1]

            missing_fr = []
            for pattern, name in FR_REQUIRED_PATTERNS:
                if not re.search(pattern, latest, re.IGNORECASE):
                    missing_fr.append(name)

            if missing_fr:
                return False, (
                    f"{phase_dir}/VERIFICATION_LOG.md latest entry missing FR checks: "
                    f"{', '.join(missing_fr)}. "
                    f"Run /verify with functional requirement queries."
                )

        # Check for remaining placeholder text in the LATEST entry
        # Find the last "## Verification:" section
        sections = re.split(r"##\s+Verification:", content)
        if len(sections) > 1:
            latest_section = sections[-1]
            for pattern in PLACEHOLDER_PATTERNS:
                if re.search(pattern, latest_section):
                    return False, (
                        f"{phase_dir}/VERIFICATION_LOG.md latest entry has placeholder text "
                        f"(pattern: {pattern}). Complete the verification before committing."
                    )

    return True, "Verification log OK"


def check_staged_files() -> bool:
    """Check if any staged files are geometry-related."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=10,
            cwd=PROJECT_ROOT
        )
        if result.returncode != 0:
            return False

        staged = result.stdout.strip().splitlines()
        for f in staged:
            if f.endswith((".scad", ".stl")):
                for watched in WATCHED_DIRS:
                    if f.startswith(watched):
                        return True
        return False
    except Exception:
        return False  # Can't determine — don't block


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only check Bash commands that are git commits
    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")

    if "git commit" not in command:
        sys.exit(0)

    # Check if geometry files are staged
    has_geometry = check_staged_files()
    if not has_geometry:
        # No geometry files in this commit — allow
        sys.exit(0)

    # Geometry files are being committed — require verification
    ok, message = check_verification_log()

    if not ok:
        print(
            f"BLOCKED: {message}\n\n"
            "Geometry files (.scad/.stl) are staged for commit but verification "
            "is incomplete. Per CLAUDE.md governance protocol:\n"
            "  1. Run /verify to execute dual-AI visual verification\n"
            "  2. Ensure VERIFICATION_LOG.md has a completed PASS/FAIL verdict\n"
            "  3. Then retry the commit\n\n"
            "To commit non-geometry files only, unstage .scad/.stl files first.",
            file=sys.stderr
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
