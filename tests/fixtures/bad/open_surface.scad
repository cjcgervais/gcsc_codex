// GCSC2 Test Fixture: Known-bad non-manifold geometry
// This creates an open surface (not watertight) - should FAIL mesh validation
//
// WARNING: This file is intentionally broken for testing purposes

// Create a "half cube" that is not closed - non-manifold
difference() {
    cube([20, 20, 20], center=true);
    // Cut away more than half - leaves an open surface
    translate([0, 0, 15]) cube([30, 30, 20], center=true);
    // This second cut creates a non-manifold edge condition
    translate([10, 0, 0]) cube([10, 30, 30], center=true);
}
