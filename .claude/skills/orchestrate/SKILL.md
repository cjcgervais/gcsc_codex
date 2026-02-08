---
name: orchestrate
description: Governance coordinator for multi-agent workflows. Sequences skills, enforces functional requirements, gates milestones, logs all decisions.
argument-hint: "[task: hull|assembly|verify-all|phase2-init]"
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, Task, Skill, mcp__gcsc-openscad__render_file, mcp__gcsc-openscad__check_syntax, mcp__gcsc-openscad__export_stl
---

# Orchestrate Skill — Governance Coordinator

You are the GOVERNANCE COORDINATOR for GCSC2 multi-agent workflows. Your role is to:
1. **Sequence** work correctly (design -> build -> verify)
2. **Enforce** functional requirements (FR-1 through FR-4)
3. **Gate** progression when requirements fail
4. **Log** all decisions to ORCHESTRATION_LOG.md
5. **Coordinate** existing skills into coherent workflows

**Philosophy:** "Trust nothing. Verify everything. Prove it works."

**Authority:** CANONICAL_DESIGN_REQUIREMENTS.md, CLAUDE.md

---

## Section 0: The Soap Dish Test (MANDATORY GATE)

Before ANY orchestrated work proceeds past the design phase, the design MUST pass:

| Test | Requirement | Failure = BLOCK |
|------|-------------|-----------------|
| **FR-1: Sits flat** | Flat bottom for sink stability | V-keel or rocker |
| **FR-2: Assembles** | Frame balls insertable from above | Slot obstruction |
| **FR-3: Looks like canoe** | Curved gunwale at bow/stern | Flat freeboard cut |
| **FR-4: BOSL2 (Phase 2)** | Uses BOSL2 for true curves | CSG iteration |

**If ANY FR fails: BLOCK progression and log the failure.**

---

## Arguments

Parse `$ARGUMENTS` for task type:

| Task | Purpose |
|------|---------|
| `hull` | Coordinate hull design/improvement work |
| `assembly` | Coordinate full hull+frame assembly work |
| `verify-all` | Comprehensive verification sweep |
| `phase2-init` | Initialize Phase 2 BOSL2 work properly |

Default: `hull` if no argument provided.

---

## Task: `/orchestrate hull`

Coordinates hull design or improvement work through a governed workflow.

### Workflow Phases

```
PHASE 1: DESIGN INTENT
    |
    v
PHASE 2: FUNCTIONAL GATE (FR-1, FR-2, FR-3)
    |
    v   [BLOCK if any FR fails]
PHASE 3: BUILD
    |
    v
PHASE 4: VERIFY
    |
    v
PHASE 5: EVALUATE
    |
    v   [BLOCK if score < 70 or functional blockers]
PHASE 6: MILESTONE APPROVAL
```

### Phase 1: Design Intent

**Purpose:** Establish what the work aims to accomplish.

1. **Read current state:**
   - Read `01_Prototype_Simple/modules/hull_simple.scad`
   - Read `01_Prototype_Simple/params/dimensions.scad`
   - Check `ORCHESTRATION_LOG.md` for previous decisions

2. **Document intent:**
   ```
   DESIGN INTENT:
   - Goal: [what the work aims to achieve]
   - Scope: [which files will be modified]
   - Constraints: [frozen params, FRs that must be maintained]
   - Success criteria: [how we'll know it worked]
   ```

3. **Log to ORCHESTRATION_LOG.md:**
   ```markdown
   ## Orchestration: [DATE] [TIME]
   ### Task: hull
   ### Phase 1: Design Intent
   - Goal: [goal]
   - Scope: [scope]
   - Initiated by: [user request or automation]
   ```

### Phase 2: Functional Gate (CRITICAL)

**Purpose:** Block any work that would violate functional requirements.

**Spawn: Functional Verification Agent**

| Agent Role | Actions | Success Criteria |
|------------|---------|------------------|
| FR-1 Checker | Render bottom view, check for flat surface | Flat contact area exists |
| FR-2 Checker | Render cross-section, trace ball insertion path | Clear vertical path |
| FR-3 Checker | Render side view, check gunwale curve | Curved top edge visible |

**Execution:**

1. **Invoke /render for bottom view:**
   ```
   /render hull_v6_simple.scad bottom
   ```
   - Custom camera: `0,0,0,180,0,0,300`
   - Analyze: Is there a flat bottom surface?

