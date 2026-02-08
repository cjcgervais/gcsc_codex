# GCSC2 Governance Constitution

**Version:** 2.1.0
**Effective Date:** 2026-02-02
**Authority:** Supreme governance document for GCSC2 project
**Supersedes:** GCSC v1-v5 Governance (archived in `00_Governance_v1-v5_DEPRECATED_REFERENCE/`)

---

## Article 0: Product Identity and Core Concept

**SUPREME AUTHORITY:** This article defines WHAT we are building. All other articles define HOW to build it. Product concept supersedes implementation details.

---

### 0.1 Product Concept and Core Innovation

**The Great Canadian Soap Canoe (GCSC)** is a revolutionary soap dish that **elevates the soap above the vessel** using a gimbaled frame mechanism, enabling drainage-free airflow drying.

---

### THE CONCEPTUAL CORNERSTONE (Creator's 5-Year Innovation)

**THIS IS THE HEART OF GCSC - 5 years of development to solve soap preservation through mechanical elevation and gimbal action.**

**Traditional soap dishes (the problem):**
- Soap sits IN the dish (rests on bottom)
- Requires drain holes to prevent water pooling
- Soap remains wet, deteriorates quickly, becomes mushy

**GCSC Innovation (the solution):**
- **Soap is ELEVATED** - Suspended on frame top members, NOT resting in hull
- **NO DRAIN HOLES** - Water drips off elevated soap to hull floor, evaporates via airflow
- **Minimal contact** - Two thin rail edges support soap (line contact, not surface contact)
- **Gimbal gripping** - Frame swing + soap weight/placement creates frictional bite
- **Airflow drying** - Open top enables evaporation, soap stays dry and lasts longer

**This is NOT a canoe. This is NOT a traditional soap dish.**
**This is a SOAP PRESERVATION device using gimbal mechanics and elevation.**

---

### Core Mechanism: Gimbal-Based Soap Elevation System

**How the innovation works:**

#### 1. Frame-Hull Gimbal Connection (CRITICAL MECHANISM)

**The Stator (Hull):**
- Hull sidewalls contain SLOTS that enable frame swing
- Slot geometry: Opens in hull sidewall, depth sufficient for ball joint
- Slot floor: CONCAVE surface that cradles the pivot ball
- Hull wall thickness: MUST be sufficient to house slots AND maintain structural integrity
- Slots positioned symmetrically on both sides of hull

**The Rotor (Frames):**
- Two inverse trapezoid frames (narrower bottom, wider at top)
- Positioned across X-axis (canoe length direction)
- Ball joints extend LATERALLY from frame sides into hull slots
- Balls seat in concave slot floor, enabling pivot action

**The Pivot Connection:**
- Frame ball joints extend laterally INTO hull sidewall slots
- Ball rests in concave slot floor (enables smooth rotation)
- Hull wall acts as BEARING for gimbal motion
- Connection allows frame to swing freely within designed limits

#### 2. Swing Limitation System (<45° Maximum)

**CRITICAL: Frames must swing freely but be LIMITED to <45° rotation**

**Why <45° limit matters:**
- Prevents frame from swinging too far (falling out, jamming)
- Ensures controlled gimbal action for soap gripping
- Maintains functional geometry for soap elevation
- Symmetrical limits on both directions of swing

**Implementation approaches (research-driven):**
- **v5.3 approach:** Canoe seat (floor rise) acts as physical swing stop
- **Alternative:** Hull geometry provides structural stop
- **Alternative:** Slot geometry limits ball travel
- **Requirement:** Some structural property of hull design MUST limit swing symmetrically

**Design constraint:**
- Whatever limits swing must be SYMMETRICAL (both sides equal)
- Must stop rotation at <45° in both directions
- Must not interfere with normal gimbal operation
- Must be robust (repeated swings, soap loading)

#### 3. Frame Geometry for Soap Support

**Frame Structure:**
- Two inverse trapezoid frames (narrower at bottom, wider at top)
- Positioned across X-axis (length of canoe)
- Top members span Y-axis (width of canoe)
- Weight distribution: Bottom heavier, creates self-righting bias

**Top Member Critical Geometry:**
- Profile: Flat top transitioning to sharp/right-angle (90°) edges
- Purpose: The edge transition creates GRIPPING BITE on soap
- Width: Spans Y-axis (frame to frame across canoe width)
- Contact: Minimal line contact, not surface contact

#### 4. Soap Placement and Gimbal Dynamics

