---
name: eval
description: Evaluate work quality against governance criteria. Produces a scorecard with pass/fail ratings. Use after completing significant work.
argument-hint: "[what: phase1|commit|geometry|all]"
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, Task, mcp__gcsc-openscad__check_syntax, mcp__gcsc-openscad__render_file, mcp__gcsc-openscad__validate_mesh
---

# Work Evaluation Skill

You are producing a quality scorecard for recent GCSC2 work. This evaluates
deliverables against the governance framework (CLAUDE.md + Constitution +
CANONICAL_DESIGN_REQUIREMENTS.md) and produces an actionable pass/fail assessment.

**CRITICAL:** The v6.1.0 "Beautiful Hull" scored 95/100 on a previous version of
this skill but FAILED human verification. That failure led to adding Category 5
(Functional Requirements). A design that cannot sit flat, cannot be assembled, or
does not look like a canoe is NOT production-ready regardless of other scores.

## Arguments

- `$ARGUMENTS` = evaluation scope (default: `all`)
  - `phase1` — evaluate Phase 1 milestone readiness
  - `commit` — evaluate current uncommitted changes
  - `geometry` — evaluate geometry quality of current builds
  - `all` — comprehensive evaluation

## Evaluation Criteria

### Category 1: Build Health (15 points)

| Check | Points | Method |
|-------|--------|--------|
| All .scad files pass syntax check | 4 | Run check_syntax on each |
| STL exports succeed and are manifold | 4 | Check STL_Exports/, >100KB, validate_mesh |
| Renders exist and are current | 4 | Check renders/ directory |
| No OpenSCAD warnings | 3 | Check syntax output for warnings |

**P1 Mesh Validation (NEW):** Use `mcp__gcsc-openscad__validate_mesh` on each STL.
A non-manifold or degenerate mesh is a BUILD FAIL even if export "succeeded".

### Category 2: Parameter Integrity (15 points)

| Check | Points | Method |
|-------|--------|--------|
| 7 frozen params at canonical values | 9 | Grep and verify each |
| No parameter duplication across files | 3 | Grep for assignments |
| All modules include dimensions.scad | 3 | Check include statements |

### Category 3: Governance Compliance (15 points)

| Check | Points | Method |
|-------|--------|--------|
| VERIFICATION_LOG.md has completed entry | 6 | Read and check for PASS/FAIL |
| Dual-AI verification performed | 3 | Check for both Claude + Gemini observations |
| Required render artifacts exist | 3 | Check 3 mandatory renders |
| No placeholder text in verification | 3 | Grep for "[TO BE" patterns |

### Category 4: Code Quality (15 points)

| Check | Points | Method |
|-------|--------|--------|
| No known bug patterns | 6 | Check for rotate([0,90,0]) etc. |
| Consistent code style | 3 | Check indentation, naming |
| No orphaned/dead code | 3 | Check for unused modules |
| Clean git status (no accidental files) | 3 | Check for temp files in tracked dirs |

### Category 5: Functional Requirements (40 points) — CRITICAL

**Authority:** CANONICAL_DESIGN_REQUIREMENTS.md (Human Verification 2026-02-05)

**Why this category exists:** The v6.1.0 "Beautiful Hull" passed all other checks
but failed human verification because it could not sit flat, could not be assembled,
and did not look like a canoe. This category prevents that failure.

**Why 40% weight:** FR is the most critical category. A design that fails functional
requirements is non-functional regardless of build health, parameter integrity, or
code quality. The v6.1.0 failure proved this conclusively.

| Check | Points | Method |
|-------|--------|--------|
| **FR-1: Flat Bottom Test** | 15 | See detailed procedure below |
| **FR-2: Ball Insertion Test** | 10 | See detailed procedure below |
| **FR-3: Canoe Form Test** | 10 | See detailed procedure below |
| **FR-4: BOSL2 Test** | 5 | See detailed procedure below (Phase 2 only) |

#### FR-1: Flat Bottom Test (15 points)

**Requirement:** Hull MUST sit stably on a flat bathroom counter.

**Verification Procedure:**
1. Render bottom view of hull (camera: `0,0,0,180,0,0,200` or top view flipped)
2. Check hull_simple.scad for hull bottom construction:
   - PASS: Flat elliptical base, no V-keel protrusion
   - FAIL: V-keel, rocker, or curved bottom that prevents stable resting
3. If `deadrise_angle` parameter exists, verify it creates visual character only,
   not actual V-bottom (for Phase 1, deadrise should affect inner cavity, not outer bottom)

**Failure indicators:**
- Parameter `deadrise_angle` applied to outer hull bottom
- No flat_bottom_height or equivalent in dimensions
- Bottom of hull() is spherical/tapered instead of flat

#### FR-2: Ball Insertion Test (10 points)

**Requirement:** Frame pivot balls (7.25mm dia) MUST be insertable into hull slots
(7.5mm dia) from above without obstruction.

