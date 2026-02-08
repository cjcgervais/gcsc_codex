// GCSC2 v6.0 - Phase 1 Minimalist Frame Module
// Inverse trapezoid frame with ball pivots for hull slots
//
// Design Philosophy: Simple inverse trapezoid demonstrating gimbal mechanism
// Two frames (forward/aft) each with top rails where soap rests

include <../params/dimensions.scad>

// ============ PIVOT BALL MODULE ============

module pivot_ball() {
    // Ball that fits into hull slot with clearance
    sphere(d=ball_diameter - tolerance, $fn=32);
}

// ============ TOP RAIL MODULE ============

module top_rail() {
    // Top rail runs PORT-TO-STARBOARD (Y-axis direction)
    // Soap rests on top surface, edges provide gripping bite
    // Rectangular cross-section: rail_thickness × rail_vertical_height

    // Rail bar oriented along Y-axis
    translate([0, 0, 0])
        rotate([0, 90, 0])  // Orient along Y-axis
            cube([rail_thickness, rail_span_y, rail_vertical_height], center=true);
}

// ============ BOTTOM RAIL MODULE ============

module bottom_rail() {
    // Bottom rail (narrower for inverse trapezoid)
    // Also runs Y-axis but shorter span

    translate([0, 0, 0])
        rotate([0, 90, 0])  // Orient along Y-axis
            cube([rail_thickness, bottom_rail_span_y, rail_vertical_height], center=true);
}

// ============ SIDE MEMBER MODULE ============

module side_member(side) {
    // Rectangular bar connecting top rail end to bottom rail end
    // Creates inverse trapezoid (wider at top, narrower at bottom)
    // side: -1 for port, +1 for starboard

    top_y = side * (rail_span_y / 2);           // End of top rail
    bottom_y = side * (bottom_rail_span_y / 2); // End of bottom rail

    // Calculate length and angle for rectangular bar
    height_diff = frame_height;
    width_diff = abs(top_y - bottom_y);
    member_length = sqrt(height_diff * height_diff + width_diff * width_diff);
    angle = atan2(width_diff, height_diff);

    // Position and rotate rectangular bar
    translate([0, (top_y + bottom_y)/2, 0])
        rotate([0, side * angle, 0])
            cube([side_member_thickness, side_member_thickness, member_length], center=true);
}

// ============ BALL EXTENSION ARM ============

module ball_with_arm(side) {
    // Short arm extending from side member to ball at pivot position
    // Ball sits at slot_y_position to align with hull slots
    // side: -1 for port, +1 for starboard

    side_member_y = side * (rail_span_y / 2);  // Where side member is
    ball_y = side * slot_y_position;            // Where ball needs to be

    // Rectangular arm extending from side member to ball position
    hull() {
        // Connection at side member location
        translate([0, side_member_y, 0])
            sphere(d=side_member_thickness, $fn=32);

        // Connection at ball position
        translate([0, ball_y, 0])
            sphere(d=side_member_thickness, $fn=32);
    }

    // Pivot ball at correct position aligned with hull slot
    translate([0, ball_y, 0])
        pivot_ball();
}

// ============ SINGLE FRAME MODULE ============

module single_frame() {
    // One inverse trapezoid frame
    // Top wider (where soap rests), bottom narrower (self-righting)
    // Positioned so pivot balls are at Z=0 (will be translated to z_pivot_seat)

    // Top rail (where soap rests)
    translate([0, 0, frame_height/2])
        top_rail();

    // Bottom rail (narrower)
    translate([0, 0, -frame_height/2])
        bottom_rail();

    // Port side member
    side_member(-1);

    // Starboard side member
    side_member(1);

    // Ball extensions at pivot height (Z=0 in this frame, will be at z_pivot_seat when assembled)
    ball_with_arm(-1);  // Port ball
    ball_with_arm(1);   // Starboard ball
}

// ============ COMPLETE FRAME ASSEMBLY ============

module frame_complete() {
    // Two frames positioned at forward and aft locations
    // Entire assembly positioned so balls are at z_pivot_seat height

    translate([0, 0, z_pivot_seat]) {
        // Forward frame
        translate([frame_x_offset, 0, 0])
            single_frame();

        // Aft frame
        translate([-frame_x_offset, 0, 0])
            single_frame();
    }
}

// ============ RENDER ============

// Render frame_complete for both preview and export
frame_complete();

// Show coordinate axes in preview only
if ($preview) {
    %translate([0, 0, 0]) {
        color("red") cylinder(d=1, h=LOA, center=true);
        rotate([0, 90, 0]) color("green") cylinder(d=1, h=beam, center=true);
        rotate([90, 0, 0]) color("blue") cylinder(d=1, h=freeboard*2, center=true);
    }
}
