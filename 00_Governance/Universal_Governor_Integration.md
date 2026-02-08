# Universal Governor Integration for GCSC2

**Version:** 1.0.0
**Date:** 2026-02-01
**Framework:** Universal Governor v1.1.0
**Project:** GCSC2 (Great Canadian Soap Canoe v2)

---

## Purpose

This document defines how the **Universal Governor skill** integrates with GCSC2 development workflow, focusing on the research-driven design philosophy that distinguishes this project.

---

## Universal Governor Overview

The Universal Governor is a five-layer governance framework providing:

**Layer 1:** Identity & Validation
**Layer 2:** Skill Registry & Routing
**Layer 3:** Policy Engine & Quality Gates
**Layer 4:** Observability & Pattern Tracking
**Layer 5:** Human-in-the-Loop Escalation

For GCSC2, Universal Governor operates as a **research and compliance specialist**, not a development automation tool.

---

## Activation Paths for GCSC2

### Path 1: Project Audit & Compliance Check

**When to use:** Periodic governance validation, pre-milestone reviews

**Activation:**
```
Activate Universal Governor for GCSC2 project audit.

Focus Areas:
- Project structure compliance
- Parameter taxonomy validation
- Governance integration status
- Readiness assessment for current phase
```

**Expected Output:**
- Comprehensive audit report
- Compliance scorecard
- Issues identified with severity ratings
- Recommendations for remediation

**Example Use Cases:**
- Before starting Phase 1 development
- After major parameter changes
- Before Phase 1 → Phase 2 transition
- Quarterly governance reviews

---

### Path 2: Research-Driven Design Exploration

**When to use:** Investigating design questions, exploring alternatives

**Activation:**
```
Activate Universal Governor for GCSC2 design research.

Research Question: [Specific design question]

Context:
- Current design state: [e.g., "Phase 1, hull geometry"]
- Pain point: [e.g., "Tumblehome angle causing printability issues"]
- Constraints: [e.g., "Must maintain LOA and beam"]

Focus:
- Research best practices
- Analyze alternatives
- Document findings in docs/
- Propose parameter changes if warranted
```

**Expected Output:**
- Research document added to `docs/`
- Analysis of alternatives
- Recommendation with rationale
- Proposed parameter changes (if applicable)
- Links to external references

**Example Research Questions:**
- "What tumblehome angle provides optimal stability for soap canoes?"
- "How can we improve frame-to-hull attachment reliability?"
- "What are best practices for OpenSCAD modular architecture?"
- "Should we use Bézier curves or hull() operator for sheer line?"

---

### Path 3: Parameter Taxonomy Validation

**When to use:** Before adding/modifying parameters, during refactoring

**Activation:**
```
Activate Universal Governor for parameter taxonomy audit.

Focus:
- Validate parameter naming follows naval architecture terms
- Check parameter categorization (Primary/Form/Structural/Derived)
- Verify single source of truth principle
- Identify hardcoded values that should be parameters
- Check parameter documentation completeness
```

**Expected Output:**
- Parameter compliance report
- Naming inconsistencies identified
- Missing parameters flagged
- Hardcoded values discovered
- Recommendations for taxonomy improvements

**Example Use Cases:**
- After adding new geometry features
- Before freezing Phase 1 design
- During Phase 1 → Phase 2 migration planning
- When modules have unexplained magic numbers

---

### Path 4: Quality Gate Validation

**When to use:** Pre-commit validation, milestone preparation

**Activation:**
```
Activate Universal Governor for quality gate validation.

Scope: [Phase 1 or Phase 2]
Validation Level: [Syntax | Geometry | Manifold | Printability | Full]

Files to validate:
- [list specific files or "all current phase files"]
```

**Expected Output:**
- Syntax validation results (openscad --check)
- Geometry build results (STL generation)
- Manifold validation (if STL exists)
- Printability analysis (overhang, wall thickness)
- Pass/fail determination for each gate

**Example Use Cases:**
- Before committing parameter changes
- After refactoring geometry modules
- Before creating git tags/releases
- Pre-test-print validation

---

### Path 5: Documentation Synchronization

**When to use:** After design changes, during governance evolution

