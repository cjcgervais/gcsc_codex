#!/usr/bin/env python3
"""
Insert Article 0 into Constitution before Article I.
Updates constitution header/history to v2.1.0.

This script is repository-relative by default. Use --repo-root to override.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Insert Article 0 into GCSC2 Constitution.")
    parser.add_argument(
        "--repo-root",
        default="",
        help="Path to repository root. Defaults to parent of scripts/.",
    )
    return parser.parse_args()


def resolve_repo_root(arg_value: str) -> Path:
    if arg_value:
        return Path(arg_value).expanduser().resolve()
    # scripts/insert_article_0.py -> repo root is parent of scripts/
    return Path(__file__).resolve().parent.parent


def main() -> int:
    args = parse_args()
    repo_root = resolve_repo_root(args.repo_root)

    proposal_path = repo_root / "00_Governance" / "proposals" / "2026-02-02-article-0-product-identity.md"
    constitution_path = repo_root / "00_Governance" / "GCSC2_Constitution.md"

    if not proposal_path.exists():
        print(f"ERROR: Proposal not found: {proposal_path}")
        return 1
    if not constitution_path.exists():
        print(f"ERROR: Constitution not found: {constitution_path}")
        return 1

    proposal = proposal_path.read_text(encoding="utf-8")

    # Extract Article 0 content from proposal.
    start_marker = "### Article 0: Product Identity and Core Concept"
    start_idx = proposal.find(start_marker)
    if start_idx == -1:
        print("ERROR: Could not find Article 0 start marker")
        return 1

    article_0_raw = proposal[start_idx:]
    end_marker = "## Implementation Checklist"
    end_idx = article_0_raw.find(end_marker)
    if end_idx == -1:
        # Fallback marker used in early drafts.
        end_marker = "---\n\n#### 0.6"
        end_idx = article_0_raw.find(end_marker)

    article_0_text = article_0_raw[:end_idx].strip() if end_idx != -1 else article_0_raw.strip()

    # Normalize heading levels for Constitution insertion.
    article_0_text = article_0_text.replace("### Article 0:", "## Article 0:")
    article_0_text = article_0_text.replace("#### 0.", "### 0.")

    constitution = constitution_path.read_text(encoding="utf-8")
    parts = constitution.split("## Article I: Foundational Principles", 1)
    if len(parts) != 2:
        print("ERROR: Could not find Article I marker")
        return 1

    header, rest = parts

    # Update version/effective date in header.
    header = header.replace("**Version:** 2.0.0", "**Version:** 2.1.0")
    header = header.replace("**Effective Date:** 2026-02-01", "**Effective Date:** 2026-02-02")

    supersedes_line = "**Supersedes:** GCSC v1-v5 Governance (archived in `00_Governance_v1-v5_DEPRECATED_REFERENCE/`)"
    if supersedes_line in header:
        header = header.replace(
            supersedes_line,
            supersedes_line
            + "\n\n**Amendment History:**\n"
            + "- **v2.1.0** (2026-02-02): Added Article 0 (Product Identity and Core Concept)\n"
            + "- **v2.0.0** (2026-02-01): GCSC2-specific governance established",
        )

    new_constitution = header + "\n" + article_0_text + "\n\n---\n\n" + "## Article I: Foundational Principles" + rest

    # Update Article I.1 to reference Article 0.
    article_i_section = """### 1.1 Project Identity

**GCSC2** is the OpenSCAD-based redesign of the Great Canadian Soap Canoe, developed under the **Universal Governor v1.1.0** framework with the following core identity:

- **Primary Tool:** OpenSCAD (CSG and BOSL2)
- **Development Environment:** Claude Code CLI
- **Governance Model:** Research-driven design philosophy
- **Version Control:** Git with semantic versioning
- **Architecture:** Phased development (Minimalist -> Production)"""

    article_i_updated = """### 1.1 Project Identity

**GCSC2** is the OpenSCAD-based redesign of the Great Canadian Soap Canoe, developed under the **Universal Governor v1.1.0** framework with the following core identity:

- **Primary Tool:** OpenSCAD (CSG and BOSL2)
- **Development Environment:** Claude Code CLI
- **Governance Model:** Research-driven design philosophy
- **Version Control:** Git with semantic versioning
- **Architecture:** Phased development (Minimalist -> Production)

**Product Concept:** See Article 0 for complete product identity, core concept, and mandatory functional requirements (FR-0 through FR-5)."""

    new_constitution = new_constitution.replace(article_i_section, article_i_updated)

    # Update Appendix B version history.
    appendix_b_old = """## Appendix B: Version History

**v2.0.0** (2026-02-01)
- Initial GCSC2-specific constitution
- Replaces legacy GCSC v1-v5 governance
- Aligned with Universal Governor v1.1.0
- Adapted for OpenSCAD workflow
- Added research-driven design philosophy
- Removed Antigravity tool references"""

    appendix_b_new = """## Appendix B: Version History

**v2.1.0** (2026-02-02)
- Added Article 0 (Product Identity and Core Concept)
- Defined FR-0: Gimbal-Based Soap Elevation System (THE CORNERSTONE)
- Established mandatory functional requirements (FR-0 through FR-5)
- Documented creator's 5-year innovation (gimbal mechanics, no drain holes)
- Added reference to v5.3 Final Assembly and GCSC_v2.6.1 concept seed

**v2.0.0** (2026-02-01)
- Initial GCSC2-specific constitution
- Replaces legacy GCSC v1-v5 governance
- Aligned with Universal Governor v1.1.0
- Adapted for OpenSCAD workflow
- Added research-driven design philosophy
- Removed Antigravity tool references"""

    new_constitution = new_constitution.replace(appendix_b_old, appendix_b_new)

    # Update footer version.
    new_constitution = new_constitution.replace(
        "**Version:** 2.0.0\n**Next Review:**",
        "**Version:** 2.1.0\n**Next Review:**",
    )

    constitution_path.write_text(new_constitution, encoding="utf-8")

    print("[OK] Article 0 inserted successfully")
    print("[OK] Version updated to 2.1.0")
    print("[OK] Article I.1 updated to reference Article 0")
    print("[OK] Appendix B updated with v2.1.0 history")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

