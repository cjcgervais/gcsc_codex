// Hull v6 Test Print with Danforth Anchors
// Three anchors attached to hull floor for printability

use <modules/hull_simple.scad>
include <params/dimensions.scad>

// Import anchor module from GCSC_Danforth_Anchor_v1.2.scad
module assembled_anchor() {
    // Shank dimensions
    shank_len = 25;
    shank_width = 2.5;
    shank_thick = 1.5;

    // U-Ring
    ring_tube_r = 0.9;
    ring_leg_len = 5;
    bolt_diam = 1.8;
    bolt_len = shank_width + 4;

    // Fluke dimensions
    fluke_len = 15.3;
    fluke_base_w = 11.9;
    fluke_thick = 0.8;
    fluke_extra_spacing = 0.5;

    // Crown
    crown_diam = 3.0;
    crown_width = shank_width + (fluke_thick * 2) + 1.0;

    drop = fluke_len - shank_width/2;
    extra_drop = 14;

    fluke_offset_y = shank_thick/2 + fluke_thick/2 + fluke_extra_spacing;
    fluke_z = -drop + shank_width/2;

    // Shank
    translate([0, 0, -drop - extra_drop])
    difference() {
        hull() {
            translate([0, 0, shank_len - shank_width/2])
                rotate([0, 90, 0])
                cylinder(h=shank_thick, d=shank_width, center=true, $fn=50);
            translate([0, 0, shank_width/2])
                rotate([0, 90, 0])
                cylinder(h=shank_thick, d=shank_width, center=true, $fn=50);
        }
        translate([0, 0, shank_width/2])
            rotate([0, 90, 0])
            cylinder(h=shank_thick+2, d=crown_diam/2 + 0.2, center=true, $fn=50);
    }

    // Crown cylinder
    translate([0, 0, fluke_z - extra_drop])
    rotate([0, 90, 0])
    cylinder(h=crown_width, d=crown_diam, center=true, $fn=50);

    // U-ring
    translate([0, 0, -drop - extra_drop + shank_len - shank_width/2])
    translate([0, 0, -1])
    rotate([0, 0, 90]) {
        leg_sp = shank_width/2 + ring_tube_r;

        // Crossbar
        rotate([90, 0, 0])
        cylinder(h=bolt_len, d=bolt_diam, center=true, $fn=50);

        // Legs
        translate([0, -leg_sp, 0])
        cylinder(h=ring_leg_len, r=ring_tube_r, $fn=50);

        translate([0, leg_sp, 0])
        cylinder(h=ring_leg_len, r=ring_tube_r, $fn=50);

        // Arch
        arch_r = leg_sp;
        arch_center_z = ring_leg_len;
        for (a = [0 : 5 : 180]) {
            hull() {
                translate([0, -arch_r * cos(a), arch_center_z + arch_r * sin(a)])
                    sphere(r=ring_tube_r, $fn=20);
                translate([0, -arch_r * cos(a+5), arch_center_z + arch_r * sin(a+5)])
                    sphere(r=ring_tube_r, $fn=20);
            }
        }
    }

    // Flukes
    translate([0, fluke_offset_y, fluke_z])
    rotate([90, 0, 0])
    translate([0, -fluke_len, 0])
    linear_extrude(height=fluke_thick, center=true)
    polygon(points=[
        [-fluke_base_w/2, 0],
        [fluke_base_w/2, 0],
        [0, fluke_len]
    ]);

    translate([0, -fluke_offset_y, fluke_z])
    rotate([90, 0, 0])
    translate([0, -fluke_len, 0])
    linear_extrude(height=fluke_thick, center=true)
    polygon(points=[
        [-fluke_base_w/2, 0],
        [fluke_base_w/2, 0],
        [0, fluke_len]
    ]);
}

// Complete hull with anchors
module hull_with_anchors() {
    // Hull
    hull_complete();

    // Three anchors standing upright at hull floor
    // Anchor was made upside down, raise up 25mm to compensate
    anchor_z = wall_thickness - 1 + 25;  // 7 - 1 + 25 = 31mm

    for (x_pos = [-32, 0, 32]) {
        translate([x_pos, 0, anchor_z])
            assembled_anchor();
    }
}

hull_with_anchors();