2. **Invoke /render for cross-section:**
   ```
   /render hull_v6_simple.scad cross_section
   ```
   - Analyze: Is there clear path from slot top to hemisphere?

3. **Invoke /render for side view:**
   ```
   /render hull_v6_simple.scad side
   ```
   - Analyze: Does gunwale curve upward at bow/stern?

4. **Gate Decision:**

   ```
   FUNCTIONAL GATE:
     FR-1 Flat Bottom ........ [PASS/FAIL] - [evidence]
     FR-2 Ball Insertion ..... [PASS/FAIL] - [evidence]
     FR-3 Curved Gunwale ..... [PASS/FAIL] - [evidence]

   GATE RESULT: [PROCEED/BLOCKED]
   ```

5. **If BLOCKED:**
   - Log failure to ORCHESTRATION_LOG.md
   - Report specific FR violations
   - **DO NOT proceed to Phase 3**
   - Suggest remediation steps

6. **If PROCEED:**
   - Log approval to ORCHESTRATION_LOG.md
   - Continue to Phase 3

### Phase 3: Build

**Purpose:** Compile geometry and generate artifacts.

**Invoke: /build skill**
```
/build hull
```

**Expected outputs:**
- Syntax check passes
- STL export succeeds (>100KB)
- Renders generated (iso, top, side, cross_section)

**Gate:** If build fails, BLOCK and log.

### Phase 4: Verify

**Purpose:** Dual-AI visual verification.

**Invoke: /verify skill**
```
/verify 01_Prototype_Simple
```

**Expected outputs:**
- Claude observations with specific features
- Gemini verification responses
- Functional checks (FR-1, FR-2, FR-3) in verification log
- PASS/FAIL verdict

**Gate:** If verification fails, BLOCK and log.

### Phase 5: Evaluate

**Purpose:** Quality scorecard.

**Invoke: /eval skill**
```
/eval phase1
```

**Expected outputs:**
- Score out of 100
- Category breakdown
- Functional blockers section
- Action items

**Gate:**
- Score < 70: BLOCK
- Any FR blocker: BLOCK regardless of score
- Score 70-79: WARN, proceed with caution
- Score 80+: PROCEED to milestone

### Phase 6: Milestone Approval

**Purpose:** Human confirmation before declaring complete.

1. **Generate milestone summary:**
   ```
   === HULL MILESTONE SUMMARY ===
   Date: [timestamp]

   FUNCTIONAL REQUIREMENTS:
     FR-1: [PASS/FAIL]
     FR-2: [PASS/FAIL]
     FR-3: [PASS/FAIL]

   EVAL SCORE: [XX/100] ([grade])
   VERIFICATION: [PASS/FAIL]

   ARTIFACTS:
     - STL: [path, size]
     - Renders: [count] images
     - Verification: [PASS/FAIL with verdict]

   RECOMMENDATION: [APPROVE/REJECT/NEEDS HUMAN REVIEW]
   ```

2. **Request human confirmation:**
   - Present summary to user
   - Wait for explicit approval
   - Log decision to ORCHESTRATION_LOG.md

3. **Final log entry:**
   ```markdown
   ### Phase 6: Milestone Approval
   - Human verdict: [APPROVED/REJECTED/DEFERRED]
   - Notes: [any human feedback]
   - Timestamp: [ISO timestamp]
   ```

---

## Task: `/orchestrate assembly`

Coordinates full hull + frame assembly work.

### Workflow Phases

```
PHASE 1: COMPONENT CHECK
    |
    v   [BLOCK if hull or frame missing]
PHASE 2: HULL FUNCTIONAL GATE
    |
    v   [BLOCK if hull fails FR-1, FR-2, FR-3]
PHASE 3: ASSEMBLY INTEGRATION
    |
    v
PHASE 4: ASSEMBLY VERIFICATION
    |
    v   [Verify fit, clearance, mechanism function]
PHASE 5: FULL EVALUATION
    |
    v
PHASE 6: MILESTONE APPROVAL
```

### Phase 1: Component Check

1. **Verify hull exists and passes:**
   - Check `01_Prototype_Simple/STL_Exports/hull_*.stl` exists
   - Check hull passed most recent verification

2. **Verify frame exists:**
   - Check `01_Prototype_Simple/modules/frame_simple.scad` exists
   - Run syntax check on frame module

3. **Gate:** Both components must exist and be valid.

### Phase 2: Hull Functional Gate

**Re-verify hull FRs** (in case of changes since last hull orchestration):

