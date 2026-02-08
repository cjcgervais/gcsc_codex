// ============================================================================
// GCSC2 Phase 2 - Hull BOSL2 Module
// ============================================================================
//
// Architecture: Station-based skin() hull construction with true curved surfaces
// Authority: CANONICAL_DESIGN_REQUIREMENTS.md
//
// FUNCTIONAL REQUIREMENTS COMPLIANCE:
//   FR-1: Flat Bottom     - section_profile() uses flat bottom segments
//   FR-2: Ball Insertion  - Slot geometry from pivot_slots.scad (proven Phase 1)
//   FR-3: Curved Gunwale  - curved_gunwale_path() uses bezier curves
//   FR-4: BOSL2 Required  - Uses skin(), bezier_curve(), path3d()
//
// FROZEN PARAMETERS (Article 0.6):
//   LOA=148, beam=64, freeboard=45, z_pivot_seat=38
//   slot_diameter=7.5, frame_x_offset=16, slot_y_position=31
//
// ============================================================================

include <../lib/BOSL2/std.scad>
include <../params/station_positions.scad>

// ============================================================================
// SECTION 1: SECTION PROFILE GENERATION
// ============================================================================
// Creates hull cross-section profiles that vary from bow to stern.
// Key insight: Canoe sections are NOT ellipses - they have:
//   - Flat or shallow-V bottom (FR-1 compliance)
//   - Rounded bilge (transition from bottom to sides)
//   - Tumblehome sides (inward curve at top)
//   - Section shape varies along length (sharper at ends, fuller at midship)

