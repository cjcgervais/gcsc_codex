// GCSC Hull v5.3 - FLOOR STEP ADJUSTMENT & GEOMETRY RECONCILIATION
// Based on v5.1
//
// FIX v5.2:
//   - floor_step_x: 39mm → 32mm (symmetric 16mm frame swing gaps)
//   - This moves the floor step-up points outward for better geometry
//   - z_pivot_seat confirmed at 38mm (matches frame)
//   - slot_y_position confirmed at 33mm (matches frame)
//
// DESIGN CHANGES (from v5.0):
//   - LENGTH (X): 135mm → 148mm (+10% longer, more representative canoe)
//   - WIDTH (Y): 96mm → 84mm (-12.5% narrower)
//   - DEPTH (Z): 62mm → 50mm (-19% shorter, shallower hull)
//   - Enhanced parabolic curves for more dramatic canoe aesthetic
//   - Anchor positioned on middle floor at z=6mm
//
// HULL FORM:
// - Elliptical cross-section amidships (|X| < step_x)
// - V-taper transition beyond step change toward bow/stern
// - Pointed vertices at X = +/-X_vertex
// - ENHANCED PARABOLIC sheer profile (rim rises dramatically toward ends)
// - FLAT BOTTOM (X = +/-40mm) for stability, steep parabolic rise at bow/stern

// ============ PARAMETERS ============

// Outer envelope at rim - SCALED
outer_rim_x = 148;      // Full length (+10% from 135mm)
outer_rim_y = 84;       // Full beam (-12.5% from 96mm)
outer_semi_x = 74;      // Half-length to vertex
outer_semi_y = 42;      // Half-beam

// Wall thickness
wall_base = 10;
wall_step = 15;

// Inner dimensions at rim (Z=45) - with tumblehome
inner_semi_x = 64;      // outer_semi_x - wall_base
inner_semi_y = 32;      // outer_semi_y - wall_base

// Floor dimensions (Z=0) - narrow keel
floor_semi_x = 40;      // Scaled proportionally
floor_semi_y = 24;      // Scaled proportionally

// BULGE PROFILE - Canoe cross-section bulges AT bottom rail
z_max_beam = 17;        // Z height of maximum beam (was 21, -19%)
bulge_amount = 6.5;     // Extra width at max beam (scaled from 7.5)

// Z-stack - SCALED DOWN (-19%)
z_floor = 0;
z_clearance = 17;       // (was 21)
z_pivot_seat = 38;      // Lowered so slot ends at rim (7mm depth)
z_slot_entry = 45;      // Slot ends at outer rim level
z_rim_base = 42;        // Interior reference height - lowered 2mm from outer rim
z_rim_flat = 44;        // Rim height amidships - outer rim level
z_rim_max = 50;         // Maximum sheer at vertices (was 62)
rim_inner_drop = 0;     // Flat rim

// Hull zones
step_x = 30;            // Where ellipse transitions to V-taper (scaled)
vertex_radius = 3;      // Small radius at bow/stern for printability

// ENHANCED PARABOLIC STABILITY PROFILE
rim_fillet = 2;         // Fillet radius for rim edges
keel_rocker = 42;       // DRAMATIC rise relative to hull height (was 55)
flat_half_length = 33;  // Half-length of flat bottom (was 30mm) - 66mm total flat
sheer_smoothness = 1.3; // Y-sheer exponent (lower = more dramatic parabolic curve)
// PROFILE: Flat from X = -33 to X = +33 (66mm flat for soap stability)
// Parabolic rise over 41mm to vertices - STEEP parabolic curve
// FLOOR: Center zone (|x| <= 32mm) at z=6mm, end zones at z=31mm
// FLOOR: Center zone (|x| <= 32mm) at z=6mm, end zones at z=31mm

// Pivot geometry - RECONCILED WITH FRAME v4.3
slot_diameter = 7.5;
frame_x_offset = 16;        // Reduced by 1mm
slot_y_position = 33;       // Reduced by 1mm per side (2mm total span)

// INTERIOR FLOOR PARAMETERS - SCALED
floor_z_center = 6;         // Floor height in center zone (was 7.5, -20%)
floor_z_ends = 31;          // Floor height at ends (was 39, -20%)
floor_step_x = 32;          // X position where floor steps up (moved +6mm toward bow/stern)