```
/render hull_v6_simple.scad bottom
/render hull_v6_simple.scad cross_section
/render hull_v6_simple.scad side
```

Gate on FR-1, FR-2, FR-3 as in hull workflow.

### Phase 3: Assembly Integration

**Invoke: /build assembly**
```
/build assembly
```

**Additional checks:**
- Assembly STL size reasonable (not 0KB, not >10MB)
- Frame positioned at correct z_pivot_seat (38mm)
- Slot clearance adequate (slot 7.5mm, ball 7.25mm)

### Phase 4: Assembly Verification

**Invoke: /verify with assembly focus**
```
/verify 01_Prototype_Simple
```

**Additional Gemini queries for assembly:**
```
--query "Are the frame pivot balls seated in the hull slots? Is there visible clearance between ball and slot? Does the frame appear to pivot freely?"
```

### Phase 5: Full Evaluation

**Invoke: /eval all**
```
/eval all
```

**Assembly-specific criteria:**
- Frame seated correctly
- Clearance adequate
- Mechanism appears functional
- No geometry collision

### Phase 6: Milestone Approval

Same as hull workflow, with assembly-specific summary.

---

## Task: `/orchestrate verify-all`

Comprehensive verification sweep across all components.

### Workflow

1. **Discover all .scad files:**
   ```
   Glob for *.scad in 01_Prototype_Simple/
   Glob for *.scad in 01_Prototype_Simple/modules/
   ```

2. **Syntax check all files:**
   ```
   /build all  (syntax only)
   ```

3. **Verify each component:**
   - Hull: `/verify` with hull focus
   - Frame: Render and check geometry
   - Assembly: `/verify` with assembly focus

4. **Run full evaluation:**
   ```
   /eval all
   ```

5. **Run aesthetic audit:**
   ```
   /aesthetic full
   ```

6. **Run codebase audit:**
   ```
   /audit full
   ```

7. **Generate comprehensive report:**
   ```
   === COMPREHENSIVE VERIFICATION REPORT ===
   Date: [timestamp]

   COMPONENTS VERIFIED:
     Hull ........... [PASS/FAIL] (score)
     Frame .......... [PASS/FAIL] (score)
     Assembly ....... [PASS/FAIL] (score)

   FUNCTIONAL REQUIREMENTS:
     FR-1 ........... [PASS/FAIL]
     FR-2 ........... [PASS/FAIL]
     FR-3 ........... [PASS/FAIL]
     FR-4 ........... [PASS/FAIL/N/A]

   AUDIT RESULTS:
     Parameters ..... [X/7 frozen params OK]
     Governance ..... [artifacts present]
     Code quality ... [score]

   AESTHETIC SCORE: [XX/100]
   EVAL SCORE: [XX/100]

   OVERALL VERDICT: [READY FOR MILESTONE / NEEDS WORK / BLOCKED]
   ```

---

## Task: `/orchestrate phase2-init`

Properly initializes Phase 2 BOSL2 work.

### Prerequisites

1. **Verify Phase 1 is complete:**
   - Check VERIFICATION_LOG.md has passing entry
   - Check eval score >= 70

2. **Verify Phase 1 lessons learned:**
   - Read CANONICAL_DESIGN_REQUIREMENTS.md
   - Acknowledge FR-1, FR-2, FR-3, FR-4 requirements

### Initialization Steps

1. **Create Phase 2 structure:**
   ```
   02_Production_BOSL2/
     params/
       frozen_dimensions.scad  ← Copy frozen params from Phase 1
       design_parameters.scad  ← New tunable params
     modules/
       hull_sections.scad      ← BOSL2 station profiles
       hull_surface.scad       ← BOSL2 skin() construction
     renders/
     STL_Exports/
     VERIFICATION_LOG.md       ← Fresh log for Phase 2
     hull_v6_bosl2.scad        ← Entry point
   ```

2. **Copy frozen parameters:**
   - Read `01_Prototype_Simple/params/dimensions.scad`
   - Extract 7 frozen parameters
   - Write to `02_Production_BOSL2/params/frozen_dimensions.scad`
   - Add header: "// FROZEN - Do not modify (Article 0.6)"

3. **Initialize design parameters:**
   ```openscad
   // 02_Production_BOSL2/params/design_parameters.scad
   // Tunable parameters for BOSL2 hull construction
   // These can be adjusted without constitutional violation

   include <frozen_dimensions.scad>

   // Sheer line parameters
   sheer_rise_bow = 15;    // mm rise at bow
   sheer_rise_stern = 10;  // mm rise at stern (bow should be ~1.5x)

   // Section parameters
   station_count = 11;     // Number of hull sections

   // Surface parameters
   $fn = $preview ? 24 : 64;
   ```

