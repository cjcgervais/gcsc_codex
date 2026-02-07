// Shell generation and geometry cut helpers.
// Method: section stations + hull() between adjacent stations.

include <gcsc_hull_profiles.scad>
include <gcsc_hull_bosl2_adapter.scad>

s_enable_flat_cut = gcsc_safe(enable_flat_cut, true);
s_enable_open_top_cut = gcsc_safe(enable_open_top_cut, false);
s_flat_cut_z = gcsc_safe(flat_cut_z, -(p_depth_mm + p_keel_depth_mm) + 0.7);
s_station_slice_mm = max(p_length_mm / (p_station_count * 14), 0.45);
s_inner_cavity_z_shift_mm = p_floor_mm;
s_end_cap_mm = max(gcsc_safe(end_cap_mm, p_wall_mm), p_wall_mm);
s_cap_tip_inset_mm = max(gcsc_safe(cap_tip_inset_mm, max(p_wall_mm * 0.95, 1.8)), 0.4);
s_cap_tip_rise_mm = gcsc_safe(cap_tip_rise_mm, p_rim_height_mm * 0.20);

function s_t_from_x(x) =
    gcsc_clamp01(x / p_length_mm + 0.5);

module gcsc_station_slice(t, inset_mm = 0) {
    beam_here = max(gcsc_beam_at(t) - 2 * inset_mm, 1.2);
    sheer_here = gcsc_gunwale_sheer_at(t);
    depth_here = max(gcsc_depth_at(t) - inset_mm + sheer_here, 1.2);
    top_ratio_here = gcsc_top_half_ratio_at_t(t);
    x_here = gcsc_station_x(t);
    keel_lift = gcsc_keel_lift_at(t);
    section_pts = gcsc_section_points(beam_here / 2, depth_here, top_ratio_here);

    gcsc_move([x_here, 0, keel_lift + sheer_here])
        gcsc_zrot(90)
            gcsc_xrot(90)
                linear_extrude(height = s_station_slice_mm, center = true, convexity = 12)
                    polygon(points = section_pts);
}

module gcsc_loft_solid(inset_mm = 0) {
    for (i = [0:p_station_count - 1]) {
        t0 = gcsc_station_t(i, p_station_count);
        t1 = gcsc_station_t(i + 1, p_station_count);
        hull() {
            gcsc_station_slice(t0, inset_mm);
            gcsc_station_slice(t1, inset_mm);
        }
    }
}

module gcsc_inner_cavity_loft_solid() {
    for (i = [0:p_station_count - 1]) {
        t0 = gcsc_station_t(i, p_station_count);
        t1 = gcsc_station_t(i + 1, p_station_count);
        hull() {
            gcsc_station_slice(t0, gcsc_wall_inset_at_t(t0));
            gcsc_station_slice(t1, gcsc_wall_inset_at_t(t1));
        }
    }
}

module gcsc_outer_hull() {
    union() {
        gcsc_loft_solid(0);
        gcsc_bow_cap();
        gcsc_stern_cap();
    }
}

module gcsc_inner_cavity_scaled() {
    inner_span_mm = max(p_length_mm - 2 * s_end_cap_mm, p_length_mm * 0.2);

    intersection() {
        translate([0, 0, s_inner_cavity_z_shift_mm])
            gcsc_inner_cavity_loft_solid();

        translate([-inner_span_mm / 2, -2 * p_beam_mm, -3 * p_depth_mm])
            cube([inner_span_mm, 4 * p_beam_mm, 6 * p_depth_mm], center = false);
    }
}

module gcsc_hull_shell() {
    difference() {
        gcsc_outer_hull();
        gcsc_inner_cavity_scaled();
    }
}

// Backward-compatible aliases.
module gcsc_outer_shell() {
    gcsc_outer_hull();
}

module gcsc_inner_shell() {
    gcsc_inner_cavity_scaled();
}

module gcsc_open_top_cut() {
    if (s_enable_open_top_cut) {
        translate([-p_length_mm, -p_beam_mm, 0])
            cube([2 * p_length_mm, 2 * p_beam_mm, p_depth_mm + p_keel_depth_mm + 120], center = false);
    }
}

module gcsc_flat_base_cut() {
    if (s_enable_flat_cut) {
        translate([-p_length_mm, -p_beam_mm, -500])
            cube([2 * p_length_mm, 2 * p_beam_mm, 500 + s_flat_cut_z], center = false);
    }
}

module gcsc_shell_band(z_low, z_high, inset_mm = 0) {
    intersection() {
        gcsc_loft_solid(inset_mm);
        translate([-p_length_mm, -p_beam_mm, z_low])
            cube([2 * p_length_mm, 2 * p_beam_mm, z_high - z_low], center = false);
    }
}

module gcsc_x_band(x_low, x_high, inset_mm = 0) {
    intersection() {
        gcsc_loft_solid(inset_mm);
        translate([x_low, -p_beam_mm, -2 * p_depth_mm])
            cube([x_high - x_low, 2 * p_beam_mm, 4 * p_depth_mm], center = false);
    }
}

module gcsc_bow_cap() {
    x_inner = p_length_mm / 2 - s_end_cap_mm;
    x_outer = p_length_mm / 2;
    t_inner = s_t_from_x(x_inner);
    t_outer = s_t_from_x(x_outer);

    hull() {
        gcsc_station_slice(t_inner, 0);
        translate([0, 0, s_cap_tip_rise_mm])
            gcsc_station_slice(t_outer, s_cap_tip_inset_mm);
    }
}

module gcsc_stern_cap() {
    x_outer = -p_length_mm / 2;
    x_inner = -p_length_mm / 2 + s_end_cap_mm;
    t_outer = s_t_from_x(x_outer);
    t_inner = s_t_from_x(x_inner);

    hull() {
        gcsc_station_slice(t_inner, 0);
        translate([0, 0, s_cap_tip_rise_mm])
            gcsc_station_slice(t_outer, s_cap_tip_inset_mm);
    }
}
