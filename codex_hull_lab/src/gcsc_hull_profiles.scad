// Hull station profile math and section definitions.
// Required public parameters are expected from presets/*.scad.

include <gcsc_hull_utils.scad>
include <gcsc_reference_params.scad>

p_length_mm = max(gcsc_safe(length_mm, 148), 120);
p_wall_mm = max(gcsc_safe(wall_mm, 2.4), 0.2);
p_interface_margin_mm = max(gcsc_safe(interface_margin_mm, 1.2), 0.3);
p_slot_interior_bias_mm = max(gcsc_safe(slot_interior_bias_mm, 0.0), 0.0);
p_slot_skin_mm = max(gcsc_safe(slot_skin_mm, max(1.2, min(p_wall_mm * 0.35, 2.0))), 1.2);
p_slot_column_d_mm = max(
    gcsc_safe(slot_column_diameter_mm, REFERENCE_SLOT_DIAMETER + 2 * (p_slot_skin_mm + 1.2)),
    REFERENCE_SLOT_DIAMETER + 2.4
);
p_beam_input_mm = max(gcsc_safe(beam_mm, 84), 1.0);
p_no_bulge_on = gcsc_safe(no_bulge_on, true);
p_slot_outer_skin_min_mm = max(gcsc_safe(slot_outer_skin_min_mm, 0.25), 0.0);
p_slot_housing_radius_mm = REFERENCE_SLOT_DIAMETER / 2 + p_slot_skin_mm;
p_min_beam_for_interface_mm =
    2 * (REFERENCE_PIVOT_Y + REFERENCE_SLOT_DIAMETER / 2 + p_slot_outer_skin_min_mm);
p_beam_mm = max(p_beam_input_mm, p_min_beam_for_interface_mm);
p_depth_input_mm = max(gcsc_safe(depth_mm, 50), p_wall_mm * 2 + 0.2);
p_frame_floor_margin_mm = max(gcsc_safe(frame_floor_margin_mm, 2.0), 0.2);
p_min_depth_for_frame_mm = (REFERENCE_SLOT_ENTRY_Z - REFERENCE_FRAME_BOTTOM_Z) + p_wall_mm + p_frame_floor_margin_mm;
p_min_depth_for_slots_mm = (REFERENCE_SLOT_ENTRY_Z - REFERENCE_PIVOT_Z) + REFERENCE_SLOT_DIAMETER / 2 + p_wall_mm + p_interface_margin_mm;
p_depth_mm = max(p_depth_input_mm, p_min_depth_for_frame_mm, p_min_depth_for_slots_mm);
p_floor_mm = max(gcsc_safe(floor_mm, max(p_wall_mm + 1.2, 4.4)), p_wall_mm + 0.6);
p_draft_mm = gcsc_clamp(gcsc_safe(draft_mm, 12), 0, p_depth_mm);
p_rim_height_mm = gcsc_safe(rim_height_mm, 2.2);
p_keel_depth_mm = gcsc_safe(keel_depth_mm, 2.0);
p_curvature_bow = gcsc_clamp01(gcsc_safe(curvature_bow, 0.58));
p_curvature_stern = gcsc_clamp01(gcsc_safe(curvature_stern, 0.52));
p_belly_fullness = gcsc_clamp01(gcsc_safe(belly_fullness, 0.58));
p_midship_plateau_half_fraction = gcsc_clamp(gcsc_safe(midship_plateau_half_fraction, 0.28), 0.12, 0.55);
p_midship_taper_exponent = max(gcsc_safe(midship_taper_exponent, 1.25), 0.6);
p_rocker = gcsc_clamp01(gcsc_safe(rocker, 0.35));
p_flat_bottom_on = gcsc_safe(flat_bottom_on, true);
p_bottom_flat_ratio = gcsc_clamp(gcsc_safe(bottom_flat_ratio, 0.42), 0.20, 0.72);
p_gunwale_rise_mm = max(gcsc_safe(gunwale_rise_mm, 4.8), 0);
p_gunwale_curve_exp = max(gcsc_safe(gunwale_curve_exp, 1.8), 0.8);
p_gunwale_end_start = gcsc_clamp(gcsc_safe(gunwale_end_start, 0.45), 0.0, 0.95);
p_gunwale_tip_merge_start = gcsc_clamp(gcsc_safe(gunwale_tip_merge_start, 0.52), 0.30, 0.98);
p_gunwale_tip_merge_exp = max(gcsc_safe(gunwale_tip_merge_exp, 1.6), 0.8);
p_gunwale_tip_merge_ratio = gcsc_clamp(gcsc_safe(gunwale_tip_merge_ratio, 0.82), 0.55, 1.0);
p_keel_end_lift_mm = max(gcsc_safe(keel_end_lift_mm, p_flat_bottom_on ? 2.2 : 0.0), 0.0);
p_keel_end_lift_exp = max(gcsc_safe(keel_end_lift_exp, 1.8), 0.8);
p_keel_end_start = gcsc_clamp(gcsc_safe(keel_end_start, 0.48), 0.0, 0.95);
p_wall_end_taper_ratio = gcsc_clamp(gcsc_safe(wall_end_taper_ratio, 0.72), 0.50, 1.0);
p_wall_end_taper_exp = max(gcsc_safe(wall_end_taper_exp, 1.6), 0.6);
p_wall_taper_end_start = gcsc_clamp(gcsc_safe(wall_taper_end_start, 0.50), 0.0, 0.95);
p_tip_depth_start = gcsc_clamp(gcsc_safe(tip_depth_start, 0.82), 0.55, 0.98);
p_tip_depth_exp = max(gcsc_safe(tip_depth_exp, 1.8), 0.8);
p_tip_depth_min_fraction = gcsc_clamp(gcsc_safe(tip_depth_min_fraction, 0.04), 0.01, 0.60);
p_end_tip_start = gcsc_clamp(gcsc_safe(end_tip_start, 0.84), 0.60, 0.99);
p_end_tip_sharpness = max(gcsc_safe(end_tip_sharpness, 2.4), 0.8);
p_end_tip_min_envelope = gcsc_clamp(gcsc_safe(end_tip_min_envelope, 0.01), 0.0, 0.20);
p_station_count = max(gcsc_safe(station_count, 13), 2);
p_top_half_ratio_input = gcsc_clamp(gcsc_safe(top_half_ratio, gcsc_lerp(0.92, 0.86, p_belly_fullness)), 0.82, 0.98);
p_min_top_half_for_slots_mm =
    REFERENCE_PIVOT_Y + REFERENCE_SLOT_DIAMETER / 2 + p_slot_outer_skin_min_mm;
