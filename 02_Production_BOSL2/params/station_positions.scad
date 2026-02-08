// GCSC2 Phase 2 - STATION POSITIONS
// Defines longitudinal positions of hull cross-sections
//
// Design Philosophy: 5 stations capture bow, forward, midship, aft, stern
// Station 2 (midship) is at X=0 (origin) for symmetry

include <frozen_dimensions.scad>
include <global_design.scad>

// ============ STATION X POSITIONS (Longitudinal) ============
// 5 stations along hull length (fore-aft axis)

station_x = [
    -half_LOA,                // Station 0: Bow (forward end)
    -half_LOA * 0.5,          // Station 1: Forward quarter (25% from bow)
    0,                        // Station 2: Midship (center, widest point)
    half_LOA * 0.5,           // Station 3: Aft quarter (75% from bow)
    half_LOA                  // Station 4: Stern (aft end)
];

// Station labels for documentation/debugging
station_names = [
    "Bow",
    "Forward Quarter",
    "Midship",
    "Aft Quarter",
    "Stern"
];

// ============ STATION BEAM SCALING ============
// How beam tapers along hull length (fraction of max beam)

function station_beam_scale() = [
    bow_beam_ratio,           // Station 0: 15% of max beam (narrow)
    forward_beam_ratio,       // Station 1: 75%
    1.0,                      // Station 2: 100% (fullest)
    aft_beam_ratio,           // Station 3: 80%
    stern_beam_ratio          // Station 4: 20% (slightly wider than bow)
];

// ============ LONGITUDINAL CURVES ============

// Sheer offset: how much gunwale rises at each station (parabolic)
function station_sheer_offset(x_pos) =
    sheer_rise * pow(abs(x_pos) / half_LOA, 2);

// Rocker offset: how much keel curves up at each station
// SDT-1 FIX: Flat center zone ensures hull sits stable on counter
// The center 60mm (30mm each side of midship) is completely flat
function station_rocker_offset(x_pos) =
    let(
        flat_zone = 30,  // Flat bottom in center 60mm for SDT-1 compliance
        effective_x = max(0, abs(x_pos) - flat_zone),
        active_length = half_LOA - flat_zone
    )
    keel_rocker * pow(effective_x / active_length, 2);

// ============ VALIDATION ============

echo("=== PHASE 2 STATION POSITIONS ===");
for (i = [0:len(station_x)-1]) {
    echo(str(
        station_names[i], ": ",
        "X=", station_x[i], "mm, ",
        "Beam=", round(beam * station_beam_scale()[i]), "mm (",
        round(station_beam_scale()[i] * 100), "%)"
    ));
}
echo("");
