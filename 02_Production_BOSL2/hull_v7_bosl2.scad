// ============================================================================
// GCSC2 Phase 2 - Hull v7 Entry Point (BOSL2)
// ============================================================================
//
// VERSION: 7.0.0-alpha
// ARCHITECTURE: BOSL2 station-based skin() hull construction
// AUTHORITY: CANONICAL_DESIGN_REQUIREMENTS.md
//
// This is the Phase 2 hull entry point. Unlike Phase 1's CSG hull() primitives,
// Phase 2 uses BOSL2's skin() function to loft between parametric cross-sections,
// producing true curved surfaces.
//
// ============================================================================
// FUNCTIONAL REQUIREMENTS (MANDATORY)
// ============================================================================
//
// FR-1: FLAT BOTTOM
//   The hull MUST sit stably on a flat surface (bathroom counter).
//   Implementation: section_profile() generates profiles with flat bottom segments.
//   Verification: View from bottom, check flat contact area.
//
// FR-2: BALL INSERTION PATH
//   Frame pivot balls MUST be insertable from above without obstruction.
//   Implementation: pivot_slots() creates clear vertical cylinders.
//   Verification: Cross-section at Y=slot_y_position shows clear path.
//
// FR-3: CURVED GUNWALE
//   Top edge MUST curve up at bow/stern (canoe sheer line).
//   Implementation: curved_gunwale_path() uses bezier curves.
//   Verification: Side view shows curved (not flat) top edge.
//
// FR-4: BOSL2 IMPLEMENTATION
//   Phase 2 MUST use BOSL2 for parametric hull construction.
//   Implementation: skin(), bezier_curve(), path3d() from BOSL2.
//   Verification: Code uses include <BOSL2/std.scad>.
//
// ============================================================================
// FROZEN PARAMETERS (Article 0.6 - IMMUTABLE)
// ============================================================================
//
//   LOA = 148mm          Length Overall
//   beam = 64mm          Maximum Beam
//   freeboard = 45mm     Freeboard height
//   z_pivot_seat = 38mm  Frame attachment Z height
//   slot_diameter = 7.5mm Hull slot diameter
//   frame_x_offset = 16mm Frame X position
//   slot_y_position = 31mm Frame Y position
//
// These parameters are constitutionally frozen and cannot be changed.
// They ensure compatibility with v5.3 frame geometry.
//
// ============================================================================
// USAGE
// ============================================================================
//
// Render complete hull:
//   openscad hull_v7_bosl2.scad -o hull_v7.stl
//
// Preview in OpenSCAD GUI:
//   Open this file, press F5 (preview) or F6 (render)
//
// Debug modes (uncomment at bottom):
//   debug_all_sections()  - Show cross-section profiles
//   debug_gunwale()       - Show gunwale curves
//   hull_outer()          - Outer surface only (no walls)
//
// ============================================================================

include <modules/hull_bosl2.scad>

// ============================================================================
// MAIN RENDER
// ============================================================================

// Render the complete hull with walls, open top, and pivot slots
hull_complete();

// ============================================================================
// DEBUG OPTIONS (uncomment to use)
// ============================================================================

// Show all cross-section profiles:
// debug_all_sections();

// Show outer surface only (faster preview):
// hull_outer();

// Show hull shell (outer - inner, no slots):
// hull_shell();

// Show gunwale curves:
// debug_gunwale();

// ============================================================================
// VERSION HISTORY
// ============================================================================
//
// v7.0.0-alpha (2026-02-05)
//   - Initial Phase 2 architecture with proper BOSL2 patterns
//   - Station-based skin() hull construction (11 stations)
//   - section_profile() with flat bottom segment (FR-1)
//   - curved_gunwale_path() with bezier curves (FR-3)
//   - Pivot slots integrated with clear insertion path (FR-2)
//
// PREVIOUS VERSIONS (Phase 1 - archived):
//   v6.1.0 - "Beautiful Hull" - FAILED human verification
//   v6.0.0 - Phase 1 CSG hull() primitives
//   v5.3   - Human-iterated reference design (BASELINE)
//
// ============================================================================

echo("=== GCSC2 HULL v7.0.0-alpha (BOSL2) ===");
echo("Phase 2 Architecture: Station-based skin() construction");
echo("");
echo("Functional Requirements Status:");
echo("  FR-1 (Flat Bottom): IMPLEMENTED - section_profile()");
echo("  FR-2 (Ball Insertion): IMPLEMENTED - pivot_slots()");
echo("  FR-3 (Curved Gunwale): IMPLEMENTED - curved_gunwale_path()");
echo("  FR-4 (BOSL2): IMPLEMENTED - skin(), bezier_curve()");
echo("");
echo("Frozen Parameters (Article 0.6):");
echo("  LOA:", LOA, "mm");
echo("  beam:", beam, "mm");
echo("  freeboard:", freeboard, "mm");
echo("  z_pivot_seat:", z_pivot_seat, "mm");
echo("  slot_diameter:", slot_diameter, "mm");
echo("  frame_x_offset:", frame_x_offset, "mm");
echo("  slot_y_position:", slot_y_position, "mm");
echo("");
