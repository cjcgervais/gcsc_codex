---
name: audit
description: Full codebase audit — parameter consistency, known bug patterns, governance compliance, module dependencies. Use before phase milestones.
argument-hint: "[scope: params|geometry|governance|bosl2|functional|full]"
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, Task, mcp__gcsc-openscad__check_syntax
---

# Codebase Audit Skill

You are executing a comprehensive GCSC2 codebase audit. This skill checks parameter
integrity, geometry correctness patterns, governance compliance, and project health.
Run this before any phase milestone or after major refactoring.

## Arguments

- `$ARGUMENTS` = audit scope (default: `full`)
  - `params` — parameter consistency only
  - `geometry` — geometry pattern checks only
  - `governance` — governance artifact checks only
  - `bosl2` — BOSL2 compliance only (Phase 2)
  - `functional` — SDT functional requirements only (SDT-1, SDT-2, SDT-3)
  - `full` — all checks (including functional requirements)

## Audit Checks

### 1. Parameter Consistency (scope: params, full)

**Frozen Parameters (Article 0.6):**

These 7 parameters are constitutionally immutable. Verify each one:

| Parameter | Canonical Value | File |
|-----------|----------------|------|
| LOA | 148 | dimensions.scad |
| beam | 64 | dimensions.scad |
| freeboard | 45 | dimensions.scad |
| z_pivot_seat | 38 | dimensions.scad |
| slot_diameter | 7.5 | dimensions.scad |
| frame_x_offset | 16 | dimensions.scad |
| slot_y_position | 31 | dimensions.scad |

For each:
1. Grep the entire codebase for the parameter name
2. Verify it is defined ONLY in `params/dimensions.scad`
3. Verify the value matches the canonical value
4. Flag any file that redefines or shadows the parameter
5. Log: `[PARAM] parameter_name = value ... OK / VIOLATION (file:line)`

**Parameter Duplication Check:**
- Grep for `=` assignments in all .scad files
- Flag any parameter defined in more than one file (except derived values)
- Verify all modules use `include <../params/dimensions.scad>`

### 2. Geometry Pattern Checks (scope: geometry, full)

**Known Bug Patterns:**

Check for the critical slot rotation bug:
```
Grep for: rotate\(\[0,\s*90,\s*0\]\) in hull-related files
If found: CRITICAL — this is the broken slot orientation
Expected: rotate([90, 0, 0]) for port/starboard slots
```

Check for:
- `rotate([0, 90, 0])` in hull modules → CRITICAL BUG (fore/aft instead of port/starboard)
- `difference()` operations without children → geometry error
- `hull()` with fewer than 3 points → degenerate geometry
- Negative `$fn` values → render errors
- `scale([0,...])` → collapsed geometry

**Module Dependency Check:**
- For each .scad file, verify all `include` and `use` paths resolve
- Check for circular dependencies
- Verify no absolute paths (should all be relative)

### 3. Governance Compliance (scope: governance, full)

**Required Artifacts:**
Check that these exist (per CLAUDE.md):
- [ ] `renders/hull_features_labeled.png`
- [ ] `renders/cross_section_proof.png`
- [ ] `renders/assembly_fit_check.png`
- [ ] `VERIFICATION_LOG.md` (with at least one completed verification entry)

**Verification Log Quality:**
Read VERIFICATION_LOG.md and check:
- Has at least one verification with both Claude AND Gemini observations
- Has explicit PASS/FAIL verdict
- Has human confirmation section
- No placeholder text remaining (e.g., "[TO BE FILLED]")

**Hook Integrity:**
Verify these hooks exist and are valid Python:
- `.claude/hooks/guard-frozen-params.py`
- `.claude/hooks/check-scad-syntax.py`
- `.claude/hooks/param-consistency-check.py`
- `.claude/hooks/enforce-verification.py`
- `.claude/hooks/bosl2-enforcement.py`
- `.claude/hooks/phase1-iteration-guard.py`

### 4. File Structure (scope: full)

Verify expected directory structure:
```
01_Prototype_Simple/
  modules/
    hull_simple.scad
    frame_simple.scad
  params/
    dimensions.scad
  renders/
  STL_Exports/
  VERIFICATION_LOG.md
```

Flag any orphaned test files, temporary renders, or files outside expected structure.

### 5. BOSL2 Compliance (scope: bosl2, full)

**Phase 2 BOSL2 Pattern Check:**

This section verifies that Phase 2 (`02_Production_BOSL2/`) uses proper BOSL2 construction
instead of regressing to Phase 1 CSG primitives.

**Why this matters:** The v6.1.0 failure proved that Phase 1 CSG (`hull()` of spheres)
cannot produce true curved surfaces. Phase 2 MUST use BOSL2 for production-quality fairing.

**Check 1: BOSL2 Include Present**

