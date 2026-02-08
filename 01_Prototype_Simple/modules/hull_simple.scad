// GCSC2 v6.0 - Phase 1 Beautiful Hull Module
// Aesthetic Design: Naval architecture principles applied
// - Asymmetric sheer (bow 1.9x higher than stern)
// - Progressive section variation (fine entry, full midship)
// - Expressed tumblehome at gunwale
// - Visual flow through 9-station control points

include <../params/dimensions.scad>

// ============ AESTHETIC PARAMETERS ============
// These create the canoe's "personality" within frozen constraints

// Sheer asymmetry: bow rises higher than stern (authentic canoe proportion)
bow_sheer_rise = 15;           // Forward sheer elevation (mm above freeboard)
stern_sheer_rise = 8;          // Aft sheer elevation (mm above freeboard)
// Ratio: 15/8 = 1.875:1 (within 1.5-2.0 authentic range)

// Section progression: finer at ends, fuller in middle
bow_section_d = 6;             // Bow entry sphere diameter (fine, knife-like)
bow_quarter_d = 7;             // Forward quarter sphere diameter
midship_d = 10;                // Midship sphere diameter (fullest)
stern_quarter_d = 8;           // Aft quarter sphere diameter
stern_section_d = 7;           // Stern exit sphere diameter (intermediate)

// Tumblehome expression at sheer (gunwale narrower than max beam)
sheer_beam_factor = 0.92;      // Sheer beam = 92% of maximum beam (tumblehome effect)

// Station positions along hull length (x-axis)
bow_tip_x = half_LOA;                    // Bow point
bow_quarter_x = half_LOA * 0.55;         // Forward quarter station
forward_mid_x = 35;                      // Forward midship station
aft_mid_x = -35;                         // Aft midship station
stern_quarter_x = -half_LOA * 0.55;      // Aft quarter station
stern_tip_x = -half_LOA;                 // Stern point

// Keel depth variation (creates V-hull character)
keel_center_drop = 2;          // Center keel lowered for V-profile (mm)

// ============ HULL OUTER MODULE ============
// 9-station hull construction with aesthetic curves

