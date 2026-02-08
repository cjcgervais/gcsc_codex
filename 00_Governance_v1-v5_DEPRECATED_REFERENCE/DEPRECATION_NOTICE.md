# DEPRECATION NOTICE

**Date:** 2026-02-01
**Status:** DEPRECATED - REFERENCE ONLY
**Applies To:** All governance documents in this directory

---

## This Governance Framework Is No Longer Active

The governance documents in this directory (`00_Governance_v1-v5_DEPRECATED_REFERENCE/`) are from the **legacy GCSC v1-v5 project** and **DO NOT APPLY to GCSC2**.

---

## Why Deprecated?

The legacy governance was designed for:
- **Python-based programmatic plate generation**
- **Antigravity AI tool integration**
- **Gemini-specific workflows**
- **Different canonical truth stack** (gcsc_programmatic_plates_v1.py, GCSC_v2.6.1.md)

GCSC2 uses:
- **OpenSCAD-based parametric design**
- **Claude Code development environment**
- **Universal Governor skill integration**
- **Different canonical truth stack** (dimensions.scad → modules/*.scad → STL)

These are fundamentally different approaches requiring different governance.

---

## Current Governance Location

**Active GCSC2 Governance:**
```
00_Governance/
├── README.md
├── GCSC2_Constitution.md
├── Universal_Governor_Integration.md
└── Research_Driven_Design_Philosophy.md
```

**Use these documents** for GCSC2 development.

---

## Why Keep This Directory?

These legacy documents are preserved for:

1. **Historical Reference** - Understanding evolution from v5.x to v6.x
2. **Design Rationale** - Some principles still valid (Zero-Assumption Doctrine, etc.)
3. **Lessons Learned** - Pain points documented inform GCSC2 governance
4. **Canonical Truth** - GCSC_v2.6.1.md remains reference specification

---

## How to Use Legacy Governance

**DO:**
- ✓ Reference for understanding v5.x design decisions
- ✓ Consult GCSC_v2.6.1.md for original specification
- ✓ Learn from governance philosophy (even if tools different)
- ✓ Cite when documenting migration from v5.x to v6.x

**DO NOT:**
- ✗ Apply Antigravity tool requirements to GCSC2
- ✗ Follow Python-specific workflows
- ✗ Enforce v1-v5 canonical truth stack on v6.x
- ✗ Treat these as current governance authority

---

## Key Legacy Documents

**GCSC_Governance_Constitution_v1.0.md**
- Legacy supreme governance document
- Contains valuable principles (Zero-Assumption, Non-Destructive Versioning)
- **References Antigravity tool - NOT APPLICABLE to GCSC2**

**GCSC_Git_Discipline_Annex_v1.0.md**
- Git workflow standards from v1-v5
- Commit format differs from GCSC2 ("GCSC:" vs "GCSC2:")

**GCSC_Geometry_Integrity_Guardrails_Annex_v1.0.md**
- 10 integrity guardrails (G1-G10)
- Principles still relevant, but applied to OpenSCAD context

**GCSC_Master_Governance_Constitution_Quick_Card_v1.0.md**
- Quick reference for v1-v5 governance
- See `00_Governance/Quick_Reference.md` for GCSC2 equivalent

---

## Migration to GCSC2 Governance

If you are migrating from v5.x development to v6.x:

**Read First:**
1. `00_Governance/GCSC2_Constitution.md` - New supreme authority
2. `00_Governance/Universal_Governor_Integration.md` - How to use UG skill
3. `docs/GCSC_REDESIGN_RESEARCH.md` - Why redesign happened

**Key Changes to Know:**
- **Tool:** Antigravity → Universal Governor skill
- **Language:** Python → OpenSCAD
- **Parameters:** Python variables → dimensions.scad
- **Geometry:** Programmatic plates → CSG modules
- **Workflow:** Gemini prompts → Claude Code + research-driven design

---

## Questions About Legacy Governance?

**For historical questions:**
- Review documents in this directory
- Consult git history of v1-v5 project

**For current governance:**
- See `00_Governance/README.md`
- Activate Universal Governor skill
- Consult GCSC2 development team

---

**FINAL WARNING:**

Using legacy governance for GCSC2 development will cause confusion and conflict. Always use `00_Governance/` for GCSC2 work.

---

**Deprecated:** 2026-02-01
**Superseded By:** GCSC2_Constitution.md v2.0.0
**Preservation Reason:** Historical reference and institutional knowledge
