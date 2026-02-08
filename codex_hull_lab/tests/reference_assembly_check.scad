// Reference assembly compatibility check.
// Renders hull + canonical frame + slot plugs in aligned coordinates.

include <../presets/gcsc_default.scad>
include <../src/gcsc_hull_core.scad>
include <../src/gcsc_reference_params.scad>
include <../reference/frame_v5_3_reference.scad>
include <../reference/slot_plug_reference.scad>

reference_alignment_z = gcsc_reference_to_model_z(0);
plug_insert_z = gcsc_reference_slot_seat_z();

color([0.90, 0.90, 0.92, 1.0])
    gcsc_hull_build();

// Frame in forward slot column.
color([0.83, 0.13, 0.13, 1.0])
    translate([REFERENCE_FRAME_SPACING, 0, reference_alignment_z])
        gcsc_reference_frame_v53_infill();

// Frame in aft slot column (visual alternate position).
color([0.85, 0.45, 0.45, 0.35])
    translate([-REFERENCE_FRAME_SPACING, 0, reference_alignment_z])
        gcsc_reference_frame_v53_infill();

for (x_sign = [-1, 1]) {
    for (y_sign = [-1, 1]) {
        color([0.22, 0.32, 0.86, 1.0])
            translate([x_sign * REFERENCE_FRAME_SPACING, y_sign * REFERENCE_PIVOT_Y, plug_insert_z])
                gcsc_reference_slot_plug();
    }
}