**Soap Placement:**
- Soap bar rests ACROSS the two frame top members
- Contact: Two minimal lines along top member edges
- Position: ABOVE hull interior (elevated, not touching floor)
- Placement bias: Where soap sits determines tilt direction

**Gimbal Action:**
- Soap weight + placement creates moment arm
- Frame tilts in direction of soap placement bias
- Tilt causes edge geometry to engage (90° edge creates bite)
- Frictional containment from minimal contact + gimbal tilt
- Frames swing within <45° limit, creating variable grip strength

**Why Dimensionality Matters:**
- Frame height, width, and pivot position determine swing characteristics
- Weight distribution (bottom vs. top) affects self-righting
- Soap placement relative to pivot point creates leverage
- Edge angle + tilt angle = gripping force magnitude

#### 5. Drainage System (NO HOLES BY DESIGN)

**How water is managed:**
- Residual water drips OFF elevated soap (gravity)
- Water falls to hull floor (intentional collection)
- Open top enables airflow circulation
- Airflow evaporates water from both soap AND hull floor
- NO drain holes needed - evaporation system

**Why this works for soap preservation:**
- Soap stays dry (minimal contact, elevated)
- Air circulation prevents moisture buildup
- Water doesn't sit against soap (elevated above floor)
- Soap lasts longer, doesn't deteriorate

**This is NOT a traditional soap dish. This is soap ELEVATION technology.**
**This is NOT a canoe. This is a SOAP PRESERVATION device that HAPPENS to look like a canoe.**


### Scale and Construction

- **Size:** ~150mm length (scaled for standard bar soap ~100mm × 50mm)
- **Form:** Miniature canoe/boat aesthetic
- **Assembly:** Two-piece (hull + removable gimbaled frame)
- **Concept Origin:** GCSC_v2.6.1 (seed specification)
- **Working Reference:** v5.3 Final Assembly (Inheritable_Dimensions/)

**See:** `Inbox/GCSC_v2.6.1.md` for original concept seed


### 0.2 Fundamental Product Characteristics

**These define WHAT GCSC is at the conceptual level:**

**Form Identity:**
- **Canoe/boat aesthetic** - Pointed ends, curved sides, nautical character
- **Open-topped vessel** - No closed lid or sealed top surface
- **Hollow interior** - Contains cavity for soap accommodation
- **Two-piece design** - Separable hull and frame components

**Mechanical Identity:**
- **Stationary hull** - Base vessel, holds frame
- **Pivoting frame** - Movable component inside hull
- **Gimbal/pivot mechanism** - Frame swings/rotates to grip soap
- **Gravity interaction** - Self-righting or stabilizing behavior
- **Soap gripping action** - Frame members contact and hold soap bar

**Functional Identity:**
- **Soap accommodation** - Holds standard bar soap (~100mm × 50mm × 25mm)
- **Drainage capability** - Water does not pool (open design or deliberate drainage)
- **Stable base** - Rests securely on counter/surface
- **Accessible design** - Soap and frame can be inserted/removed from above


### 0.3 Mandatory Functional Requirements

**These are NON-NEGOTIABLE across all phases and versions:**

**FR-0: Soap Elevation and Drainage-Free Design (THE CORNERSTONE)**

**This is the defining innovation. If this is violated, it is not GCSC.**

**Soap Elevation Requirements:**
- Soap MUST be elevated ABOVE hull floor (pedestalized on frame)
- Contact: Minimal line contact on frame top member edges (NOT surface contact)
- Frame top members MUST have geometry that creates gripping bite
- Soap MUST rest ACROSS two frame top members (spanning Y-axis)
- Soap position: ABOVE hull interior, NOT touching floor

**Frame Geometry Requirements:**
- Frame shape: Inverse trapezoid or similar (narrower bottom, wider top)
- Top member profile: Flat top transitioning to sharp/right-angle edge
- Top members span Y-axis (width of canoe)
- Frame pivot mechanism enables gimbal action for gripping

**NO DRAIN HOLES Principle:**
- Hull floor MUST NOT have drain holes (by design, not omission)
- Water drips from elevated soap to hull floor (intentional)
- Water evaporates via airflow from open top
- Soap stays DRY because it's elevated with minimal contact

**Why This Matters:**
- Traditional soap dishes = soap sits in water, needs drain holes
- GCSC innovation = soap elevated, water below, airflow dries both
- This is the CORE CONCEPT that differentiates GCSC from all other soap dishes

