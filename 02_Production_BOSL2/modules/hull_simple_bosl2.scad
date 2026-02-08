// GCSC2 Phase 2 - Simple BOSL2 Hull Module
// Milestone 1: Prove station-based skin() approach works
// Uses simple oval profiles before adding Bézier complexity

include <../lib/BOSL2/std.scad>
include <../lib/BOSL2/skin.scad>
include <../params/station_positions.scad>

// ============ SIMPLE HULL OUTER SURFACE ============
// Creates basic canoe shape with 5 oval cross-sections

module hull_outer_simple() {
    // Generate profile at each station
    profiles_3d = [
        for (i = [0:len(station_x)-1])
            let(
                x = station_x[i],
                beam_scale = station_beam_scale()[i],
                local_beam = beam * beam_scale,
                local_freeboard = freeboard + station_sheer_offset(x),
                z_offset = station_rocker_offset(x),

                // Simple oval profile (ellipse in Y-Z plane)
                // Y-axis: beam (width), Z-axis: freeboard (height)
                profile_2d = ellipse(d=[local_beam, local_freeboard], $fn=32)
            )
            // Transform to 3D position
            path3d(profile_2d, x, z_offset)
    ];

    // Loft surface between profiles
    skin(profiles_3d, slices=10, method="tangent", caps=false);
}

// ============ TEST RENDERING ============

hull_outer_simple();

echo("=== MILESTONE 1: SIMPLE STATION HULL ===");
echo("Expected: Canoe-shaped hull with pointed ends and wide middle");
echo("Stations:", len(station_x));
echo("LOA:", LOA, "mm");
echo("Max beam (midship):", beam, "mm");
