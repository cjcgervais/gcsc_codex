// GCSC2 Danforth Anchor v1.2 - Standalone Decorative Component
//
// This file is intentionally STANDALONE and does NOT include dimensions.scad.
// Reason: This is a decorative miniature anchor with its own aesthetic proportions.
// It has no geometric relationship to hull/frame dimensions - it's purely ornamental.
// The anchor dimensions are chosen for visual appeal, not functional integration.
//
// Governance: Exempt from parameter consistency checks per Article 0.6 note:
// "Standalone decorative components may define their own parameters."

// --- Global Settings ---
$fn = 50;

// --- Dimensions & Parameters ---

// Shank (Central vertical shaft) dimensions
shank_len = 25;
shank_width = 2.5;
shank_thick = 1.5;

// U-Ring (rope attachment at top of shank)
ring_tube_r = 0.9;
ring_leg_len = 5;
bolt_diam = 1.8;
bolt_len = shank_width + 4;

// Fluke (triangular flat blades) - 15% smaller
fluke_len = 15.3;
fluke_base_w = 11.9;
fluke_thick = 0.8;
fluke_extra_spacing = 0.5; // extra gap per side (1mm total)

// Crown (Pivot bar) dimensions
crown_diam = 3.0;
crown_width = shank_width + (fluke_thick * 2) + 1.0;

// How far the shank/crown drops into the fluke triangles
shank_drop = fluke_len * 0.35;

// --- Modules ---

module shank() {
    difference() {
        hull() {
            translate([0, 0, shank_len - shank_width/2])
                rotate([0, 90, 0])
                cylinder(h=shank_thick, d=shank_width, center=true);
            translate([0, 0, shank_width/2])
                rotate([0, 90, 0])
                cylinder(h=shank_thick, d=shank_width, center=true);
        }
        // Bottom hole for crown pivot
        translate([0, 0, shank_width/2])
            rotate([0, 90, 0])
            cylinder(h=shank_thick+2, d=crown_diam/2 + 0.2, center=true);
    }
}

module u_ring() {
    leg_sp = shank_width/2 + ring_tube_r;

    // Crossbar bolt
    rotate([90, 0, 0])
    cylinder(h=bolt_len, d=bolt_diam, center=true);

    // Left leg
    translate([0, -leg_sp, 0])
    cylinder(h=ring_leg_len, r=ring_tube_r);

    // Right leg
    translate([0, leg_sp, 0])
    cylinder(h=ring_leg_len, r=ring_tube_r);

    // Semicircular arch connecting leg tops
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

module single_fluke_2d() {
    polygon(points=[
        [-fluke_base_w/2, 0],
        [fluke_base_w/2, 0],
        [0, fluke_len]
    ]);
}

module fluke_assembly() {
    // Crown pivot bar
    rotate([0, 90, 0])
    cylinder(h=crown_width, d=crown_diam, center=true);

    fluke_offset_y = shank_thick/2 + fluke_thick/2 + fluke_extra_spacing;

    // Right Fluke
    translate([0, fluke_offset_y, 0])
    rotate([90, 0, 0])
    rotate([0, 0, 0])
    translate([0, -fluke_len, 0])
    linear_extrude(height=fluke_thick, center=true)
    single_fluke_2d();

    // Left Fluke
    translate([0, -fluke_offset_y, 0])
    rotate([90, 0, 0])
    translate([0, -fluke_len, 0])
    linear_extrude(height=fluke_thick, center=true)
    single_fluke_2d();
}

module assembled_anchor() {
    drop = fluke_len - shank_width/2;
    extra_drop = 14; // lower shank/cylinder/u-ring 14mm below triangle tips

    fluke_offset_y = shank_thick/2 + fluke_thick/2 + fluke_extra_spacing;
    fluke_z = -drop + shank_width/2; // original fluke/crown Z position

    // 1. Shank — lowered
    translate([0, 0, -drop - extra_drop])
    shank();

    // 2. Crown cylinder — lowered with shank
    translate([0, 0, fluke_z - extra_drop])
    rotate([0, 90, 0])
    cylinder(h=crown_width, d=crown_diam, center=true);

    // 3. U-ring — lowered with shank
    translate([0, 0, -drop - extra_drop + shank_len - shank_width/2])
    translate([0, 0, -1])
    rotate([0, 0, 90])
    u_ring();

    // 4. Fluke triangles — stay at original position
    translate([0, fluke_offset_y, fluke_z])
    rotate([90, 0, 0])
    translate([0, -fluke_len, 0])
    linear_extrude(height=fluke_thick, center=true)
    single_fluke_2d();

    translate([0, -fluke_offset_y, fluke_z])
    rotate([90, 0, 0])
    translate([0, -fluke_len, 0])
    linear_extrude(height=fluke_thick, center=true)
    single_fluke_2d();
}

// --- Final Positioning ---
vertical_shift = -(shank_width/2 - fluke_len);

// Top of ring
leg_sp_calc = shank_width/2 + ring_tube_r;
ring_top_z = (shank_len - shank_width/2) + ring_leg_len + leg_sp_calc + ring_tube_r;

union() {
    translate([0, 0, vertical_shift])
    assembled_anchor();
}

final_height = ring_top_z + vertical_shift;
echo(str("Total Anchor Height: ", final_height, "mm"));