**Verification Procedure:**
1. Render cross-section view at slot position (`cross_section` camera preset)
2. Examine pivot_slots() module in hull_simple.scad:
   - Check slot is created by simple cylinder subtraction
   - Check no horizontal strips or ledges obstruct vertical insertion path
   - Verify slot_diameter (7.5mm) > ball_diameter (7.25mm)
3. If any geometry intersects the vertical path from slot top to hemisphere seat: FAIL

**Failure indicators:**
- Complex slot geometry with multiple difference() operations
- "Retention strips" or "insertion guides" that narrow the slot
- Slot cylinder diameter reduced anywhere along its length
- Hemisphere seat is deeper than slot reaches

#### FR-3: Canoe Form Test (10 points)

**Requirement:** Hull must be recognizable as a canoe with curved gunwale (sheer line).

**Verification Procedure:**
1. Render side view of hull (`side` camera preset)
2. Examine the top edge (gunwale) profile:
   - PASS: Curved edge that rises toward bow and stern (characteristic canoe sheer)
   - FAIL: Flat horizontal top edge (freeboard is constant Z height)
3. Check hull construction in hull_simple.scad:
   - Look for how freeboard/sheer is implemented
   - Phase 1 limitation: hull() of spheres can only approximate curved gunwale
   - Phase 2 requirement: BOSL2 skin() or path_sweep() for true curved sheer

**Failure indicators:**
- `intersection()` with horizontal plane at constant Z
- No sheer_rise parameter or sheer_rise = 0
- Top edge is straight horizontal line in side render
- Freeboard cut creates flat top instead of curved profile

**Phase 1 vs Phase 2 Grading:**
- Phase 1 (CSG): 10 points if best-effort curved gunwale is attempted
- Phase 2 (BOSL2): 10 points ONLY if true curved sheer using BOSL2 functions

#### FR-4: BOSL2 Test (5 points) — Phase 2 Only

**Requirement:** Phase 2 hull files MUST use BOSL2 for curved surfaces.

**Verification Procedure:**
1. Check for BOSL2 include statement:
   - Grep for `include.*BOSL2.*std\.scad` in Phase 2 hull files
   - PASS: Include statement present
   - FAIL: No BOSL2 include in Phase 2 hull module
2. Check for BOSL2 hull construction functions:
   - Grep for `\bskin\s*\(` or `\bpath_sweep\s*\(` in hull modules
   - PASS: BOSL2 lofting function used for primary hull surface
   - FAIL: Only CSG primitives found
3. Check that CSG `hull()` is NOT used for primary hull:
   - Grep for `hull\s*\(\s*\).*sphere` in Phase 2 hull modules
   - PASS: No hull() of spheres pattern
   - FAIL: Phase 1 CSG pattern in Phase 2 file

**Scoring:**
- Phase 1 files: N/A — skip this check entirely (Phase 1 is CSG-limited by design)
- Phase 2 files with proper BOSL2: 5 points
- Phase 2 files without BOSL2: 0 points AND report as FUNCTIONAL BLOCKER

**Why this matters:** Phase 1 CSG (hull() of spheres) cannot produce true curved surfaces.
The v6.1.0 failure proved that iterating on CSG yields diminishing returns. Phase 2 MUST
use BOSL2 for production-quality hull fairing.

## Evaluation Procedure

### Step 1: Gather Evidence

Read the following files and run the following checks:
1. All .scad files in `01_Prototype_Simple/` and `modules/`
2. `params/dimensions.scad` — verify frozen parameters
3. `VERIFICATION_LOG.md` — check verification status
4. Run syntax checks on all .scad files
5. Check `renders/` and `STL_Exports/` for artifacts
6. Check git status for cleanliness
7. **NEW:** Render side view and cross-section for functional verification
8. **NEW:** Read hull_simple.scad and analyze hull/slot construction

### Step 2: Score Each Category

For each check, assign full points or 0 (no partial credit).
Document the evidence for each score.

**CRITICAL:** Category 5 (Functional Requirements) failures are BLOCKING.
A design that fails FR-1, FR-2, FR-3, or FR-4 is NOT production-ready regardless
of total score. Report these failures prominently.

### Step 3: Produce Scorecard

