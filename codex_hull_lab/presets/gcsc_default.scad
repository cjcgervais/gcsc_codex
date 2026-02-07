// Default preset (A1 Mini safe envelope).

length_mm = 148;
beam_mm = 79.5;
depth_mm = 50;
draft_mm = 20;
wall_mm = 9.0;               // Streamlined thick wall
floor_mm = 10.0;             // Keep floor robust relative to thicker shell
rim_height_mm = 2.2;
keel_depth_mm = 2.0;

curvature_bow = 0.58;        // 0..1
curvature_stern = 0.52;      // 0..1
belly_fullness = 0.40;       // no_bulge_on controls true no-bulge profile
midship_plateau_half_fraction = 0.30;
midship_taper_exponent = 1.30;
rocker = 0.0;                // flat-bottom mode ignores rocker
flat_bottom_on = true;
bottom_flat_ratio = 0.69;    // 50% wider base footprint from centerline
top_half_ratio = 0.98;
gunwale_rise_mm = 6.0;
gunwale_curve_exp = 1.6;
gunwale_end_start = 0.44;
gunwale_tip_merge_start = 0.50;
gunwale_tip_merge_exp = 1.70;
gunwale_tip_merge_ratio = 0.76;
keel_end_lift_mm = 4.8;
keel_end_lift_exp = 1.6;
keel_end_start = 0.44;
wall_end_taper_ratio = 0.62;
wall_end_taper_exp = 1.2;
wall_taper_end_start = 0.50;
tip_depth_start = 0.55;
tip_depth_exp = 2.0;
tip_depth_min_fraction = 0.04;
end_tip_start = 0.60;
end_tip_sharpness = 1.8;
end_tip_min_envelope = 0.045;
cap_tip_inset_mm = 1.4;
cap_tip_rise_mm = 0.6;
station_count = 15;          // 9..17 practical range
no_bulge_on = true;

enable_inner_cavity = true;
enable_rim_reinforcement = false;
enable_keel = false;
enable_drainage_hole = false;
enable_reference_interface = true;
enable_open_top_cut = false;
pivot_columns_on = false;    // Disable large internal cylinders; slots remain negative cutouts

seat_on = true;
seat_length_mm = 12;
seat_height_mm = 18;
seat_target_z = -8.0;

anchor_on = true;
anchor_length_mm = 12;
anchor_width_mm = 20;
anchor_height_mm = 8;

feet_on = true;
foot_diameter_mm = 8.0;
foot_recess_depth_mm = 1.0;
foot_edge_margin_mm = 10;
foot_span_fraction = 0.44;
foot_lateral_offset_mm = 14;
foot_recess_skin_mm = 1.2;

enable_flat_cut = true;
flat_cut_z = -50.0;

keel_width_mm = 5.5;
drainage_hole_diameter_mm = 3.0;
interface_margin_mm = 0.6;
frame_floor_margin_mm = 2.0;
slot_skin_mm = 1.2;
slot_column_diameter_mm = 12.0;
end_cap_mm = 10.0;
slot_entry_overcut_mm = 0.0;
slot_interior_bias_mm = 0.0;
slot_outer_skin_min_mm = 1.0;
slot_entry_relief_mm = 1.2;
min_frame_floor_clearance_mm = 11.0;
slot_wall_reinforcement_on = true;
slot_wall_reinf_x_span_mm = 20.0;
slot_wall_reinf_band_mm = 3.6;
slot_wall_reinf_center_offset_mm = 0.6;
slot_wall_reinf_z_pad_mm = 2.2;

$fn = 56;
