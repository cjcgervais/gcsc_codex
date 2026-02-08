---
name: aesthetic
description: Deep aesthetic research for canoe hull design. Applies naval architecture principles, BOSL2 best practices, and bathroom product philosophy to inform OpenSCAD development decisions.
argument-hint: "[scope: hull|form|material|bosl2|full|research <topic>]"
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, Task, WebSearch, WebFetch, mcp__gcsc-openscad__render_file, mcp__gcsc-openscad__render_standard_views
---

# Aesthetic Research Skill

You are executing the GCSC2 aesthetic research protocol. This skill applies deep design
research to inform OpenSCAD model development, drawing on naval architecture, bathroom
product philosophy, and BOSL2 technical best practices.

**Philosophy:** "The gimbal mechanism IS the invention. The canoe shape IS the personality."

**CRITICAL WARNING:** The v6.1.0 "Beautiful Hull" FAILED human verification despite
scoring 95/100 on automated eval. This skill was the root cause - it recommended
naval architecture improvements (V-keel, asymmetric sheer) that broke functional
requirements. Aesthetic improvements that break functionality are NOT improvements.

---

## Section 0: FUNCTIONAL PREREQUISITES (MANDATORY)

**Authority:** CANONICAL_DESIGN_REQUIREMENTS.md
**Status:** ALL aesthetic analysis MUST validate these requirements FIRST

Before ANY aesthetic recommendation, you MUST verify the design passes these non-negotiable
functional requirements. Aesthetic improvements that violate any FR are FORBIDDEN.

### FR-1: Flat Bottom for Sink Stability

**Requirement:** The hull MUST have a flat bottom surface that sits stably on a bathroom counter.

**Verification:**
- Bottom view render shows flat contact surface
- No V-keel, rocker, or rounded bottom that causes tipping

**FORBIDDEN Aesthetic Changes:**
- Adding V-keel for "authentic canoe character"
- Increasing deadrise angle to create "hydrodynamic form"
- Any bottom geometry that prevents stable resting

**Correct Approach:**
- Visual keel LINE (decorative ridge on flat bottom) is acceptable
- Deadrise can exist ABOVE the flat contact zone
- Soap dish sits flat = functional; looks like canoe = aesthetic

### FR-2: Frame Ball Insertion Path

**Requirement:** Frame pivot balls MUST be insertable into hull slots from above without obstruction.

**Verification:**
- Cross-section render at y=slot_y_position
- Clear vertical path from slot top to hemisphere seat
- Ball diameter (7.25mm) fits through entire slot length (7.5mm slot diameter)

**FORBIDDEN Aesthetic Changes:**
- Adding decorative elements near slots that obstruct insertion
- Thickening gunwale in ways that narrow slot openings
- Any geometry that blocks the ball entry path

**Correct Approach:**
- Slot geometry is FROZEN for functional reasons
- Aesthetic work must AVOID the slot zones entirely
- If you can't see clear vertical path in cross-section, design is BROKEN

### FR-3: Curved Gunwale (THE Canoe Aesthetic)

**Requirement:** The top edge of the hull MUST have the characteristic curved profile rising at bow and stern.

**CRITICAL INSIGHT:** The curved gunwale IS the defining canoe aesthetic feature. This is
what makes people recognize it as a canoe. Naval architecture details (section progression,
tumblehome, deadrise) are secondary and invisible to most observers.

**Verification:**
- Side view render shows curved top edge rising toward bow and stern
- NOT a straight horizontal line (flat freeboard cut)
- Sweep should be continuous and fair

**This is WHERE aesthetic work should focus:**
- Sheer line curvature (the gunwale sweep)
- Bow/stern rise ratio (traditional: bow 1.5x stern)
- Continuity and fairness of the curve

### FR-4: BOSL2 Implementation for True Curves

**Requirement:** Phase 2 designs MUST use BOSL2 library for parametric hull construction.

**Rationale:**
- Phase 1 CSG primitives (hull() of spheres) CANNOT produce true curved surfaces
- Aesthetic improvements to Phase 1 geometry yield diminishing returns
- BOSL2 provides skin(), path_sweep(), bezier curves for proper hull fairing

**FORBIDDEN Actions:**
- Continuing to iterate aesthetic improvements on Phase 1 hull_simple.scad
- Recommending CSG-based approaches for smooth curves

