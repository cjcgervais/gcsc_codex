// Namespaced wrapper for canonical Danforth anchor geometry.
// Import STL directly to preserve exact inherited shape and avoid
// SCAD hull()-based render instability in some OpenSCAD builds.

module gcsc_reference_anchor() {
    import("../Inheritable_Dimensions/STL_files/GCSC_Danforth_Anchor_v1.2.stl", convexity = 12);
}