p_min_top_half_ratio_for_slots = p_min_top_half_for_slots_mm / (p_beam_mm / 2);
p_top_half_ratio = gcsc_clamp(max(p_top_half_ratio_input, p_min_top_half_ratio_for_slots), 0.82, 0.98);

// Canonical slot and frame reference coordinates in this hull model space.
p_reference_slot_entry_z_model = gcsc_reference_slot_entry_model_z();
p_reference_pivot_z_model = gcsc_reference_pivot_seat_model_z();
p_reference_frame_bottom_z_model = gcsc_reference_to_model_z(REFERENCE_FRAME_BOTTOM_Z);

function gcsc_reference_slot_entry_z() =
    p_reference_slot_entry_z_model;

function gcsc_reference_slot_seat_z() =
    p_reference_pivot_z_model;

function gcsc_reference_frame_bottom_z() =
    p_reference_frame_bottom_z_model;

function gcsc_station_t(index, count) =
    count <= 0 ? 0 : index / count;

function gcsc_station_x(t) =
    (t - 0.5) * p_length_mm;

function gcsc_bow_ramp(t) =
    pow(gcsc_clamp01(2 * t), gcsc_lerp(1.9, 0.65, p_curvature_bow));

function gcsc_stern_ramp(t) =
    pow(gcsc_clamp01(2 * (1 - t)), gcsc_lerp(1.9, 0.65, p_curvature_stern));

function gcsc_longitudinal_envelope_base(t) =
    gcsc_clamp(0.08 + 0.92 * min(gcsc_bow_ramp(t), gcsc_stern_ramp(t)), 0.06, 1.0);

function gcsc_midship_plateau_envelope(t) =
    let(
        axial = abs(2 * t - 1),
        span = max(1 - p_midship_plateau_half_fraction, 0.001),
        q = gcsc_clamp01((axial - p_midship_plateau_half_fraction) / span),
        taper = pow(q, p_midship_taper_exponent)
    )
    gcsc_clamp(1.0 - 0.90 * taper, 0.10, 1.0);

function gcsc_end_weight(axial, start, expv) =
    pow(gcsc_smoothstep(start, 1.0, axial), expv);