**Test:**
- Soap bar placed on assembled frame stays elevated above hull floor
- No drain holes visible in hull floor
- Frame top members have edge geometry (not flat surface)
- Water can collect at floor without contacting elevated soap

**Authority:** Creator's conceptual cornerstone - this IS the GCSC invention

**Authority:** Creator's 5-year brainchild - this IS the GCSC invention

**This is NOT replicating a canoe. This is a NEW INVENTION for soap preservation using gimbal mechanics and elevation.**


**FR-1: Open-Top Access (Enables Airflow)**
- Hull MUST be open at the top (no sealed surface)
- Open top enables airflow circulation for evaporation
- Interior cavity MUST be accessible from above
- Frame MUST be installable/removable from top opening
- **Why Open Top:** Not just aesthetics - airflow is functional requirement for drainage-free design
- **Test:** Can see into hull from top view; air circulates freely
- **Authority:** Open top enables the evaporation system (part of FR-0 innovation)

**FR-2: Frame Gimbal Mechanism**
- Frame MUST pivot/rotate relative to hull (gimbal action)
- Pivot creates gripping bite when soap placement tilts frame
- Mechanism: pins, balls, hinges, or research-backed pivot geometry
- Gimbal effect + minimal contact edges = frictional soap containment
- **Test:** Frame demonstrably moves/tilts relative to stationary hull
- **Authority:** Gimbal action is how the gripping bite works (FR-0 mechanism)

**FR-3: Soap Bar Accommodation**
- Interior volume MUST accommodate standard soap bar (~100mm × 50mm × 25mm)
- Soap MUST rest ON frame top member edges (not in hull)
- Frame separation and geometry MUST support soap elevation
- Soap MUST be insertable/removable through top access
- **Test:** Standard soap bar rests across frame top members, stays elevated
- **Authority:** Primary functional purpose (FR-0 implementation)

**FR-4: Canoe Aesthetic Form**
- Overall shape MUST read as "boat" or "canoe" when viewed
- Pointed ends or directional form required (bow/stern character)
- Hull form must be vessel-like (not box, not cylinder)
- **Test:** Recognizable as miniature canoe by visual inspection
- **Authority:** Product name and market identity

**FR-5: Structural Stability**
- Assembled product MUST sit stable on flat surface
- Hull MUST not tip during normal use
- Frame MUST not fall out or disengage unintentionally
- **Test:** Rests securely; frame stays in place when lifted
- **Authority:** Basic usability requirement


### 0.4 What GCSC Is NOT

**Forbidden design characteristics that violate core concept:**

❌ **NOT a traditional soap dish** - Soap does NOT sit in the hull touching the floor
❌ **NOT drain-hole based** - NO drain holes in hull (water evaporates via airflow, not drains)
❌ **NOT surface-contact design** - Soap contact must be minimal EDGES, not flat surfaces
❌ **NOT a closed vessel** - Sealed top prevents airflow (violates drainage-free system)
❌ **NOT purely decorative** - Must functionally elevate and dry soap
❌ **NOT a fixed single piece** - Hull and frame must be separable
❌ **NOT a simple box** - Must have boat/vessel aesthetic character
❌ **NOT a static design** - Frame must gimbal/pivot (creates gripping bite)
❌ **NOT inaccessible** - Interior must be reachable from top

**CRITICAL VIOLATIONS (immediate rejection):**
- Adding drain holes to hull floor
- Soap resting on hull floor (not elevated)
- Flat-surface soap contact (not edge contact)
- Sealed top (prevents airflow)
- No frame gimbal action

**If any forbidden characteristic appears, the design violates Article 0.**

**Common LLM Mistakes to AVOID:**
- "Let's add drain holes" ← NO! Violates FR-0 cornerstone
- "Soap sits in the dish" ← NO! Soap is ELEVATED on frame
- "Flat top rails for comfort" ← NO! Edges create bite (FR-0)
- Assuming traditional soap dish drainage patterns


### 0.5 Reference Standards

**Canonical Working Example: v5.3 Final Assembly**

Location: `Inheritable_Dimensions/Final_Assembly/`

**Why v5.3 is the reference:**
- Proven functionality (7/7 compatibility checks)
- Physical user testing validated
- Production-ready STL files exist
- Shows concept successfully implemented

**What to reference from v5.3:**
- ✅ Visual form (what it looks like)
- ✅ Functional proof (that it works)
- ✅ Scale and proportions (soap dish size)
- ✅ Open-top geometry (visible interior)
- ✅ Frame pivot mechanism (balls in slots)

