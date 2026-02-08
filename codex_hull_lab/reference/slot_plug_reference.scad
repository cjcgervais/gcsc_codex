// Namespaced wrapper for canonical GCSC Slot Plug geometry.
// Uses `use` to avoid rendering side effects from top-level calls in source.

use <../Inheritable_Dimensions/Open_Scad_Files/GCSC_Slot_Plugs_v3.0_tight.scad>

module gcsc_reference_slot_plug() {
    slot_plug();
}

module gcsc_reference_slot_plug_printable() {
    slot_plug_printable();
}
