# Iteration Log

## 2026-02-07

### v0.1 - Initial Codex Hull Lab

- Initialized `codex_hull_lab/` structure.
- Added modular source layout and single entry file.
- Added baseline docs, presets, tests, and tooling scripts.

### v0.2 - BOSL2-native Hull Core Implementation

- Reworked hull generator to station-based segmented loft (`hull()` between adjacent stations).
- Implemented shelling by subtracting inward-offset inner loft from outer loft.
- Added required parameter API (`length_mm`, `beam_mm`, `depth_mm`, `draft_mm`, `wall_mm`, `rim_height_mm`, `keel_depth_mm`, `curvature_bow`, `curvature_stern`, `belly_fullness`, `rocker`, `station_count`).
- Added public build module `gcsc_hull_build()` and wired `src/gcsc_hull_entry.scad` to it.
- Updated BOSL2 adapter with explicit graceful assertion when BOSL2 is missing.

### v0.3 - Preset Regression and Flat-Cut Calibration Tools

- Added `tests/preset_smoke.scad` to stage all four presets in one visual regression scene.
- Extended `tools/render_preview.ps1` with `-Preset` so preset-specific previews can be rendered without editing source files.
- Added `tools/flat_cut_calibration.ps1` and `tests/flat_cut_calibration_slice.scad` for 20 mm center-slice calibration exports used to tune `flat_cut_z`.

### v0.2 - Multi-volume hull repair

Audit findings across build pipeline:

- Outer hull surface generator: `gcsc_outer_hull()` in `src/gcsc_hull_shell.scad`.
- Hollowing module: `gcsc_hull_shell()` in `src/gcsc_hull_shell.scad` (`difference` of outer hull and translated/scaled inner cavity).
- Positive feature modules: `gcsc_keel_feature()` and `gcsc_rim_reinforcement_feature()` in `src/gcsc_hull_features.scad`.
- Top-level combiner: `gcsc_hull_build()` in `src/gcsc_hull_core.scad`.

Repair actions:

- Reworked top-level composition to an explicit positive `union()` in `gcsc_hull_positive_union()`, then applied cuts in a single `difference()` inside `gcsc_hull_build()`.
- Added safe parameter clamps to prevent invalid shell subtraction:
  - `wall_mm > 0`
  - `beam_mm > 0`
  - `depth_mm > wall_mm * 2`
- Ensured feature overlap with hull body (not just touching surfaces) so keel/rim merge into one watertight solid instead of separate volumes.

### v0.4 - Great_Canadian_Soap_Canoe Reference Integration

- Added v5.3 reference wrapper layer under `reference/`:
  - `hull_v5_3_reference.scad`
  - `frame_v5_3_reference.scad`
  - `slot_plug_reference.scad`
  - `anchor_reference.scad`
- Added `src/gcsc_reference_params.scad` to lock canonical interface dimensions:
  - Pivot Y/Z, slot/ball diameters, frame spacing, foot pad geometry, and fit target.
- Constrained hull behavior to inherited interface coordinates:
  - Added canonical pivot slot cuts with hemispherical seat.
  - Added slot-entry relief and local wall-clearance volumes.
  - Enforced frame spacing invariants and compatibility guard assertions.
- Added `gcsc_internal_frame_support()` into positive geometry union.
- Added reference-compatible foot-pad recess cuts.
- Added `tests/reference_assembly_check.scad` to render generated hull + reference frame + slot plugs in aligned coordinates.
- Updated presets and docs for the Great_Canadian_Soap_Canoe lab positioning and v5.3 compatibility-first workflow.

### v0.5 - True GCSC Mechanics + Sink-Stable Base

- Removed internal frame-support/rib behavior from active build flow.
- Added `gcsc_seat_stops_feature()` with fixed stop locations at `x = +/-32`.
- Added `gcsc_anchor_stop_feature()` at `x = 0` as decorative + physical stop.
- Added `gcsc_pivot_interface_columns_feature()` at locked frame columns (`x = +/-16`) to house slot region inside wall volume.
- Simplified slot subtraction to locked hemispherical-terminus cavities only (7.5 mm), removing exterior-risk relief cuts.
- Added explicit bow/stern end caps in shell generation (`gcsc_bow_cap()`, `gcsc_stern_cap()`) and constrained inner cavity span so end caps remain.
- Added low-profile sink-stable flat skid pad via `gcsc_base_flat_feature()`.
- Added four foot recess pockets via `gcsc_foot_recess_cutouts()` with default geometry:
  - diameter: `8.0 mm`
  - depth: `1.0 mm`
