// Experimental style overlay on mechanics-locked baseline.
// Use for non-canonical profile exploration.

include <gcsc_mechanics_locked.scad>

curvature_bow = 0.78;
curvature_stern = 0.35;
belly_fullness = 0.42;
midship_plateau_half_fraction = 0.32;
midship_taper_exponent = 1.35;
midship_plateau_blend = 1.0;
midship_plateau_end_blend = 0.72;
rocker = 0.60;
bottom_flat_ratio = 0.69;
top_half_ratio = 0.98;
gunwale_rise_mm = 5.8;
gunwale_curve_exp = 1.9;
keel_end_lift_mm = 2.8;
keel_end_lift_exp = 1.9;
wall_end_taper_ratio = 0.70;
wall_end_taper_exp = 1.7;
station_count = 17;
no_bulge_on = true;

$fn = 72;