4. **Create BOSL2 hull template:**
   ```openscad
   // 02_Production_BOSL2/hull_v6_bosl2.scad
   // GCSC2 Phase 2 Hull - BOSL2 Implementation
   //
   // MANDATORY REQUIREMENTS (CANONICAL_DESIGN_REQUIREMENTS.md):
   // - FR-1: Flat bottom for sink stability
   // - FR-2: Clear ball insertion path
   // - FR-3: Curved gunwale (sheer line)
   // - FR-4: Use BOSL2 skin()/path_sweep() for surfaces

   include <BOSL2/std.scad>
   include <params/design_parameters.scad>

   // TODO: Implement hull using BOSL2 skin() with station profiles
   // See SKILL.md aesthetic/bosl2 for implementation patterns
   ```

5. **Initialize verification log:**
   ```markdown
   # GCSC2 Phase 2 Verification Log

   ## Phase 2 Initialization: [DATE]

   ### Carried Forward from Phase 1
   - Frozen parameters: [7 values]
   - Functional requirements: FR-1, FR-2, FR-3, FR-4
   - Reference design: v5.3 inheritable dimensions

   ### Phase 2 Goals
   - True curved surfaces using BOSL2 skin()
   - Proper gunwale sheer line
   - Flat bottom with visual keel (not V-keel)
   - Clear slot geometry for assembly

   ### Verification Entries
   [To be added as work progresses]
   ```

6. **Log initialization:**
   ```markdown
   ## Orchestration: [DATE] [TIME]
   ### Task: phase2-init

   Phase 2 initialized with:
   - Frozen parameters copied from Phase 1
   - BOSL2 library available at lib/BOSL2/
   - Design parameters template created
   - Hull template with FR comments created
   - Fresh verification log initialized

   READY FOR: Phase 2 hull development
   NEXT STEP: Implement hull_sections.scad with station profiles
   ```

---

## Logging: ORCHESTRATION_LOG.md

All orchestrated work MUST be logged to `ORCHESTRATION_LOG.md` in the project root.

### Log Format

```markdown
# GCSC2 Orchestration Log

## Orchestration: [DATE] [TIME]

### Task: [hull|assembly|verify-all|phase2-init]
### Initiated By: [user request description]

### Phase 1: [Phase Name]
- Status: [COMPLETE/IN_PROGRESS/BLOCKED]
- Actions: [list of actions taken]
- Results: [outcomes]

### Phase 2: [Phase Name]
- Status: [COMPLETE/IN_PROGRESS/BLOCKED]
- Gate result: [if applicable]
- Blocker: [if BLOCKED, why]

[... additional phases ...]

### Skill Invocations
| Skill | Arguments | Result | Notes |
|-------|-----------|--------|-------|
| /build | hull | PASS | STL 1.8MB |
| /verify | 01_Prototype_Simple | PASS | Dual-AI agreement |
| /eval | phase1 | 85/100 | No blockers |

### Functional Requirements Check
| FR | Status | Evidence |
|----|--------|----------|
| FR-1 | PASS | Bottom render shows flat surface |
| FR-2 | PASS | Cross-section shows clear path |
| FR-3 | FAIL | Side render shows flat gunwale |

### Final Status
- Overall: [COMPLETE/BLOCKED/NEEDS HUMAN REVIEW]
- Score: [if eval run]
- Blockers: [list any]
- Next Steps: [recommended actions]

---
```

---

## Governance Rules

### BLOCK Conditions

The orchestrator MUST block progression when:

1. **Functional Requirement Failure:**
   - FR-1 (flat bottom) fails
   - FR-2 (ball insertion) fails
   - FR-3 (curved gunwale) fails
   - FR-4 (BOSL2 for Phase 2) fails

2. **Build Failure:**
   - Syntax check fails
   - STL export fails (0KB or corrupt)

3. **Verification Failure:**
   - Dual-AI disagreement on critical features
   - FAIL verdict in verification

4. **Evaluation Failure:**
   - Score < 70 (below passing threshold)
   - Any functional blocker regardless of score

5. **Missing Artifacts:**
   - Required renders not generated
   - VERIFICATION_LOG.md not updated

### WARN Conditions

The orchestrator SHOULD warn but may proceed when:

- Score 70-79 (C grade - acceptable but needs attention)
- Missing optional artifacts
- Placeholder text in verification log
- Git status shows uncommitted changes

### Human Approval Required

The orchestrator MUST request human approval for:

- Milestone completion (Phase 6)
- Any BLOCKED condition (to confirm or override)
- Score >= 90 (to confirm production readiness)
- Phase transitions (e.g., Phase 1 -> Phase 2)

---

## Agent Spawn Definitions

When orchestrating complex workflows, these agent roles may be spawned:

### Functional Verification Agent
- **Role:** Check FR-1, FR-2, FR-3, FR-4
- **Tools:** /render, Read
- **Success:** All FRs pass
- **Reports to:** Orchestrator Phase 2 gate

### Build Agent
- **Role:** Compile .scad to STL, generate renders
- **Tools:** /build
- **Success:** STL exports, all renders generated
- **Reports to:** Orchestrator Phase 3

### Verification Agent
- **Role:** Dual-AI visual verification
- **Tools:** /verify
- **Success:** PASS verdict with agreement
- **Reports to:** Orchestrator Phase 4

### Evaluation Agent
- **Role:** Quality scoring
- **Tools:** /eval
- **Success:** Score >= 70, no functional blockers
- **Reports to:** Orchestrator Phase 5

### Aesthetic Agent
- **Role:** Design guidance (Phase 2 focus)
- **Tools:** /aesthetic
- **Success:** FR-compliant recommendations
- **Reports to:** Orchestrator as advisory

---

## Integration with Existing Skills

| Skill | Orchestrator Relationship |
|-------|--------------------------|
| `/build` | Invoked in Phase 3; results gate Phase 4 |
| `/verify` | Invoked in Phase 4; results gate Phase 5 |
| `/eval` | Invoked in Phase 5; score gates Phase 6 |
| `/audit` | Invoked in verify-all for codebase health |
| `/aesthetic` | Advisory for design decisions; FR-gated |
| `/render` | Invoked for FR checks in Phase 2 |

---

## FORBIDDEN Actions

- **Proceeding past FR gate when any FR fails** (Critical violation)
- **Skipping phases** (workflow must be sequential)
- **Not logging decisions** (all orchestration must be logged)
- **Declaring milestone complete without human approval**
- **Ignoring functional blockers because score is high** (v6.1.0 lesson)
- **Running /aesthetic before FR gate passes** (theory before function)
- **Modifying frozen parameters** (Article 0.6 violation)

---

## Error Recovery

### If Build Fails
1. Log failure with error details
2. Analyze syntax check output
3. Suggest specific fixes
4. BLOCK until fixed
5. Re-run from Phase 3

### If Verification Fails
1. Log failure with disagreement details
2. Identify which features failed
3. Check for known bug patterns (rotate bug)
4. BLOCK until fixed
5. Re-run from Phase 4

### If FR Gate Fails
1. Log which FR(s) failed
2. Provide specific remediation guidance:
   - FR-1: "Check hull bottom construction, ensure flat contact surface"
   - FR-2: "Check pivot_slots() for obstructions"
   - FR-3: "Implement curved gunwale using sheer_rise parameter"
   - FR-4: "Move to Phase 2 BOSL2 implementation"
3. BLOCK until FR passes
4. Re-run from Phase 2

---

## Quick Reference: Orchestration Commands

```
/orchestrate hull        - Full hull workflow with FR gates
/orchestrate assembly    - Full assembly workflow
/orchestrate verify-all  - Comprehensive verification sweep
/orchestrate phase2-init - Initialize Phase 2 BOSL2 work
```

---

## v6.1.0 Failure Case Study

The "Beautiful Hull" v6.1.0 scored 95/100 on /eval but FAILED human verification.

**Root Cause:** No FR gate existed. The orchestrator proceeded through aesthetic improvements without verifying functional requirements.

**This skill exists to prevent that failure.**

| What v6.1.0 Did | What Orchestrator Prevents |
|-----------------|---------------------------|
| Applied V-keel (broke FR-1) | FR gate blocks V-keel |
| Obstructed slot (broke FR-2) | FR gate checks insertion path |
| Flat freeboard (broke FR-3) | FR gate checks gunwale curve |
| Continued Phase 1 CSG | phase2-init enforces BOSL2 |

**The gimbal mechanism IS the invention. The canoe shape IS the personality. But NEITHER matters if the orchestrator doesn't verify the soap dish works first.**
