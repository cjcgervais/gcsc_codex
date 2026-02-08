// Fast-print style overlay on mechanics-locked baseline.

include <gcsc_mechanics_locked.scad>

curvature_bow = 0.50;
curvature_stern = 0.48;
belly_fullness = 0.35;
midship_plateau_half_fraction = 0.30;
midship_taper_exponent = 1.30;
midship_plateau_blend = 1.0;
midship_plateau_end_blend = 0.72;
rocker = 0.30;
bottom_flat_ratio = 0.66;
top_half_ratio = 0.98;
gunwale_rise_mm = 4.0;
gunwale_curve_exp = 1.9;
keel_end_lift_mm = 2.0;
keel_end_lift_exp = 1.8;
wall_end_taper_ratio = 0.70;
wall_end_taper_exp = 1.5;
station_count = 11;
no_bulge_on = true;

$fn = 38;
