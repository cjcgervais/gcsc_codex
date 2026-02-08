// CF_Frame_v5.3_infill - SIDE MEMBERS IN 2MM TOTAL, UP 2MM FROM LENGTHENED
// Based on: CF_Frame_v5.2_infill.scad
//
// NEW in v5.3_infill:
//   - Side members at z=34mm (up 2mm from lengthened position)
//   - Side member offset reduced to 1mm (in 2mm total from v5.2)
//   - 5mm rise for ball extender support
//
// MAINTAINED from v5.2:
//   - Main top rail body: 52mm span (±26mm)
//   - 45-degree tapered ends from ±26mm to ±29.5mm
//   - Overall span: 59mm
//   - ball_y_position: matches hull slot_y_position (from dimensions.scad)
//   - z_pivot_seat: matches hull z_pivot_seat (from dimensions.scad)

// Import shared parameters (Article 0.6 frozen params)
include <params/dimensions.scad>

// ============ PARAMETERS ============

// Z-stack (matched to Hull v5.0, scaled -19%)
// z_pivot_seat imported from dimensions.scad (38mm)
z_clearance = 17;       // (was 21)
z_rim_base = 45;        // (was 56)

// Original bottom member dimensions (for volume calculation)
original_bottom_member_height = 16;
original_rail_width = 3;
original_bottom_rail_span = 40;
original_volume = original_rail_width * original_bottom_rail_span * original_bottom_member_height;

// ============ CANADIAN FLAG PARAMETERS (EXACT FROM SVG) ============

flag_height = original_bottom_member_height * 1.035;
flag_width = flag_height * 2;
flag_red_bar_width = flag_width * 0.25;
flag_white_center = flag_width * 0.50;

red_bar_cutout_width = flag_red_bar_width - 0.3;
red_bar_cutout_height = flag_height - 0.3;

maple_leaf_height = flag_height * 0.84;
maple_leaf_scale = maple_leaf_height / 100;

red_bar_volume = 2 * red_bar_cutout_width * red_bar_cutout_height * original_rail_width;
maple_leaf_area_factor = 0.55;
maple_leaf_width = maple_leaf_height * 0.923;
maple_leaf_volume = maple_leaf_height * maple_leaf_width * maple_leaf_area_factor * original_rail_width;
total_removed_volume = red_bar_volume + maple_leaf_volume;

// SCALED bottom member height
bottom_member_height = 18;  // Slightly increased from 16 to maintain flag visibility

// ============ FRAME DIMENSIONS - SCALED ============

bottom_member_z_bot = 17;       // (was 21, -19%)
bottom_member_z_top = bottom_member_z_bot + bottom_member_height;
bottom_member_z_center = bottom_member_z_bot + bottom_member_height/2;

top_member_z_bot = 39;          // (was 49, -20%)
top_member_z_top = 45;          // (was 56, -20%)
top_member_height = 6;          // (was 7, -14%)
top_member_z_center = 42;       // (was 52.5)

bottom_rail_span = 36;          // (was 41, -12%)
top_rail_span = 55;             // Overall span (to taper tips)
top_rail_main_span = 48;        // Main rail body span

bottom_half = bottom_rail_span / 2;
top_half = top_rail_span / 2;           // 29.5mm (taper tip)
top_half_main = top_rail_main_span / 2; // 26mm (main body)

side_member_width = 3;
side_member_depth = 3;

// Side member starting point - v5.3 adjustment
side_member_z_bot = 34.175;  // z=34.175mm - fine tuned up 0.175mm

// Side member top connection at bottom of top rail
side_member_z_top = top_member_z_bot;  // z=39mm - bottom of top rail

// ball_diameter imported from dimensions.scad (7.25mm)
// slot_y_position imported from dimensions.scad (31mm) - used as ball_y_position
ball_y_position = slot_y_position;  // Use canonical value from dimensions.scad
ball_radius = ball_diameter / 2;

rail_width = 3;
top_rail_width = 3;
cutout_depth = rail_width + 2;

$fn = 32;

// ============ MAPLE LEAF POINTS (Official from SVG) ============