// Generate a single hull cross-section profile at station position x
// Returns a 2D path in the Y-Z plane (Y=beam direction, Z=up)
function section_profile(x_pos, n_points=32) =
    let(
        // ============================================================
        // SDT-2 FIX: SLOT ZONE BEAM MAINTENANCE
        // ============================================================
        // Problem: Frozen slot_y_position=31mm requires slots at Y=31mm
        // But aggressive taper reduced beam to ~26mm at x=frame_x_offset
        // Result: Slots were OUTSIDE the hull wall (no openings)
        //
        // Solution: Maintain full beam through "slot zone" (|x| <= 20mm)
        // This ensures hull wall extends to Y=32mm at slot positions
        // ============================================================
        slot_zone = 20,  // frame_x_offset(16) + 4mm margin

        // Station parameters at this X position
        // Within slot zone: treat as midship (x_norm=0, full beam)
        // Outside slot zone: taper from slot_zone edge to bow/stern
        x_norm = abs(x_pos) <= slot_zone ? 0 :
                 (abs(x_pos) - slot_zone) / (half_LOA - slot_zone),
        beam_scale = lerp(1.0, x_pos < 0 ? bow_beam_ratio : stern_beam_ratio, x_norm),
        local_half_beam = half_beam * beam_scale,

        // Vertical adjustments
        sheer_offset = station_sheer_offset(x_pos),
        rocker_offset = station_rocker_offset(x_pos),
        local_freeboard = freeboard + sheer_offset,

        // Section shape parameters (vary with station position)
        // At ends: sharper entry (more V-like, narrower)
        // At midship: fuller section (flatter bottom, wider)
        flatness = lerp(1.0, 0.3, x_norm),  // 1.0=flat bottom, 0.3=sharper V
        bilge_radius_ratio = lerp(0.35, 0.15, x_norm),  // Bilge rounding

        // FR-1 COMPLIANCE: Flat bottom width
        // At midship: substantial flat area for stability
        // At ends: narrower but still not a sharp V
        flat_bottom_half_width = local_half_beam * flatness * 0.4,

        // Key heights
        z_bottom = rocker_offset,  // Keel curves up at ends
        z_bilge = z_bottom + local_freeboard * 0.2,  // Bilge transition
        z_max_beam = z_bottom + local_freeboard * 0.35,  // Widest point
        z_sheer = local_freeboard,  // Top edge

        // Tumblehome: beam narrows above max beam point
        // FIX 4: In slot zone, reduce tumblehome to ensure hull extends past slot_y_position
        // at z_pivot_seat. Without this, hull only reaches Y≈29mm but slots are at Y=31mm.
        in_slot_zone = abs(x_pos) <= slot_zone,
        effective_tumblehome_angle = in_slot_zone ? 0 : tumblehome_angle,  // No tumblehome in slot zone
        tumblehome_inset = tan(effective_tumblehome_angle) * (z_sheer - z_max_beam),
        beam_at_sheer = local_half_beam - tumblehome_inset,

        // Build profile as sequence of points (starboard side, bottom to top)
        // Then mirror for port side
        n_bottom = max(2, floor(n_points * 0.15)),
        n_bilge = max(3, floor(n_points * 0.25)),
        n_side = max(3, floor(n_points * 0.25)),
        n_tumblehome = max(2, floor(n_points * 0.1)),

        // Bottom segment (flat, FR-1 compliance)
        bottom_pts = [for(i=[0:n_bottom-1])
            let(t = i / (n_bottom - 1))
            [lerp(0, flat_bottom_half_width, t), z_bottom]
        ],

        // Bilge segment (curved transition from bottom to side)
        bilge_pts = [for(i=[1:n_bilge])
            let(
                t = i / n_bilge,
                angle = t * 90,  // 0 to 90 degrees
                y = flat_bottom_half_width + (local_half_beam - flat_bottom_half_width) * sin(angle) * bilge_radius_ratio +
                    (local_half_beam - flat_bottom_half_width) * (1 - bilge_radius_ratio) * t,
                z = z_bottom + (z_bilge - z_bottom) * (1 - cos(angle))
            )
            [y, z]
        ],

        // FIX 2: Calculate where bilge ends for Y-continuity
        // Bilge ends at (local_half_beam, z_bilge) when t=1, angle=90
        bilge_end_y = flat_bottom_half_width + (local_half_beam - flat_bottom_half_width),  // = local_half_beam

        // Side segment (from bilge end to max beam height)
        // FIX 2: Start at bilge_end_y instead of 0.7*local_half_beam to eliminate 10mm gap
        side_pts = [for(i=[1:n_side])
            let(
                t = i / n_side,
                y = lerp(bilge_end_y, local_half_beam, t),  // Continuous from bilge end
                z = lerp(z_bilge, z_max_beam, t)
            )
            [y, z]
        ],

        // Tumblehome segment (inward curve to sheer)
        tumblehome_pts = [for(i=[1:n_tumblehome])
            let(
                t = i / n_tumblehome,
                y = lerp(local_half_beam, beam_at_sheer, t),
                z = lerp(z_max_beam, z_sheer, t)
            )
            [y, z]
        ],

        // Combine starboard half (positive Y)
        starboard_half = concat(bottom_pts, bilge_pts, side_pts, tumblehome_pts),

        // FIX 1: Mirror to port side - INCLUDE sheer point (last index) for closed loop
        // Previous bug: started at len-2, missing the sheer crossover point
        // The profile must form a closed loop for skin() to work correctly
        port_half = [for(i=[len(starboard_half)-1:-1:1])  // Include sheer (len-1), stop before centerline dup (0)
            [-starboard_half[i][0], starboard_half[i][1]]
        ],

        // PROFILE CLOSURE FIX (GPT/Agent identified bug):
        // Profile must form a CLOSED loop for CGAL/skin() to produce valid manifold.
        // Previous code: profile ended at port_half's last point (near centerline but not AT centerline)
        // This created a ~4mm gap at keel centerline causing groove artifacts.
        // Fix: Explicitly add starboard_half[0] (the centerline starting point) to close the loop.
        // Invariants maintained:
        //   - First point = last point (closed loop)
        //   - No duplicate adjacent points (port_half stops at index 1)
        //   - Consistent winding order (CCW when viewed from +X)
        profile = concat(starboard_half, port_half, [starboard_half[0]])
    )
    profile;


// ============================================================================
// SECTION 2: CURVED GUNWALE PATH (FR-3 COMPLIANCE)
// ============================================================================
// The gunwale (top edge) MUST have the characteristic curved profile of a canoe.
// This is THE defining aesthetic feature that makes it look like a canoe.
// Uses Bezier curves for smooth, natural-looking sheer line.