**Activation:**
```
Activate Universal Governor for documentation sync check.

Recent Changes:
- [describe what changed, e.g., "Increased tumblehome to 8°"]

Validate:
- README.md reflects current design
- Research docs cite this change
- CHANGELOG.md updated
- Governance documents still align
- Parameter comments accurate
```

**Expected Output:**
- Documentation compliance report
- Out-of-sync files identified
- Proposed documentation updates
- Governance alignment check

**Example Use Cases:**
- After implementing research recommendations
- After parameter taxonomy changes
- Before milestone releases
- When governance feels misaligned with reality

---

## Universal Governor Workflow for Research-Driven Design

### Workflow Overview

```
┌─────────────────────────────────────────────┐
│  1. RESEARCH QUESTION IDENTIFIED            │
│     (Human or UG identifies design issue)   │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  2. UG RESEARCH ACTIVATION                  │
│     - Explore design space                  │
│     - Analyze alternatives                  │
│     - Consult external references           │
│     - Document findings in docs/            │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  3. UG PROPOSAL GENERATION                  │
│     - Recommend design changes              │
│     - Propose parameter modifications       │
│     - Document rationale                    │
│     - Estimate impact                       │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  4. HUMAN REVIEW & DECISION                 │
│     - Review research findings              │
│     - Evaluate proposals                    │
│     - Approve/Modify/Reject                 │
│     - Provide additional constraints        │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  5. IMPLEMENTATION (if approved)            │
│     - Update dimensions.scad                │
│     - Modify geometry modules if needed     │
│     - Run quality gate validation           │
│     - Generate new builds                   │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  6. VALIDATION & DOCUMENTATION              │
│     - Visual inspection of renders          │
│     - Manifold validation                   │
│     - Update CHANGELOG.md                   │
│     - Commit with research citation         │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  7. PHYSICAL VALIDATION (if applicable)     │
│     - Export STL for test print             │
│     - Print and assemble                    │
│     - Document success/issues               │
│     - Feed findings back to research        │
└─────────────────────────────────────────────┘
```

### Workflow Roles

**Universal Governor Responsibilities:**
- Conduct research (explore design space, external references)
- Document findings in structured format
- Propose evidence-based changes
- Validate compliance with governance
- Check quality gates
- Generate documentation

**Human Responsibilities:**
- Define research questions
- Approve/reject design proposals
- Make final parameter decisions
- Execute git commits
- Perform physical validation
- Override governance when justified (with documentation)

**Boundary Clarity:**
- UG proposes, human decides
- UG validates, human approves
- UG documents, human commits
- UG analyzes, human acts

---

## GCSC2-Specific UG Capabilities

### Capability 1: Naval Architecture Research

**What UG can do:**
- Research standard naval architecture terminology
- Find historical precedents for design decisions
- Analyze hull form principles (tumblehome, deadrise, rocker)
- Recommend parameter ranges based on vessel type
- Identify scaling issues when adapting full-size principles to soap canoe scale

**Example:**
```
Research Question: "What deadrise angle is appropriate for a soap canoe?"

UG Response:
- Researches deadrise angles for small craft
- Finds 0° (flat) to 20° (deep-V) typical range
- Notes soap canoes are paddled, not powered (favor stability over speed)
- Recommends 10-15° as compromise
- Documents in docs/GCSC_REDESIGN_RESEARCH.md
- Proposes deadrise_angle = 12 in dimensions.scad
```

### Capability 2: OpenSCAD Best Practices Audit

**What UG can do:**
- Identify anti-patterns in OpenSCAD code
- Suggest modularization improvements
- Check for performance issues (excessive $fn, redundant operations)
- Validate CSG operation order (difference before union, etc.)
- Recommend BOSL2 alternatives for complex operations

**Example:**
```
Audit Request: "Check hull_simple.scad for OpenSCAD best practices"

UG Response:
- Identifies hardcoded $fn=64 (should be parameter)
- Notes hull() operation used correctly
- Suggests extracting point calculations to separate function
- Validates module naming conventions
- Recommends adding module-level documentation
```

### Capability 3: Parameter Dependency Analysis

