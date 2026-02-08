// GCSC2 Phase 2 - FROZEN DIMENSIONS (Article 0.6)
// These 7 parameters are IMMUTABLE - they preserve v5.3/v6.0 compatibility
// DO NOT MODIFY - any change breaks frozen parameter compliance
//
// Validated: 2026-02-03 (copied from Phase 1 v6.0)

// ============ ARTICLE 0.6 FROZEN PARAMETERS ============
// These dimensions are constitutionally frozen and cannot be changed

LOA = 148;                    // Length Overall (mm) - FROZEN
beam = 64;                    // Maximum Beam (mm) - FROZEN
freeboard = 45;               // Freeboard (mm) - FROZEN
z_pivot_seat = 38;            // Frame Attachment Height (mm) - FROZEN
slot_diameter = 7.5;          // Slot Diameter (mm) - FROZEN
frame_x_offset = 16;          // Frame Longitudinal Position (mm) - FROZEN
slot_y_position = 31;         // Frame Lateral Position (mm) - FROZEN

// ============ DERIVED VALUES (Computed from frozen params) ============

half_LOA = LOA / 2;
half_beam = beam / 2;

// ============ VALIDATION ============

echo("=== PHASE 2 FROZEN PARAMETERS ===");
echo("LOA:", LOA, "mm [FROZEN]");
echo("beam:", beam, "mm [FROZEN]");
echo("freeboard:", freeboard, "mm [FROZEN]");
echo("z_pivot_seat:", z_pivot_seat, "mm [FROZEN]");
echo("slot_diameter:", slot_diameter, "mm [FROZEN]");
echo("frame_x_offset:", frame_x_offset, "mm [FROZEN]");
echo("slot_y_position:", slot_y_position, "mm [FROZEN]");
echo("");
