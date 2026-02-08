// GCSC Slot Plugs v3.0 TIGHT
// Tighter shaft variant for fit testing (0.10mm clearance vs 0.15mm standard)
// For Hull v4.6 (7.5mm slots, Y=39) with Frame v3.9 (7.25mm balls)
// Print 4x (one per slot)

// ============ PARAMETERS ============

slot_diameter = 7.5;
z_pivot_seat = 49;
z_slot_entry = 56;
slot_radius = slot_diameter / 2;

ball_diameter = 7.25;
ball_radius = ball_diameter / 2;

// ============ PLUG DIMENSIONS ============

shaft_clearance = 0.10;         // TIGHT (standard = 0.15)
shaft_diameter = slot_diameter - shaft_clearance;  // 7.40mm

ball_clearance = 0.25;
hemisphere_center_z = z_pivot_seat + ball_clearance;
shaft_length = z_slot_entry - hemisphere_center_z;

cavity_diameter = 8.0;
cavity_radius = cavity_diameter / 2;

cap_overhang = 1.5;
cap_diameter = slot_diameter + cap_overhang * 2;
cap_thickness = 1.5;

lift_tab_width = 3.5;
lift_tab_length = 4;
lift_tab_thickness = 1.2;

$fn = 64;

// ============ MODULES ============

module plug_shaft() {
    difference() {
        cylinder(h = shaft_length, d = shaft_diameter);
        sphere(d = cavity_diameter);
    }
}

module plug_cap() {
    union() {
        cylinder(h = cap_thickness, d = cap_diameter);
        translate([cap_diameter/2 - 1, 0, 0])
            hull() {
                cylinder(h = lift_tab_thickness, d = lift_tab_width);
                translate([lift_tab_length, 0, 0])
                    cylinder(h = lift_tab_thickness, d = lift_tab_width);
            }
    }
}

module slot_plug() {
    union() {
        plug_shaft();
        translate([0, 0, shaft_length])
            plug_cap();
    }
}

module slot_plug_printable() {
    translate([0, 0, cap_thickness])
        rotate([180, 0, 0])
            slot_plug();
}

// ============ RENDER ============

slot_plug();

// Uncomment for print orientation:
// slot_plug_printable();

// Uncomment for 4-up batch:
// for (i = [0:3])
//     translate([i * 14, 0, 0])
//         slot_plug_printable();

// ============ VERIFICATION ============
echo("=== SLOT PLUGS v3.0 TIGHT ===");
echo("Shaft clearance:", shaft_clearance, "mm (standard: 0.15)");
echo("Shaft diameter:", shaft_diameter, "mm (slot:", slot_diameter, ")");
echo("Shaft length:", shaft_length, "mm");
echo("Cavity diameter:", cavity_diameter, "mm (ball:", ball_diameter, ")");
echo("Cap diameter:", cap_diameter, "mm");
