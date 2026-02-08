// Stability-focused style overlay on mechanics-locked baseline.

include <gcsc_mechanics_locked.scad>

curvature_bow = 0.55;
curvature_stern = 0.55;
belly_fullness = 0.45;
midship_plateau_half_fraction = 0.32;
midship_taper_exponent = 1.35;
midship_plateau_blend = 1.0;
midship_plateau_end_blend = 0.72;
rocker = 0.28;
bottom_flat_ratio = 0.72;
top_half_ratio = 0.98;
gunwale_rise_mm = 5.5;
gunwale_curve_exp = 1.95;
keel_end_lift_mm = 2.6;
keel_end_lift_exp = 1.9;
wall_end_taper_ratio = 0.74;
wall_end_taper_exp = 1.7;
station_count = 17;
no_bulge_on = true;

$fn = 64;
