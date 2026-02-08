// GCSC2 Phase 2 - Hull with Open Top
// Milestone 3: Cut top open at sheer line (FR-1 requirement)

include <../lib/BOSL2/std.scad>
include <../lib/BOSL2/skin.scad>
include <../params/station_positions.scad>

// ============ HULL OUTER SURFACE ============

module hull_outer_simple() {
    profiles_3d = [
        for (i = [0:len(station_x)-1])
            let(
                x = station_x[i],
                beam_scale = station_beam_scale()[i],
                local_beam = beam * beam_scale,
                local_freeboard = freeboard + station_sheer_offset(x),
                z_offset = station_rocker_offset(x),
                profile_2d = ellipse(d=[local_beam, local_freeboard], $fn=32)
            )
            path3d(profile_2d, x, z_offset)
    ];

    skin(profiles_3d, slices=10, method="tangent", caps=false);
}

// ============ HULL WITH WALLS AND OPEN TOP ============

module hull_open_top() {
    scale_xy = (beam - 2 * wall_thickness) / beam;
    scale_z = (freeboard - wall_thickness) / freeboard;

    difference() {
        // Hull with walls
        difference() {
            hull_outer_simple();
            translate([0, 0, wall_thickness])
                scale([scale_xy, scale_xy, scale_z])
                    hull_outer_simple();
        }

        // Cut top open - everything above freeboard + sheer_rise
        translate([0, 0, freeboard + sheer_rise + 5])
            cube([LOA * 3, beam * 3, 50], center=true);
    }
}

// ============ TEST RENDERING ============

hull_open_top();

echo("=== MILESTONE 3: HULL WITH OPEN TOP ===");
echo("Freeboard (midship):", freeboard, "mm");
echo("Max sheer height:", freeboard + sheer_rise, "mm");
echo("FR-1 open-top requirement: IMPLEMENTED");
