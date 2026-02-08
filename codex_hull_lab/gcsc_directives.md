# CODEX DIRECTIVE — Align Hull Lab to True GCSC Mechanics (v5.3 behavior)

We have a working hull + locked interface geometry, but the mechanics must match the real GCSC:

MECHANICS (MUST MATCH):
1) NO frame supports / ribs. Remove any internal frame support structures. (GCSC does not use them.)
2) Seats are Z step-ups in the floor that act as swing stops at:
   - x = +32
   - x = -32
   These are solid "seat pedestals" / "floor step-ups", not posts.
3) Frame pivot columns remain at:
   - x = +16
   - x = -16
   (Do not change locked interface geometry: slot dia 7.5, pivot coords, etc.)
4) Decorative anchor / swing stop at:
   - x = 0
   This is decorative + physical stop. Implement as a solid feature that unions into hull.
5) Slots (7.5mm) must be INTERNAL to the wall:
   - NO open holes to the outside.
   - Slots must be fully enclosed within wall thickness, with only internal access if any.
6) Bow and stern MUST be CLOSED:
   - No open ends.
   - Create end caps with a minimum thickness equal to wall_mm.
   - Ensure watertight solid.

TARGET FIXES:
- Codex hull currently has some holes (likely slot cutouts piercing outside) and open bow/stern.
- Update geometry so STL is watertight and visually matches the real product (like the user's red print).

FILES TO EDIT:
- codex_hull_lab/src/gcsc_hull_features.scad
- codex_hull_lab/src/gcsc_hull_shell.scad
- codex_hull_lab/src/gcsc_hull_core.scad
- codex_hull_lab/presets/*.scad (add toggles/parameters)
- codex_hull_lab/tests/reference_assembly_check.scad (ensure still passes)

IMPLEMENTATION REQUIREMENTS:

A) Remove frame supports
- Disable or delete gcsc_internal_frame_support() usage and any rib/frame-support generation.
- Hull should be clean interior except for:
  - floor seats (x=±32)
  - pivot/interface columns (x=±16)
  - optional decorative anchor at x=0

B) Add floor seat step-ups at x=±32
- Create module: gcsc_seat_stops_feature()
- Two mirrored seat blocks:
  - centered at x = ±32
  - placed on hull interior floor (z near floor)
  - "Z step-up": a raised plateau with smooth edges (simple chamfer ok)
  - unions to hull interior (must not create separate solids)
- Add parameters in presets:
  seat_on=true
  seat_width_mm, seat_length_mm, seat_height_mm
  seat_edge_margin_mm (keep off inner walls)

C) Decorative anchor stop at x=0
- Create module: gcsc_anchor_stop_feature()
- Simple anchor-like boss or stop block at x=0, centered, that unions to hull floor.
- Keep it printable, no fragile overhangs.
- Add toggle: anchor_on=true

D) Seal slots (no exterior holes)
- Audit slot cutouts: ensure they do NOT pierce outer wall.
- If current slot logic uses difference() that reaches outside, modify:
  - slot cavities must be fully inside wall volume.
  - add a "skin_thickness_mm" outside the slot (>= 1.2mm recommended).
- Add preset parameter:
  slot_skin_mm = max(1.2, wall_mm/2)
- If needed, move slots slightly inward or increase wall thickness locally in slot region.

E) Close bow and stern
- In shell/outer hull generation, ensure loft produces closed ends.
- Add explicit end caps if loft is open:
  - Create bow_cap() and stern_cap()
  - Cap thickness >= wall_mm
  - Must union to outer hull before hollowing subtraction.
- After hollowing, ensure inner cavity does not cut through end caps (leave cap thickness).

F) Validation
- Render:
  codex_hull_lab/tests/reference_assembly_check.scad
- Export STL and ensure:
  - watertight true (if you have trimesh checks available)
  - no visible holes on exterior
  - bow/stern closed
  - slots are internal (not visible from outside)

OUTPUT:
- List exact changes made
- Which toggles/params control seats + anchor + slots
- Confirm reference assembly still aligns
Stop.


---- part 2

# CODEX DIRECTIVE — Add Sink-Stable Flat Footprint + Rubber Foot Recesses (8mm x 3mm)

We must upgrade the hull underside so the soap canoe sits stable on a sink and does NOT rock/tip.

Constraints:
- Keep overall “stand” height low (soap dish). No tall legs.
- Provide a flat footprint region so it sits solidly even on slightly curved sink surfaces.
- Add 4 recessed pockets for stick-on rubber feet:
  - diameter: 8.0 mm
  - depth: 3.0 mm
- Preserve locked v5.3 interface geometry:
  - pivot/slots/frame spacing etc must not move.

Implementation goals:
1) Replace any tall stand geometry with a low-profile “keel skid pad”:
   - a flat bottom band that provides stability.
   - must union to hull, not separate solids.
2) Add 4 foot recess pockets on the underside:
   - circular recesses, 8mm dia, 3mm deep
   - positioned near corners of the footprint for anti-rock stability
   - ensure enough material remains under recess (do NOT punch through the hull).
3) Ensure bottom is locally planar:
   - allow a controlled “flat_cut_z” or “keel_flat_plane_z” that trims/joins the underside.

Files to modify:
- codex_hull_lab/src/gcsc_hull_features.scad
- codex_hull_lab/src/gcsc_hull_shell.scad (if needed for bottom flattening)
- codex_hull_lab/src/gcsc_hull_core.scad
- codex_hull_lab/presets/gcsc_default.scad and gcsc_experiment.scad
- codex_hull_lab/tests/reference_assembly_check.scad (ensure still passes)

Add/ensure these preset params (safe defaults):
- base_flat_on = true
- base_flat_height_mm = 1.6            # how much “skid thickness” protrudes downward (LOW)
- base_flat_width_mm = 18              # width of flat band across keel area
- base_flat_length_fraction = 0.70     # fraction of hull length covered by flat pad
- base_flat_z_offset_mm = 0            # tweak down/up slightly if needed

- feet_on = true
- foot_diameter_mm = 8.0
- foot_recess_depth_mm = 3.0
- foot_edge_margin_mm = 10             # keep away from extreme bow/stern thin areas
- foot_span_fraction = 0.55            # spacing across length where feet land
- foot_lateral_offset_mm = 14          # half-spacing left/right from centerline (tune safely)
- foot_recess_skin_mm = 1.2            # minimum remaining wall thickness under recess

Required geometry changes:

A) Low-profile flat keel footprint (skid pad)
Create module: gcsc_base_flat_feature()
- Build a shallow rectangular/rounded pad underneath the hull centered on x=0.
- Must be flat on the bottom (planar).
- Should extend along the hull length for base_flat_length_fraction of length.
- Should be wide enough to resist rocking: base_flat_width_mm.
- Keep it low: base_flat_height_mm (1.2–2.0mm typical).
- Union the pad into the hull BEFORE hollowing if needed, or union afterward if it doesn’t break watertightness.

B) Foot recess pockets
Create module: gcsc_foot_recess_cutouts()
- 4 cylinders used as subtractive cuts from the underside of the skid pad / hull bottom.
- Each recess: diameter foot_diameter_mm, depth foot_recess_depth_mm.
- Position as a rectangle footprint:
  - Two near bow, two near stern (but not too close to ends)
  - Left/right symmetric around centerline
- Must NOT cut through the hull:
  - enforce minimum remaining thickness foot_recess_skin_mm.
  - If necessary, locally thicken the base pad under feet.

C) Wire into build:
- Positive union includes hull shell + base_flat_feature.
- Then subtract foot recess cutouts if feet_on=true.
- Ensure no exterior holes, watertight STL.

D) Stability check:
Add to docs/ITERATION_LOG.md:
- v0.4 “Sink stability base + foot recess pockets”
Include:
- footprint dimensions
- recess positions
- confirmation it prints flat and sits stable.

E) Validation:
Render and export:
- codex_hull_lab/tests/reference_assembly_check.scad
- ensure bow/stern still closed (no new holes)
- ensure underside is visibly flat and low
- ensure STL remains watertight and single connected component

Output:
- list modified files
- report the final footprint size (approx width x length)
- list foot recess coordinates and depth
Stop.

