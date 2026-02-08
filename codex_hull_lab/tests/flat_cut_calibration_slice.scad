// 20 mm center slice for flat-cut bed-contact calibration.

include <../presets/gcsc_default.scad>
include <../src/gcsc_hull_core.scad>

slice_width_mm = 20;

intersection() {
    gcsc_hull_build();
    translate([
        -slice_width_mm / 2,
        -(beam_mm + 40),
        -(depth_mm + keel_depth_mm + 60)
    ])
        cube([
            slice_width_mm,
            2 * (beam_mm + 40),
            depth_mm + keel_depth_mm + 120
        ], center = false);
}
