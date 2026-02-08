// GCSC2 Phase 2 - Pivot Slots Module
// Copied from Phase 1 - PROVEN GEOMETRY (DO NOT MODIFY)
// These slots MUST align with frozen parameters for frame compatibility

include <../params/frozen_dimensions.scad>

// ============ PIVOT SLOTS (From Phase 1) ============
// Creates 4 slots for frame ball pivots
// Position: X = ±frame_x_offset, Y = ±slot_y_position
// Geometry: Vertical cylinder + concave hemisphere seat at Z = z_pivot_seat

module pivot_slots() {
    slot_top = freeboard + 10;
    slot_bottom = 39;
    slot_height = slot_top - slot_bottom;
    hemisphere_center_z = slot_bottom;
    hemisphere_diameter = slot_diameter;

    for (side = [-1, 1]) {
        for (x_pos = [-frame_x_offset, frame_x_offset]) {
            translate([x_pos, side * slot_y_position, (slot_top + slot_bottom)/2]) {
                // Vertical cylinder for slot
                cylinder(d=slot_diameter, h=slot_height, center=true, $fn=32);

                // Concave hemisphere seat at bottom
                slot_center_z = (slot_top + slot_bottom)/2;
                translate([0, 0, hemisphere_center_z - slot_center_z]) {
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

echo("=== PIVOT SLOTS MODULE ===");
echo("Slot positions:");
echo("  X: ±", frame_x_offset, "mm [FROZEN]");
echo("  Y: ±", slot_y_position, "mm [FROZEN]");
echo("  Z hemisphere center:", 39, "mm (at z_pivot_seat =", z_pivot_seat, "mm)");
echo("Slot diameter:", slot_diameter, "mm [FROZEN]");
