# CODEX DIRECTIVE — Integrate GCSC v5.3 as Canonical Geometry Reference

Context:
The following files represent the fully verified mechanical reference assembly:

/mnt/data/GCSC_Hull_v5.3.scad
/mnt/data/CF_Frame_v5.3_infill.scad
/mnt/data/GCSC_Slot_Plugs_v3.0_tight.scad
/mnt/data/GCSC_Danforth_Anchor_v1.2.scad
/mnt/data/Final_GCSC_Assembly.md

These components have verified compatibility:

- Pivot Y: 33.0 mm
- Pivot Z: 38.0 mm
- Slot diameter: 7.5 mm
- Ball diameter: 7.25 mm
- Clearance: 0.12 mm
- Symmetric spacing: 16 mm
- Proven functional swing mechanics

These dimensions are now canonical and must not be altered.

---

## Objective

Upgrade codex_hull_lab so that all generated hulls preserve compatibility with v5.3 frame, slot, and pivot geometry.

The hull lab must become a parameterized derivative of v5.3, not a replacement.

---

## Step 1 — Import canonical geometry reference

Create:

codex_hull_lab/reference/
  hull_v5_3_reference.scad
  frame_v5_3_reference.scad
  slot_plug_reference.scad
  anchor_reference.scad

Wrap each imported file in a namespace module, for example:

module gcsc_reference_hull()
{
    include <../../reference/GCSC_Hull_v5.3.scad>
}

Do not modify original reference files.

---

## Step 2 — Extract critical reference parameters

Define in:

codex_hull_lab/src/gcsc_reference_params.scad

REFERENCE_PIVOT_Y = 33.0;
REFERENCE_PIVOT_Z = 38.0;

REFERENCE_SLOT_DIAMETER = 7.5;
REFERENCE_BALL_DIAMETER = 7.25;

REFERENCE_FRAME_SPACING = 16.0;

REFERENCE_FOOT_PAD_DIAMETER = 8.0;
REFERENCE_FOOT_PAD_DEPTH = 1.5;

All future hulls must preserve these coordinates.

---

## Step 3 — Constrain hull generator

Modify:

gcsc_hull_core.scad
gcsc_hull_profiles.scad
gcsc_hull_features.scad

So that:

- Frame pivot sockets are placed exactly at REFERENCE_PIVOT_Y, REFERENCE_PIVOT_Z
- Slot geometry matches reference slot diameter and placement
- Frame spacing remains symmetric at 16mm

Hull curvature and shell thickness may vary, but interface geometry must remain invariant.

---

## Step 4 — Add frame rib system compatible with CF_Frame_v5.3_infill

Create:

module gcsc_internal_frame_support()

This module must:

- Support CF_Frame_v5.3_infill geometry
- Not interfere with pivot rotation envelope
- Not obstruct slot plug system

---

## Step 5 — Add slot plug compatibility

Ensure slot geometry matches:

GCSC_Slot_Plugs_v3.0_tight.scad

Slots must accept plug with 0.12mm clearance tolerance.

---

## Step 6 — Add assembly verification mode

Create:

codex_hull_lab/tests/reference_assembly_check.scad

This file must:

- Render generated hull + reference frame + slot plugs
- Confirm alignment visually
- Provide developer confirmation that geometry remains compatible

---

## Step 7 — Preserve codex_hull_lab modular architecture

Do not collapse modular structure.

Maintain:

src/
presets/
features/
reference/
tests/

---

## Success criteria

Generated hulls:

- Accept CF_Frame_v5.3_infill without modification
- Accept GCSC_Slot_Plugs_v3.0_tight
- Preserve pivot alignment
- Preserve slot geometry

Hull remains watertight and printable.

---

## Final output

Print:

- Files modified
- Reference parameters imported
- Compatibility constraints enforced
- Confirmation of reference-constrained hull generation

Stop.
