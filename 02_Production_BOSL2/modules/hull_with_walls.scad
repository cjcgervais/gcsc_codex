// GCSC2 Phase 2 - Hull with Wall Thickness
// Milestone 2: Add uniform wall thickness using scale approach

include <../lib/BOSL2/std.scad>
include <../lib/BOSL2/skin.scad>
include <../params/station_positions.scad>

// ============ HULL OUTER SURFACE ============
// Reusable module for outer hull shape

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

// ============ HULL WITH UNIFORM WALL THICKNESS ============
// Uses scale approach: outer hull minus scaled inner hull

module hull_complete() {
    // Calculate scale factors for uniform wall thickness
    scale_xy = (beam - 2 * wall_thickness) / beam;
    scale_z = (freeboard - wall_thickness) / freeboard;

    difference() {
        // Outer hull (full size)
        hull_outer_simple();

        // Inner hull (scaled down, offset upward)
        translate([0, 0, wall_thickness])
            scale([scale_xy, scale_xy, scale_z])
                hull_outer_simple();
    }
}

// ============ TEST RENDERING ============

hull_complete();

echo("=== MILESTONE 2: HULL WITH WALL THICKNESS ===");
echo("Wall thickness:", wall_thickness, "mm");
echo("Scale XY:", (beam - 2 * wall_thickness) / beam);
echo("Scale Z:", (freeboard - wall_thickness) / freeboard);
