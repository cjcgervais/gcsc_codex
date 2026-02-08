// Top-level hull composition module.

include <gcsc_hull_features.scad>
include <gcsc_hull_bosl2_adapter.scad>

c_enable_inner_cavity = gcsc_safe(enable_inner_cavity, true);

module gcsc_hull_keel() {
    gcsc_keel_feature();
}

module gcsc_hull_rim() {
    gcsc_rim_reinforcement_feature();
}

module gcsc_hull_positive_union() {
    union() {
        if (c_enable_inner_cavity) {
            gcsc_hull_shell();
        }
        else {
            gcsc_outer_hull();
        }

        if (f_enable_keel) {
            gcsc_hull_keel();
        }

        if (f_enable_rim_reinforcement) {
            gcsc_hull_rim();
        }

        gcsc_slot_wall_reinforcement_feature();
        gcsc_seat_stops_feature();
        gcsc_anchor_stop_feature();
    }
}

// Public module expected by gcsc_hull_entry.scad.
module gcsc_hull_build() {
    gcsc_require_bosl2();
    gcsc_reference_guardrails();

    union() {
        difference() {
            gcsc_hull_positive_union();
            gcsc_open_top_cut();
            gcsc_reference_slot_interface_cuts();
            gcsc_foot_recess_cutouts();
            gcsc_flat_base_cut();
            if (f_enable_drainage_hole) {
                gcsc_drainage_hole_cut();
            }
        }
    }
}