For each .scad file in `02_Production_BOSL2/modules/` with "hull" in the name:
```
Grep for: include.*BOSL2.*std\.scad
If missing: CRITICAL — Phase 2 hull file requires BOSL2 include
Expected: include <lib/BOSL2/std.scad> or include <../lib/BOSL2/std.scad>
```

Log: `[BOSL2] hull_bosl2.scad ... BOSL2 include: OK / MISSING`

**Check 2: BOSL2 Hull Construction**

For each Phase 2 hull module:
```
Grep for: \bskin\s*\( or \bpath_sweep\s*\(
If missing: WARNING — No BOSL2 lofting function found
Expected: skin() used for primary hull surface construction
```

Log: `[BOSL2] hull_bosl2.scad ... skin()/path_sweep(): FOUND / NOT FOUND`

**Check 3: No CSG Hull Pattern**

For each Phase 2 hull module:
```
Grep for: hull\s*\(\s*\)\s*\{[^}]*sphere
If found: CRITICAL — Phase 1 CSG pattern in Phase 2 file
This is forbidden: Phase 2 must not use hull() of spheres for hull construction
```

Log: `[BOSL2] hull_bosl2.scad ... CSG hull() pattern: CLEAN / VIOLATION`

**BOSL2 Library Integrity:**

Verify BOSL2 submodule is present and valid:
```
Check: 02_Production_BOSL2/lib/BOSL2/std.scad exists
Check: 02_Production_BOSL2/lib/BOSL2/version.scad exists
If missing: CRITICAL — BOSL2 library not installed
```

**Severity:**
- CRITICAL: Missing BOSL2 include, CSG pattern in Phase 2 → FAIL
- WARNING: No skin()/path_sweep() found but BOSL2 included → WARN
- INFO: BOSL2 properly used → PASS

### 6. Functional Requirements Compliance (scope: functional, full)

**Purpose:** Verify design meets Soap Dish Test (SDT) operational requirements.

**Note:** These are SDT checks derived from Constitutional Functional Requirements (FR-1 through FR-4).
SDT-4 (BOSL2) is covered in Section 5 above.

#### SDT-1: Flat Bottom Check

**Why this matters:** The v6.1.0 "Beautiful Hull" failed because a V-keel made it unable to sit
flat on a bathroom counter. A canoe soap dish MUST rest stably.

1. **Hull Bottom Analysis:**
   - Grep hull modules for bottom/keel construction patterns
   - Check for V-keel anti-patterns: `deadrise`, `v_angle`, `keel_depth > 0`
   - Verify flat bottom indicators: `flat_bottom`, `bottom_flat`, `rocker = 0`

2. **Checks:**
   ```
   Grep for: deadrise_angle|v_angle|keel_depth|v_keel
   If deadrise_angle > 5 without flat bottom compensation: WARNING
   If keel_depth > 0 or v_keel present: CRITICAL

   Grep for: flat_bottom|bottom_flat|rocker\s*=\s*0
   If found: Good indicator of flat bottom design
   If missing AND v-keel patterns found: CRITICAL
   ```

3. **Failure Indicators:**
   - Any `deadrise_angle > 5` without flat bottom compensation
   - `keel_depth` or `v_keel` parameters present and > 0
   - Missing `flat_bottom_height` or equivalent in V-hull designs

**Log:** `[SDT-1] Flat bottom check ... PASS / WARN / FAIL (evidence)`

#### SDT-2: Ball Insertion Path Check

**Why this matters:** The frame balls must be insertable from above through the hull slots.
If slots are obstructed or oriented incorrectly, assembly is impossible.

1. **Slot Geometry Analysis:**
   - Read pivot_slots() module in hull files
   - Verify slot_diameter (7.5mm) > ball_diameter (7.25mm frozen value)
   - Check for slot obstructions in difference() operations

2. **Known Bug Pattern (CRITICAL):**
   ```
   Grep for: rotate\s*\(\s*\[\s*0\s*,\s*90\s*,\s*0\s*\]\s*\)
   Context: in pivot_slots() or slot-related modules

   BROKEN: rotate([0, 90, 0]) — slots oriented fore/aft, not visible from top
   CORRECT: rotate([90, 0, 0]) — slots oriented port/starboard, visible from top

   If rotate([0, 90, 0]) found in slot context: CRITICAL
   ```

3. **Slot Clearance Check:**
   ```
   Read dimensions.scad for:
   - slot_diameter (should be 7.5)
   - ball_diameter (should be 7.25 or derived)

   If slot_diameter <= ball_diameter: CRITICAL — balls cannot fit
   If slot_diameter - ball_diameter < 0.2: WARNING — very tight tolerance
   ```

4. **Failure Indicators:**
   - Slot diameter <= ball diameter
   - Rotate bug pattern `rotate([0, 90, 0])` present in slot context
   - Slot obstructions from later difference() operations

**Log:** `[SDT-2] Ball insertion path ... PASS / WARN / FAIL (evidence)`
**Log:** `[SDT-2] Rotate bug check ... NOT FOUND / FOUND at file:line`