**What NOT to copy from v5.3:**
- ❌ Implementation approach (GCSC2 uses research-backed methods)
- ❌ Specific code structure (v5.x was monolithic, GCSC2 is modular)
- ❌ Parameter names (GCSC2 uses semantic naming)
- ❌ Geometric algorithms (GCSC2 researches best approaches)

**Conceptual Seed: GCSC_v2.6.1**

Location: `Inbox/GCSC_v2.6.1.md`

**Why v2.6.1 is referenced:**
- Original vision document
- Establishes core concept (canoe + gimbal + soap gripping)
- Defines functional intent

**What to extract from v2.6.1:**
- ✅ Core concept (what it is)
- ✅ Functional purpose (why it exists)
- ✅ Mechanical principle (frame pivots to grip)

**What NOT to use from v2.6.1:**
- ❌ Specific implementation (problematic design approach)
- ❌ Geometric methodology (black-boxed, bug-prone)
- ❌ Design language that didn't work
- ❌ Any implementation details


### 0.6 Visual Reference Requirements

**Required Reference Images** (to be created in `docs/reference_images/`):

**From v5.3 Final Assembly:**
1. **`v5.3_overview.jpg`** - Complete assembled canoe (shows overall form)
2. **`v5.3_top_view.jpg`** - Looking down into open hull (shows accessible interior)
3. **`v5.3_frame_detail.jpg`** - Frame component showing pivot mechanism
4. **`v5.3_with_soap.jpg`** - Functional use case (soap bar in place)
5. **`v5.3_pivot_action.jpg`** - Frame tilted/pivoted (shows mechanical action)

**Purpose of references:**
- LLMs have no persistent visual memory
- Each conversation starts without knowledge of "what GCSC looks like"
- References establish canonical appearance
- Prevents conceptual drift (closed vessels, non-canoe forms)

**Reference Usage:**
- Show to LLM at start of design work
- Compare renders against references during validation
- Use as "this is what we're making" proof


### 0.7 Validation Priority and Enforcement

**CRITICAL: Product identity validation BEFORE technical validation**

**Validation Sequence (MANDATORY):**

```
GATE 0: PRODUCT IDENTITY (Article 0 - THIS GATE)
├─ Visual: Is it open-topped? (FR-1)
├─ Visual: Does it look like a canoe? (FR-4)
├─ Mechanical: Does frame pivot? (FR-2)
├─ Functional: Can it hold soap? (FR-3)
├─ Stable: Does it sit flat? (FR-5)
└─ FAIL ANY = REJECT IMMEDIATELY

GATE 1-5: TECHNICAL VALIDATION (Article IV)
├─ Parameter sanity
├─ Build validation
├─ Manifold check
├─ Dimensional accuracy
└─ Only execute if GATE 0 PASSED
```

**Rationale:**
- Technically perfect closed vessel = 100% failure
- Slightly imperfect open canoe = refinable success
- Product identity cannot be "fixed later"


### 0.8 Phase-Specific Application

**Phase 1: Minimalist Prototyping**

Article 0 requirements apply with these interpretations:

**Minimalism applies to:**
- Code complexity (simple, readable implementations)
- Parameter count (essential dimensions only)
- Build time (quick iteration cycles)
- Aesthetic details (fair curves deferred to Phase 2)

**Minimalism does NOT apply to:**
- Functional requirements (FR-1 through FR-5 are MANDATORY)
- Product identity (must look like canoe, must be open-topped)
- Core mechanism (frame must pivot, even if simplified)

**Phase 1 Success Criteria:**
- All FR-1 through FR-5 satisfied
- Design validated through physical test print
- Proves concept works with minimal implementation

**Phase 2: Production Quality**

All Article 0 requirements remain, with enhancements:

**Phase 2 additions:**
- Improved aesthetics (fair curves, smooth surfaces, refined form)
- Enhanced mechanism (optimized pivot geometry, better tolerances)
- Production features (decorations, branding, aesthetic refinement)
- Research-backed implementation (BOSL2, advanced geometry)

**Phase 2 preserves:**
- Same core concept (FR-1 through FR-5)
- Same visual identity (canoe form)
- Same functional purpose (soap holding with pivot mechanism)

**Constitutional Principle:**

> *"Phases differ in implementation quality and aesthetic refinement, but NEVER in fundamental product identity."*


### 0.9 Design Freedom Within Constraints

**Article 0 establishes boundaries, not prescriptions:**