- Default preset (`gcsc_default`) computed base footprint:
  - approx `103.6 mm` (length) x `38.0 mm` (width)
- Default foot recess centers:
  - `(-40.7, -14)`, `(-40.7, 14)`, `(40.7, -14)`, `(40.7, 14)`

Validation summary:

- `tests/render_test.scad`: rendered, `Simple: yes`
- `tests/parameter_sweep.scad`: rendered, `Simple: yes`
- `tests/reference_assembly_check.scad`: rendered, `Simple: yes`
- `src/gcsc_hull_entry.scad` STL mesh check (trimesh):
  - watertight: `true`
  - is_volume: `true`
  - connected components: `1`

### v0.6 - Flat Waterline Floor + Wall-Housed Internal Slots

- Replaced curved-keel behavior with true flat-bottom mode:
  - Added `flat_bottom_on` profile control and disabled keel lift in flat mode.
- Added robust floor thickness control:
  - `floor_mm` now drives inner cavity shift for a thick flat floor.
- Added curved-up gunwale behavior with preserved flat floor:
  - `gunwale_rise_mm` and `gunwale_curve_exp` applied per-station.
- Updated seat stop behavior to true end-floor fills:
  - Seat zones now fill from `x = +/-32` toward bow/stern with no side/back gaps.
  - Seat top target supports frame swing-stop contact (`seat_target_z`).
- Kept decorative/functional center stop at `x = 0`.
- Kept frame columns at `x = +/-16`.
- Kept internal slot negative-space geometry with hemispherical termini:
  - diameter `7.5 mm`
  - nominal depth `7 mm` to seat centerline with controlled top overcut.
- Removed active flat skid-pad dependency; foot recesses are now cut directly into the flat floor.
- Foot recess default retained per user correction:
  - diameter: `8.0 mm`
  - depth: `1.0 mm`
  - default centers: `(-40.7, -9.0)`, `(-40.7, 9.0)`, `(40.7, -9.0)`, `(40.7, 9.0)`

Validation summary:

- `src/gcsc_hull_entry.scad` export:
  - `Simple: yes`
  - mesh (trimesh): watertight `true`, is_volume `true`, connected components `1`
- `tests/reference_assembly_check.scad` export:
  - rendered with locked interface placements preserved

### v0.7 - Slot Pocket Geometry + Wall Thickening

- Updated slot subtraction geometry to ensure each slot is a shallow pocket with
  explicit concave terminus behavior:
  - maintained locked diameter (`7.5 mm`)
  - maintained locked seat/entry references (`z_pivot_seat=38`, `z_slot_entry=45`)
  - enforced `~7 mm` seat-center depth check
  - changed seat cut to lower-hemisphere-only subtraction (concave seat), avoiding
    full-sphere cylindrical-through appearance
- Thickened default hull structure around slot housing:
  - `wall_mm: 3.0 -> 4.8`
  - `floor_mm: 4.8 -> 6.0`
  - `slot_skin_mm: 1.2 -> 2.0`
  - `slot_column_diameter_mm: 12.0 -> 13.8`
  - `end_cap_mm: 2.4 -> 4.8`
  - `slot_entry_overcut_mm: 1.0 -> 0.25`

Assumption recorded:

- "Slots only go down like 7 mm and terminate in a concave seat" interpreted as
  `7 mm` from slot entry plane to seat centerline, with concavity continuing below
  that centerline as a hemispherical terminus (v5.3-compatible behavior).

Validation summary:

- `tests/render_test.scad` rendered with OpenSCAD CLI:
  - output: `_codex/validate_render_test_20260207_slotfix_cli.stl`
  - `Simple: yes`
- `tests/reference_assembly_check.scad` rendered with OpenSCAD CLI:
  - output: `_codex/validate_reference_assembly_20260207_slotfix_cli.stl`
  - `Simple: yes`
- Mesh check on render-test hull STL (`trimesh`):
  - watertight: `true`
  - is_volume: `true`
  - connected components: `1`

