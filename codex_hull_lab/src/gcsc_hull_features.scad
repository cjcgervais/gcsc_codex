// Compatibility-critical hull features and mechanics.

include <gcsc_hull_shell.scad>
include <gcsc_hull_bosl2_adapter.scad>
include <gcsc_reference_params.scad>
include <../reference/anchor_reference.scad>

f_enable_keel = gcsc_safe(enable_keel, false);
f_enable_rim_reinforcement = gcsc_safe(enable_rim_reinforcement, false);
f_enable_drainage_hole = gcsc_safe(enable_drainage_hole, false);
f_enable_reference_interface = gcsc_safe(enable_reference_interface, true);

f_seat_on = gcsc_safe(seat_on, true);
f_seat_length_mm = max(gcsc_safe(seat_length_mm, 12), 4);
f_seat_height_mm = max(gcsc_safe(seat_height_mm, 18), 1.0);
f_seat_target_z = gcsc_safe(seat_target_z, gcsc_reference_frame_bottom_z() + 0.8);

f_anchor_on = gcsc_safe(anchor_on, true);
f_anchor_length_mm = max(gcsc_safe(anchor_length_mm, 14), 5);
f_anchor_width_mm = max(gcsc_safe(anchor_width_mm, 20), 6);
f_anchor_height_mm = max(gcsc_safe(anchor_height_mm, 8), 1.0);
f_anchor_internal_offset_comp_mm = 14.0;
f_anchor_source_vertical_shift_mm = 14.05;
f_anchor_embed_mm = 0.20;
f_anchor_rotation_z_deg = 90;
f_anchor_drop_mm = 8.0;

f_feet_on = gcsc_safe(feet_on, true);
f_foot_diameter_mm = max(gcsc_safe(foot_diameter_mm, 8.0), 4.0);
f_foot_recess_depth_mm = max(gcsc_safe(foot_recess_depth_mm, 1.0), 0.2);
f_foot_edge_margin_mm = max(gcsc_safe(foot_edge_margin_mm, 10), 2);
f_foot_span_fraction = gcsc_clamp(gcsc_safe(foot_span_fraction, 0.44), 0.20, 0.90);
f_foot_lateral_offset_mm = max(gcsc_safe(foot_lateral_offset_mm, 14), 2);
f_foot_recess_skin_mm = max(gcsc_safe(foot_recess_skin_mm, 1.2), 0.4);

f_slot_skin_mm = max(gcsc_safe(slot_skin_mm, p_slot_skin_mm), 1.2);
f_slot_column_diameter_mm = max(
    gcsc_safe(slot_column_diameter_mm, REFERENCE_SLOT_DIAMETER + 2 * (f_slot_skin_mm + 1.2)),
    REFERENCE_SLOT_DIAMETER + 2.4
);
f_slot_entry_overcut_mm = max(gcsc_safe(slot_entry_overcut_mm, 0.0), 0.0);
f_slot_interior_bias_mm = max(gcsc_safe(slot_interior_bias_mm, 0.0), 0.0);
f_slot_entry_relief_mm = max(gcsc_safe(slot_entry_relief_mm, 1.2), 0.0);
f_slot_wall_reinforcement_on = gcsc_safe(slot_wall_reinforcement_on, true);
f_slot_wall_reinf_x_span_mm = max(gcsc_safe(slot_wall_reinf_x_span_mm, 20.0), 6.0);
f_slot_wall_reinf_band_mm = max(gcsc_safe(slot_wall_reinf_band_mm, 3.4), 1.2);
f_slot_wall_reinf_center_offset_mm = gcsc_safe(slot_wall_reinf_center_offset_mm, 0.6);
f_slot_wall_reinf_z_pad_mm = max(gcsc_safe(slot_wall_reinf_z_pad_mm, 2.2), 0.0);
f_min_frame_floor_clearance_mm = max(gcsc_safe(min_frame_floor_clearance_mm, 11.0), 0.0);