**What Article 0 REQUIRES:**
- Open-topped form (FR-1)
- Canoe aesthetic (FR-4)
- Pivoting frame (FR-2)
- Soap accommodation (FR-3)
- Stable base (FR-5)

**What Article 0 PERMITS (research-driven decisions):**
- Pivot mechanism type (balls/slots, hinges, pins, innovative)
- Hull geometry approach (lofting, CSG, BOSL2 skinning)
- Frame structure design (trapezoidal, rectangular, organic)
- Parameter taxonomy (as long as semantic and researched)
- Wall thickness, clearances, tolerances (as long as functional)
- Aesthetic details (sheer curves, tumblehome, decorations)

**Design Principle:**
Article 0 says "you must end up with an open-topped canoe soap dish with pivoting frame." HOW you achieve that is determined by research (Article III.1) and phase requirements (Article III.3).


### 0.10 Amendment to Existing Articles

**Article I.1 Project Identity - MODIFY:**

Current text:
> **GCSC2** is the OpenSCAD-based redesign of the Great Canadian Soap Canoe, developed under the **Universal Governor v1.1.0** framework...

Add after existing text:
> **Product Concept:** See Article 0 for complete product identity, core concept, and mandatory functional requirements.

**Article III.3 Phase Governance - ADD CLAUSE:**

Add to Phase 1 section:
> **Functional Requirements:** Article 0 (FR-1 through FR-5) are MANDATORY in Phase 1. Minimalism applies to code and parameters, NOT to product concept or core functionality.

Add to Phase 2 section:
> **Functional Requirements:** All Article 0 requirements from Phase 1 remain mandatory. Phase 2 adds aesthetic refinement and enhanced implementation, but does not alter core product concept.

**Article IV Quality Standards - ADD GATE 0:**

Add before existing 4.1:

> ### 4.0 Product Identity Validation (Gate 0)
>
> **MANDATORY FIRST GATE - Execute before all other validation**
>
> **Validation Questions:**
> 1. Is the hull open at the top? (FR-1)
> 2. Does it look like a canoe/boat? (FR-4)
> 3. Does the frame pivot/move? (FR-2)
> 4. Can it hold a soap bar? (FR-3)
> 5. Does it sit stable on a surface? (FR-5)
>
> **Enforcement:**
> - ANY "no" answer = IMMEDIATE FAILURE
> - Do not proceed to Gates 1-5 if Gate 0 fails
> - Error message: "Article 0 violation: [specific FR]"
> - Compare visual renders to v5.3 reference images
>
> **Authority:** Article 0 (Product Identity) supersedes technical validation



---


## Article I: Foundational Principles

### 1.1 Project Identity

**GCSC2** is the OpenSCAD-based redesign of the Great Canadian Soap Canoe, developed under the **Universal Governor v1.1.0** framework with the following core identity:

- **Primary Tool:** OpenSCAD (CSG and BOSL2)
- **Development Environment:** Claude Code CLI
- **Governance Model:** Research-driven design philosophy
- **Version Control:** Git with semantic versioning
- **Architecture:** Phased development (Minimalist → Production)

### 1.2 Core Governance Laws

**Law 1: Research Primacy**
> All design decisions must be grounded in documented research. Intuition may guide exploration, but only research-validated findings may alter canonical geometry.

**Law 2: Parameter Sovereignty**
> Parameters are the single source of truth. All geometry derives from parameters. Parameters are semantic (naval architecture terminology), not arbitrary.

**Law 3: Non-Destructive Evolution**
> Versions never overwrite. Git tags mark milestones. Build outputs are ephemeral, source code is eternal.

**Law 4: Phase Respect**
> Phase 1 (Minimalist) and Phase 2 (Production) serve different purposes. Never backport production complexity to minimalist phase. Never prematurely optimize minimalist code.

**Law 5: Validation Before Acceptance**
> No design change is accepted until validated: Code must compile, geometry must render, STL must be manifold, physical print must succeed (where applicable).

**Law 6: Human-in-the-Loop Authority**
> AI assists, humans decide. Critical changes (parameter taxonomy, phase transitions, canonical geometry) require explicit human approval.

**Law 7: Zero-Assumption Doctrine**
> Assume nothing about the user's environment, knowledge, or intentions. Validate parameters, check dependencies, document assumptions explicitly.

**Law 8: Simplicity Mandate**
> The right amount of complexity is the minimum needed for the current task. Resist over-engineering. Three similar lines beat a premature abstraction.