### v0.7.1 - Wall Accommodation Mirrored to Other Presets

- Applied the same slot-housing wall defaults from `gcsc_default` to:
  - `presets/gcsc_fast_print.scad`
  - `presets/gcsc_high_stability.scad`
- Updated in both presets:
  - `wall_mm = 4.8`
  - `floor_mm = 6.0`
  - `slot_skin_mm = 2.0`
  - `slot_column_diameter_mm = 13.8`
  - `end_cap_mm = 4.8`
  - `slot_entry_overcut_mm = 0.25`

Validation summary:

- `gcsc_fast_print` render target:
  - `_codex/validate_fast_print_20260207_slotfix_cli.stl`
  - OpenSCAD: `Simple: yes`
  - trimesh: watertight `true`, is_volume `true`, connected components `1`
- `gcsc_high_stability` render target:
  - `_codex/validate_high_stability_20260207_slotfix_cli.stl`
  - OpenSCAD: `Simple: yes`
  - trimesh: watertight `true`, is_volume `true`, connected components `1`

### v0.8 - Remove Slot Columns, Enforce True Wall Thickening

- Removed large slot-housing column behavior from active defaults by switching
  `pivot_columns_on` to `false` across active presets.
- Increased actual shell wall thickness target to `wall_mm = 6.0` across active
  presets so thickening happens in the hull shell, not via interior cylinders.
- Kept slot geometry as negative cutouts only:
  - no positive slot cylinders in build by default
  - seat-terminus slot cut remains `7.5 mm` concave interface cut
- Tightened slot interface beam floor logic:
  - replaced column-based beam minimum dependency with slot-housing-radius-based
    beam minimum so wall thickness is driven by shell math.
- Removed unused `slot_support_factor` input path to avoid unknown-variable noise.

Validation summary:

- `tests/render_test.scad`:
  - `_codex/validate_render_test_20260207_wallfix_cli.stl`
  - OpenSCAD: `Simple: yes`
  - trimesh: watertight `true`, is_volume `true`, connected components `1`
- `tests/reference_assembly_check.scad`:
  - `_codex/validate_reference_assembly_20260207_wallfix_cli.stl`
  - OpenSCAD: `Simple: yes`
  - trimesh: watertight `true`, is_volume `true`, connected components `1`

### v0.9 - 9 mm Wall + Inward Top-Down Slot Path

- Raised active preset wall targets to requested heavy wall class:
  - `wall_mm = 9.0`
  - `floor_mm = 10.0`
  - `end_cap_mm = 9.0`
- Updated slot generation to top-down inward-biased negative cavity behavior:
  - entry path biased toward interior (`y=0`) using `slot_interior_bias_mm`
  - strict `7.0 mm` depth-to-seat-center check (`+/-0.01`)
  - explicit concave 7.5 mm seat terminus retained
  - reduced outer-side clip guard so slot body stays internal without forcing
    shallow exterior-only depression behavior
  - added intermediate cavity bridge volumes to create a fuller slot channel from
    entry toward seat
- Increased beam in presets so fixed slot coordinates remain properly housed by
  shell thickness at slot heights:
  - default `beam_mm: 84 -> 92`
  - fast_print `beam_mm: 82 -> 90`
  - high_stability `beam_mm: 88 -> 94`
  - experiment `beam_mm: 86 -> 94`

Validation summary:

- Default pipeline:
  - `_codex/validate_render_test_20260207_slotbias9d_cli.stl` (`Simple: yes`)
  - `_codex/validate_reference_assembly_20260207_slotbias9d_cli.stl` (`Simple: yes`)
  - trimesh both: watertight `true`, is_volume `true`, components `1`
- Additional preset checks:
  - `_codex/validate_fast_print_20260207_slotbias9d_cli.stl` (`Simple: yes`)
  - `_codex/validate_high_stability_20260207_slotbias9d_cli.stl` (`Simple: yes`)
  - trimesh both: watertight `true`, is_volume `true`, components `1`

### v0.10 - Inheritable Slot Pattern Alignment + Open-Top Protection

- Aligned slot behavior closer to Inheritable_Dimensions intent:
  - vertical top-entry shaft (biased toward interior side)
  - vertical/mid bridge support to avoid 45-degree-only dish behavior
  - explicit entry relief to prevent a thin strip covering slot from above
  - strict 7 mm entry-to-seat-center depth check preserved