// Resolution
$fn = 64;

// ============ FUNCTIONS ============

// Manual tanh implementation
function my_tanh(x) =
    let(e2x = exp(2 * x))
    (e2x - 1) / (e2x + 1);

// BULGE PROFILE for canoe cross-section
function bulge_at_z(z) =
    let(
        factor = (z <= z_max_beam) ?
            1 - pow((z_max_beam - z) / z_max_beam, 2) :
            pow((z_rim_base - z) / (z_rim_base - z_max_beam), 1.2)
    )
    bulge_amount * factor;

// Interior Y half-width at given Z (with bulge)
function interior_y_at_z(z) =
    let(
        t = z / z_rim_base,
        base_y = floor_semi_y + (inner_semi_y - floor_semi_y) * t,
        bulge = bulge_at_z(z)
    )
    base_y + bulge;

// ENHANCED PARABOLIC SHEER - rim curves up MORE dramatically
// Steeper parabola for more dramatic canoe aesthetic
function sheer_rise(x) =
    let(
        t = abs(x) / outer_semi_x,
        // Enhanced parabolic curve with steeper rise
        parabolic_curve = pow(t, 1.8)  // Lower exponent = more dramatic curve
    )
    (z_rim_max - z_rim_flat) * parabolic_curve;

// Get rim Z at given X
function rim_z_at(x) = z_rim_flat + sheer_rise(x);

// ENHANCED KEEL ROCKER - MORE DRAMATIC parabolic rise
// Flat from center to +/-flat_half_length, then steep parabolic rise
function keel_rocker_at(x) =
    let(
        abs_x = abs(x),
        rise_zone = outer_semi_x - flat_half_length,  // 74 - 33 = 41mm rise zone
        t = (abs_x <= flat_half_length) ? 0 :
            (abs_x - flat_half_length) / rise_zone,
        // Enhanced parabolic rise - MORE dramatic
        parabolic_rise = pow(t, 1.6)  // Lower exponent = steeper curve
    )
    keel_rocker * parabolic_rise;

// Y-SHEER factor - enhanced parabolic taper
function y_sheer_factor(x) =
    let(
        t = (abs(x) - step_x) / (outer_semi_x - step_x),
        clamped_t = max(0, min(1, t)),
        curve = pow(clamped_t, sheer_smoothness)
    )
    1 - 0.7 * curve;

// Superellipse exponent
function superellipse_n(x) =
    let(
        t = (abs(x) - step_x) / (outer_semi_x - step_x),
        clamped_t = max(0, min(1, t))
    )
    2.0 - 0.8 * clamped_t;

// Y half-width at given X (shrinks toward vertex)
function y_half_at_x(x, base_y) =
    let(
        t = abs(x) / outer_semi_x,
        taper = 1 - t * t
    )
    base_y * max(0.05, taper);

// Combined Y half-width at given X and Z
function y_half_at(x, z, is_outer) =
    let(
        base_y = is_outer ?
            (floor_semi_y + wall_base) + ((inner_semi_y + wall_base) - (floor_semi_y + wall_base)) * (z / z_rim_base) + bulge_at_z(z) :
            interior_y_at_z(z),
        t = abs(x) / outer_semi_x,
        base_taper = 1 - t * t,
        adjusted_taper = (abs(x) <= step_x) ? base_taper : base_taper * y_sheer_factor(x) + (1 - y_sheer_factor(x)) * 0.15
    )
    base_y * max(0.08, adjusted_taper);

// ============ MODULES ============

// Superellipse 2D shape
module superellipse_2d(a, b, n, segments=64) {
    points = [
        for (i = [0:segments-1])
            let(
                theta = i * 360 / segments,
                cos_t = cos(theta),
                sin_t = sin(theta),
                r_factor = pow(pow(abs(cos_t), n) + pow(abs(sin_t), n), -1/n),
                x = a * r_factor * cos_t,
                y = b * r_factor * sin_t
            )
            [x, y]
    ];
    polygon(points);
}

