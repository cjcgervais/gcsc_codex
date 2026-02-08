// Namespaced wrapper for canonical GCSC Hull v5.3 reference geometry.
// Uses `use` to avoid rendering side effects from top-level calls in source.

use <../Inheritable_Dimensions/Open_Scad_Files/GCSC_Hull_v5.3.scad>

module gcsc_reference_hull_v53() {
    gcsc_hull_v53();
}