- Added `slot_entry_relief_mm` parameter and defaulted to `1.2` in active presets.
- Forced `high_stability` preset to open-top behavior by disabling rim reinforcement:
  - `enable_rim_reinforcement = false`

Validation summary:

- Default/reference pipeline:
  - `_codex/validate_render_test_20260207_slotfinal_cli.stl` (`Simple: yes`)
  - `_codex/validate_reference_assembly_20260207_slotfinal_cli.stl` (`Simple: yes`)
- High stability direct build:
  - `_codex/validate_high_stability_20260207_slotfinal_cli.stl` (`Simple: yes`)
- trimesh (all above):
  - watertight `true`
  - is_volume `true`
  - connected components `1`

### v0.11 - Strict Slot Primitive Mode (User Clarification)

- Updated slot cavity implementation to strict primitive behavior:
  - one vertical cylindrical negative cut
  - terminating in one concave hemispherical seat on the same axis
  - removed multi-bridge blended slot shaping from prior iteration
- Kept inward bias minimal and controlled (`slot_interior_bias_mm = 1.4`) so slot
  favors interior side without drifting far from locked pivot references.
- Kept entry relief (`slot_entry_relief_mm = 1.2`) to avoid thin strip/lip covering
  slot entry from top.
- Retained thick wall baseline (`wall_mm = 9.0`) and open-top high-stability preset.

Validation summary:

- `_codex/validate_render_test_20260207_slotstrict_cli.stl` (`Simple: yes`)
- `_codex/validate_reference_assembly_20260207_slotstrict_cli.stl` (`Simple: yes`)
- `_codex/validate_high_stability_20260207_slotstrict_cli.stl` (`Simple: yes`)
- trimesh (all above): watertight `true`, is_volume `true`, components `1`

### v0.12 - Midsection Taper Remediation + Base Widening

- Addressed user-reported overly curved midwall and narrow base by changing
  profile generation instead of slot-cut complexity.
- Added midship width plateau controls in profile math:
  - `midship_plateau_half_fraction`
  - `midship_taper_exponent`
  - `gcsc_longitudinal_envelope()` now takes the max of legacy bow/stern envelope
    and a plateau envelope to keep `x=+/-16` slot stations wider.
- Increased base stability footprint by widening flat-bottom band defaults:
  - `bottom_flat_ratio` increased across active presets
  - added explicit `top_half_ratio` defaults to reduce gunwale-to-midwall taper
  - widened `beam_mm` in active presets
- Kept strict slot primitive mode from v0.11:
  - vertical cylinder + hemispherical seat only
  - slight interior bias only

Validation summary:

- `_codex/validate_render_test_20260207_profilefix2_cli.stl`
  - OpenSCAD: `Simple: yes`
  - trimesh: watertight `true`, is_volume `true`, components `1`
  - bottom contact width estimate: `44.796 mm`
  - slot-station outer half-width at `x=16, z=-7`: `~38.50 mm`
- `_codex/validate_high_stability_20260207_profilefix2_cli.stl`
  - OpenSCAD: `Simple: yes`
  - trimesh: watertight `true`, is_volume `true`, components `1`
  - bottom contact width estimate: `48.959 mm`

### v0.13 - Streamlined Thick Wall (No Bulges, No Columns)

- Enforced streamlined no-bulge profile behavior:
  - added `no_bulge_on` profile control and defaulted it to `true` in active presets.
- Removed pivot-column contribution from active hull build path.
- Added local slot-zone sidewall reinforcement bands:
  - `gcsc_slot_wall_reinforcement_feature()`
  - keeps slot area thick without cylindrical internal columns.
- Kept locked interface coordinates and switched slot defaults to true vertical axis:
  - `slot_interior_bias_mm = 0.0`
  - slot diameter `7.5 mm`, seat depth `7.0 mm`, hemispherical seat preserved.
- Reduced global beam targets to user-requested narrow class:
  - active preset beam setpoints moved to `74 mm`.
- Increased base footprint width from centerline by 50% ratio change:
  - `bottom_flat_ratio` raised to `~1.5x` prior values (e.g. `0.46 -> 0.69`).
