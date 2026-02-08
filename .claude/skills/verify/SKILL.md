---
name: verify
description: Run the CLAUDE.md dual-AI visual verification protocol. Use before claiming phase completion or after significant geometry changes.
argument-hint: "[phase-dir]"
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, Task
---

# Visual Verification Protocol (CLAUDE.md Article IV.6)

You are executing the mandatory visual verification protocol defined in CLAUDE.md.
This protocol exists because validate.sh once passed while frame slots were completely
missing — a critical geometry bug went undetected.

**CRITICAL UPDATE (2026-02-05):** The v6.1.0 "Beautiful Hull" PASSED this protocol but
FAILED human verification because it checked visibility, not functional assembly.
This protocol now includes mandatory functional checks.

**Trust nothing. Verify everything. Prove it works.**

## Arguments

- `$ARGUMENTS` = optional phase directory (default: `01_Prototype_Simple`)

## Protocol Steps

Execute these steps IN ORDER. Do NOT skip any step. Do NOT say "looks good" without
specific evidence.

### Step 1: Determine Scope

Identify which phase directory to verify:
- If `$ARGUMENTS` is provided, use that directory
- Otherwise default to `01_Prototype_Simple`
- Identify the main .scad files (hull, frame, assembly)

### Step 2: Render Required Verification Images

Render these MANDATORY images (all required for phase approval):

1. **Hull overview** — isometric view showing overall hull form
   - Render the hull .scad file with camera preset `iso`
   - Save to `renders/hull_features_labeled.png`

2. **Cross-section proof** — view showing internal geometry (wall thickness, slot seats)
   - Render with camera preset `cross_section`
   - Save to `renders/cross_section_proof.png`

3. **Assembly fit check** — hull + frames together
   - Render the assembly .scad file with camera preset `assembly`
   - Save to `renders/assembly_fit_check.png`

4. **Top-down view** — verify slot openings
   - Render hull with camera preset `top`
   - Save to `renders/hull_top_verification.png`

5. **Bottom view** — verify flat bottom surface (NEW - FR-1)
   - Render hull with camera preset looking at bottom
   - Use custom camera: `0,0,0,180,0,0,300` (bottom view)
   - Save to `renders/hull_bottom_verification.png`

6. **Side view** — verify curved gunwale/sheer line (NEW - FR-3)
   - Render hull with camera preset `side`
   - Save to `renders/hull_side_verification.png`

### Step 3: Claude Visual Analysis

For EACH rendered image, you MUST:

1. **Read the image file** using the Read tool
2. **Describe specific geometric features** you can see:
   - Hull: canoe silhouette, open top, gunwale edges, keel line
   - Slots: count visible slot openings (expect 4), hemisphere seats
   - Frame: inverse trapezoid shape, ball pivots, top/bottom rails
   - Assembly: frames seated in slots, clearance gaps, symmetry
3. **List features that SHOULD be visible but are NOT**
4. **State confidence**: low / medium / high
5. **If confidence < high**: flag for Gemini verification

### Step 3.5: Assembly Insertability Check (FR-2 - MANDATORY)

**This step exists because v6.1.0 PASSED visibility checks but FAILED assembly.**

Using the cross-section render (`renders/cross_section_proof.png`):

1. **Identify the slot path** from top opening to hemisphere seat
2. **Check for obstructions**:
   - Are there strips, ledges, or narrowing in the slot?
   - Is the slot width consistent from top to hemisphere?
   - Slot diameter should be 7.5mm; ball diameter is 7.25mm (0.25mm clearance)
3. **Trace the insertion path**:
   - A 7.25mm ball must fit down through the entire slot
   - Clear vertical path from slot top to hemisphere seat required
4. **Document findings**:
   - "Clear path: YES/NO"
   - "Obstructions found: [list or none]"
   - "Estimated clearance: [adequate/insufficient]"

**If any obstruction prevents ball insertion: FAIL the verification immediately.**

### Step 3.6: Flat Bottom Stability Check (FR-1 - MANDATORY)

**This step exists because v6.1.0 had a V-keel that prevented stable resting.**

Using the bottom view render (`renders/hull_bottom_verification.png`):

1. **Check for flat bottom surface**:
   - Is there a flat plane that can rest on a counter?
   - Or is there a V-keel, rocker, or curved bottom?