**Correct Approach:**
- Acknowledge Phase 1 limitations explicitly
- Direct aesthetic recommendations toward Phase 2 BOSL2 implementation
- Use Phase 1 only for functional validation, not aesthetic refinement

### The Soap Dish Test (MANDATORY VALIDATION)

Before ANY aesthetic recommendation is considered valid, confirm the design passes:

| Test | Question | Required Answer |
|------|----------|-----------------|
| **Sits flat** | Does it rest stably on a flat surface? | YES |
| **Assembles** | Can the frame balls be inserted from above? | YES |
| **Holds soap** | Is there adequate interior volume? | YES |
| **Drains** | Can water escape (not pool inside)? | YES |
| **Looks like canoe** | Would a person recognize it as a miniature canoe? | YES |

**If ANY answer is NO, aesthetic analysis STOPS until functional issue is fixed.**

---

## Arguments

Parse `$ARGUMENTS` for scope:
- `hull` - Canoe hull form analysis (gunwale curves, visual proportions)
- `form` - Form factor optimization within frozen parameters
- `material` - Material selection and finish recommendations
- `bosl2` - BOSL2 implementation patterns for Phase 2
- `full` - Complete aesthetic audit across all dimensions
- `research <topic>` - Deep research mode on a specific topic

---

## Research Foundation Documents

Before execution, ensure you have read and understood these foundational documents:

| Document | Path | Contents |
|----------|------|----------|
| Canonical Requirements | `CANONICAL_DESIGN_REQUIREMENTS.md` | MANDATORY functional requirements |
| Canoe Hull Aesthetics | `docs/CANOE_HULL_AESTHETICS_GUIDE.md` | Naval architecture (apply with caution) |
| Bathroom Product Philosophy | `docs/BATHROOM_PRODUCT_AESTHETIC_PHILOSOPHY.md` | Cultural context, market positioning |
| BOSL2 Guide (inline) | See Section 6 below | Technical implementation patterns |
| Frozen Parameters | `01_Prototype_Simple/params/dimensions.scad` | Immutable constraints |

---

## Scope: Hull Form Analysis

When `$ARGUMENTS` includes `hull`:

### Step 1: Functional Prerequisites Check

**MANDATORY FIRST STEP:** Before any aesthetic analysis, verify:

1. Read `01_Prototype_Simple/modules/hull_simple.scad`
2. Render bottom view - confirm flat contact surface exists
3. Render cross-section at slot - confirm clear ball insertion path
4. Render side view - confirm curved gunwale (not flat freeboard cut)

**If any check fails, STOP and report functional issue before proceeding.**

### Step 2: Load Context

1. Read `01_Prototype_Simple/params/dimensions.scad`
2. Read `docs/CANOE_HULL_AESTHETICS_GUIDE.md` (apply with functional grounding)
3. Read current renders in `01_Prototype_Simple/renders/`

### Step 3: Analyze Gunwale Curve (THE Primary Aesthetic Feature)

The sheer line (gunwale curve) is the SINGLE MOST IMPORTANT aesthetic feature.
This is what makes people recognize the object as a canoe.

| Aspect | Current | Assessment | Recommendation |
|--------|---------|------------|----------------|
| Continuity | [evaluate] | Smooth curve or flat sections? | Must be continuous |
| Rise at bow | [measure] | Sufficient drama? | 10-25% of freeboard |
| Rise at stern | [measure] | Proper ratio to bow? | Bow should be 1.5x stern |
| Fairness | [evaluate] | Any flat spots or kinks? | Must be mathematically fair |

### Step 4: Analyze Visual Proportions (Secondary)

These are less important than gunwale curve but contribute to overall form:

| Feature | Current Value | Assessment |
|---------|---------------|------------|
| L/B Ratio | 148/64 = 2.31:1 | Stubby but intentional for soap dish |
| Freeboard/Beam | 45/64 = 0.70 | High-sided, appropriate |
| Tumblehome | 8 degrees | Within optimal range (5-12) |

**NOTE:** These ratios are largely FROZEN. Do not recommend changes.

### Step 5: Identify Improvement Opportunities (Within Functional Constraints)

**PERMITTED improvements:**

1. **Sheer Line Enhancement** (FR-3 compliant)
   - Adjust curvature for better visual sweep
   - Implement differential sheer (bow 1.5x stern)
   - Ensure fairness (no flat spots)