---

## Article II: Canonical Truth Stack

### 2.1 Hierarchy of Authority

The canonical truth for GCSC2 geometry is defined by this hierarchy (highest to lowest authority):

**Level 1: Research Documentation**
- `docs/GCSC_REDESIGN_RESEARCH.md` - Design decisions and rationale
- `docs/GCSC_v2.6.1.md` - Original specification (historical reference)

**Level 2: Parameter Definitions**
- `01_Prototype_Simple/params/dimensions.scad` - Phase 1 canonical parameters
- `02_Production_BOSL2/params/*.scad` - Phase 2 canonical parameters (when developed)

**Level 3: Geometry Modules**
- `01_Prototype_Simple/modules/hull_simple.scad` - Hull geometry implementation
- `01_Prototype_Simple/modules/frame_simple.scad` - Frame geometry implementation
- `02_Production_BOSL2/modules/*.scad` - Phase 2 implementations (when developed)

**Level 4: Assembly Files**
- `01_Prototype_Simple/hull_v6_simple.scad` - Top-level hull assembly
- `01_Prototype_Simple/frame_v6_simple.scad` - Top-level frame assembly

**Level 5: Build Outputs** (ephemeral, not canonical)
- `STL_Exports/*.stl` - Exportable geometry (git-ignored)
- `renders/*.png` - Visualization (git-ignored)

### 2.2 Source of Truth Resolution

When sources conflict, resolution order:

1. **Research documentation** (if explicitly documented design decision)
2. **Parameter file** (if parameter semantically defines the dimension)
3. **Geometry module** (if implementation detail not exposed as parameter)
4. **Git history** (commit messages explain evolution)
5. **Physical test print** (reality trumps simulation)

---

## Article III: Development Protocols

### 3.1 Research-Driven Design Workflow

All significant design changes follow this mandated workflow:

```
Research Phase
    ↓
  Document findings in docs/
    ↓
  Propose design change (with rationale)
    ↓
  Human approval
    ↓
  Update parameters (dimensions.scad)
    ↓
  Update geometry modules (if needed)
    ↓
  Build & validate (make all)
    ↓
  Visual inspection (renders)
    ↓
  Commit with research reference
    ↓
  Tag milestone (if significant)
```

**Mandatory Documentation:**
- WHY the change (problem solved, opportunity seized)
- WHAT alternatives considered
- HOW the solution works
- VALIDATION performed

### 3.2 Parameter Evolution Protocol

Parameters may only change through:

**Addition:** New parameters added to dimensions.scad with:
- Semantic name (naval architecture term preferred)
- Units in comment (mm, degrees, etc.)
- Default value with rationale
- Category assignment (Primary, Form, Structural, Derived)

**Modification:** Existing parameter values changed with:
- Research justification documented
- Impact analysis (what geometry affected)
- Validation that build succeeds
- Git commit explaining change

**Deprecation:** Parameters made obsolete by:
- Comment marking as deprecated with date
- Redirect to new parameter (if applicable)
- Maintain for one version cycle before removal

**Deletion:** Parameters removed only:
- After one version cycle as deprecated
- With confirmation no modules reference it
- With git commit documenting removal rationale

### 3.3 Phase Governance

**Phase 1: Minimalist CSG Prototyping**
- **Purpose:** Rapid iteration, design validation, test printing
- **Tools:** OpenSCAD CSG primitives (cube, cylinder, hull, intersection)
- **Complexity Budget:** Keep modules under 150 lines
- **Optimization:** Favor clarity over cleverness
- **Build Time:** Acceptable up to 60 seconds
- **Exit Criteria:** Design validated through physical test print

**Phase 2: Production BOSL2 Implementation**
- **Purpose:** Production-quality geometry, aesthetic refinement
- **Tools:** BOSL2 library (Bézier curves, skin(), advanced operations)
- **Complexity Budget:** Acceptable if justified by quality improvement
- **Optimization:** Favor quality over build time
- **Build Time:** Acceptable up to 5 minutes
- **Entry Criteria:** Phase 1 design frozen and validated

**Phase Transition Protocol:**
- Phase 1 must reach "frozen" state (no design changes for 1 week)
- Physical test print must validate design
- Phase 2 begins by copying Phase 1 parameters
- Phase 1 remains available for quick iterations
- No backporting from Phase 2 to Phase 1

---

## Article IV: Quality Standards

### 4.1 Code Quality Gates

All code must pass before commit:

**Syntax Validation:**
- `openscad --check <file>` reports no errors
- No undefined variables or functions
- All includes resolve successfully

**Geometry Validation:**
- `openscad -o <output.stl> <file>` completes successfully
- STL file generated is non-zero size
- Visual inspection shows expected geometry

**Parameter Validation:**
- All parameters have units documented
- All parameters used by at least one module
- No parameters with magic numbers (use calculations)

**Documentation Validation:**
- Module purpose explained in header comment
- Complex algorithms commented
- Non-obvious design decisions documented

### 4.2 Build Quality Gates

**Manifold Validation:**
- STL must be manifold (watertight)
- No inverted normals
- No self-intersections

**Printability Validation:**
- Overhang angles ≤ 45° (or supported)
- Minimum wall thickness ≥ 2mm
- No features smaller than 0.4mm (2 nozzle widths)

**Dimensional Validation:**
- Bounding box matches expected LOA × beam × height
- Critical dimensions (slot diameters, ball positions) within tolerance

### 4.3 Freeze-on-Failure Protocol

If validation fails:

1. **STOP IMMEDIATELY** - Do not proceed with commit
2. **DIAGNOSE** - Identify failure mode (syntax, geometry, manifold, printability)
3. **FIX** - Correct the issue in source files
4. **REVALIDATE** - Run full validation again
5. **DOCUMENT** - Record failure and fix in commit message

**NO EXCEPTIONS:** Failed builds never committed to main branch.

---

## Article V: Universal Governor Integration

### 5.1 Universal Governor Role

The **Universal Governor skill** operates within GCSC2 with these responsibilities:

**Research Activation:**
- Conduct design research when requested
- Document findings in `docs/` directory
- Propose parameter or geometry changes based on research
- Maintain research → design traceability

**Audit & Compliance:**
- Validate project structure compliance
- Check parameter taxonomy adherence
- Verify quality gates before commits
- Identify governance violations

**Governance Evolution:**
- Propose governance improvements based on lessons learned
- Document governance edge cases
- Maintain governance-reality alignment

### 5.2 Human-Governor Authority Boundary

**Universal Governor has authority to:**
- Analyze and report on project state
- Propose design changes (with research backing)
- Validate compliance with this Constitution
- Generate documentation and research
- Identify governance gaps

**Universal Governor does NOT have authority to:**
- Make canonical parameter changes without human approval
- Commit to repository without human review
- Delete or deprecate governance documents
- Override Phase Governance protocols
- Skip validation gates

**Decision Flow:**
```
Research/Analysis (Governor)
    → Proposal (Governor)
    → Review (Human)
    → Approval/Modification (Human)
    → Implementation (Governor under supervision)
    → Validation (Governor + Human)
    → Commit (Human authorization)
```

### 5.3 Governance Alignment Maintenance

**Quarterly Review Protocol:**
- Every 3 months (or after each major phase milestone)
- Review this Constitution for real-world alignment
- Document governance friction points
- Propose amendments if needed
- Human approval required for constitutional changes