module hull_outer() {
    hull() {
        // === STATION 1: BOW TIP ===
        // Fine entry point with elevated sheer
        translate([bow_tip_x, 0, freeboard + bow_sheer_rise])
            sphere(d=bow_section_d, $fn=32);
        // Bow keel point (slightly raised for entry angle)
        translate([bow_tip_x - 6, 0, 2])
            sphere(d=4, $fn=32);

        // === STATION 2: BOW QUARTER (X = +55% of half_LOA) ===
        // Transitioning from fine entry to fuller sections
        for (y = [-half_beam * 0.6, half_beam * 0.6]) {
            // Sheer points with tumblehome (narrower at top)
            translate([bow_quarter_x, y * sheer_beam_factor, freeboard + bow_sheer_rise * 0.7])
                sphere(d=bow_quarter_d, $fn=32);
            // Keel points
            translate([bow_quarter_x, y * 0.4, -keel_center_drop * 0.5])
                sphere(d=5, $fn=32);
        }
        // Center keel spine at bow quarter (V-hull expression)
        translate([bow_quarter_x, 0, -keel_center_drop])
            sphere(d=3, $fn=32);

        // === STATION 3: FORWARD MIDSHIP ===
        // Full beam developing, maximum section area approaching
        for (y = [-half_beam, half_beam]) {
            // Sheer points with tumblehome
            translate([forward_mid_x, y * sheer_beam_factor, freeboard])
                sphere(d=midship_d, $fn=32);
            // Maximum beam points (lower, at z_max_beam)
            translate([forward_mid_x, y, z_max_beam])
                sphere(d=midship_d, $fn=32);
            // Bilge points (transition to keel)
            translate([forward_mid_x, y * 0.5, 0])
                sphere(d=6, $fn=32);
        }
        // Center keel spine (V-hull)
        translate([forward_mid_x, 0, -keel_center_drop])
            sphere(d=4, $fn=32);

        // === STATION 4: TRUE MIDSHIP (X = 0) ===
        // Maximum fullness - the "belly" of the canoe
        for (y = [-half_beam, half_beam]) {
            // Sheer points with tumblehome
            translate([0, y * sheer_beam_factor, freeboard])
                sphere(d=midship_d, $fn=32);
            // Maximum beam points (fullest section)
            translate([0, y * 1.02, z_max_beam])  // Slightly fuller here
                sphere(d=midship_d + 1, $fn=32);
            // Bilge points
            translate([0, y * 0.5, 0])
                sphere(d=7, $fn=32);
        }
        // Center keel (deepest point)
        translate([0, 0, -keel_center_drop])
            sphere(d=5, $fn=32);

        // === STATION 5: AFT MIDSHIP ===
        // Beginning to taper toward stern
        for (y = [-half_beam, half_beam]) {
            // Sheer points with tumblehome (sheer lower than forward)
            translate([aft_mid_x, y * sheer_beam_factor, freeboard])
                sphere(d=midship_d, $fn=32);
            // Maximum beam points
            translate([aft_mid_x, y, z_max_beam])
                sphere(d=midship_d, $fn=32);
            // Bilge points
            translate([aft_mid_x, y * 0.5, 0])
                sphere(d=6, $fn=32);
        }
        // Center keel spine
        translate([aft_mid_x, 0, -keel_center_drop])
            sphere(d=4, $fn=32);

        // === STATION 6: STERN QUARTER (X = -55% of half_LOA) ===
        // Refining toward stern, but not as fine as bow
        for (y = [-half_beam * 0.65, half_beam * 0.65]) {
            // Sheer points (lower rise than bow quarter)
            translate([stern_quarter_x, y * sheer_beam_factor, freeboard + stern_sheer_rise * 0.6])
                sphere(d=stern_quarter_d, $fn=32);
            // Keel points
            translate([stern_quarter_x, y * 0.45, -keel_center_drop * 0.3])
                sphere(d=5, $fn=32);
        }
        // Center keel spine
        translate([stern_quarter_x, 0, -keel_center_drop * 0.5])
            sphere(d=3, $fn=32);

        // === STATION 7: STERN TIP ===
        // Clean exit with lower sheer than bow
        translate([stern_tip_x, 0, freeboard + stern_sheer_rise])
            sphere(d=stern_section_d, $fn=32);
        // Stern keel point
        translate([stern_tip_x + 6, 0, 1])
            sphere(d=4, $fn=32);
    }
}

module hull_inner() {
    scale_factor = (beam - 2*wall_thickness) / beam;
    z_scale_factor = (freeboard - wall_thickness) / freeboard;
    translate([0, 0, wall_thickness])
    scale([scale_factor, scale_factor, z_scale_factor])
    hull_outer();
}

module pivot_slots() {
    slot_top = freeboard + 10;
    slot_bottom = 39;
    slot_height = slot_top - slot_bottom;
    hemisphere_center_z = slot_bottom;
    hemisphere_diameter = slot_diameter;  // Match slot diameter for 0.5mm clearance

    for (side = [-1, 1]) {
        for (x_pos = [-frame_x_offset, frame_x_offset]) {
            translate([x_pos, side * slot_y_position, (slot_top + slot_bottom)/2]) {
                cylinder(d=slot_diameter, h=slot_height, center=true, $fn=32);
                slot_center_z = (slot_top + slot_bottom)/2;
                translate([0, 0, hemisphere_center_z - slot_center_z]) {
                    intersection() {
                        sphere(d=hemisphere_diameter, $fn=32);
                        translate([0, 0, -hemisphere_diameter/2])
                            cube([hemisphere_diameter*2, hemisphere_diameter*2, hemisphere_diameter], center=true);
                    }
                }
            }
        }
    }
}

module hull_complete() {
    difference() {
        hull_outer();
        hull_inner();
        translate([0, 0, freeboard + 25])
            cube([LOA * 3, beam * 3, 50], center=true);
        pivot_slots();
    }
}

if ($preview) {
    hull_complete();
    %translate([0, 0, 0]) {
        color("red") cylinder(d=1, h=LOA*1.2, center=true);
        rotate([0, 90, 0]) color("green") cylinder(d=1, h=beam*1.2, center=true);
        rotate([90, 0, 0]) color("blue") cylinder(d=1, h=freeboard*1.5, center=true);
    }
}