f_drainage_hole_diameter_mm = gcsc_safe(drainage_hole_diameter_mm, 3.0);
f_keel_width_mm = gcsc_safe(keel_width_mm, 5.5);
f_feature_overlap_mm = max(p_wall_mm * 0.35, 0.3);
f_keel_radius_mm = max(p_keel_depth_mm * 0.62, 0.35);
f_keel_overlap_mm = max(min(p_keel_depth_mm * 0.45, p_wall_mm * 0.6), 0.2);
f_keel_center_z = -p_depth_mm - p_keel_depth_mm + f_keel_radius_mm + f_keel_overlap_mm;

f_foot_x_limit_mm = max(p_length_mm / 2 - f_foot_edge_margin_mm - f_foot_diameter_mm / 2, 6);
f_foot_x_offset_mm = gcsc_clamp((p_length_mm * f_foot_span_fraction) / 2, 6, f_foot_x_limit_mm);
f_foot_y_limit_mm = max(p_beam_mm / 2 - f_foot_edge_margin_mm - f_foot_diameter_mm / 2, 4);
f_floor_flat_half_mm = max((gcsc_beam_at(0.5) / 2) * p_bottom_flat_ratio - 0.6, 4);
f_foot_y_limit_flat_mm = max(f_floor_flat_half_mm - f_foot_diameter_mm / 2 - 0.4, 2);
f_foot_y_offset_mm = gcsc_clamp(f_foot_lateral_offset_mm, 2, min(f_foot_y_limit_mm, f_foot_y_limit_flat_mm));

function gcsc_t_from_x(x) =
    gcsc_clamp01(x / p_length_mm + 0.5);

function gcsc_outer_floor_z_at_x(x) =
    let(t = gcsc_t_from_x(x))
    -gcsc_depth_at(t) + gcsc_keel_lift_at(t);

function gcsc_inner_floor_z_at_x(x) =
    gcsc_outer_floor_z_at_x(x) + p_floor_mm;

module gcsc_reference_slot_axes() {
    for (x_sign = [-1, 1]) {
        for (y_sign = [-1, 1]) {
            translate([x_sign * REFERENCE_FRAME_SPACING, y_sign * REFERENCE_PIVOT_Y, 0])
                children();
        }
    }
}

module gcsc_rounded_block_xy(length_x, width_y, height_z, corner_r = 1.0) {
    l_core = max(length_x - 2 * corner_r, 0.2);
    w_core = max(width_y - 2 * corner_r, 0.2);
    r = min(corner_r, min(length_x, width_y) / 2 - 0.05);
    linear_extrude(height = height_z, center = false, convexity = 6)
        offset(r = max(r, 0))
            square([l_core, w_core], center = true);
}

module gcsc_end_floor_fill(x_start, x_end, seat_top_z) {
    seat_base_z = min(gcsc_inner_floor_z_at_x((x_start + x_end) / 2), seat_top_z - 0.4);
    x_min = min(x_start, x_end);
    x_max = max(x_start, x_end);
    seat_h = max(seat_top_z - seat_base_z, 0.5);

    intersection() {
        translate([x_min, -p_beam_mm, seat_base_z])
            cube([x_max - x_min, 2 * p_beam_mm, seat_h], center = false);
        gcsc_inner_cavity_scaled();
    }
}