**Amendment Process:**
1. Identify governance-reality mismatch
2. Document the friction (what rule doesn't fit reality)
3. Research alternatives (how other projects handle it)
4. Draft amendment proposal
5. Human review and approval
6. Update Constitution with version increment
7. Update CHANGELOG.md with governance changes

---

## Article VI: Git Workflow Governance

### 6.1 Branch Strategy

**Main Branch (`main`):**
- Always buildable
- Only validated changes
- Tagged with semantic versions

**Feature Branches:**
- Format: `feature/<description>` (e.g., `feature/hull-sheer-refinement`)
- Created from `main`
- Merged back to `main` after validation
- Deleted after merge

**Phase Branches:**
- `phase1-development` - Active Phase 1 work
- `phase2-development` - Active Phase 2 work (when started)
- Long-lived, merged to `main` at milestones

### 6.2 Commit Message Format

```
GCSC2: <type>: <concise description>

<optional detailed explanation>

Research: <link to docs/ if applicable>
Validation: <what validation performed>

Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:**
- `feat:` - New feature or capability
- `fix:` - Bug fix or correction
- `refactor:` - Code restructure without behavior change
- `docs:` - Documentation only
- `research:` - Research findings added to docs/
- `param:` - Parameter change
- `build:` - Build system change

**Examples:**
```
GCSC2: param: Increase tumblehome_angle to 8° for stability

Research shows 6° tumblehome insufficient for stability with
current freeboard-to-beam ratio. Increased to 8° based on
historical soap canoe data.

Research: docs/GCSC_REDESIGN_RESEARCH.md#tumblehome-analysis
Validation: Built hull.stl, visual inspection confirms geometry
```

### 6.3 Versioning Protocol

**Semantic Versioning:** MAJOR.MINOR.PATCH

**MAJOR** - Incompatible parameter changes (e.g., 5.x → 6.x)
**MINOR** - New features, backward-compatible (e.g., 6.0 → 6.1)
**PATCH** - Bug fixes, refinements (e.g., 6.1.0 → 6.1.1)

**Git Tags:**
- `v6.0.0-alpha` - Pre-validation release
- `v6.0.0-beta` - Validated in OpenSCAD, pending physical test
- `v6.0.0` - Physical test validated, production-ready

**Phase Milestones:**
- `v6.0.0` - Phase 1 complete, design frozen
- `v6.1.0` - Phase 2 complete, BOSL2 implementation
- `v6.2.0` - Production optimization

---

## Article VII: Documentation Governance

### 7.1 Documentation Hierarchy

**Required Documentation:**
1. `README.md` - Project overview, quick start
2. `QUICKSTART.md` - Activation paths for different user types
3. `CHANGELOG.md` - Version history following Keep a Changelog format
4. `docs/GCSC_REDESIGN_RESEARCH.md` - Design research and decisions
5. `00_Governance/` - This directory

**Optional Documentation:**
6. `TROUBLESHOOTING.md` - Common issues and solutions (created when needed)
7. `docs/PHASE1_TO_PHASE2_MIGRATION.md` - Migration guide (when Phase 2 starts)
8. Phase-specific READMEs in `01_Prototype_Simple/` and `02_Production_BOSL2/`

### 7.2 Documentation Standards

**All documentation must:**
- Use GitHub-flavored Markdown
- Include table of contents for documents > 200 lines
- Use semantic headers (H1 for title, H2 for major sections)
- Include version number and date at top
- Link to related documents
- Avoid absolute paths (use relative links)

**Research documentation must:**
- State the research question
- List alternatives considered
- Document selection rationale
- Include external references (if any)
- Link to resulting parameter/code changes

---

## Article VIII: Constitutional Amendments

### 8.1 Amendment Authority

This Constitution may be amended by:

1. **Human decision** with documented rationale
2. **Universal Governor proposal** with human approval
3. **Research findings** that invalidate current governance

### 8.2 Amendment Process

1. Draft amendment in new file: `00_Governance/proposals/YYYY-MM-DD-<topic>.md`
2. Document rationale and impact analysis
3. Human review period (minimum 24 hours)
4. Approval or rejection with documented reasoning
5. If approved: Update Constitution, increment version, update CHANGELOG.md
6. Move proposal to `00_Governance/amendments/` for historical record

### 8.3 Constitutional Supremacy

In case of conflict:

**This Constitution** > Project documentation > Code comments > Git history

If code contradicts Constitution, **code is wrong** and must be corrected.

---

## Appendix A: Glossary

**Canonical Truth:** The authoritative source of geometry or parameters
**CSG:** Constructive Solid Geometry (cube, sphere, hull, difference, etc.)
**Freeboard:** Vertical distance from waterline to deck (sheer)
**LOA:** Length Overall - total length of vessel
**Manifold:** Geometry that is watertight, has consistent normals, no holes
**Phase 1:** Minimalist prototyping phase using CSG
**Phase 2:** Production phase using BOSL2 library
**Research-Driven:** Design decisions based on documented research, not intuition
**Tumblehome:** Inward slope of hull sides above waterline
**Universal Governor:** AI skill for governance, research, and compliance

---

## Appendix B: Version History

**v2.0.0** (2026-02-01)
- Initial GCSC2-specific constitution
- Replaces legacy GCSC v1-v5 governance
- Aligned with Universal Governor v1.1.0
- Adapted for OpenSCAD workflow
- Added research-driven design philosophy
- Removed Antigravity tool references

---

**CONSTITUTIONAL AUTHORITY DECLARATION**

This Constitution is the supreme governance document for GCSC2. All development, research, and decision-making must comply with its provisions. When reality conflicts with Constitution, reality must be documented and Constitution amended—never ignored.

**Adopted:** 2026-02-01
**Version:** 2.0.0
**Next Review:** After Phase 1 completion or 2026-05-01 (whichever first)

---

*"Research guides us, parameters define us, validation proves us."*
— GCSC2 Development Philosophy
