# GCSC2 Governance Quick Reference

**Version:** 2.0.0 | **Project:** GCSC2 | **Updated:** 2026-02-01

---

## 8 Core Governance Laws

**Law 1: Research Primacy**
> Design decisions grounded in documented research, not intuition

**Law 2: Parameter Sovereignty**
> Parameters are single source of truth. All geometry derives from parameters.

**Law 3: Non-Destructive Evolution**
> Git tags mark milestones. Build outputs ephemeral, source code eternal.

**Law 4: Phase Respect**
> Phase 1 (Minimalist) ≠ Phase 2 (Production). Never backport complexity.

**Law 5: Validation Before Acceptance**
> Code compiles → Geometry renders → STL manifold → Print succeeds

**Law 6: Human-in-the-Loop Authority**
> AI assists, humans decide. Critical changes require explicit approval.

**Law 7: Zero-Assumption Doctrine**
> Validate parameters, check dependencies, document assumptions explicitly.

**Law 8: Simplicity Mandate**
> Minimum complexity for current task. Resist over-engineering.

---

## Canonical Truth Stack (Highest → Lowest Authority)

```
Level 1: Research Documentation
├─ docs/GCSC_REDESIGN_RESEARCH.md (design rationale)
└─ docs/GCSC_v2.6.1.md (original spec - historical)

Level 2: Parameter Definitions
├─ 01_Prototype_Simple/params/dimensions.scad (Phase 1)
└─ 02_Production_BOSL2/params/*.scad (Phase 2, when developed)

Level 3: Geometry Modules
├─ 01_Prototype_Simple/modules/hull_simple.scad
└─ 01_Prototype_Simple/modules/frame_simple.scad

Level 4: Assembly Files
├─ hull_v6_simple.scad (top-level)
└─ frame_v6_simple.scad (top-level)

Level 5: Build Outputs (EPHEMERAL - not canonical)
├─ STL_Exports/*.stl (git-ignored)
└─ renders/*.png (git-ignored)
```

---

## Research-Driven Workflow

```
Question → Research → Document → Decide → Implement → Validate → Commit
```

**Research Quality:**
- **High Impact:** External refs, trade-off analysis, quantitative comparison
- **Medium Impact:** 2-3 alternatives, qualitative comparison
- **Low Impact:** Quick test, documented in commit message

**What Requires Research:**
- ✓ Parameter changes (especially Primary: LOA, beam, freeboard)
- ✓ Geometry algorithm changes
- ✓ Phase transitions
- ✗ Documentation updates (no research needed)
- ✗ Build script tweaks (no research needed)

---

## Quality Gates (Must Pass Before Commit)

**Gate 1: Syntax Validation**
```bash
openscad --check <file>  # No errors
```

**Gate 2: Build Validation**
```bash
make all  # STL generated, non-zero size
```

**Gate 3: Manifold Validation**
```bash
manifold STL_Exports/hull.stl  # Watertight, no inversions
```

**Gate 4: Parameter Sanity**
- LOA > beam (length > width)
- wall_thickness ≥ 2mm (printable)
- Angles in valid ranges (0-90°)

**Gate 5: Documentation Sync**
- CHANGELOG.md updated
- Research docs cite changes
- Code comments match behavior

---

## Universal Governor Activation Paths

**Path 1: Project Audit**
```
Activate Universal Governor for GCSC2 project audit.
Focus: [Structure | Parameters | Governance | Readiness]
```

**Path 2: Design Research**
```
Activate Universal Governor for GCSC2 design research.
Research Question: [Specific question]
Context: [Current state, pain points, constraints]
```

**Path 3: Parameter Taxonomy Validation**
```
Activate Universal Governor for parameter taxonomy audit.
Focus: Naming, categorization, hardcoded values, completeness
```

**Path 4: Quality Gate Validation**
```
Activate Universal Governor for quality gate validation.
Scope: [Phase 1 | Phase 2]
Validation Level: [Syntax | Geometry | Manifold | Full]
```

**Path 5: Documentation Sync**
```
Activate Universal Governor for documentation sync check.
Recent Changes: [description]
Validate: README, research docs, CHANGELOG, governance alignment
```

**UG Authority:** Proposes, analyzes, validates. Human decides, approves, commits.

