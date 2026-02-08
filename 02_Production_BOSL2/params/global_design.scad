// GCSC2 Phase 2 - GLOBAL DESIGN PARAMETERS
// These parameters control overall hull form - TUNABLE in Phase 2
//
// Design Philosophy: These define HOW the hull reaches the frozen dimension
// constraints (LOA, beam, freeboard), not WHAT those constraints are.

include <frozen_dimensions.scad>

// ============ HULL FORM PARAMETERS (from Phase 1) ============

tumblehome_angle = 8;         // Inward slope of sides above max beam (degrees)
                              // Range: [0-20], 0=vertical, 15=aggressive
                              // Effect: Hull sides lean inward at sheer

deadrise_angle = 12;          // V-angle of hull bottom (degrees)
                              // Range: [5-25], 5=flat, 25=sharp V
                              // Effect: Hull floor geometry, entry angle

sheer_rise = 20;              // Sheer elevation at bow/stern (mm above midship)
                              // Range: [10-30]
                              // Effect: Gunwale curves up at ends

keel_rocker = 8;              // Keel upward curve at bow/stern (mm)
                              // Range: [5-15] for soap dish stability (SDT-1)
                              // Effect: Bottom curves up at ends
                              // NOTE: Reduced from 42mm to 8mm for flat bottom stability
                              // SDT-1 FIX: v6.1.0 failed because excessive rocker
                              // prevented hull from sitting flat on counter

// ============ PHASE 2 BEAM DISTRIBUTION ============
// Controls how beam tapers bow-to-stern (new in Phase 2)

bow_beam_ratio = 0.15;        // Bow beam as fraction of max beam
                              // Range: [0.1-0.3], smaller=sharper entry

stern_beam_ratio = 0.20;      // Stern beam as fraction of max beam
                              // Range: [0.15-0.4], can be wider than bow

forward_beam_ratio = 0.75;    // Forward quarter (25% LOA) beam ratio
                              // Range: [0.6-0.9]

aft_beam_ratio = 0.80;        // Aft quarter (75% LOA) beam ratio
                              // Range: [0.7-0.95]

// ============ MANUFACTURING PARAMETERS ============

wall_thickness = 7;           // Hull shell thickness (mm)
tolerance = 0.2;              // Fit clearance (mm)
$fn = 64;                     // Render quality (64=production, 32=preview)

// ============ DERIVED VALUES ============

// Maximum beam height (typical canoe: 34% up from keel)
z_max_beam = freeboard * 0.34;

// Tumblehome offset at sheer
tumblehome_offset = tan(tumblehome_angle) * freeboard;

// Interior dimensions
interior_beam_at_sheer = beam - 2 * (wall_thickness + tumblehome_offset);

// ============ VALIDATION ============

echo("=== PHASE 2 GLOBAL DESIGN PARAMETERS ===");
echo("Tumblehome angle:", tumblehome_angle, "degrees");
echo("Deadrise angle:", deadrise_angle, "degrees");
echo("Sheer rise:", sheer_rise, "mm");
echo("Keel rocker:", keel_rocker, "mm");
echo("");
echo("Beam distribution:");
echo("  Bow:", bow_beam_ratio * 100, "%");
echo("  Forward quarter:", forward_beam_ratio * 100, "%");
echo("  Midship: 100%");
echo("  Aft quarter:", aft_beam_ratio * 100, "%");
echo("  Stern:", stern_beam_ratio * 100, "%");
echo("");
