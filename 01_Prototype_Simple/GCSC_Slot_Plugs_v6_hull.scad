// GCSC Slot Plugs for Hull v6
// Updated for current hull dimensions
// For Hull v6 (7.5mm slots, Y=31mm, z_pivot_seat=38mm)
// Print 4x (one per slot)

include <params/dimensions.scad>

// ============ PLUG DIMENSIONS ============

slot_top = freeboard + 10;  // 55mm - matches hull_simple.scad
slot_bottom = 39;           // matches hull_simple.scad

shaft_clearance = 0.10;         // TIGHT fit
shaft_diameter = slot_diameter - shaft_clearance;  // 7.40mm for 7.5mm slot

ball_clearance = 0.25;
hemisphere_center_z = z_pivot_seat + ball_clearance;  // 38.25mm
shaft_length = slot_top - hemisphere_center_z;  // 55 - 38.25 = 16.75mm

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

// Uncomment for single plug view:
// slot_plug();

// Print orientation (cap down):
slot_plug_printable();

// Uncomment for 4-up batch:
// for (i = [0:3])
//     translate([i * 14, 0, 0])
//         slot_plug_printable();

// ============ VERIFICATION ============
echo("=== SLOT PLUGS for Hull v6 ===");
echo("Hull slot diameter:", slot_diameter, "mm");
echo("Hull z_pivot_seat:", z_pivot_seat, "mm");
echo("Hull slot_top:", slot_top, "mm");
echo("Hull slot_bottom:", slot_bottom, "mm");
echo("");
echo("Plug shaft diameter:", shaft_diameter, "mm (clearance:", shaft_clearance, "mm)");
echo("Plug shaft length:", shaft_length, "mm");
echo("Plug hemisphere center Z:", hemisphere_center_z, "mm");
echo("Plug cavity diameter:", cavity_diameter, "mm (ball:", ball_diameter, "mm)");
echo("Plug cap diameter:", cap_diameter, "mm");
