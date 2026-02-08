---
name: build
description: Full build pipeline — syntax check all .scad files, export STL, render standard views, report results. Use after geometry changes.
argument-hint: "[target: hull|frame|assembly|all]"
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, Task, mcp__gcsc-openscad__check_syntax, mcp__gcsc-openscad__export_stl, mcp__gcsc-openscad__render_file, mcp__gcsc-openscad__render_standard_views, mcp__gcsc-openscad__validate_mesh
---

# Build Pipeline Skill

You are executing the GCSC2 build pipeline. This compiles OpenSCAD sources to STL,
renders verification images, and reports build health. Every geometry change should
be followed by a build to catch errors early.

## Arguments

- `$ARGUMENTS` = target component (default: `all`)
  - `hull` — build hull only
  - `frame` — build frame only
  - `assembly` — build assembly (hull + frame)
  - `all` — build everything

## Build Targets

The build system operates on `01_Prototype_Simple/` (Phase 1) as the primary target.

| Target | Source File | STL Output | Renders |
|--------|-----------|------------|---------|
| hull | `hull_v6_simple.scad` (or `modules/hull_simple.scad`) | `STL_Exports/hull_v6_simple.stl` | iso, top, side, cross_section |
| frame | `frame_v6_simple.scad` (or `modules/frame_simple.scad`) | `STL_Exports/frame_v6_simple.stl` | iso, front |
| assembly | `assembly_complete.scad` | `STL_Exports/assembly_complete.stl` | assembly, top, side |

## Pipeline Steps

Execute IN ORDER. Report results for each step.

### Step 1: Discover Build Targets

```
Glob for *.scad files in 01_Prototype_Simple/ and 01_Prototype_Simple/modules/
Identify which targets match $ARGUMENTS
List all files that will be processed
```

### Step 2: Syntax Check (Fast Gate)

For EACH .scad file in scope:
1. Use the `mcp__gcsc-openscad__check_syntax` tool
2. If ANY file fails syntax check, STOP and report errors
3. Log: `[SYNTAX] filename.scad: OK / FAIL`

This is the fast gate — catches errors in seconds, not minutes.

### Step 3: Export STL

For each target component:
1. Use `mcp__gcsc-openscad__export_stl` to generate STL
2. Record file size in KB
3. If export fails, report error but continue with other targets
4. Log: `[STL] component.stl: SIZE_KB / FAIL`

### Step 3.5: Mesh Integrity Validation (P1 Governance)

For each exported STL:
1. Use `mcp__gcsc-openscad__validate_mesh` tool to check mesh integrity
2. Verify:
   - Manifold (watertight) - no open edges
   - No degenerate facets (zero-area triangles)
   - Reasonable file size (>100KB for hull)
3. Log: `[MESH] component.stl: VALID / WARN (details)`

**Why this matters:** hull_v7_bosl2 passed all syntax checks but had catastrophic
geometry defects (lopsided hull, open ends) that only mesh validation catches.

**Note:** If admesh is not installed, falls back to basic size/facet count checks.
Install admesh for full validation: `apt install admesh` or `choco install admesh`

### Step 4: Render Standard Views

For each target component:
1. Use `mcp__gcsc-openscad__render_standard_views` with appropriate views
2. Hull: `["iso", "top", "side", "cross_section"]`
3. Frame: `["iso", "front"]`
4. Assembly: `["assembly", "top", "side"]`
5. Log: `[RENDER] component_view.png: OK / FAIL`

### Step 5: Visual Spot-Check

For each rendered image:
1. Read the image file
2. State ONE specific observation (not "looks good" — name a geometric feature)
3. Flag anything unexpected

### Step 5.5: Functional Requirements Spot Check

For hull builds, verify basic FR compliance. This is a quick spot-check, not a full
verification gate — run `/verify` for complete validation.

**FR-1 Quick Check (Flat Bottom):**
- Render bottom view using camera: `0,0,0,180,0,0,200`
- Confirm flat contact surface visible (not V-keel or excessive rocker)
- WARN if bottom appears curved or pointed

**FR-2 Quick Check (Ball Insertion Path):**
- Check cross_section render from Step 4
- Confirm 4 slot openings visible with clear vertical paths
- WARN if slots appear obstructed or missing

**FR-3 Quick Check (Canoe Form):**
- Check side render from Step 4
- Confirm gunwale curves upward at bow/stern (sheer line)
- WARN if top edge is flat-cut or lacks canoe character

**FR-4 Quick Check (BOSL2 for Phase 2):**
- Only applies to files in `02_Production_BOSL2/`
- Grep for `include.*BOSL2` in source file
- WARN if Phase 2 hull file lacks BOSL2 include

Log format: `[FR] component: FR-1 [OK/WARN], FR-2 [OK/WARN], FR-3 [OK/WARN], FR-4 [OK/WARN/N/A]`

**Important:** FR checks are advisory warnings, not blocking gates. A WARN result
should prompt the developer to investigate but does not fail the build. Use `/verify`
for authoritative functional validation.

### Step 6: Build Report

Output a summary table:

```
=== GCSC2 BUILD REPORT ===
Target: [all/hull/frame/assembly]
Date: [timestamp]

SYNTAX CHECK:
  [x] hull_simple.scad ........... OK
  [x] frame_simple.scad .......... OK
  [x] dimensions.scad ............ OK

STL EXPORT:
  [x] hull_v6_simple.stl ......... 1,842 KB
  [x] frame_v6_simple.stl ........ 453 KB

RENDERS:
  [x] hull_iso.png ............... OK
  [x] hull_top.png ............... OK
  [x] frame_iso.png .............. OK

SPOT CHECK:
  hull_iso: [one specific observation]
  frame_iso: [one specific observation]

FUNCTIONAL REQUIREMENTS (hull only):
  FR-1 (Flat Bottom): ............ OK / WARN
  FR-2 (Ball Insertion): ......... OK / WARN
  FR-3 (Canoe Form): ............. OK / WARN
  FR-4 (BOSL2): .................. OK / WARN / N/A

RESULT: PASS / FAIL (N errors, M FR warnings)
```

**Note on FR Warnings:** FR warnings do not fail the build but indicate potential
functional issues that should be investigated. If any FR shows WARN, consider
running `/verify` for complete validation before proceeding to milestone.

## Error Handling

- Syntax errors: STOP build, report errors, suggest fixes
- STL export failures: Continue with other targets, report at end
- Render failures: Continue, report at end
- Missing source files: Report which files are missing and expected locations

## Known Patterns

- If hull renders show smooth surface with NO slot openings, the `rotate()` in
  `pivot_slots()` is wrong (known bug: `rotate([0,90,0])` vs correct `rotate([90,0,0])`)
- If STL file size is suspiciously small (<100KB for hull), geometry may be incomplete
- If assembly STL exceeds 10MB, check for accidental duplicate geometry
