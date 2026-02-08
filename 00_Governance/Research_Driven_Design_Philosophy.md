# Research-Driven Design Philosophy

**Version:** 1.0.0
**Date:** 2026-02-01
**Project:** GCSC2 (Great Canadian Soap Canoe v2)
**Authority:** Governance Annex to GCSC2_Constitution.md

---

## Purpose

This document defines the **research-driven design philosophy** that governs GCSC2 development. It explains **why** research is mandatory, **how** it integrates with the design process, and **what** distinguishes this approach from intuition-based development.

---

## Philosophy Foundation

### Core Principle

> **"Every design decision has a reason, and every reason has documentation."**

GCSC2 rejects "because it looks good" or "because I tried it and it worked" as sufficient justification for canonical design decisions. Instead:

- **Research precedes decisions** (not post-hoc rationalization)
- **Documentation captures rationale** (not just what, but why)
- **Evidence guides iteration** (measure, don't guess)
- **History informs future** (learn from past, document for future)

### The GCSC v5.x Problem

The legacy GCSC v1-v5 project suffered from **undocumented iteration**:

- Parameters changed frequently without recorded rationale
- Design decisions lost to memory ("why did we choose 7.5mm slots?")
- Pain points accumulated without systematic analysis
- Refactoring became archaeology ("what was the intent here?")

**Result:** Development became frustrating, knowledge became tribal, progress slowed.

### The GCSC2 Solution

GCSC2 mandates **research-driven design** to prevent these issues:

- All significant decisions documented before implementation
- Research findings captured in `docs/` for future reference
- Pain points analyzed systematically (see: `docs/GCSC_REDESIGN_RESEARCH.md`)
- Design evolution traceable through git history + research citations

**Result:** Development becomes cumulative, knowledge becomes durable, progress accelerates.

---

## What Qualifies as "Research"?

### Research Defined

For GCSC2 purposes, **research** is any systematic investigation that:

1. **Addresses a specific design question** (not open-ended exploration)
2. **Considers multiple alternatives** (not just validating a preferred option)
3. **Documents findings** (in `docs/` directory, not just mental notes)
4. **Cites sources when applicable** (external references, prior work, first principles)
5. **Produces actionable recommendations** (informs parameters or geometry)

### Research Spectrum

**HIGH-RIGOR RESEARCH** (required for major decisions):
- External references consulted (naval architecture principles, OpenSCAD best practices)
- Multiple alternatives evaluated with trade-off analysis
- Quantitative comparisons where possible (build time, print time, strength)
- Documented in formal research doc (`docs/*.md`)

**MEDIUM-RIGOR RESEARCH** (required for significant changes):
- Internal analysis (review current design, identify issues)
- 2-3 alternatives considered
- Qualitative comparison (pros/cons list)
- Documented in commit message or inline comments

**LOW-RIGOR RESEARCH** (acceptable for minor tweaks):
- Single alternative explored
- Quick test/iteration (change parameter, rebuild, inspect)
- Documented in commit message

**NOT RESEARCH** (insufficient for canonical changes):
- "I think this looks better" (subjective, no alternatives considered)
- "Let's try this" without documenting outcome
- Trial-and-error without systematic recording
- Copying from example without understanding

### Examples

**✓ GOOD RESEARCH (High Rigor):**
```
Research Question: What tumblehome angle optimizes stability vs. capacity?

Alternatives Considered:
1. 6° tumblehome (current v5.x design)
2. 8° tumblehome (increased stability)
3. 10° tumblehome (maximum stability)
4. 0° tumblehome (vertical sides, maximum capacity)

Analysis:
- 6°: Historical choice, but stability marginal at current freeboard
- 8°: Increases metacentric height ~15% (estimated), reduces capacity 8%
- 10°: Excellent stability, but capacity reduced 18% (unacceptable)
- 0°: Maximum capacity, but unstable (metacentric height too low)

External References:
- "Small Craft Naval Architecture" - tumblehome for paddled vessels 5-12°
- Soap canoe competition history - capsizes common with <7° tumblehome

Recommendation: 8° tumblehome as optimal compromise

Validation Plan: Build test print, stability test in water

Documented In: docs/GCSC_REDESIGN_RESEARCH.md#tumblehome-analysis
```

**✗ POOR RESEARCH (Insufficient):**
```
"Changed tumblehome to 8° because it looks cooler and might be more stable."

[No alternatives considered, no external references, no validation plan]
```

**✓ ACCEPTABLE RESEARCH (Medium Rigor):**
```
Commit Message:
GCSC2: param: Increase wall_thickness from 3mm to 3.2mm

Analysis:
- Current 3mm walls passed printability test
- However, hull flex during handling suggests marginal strength
- Alternatives: 3mm (current), 3.2mm (+7% material), 4mm (+33% material)
- 3.2mm chosen: Minimal weight increase, noticeable stiffness improvement
- 4mm rejected: Diminishing returns, print time increases 25%

Validation: Rebuilt hull.stl, checked wall uniformity in slicer
```

---

## The Research Workflow

### Step 1: Question Identification

**Trigger Events:**
- Design pain point encountered ("frame attachment unreliable")
- Performance issue observed ("build time too long")
- User feedback received ("hull too fragile")
- Alternative discovered ("BOSL2 has better primitives")
- Phase transition approaching ("ready for production quality?")

**Output:** Clear research question
- Bad: "Make hull better"
- Good: "How can we reduce hull build time by 30% without reducing strength?"

### Step 2: Research Execution

**Methods (choose appropriate for rigor level):**

**Literature Review:**
- OpenSCAD documentation and tutorials
- Naval architecture principles
- 3D printing best practices
- Prior GCSC versions (docs/GCSC_v2.6.1.md)

**Experimental Investigation:**
- Parameter sweeps (try multiple values, measure results)
- A/B testing (build two variants, compare)
- Prototype iteration (quick tests on subset of geometry)

**Expert Consultation:**
- OpenSCAD community forums
- Naval architecture resources
- 3D printing communities

**First Principles Analysis:**
- Geometric calculations (volume, surface area, stability)
- Structural analysis (stress points, failure modes)
- Manufacturing constraints (printability, assembly)

### Step 3: Documentation

**Minimal Documentation (commit message):**
```
GCSC2: param: <change description>

Research Question: <what were you investigating?>
Alternatives: <what options considered?>
Selection: <why this option?>
Validation: <how verified?>
```

**Standard Documentation (research section in docs/):**
```markdown
## [Topic] Research

**Date:** YYYY-MM-DD
**Question:** [Specific design question]

### Background
[Context: current state, pain point, opportunity]

### Alternatives Considered
1. **Option A:** [description]
   - Pros: [list]
   - Cons: [list]
   - Trade-offs: [analysis]

2. **Option B:** [description]
   [... repeat for each alternative ...]

### Analysis
[Comparison, trade-off evaluation, calculations if applicable]

### External References
- [Source 1]: [key finding]
- [Source 2]: [key finding]

### Recommendation
[Selected option with rationale]

### Implementation Plan
- Parameter changes: [list]
- Code changes: [list]
- Validation steps: [list]

### Follow-Up Questions
[Any unresolved issues for future research]
```

**Comprehensive Documentation (dedicated research doc):**
- See: `docs/GCSC_REDESIGN_RESEARCH.md` as exemplar
- Used for major design decisions (Phase selection, architecture)

### Step 4: Review & Approval

**Self-Review Checklist:**
- [ ] Research question clearly stated?
- [ ] Multiple alternatives considered (or justified why single option)?
- [ ] Selection rationale documented?
- [ ] External references cited (if applicable)?
- [ ] Validation plan defined?

**Human Review:**
- Human developer reviews research findings
- May request additional alternatives
- May challenge assumptions
- Approves or requests revision

**Universal Governor Review (if activated):**
- UG validates research rigor
- UG may suggest additional references
- UG checks alignment with governance
- UG cannot override human decision

### Step 5: Implementation

**Parameter Changes:**
```openscad
// Update dimensions.scad
// RESEARCH: docs/GCSC_REDESIGN_RESEARCH.md#tumblehome-analysis
tumblehome_angle = 8;  // Was 6, increased for stability (2026-02-01)
```

**Geometry Changes:**
- Update modules if needed
- Maintain comments linking to research

**Build & Validate:**
- `make all` to rebuild
- Visual inspection of renders
- Manifold validation
- Test print if critical

### Step 6: Knowledge Capture

**Update Documentation:**
- `CHANGELOG.md` - What changed
- Research docs - Why changed
- Code comments - Link to research

**Git Commit:**
```
GCSC2: param: Increase tumblehome_angle to 8°

Stability analysis showed 6° tumblehome insufficient for current
freeboard-to-beam ratio. Increased to 8° based on naval architecture
best practices for paddled small craft.

Research: docs/GCSC_REDESIGN_RESEARCH.md#tumblehome-analysis
Validation: Built hull.stl, visual inspection confirms geometry

Generated with Claude Code
Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Lessons Learned:**
- Document what worked / didn't work
- Note any unexpected outcomes
- Flag follow-up research questions

---

## Research Governance Rules

### Rule 1: No Canonical Changes Without Research

**Canonical changes** (require research):
- Parameter value modifications
- Parameter additions/deletions
- Geometry algorithm changes
- Module API changes
- Phase transitions

**Non-canonical changes** (research optional):
- Build script tweaks
- Documentation updates
- Code comments
- Directory reorganization

### Rule 2: Research Rigor Scales with Impact

**High Impact** → High-rigor research required:
- Changes to Primary Parameters (LOA, beam, freeboard)
- Major geometry refactoring
- Phase transitions
- Architecture decisions

**Medium Impact** → Medium-rigor research required:
- Changes to Form Parameters (tumblehome, deadrise)
- Module refactoring
- Build system changes

**Low Impact** → Low-rigor research acceptable:
- Tweaking Derived Parameters
- Code style improvements
- Comment additions

### Rule 3: Research Must Precede Implementation

**Correct Sequence:**
```
Research → Document → Approve → Implement → Validate → Commit
```

**Forbidden Sequence:**
```
Implement → Discover it works → Rationalize decision → Commit
```

**Exception:** Exploratory prototyping is allowed in feature branches with explicit "WIP - Exploration" commit messages, but before merging to main, research must be documented.

### Rule 4: Research Findings Are Versioned

**Research documents versioned with project:**
- Research in `docs/` committed to git
- Research findings tied to specific project versions
- Old research preserved (never deleted) for historical context
- New research may supersede old (with explicit citation)

**Example:**
```
docs/GCSC_REDESIGN_RESEARCH.md (v6.0 research)
docs/GCSC_v5_RETROSPECTIVE.md (v5 analysis - historical)
docs/GCSC_v2.6.1.md (v2 spec - canonical reference)
```

### Rule 5: Research Validates Itself

**Research must include validation plan:**
- How will we know if this works?
- What measurements confirm success?
- What tests required before acceptance?

**Example Validation Plans:**
```
Parameter Change: tumblehome_angle = 8
Validation:
- Build hull.stl successfully
- Visual inspection confirms 8° angle
- Test print validates printability
- Water test confirms improved stability

Code Refactor: Extract hull point calculation to function
Validation:
- Build produces identical STL (binary diff)
- Visual inspection shows no geometry change
- Performance: build time unchanged or improved
```

---

## Integration with Development Workflow

### Daily Development Loop

```
┌─────────────────────────────────────────┐
│  1. Encounter Design Question           │
│     "Should we increase slot diameter?" │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  2. Quick Research (30 min - 2 hours)   │
│     - Review current design             │
│     - Consider 2-3 alternatives         │
│     - Document findings                 │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  3. Decision & Documentation            │
│     - Select option with rationale      │
│     - Update parameters or code         │
│     - Commit with research citation     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  4. Validation                          │
│     - Build & visual inspection         │
│     - Physical test if critical         │
└─────────────────────────────────────────┘
```

**Time Budget:**
- Simple questions: 30 minutes research
- Medium questions: 1-2 hours research
- Complex questions: Half-day to full-day research

### Weekly Research Sessions

**Recommended:** Dedicate Friday afternoons to research

**Activities:**
- Review accumulated design questions
- Deep-dive research on major decisions
- Update research documentation
- Plan next week's design priorities

**Output:**
- Updated `docs/GCSC_REDESIGN_RESEARCH.md`
- Research backlog prioritized
- Clear design direction for next week

### Milestone Research Reviews

**Before major milestones:**
- Review all research since last milestone
- Validate design decisions still sound
- Identify any research gaps
- Document lessons learned

**Milestones:**
- Phase 1 design freeze
- First test print
- Phase 1 → Phase 2 transition
- Production release

---

## Research Quality Standards

### Acceptable Research Quality

**Minimum Standards:**
1. **Question Clarity:** Can be stated in one sentence
2. **Alternative Exploration:** At least 2 options considered (or justified why only 1)
3. **Rationale:** Explanation of why selected option best
4. **Documentation:** Findable in git history or docs/

**Quality Indicators:**
- Future you could understand decision 6 months later
- Another developer could validate reasoning
- Decision could be challenged with evidence

### Unacceptable Research

**Red Flags:**
- "Trust me, it's better"
- "I tried it and it worked"
- No documentation of alternatives
- No link between research and decision
- Post-hoc rationalization ("I made change, now justify it")

---

## Research Examples from GCSC2

### Example 1: Option D Hybrid Approach Selection

**Research Doc:** `docs/GCSC_REDESIGN_RESEARCH.md` (Section II)

**Question:** Which redesign approach for GCSC2?

**Alternatives:**
- Option A: Pure CSG forever
- Option B: BOSL2 from day 1
- Option C: Full rebuild in Python/CadQuery
- Option D: Hybrid (CSG prototype → BOSL2 production)

**Analysis:**
- Evaluated pain points of v5.x
- Assessed learning curve for each option
- Considered maintainability
- Analyzed build time trade-offs

**Result:** Option D selected (now implemented as Phase 1 + Phase 2)

**Quality:** HIGH - Comprehensive, documented, alternative options evaluated

---

### Example 2: Parameter Naming Convention

**Research:** Embedded in constitution development

**Question:** How should parameters be named?

**Alternatives:**
- Arbitrary names (x1, y1, width, height)
- Coordinate-based (x_max, y_offset, z_pivot)
- Semantic naval terms (LOA, beam, freeboard, tumblehome)

**Analysis:**
- Arbitrary: Easy to write, impossible to understand later
- Coordinate-based: Clear intent, but doesn't convey design meaning
- Semantic naval: Requires learning terminology, but self-documenting

**Result:** Semantic naval architecture terms mandated

**Quality:** MEDIUM - Clear rationale, but limited external research

---

### Example 3: Slot Diameter Parameter

**Research:** (Hypothetical, demonstrates inline research)

**Commit Message:**
```
GCSC2: param: Increase slot_diameter from 7.5mm to 8.0mm

Research Question: Original 7.5mm slots too tight for reliable frame insertion

Alternatives:
1. Keep 7.5mm, improve printing tolerances (difficult, not reliable)
2. Increase to 8.0mm (+0.5mm clearance)
3. Increase to 8.5mm (+1.0mm clearance)

Analysis:
- 7.5mm: Requires perfect print, frame assembly difficult
- 8.0mm: Provides 0.25mm radial clearance, comfortable fit
- 8.5mm: Too loose, frame rattles in slots

External Reference: 3D printing tolerance guidance (0.2-0.4mm clearance typical)

Selection: 8.0mm provides reliable fit with manufacturing tolerance

Validation: Test print confirms comfortable insertion, no rattle
```

**Quality:** MEDIUM-HIGH - Clear question, alternatives, validation

---

## Benefits of Research-Driven Approach

### Immediate Benefits

**1. Better Decisions**
- Evidence-based choices beat intuition
- Trade-offs explicitly evaluated
- Fewer regrets ("wish we'd considered X")

**2. Faster Iteration**
- Don't waste time on obviously poor options
- Research shortcuts trial-and-error
- Validation plan prevents surprise failures

**3. Reduced Rework**
- Decisions less likely to be reversed
- Changes based on evidence, not whim
- Design converges faster

### Long-Term Benefits

**4. Knowledge Persistence**
- Future you understands past decisions
- New contributors can learn design rationale
- Knowledge doesn't die with memory

**5. Design Confidence**
- Validation provides evidence design works
- Research backs up claims
- Less second-guessing

**6. Continuous Improvement**
- Research captures lessons learned
- Each version smarter than last
- Patterns identified and reused

### Community Benefits

**7. Transparency**
- Decisions explainable to others
- Open source contributors can validate reasoning
- Educational value (teach naval architecture + OpenSCAD)

**8. Credibility**
- Research-backed design more trustworthy
- Can defend decisions with evidence
- Professional-grade development process

---

## Common Objections and Responses

### Objection 1: "Research slows me down"

**Response:**
- Upfront research saves backend rework
- 1 hour research prevents 5 hours wasted iteration
- Fast decisions often become slow regrets

**Compromise:**
- Research rigor scales with impact (Rule 2)
- Low-impact changes need minimal research
- Use research templates to speed documentation

---

### Objection 2: "Sometimes I just want to try something"

**Response:**
- Exploratory prototyping is fine in feature branches
- Mark commits as "WIP - Exploration"
- Before merging to main, document what you learned
- Experimentation ≠ canonical acceptance

**Guidance:**
```
# Feature branch - exploration allowed
git checkout -b feature/hull-experiment
# Try wild ideas here, commit frequently
# When you find something that works:
# THEN do research, document, prepare for main merge
```

---

### Objection 3: "My research isn't rigorous enough"

**Response:**
- Research quality scales with decision importance
- Even simple "I tried A and B, B was better because X" is research
- Document what you did, even if informal
- Perfect is enemy of good (some research > no research)

**Minimum Bar:**
- Can you explain your decision to someone else?
- Did you consider at least one alternative?
- Is it written down somewhere?

If yes to all three → sufficient research for most changes

---

### Objection 4: "I don't know enough about naval architecture"

**Response:**
- Research is how you learn
- External references encouraged (cite sources)
- Universal Governor can help with research questions
- First principles reasoning acceptable (calculate, don't guess)

**Guidance:**
- Start with what you know (geometry, printability, manufacturing)
- Expand to what you can learn (naval terms, design principles)
- Document your learning (future reference)

---

## Research Tools and Resources

### Internal Resources

**GCSC Historical Knowledge:**
- `docs/GCSC_v2.6.1.md` - Original specification
- `docs/GCSC_REDESIGN_RESEARCH.md` - Redesign analysis
- Git history - Evolution of decisions

**GCSC2 Framework:**
- `dimensions.scad` - Current parameter values
- Module comments - Design rationale
- CHANGELOG.md - What changed and when

### External Resources

**OpenSCAD:**
- [OpenSCAD User Manual](https://openscad.org/documentation.html)
- OpenSCAD forums and community
- BOSL2 library documentation (Phase 2)

**Naval Architecture:**
- Small craft design principles
- Stability and buoyancy basics
- Terminology references

**3D Printing:**
- Printability guidelines
- Tolerance standards
- Material properties (PLA, PETG)

### Research Assistance

**Universal Governor:**
- Activate for design research questions
- UG can search, analyze, document findings
- See: `Universal_Governor_Integration.md`

**Human Consultation:**
- OpenSCAD community
- Naval architecture forums
- 3D printing communities

---

## Summary

### The Philosophy in One Page

**GCSC2 Design Philosophy:**
1. **Research precedes decisions** - Don't guess when you can know
2. **Documentation captures knowledge** - Write it down
3. **Evidence guides iteration** - Measure and compare
4. **Quality scales with impact** - Important decisions need rigor
5. **Validation proves assumptions** - Test your theories

**The Research Loop:**
```
Question → Research → Document → Decide → Implement → Validate → Commit
```

**Research Quality:**
- Minimum: Consider alternatives, document choice
- Standard: External references, trade-off analysis
- Comprehensive: Quantitative comparison, validation plan

**Why It Matters:**
- Better decisions (evidence > intuition)
- Faster iteration (research > trial-and-error)
- Durable knowledge (documentation > memory)
- Design confidence (validation > hope)

---

**Remember:** Every parameter has a purpose. Every decision has a reason. Every reason has documentation.

---

**Document Version:** 1.0.0
**Last Updated:** 2026-02-01
**Next Review:** After Phase 1 completion
**Maintained By:** GCSC2 Development Team + Universal Governor