2. **Visual Keel Line** (FR-1 compliant)
   - Decorative ridge on FLAT bottom
   - Does NOT create V-keel or tipping
   - Visual interest without functional compromise

3. **Surface Detailing** (FR-2 compliant)
   - Must AVOID slot zones
   - Surface texture for visual interest
   - Gunwale edge profile

**FORBIDDEN improvements:**

- V-keel (violates FR-1)
- Slot zone modifications (violates FR-2)
- Flat freeboard cut (violates FR-3)
- Any change to frozen parameters

### Step 6: Generate Hull Assessment Report

```
=== HULL AESTHETIC ASSESSMENT ===
Date: [timestamp]

FUNCTIONAL PREREQUISITES:
  FR-1 Flat Bottom ............ [PASS/FAIL]
  FR-2 Ball Insertion ......... [PASS/FAIL]
  FR-3 Curved Gunwale ......... [PASS/FAIL]
  FR-4 Phase Appropriate ...... [PASS/FAIL - Phase 1 or 2?]

SOAP DISH TEST:
  Sits flat? .................. [YES/NO]
  Assembles? .................. [YES/NO]
  Holds soap? ................. [YES/NO]
  Drains? ..................... [YES/NO]
  Looks like canoe? ........... [YES/NO]

[If any FAIL/NO above, STOP - fix functional issues first]

GUNWALE CURVE ANALYSIS (Primary Aesthetic):
  Continuity .................. [score/10]
  Drama/Rise .................. [score/10]
  Bow/Stern Ratio ............. [score/10]
  Fairness .................... [score/10]

VISUAL PROPORTIONS (Secondary):
  Overall balance ............. [assessment]
  Tumblehome execution ........ [assessment]

RECOMMENDATIONS (functionally grounded):
  1. [Improvement that maintains all FRs]
  2. [Improvement that maintains all FRs]
  3. [Consider Phase 2 BOSL2 for: ...]

PARAMETER ADJUSTMENTS (non-frozen, FR-compliant):
  sheer_rise: [current] → [suggested] (if any)
  [Note: Most params are frozen or require BOSL2]
```

---

## Scope: Form Factor Optimization

When `$ARGUMENTS` includes `form`:

### Step 1: Functional Prerequisites Check

**MANDATORY:** Verify FR-1 through FR-4 pass before any analysis.

### Step 2: Load Context

1. Read `01_Prototype_Simple/params/dimensions.scad` (frozen params)
2. Review current renders in `01_Prototype_Simple/renders/`
3. Read reference images if available

### Step 3: Analyze Within Constraints

The frozen parameters define an immutable envelope:
- **LOA**: 148mm (length) - FROZEN
- **beam**: 64mm (width) - FROZEN
- **freeboard**: 45mm (height) - FROZEN
- **z_pivot_seat**: 38mm (frame attachment) - FROZEN
- **slot_diameter**: 7.5mm (pivot geometry) - FROZEN
- **frame_x_offset**: 16mm (frame position) - FROZEN
- **slot_y_position**: 31mm (frame Y position) - FROZEN

**Within these constraints, evaluate:**

1. **Canoe Recognition** (most important)
   - Does the curved gunwale read as "canoe"?
   - Are bow/stern tips sufficiently pointed?
   - Is there appropriate visual taper toward ends?

2. **Gimbal Frame Visibility**
   - Is the mechanism visible and celebrated?
   - Does frame contrast with hull?
   - Are pivot balls adequately prominent?

3. **Functional Surface Features**
   - Drainage provisions present?
   - Appropriate wall thickness for scale?
   - Gunwale profile defined?

### Step 4: Soap Accommodation Check

Reference: Standard soap bar 80x76x25mm, classic artisan 89x64x25mm

| Dimension | Available | Required | Margin |
|-----------|-----------|----------|--------|
| Interior Length | ~134mm | 89mm | +45mm (good) |
| Interior Beam | ~50mm | 64mm | -14mm (overhangs rails) |
| Frame Span | 60mm | 64mm | -4mm (slight overhang) |

Verdict: Soap accommodation is [adequate/insufficient/optimal]

### Step 5: Generate Form Factor Report