// Raised end-floor seats at x = +/-32; filled to walls and toward bow/stern.
module gcsc_seat_stops_feature() {
    if (f_seat_on) {
        seat_top_z_pos = max(gcsc_inner_floor_z_at_x(32) + f_seat_height_mm, f_seat_target_z);
        seat_top_z_neg = max(gcsc_inner_floor_z_at_x(-32) + f_seat_height_mm, f_seat_target_z);
        floor_clearance_mm = gcsc_reference_frame_bottom_z() - gcsc_inner_floor_z_at_x(REFERENCE_FRAME_SPACING);
        seat_dx_mm = 32 - REFERENCE_FRAME_SPACING;
        seat_dz_mm = gcsc_reference_slot_seat_z() - gcsc_reference_frame_bottom_z();
        seat_contact_z_required = gcsc_reference_slot_seat_z() - sqrt(max(seat_dz_mm * seat_dz_mm - seat_dx_mm * seat_dx_mm, 0));
        seat_contact_angle_deg = atan2(seat_dx_mm, sqrt(max(seat_dz_mm * seat_dz_mm - seat_dx_mm * seat_dx_mm, 0)));

        assert(
            floor_clearance_mm >= f_min_frame_floor_clearance_mm,
            str(
                "Frame bottom floor clearance too low. Need >= ",
                f_min_frame_floor_clearance_mm,
                " mm, got ",
                floor_clearance_mm,
                " mm."
            )
        );
        assert(
            seat_dz_mm > seat_dx_mm,
            "Seat stop geometry impossible: frame bottom cannot reach x=32 from x=16 with current Z offsets."
        );
        assert(
            seat_top_z_pos >= seat_contact_z_required && seat_top_z_neg >= seat_contact_z_required,
            str(
                "Seat top too low for x=+/-32 stop. Need >= ",
                seat_contact_z_required,
                " mm, got +=",
                seat_top_z_pos,
                " / -=",
                seat_top_z_neg,
                " mm."
            )
        );

        echo(str("Frame floor clearance (mm): ", floor_clearance_mm));
        echo(str("Seat contact angle at x=32 (deg): ", seat_contact_angle_deg));
        echo(str("Required seat-top Z for x=32 hit (model mm): ", seat_contact_z_required));

        gcsc_end_floor_fill(32, p_length_mm / 2 - s_end_cap_mm * 0.3, seat_top_z_pos);
        gcsc_end_floor_fill(-32, -p_length_mm / 2 + s_end_cap_mm * 0.3, seat_top_z_neg);
    }
}

// Decorative center stop at x = 0 that also limits frame sweep.
module gcsc_anchor_stop_feature() {
    if (f_anchor_on) {
        // Canonical Danforth anchor placement from inheritable dimensions:
        // keep X centered and raise by +14 mm to compensate anchor internal drop.
        anchor_floor_z = gcsc_inner_floor_z_at_x(0);
        anchor_z =
            anchor_floor_z
            + f_anchor_source_vertical_shift_mm
            + f_anchor_internal_offset_comp_mm
            - f_anchor_embed_mm
            - f_anchor_drop_mm;

        translate([0, 0, anchor_z])
            rotate([0, 0, f_anchor_rotation_z_deg])
                gcsc_reference_anchor();
    }
}

// Localized sidewall thickening in the slot zone without creating interior columns.
module gcsc_slot_wall_reinforcement_feature() {
    if (f_slot_wall_reinforcement_on) {
        slot_seat_z = gcsc_reference_slot_seat_z();
        slot_entry_z = gcsc_reference_slot_entry_z();
        z_low = slot_seat_z - REFERENCE_SLOT_DIAMETER / 2 - f_slot_wall_reinf_z_pad_mm;
        z_high = slot_entry_z + f_slot_entry_relief_mm + f_slot_wall_reinf_z_pad_mm;
        z_span = max(z_high - z_low, 0.6);

        for (x_sign = [-1, 1]) {
            for (y_sign = [-1, 1]) {
                intersection() {
                    translate([
                        x_sign * REFERENCE_FRAME_SPACING,
                        y_sign * (REFERENCE_PIVOT_Y + f_slot_wall_reinf_center_offset_mm),
                        (z_low + z_high) / 2
                    ])
                        cube([f_slot_wall_reinf_x_span_mm, f_slot_wall_reinf_band_mm, z_span], center = true);
                    gcsc_outer_hull();
                }
            }
        }
    }
}

// Deprecated by explicit user request (no columns in slot zone).
module gcsc_pivot_interface_columns_feature() {}

module gcsc_slot_vertical_clip(z_min, z_max) {
    translate([-20, -20, z_min])
        cube([40, 40, z_max - z_min], center = false);
}

// True vertical 7 mm slot with concave seat terminus.
module gcsc_reference_single_pivot_slot_cut(y_sign = 1) {
    slot_seat_z = gcsc_reference_slot_seat_z();
    slot_entry_z = gcsc_reference_slot_entry_z();
    slot_depth_to_seat_center = max(slot_entry_z - slot_seat_z, 0.1);
    seat_radius_mm = REFERENCE_SLOT_DIAMETER / 2;
    seat_clip_r_mm = seat_radius_mm + 0.3;
    seat_clip_z = slot_seat_z - seat_radius_mm - 0.05;
    seat_clip_h = seat_radius_mm + 0.05;
    slot_z_min = seat_clip_z;
    slot_z_max = slot_entry_z + f_slot_entry_overcut_mm + f_slot_entry_relief_mm;
    slot_axis_y = -y_sign * f_slot_interior_bias_mm;