**What UG can do:**
- Map parameter dependencies (which parameters derive from which)
- Identify circular dependencies (dangerous)
- Suggest parameter categorization (Primary vs. Derived)
- Check for unused parameters
- Validate parameter units consistency

**Example:**
```
Analysis Request: "Map parameter dependencies in dimensions.scad"

UG Response:
Primary (Independent):
- LOA, beam, freeboard, wall_thickness
- tumblehome_angle, deadrise_angle

Derived (Calculated):
- half_LOA ← LOA
- z_max_beam ← freeboard
- interior_beam_at_sheer ← beam, wall_thickness, tumblehome_angle, freeboard

Issues Found:
- None (clean dependency tree)

Recommendations:
- Consider adding LOA_to_beam_ratio as derived parameter for quick assessment
```

### Capability 4: Phase Readiness Assessment

**What UG can do:**
- Evaluate readiness for phase milestones
- Check exit criteria for Phase 1 (design frozen, test print validated)
- Check entry criteria for Phase 2 (BOSL2 installed, parameters migrated)
- Identify blocking issues
- Recommend preparation steps

**Example:**
```
Assessment Request: "Is Phase 1 ready to freeze?"

UG Response:
Exit Criteria Checklist:
✓ Parameters stable for 1+ week
✓ Geometry modules complete
✓ STL builds successfully
✓ Manifold validation passes
✗ Physical test print NOT completed
✗ Design iteration NOT ceased

Verdict: NOT READY

Blocking Issues:
1. Test print required for validation
2. Design still actively changing (last param change: 2 days ago)

Recommendations:
1. Execute test print this week
2. Freeze parameter changes for 1 week
3. Re-assess next week
```

### Capability 5: Governance Evolution Proposals

**What UG can do:**
- Identify governance-reality friction
- Propose constitutional amendments
- Document governance edge cases
- Suggest new quality gates
- Recommend process improvements

**Example:**
```
Friction Identified: "Makefile overwrites STL files, Constitution says 'never overwrite'"

UG Analysis:
- Constitution Article III.2 mandates non-destructive versioning
- Makefile practice: each build overwrites previous STL
- This is common practice for build artifacts (not source code)
- Source code follows non-destructive (git versions)
- Build outputs are ephemeral, not canonical

Proposal:
Amend Constitution Article II.1 to clarify:
"Build outputs (STL, PNG) are ephemeral and may be regenerated.
Non-destructive versioning applies to source code (.scad files) only."

Rationale:
- Aligns governance with standard build system practices
- Maintains spirit of law (protect canonical source)
- Removes friction from normal development workflow
```

---

## Integration with GCSC2 Development Phases

### Phase 1: Minimalist Prototyping

**UG Primary Role:** Research and rapid validation

**Key Activations:**
1. **Design Question Research** - Frequent, as design solidifies
2. **Parameter Validation** - Each time params change
3. **Quality Gate Checks** - Before each commit
4. **Printability Analysis** - Before test prints

**UG Not Used For:**
- Writing actual OpenSCAD code (human does this)
- Direct git commits (human authorizes)
- Arbitrary design changes without research backing

### Phase 2: Production BOSL2

**UG Primary Role:** Migration guidance and quality assurance

**Key Activations:**
1. **BOSL2 Best Practices Research** - How to use library effectively
2. **Phase 1 → Phase 2 Migration** - Parameter mapping, module conversion
3. **Performance Optimization** - Build time vs. quality trade-offs
4. **Advanced Geometry Validation** - Bézier curve correctness, etc.

**UG Not Used For:**
- Learning BOSL2 through trial-and-error (UG provides research first)
- Premature optimization before Phase 1 validated

---

## Quality Gates Enforced by UG

### Gate 1: Syntax Validation
```bash
openscad --check dimensions.scad
openscad --check hull_simple.scad
openscad --check frame_simple.scad
```
**UG checks:** No errors, all includes resolve

### Gate 2: Build Validation
```bash
make all
```
**UG checks:** STL files generated, non-zero size

### Gate 3: Manifold Validation
```bash
manifold STL_Exports/hull.stl
```
**UG checks:** Watertight, consistent normals, no self-intersections