function gcsc_end_tip_envelope(t) =
    let(
        axial = abs(2 * t - 1),
        w = gcsc_end_weight(axial, p_end_tip_start, p_end_tip_sharpness)
    )
    gcsc_lerp(1.0, p_end_tip_min_envelope, w);

function gcsc_longitudinal_envelope(t) =
    max(gcsc_longitudinal_envelope_base(t), gcsc_midship_plateau_envelope(t))
    * gcsc_end_tip_envelope(t);

function gcsc_midship_gain() =
    p_no_bulge_on ? 1.0 : gcsc_lerp(0.90, 1.12, p_belly_fullness);

function gcsc_beam_at(t) =
    p_beam_mm * gcsc_midship_gain() * gcsc_longitudinal_envelope(t);

function gcsc_depth_drop_at_ends() =
    p_flat_bottom_on ? 0 : p_depth_mm * gcsc_lerp(0.06, 0.23, p_rocker);

function gcsc_tip_depth_drop_at(t) =
    let(
        axial = abs(2 * t - 1),
        w = gcsc_end_weight(axial, p_tip_depth_start, p_tip_depth_exp)
    )
    p_depth_mm * (1 - p_tip_depth_min_fraction) * w;

function gcsc_depth_at(t) =
    let(
        rocker_drop = gcsc_depth_drop_at_ends() * pow(abs(2 * t - 1), 1.35),
        tip_drop = p_flat_bottom_on ? gcsc_tip_depth_drop_at(t) : 0,
        drop = max(rocker_drop, tip_drop)
    )
    max(p_depth_mm - drop, p_depth_mm * p_tip_depth_min_fraction);

function gcsc_keel_lift_at(t) =
    let(axial = abs(2 * t - 1))
    p_flat_bottom_on ?
    p_keel_end_lift_mm * gcsc_end_weight(axial, p_keel_end_start, p_keel_end_lift_exp) :
    gcsc_depth_drop_at_ends() * pow(abs(2 * t - 1), 1.45);

function gcsc_gunwale_sheer_at(t) =
    let(axial = abs(2 * t - 1))
    p_gunwale_rise_mm * gcsc_end_weight(axial, p_gunwale_end_start, p_gunwale_curve_exp);

function gcsc_top_half_ratio() =
    p_top_half_ratio;

function gcsc_top_half_ratio_at_t(t) =
    let(
        axial = abs(2 * t - 1),
        merge_w = gcsc_end_weight(axial, p_gunwale_tip_merge_start, p_gunwale_tip_merge_exp),
        ratio_here = p_top_half_ratio * gcsc_lerp(1.0, p_gunwale_tip_merge_ratio, merge_w)
    )
    gcsc_clamp(ratio_here, 0.35, 1.0);

function gcsc_waterline_z() =
    -gcsc_clamp(p_draft_mm, 0, p_depth_mm);

// Center-heavy wall: thickest at midship, tapered toward bow/stern.
function gcsc_wall_inset_at_t(t) =
    let(
        axial = abs(2 * t - 1),
        w = gcsc_end_weight(axial, p_wall_taper_end_start, p_wall_end_taper_exp)
    )
    gcsc_lerp(p_wall_mm, p_wall_mm * p_wall_end_taper_ratio, w);

// Returns YZ points for a closed 2D section polygon.
function gcsc_section_points(half_beam, depth, top_ratio = gcsc_top_half_ratio()) =
    let(top_half = half_beam * top_ratio)
    p_flat_bottom_on ?
    let(bottom_half = max(half_beam * p_bottom_flat_ratio, 0.05))
    [
        [-top_half, 0],
        [ top_half, 0],
        [ half_beam, -depth * 0.22],
        [ half_beam * 0.97, -depth * 0.46],
        [ half_beam * 0.79, -depth * 0.72],
        [ bottom_half, -depth],
        [-bottom_half, -depth],
        [-half_beam * 0.79, -depth * 0.72],
        [-half_beam * 0.97, -depth * 0.46],
        [-half_beam, -depth * 0.22]
    ] :
    [
        [-top_half, 0],
        [ top_half, 0],
        [ half_beam, -depth * 0.22],
        [ half_beam * 0.97, -depth * 0.46],
        [ half_beam * 0.79, -depth * 0.68],
        [ half_beam * 0.46, -depth * 0.88],
        [ 0, -depth],
        [-half_beam * 0.46, -depth * 0.88],
        [-half_beam * 0.79, -depth * 0.68],
        [-half_beam * 0.97, -depth * 0.46],
        [-half_beam, -depth * 0.22]
    ];