```
+==============================================================+
|                  GCSC2 QUALITY SCORECARD                     |
|                  Date: [timestamp]                           |
|                  Scope: [scope]                              |
+==============================================================+
|                                                              |
|  BUILD HEALTH                    [XX/15]                     |
|    Syntax checks ................. [PASS/FAIL]  (6 pts)      |
|    STL exports ................... [PASS/FAIL]  (3 pts)      |
|    Renders current ............... [PASS/FAIL]  (3 pts)      |
|    No warnings ................... [PASS/FAIL]  (3 pts)      |
|                                                              |
|  PARAMETER INTEGRITY             [XX/15]                     |
|    Frozen params correct ......... [PASS/FAIL]  (9 pts)      |
|    No duplication ................ [PASS/FAIL]  (3 pts)      |
|    Includes valid ................ [PASS/FAIL]  (3 pts)      |
|                                                              |
|  GOVERNANCE COMPLIANCE           [XX/15]                     |
|    Verification log .............. [PASS/FAIL]  (6 pts)      |
|    Dual-AI verification .......... [PASS/FAIL]  (3 pts)      |
|    Render artifacts .............. [PASS/FAIL]  (3 pts)      |
|    No placeholders ............... [PASS/FAIL]  (3 pts)      |
|                                                              |
|  CODE QUALITY                    [XX/15]                     |
|    No bug patterns ............... [PASS/FAIL]  (6 pts)      |
|    Style consistent .............. [PASS/FAIL]  (3 pts)      |
|    No dead code .................. [PASS/FAIL]  (3 pts)      |
|    Git clean ..................... [PASS/FAIL]  (3 pts)      |
|                                                              |
|  FUNCTIONAL REQUIREMENTS         [XX/40]  <<< CRITICAL <<<   |
|    FR-1: Flat Bottom ............. [PASS/FAIL]  (15 pts)     |
|    FR-2: Ball Insertion .......... [PASS/FAIL]  (10 pts)     |
|    FR-3: Canoe Form .............. [PASS/FAIL]  (10 pts)     |
|    FR-4: BOSL2 Usage ............. [PASS/FAIL/N/A] (5 pts)   |
|                                                              |
+==============================================================+
|  TOTAL SCORE:  [XX/100]                                      |
|  GRADE:        [A/B/C/D/F]                                   |
|  VERDICT:      [PASS/FAIL]                                   |
+==============================================================+
|                                                              |
|  FUNCTIONAL BLOCKERS:                                        |
|  [List any FR-1/FR-2/FR-3/FR-4 failures here - BLOCKING]     |
|                                                              |
+==============================================================+
```

### The Soap Dish Test (Summary Check)

Before finalizing the scorecard, answer these 6 questions:

| Question | Answer | Evidence |
|----------|--------|----------|
| 1. Does it sit flat on a surface? | YES/NO | [Bottom render analysis] |
| 2. Can the frame be inserted? | YES/NO | [Slot cross-section analysis] |
| 3. Does it hold soap adequately? | YES/NO | [Interior volume check] |
| 4. Can water drain? | YES/NO | [Drainage path check] |
| 5. Does it look like a canoe? | YES/NO | [Side render - curved gunwale] |
| 6. Uses BOSL2 (Phase 2 only)? | YES/NO/N/A | [Code review] |

If ANY answer is NO (except N/A for Phase 1), report as FUNCTIONAL BLOCKER even if total score is high.

### Grading Scale

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | A | Production ready (if no functional blockers) |
| 80-89 | B | Good — minor issues to address |
| 70-79 | C | Acceptable — needs attention before milestone |
| 60-69 | D | Below standard — must fix before proceeding |
| <60 | F | Failing — critical issues require immediate action |

**Pass threshold: 70/100 (C or better)**
**Phase milestone threshold: 80/100 (B or better)**

**CRITICAL OVERRIDE:** Any functional blocker (FR-1/FR-2/FR-3/FR-4 failure) downgrades
verdict to FAIL regardless of total score. A 95/100 with a functional blocker
is still FAIL.

### Step 4: Action Items

List specific, actionable fixes for any failed checks:
```
ACTION ITEMS:

FUNCTIONAL BLOCKERS (must fix before ANY approval):
1. [FR-BLOCK] FR-1 FAIL: V-keel prevents stable resting — flatten hull bottom
2. [FR-BLOCK] FR-2 FAIL: Slot obstruction — remove insertion strips
3. [FR-BLOCK] FR-3 FAIL: Flat gunwale — implement curved sheer line
4. [FR-BLOCK] FR-4 FAIL: No BOSL2 in Phase 2 — add include and use skin()

Other issues:
5. [CRITICAL] Fix rotate() in hull_simple.scad:68 — wrong slot orientation
6. [WARNING] Update VERIFICATION_LOG.md — placeholder text at line 27
7. [INFO] Remove orphaned test_slots_only.scad from tracked files
```

## Reference: v6.1.0 Failure Case Study

The v6.1.0 "Beautiful Hull" scored 95/100 on the previous eval criteria:
- Build Health: 25/25
- Parameter Integrity: 25/25
- Governance Compliance: 20/25 (minor placeholder issue)
- Code Quality: 25/25

**But it FAILED human verification because:**
- FR-1 FAIL: V-keel made it tip over on sink
- FR-2 FAIL: Slot geometry blocked ball insertion
- FR-3 FAIL: Flat freeboard cut, not curved gunwale

**Lesson:** A high score without functional verification is meaningless.
This is why Category 5 now exists and why functional blockers override the total.

## FORBIDDEN

- Giving a passing score without checking every criterion
- Awarding partial points (each check is pass/fail)
- Skipping the evidence documentation
- Saying "overall looks good" without the scorecard
- **NEW:** Ignoring functional blockers because other scores are high
- **NEW:** Skipping the Soap Dish Test questions
- **NEW:** Passing a design without verifying FR-1, FR-2, FR-3, and FR-4 (Phase 2)