### Gate 4: Parameter Sanity
**UG checks:**
- LOA > beam (length exceeds width)
- freeboard < LOA/2 (not absurdly tall)
- wall_thickness ≥ 2mm (printable)
- Angles in valid ranges (0-90°)

### Gate 5: Documentation Sync
**UG checks:**
- CHANGELOG.md updated
- Research docs cite parameter changes
- README.md reflects current design
- Comments in code match actual behavior

---

## Governance Compliance Monitoring

### Weekly Compliance Checks (Automated UG Activation)

If project development active, UG runs weekly audit:

**Checks:**
1. Recent commits follow message format
2. Parameter changes have research citations
3. Quality gates passed on latest builds
4. Documentation in sync with code
5. No governance violations

**Report Delivered To:** Human developer
**Action Required:** Review and address any issues

### Milestone Compliance Checks (Manual UG Activation)

Before major milestones (git tags, phase transitions):

**Human activates:**
```
Activate Universal Governor for milestone readiness check.

Milestone: [e.g., "v6.0.0-beta - Phase 1 first test print"]
```

**UG validates:**
- All quality gates passed
- Documentation complete
- Governance compliant
- Readiness criteria met

**Output:** GO / NO-GO recommendation with detailed report

---

## Advanced UG Workflows

### Workflow A: Research → Design → Implementation Pipeline

**Step 1: Research Activation**
```
UG: Research Question: "How to improve frame-hull attachment strength?"
   → Conducts research
   → Documents in docs/GCSC_REDESIGN_RESEARCH.md
   → Identifies 3 alternatives
```

**Step 2: Proposal Generation**
```
UG: Proposes: Increase slot_diameter from 7.5mm to 8.0mm
   → Rationale: Provides 0.25mm tolerance for PLA shrinkage
   → Impact: Affects hull_simple.scad pivot_slots() module
   → Validation: Must rebuild and test print
```

**Step 3: Human Decision**
```
Human: Reviews research, approves proposal
```

**Step 4: UG-Guided Implementation**
```
UG: Guides human through:
   1. Update dimensions.scad: slot_diameter = 8.0
   2. Rebuild: make all
   3. Visual inspection: renders/
   4. Update CHANGELOG.md
   5. Commit with research reference
```

**Step 5: Validation**
```
UG: Runs quality gates
   → Syntax: PASS
   → Build: PASS
   → Manifold: PASS
   → Documentation: PASS
```

### Workflow B: Governance Friction Resolution

**Friction Detected:**
```
Human: "Constitution says freeze on failure, but I want to commit a WIP branch"
```

**UG Analysis:**
```
UG: Analyzes Constitution Article IV.3 (Freeze-on-Failure)
   → Identifies intent: Don't commit broken code to MAIN
   → Notes: Doesn't prohibit WIP branches
   → Recommends: Clarify Constitution language
```

**Amendment Proposal:**
```
UG: Drafts proposal/2026-02-01-wip-branch-clarification.md
   → Proposes: Add "on main branch" qualifier to freeze protocol
   → Rationale: Allow experimental branches without governance violation
   → Human reviews and approves
```

**Constitution Updated:**
```
Article IV.3 amended:
"If validation fails on MAIN BRANCH, freeze. Feature branches may contain
 WIP code but must pass validation before merging to main."
```

---

## GCSC2-Specific UG Limitations

### What UG Cannot Do

**1. Cannot Override Human Design Intent**
- Even if research suggests alternative, human has final say
- UG documents disagreement but implements human decision

**2. Cannot Commit Without Human Authorization**
- UG can draft commit messages
- UG can stage files
- Human must execute `git commit` and `git push`

**3. Cannot Skip Validation Gates**
- Even under time pressure, gates are mandatory
- Human can acknowledge risk and proceed, but UG must warn

**4. Cannot Make Phase Transitions Autonomously**
- Phase 1 → Phase 2 requires explicit human decision
- UG can recommend, but cannot execute

**5. Cannot Delete Canonical Files**
- Parameters, geometry modules are sacred
- UG can propose deprecation, but human deletes

### What UG Should Not Be Used For