- Spread foot recess layout:
  - default offsets now `x = +/-48.1`, `y = +/-14.0`.

Validation summary (default preset / entry build):

- `_codex/validate_entry_20260207_streamlined_cli.stl`
  - watertight `true`
  - is_volume `true`
  - connected components `1`
  - bounding box: `148.705 x 74.0 x 55.0 mm`
  - base contact span near min-Z: `51.06 mm` (Y)
- `_codex/validate_reference_assembly_20260207_streamlined_cli.stl`
  - is_volume `true`
  - connected components `1`

### v0.14 - Midship Foot Recess Shift + Swing/Floor Guard Confirmation

- Pulled 4 foot recesses inward toward midship (away from bow/stern):
  - reduced `foot_span_fraction` defaults in active presets.
  - updated fallback default in feature math to `0.44`.
- Kept lateral foot offsets unchanged (Y placement) and only reduced X spread.
- Retained prior swing-fit seat and slot settings:
  - inward slot bias toward `y=0` (`slot_interior_bias_mm = 1.2`)
  - raised distal seat target (`seat_target_z = -18.0`)
  - floor-clearance guard `min_frame_floor_clearance_mm = 11.0`.

Measured results (`gcsc_default`):

- CF frame ball center-to-center distance: `66.0 mm` (`y = +/-33`).
- Slot axes after inward bias: `y = +/-31.8 mm`.
- Slot depth to seat center: `7.0 mm`; radial clearance: `0.125 mm`.
- Frame bottom to hull floor clearance: `12.0 mm` (`>= 11.0 mm` target).
- Seat stop requirement for contact at `x = +/-32`:
  - required minimum seat top `z = -20.601 mm`
  - configured seat top `z = -18.0 mm` (higher, so contact achieved).
- Foot recess centers moved to:
  - `(-32.56, -14.0)`, `(-32.56, 14.0)`, `(32.56, -14.0)`, `(32.56, 14.0)`.

Validation outputs:

- `_codex/validate_entry_20260207_swingfit_midfeet_cli.stl`
  - watertight `true`, is_volume `true`, connected components `1`
- `_codex/validate_render_test_20260207_swingfit_midfeet_cli.stl`
- `_codex/validate_reference_assembly_20260207_swingfit_midfeet_cli.stl`

### v0.15 - Slot Y Re-Lock + Beam +2mm + End Curvature/Taper

- Re-locked slot cut centerlines to exact reference Y positions by removing
  inward slot-axis shift:
  - `slot_interior_bias_mm = 0.0` in active presets.
- Widened active preset beam by `+2.0 mm`:
  - `75.5 -> 77.5`.
- Added stronger bow/stern shaping while preserving midship stability:
  - `keel_end_lift_mm`, `keel_end_lift_exp`
  - increased gunwale end curvature response via preset tuning.
- Added algorithmic wall taper for center-heavy massing:
  - `wall_end_taper_ratio`, `wall_end_taper_exp`
  - inner cavity inset now varies by station (`gcsc_wall_inset_at_t`), thinner
    at bow/stern than midship.

Measured default results:

- CF frame ball C-C Y: `66.0 mm`
- Slot centerlines: `y = +/-33.0 mm`
- Hull Y width: `77.5 mm`
- Outer skin at slot/rim zone: `~1.225 mm`
- Frame bottom floor clearance at `x=16`: `11.848 mm` (>= `11 mm`)
- Seat stop requirement at `x=+/-32`:
  - required min seat top `z = -20.601 mm`
  - configured seat top `z = -18.0 mm`
- Wall thickness profile (default):
  - midship: `10.0 mm`
  - bow/stern target: `7.2 mm`

Validation outputs:

- `_codex/validate_entry_20260207_y33widen2_cli.stl`
- `_codex/validate_render_test_20260207_y33widen2_cli.stl`
- `_codex/validate_reference_assembly_20260207_y33widen2_cli.stl`

### v0.16 - Gunwale Y-Axis Tip Merge (Bow/Stern Horn Softening)

- Smoothed end-zone blending for bow/stern transitions by updating
  `gcsc_end_weight()` to use `gcsc_smoothstep()`.
- Added station-aware gunwale top-width blending controls:
  - `gunwale_tip_merge_start`
  - `gunwale_tip_merge_exp`
  - `gunwale_tip_merge_ratio`
