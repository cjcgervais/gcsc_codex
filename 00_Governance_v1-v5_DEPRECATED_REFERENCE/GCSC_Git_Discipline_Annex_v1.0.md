# GCSC Git Discipline Annex — v1.0

**Project:** The Great Canadian Soap Canoe™  
**Classification:** Governance Annex (Git + File Integrity)  
**Status:** Locked and Active

## 1. Purpose
This annex defines the Git discipline rules for all work involving the canonical
geometry specification (`GCSC_v2.6.1.md`), the deterministic geometry kernel
(`gcsc_programmatic_plates_v1.py`), the programmatic plates, and all related 
documentation.  
Its role is to prevent accidental drift, ensure version clarity, and maintain 
a stable mechanical truth for the product.

This annex applies to:
- Human edits
- Antigravity / Gemini generations
- Automated rebuilds of programmatic plates
- Any future LLM-assisted tools

## 2. Canonical Files (Protected Tier)
The following files are *mechanically authoritative* and must never be modified
without an explicit geometry version bump:

- `GCSC_v2.6.1.md` (Engineering spec)
- `GCSC/02_Diagrams/gcsc_programmatic_plates_v1.py` (Geometry kernel)
- `GCSC/02_Diagrams/Programmatic_Plates/` (Canonical plates)
- `GCSC_Programmatic_Plates_Record_v1.1.md`
- `GCSC_Bundle_Manifest_v2.6.1+Plates_v1.1.md`
- This annex

These files represent locked truth.  
Any change to geometry or numeric logic requires:
1. A new spec version (e.g., `GCSC_v2.7.0.md`)
2. A new programmatic kernel version (e.g., `gcsc_programmatic_plates_v2.py`)
3. A new plate set (e.g., `Plates_v2.0`)
4. A new manifest and annex revision

No silent edits are ever permitted.

## 3. What Antigravity / Gemini Are Allowed To Change
Allowed:
- Regenerate canonical plates from the existing kernel
- Update documentation files (records, manifests, annexes)
- Apply strictly non-geometric micro-fixes when explicitly instructed
- Auto-commit and auto-push without asking for confirmation

Not allowed:
- Changing geometry
- Adding new dimensions
- Renaming canonical files
- Reformatting or restructuring the geometry kernel
- Altering the Z-stack, hull loft, bumper geometry, frame widths, or swing envelope

If a request would violate these rules, the tool must halt and report instead of guessing.

## 4. Commit Discipline
All commits must follow the canonical prefix system:

### 4.1 Allowed Commit Prefixes
- **GCSC:** programmatic plate regeneration, doc updates, micro-fixes
- **GCSC-SPEC:** changes to the engineering spec (requires version bump)
- **GCSC-KERNEL:** changes to the geometry kernel (requires version bump)
- **GCSC-DOC:** documentation-only updates

### 4.2 Required Commit Format
PREFIX: clear description (version tag if applicable)
Examples:
GCSC: regenerate programmatic plates v1.1
GCSC-DOC: add Git Discipline Annex v1.0
GCSC-SPEC: bump to GCSC_v2.7.0.md (new geometry requirements)

## 5. Auto-Push Rule (Mandatory)
Antigravity/Gemini must ALWAYS:
- stage all modified files,
- commit with correct prefix,
- push directly to `origin/main`.

No confirmation from the user is required.  
No unpushed commits are ever permitted for GCSC.

## 6. Version Control Rules

### 6.1 Geometry Changes → Mandatory Version Bump
Any change that affects:
- dimensions  
- semiaxes  
- hull loft  
- Z-stack  
- bumper geometry  
- frame positions  
- swing envelopes  

requires:
- updating the spec file name (`v2.6.1` → `v2.7.0`)
- creating a new kernel file
- regenerating plates under a new plate version folder
- updating the manifest and annex

### 6.2 Visualization or Label Tweaks
Allowed without geometry bump IF they do not change:
- numeric values  
- projection math  
- plate ordering  
- filename patterns  

These changes should produce:
GCSC: visualization micro-fix v1.x

## 7. Safety Rule for All LLM Agents
If an LLM agent (any model) receives a request that *might* involve geometry changes,
it must:

1. Stop execution
2. Warn the user
3. Request explicit confirmation and/or provide a spec delta
4. Reject all silent edits

This prevents accidental corruption of canonical geometry.

## 8. Review & Update Schedule
This annex should be reviewed at the same time as:
- new spec releases
- new kernel releases
- major code regeneration changes
- major documentation bundle updates

A new annex version should be created only when rules materially change.
