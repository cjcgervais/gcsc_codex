// Parameter sweep scene for quick visual regression checks.

include <../presets/gcsc_default.scad>
include <../src/gcsc_hull_core.scad>

translate([-190, 0, 0])
    let(beam_mm = 60, depth_mm = 18, station_count = 9, $fn = 28)
        gcsc_hull_build();

translate([0, 0, 0])
    let(beam_mm = 64, depth_mm = 20, station_count = 13, $fn = 32)
        gcsc_hull_build();

translate([190, 0, 0])
    let(beam_mm = 68, depth_mm = 22, station_count = 17, $fn = 36)
        gcsc_hull_build();