- Applied new top-width blend in station generation so tip-adjacent gunwale
  sections merge into hull shoulders instead of presenting a sharp horn look.
- Retuned default preset end taper for a softer lead-in:
  - `end_tip_start = 0.60`
  - `end_tip_sharpness = 1.8`
  - `end_tip_min_envelope = 0.045`

Validation summary (default entry build):

- `_codex/validate_entry_20260207_gunwaleblend_cli.stl`
  - trimesh: watertight `true`, is_volume `true`, components `1`
  - bounds: `[-74.3524, -39.75, -50.0]` to `[74.3524, 39.75, 11.4]`

### v0.17 - Inheritable Danforth Anchor at X=0 with +14 mm Compensation

- Replaced synthetic center stop block with canonical Danforth anchor placement
  in `gcsc_anchor_stop_feature()`.
- Anchor is now placed at exact centerline `x = 0`.
- Applied inherited vertical compensation pattern from v5.3:
  - source shift `+14.05 mm`
  - internal offset compensation `+14.0 mm`
  - light floor embed `-0.20 mm`
- Kept anchor geometry untouched by loading canonical reference wrapper;
  no shape edits were applied to the Danforth model.

Validation summary (default entry build):

- `_codex/validate_entry_20260207_anchor_at_x0_z14_cli.stl`
  - trimesh: watertight `true`, is_volume `true`, components `1`
  - bounds: `[-74.3524, -39.75, -50.0]` to `[74.3524, 39.75, 11.4]`

### v0.18 - Anchor Z Drop Adjustment (-8 mm)

- Lowered Danforth anchor placement by an additional `8.0 mm` while keeping
  inherited anchor geometry unchanged.
- Added fixed placement offset:
  - `f_anchor_drop_mm = 8.0`
  - applied as subtraction in `anchor_z` calculation.

Export artifact:

- `_codex/validate_entry_20260207_anchor_zminus8_cli.stl`

### v0.19 - Phase B: Mechanics-Locked Presets + Shape Sensitivity Gate

- Added mechanics/style preset split:
  - new baseline preset `presets/gcsc_mechanics_locked.scad`
  - style presets now include the mechanics baseline and override profile controls only:
    - `presets/gcsc_default.scad`
    - `presets/gcsc_fast_print.scad`
    - `presets/gcsc_high_stability.scad`
    - `presets/gcsc_experiment.scad`
- Updated profile controls for predictable end-response:
  - corrected bow/stern curvature mapping so bow controls bow-side response and stern controls stern-side response
  - exposed deterministic measurement helpers in `src/gcsc_hull_profiles.scad`:
    - tip half-beam, tip top-half-beam, and taper response metrics
  - added `midship_plateau_blend` and `midship_plateau_end_blend` controls to keep slot-zone width stable while preserving end sensitivity
- Added deterministic sensitivity verifier:
  - `tools/verify_shape_sensitivity.py`
  - checks measurable response for:
    - `curvature_bow`
    - `curvature_stern`
    - `gunwale_tip_merge_ratio`
  - writes JSON report under `_codex/reports/`
- Added regression suite:
  - `tests/test_shape_sensitivity.py`
  - enforces mechanics-locked preset split and sensitivity gate behavior
- Reliability fix:
  - `tools/verify_reference_fit.py` now exports fresh geometry by default
  - optional reuse path is explicit via `--reuse-exported-stls`

Validation summary:

- `python codex_hull_lab/tools/verify_reference_fit.py --output-json _codex/reports/reference_fit_report.json --floor-clearance-min-mm 2.0`
  - PASS
  - min frame gap: `0.11365340133589984 mm`
  - floor clearance: `3.0 mm`
- `python codex_hull_lab/tools/verify_shape_sensitivity.py --output-json _codex/reports/shape_sensitivity_report.json`
  - PASS
  - bow delta: `0.4091 mm`
  - stern delta: `0.3943 mm`
  - gunwale min top-half delta: `0.9451 mm`
- `python tests/test_reference_fit.py`
  - `4/4` OK
- `python tests/test_shape_sensitivity.py`
  - `5/5` OK
- OpenSCAD profile validation:
  - `codex_hull_lab/tests/render_test.scad` compiled to `_codex/reports/phaseb_render_test.csg`
  - `codex_hull_lab/tests/parameter_sweep.scad` compiled to `_codex/reports/phaseb_parameter_sweep.csg`