2. **Identify contact points**:
   - A stable soap dish needs a flat base OR multiple contact points
   - Single-line contact (V-keel) = UNSTABLE
3. **Document findings**:
   - "Flat bottom: YES/NO"
   - "Contact type: [flat plane / multiple points / V-keel / rocker]"
   - "Stability assessment: [stable / unstable]"

**If the hull cannot sit stably on a flat surface: FAIL the verification immediately.**

### Step 3.7: Canoe Form Character Check (FR-3 - MANDATORY)

**This step exists because v6.1.0 had flat freeboard, not curved canoe gunwale.**

Using the side view render (`renders/hull_side_verification.png`):

1. **Check the gunwale (top edge) profile**:
   - Does the top edge curve upward at bow and stern?
   - Or is it a straight horizontal line?
2. **Assess canoe recognition**:
   - Would a person recognize this as a miniature canoe?
   - The curved gunwale (sheer line) is THE defining canoe feature
3. **Document findings**:
   - "Gunwale curve: [curved up at ends / straight / irregular]"
   - "Canoe recognition: [clearly a canoe / questionable / not a canoe]"

**If the design is not recognizable as a canoe: FLAG for human review.**

### Step 4: Gemini Independent Verification

Run the Gemini verification script for each critical image:

```bash
source ../../.env  # or ../.env depending on cwd
python3 ../scripts/gemini_verify.py \
    --image "<path-to-render>" \
    --query "<query>"
```

**Required Gemini queries (FUNCTION-FOCUSED — visibility alone is insufficient):**

The v6.1.0 failure proved that checking "are slots visible?" is NOT enough.
We must verify "can balls be INSERTED?", "does it sit FLAT?", "is it recognizably a CANOE?"

1. **Hull overview** (slot visibility + context):
```
--query "Describe the 3D geometry in detail. Are frame pivot slots visible as openings in the hull surface? Count any slot openings. Is this an open-top canoe shape?"
```

2. **FR-1: Bottom stability** (MANDATORY functional check):
```
--query "Look at the bottom surface of this hull. Is there a flat plane that could rest stably on a bathroom countertop? Or is there a V-keel, curved bottom, or rocker that would make it tip over? Describe the bottom contact surface in detail. Would this sit flat without tipping?"
```

3. **FR-2: Ball insertion path** (MANDATORY functional check):
```
--query "Examine this slot cross-section carefully. Trace the path a 7.25mm diameter sphere would take if dropped from the slot opening at the top. Is there a clear vertical path all the way down to the hemisphere seat at the bottom, or are there obstructions (strips, ledges, narrowing, internal geometry) that would block insertion? Could you physically insert a ball bearing from above without it getting stuck?"
```

4. **FR-3: Canoe form recognition** (MANDATORY functional check):
```
--query "Look at the side profile of this hull. Does the top edge (gunwale) curve upward at the bow and stern like a traditional canoe sheer line? Or is it a straight horizontal line that looks more like a bathtub? Would someone looking at this immediately recognize it as a miniature canoe shape?"
```

5. **FR-4: Surface quality** (Phase 2 only — BOSL2 verification):
```
--query "Examine the hull surface quality. Are the curves smooth and continuous (indicating BOSL2 lofted surfaces), or do they appear faceted/segmented (indicating CSG hull() of spheres)? Is the surface fair - meaning smooth transitions without visible polygon edges?"
```

> **CRITICAL LESSON FROM v6.1.0:**
> Gemini (and Claude) correctly answered "slots visible? YES" while the design
> was actually non-functional. The slots were visible but OBSTRUCTED. Always
> ask about FUNCTION (insertable, stable, recognizable) not just FORM (visible, present).

### Step 5: Compare Observations

Compare your observations with Gemini's:

**Visibility checks:**
- Do you AGREE on the number of visible slots?
- Do you AGREE on the hull form (open top, canoe shape)?
- Do you AGREE on frame geometry (if assembly rendered)?

**Functional checks (NEW - MANDATORY):**
- Do you AGREE on ball insertability (clear path, no obstructions)?
- Do you AGREE on bottom flatness (stable resting)?
- Do you AGREE on gunwale curve (canoe character)?

Note any DISAGREEMENTS explicitly.

### Step 6: Generate Verification Log

Append a timestamped entry to `VERIFICATION_LOG.md` with this exact format:

```markdown
## Verification: [DATE] [TIME]

### Claude Observations
- Hull: [specific description]
- Slots: [count and description]
- Frame: [specific description]
- Assembly: [specific description]
- Missing features: [list or "none"]
- Confidence: [low/medium/high]

### Functional Checks (FR-1, FR-2, FR-3)
- **FR-1 Flat Bottom:** [YES/NO] — [description of contact surface]
- **FR-2 Ball Insertion:** [CLEAR/OBSTRUCTED] — [description of slot path]
- **FR-3 Curved Gunwale:** [YES/NO] — [description of sheer line]

### Gemini Observations
- Hull overview: [paste response]
- Cross-section (insertability): [paste response]
- Bottom view (stability): [paste response]
- Side view (canoe form): [paste response]

### Agreement
- Slot count: [agree/disagree]
- Hull form: [agree/disagree]
- Frame geometry: [agree/disagree]
- **Ball insertability: [agree/disagree]** (NEW)
- **Bottom flatness: [agree/disagree]** (NEW)
- **Gunwale curve: [agree/disagree]** (NEW)

### Soap Dish Test
- [ ] Sits flat on surface (FR-1)
- [ ] Frame can be inserted (FR-2)
- [ ] Holds soap (adequate volume)
- [ ] Water can drain (not pooling)
- [ ] Recognizable as canoe (FR-3)

### Verdict
- [PASS/FAIL] — [specific reason]
- If FAIL: [which FR requirements failed]

### Required Artifacts
- [ ] renders/hull_features_labeled.png
- [ ] renders/cross_section_proof.png
- [ ] renders/assembly_fit_check.png
- [ ] renders/hull_top_verification.png
- [ ] renders/hull_bottom_verification.png (NEW)
- [ ] renders/hull_side_verification.png (NEW)
- [ ] VERIFICATION_LOG.md updated
- [ ] Human confirmation pending
```

### Step 7: Final Assessment

State clearly:
- **PASS**: All features verified, all functional requirements met, Claude and Gemini agree, artifacts generated
- **FAIL**: Missing features, functional requirement failure, disagreement, or low confidence — specify what failed

**PASS requires ALL of the following:**
1. 4 visible slot openings
2. Clear ball insertion path (FR-2)
3. Flat bottom for stability (FR-1)
4. Curved gunwale for canoe character (FR-3)
5. Claude and Gemini agreement on functional checks

## FORBIDDEN Actions

- Saying "looks good" or "should work" without reading the actual image
- Auto-passing without specific observations
- Skipping Gemini verification when confidence < high
- Claiming verification complete without all required render artifacts
- Stating "manual verification recommended" as a substitute for doing the work
- **Passing verification without checking assembly insertability (FR-2)** (NEW)
- **Passing verification without checking flat bottom stability (FR-1)** (NEW)
- **Ignoring gunwale/sheer line character when assessing canoe form (FR-3)** (NEW)
- **Asking "are slots visible?" without asking "can balls be inserted?"** (NEW)

## Reference: Known Failure Modes

### Slot Rotation Bug (Critical)

The slot geometry bug (hull_simple.scad:68):
- **Broken**: `rotate([0, 90, 0])` = smooth hull surface, NO visible slots
- **Fixed**: `rotate([90, 0, 0])` = 4 visible slot openings in hull

If you see a smooth hull with NO slot openings, the geometry is BROKEN regardless
of what validate.sh reports.

### V6.1.0 "Beautiful Hull" Failure (Critical - NEW)

The v6.1.0 design passed all visibility checks but failed functional assembly:
- **Visible slots**: YES (passed visual check)
- **Insertable balls**: NO (slot obstructions blocked assembly)
- **Flat bottom**: NO (V-keel prevented stable resting)
- **Curved gunwale**: NO (flat freeboard cut)

**Lesson:** Visibility is not insertability. Always verify the insertion PATH, not just the opening.

## Functional Requirements Reference

| FR | Requirement | Verification Method |
|----|-------------|---------------------|
| FR-1 | Flat bottom for sink stability | Bottom view render, check for flat surface |
| FR-2 | Frame balls insertable from above | Cross-section render, trace insertion path |
| FR-3 | Curved gunwale (canoe sheer line) | Side view render, check top edge curve |

**Authority:** `CANONICAL_DESIGN_REQUIREMENTS.md`

**The gimbal mechanism IS the invention. The canoe shape IS the personality. But NEITHER matters if it can't sit on a sink or be assembled.**