// True canoe hull form with bulging cross-section
module canoe_hull_outer() {
    // X stations - SCALED for longer hull (17 stations)
    x_stations = [
        -66, -60, -55, -50, -45, -33, -25, -10,
        0,
        10, 25, 33, 45, 50, 55, 60, 66
    ];

    // Z stations (5 stations for fast iteration)
    z_stations = [0, z_max_beam, 30, 39, z_rim_base];

    hull() {
        for (x = x_stations) {
            for (z = z_stations) {
                floor_z = keel_rocker_at(x);
                rim_z = rim_z_at(x);
                t = z / z_rim_base;
                z_local = floor_z + t * (rim_z - floor_z);

                y_local = y_half_at(x, z, true);
                n = (abs(x) <= step_x) ? 2.0 : superellipse_n(x);

                translate([x, 0, z_local])
                    linear_extrude(height=0.1)
                        superellipse_2d(
                            max(vertex_radius, (z == 0) ? wall_base * 0.8 : wall_base),
                            max(vertex_radius, y_local),
                            n);
            }
        }
    }
}

// Interior cavity with bulging cross-section
module canoe_hull_interior() {
    x_stations = [
        -60, -55, -50, -45, -33, -25, -10,
        0,
        10, 25, 33, 45, 50, 55, 60
    ];

    z_stations = [0, z_max_beam, 30, 39, z_rim_base];

    hull() {
        for (x = x_stations) {
            for (z = z_stations) {
                floor_z = keel_rocker_at(x);
                rim_z = rim_z_at(x);
                t = z / z_rim_base;
                z_local = floor_z + t * (rim_z - floor_z);

                y_local = y_half_at(x, z, false);
                n = (abs(x) <= step_x) ? 2.0 : superellipse_n(x);

                translate([x, 0, z_local + 0.1])
                    linear_extrude(height=0.1)
                        superellipse_2d(
                            max(1, wall_base * 0.3),
                            max(1, y_local),
                            n);
            }
        }
    }

    // Rim cut with INWARD SLOPE
    hull() {
        for (x = [
        -66, -60, -55, -50, -45, -33, -25, -10,
        0,
        10, 25, 33, 45, 50, 55, 60, 66
        ]) {
            z_rim = rim_z_at(x);
            y_local = y_half_at(x, z_rim_base, false) * 1.02;
            n = (abs(x) <= step_x) ? 2.0 : superellipse_n(x);

            translate([x, 0, z_rim - rim_inner_drop])
                linear_extrude(height=10 + rim_inner_drop)
                    superellipse_2d(
                        max(1, wall_base * 0.5),
                        max(1, y_local),
                        n);
        }
    }
}

// Pivot slot with hemispherical seat (RECONCILED with v4.6)
module pivot_slot() {
    slot_length = z_slot_entry - z_pivot_seat;  // v5.1: 46-39 = 7mm (matches v4.6)

    // Vertical slot shaft
    translate([0, 0, z_pivot_seat])
        cylinder(h=slot_length, d=slot_diameter);

    // Hemispherical concave seat at bottom (terminus concavity)
    translate([0, 0, z_pivot_seat])
        sphere(d=slot_diameter);
}

// All four pivot slots
module pivot_slots() {
    for (x_sign = [-1, 1]) {
        for (y_sign = [-1, 1]) {
            translate([x_sign * frame_x_offset, y_sign * slot_y_position, 0])
                pivot_slot();
        }
    }
}

// Slot clearance volumes - ensures interior wall doesn't block slots
// Creates clearance ONLY around pivot seat area, NOT through floor
module slot_clearance_volumes() {
    clearance_diameter = 10;  // Wider to push interior wall away laterally
    clearance_z_start = z_pivot_seat - 8;  // Start below pivot seat
    clearance_height = (z_rim_base + 10) - clearance_z_start;

    for (x_sign = [-1, 1]) {
        for (y_sign = [-1, 1]) {
            translate([x_sign * frame_x_offset, y_sign * slot_y_position, clearance_z_start])
                cylinder(h=clearance_height, d=clearance_diameter);
        }
    }
}

// Rubber feet recesses - discrete stick-on size (6 feet total)
module rubber_feet() {
    foot_d = 8;         // 8mm diameter (common small, discrete)
    foot_depth = 1.5;   // 1.5mm depth (z=0 to z=-1.5mm)