// Generate the 3D path of the gunwale (sheer line) for one side
// Returns a 3D path from bow to stern at the top edge of the hull
function curved_gunwale_path(side=1, n_points=48) =
    let(
        // Generate points along the gunwale using bezier control for smooth curve
        // Control points for sheer curve (in X-Z plane, side determines Y)
        bow_point = [-half_LOA, side * beam_at_station(-half_LOA), gunwale_z(-half_LOA)],
        bow_control = [-half_LOA * 0.7, side * beam_at_station(-half_LOA * 0.7), gunwale_z(-half_LOA * 0.5)],
        mid_point = [0, side * half_beam * (1 - tan(tumblehome_angle) * freeboard * 0.35 / half_beam), freeboard],
        stern_control = [half_LOA * 0.7, side * beam_at_station(half_LOA * 0.7), gunwale_z(half_LOA * 0.5)],
        stern_point = [half_LOA, side * beam_at_station(half_LOA), gunwale_z(half_LOA)],

        // Cubic bezier for each half (bow to mid, mid to stern)
        bow_to_mid = bezier_curve([bow_point, bow_control, mid_point], splinesteps=n_points/2),
        mid_to_stern = bezier_curve([mid_point, stern_control, stern_point], splinesteps=n_points/2)
    )
    concat(bow_to_mid, [for(i=[1:len(mid_to_stern)-1]) mid_to_stern[i]]);

// Helper: Get beam at a given X position (accounting for tumblehome at sheer)
function beam_at_station(x_pos) =
    let(
        x_norm = abs(x_pos) / half_LOA,
        beam_scale = x_pos < 0 ? lerp(1.0, bow_beam_ratio, x_norm) : lerp(1.0, stern_beam_ratio, x_norm),
        local_half_beam = half_beam * beam_scale,
        sheer_offset = station_sheer_offset(x_pos),
        local_freeboard = freeboard + sheer_offset,
        tumblehome_inset = tan(tumblehome_angle) * local_freeboard * 0.35
    )
    local_half_beam - tumblehome_inset;

// Helper: Get gunwale Z height at a given X position
function gunwale_z(x_pos) =
    freeboard + station_sheer_offset(x_pos);


// ============================================================================
// SECTION 3: HULL SURFACE CONSTRUCTION
// ============================================================================
// Uses BOSL2 skin() to loft between cross-section profiles.

// Number of stations for hull lofting (more = smoother, slower)
hull_stations = 11;  // Odd number ensures midship station at x=0

// Generate station X positions for smooth lofting
function hull_station_x_positions(n=hull_stations) =
    [for(i=[0:n-1]) lerp(-half_LOA, half_LOA, i/(n-1))];

// Generate all hull profiles as 3D paths
function hull_profiles_3d(n=hull_stations) =
    let(
        x_positions = hull_station_x_positions(n)
    )
    [for(x = x_positions)
        let(
            profile_2d = section_profile(x),
            rocker = station_rocker_offset(x)
        )
        // Transform 2D profile (Y,Z) to 3D position at this X station
        [for(pt = profile_2d) [x, pt[0], pt[1]]]
    ];

// Hull outer surface module
module hull_outer() {
    profiles = hull_profiles_3d();

    // Use skin() to loft between profiles
    // method="reindex" helps align points between different-sized sections
    skin(profiles, slices=8, method="reindex", caps=true, style="min_edge");
}

// Hull inner surface (for wall thickness)
// STEP 2 FIX: Replace uniform scaling with profile-based insetting
//
// WHY SCALING FAILS FOR TAPERED HULLS:
// - Scaling works at midship but fails at tapered bow/stern
// - Inner hull X-extent equals outer, causing end cap punch-through
//
// FIX: Generate inner hull from inset profiles with SHORTER X range
// - Inner hull stops before bow/stern (no end cap collision)
// - Each inner profile is inset toward centroid by wall_thickness
module hull_inner() {
    // Inner hull uses SHORTER station range (stops before bow/stern)
    inner_margin = wall_thickness * 1.5;
    inner_start_x = -half_LOA + inner_margin;
    inner_end_x = half_LOA - inner_margin;

    // Generate inner profiles with inset and shortened range
    inner_profiles = [
        for(i = [0:hull_stations-1])
            let(
                // Map station index to inner X range
                t = i / (hull_stations - 1),
                x = lerp(inner_start_x, inner_end_x, t),

                // Get outer profile at this X and inset it
                outer_profile = section_profile(x),

                // Inset the profile toward centroid by wall_thickness
                // Profile is symmetric about Y=0, center height approx freeboard/2
                centroid_y = 0,
                centroid_z = freeboard / 2 + wall_thickness,

                // Inset each point toward centroid
                inset_profile = [
                    for(pt = outer_profile)
                        let(
                            dy = pt[0] - centroid_y,
                            dz = pt[1] - centroid_z,
                            dist = sqrt(dy*dy + dz*dz),
                            new_dist = max(1, dist - wall_thickness),
                            scale_factor = dist > 0.001 ? new_dist / dist : 1
                        )
                        [centroid_y + dy * scale_factor, centroid_z + dz * scale_factor]
                ]
            )
            // Transform 2D inset profile to 3D at this X station
            [for(pt = inset_profile) [x, pt[0], pt[1]]]
    ];

