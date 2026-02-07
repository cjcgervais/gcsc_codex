# Parameters

Units: millimeters unless noted.

## Locked Interface Invariants

Defined in `src/gcsc_reference_params.scad`:

- `REFERENCE_FRAME_SPACING = 16.0` (frame columns at `x = +/-16`)
- `REFERENCE_PIVOT_Y = 33.0`
- `REFERENCE_PIVOT_Z = 38.0` (mapped into model space by helper functions)
- `REFERENCE_SLOT_DIAMETER = 7.5`
- `REFERENCE_BALL_DIAMETER = 7.25`

Slots are cut with hemispherical termini at all four interface locations.

## Core Hull Controls

- `length_mm`, `beam_mm`, `depth_mm`, `wall_mm`, `draft_mm`
- `floor_mm` (floor thickness for robust flat footprint and recess support)
- `curvature_bow`, `curvature_stern`, `belly_fullness`, `rocker`
- `no_bulge_on` (default `true`; enforces streamlined no-bulge longitudinal width)
- `flat_bottom_on` (default `true`)
- `bottom_flat_ratio` (bottom flat-band fraction of section half-beam)
- `gunwale_rise_mm`, `gunwale_curve_exp`
- `gunwale_tip_merge_start`, `gunwale_tip_merge_exp`, `gunwale_tip_merge_ratio`
  (blends gunwale Y-width into bow/stern tips to avoid horn-like tip shoulders)
- `keel_end_lift_mm`, `keel_end_lift_exp` (end rocker/lift control in flat-bottom mode)
- `wall_end_taper_ratio`, `wall_end_taper_exp` (center-heavy wall taper toward bow/stern)
- `end_tip_start`, `end_tip_sharpness`, `end_tip_min_envelope`
  (controls how quickly station beam tapers into bow/stern tip envelope)
- `station_count`
- `end_cap_mm` (minimum bow/stern cap thickness; clamped to `>= wall_mm`)

## Mechanical Feature Toggles

- `enable_reference_interface` (default `true`)
- `pivot_columns_on` (deprecated/no-op; columns are removed from active geometry)
- `seat_on` (default `true`)
- `anchor_on` (default `true`)
- `feet_on` (default `true`)

## Seat Stop Parameters (x = +/-32 fixed)

- `seat_length_mm`
- `seat_height_mm`
- `seat_target_z`

## Anchor Stop Parameters (x = 0)

- `anchor_length_mm`
- `anchor_width_mm`
- `anchor_height_mm`

## Flat Floor + Feet Parameters

- `foot_diameter_mm` (default `8.0`)
- `foot_recess_depth_mm` (default `1.0`)
- `foot_edge_margin_mm`
- `foot_span_fraction`
- `foot_lateral_offset_mm`
- `foot_recess_skin_mm`

## Slot Housing / Safety

- `slot_skin_mm` (minimum wall skin around slot region)
- `slot_entry_overcut_mm` (small top overcut to keep slot entries open)
- `slot_outer_skin_min_mm` (minimum required outer skin used by beam guard)
- `slot_interior_bias_mm` (default `0.0`; `0` keeps slot centerline at locked `y=+/-33`)
- `min_frame_floor_clearance_mm` (minimum required frame-bottom to floor clearance)
- `slot_wall_reinforcement_on` (default `true`)
- `slot_wall_reinf_x_span_mm`
- `slot_wall_reinf_band_mm`
- `slot_wall_reinf_center_offset_mm`
- `slot_wall_reinf_z_pad_mm`
- `interface_margin_mm`
- `frame_floor_margin_mm`

## Optional Legacy Features

- `enable_keel` (default `false`)
- `enable_rim_reinforcement` (default `false`)
- `enable_drainage_hole` (default `false`, non-canonical)
- `enable_flat_cut`, `flat_cut_z`