```
=== FORM FACTOR OPTIMIZATION REPORT ===
Date: [timestamp]

FUNCTIONAL PREREQUISITES: [All PASS required]

CANOE RECOGNITION (Primary Goal):
  Curved gunwale visible? ..... [YES/NO]
  Bow/stern pointed? .......... [YES/NO]
  Would observers say "canoe"? . [YES/NO]

ENVELOPE UTILIZATION:
  Length axis ................. [assessment]
  Beam utilization ............ [assessment]
  Vertical presence ........... [assessment]

VISUAL BALANCE:
  Gunwale sweep ............... [score/10]
  Mechanism visibility ........ [score/10]
  Surface treatment ........... [score/10]

RECOMMENDATIONS (FR-compliant):
  1. [High priority - maintains all FRs]
  2. [Medium priority - maintains all FRs]
  3. [Phase 2 BOSL2 opportunity]
```

---

## Scope: Material Selection

When `$ARGUMENTS` includes `material`:

### Step 1: Context

Review `docs/BATHROOM_PRODUCT_AESTHETIC_PHILOSOPHY.md` for color psychology
and material language research.

### Step 2: Evaluate Material Options

**Tier 1: Most Canoe-Like**

| Material | Effect | Layer Line Hiding | Post-Processing |
|----------|--------|-------------------|-----------------|
| Wood PLA (Walnut) | Authentic grain | Excellent | Sandable, stainable |
| Wood PLA (Cherry) | Warm red-brown | Excellent | Sandable, stainable |
| Matte Brown PLA | Uniform color | Good | Standard |
| Matte Forest Green | Traditional canoe | Good | Standard |

**Tier 2: Modern/Distinctive**

| Material | Effect | Best Use Case |
|----------|--------|---------------|
| Clear PETG | Show mechanism | Demonstration model |
| Bright Red | High visibility | Gift/toy market |
| Navy Blue | Nautical theme | Maritime aesthetic |

**Tier 3: Multi-Material**

| Combination | Effect |
|-------------|--------|
| Wood hull + white frame | Mechanism pop |
| Red hull + cream frame | Toy aesthetic |
| Clear hull + colored frame | Maximum mechanism visibility |

### Step 3: Finish Recommendations

| Surface | Treatment | Purpose |
|---------|-----------|---------|
| Hull exterior | Light sand (400 grit) | Smooth touch |
| Gunwale edge | Round-over, polish | Comfortable grip |
| Frame rails | Slight texture | Soap grip |
| Pivot balls | Smooth | Free movement |

### Step 4: Generate Material Report

```
=== MATERIAL SELECTION GUIDE ===
Target Market: [persona description]

RECOMMENDED PRIMARY:
  Hull: [material] in [color]
  Frame: [material] in [color]

PRINT SETTINGS:
  Layer height: [value]
  Orientation: [description]
  Supports: [yes/no, where]

POST-PROCESSING:
  [Step-by-step finishing guide]

ALTERNATIVES:
  Premium edition: [description]
  Economy edition: [description]
```

---

## Scope: BOSL2 Implementation

When `$ARGUMENTS` includes `bosl2`:

### Step 1: Context

Phase 2 production work uses BOSL2 (installed at `02_Production_BOSL2/lib/BOSL2/`).

**CRITICAL:** BOSL2 is REQUIRED for true curved surfaces. Phase 1 CSG cannot achieve
the aesthetic quality needed for production. Do not waste effort refining Phase 1.

### Step 2: Hull Construction Pattern

**Recommended Approach: `skin()` with Parametric Stations**

```openscad
include <BOSL2/std.scad>

// Define stations from bow (-LOA/2) to stern (+LOA/2)
function station_positions() = lerpn(-LOA/2, LOA/2, 11);

// Generate cross-section at each station
function station_profile(x) =
    let(
        t = (x + LOA/2) / LOA,  // 0 at bow, 1 at stern
        local_beam = beam * sin(t * 180),  // Parabolic distribution
        local_depth = freeboard * (0.3 + 0.7*sin(t * 180))
    )
    ellipse_section(local_beam/2, local_depth);

// Construct hull surface
profiles = [for (x = station_positions()) station_profile(x)];
skin(profiles, slices=4, method="distance", caps=true);
```

### Step 3: BOSL2 Hull Must Satisfy Functional Requirements

