// GCSC2 Test Fixture: Known-bad degenerate geometry
// This creates zero-volume geometry - should FAIL mesh validation
//
// WARNING: This file is intentionally broken for testing purposes

// A 2D square has no volume - degenerate in 3D context
// This will produce an empty or zero-facet STL
linear_extrude(height=0) {
    square([10, 10], center=true);
}