    // Outer corner feet (4 feet, moved inward from edges)
    for (x = [-28, 28]) {
        for (y = [-14, 14]) {
            translate([x, y, -foot_depth])
                cylinder(h=foot_depth + 0.1, d=foot_d);
        }
    }

    // Additional center feet for better stability (2 feet at midship)
    for (y = [-18, 18]) {
        translate([0, y, -foot_depth])
            cylinder(h=foot_depth + 0.1, d=foot_d);
    }
}

// Interior floor fill with step-ups
module inner_floor_fill() {
    // Center zone floor (|x| <= floor_step_x) - flat top at z=floor_z_center
    hull() {
        for (x = [-32, -28, -24, -20, -16, -12, -8, -4, 0, 4, 8, 12, 16, 20, 24, 28, 32]) {
            y_local = y_half_at(x, 33, false) + 3;
            n = (abs(x) <= step_x) ? 2.0 : superellipse_n(x);
            translate([x, 0, 0])
                linear_extrude(height=floor_z_center)
                    superellipse_2d(3, max(1, y_local), n);
        }
    }

    // Bow end floor (x > floor_step_x) - raised to z=floor_z_ends
    hull() {
        for (x = [32, 38, 44, 50, 56, inner_semi_x]) {
            y_local = y_half_at(x, 33, false) + 3;
            n = superellipse_n(x);
            translate([x, 0, 0])
                linear_extrude(height=floor_z_ends)
                    superellipse_2d(max(1, 3), max(1, y_local), n);
        }
    }

    // Stern end floor (x < -floor_step_x) - raised to z=floor_z_ends
    hull() {
        for (x = [-32, -38, -44, -50, -56, -inner_semi_x]) {
            y_local = y_half_at(x, 33, false) + 3;
            n = superellipse_n(x);
            translate([x, 0, 0])
                linear_extrude(height=floor_z_ends)
                    superellipse_2d(max(1, 3), max(1, y_local), n);
        }
    }
}

// ============ DANFORTH ANCHOR INTEGRATION ============

// Import anchor from v1.2
use <GCSC_Danforth_Anchor_v1.2.scad>

// Anchor positioning (sits on middle floor at z=6mm)
// From anchor file: assembled_anchor() needs vertical_shift = 14.05
// to bring shank bottom to z=0, then translate up to floor_z_center
module positioned_anchor() {
    anchor_vertical_shift = 14.05;
    anchor_shank_base_offset = 14.0;

    // Place anchor on floor, rotated 90° so flukes span Y axis
    translate([0, 0, floor_z_center + anchor_shank_base_offset])
        rotate([0, 0, 90])
            translate([0, 0, anchor_vertical_shift])
                assembled_anchor();
}

// ============ MAIN HULL ASSEMBLY ============

module gcsc_hull_v53() {
    union() {
        difference() {
            // Outer canoe form
            canoe_hull_outer();

            // Interior cavity
            canoe_hull_interior();

            // Pivot slots
            pivot_slots();

            // Slot entry cutouts - carve away rim lip around slots
            for (x_sign = [-1, 1]) {
                for (y_sign = [-1, 1]) {
                    translate([x_sign * frame_x_offset, y_sign * slot_y_position, z_slot_entry - 2])
                        cylinder(h=10, d=slot_diameter);
                }
            }

            // Rubber feet
            rubber_feet();
        }

        // Interior floor fill - clipped to interior cavity shape
        intersection() {
            inner_floor_fill();
            canoe_hull_interior();
        }

        // Danforth anchor on middle floor
        positioned_anchor();
    }
}

// ============ RENDER ============

gcsc_hull_v53();

// ============ VERIFICATION ============
echo("=== GCSC HULL v5.3 ===");
echo("Length (X):", outer_rim_x, "mm (full length)");
echo("Width (Y):", outer_rim_y, "mm (full beam)");
echo("Depth (Z):", z_rim_max, "mm (max height)");
echo("Floor center Z:", floor_z_center, "mm");
echo("Floor ends Z:", floor_z_ends, "mm");
echo("Keel rocker:", keel_rocker, "mm");
echo("Flat bottom length:", flat_half_length * 2, "mm");