**FR-1 Compliance (Flat Bottom):**
```openscad
// Station profile must have flat bottom section
function station_profile(x) =
    let(
        // ... beam and depth calculations ...
        flat_zone = 10,  // mm of flat bottom
        // Create profile with flat bottom, then curved sides
    )
    // Use path operations to ensure flat bottom contact surface
```

**FR-2 Compliance (Slot Geometry):**
```openscad
// Slot cutouts must use correct rotation
module pivot_slots() {
    // CORRECT: rotate([90, 0, 0]) - slots open port/starboard
    // WRONG: rotate([0, 90, 0]) - slots aligned fore/aft (invisible)
    rotate([90, 0, 0]) cylinder(d=slot_diameter, h=beam);
}
```

**FR-3 Compliance (Curved Gunwale):**
```openscad
// Gunwale curve defined explicitly
function sheer_rise(x) =
    let(t = abs(x) / (LOA/2))
    sheer_base * (1 - (1-t)^2);  // Parabolic rise toward ends
```

### Step 4: Key BOSL2 Functions for Hull Work

| Function | Purpose | When to Use |
|----------|---------|-------------|
| `skin()` | Loft between sections | Main hull surface |
| `path_sweep()` | Sweep shape along path | Alternative hull method |
| `bezier_curve()` | Fair curves | Sheer line, keel line |
| `smooth_path()` | Continuous curvature | Gunwale edge |
| `lerp()` / `lerpn()` | Interpolation | Station parameters |
| `vnf_vertex_array()` | Direct mesh | Maximum control |
| `offset()` | 2D shell | Cross-section hollowing |

### Step 5: Performance Guidelines

| Context | $fn | $fs | $fa |
|---------|-----|-----|-----|
| Preview | 24 | 2 | 12 |
| Detail check | 48 | 1 | 6 |
| Final render | 64 | 0.5 | 3 |

**Critical**: Use `$preview` conditional for fast iteration:
```openscad
$fn = $preview ? 24 : 64;
```

### Step 6: Generate BOSL2 Implementation Guide

```
=== BOSL2 IMPLEMENTATION CHECKLIST ===

FUNCTIONAL REQUIREMENTS:
  [ ] FR-1: Flat bottom contact surface verified
  [ ] FR-2: Slot geometry uses rotate([90,0,0])
  [ ] FR-3: Gunwale curve rises at bow/stern
  [ ] FR-4: Using BOSL2 skin()/path_sweep() for surfaces

FILE STRUCTURE:
  [ ] 02_Production_BOSL2/params/frozen_dimensions.scad (copy from Phase 1)
  [ ] 02_Production_BOSL2/params/design_parameters.scad (tunable params)
  [ ] 02_Production_BOSL2/modules/hull_sections.scad
  [ ] 02_Production_BOSL2/modules/hull_surface.scad
  [ ] 02_Production_BOSL2/hull_v6_bosl2.scad (entry point)

KEY PATTERNS:
  [ ] Use include <BOSL2/std.scad> in entry point
  [ ] Define sections as functions for parametric control
  [ ] Use skin() with method="distance" for organic lofting
  [ ] Apply smooth_path() to visible edges
  [ ] Use $preview conditionals for performance

SOAP DISH TEST VALIDATION:
  [ ] Sits flat - bottom render confirms flat surface
  [ ] Assembles - cross-section shows clear ball path
  [ ] Holds soap - interior volume adequate
  [ ] Drains - drainage provisions present
  [ ] Looks like canoe - side view shows curved gunwale
```

---

## Scope: Full Aesthetic Audit

When `$ARGUMENTS` includes `full`:

Execute ALL of the above scopes in sequence:
1. **Functional prerequisites check** (MANDATORY FIRST)
2. Hull form analysis
3. Form factor optimization
4. Material selection
5. BOSL2 implementation readiness

Then synthesize into a master report:

```
+======================================================+
|            GCSC2 AESTHETIC AUDIT REPORT              |
|            Date: [timestamp]                         |
+======================================================+

FUNCTIONAL PREREQUISITES (GATE)      [PASS/FAIL]
  FR-1 Flat Bottom ............. [P/F]
  FR-2 Ball Insertion .......... [P/F]
  FR-3 Curved Gunwale .......... [P/F]
  FR-4 BOSL2 (Phase 2) ......... [P/F or N/A for Phase 1]

SOAP DISH TEST (GATE)                [PASS/FAIL]
  Sits flat? ................... [Y/N]
  Assembles? ................... [Y/N]
  Holds soap? .................. [Y/N]
  Drains? ...................... [Y/N]
  Looks like canoe? ............ [Y/N]

[IF ANY GATE FAILS: STOP - Report "AESTHETIC AUDIT BLOCKED"
 and list functional issues to fix first]

+------------------------------------------------------+

GUNWALE CURVE (Primary)           [XX/30]
  Continuity ................... [score/10]
  Drama/Rise ................... [score/10]
  Fairness ..................... [score/10]

VISUAL PROPORTIONS                [XX/20]
  Overall balance .............. [score/10]
  Canoe recognition ............ [score/10]

FORM FACTOR                       [XX/20]
  Envelope utilization ......... [score/10]
  Mechanism visibility ......... [score/10]

MATERIAL/FINISH                   [XX/20]
  Material appropriateness ..... [score/10]
  Finish quality potential ..... [score/10]

BOSL2 READINESS                   [XX/10]
  Pattern compliance ........... [score/10]

+------------------------------------------------------+
  TOTAL:  [XX/100]
  GRADE:  [A/B/C/D/F]
  AESTHETIC VERDICT: [PASS/NEEDS WORK/BLOCKED BY FUNCTION]
+======================================================+
```

---

## Scope: Deep Research Mode

When `$ARGUMENTS` starts with `research`:

Parse the topic from `$ARGUMENTS` after "research".

### Research Protocol

1. **Frame the Question**
   - What specific aesthetic question needs answering?
   - What design decision will this inform?
   - **Does this question respect functional requirements?**

2. **Functional Grounding Check**
   - Before researching "how to make X more beautiful"
   - Ask: "Will any recommendation from this research violate FR-1 through FR-4?"
   - If yes, reframe the research question

3. **Search Strategy**
   - Use WebSearch with specific queries
   - Prioritize authoritative sources (naval architecture, industrial design)
   - Cross-reference multiple sources
   - **Filter for applicability** - hydrodynamics research is irrelevant for soap dish

4. **Synthesize Findings**
   - Extract quantitative data (ratios, angles, measurements)
   - Note qualitative principles (visual flow, tension, harmony)
   - **Apply functional filter** - discard recommendations that break FRs
   - Apply to GCSC2 context

5. **Document Results**
   - Add findings to appropriate research document
   - Update CANOE_HULL_AESTHETICS_GUIDE.md or BATHROOM_PRODUCT_AESTHETIC_PHILOSOPHY.md
   - Include source citations
   - **Note any discarded recommendations and WHY they were discarded**

### Research Report Format

```
=== AESTHETIC RESEARCH: [Topic] ===
Date: [timestamp]
Question: [specific question being answered]

FUNCTIONAL GROUNDING:
  FR-1 Flat Bottom impact: [none/constrained/blocked]
  FR-2 Ball Insertion impact: [none/constrained/blocked]
  FR-3 Curved Gunwale impact: [none/constrained/blocked]
  FR-4 BOSL2 Requirement: [applies/does not apply]

SOURCES CONSULTED:
- [Source 1: key finding]
- [Source 2: key finding]
- [Source 3: key finding]

SYNTHESIS:
[Consolidated understanding]

DISCARDED RECOMMENDATIONS:
[List any theoretically good ideas that violate FRs]
- [Idea]: Violates FR-[X] because [reason]

APPLICABLE TO GCSC2:
[Specific recommendations that maintain all FRs]

PARAMETER IMPACTS:
[Which non-frozen parameters should change, if any]
```

---

## Aesthetic Principles Quick Reference

From the foundational research, these principles guide all aesthetic decisions:

### From Functional Requirements (HIGHEST PRIORITY)

1. **Soap dish function FIRST** - it must sit flat, assemble, and work
2. **Curved gunwale IS the canoe** - this is THE defining visual feature
3. **Slot geometry is sacred** - never compromise for aesthetics
4. **BOSL2 for true curves** - Phase 1 CSG has inherent limitations

### From Naval Architecture (Apply With Caution)

1. **Every curve must have a reason** - no arbitrary shapes
2. **Sheer line is paramount** - defines canoe character (this aligns with FR-3)
3. ~~**Section variation creates flow**~~ - relevant for BOSL2, not visible in CSG
4. **Fairness is non-negotiable** - continuous, smooth curvature

