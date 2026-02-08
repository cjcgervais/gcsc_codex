// GCSC2 v6.0 - Phase 1 Minimalist Parameters
// Design Intent: Clear boat terminology, single source of truth
//
// Based on GCSC v5.2 dimensions, translated to proper naval architecture terms

// ============ PRIMARY DIMENSIONS ============
// These are the core parameters. All other values derive from these.

LOA = 148;                    // Length Overall (mm) - total canoe length
beam = 64;                    // Maximum Beam (mm) - widest point (reduced by 20mm for less angular profile)
freeboard = 45;               // Freeboard (mm) - height at midship from keel to sheer
wall_thickness = 7;           // Shell Thickness (mm) - uniform wall

// ============ HULL FORM PARAMETERS ============

tumblehome_angle = 8;         // Tumblehome (degrees) - inward slope of sides above max beam
deadrise_angle = 12;          // Deadrise (degrees) - V-angle of hull bottom
sheer_rise = 20;              // Sheer Rise (mm) - how much gunwale curves up at bow/stern
keel_rocker = 42;             // Keel Rocker (mm) - upward curve of keel at bow/stern

// ============ STRUCTURAL PARAMETERS ============

z_pivot_seat = 38;            // Frame Attachment Height (mm) - where frame balls sit (frame top rail aligns with hull freeboard at 45mm)
slot_diameter = 7.5;          // Slot Diameter (mm) - for frame ball pivots (0.25mm clearance for 7.25mm balls)
frame_x_offset = 16;          // Frame Longitudinal Position (mm) - fore/aft from center
slot_y_position = 31;         // Frame Lateral Position (mm) - port/starboard from centerline (port/starboard from centerline)

// ============ FRAME STRUCTURAL PARAMETERS ============

// Top rail dimensions (where soap rests)
rail_thickness = 3;           // Rail Thickness (mm) - cross-section thin dimension
rail_vertical_height = 6;     // Rail Vertical Height (mm) - how tall rail bar is
rail_span_y = 60;             // Rail Span Y (mm) - port-to-starboard length

// Frame trapezoid dimensions
frame_height = 22;            // Frame Height (mm) - total vertical extent of inverse trapezoid
bottom_rail_span_y = 36;      // Bottom Rail Span (mm) - narrower for inverse trapezoid

// Pivot and connection
ball_diameter = 7.25;         // Ball Diameter (mm) - pivot balls (matches CF_Frame_v5.3_infill)
ball_arm_length = 5;          // Ball Arm Length (mm) - extension arm from frame to ball

// Side member dimensions
side_member_thickness = 3;    // Side Member Thickness (mm) - cross-section

// ============ MANUFACTURING PARAMETERS ============

tolerance = 0.2;              // Fit Clearance (mm) - for frame/hull interface
$fn = 64;                     // Render Quality - facets for circles (64 = production, 32 = preview)

// ============ DERIVED VALUES (Computed, not edited) ============
// These are calculated from the primary dimensions above

half_LOA = LOA / 2;
half_beam = beam / 2;
socket_clearance = slot_diameter + tolerance * 2;

// Maximum beam occurs at 34% of freeboard height (typical canoe proportions)
z_max_beam = freeboard * 0.34;

// Interior beam accounting for wall thickness and tumblehome
interior_beam_at_sheer = beam - 2 * (wall_thickness + tan(tumblehome_angle) * freeboard);

// ============ HELPER FUNCTIONS ============

// Helper function to compute tumblehome scaling factor
// Used by hull_simple.scad to control sheer point scaling
function tumblehome_factor() =
    1.0 - (tan(tumblehome_angle) * freeboard / half_beam);

// ============ VALIDATION ============
// Echo key dimensions for verification

echo("=== GCSC2 v6.0 PARAMETERS ===");
echo("LOA:", LOA, "mm");
echo("Beam:", beam, "mm");
echo("Freeboard:", freeboard, "mm");
echo("Wall thickness:", wall_thickness, "mm");
echo("Tumblehome angle:", tumblehome_angle, "degrees");
echo("Deadrise angle:", deadrise_angle, "degrees");
echo("");
echo("Frame attachment:");
echo("  Z height:", z_pivot_seat, "mm");
echo("  X offset:", frame_x_offset, "mm");
echo("  Y position:", slot_y_position, "mm");
echo("  Slot diameter:", slot_diameter, "mm");
echo("");
echo("Derived values:");
echo("  Z max beam:", z_max_beam, "mm");
echo("  Interior beam at sheer:", interior_beam_at_sheer, "mm");
