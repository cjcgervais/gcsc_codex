// Default style overlay on top of mechanics-locked baseline.

include <gcsc_mechanics_locked.scad>

curvature_bow = 0.58;        // 0..1
curvature_stern = 0.52;      // 0..1
belly_fullness = 0.40;
midship_plateau_half_fraction = 0.30;
midship_taper_exponent = 1.30;
midship_plateau_blend = 1.0;
midship_plateau_end_blend = 0.72;
rocker = 0.0;                // flat-bottom mode ignores rocker
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
station_count = 15;
no_bulge_on = true;

$fn = 56;
