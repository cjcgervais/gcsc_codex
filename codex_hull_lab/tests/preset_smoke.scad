// Visual regression scene showing all four presets.
// Note: each preset is compiled in an isolated module scope.

module smoke_default() {
    include <../presets/gcsc_default.scad>
    include <../src/gcsc_hull_core.scad>
    gcsc_hull_build();
}

module smoke_fast_print() {
    include <../presets/gcsc_fast_print.scad>
    include <../src/gcsc_hull_core.scad>
    gcsc_hull_build();
}

module smoke_high_stability() {
    include <../presets/gcsc_high_stability.scad>
    include <../src/gcsc_hull_core.scad>
    gcsc_hull_build();
}

module smoke_experiment() {
    include <../presets/gcsc_experiment.scad>
    include <../src/gcsc_hull_core.scad>
    gcsc_hull_build();
}

translate([-260, 0, 0]) smoke_default();
translate([-85, 0, 0]) smoke_fast_print();
translate([90, 0, 0]) smoke_high_stability();
translate([265, 0, 0]) smoke_experiment();