**WARNING:** Naval architecture optimizes for hydrodynamics. GCSC is a soap dish.
Selectively apply principles that improve APPEARANCE without breaking FUNCTION.

### From Bathroom Product Philosophy

1. **Function first, form follows** - gimbal is invention, canoe is personality
2. **Earned presence** - every element justifies its place
3. **Quiet confidence** - quality commands attention, not loudness
4. **Tactile reward** - interaction creates positive emotion
5. **Story-rich simplicity** - simple to see, rich to explain
6. **Material honesty** - 3D printing as choice, not compromise

### From Form Factor Research

1. **Embrace the stubby ratio** - 2.3:1 is intentional, not failed canoe
2. **Celebrate the mechanism** - gimbal is the differentiator
3. **Curved gunwale = canoe** - this single feature creates recognition
4. **Wood PLA hides layer lines** - material solves print artifact
5. **Multi-color highlights function** - contrast shows how it works

---

## FORBIDDEN Actions

**Constitutional Violations:**
- Recommending changes to frozen parameters (Article 0.6)
- Suggesting aesthetic changes that compromise gimbal function

**Functional Requirement Violations:**
- Recommending V-keel or rounded bottom (violates FR-1)
- Modifying slot geometry for aesthetics (violates FR-2)
- Flat freeboard cut that removes curved gunwale (violates FR-3)
- Iterating aesthetics on Phase 1 CSG instead of moving to BOSL2 (violates FR-4)

**Process Violations:**
- Proceeding with aesthetic analysis when functional prerequisites fail
- Claiming aesthetic approval without specific evidence
- Using generic terms ("looks good") instead of quantified assessments
- Ignoring the research foundation documents

**Theory Over Practice Violations:**
- Prioritizing naval architecture theory over soap dish practicality
- Recommending hydrodynamic improvements (irrelevant for soap dish)
- Applying "authentic canoe" changes that break bathroom function
- Treating theoretical elegance as more important than usability

---

## Integration with Other Skills

| Skill | Relationship to /aesthetic |
|-------|---------------------------|
| `/verify` | Aesthetic quality is part of visual verification |
| `/build` | Run build to see aesthetic impact of changes |
| `/audit` | Audit checks parameter consistency including aesthetic params |
| `/eval` | Final scoring includes aesthetic criteria |
| `/render` | Quick visual check of aesthetic changes |

**CRITICAL Integration:**
- `/eval` must include Soap Dish Test criteria
- `/verify` must ask "can balls be inserted?" not just "are slots visible?"
- All skills must respect CANONICAL_DESIGN_REQUIREMENTS.md

**Typical workflow:**
```
/aesthetic hull        - Verify FRs, then identify improvement opportunities
Edit hull parameters   - Implement FR-compliant recommendations only
/render hull          - Quick visual check
/build hull           - Full render suite
/aesthetic form       - Validate improvements against Soap Dish Test
/verify               - Full verification before milestone
```

---

## Lessons Learned: v6.1.0 "Beautiful Hull" Failure

The v6.1.0 design applied this skill's naval architecture recommendations and scored
95/100 on automated evaluation. It FAILED human verification because:

| Recommendation | Result | Why It Failed |
|----------------|--------|---------------|
| Asymmetric sheer rise | Invisible | Freeboard was flat-cut, sheer only in internal CSG |
| Section progression | Subtle | CSG primitives can't express true section variation |
| V-keel character | BROKE FUNCTION | Hull tips over on bathroom counter |
| Tumblehome factor | Marginal | Scaling change, not true tumblehome |

**Root Cause:** This skill prioritized theoretical naval architecture over practical
soap dish function. The skill has been rewritten to prevent this failure mode.

**New Safeguard:** Section 0 (Functional Prerequisites) is MANDATORY and FIRST.
No aesthetic analysis proceeds until FR-1 through FR-4 are verified as passing.

---

## Summary: The Hierarchy of Concerns

1. **FUNCTION** - Does it work as a soap dish? (FR-1 through FR-4)
2. **RECOGNITION** - Does it look like a canoe? (curved gunwale)
3. **AESTHETICS** - Is the form pleasing? (proportions, fairness, finish)
4. **THEORY** - Does it follow naval architecture? (apply only if 1-3 are satisfied)

**Never let concerns at level N compromise concerns at level N-1.**