---

## Git Workflow

**Branch Strategy:**
- `main` - Always buildable, only validated changes
- `feature/<description>` - Feature work, deleted after merge
- `phase1-development` - Long-lived Phase 1 work

**Commit Format:**
```
GCSC2: <type>: <description>

<detailed explanation if needed>

Research: <link to docs/ if applicable>
Validation: <what validation performed>

Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:** feat, fix, refactor, docs, research, param, build

**Versioning:** MAJOR.MINOR.PATCH (semantic versioning)
- v6.0.0-alpha - Pre-validation
- v6.0.0-beta - Validated in OpenSCAD
- v6.0.0 - Physical test validated

---

## Parameter Evolution

**Add Parameter:**
1. Semantic name (naval architecture term)
2. Units in comment (mm, degrees)
3. Default value with rationale
4. Category (Primary | Form | Structural | Derived)

**Modify Parameter:**
1. Research justification
2. Impact analysis
3. Build validates
4. Git commit explains

**Deprecate Parameter:**
1. Comment as deprecated with date
2. Redirect to new parameter
3. Maintain for one version cycle

**Delete Parameter:**
1. After one version cycle deprecated
2. Confirm no modules reference
3. Git commit documents removal

---

## Phase Governance

**Phase 1: Minimalist CSG**
- Purpose: Rapid iteration, design validation
- Tools: OpenSCAD CSG (cube, cylinder, hull)
- Complexity: Keep modules < 150 lines
- Exit: Design validated through test print

**Phase 2: Production BOSL2**
- Purpose: Production quality, aesthetic refinement
- Tools: BOSL2 library (Bézier, skin)
- Entry: Phase 1 frozen and validated
- No backporting from Phase 2 to Phase 1

---

## Freeze-on-Failure Protocol

**If validation fails:**
1. **STOP** - Do not commit
2. **DIAGNOSE** - Identify failure mode
3. **FIX** - Correct in source files
4. **REVALIDATE** - Run full validation again
5. **DOCUMENT** - Record in commit message

**NO EXCEPTIONS:** Failed builds never committed to main.

---

## Decision Authority Hierarchy

**When sources conflict:**
1. Research documentation (if explicit decision documented)
2. Parameter file (if parameter semantically defines it)
3. Geometry module (if implementation detail)
4. Git history (commit messages explain evolution)
5. Physical test print (reality trumps simulation)

**Constitutional Authority:**
```
Constitution > Project Docs > Code Comments > Git History
```

If code contradicts Constitution, **code is wrong**.

---

## Common Scenarios

**Q: I want to try a design idea**
→ Create feature branch, mark "WIP - Exploration", document findings before merge

**Q: Should I change this parameter?**
→ Research: Why change? What alternatives? Document, then change.

**Q: Build failed, can I commit to save progress?**
→ NO. Fix failure, validate, then commit.

**Q: Do I need research for fixing a typo?**
→ NO. Research scales with impact. Typos = low impact.

**Q: Can I skip quality gates if I'm in a hurry?**
→ NO. Gates are mandatory. Human can acknowledge risk but UG must warn.

**Q: Who has final authority?**
→ Human decides. UG proposes/validates. Constitution guides.

---

## Emergency Contacts

**Full Governance:**
- `00_Governance/GCSC2_Constitution.md` (supreme authority)

**Universal Governor:**
- `00_Governance/Universal_Governor_Integration.md` (how to activate)

**Research Philosophy:**
- `00_Governance/Research_Driven_Design_Philosophy.md` (why research matters)

**Development Guide:**
- `GCSC2_DEVELOPMENT_SKILL_PROMPT.md` (phase-specific how-to)

**Quick Start:**
- `QUICKSTART.md` (4 activation paths)

---

## Key Reminders

✓ **Research before deciding**
✓ **Document before implementing**
✓ **Validate before committing**
✓ **Parameters are single source of truth**
✓ **Human approves, UG assists**
✓ **Simple beats clever**
✓ **Evidence beats intuition**
✓ **Reality beats theory**

---

*"Research guides us, parameters define us, validation proves us."*
— GCSC2 Development Philosophy

**Version:** 2.0.0 | **Next Review:** After Phase 1 completion | **Maintained By:** Universal Governor
