// Complete Assembly - Hull + Two Frames
// For physical verification of frame-hull fit

use <modules/hull_simple.scad>
include <params/dimensions.scad>

// Import CF_Frame v5.3 inline (uses params from dimensions.scad)
module cf_frame_v53() {
    // Use canonical values from dimensions.scad (Article 0.6 frozen params)
    z_pivot_seat_frame = z_pivot_seat;       // 38mm from dimensions.scad
    ball_diameter_frame = ball_diameter;     // 7.25mm from dimensions.scad
    ball_y_position_frame = slot_y_position; // 31mm from dimensions.scad

    // Frame-specific geometry (derived, not frozen)
    top_member_z_bot = z_pivot_seat + 1;     // 39mm - just above pivot
    top_member_z_top = freeboard;            // 45mm - at freeboard
    top_member_height = top_member_z_top - top_member_z_bot;  // 6mm
    top_rail_main_span = 48;

    bottom_member_z_bot = 17;
    bottom_member_height = 18;
    bottom_rail_span = 36;

    rail_width = 3;

    // Top rail
    translate([0, 0, top_member_z_bot + top_member_height/2])
        cube([rail_width, top_rail_main_span, top_member_height], center=true);

    // Bottom rail
    translate([0, 0, bottom_member_z_bot + bottom_member_height/2])
        cube([rail_width, bottom_rail_span, bottom_member_height], center=true);

    // Side members
    for (y_sign = [-1, 1]) {
        hull() {
            translate([0, y_sign * (bottom_rail_span/2), bottom_member_z_bot + bottom_member_height])
                cube([3, 3, 0.1], center=true);
            translate([0, y_sign * (top_rail_main_span/2), top_member_z_bot])
                cube([3, 3, 0.1], center=true);
        }
    }

    // Ball pivots
    for (y_sign = [-1, 1]) {
        translate([0, y_sign * ball_y_position_frame, z_pivot_seat_frame])
            sphere(d=ball_diameter_frame, $fn=32);

        // Extender arms
        hull() {
            translate([0, y_sign * (top_rail_main_span/2), z_pivot_seat_frame])
                sphere(d=2.7, $fn=32);
            translate([0, y_sign * ball_y_position_frame, z_pivot_seat_frame])
                sphere(d=ball_diameter_frame * 0.7, $fn=32);
        }
    }
}

// Hull
hull_complete();

// Forward frame
translate([frame_x_offset, 0, 0])
    cf_frame_v53();

// Aft frame
translate([-frame_x_offset, 0, 0])
    cf_frame_v53();