    assert(
        abs(slot_depth_to_seat_center - 7.0) <= 0.01,
        str("Slot depth drifted from 7 mm target: ", slot_depth_to_seat_center)
    );

    intersection() {
        union() {
            // Top-entry vertical shaft.
            translate([0, slot_axis_y, slot_seat_z])
                cylinder(
                    h = slot_depth_to_seat_center + f_slot_entry_overcut_mm + f_slot_entry_relief_mm,
                    d = REFERENCE_SLOT_DIAMETER,
                    $fn = 56
                );

            // Concave hemispherical seat terminus on the same vertical axis.
            intersection() {
                translate([0, slot_axis_y, slot_seat_z])
                    sphere(d = REFERENCE_SLOT_DIAMETER, $fn = 56);
                translate([-seat_clip_r_mm, slot_axis_y - seat_clip_r_mm, seat_clip_z])
                    cube([2 * seat_clip_r_mm, 2 * seat_clip_r_mm, seat_clip_h], center = false);
            }
        }
        gcsc_slot_vertical_clip(slot_z_min, slot_z_max);
    }
}

module gcsc_reference_slot_interface_cuts() {
    if (f_enable_reference_interface) {
        gcsc_reference_guardrails();
        for (x_sign = [-1, 1]) {
            for (y_sign = [-1, 1]) {
                translate([x_sign * REFERENCE_FRAME_SPACING, y_sign * REFERENCE_PIVOT_Y, 0])
                    gcsc_reference_single_pivot_slot_cut(y_sign);
            }
        }
    }
}

// Recesses are cut directly into thick flat floor (not a separate skid base).
module gcsc_foot_recess_cutouts() {
    if (f_feet_on) {
        floor_bottom_z = gcsc_outer_floor_z_at_x(0);
        assert(
            p_floor_mm >= f_foot_recess_depth_mm + f_foot_recess_skin_mm,
            "floor_mm too thin for requested foot recess depth + skin."
        );
        for (x_sign = [-1, 1]) {
            for (y_sign = [-1, 1]) {
                translate([x_sign * f_foot_x_offset_mm, y_sign * f_foot_y_offset_mm, floor_bottom_z - 0.05])
                    cylinder(h = f_foot_recess_depth_mm + 0.10, d = f_foot_diameter_mm, $fn = 44);
            }
        }
    }
}

// Deprecated by user directive; floor is now intrinsically flat.
module gcsc_base_flat_feature() {}

module gcsc_keel_feature() {
    if (f_enable_keel) {
        hull() {
            gcsc_move([-p_length_mm * 0.36, 0, f_keel_center_z])
                gcsc_xrot(90)
                    cylinder(h = f_keel_width_mm, r = f_keel_radius_mm, center = true, $fn = 44);
            gcsc_move([p_length_mm * 0.36, 0, f_keel_center_z])
                gcsc_xrot(90)
                    cylinder(h = f_keel_width_mm, r = f_keel_radius_mm, center = true, $fn = 44);
        }
    }
}

module gcsc_rim_reinforcement_feature() {
    if (f_enable_rim_reinforcement) {
        difference() {
            gcsc_shell_band(-p_rim_height_mm - f_feature_overlap_mm, -0.02, -f_feature_overlap_mm * 0.2);
            gcsc_shell_band(-p_rim_height_mm - 0.1, 0.25, max(p_wall_mm * 0.75, 0.8));
        }
    }
}

module gcsc_drainage_hole_cut() {
    if (f_enable_drainage_hole) {
        gcsc_move([0, 0, -p_depth_mm + max(p_wall_mm * 0.6, 0.85)])
            gcsc_xrot(90)
                cylinder(h = p_beam_mm * 1.6, r = f_drainage_hole_diameter_mm / 2, center = true, $fn = 42);
    }
}