    // Translate up by wall_thickness for floor
    translate([0, 0, wall_thickness])
        skin(inner_profiles, slices=8, method="reindex", caps=true, style="min_edge");
}

// Complete hull shell with walls
module hull_shell() {
    difference() {
        hull_outer();
        hull_inner();
    }
}


// ============================================================================
// SECTION 4: OPEN-TOP HULL (FR-1 SOAP DISH REQUIREMENT)
// ============================================================================
// Cut the top open following the curved gunwale line.
// This creates the actual soap dish bowl.

module hull_open_top() {
    // The curved gunwale defines where we cut
    // We need to cut everything ABOVE the sheer line
    max_sheer_z = freeboard + sheer_rise + 1;  // Highest point + margin

    difference() {
        hull_shell();

        // Simple planar cut at maximum sheer height
        // TODO: In future, follow actual curved gunwale for better aesthetics
        translate([0, 0, max_sheer_z + 25])
            cube([LOA + 10, beam + 10, 50], center=true);
    }
}


// ============================================================================
// SECTION 5: COMPLETE HULL WITH PIVOT SLOTS
// ============================================================================
// Combines hull shell with frame pivot slots for gimbal mechanism.

module hull_complete() {
    difference() {
        hull_open_top();

        // Import pivot slots from proven Phase 1 geometry
        pivot_slots();
    }
}

// Pivot slots module (inline for now, can be imported from pivot_slots.scad)
module pivot_slots() {
    slot_top = freeboard + sheer_rise + 5;
    slot_bottom = z_pivot_seat + 1;  // Just above pivot seat
    slot_height = slot_top - slot_bottom;
    hemisphere_center_z = z_pivot_seat + 1;
    hemisphere_diameter = slot_diameter;

    for (side = [-1, 1]) {
        for (x_pos = [-frame_x_offset, frame_x_offset]) {
            translate([x_pos, side * slot_y_position, (slot_top + slot_bottom)/2]) {
                // Vertical cylinder for slot (FR-2: clear insertion path)
                cylinder(d=slot_diameter, h=slot_height, center=true, $fn=32);

                // Concave hemisphere seat at bottom
                translate([0, 0, hemisphere_center_z - (slot_top + slot_bottom)/2]) {
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


// ============================================================================
// SECTION 6: DEBUG AND VISUALIZATION
// ============================================================================

// Show cross-section at a specific X position
module debug_section(x_pos=0) {
    profile = section_profile(x_pos);
    rocker = station_rocker_offset(x_pos);

    color("blue", 0.5)
    translate([x_pos, 0, 0])
    rotate([90, 0, 90])
    linear_extrude(1, center=true)
    polygon(profile);
}

// Show all station cross-sections
module debug_all_sections() {
    x_positions = hull_station_x_positions();
    for(x = x_positions) {
        debug_section(x);
    }
}

// Show gunwale curves using BOSL2 stroke (Phase 2 compliant)
module debug_gunwale() {
    // Starboard gunwale - use stroke() instead of hull() of spheres
    color("red")
    stroke(curved_gunwale_path(1), width=1, $fn=8);

    // Port gunwale
    color("red")
    stroke(curved_gunwale_path(-1), width=1, $fn=8);
}


// ============================================================================
// SECTION 7: ECHO DIAGNOSTICS
// ============================================================================

echo("=== GCSC2 PHASE 2: HULL_BOSL2.SCAD ===");
echo("Frozen Parameters:");
echo("  LOA:", LOA, "mm");
echo("  beam:", beam, "mm");
echo("  freeboard:", freeboard, "mm");
echo("  z_pivot_seat:", z_pivot_seat, "mm");
echo("");
echo("Functional Requirements:");
echo("  FR-1 (Flat Bottom): section_profile() with flat bottom segment");
echo("  FR-2 (Ball Insertion): pivot_slots() with clear vertical path");
echo("  FR-3 (Curved Gunwale): curved_gunwale_path() with bezier curves");
echo("  FR-4 (BOSL2): skin(), bezier_curve() from BOSL2 library");
echo("");
echo("Hull Construction:");
echo("  Stations:", hull_stations);
echo("  Station X range:", -half_LOA, "to", half_LOA);
echo("  Skin method: reindex");
echo("");