maple_leaf_points = [
    [2.23, -50.0], [1.12, -28.59], [3.87, -26.15], [25.19, -29.9],
    [22.31, -21.96], [22.8, -20.15], [46.15, -1.24], [40.89, 1.22],
    [40.05, 3.18], [44.67, 17.37], [31.22, 14.52], [29.4, 15.46],
    [26.8, 21.59], [16.3, 10.32], [13.55, 11.74], [18.61, 37.84],
    [10.5, 33.15], [8.24, 33.82], [0.0, 50.0], [-8.24, 33.82],
    [-10.5, 33.15], [-18.61, 37.84], [-13.55, 11.74], [-16.3, 10.32],
    [-26.8, 21.59], [-29.4, 15.46], [-31.22, 14.52], [-44.67, 17.37],
    [-40.05, 3.18], [-40.89, 1.22], [-46.15, -1.24], [-22.8, -20.15],
    [-22.31, -21.96], [-25.19, -29.9], [-3.87, -26.15], [-1.12, -28.59],
    [-2.23, -50.0]
];

// ============ FUNCTIONS ============

function side_member_y_at(z) =
    let(t = (z - bottom_member_z_center) / (top_member_z_center - bottom_member_z_center))
    bottom_half + (top_half - bottom_half) * clamp(t, 0, 1);

function clamp(val, lo, hi) = min(hi, max(lo, val));

// ============ MODULES ============

module maple_leaf_2d() {
    scale([maple_leaf_scale, maple_leaf_scale])
        polygon(points = maple_leaf_points);
}

module maple_leaf_cutout() {
    translate([0, 0, bottom_member_z_center])
        rotate([0, 90, 0])
            rotate([0, 0, 90])
                linear_extrude(height = cutout_depth, center = true)
                    maple_leaf_2d();
}

module left_red_bar_cutout() {
    y_inner_edge = -flag_white_center/2;
    y_pos = y_inner_edge - (red_bar_cutout_width/2);
    translate([0, y_pos, bottom_member_z_center])
        cube([cutout_depth, red_bar_cutout_width, red_bar_cutout_height], center = true);
}

module right_red_bar_cutout() {
    y_inner_edge = flag_white_center/2;
    y_pos = y_inner_edge + (red_bar_cutout_width/2);
    translate([0, y_pos, bottom_member_z_center])
        cube([cutout_depth, red_bar_cutout_width, red_bar_cutout_height], center = true);
}

module bottom_rail_solid() {
    translate([0, 0, bottom_member_z_bot + bottom_member_height/2])
        cube([rail_width, bottom_rail_span, bottom_member_height], center=true);
}

module bottom_rail_canadian_flag() {
    difference() {
        bottom_rail_solid();
        maple_leaf_cutout();
        left_red_bar_cutout();
        right_red_bar_cutout();
    }
}

// Top rail with 45-degree tapered ends
module top_rail() {
    difference() {
        // Main rail body at 52mm span
        translate([0, 0, top_member_z_bot + top_member_height/2])
            cube([top_rail_width, top_rail_main_span, top_member_height], center=true);

        // Add 45-degree tapered extensions on each end
        union() {
            // End tapers (from ±26mm to ±29.5mm)
            for (y_sign = [-1, 1]) {
                translate([0, y_sign * top_half_main, top_member_z_bot + top_member_height/2]) {
                    // Create the taper using hull between main body and outer tip
                    hull() {
                        // Inner edge at main body (52mm span)
                        translate([0, 0, 0])
                            cube([top_rail_width, 0.1, top_member_height], center=true);
                        // Outer tip at 59mm span, tapered down to bottom
                        translate([0, y_sign * (top_half - top_half_main), -top_member_height/2])
                            cube([top_rail_width, 0.1, 0.1], center=true);
                    }
                }
            }
        }
    }

    // Add the 45-degree tapered extensions
    for (y_sign = [-1, 1]) {
        hull() {
            // Inner edge at main body (±26mm) - full height
            translate([0, y_sign * top_half_main, top_member_z_bot + top_member_height/2])
                cube([top_rail_width, 0.1, top_member_height], center=true);
            // Outer tip at ±29.5mm - tapered to bottom
            translate([0, y_sign * top_half, top_member_z_bot])
                cube([top_rail_width, 0.1, 0.1], center=true);
        }
    }
}