### v0.20 - Phase C: Governance + Session Memory Hardening

- Added canonical slot acceptance specification:
  - `docs/SLOT_MECHANISM_ACCEPTANCE.md`
  - codifies non-negotiable slot behavior, deterministic tolerances, and required artifacts.
- Hardened governance hook behavior:
  - `.claude/hooks/functional-requirements-check.py` now consumes deterministic mechanics output when available and fresh.
  - hard-block conditions added for:
    - `slot_insertion_corridor = false`
    - `frame_interference = false`
    - `frame_floor_clearance = false`
  - legacy regex checks remain in place for advisory and critical pattern detection.
- Reconciled historical compatibility claim provenance:
  - annotated `Inheritable_Dimensions/Final_GCSC_Assembly.md` to mark `PASS (11mm)` floor-clearance text as historical and superseded by deterministic geometry-grounded measurements.
- Added governance regression coverage:
  - `tests/test_functional_requirements_hook.py`
  - verifies mechanics-report-driven hard blocking and stale-report fail-open behavior.

### v0.21 - Full Validation Unification + Traceable Release Packaging

- Added authoritative validator:
  - `codex_hull_lab/tools/validate_full.py`
  - single command now orchestrates:
    - `verify_reference_fit.py`
    - `verify_shape_sensitivity.py`
    - `tests/test_reference_fit.py`
    - `tests/test_shape_sensitivity.py`
    - `tests/test_functional_requirements_hook.py`
  - emits canonical machine-readable report:
    - `_codex/reports/full_validation_report.json`

- Added deterministic robustness sweeps:
  - baseline checks across preset variants:
    - `gcsc_default`, `gcsc_fast_print`, `gcsc_high_stability`, `gcsc_experiment`
  - bounded perturbations applied per preset:
    - `slot_entry_relief_plus_0p60`
    - `floor_plus_0p80`
  - sweep hard-fails when any scenario breaks:
    - `slot_insertion_corridor`
    - `frame_interference`
    - `frame_floor_clearance`

- Added dynamic kinematic validation:
  - sampled swing-path collision checks around pivot axis (Y-axis) for both frame placements.
  - neutral-only checks are now supplemented by angle-sweep interference/gap gates.

- Added manufacturability gates:
  - minimum wall-thickness estimate
  - recess skin thickness check
  - overhang risk ratio
  - stable contact-footprint area/span checks

- Added golden geometry signatures:
  - `codex_hull_lab/reference/golden_geometry_signatures.json`
  - validated by `validate_full.py` for key presets.
  - drift requires explicit override via:
    - `--allow-signature-drift` (or `GCSC_ALLOW_SIGNATURE_DRIFT=1`)

- Added release packaging automation:
  - `codex_hull_lab/tools/package_release.py`
  - exports STL + 3MF, writes provenance sidecars, copies validation reports, writes release manifest under:
    - `_codex/releases/<version>/`

- Added long-term hygiene routine:
  - `codex_hull_lab/tools/hygiene_maintenance.py`
  - archives stale `_codex/tmp_*` artifacts into `_codex/archive/tmp_cleanup/*`
  - normalizes mojibake patterns in inherited doc zones.

- CI unification:
  - `.github/workflows/validate.yml` mechanics job now runs:
    - `python codex_hull_lab/tools/validate_full.py --project-root . --output-json _codex/reports/full_validation_report.json`
  - validation JSON artifacts are uploaded on every mechanics job run:
    - `_codex/reports/*.json`

Validation summary:

- `python codex_hull_lab/tools/validate_full.py --project-root . --output-json _codex/reports/full_validation_report.json --write-signature-baseline --no-subcommand-fail-fast`
  - PASS
  - report: `_codex/reports/full_validation_report.json`
- `python codex_hull_lab/tools/package_release.py --project-root . --version vsmoke-package --presets gcsc_default --skip-validation --overwrite`
  - PASS
  - bundle: `_codex/releases/vsmoke-package/`
- `python codex_hull_lab/tools/hygiene_maintenance.py --project-root . --dry-run`
  - PASS (no stale tmp files moved in dry-run; no mojibake replacements needed in scanned scope)