#### SDT-3: Curved Gunwale Check

**Why this matters:** A canoe's defining visual feature is the curved sheer line (gunwale).
A flat-topped hull looks like a bathtub, not a canoe. The v6.1.0 failure included a flat
freeboard cut that destroyed the canoe character.

1. **Sheer Line Analysis:**
   - Grep for `sheer_rise` parameter in dimensions.scad and hull modules
   - Verify sheer_rise > 0 (optimal range: 10-30mm per CLAUDE.md)
   - Check that bow/stern have higher freeboard than midship

2. **Checks:**
   ```
   Grep for: sheer_rise|sheer_height|gunwale_rise
   If found and value > 0: PASS
   If found and value = 0: WARNING — no sheer rise defined
   If not found: WARNING — sheer line may not be implemented

   Grep for: bow_rise|stern_rise|end_rise
   If found: Check that values > 0 for canoe character
   ```

3. **Flat Top Anti-Pattern:**
   ```
   Grep for: flat.*top|freeboard_flat|straight.*gunwale
   If found: WARNING — may indicate flat-topped hull

   Look for: minkowski or hull() operations that would flatten the top edge
   ```

4. **Failure Indicators:**
   - `sheer_rise = 0` or missing entirely
   - Flat top edge in hull construction (no Z variation along length)
   - No variation in freeboard between midship and bow/stern

**Log:** `[SDT-3] Curved gunwale check ... PASS / WARN / FAIL (evidence)`

#### SDT Audit Summary

After running all SDT checks, produce a summary:

```
=== FUNCTIONAL REQUIREMENTS AUDIT (SDT) ===

SDT-1 (Flat Bottom):
  Status: [PASS/WARN/FAIL]
  Evidence: [specific parameter values or patterns found]

SDT-2 (Ball Insertion):
  Status: [PASS/WARN/FAIL]
  Evidence: [slot_diameter vs ball_diameter, clearance calculation]
  Rotate Bug: [NOT FOUND / FOUND at file:line]

SDT-3 (Curved Gunwale):
  Status: [PASS/WARN/FAIL]
  Evidence: [sheer_rise value, bow/stern rise indicators]

SDT-4 (BOSL2 for Phase 2):
  Status: [PASS/WARN/FAIL/N/A if Phase 1]
  Evidence: [see Section 5 BOSL2 Compliance above]

FUNCTIONAL OVERALL: [PASS/WARN/FAIL] ([N] critical, [M] warnings)
```

**Severity:**
- CRITICAL: V-keel present, rotate bug found, slot too small, no sheer at all → FAIL
- WARNING: Missing parameters but no anti-patterns, tight tolerances → PASS with warnings
- INFO: All SDT checks pass with good margins → PASS

## Audit Report Format

```
=== GCSC2 CODEBASE AUDIT ===
Scope: [full/params/geometry/governance/bosl2/functional]
Date: [timestamp]

PARAMETER INTEGRITY:
  [x] LOA = 148 .................. OK (1 definition, dimensions.scad:9)
  [x] beam = 64 .................. OK (1 definition, dimensions.scad:10)
  [!] slot_diameter .............. WARN (also defined in test_file.scad:12)
  ...
  Frozen params: 7/7 OK

GEOMETRY PATTERNS:
  [x] No rotate([0,90,0]) bugs ... OK
  [x] All includes resolve ....... OK
  [x] No degenerate geometry ..... OK
  ...
  Pattern checks: N/N OK

GOVERNANCE:
  [x] Verification renders ....... 3/3 present
  [x] VERIFICATION_LOG.md ........ Has completed entry
  [!] Human confirmation ......... PENDING
  ...
  Governance: N/N OK

BOSL2 COMPLIANCE (Phase 2):
  [x] BOSL2 include present ....... OK (hull_bosl2.scad)
  [x] skin()/path_sweep() used .... OK (hull_bosl2.scad:45)
  [x] No CSG hull() pattern ....... OK (no violations)
  [x] BOSL2 library present ....... OK (lib/BOSL2/)
  ...
  BOSL2 checks: N/N OK

FUNCTIONAL REQUIREMENTS (SDT):
  [x] SDT-1 Flat bottom ........... OK (no v-keel, flat_bottom_height=3)
  [x] SDT-2 Ball insertion ........ OK (slot 7.5 > ball 7.25, 0.25mm clearance)
  [x] SDT-2 Rotate bug ............ OK (not found)
  [!] SDT-3 Curved gunwale ........ WARN (sheer_rise=15, below optimal 20)
  ...
  Functional checks: 3/4 OK, 1 WARN

OVERALL: PASS / FAIL (N critical, M warnings)
```

## Severity Levels

- **CRITICAL**: Frozen parameter violation, known bug pattern found → FAIL
- **WARNING**: Missing optional artifacts, placeholder text → PASS with warnings
- **INFO**: Suggestions for improvement → PASS