// Side member at z=34.175mm and moved to 1.5mm offset
module side_member(y_sign) {
    y_bot = y_sign * (bottom_half - side_member_depth/2 + 1.5);  // Moved out 1.5mm
    y_top = y_sign * (top_half - side_member_depth/2 + 1.5);      // Moved out 1.5mm

    hull() {
        // Bottom connection - at z=34.175mm and out 1.5mm
        translate([0, y_bot, side_member_z_bot])
            cube([side_member_width, side_member_depth, 0.1], center=true);
        // Top connection - out 1.5mm
        translate([0, y_top, side_member_z_top])
            cube([side_member_width, side_member_depth, 0.1], center=true);
    }
}

module ball_joint(y_sign) {
    translate([0, y_sign * ball_y_position, z_pivot_seat])
        sphere(d=ball_diameter);

    y_side = side_member_y_at(z_pivot_seat);
    hull() {
        translate([0, y_sign * y_side, z_pivot_seat])
            sphere(d=side_member_depth * 0.9);
        translate([0, y_sign * (ball_y_position - ball_radius * 0.3), z_pivot_seat])
            sphere(d=ball_diameter * 0.7);
    }
}

// Trapezoidal infill - CLEAN, no extra gussets
module trapezoid_infill() {
    // Main trapezoid from rail to rail
    hull() {
        // Bottom rectangle at top of flag rail
        translate([0, 0, bottom_member_z_top])
            cube([rail_width, bottom_rail_span, 0.1], center = true);
        // Top rectangle at bottom of top rail
        translate([0, 0, top_member_z_bot])
            cube([rail_width, top_rail_main_span, 0.1], center = true);
    }

    // Fill the triangular gaps on each side between trapezoid edge and side member
    for (y_sign = [-1, 1]) {
        hull() {
            // Bottom rail outer edge
            translate([0, y_sign * bottom_half, bottom_member_z_top])
                cube([rail_width, 0.1, 0.1], center = true);
            // Bottom side member inner edge - moved out 1.5mm
            translate([0, y_sign * (bottom_half - side_member_depth/2 + 1.5), side_member_z_bot])
                cube([rail_width, 0.1, 0.1], center = true);
            // Top rail main body edge
            translate([0, y_sign * top_half_main, top_member_z_bot])
                cube([rail_width, 0.1, 0.1], center = true);
            // Top side member inner edge - moved out 1.5mm
            translate([0, y_sign * (top_half - side_member_depth/2 + 1.5), side_member_z_top])
                cube([rail_width, 0.1, 0.1], center = true);
        }
    }
}

// Complete Canadian Flag frame with infill
module cf_frame_v53_infill() {
    bottom_rail_canadian_flag();
    trapezoid_infill();
    top_rail();
    for (y_sign = [-1, 1]) {
        side_member(y_sign);
        ball_joint(y_sign);
    }
}

// ============ RENDER ============

cf_frame_v53_infill();

// ============ VERIFICATION ============
echo("=== CF FRAME v5.3 INFILL - SIDE MEMBERS IN 2MM, UP 2MM ===");
echo("Bottom rail span:", bottom_rail_span, "mm");
echo("Top rail main body span:", top_rail_main_span, "mm");
echo("Ball Y position:", ball_y_position, "mm");
echo("Ball Z position:", z_pivot_seat, "mm");
echo("");
echo("Side member bottom Z:", side_member_z_bot, "mm (v5.2 was 35mm)");
echo("Side member top Z:", side_member_z_top, "mm");
echo("Side member Z rise:", side_member_z_top - side_member_z_bot, "mm (v5.2 was 4mm)");
echo("Side member Y span:", top_half - bottom_half, "mm");
echo("Side member angle:", atan((side_member_z_top - side_member_z_bot) / (top_half - bottom_half)), "degrees");
echo("Side member Y offset: 1.5mm out (in 1.5mm from v5.2)");