**1. Trial-and-Error Code Development**
- UG is research specialist, not code writer
- Use UG for "what should this parameter be?" not "write hull code"

**2. Arbitrary Design Exploration**
- UG needs specific research questions
- "Make it cooler" is not actionable; "Improve hydrodynamic efficiency" is

**3. Bypassing Learning**
- UG can explain BOSL2 concepts
- UG should not write all BOSL2 code (human learns by doing)

**4. Micro-Management**
- Don't activate UG for every single line change
- Use for significant decisions, research questions, compliance checks

---

## Activation Best Practices

### When to Activate UG

**✓ GOOD TIMES TO ACTIVATE:**
- Before starting a new development phase
- When encountering design decision points
- Before committing significant changes
- After completing milestones (retrospective)
- When governance feels misaligned with reality
- When stuck on a design problem

**✗ POOR TIMES TO ACTIVATE:**
- For every small code edit
- When you just want code written for you
- To avoid reading documentation
- During creative exploration (use UG after to validate)

### How to Write Effective Activation Prompts

**BAD PROMPT:**
```
"Check my project"
```
*Too vague, UG doesn't know what to check*

**GOOD PROMPT:**
```
Activate Universal Governor for GCSC2 project audit.

Focus Areas:
- Parameter taxonomy compliance
- Phase 1 readiness for test print
- Recent commit message format adherence
```
*Specific scope, clear objectives*

**BAD PROMPT:**
```
"Make the hull better"
```
*No research question, no criteria for "better"*

**GOOD PROMPT:**
```
Activate Universal Governor for GCSC2 design research.

Research Question: How can we reduce hull print time while maintaining structural integrity?

Current State: Hull prints in 4 hours with 20% infill
Constraints: Must maintain wall_thickness ≥ 3mm, LOA and beam fixed
```
*Clear question, context provided, constraints specified*

---

## Integration with Other GCSC2 Documentation

### Document Relationship Map

```
GCSC2_Constitution.md (SUPREME AUTHORITY)
    ↓
    ├─→ Universal_Governor_Integration.md (THIS DOCUMENT - HOW to use UG)
    ├─→ Research_Driven_Design_Philosophy.md (WHY research matters)
    ├─→ Parameter_Taxonomy_Governance.md (WHAT parameters must follow)
    └─→ Quality_Standards.md (WHEN to validate)

GCSC_REDESIGN_RESEARCH.md (RESEARCH FINDINGS)
    ↑
    └─ UG generates and updates this

GCSC2_DEVELOPMENT_SKILL_PROMPT.md (DEVELOPMENT GUIDE)
    ↔ Complementary to UG (dev prompt for code, UG for governance/research)
```

### When to Use Which Document

**Use Constitution when:**
- Resolving conflicts between documents
- Making governance decisions
- Amending project processes

**Use this document when:**
- Activating Universal Governor
- Understanding UG capabilities
- Writing activation prompts

**Use Research_Driven_Design_Philosophy.md when:**
- Understanding why research is mandatory
- Learning the research workflow
- Justifying design decisions

**Use GCSC2_DEVELOPMENT_SKILL_PROMPT.md when:**
- Writing OpenSCAD code
- Following phase-specific guidelines
- Understanding development workflow

---

## Version History

**v1.0.0** (2026-02-01)
- Initial Universal Governor integration document for GCSC2
- Defined 5 activation paths
- Documented research-driven workflow
- Established UG capabilities and limitations
- Aligned with GCSC2_Constitution.md v2.0.0

---

## Summary

The Universal Governor operates within GCSC2 as a **research specialist and governance auditor**, not an autonomous code generator. Its core value proposition:

1. **Research Excellence** - Investigates design questions with rigor
2. **Governance Compliance** - Ensures project follows its own rules
3. **Quality Assurance** - Validates gates before milestones
4. **Documentation Sync** - Keeps docs aligned with code
5. **Human Augmentation** - Enhances decision-making without replacing it

**Remember:** UG proposes, human decides. UG validates, human approves. UG documents, human commits.

---

**Document Version:** 1.0.0
**Last Updated:** 2026-02-01
**Maintained By:** Universal Governor Skill
**Review Cycle:** After Phase 1 completion or quarterly
